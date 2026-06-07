#include <Servo.h>
#include <math.h>

// =====================================================
// Delta Robot Pick & Place State Machine with IK
// Coordinate convention follows Python IK/FK model:
//   - Base/platform center line is origin in X-Y.
//   - z negative = below the motor/base plane.
//   - theta input is kinematic theta [deg], not raw servo angle.
// =====================================================

// =====================
// Servo objects
// =====================
Servo servo1;
Servo servo2;
Servo servo3;

// =====================
// Pin settings
// =====================
const int SERVO1_PIN = 9;
const int SERVO2_PIN = 10;
const int SERVO3_PIN = 11;
const int PUMP_PIN = 6;   // MOSFET SIG for vacuum pump

// =====================
// Delta geometry [mm]
// Same as Python geometry.py NOMINAL_DELTA_GEOMETRY
// =====================
const float GEOM_L  = 125.0;   // upper_arm_length_mm
const float GEOM_l  = 300.0;   // parallelogram_link_length_mm
const float GEOM_wB = 46.0;    // base_center_to_side_mm
const float GEOM_uP = 27.177;  // platform_center_to_vertex_mm

// FK result for theta = 0,0,0 with the current geometry.
// Use as model home/reference. Real hardware may need small calibration.
const float BASE_X = 0.0;
const float BASE_Y = 0.0;
const float BASE_Z = -263.277;
const float HOME_Z = -250.0;

// =====================
// Pick & Place target positions [mm]
// z negative = lower/downward.
// travelZ should be higher than pick/place height, meaning less negative.
// =====================
float pickX = BASE_X;
float pickY = BASE_Y;
float pickZ = -261.0;

float placeX = BASE_X + 70.0;
float placeY = BASE_Y;
float placeZ = -260.0;

float travelZ = BASE_Z + 40.0;     // safe travel height, default ≈ -223.277

const int GRID_POINT_COUNT = 9;
const float GRID_X[GRID_POINT_COUNT] = {
  -40.0, 0.0, 40.0,
  -40.0, 0.0, 40.0,
  -40.0, 0.0, 40.0
};
const float GRID_Y[GRID_POINT_COUNT] = {
  -40.0, -40.0, -40.0,
  0.0, 0.0, 0.0,
  40.0, 40.0, 40.0
};
int currentGridIndex = 0;

// =====================
// Optional waypoint test parameters
// =====================
float TEST_Z = BASE_Z;             // waypoint test height
float TEST_N = 20.0;               // start small, increase to 40 later
float SQUARE_SIZE = 20.0;
float CIRCLE_R = 20.0;
int HOLD_MS = 1000;
int STATIC_HOLD_MS = 15000;

// =====================
// Arm outward unit vectors
// Same as Python ARM_OUTWARD_UNIT_VECTORS
// =====================
const float SQRT_3_OVER_2 = 0.8660254038;
const float ARM_UX[3] = {0.0, SQRT_3_OVER_2, -SQRT_3_OVER_2};
const float ARM_UY[3] = {-1.0, 0.5, 0.5};

// =====================
// Kinematic theta -> servo command mapping
// theta = 0 deg corresponds to each measured center command.
// =====================
const int SERVO1_CENTER_CMD = 84;
const int SERVO2_CENTER_CMD = 86;
const int SERVO3_CENTER_CMD = 88;

// Current upside-down final mounting convention from motor_test_ik.ino.
// If a motor rotates opposite to desired kinematic direction, change only that sign.
const int SERVO1_SIGN = -1;
const int SERVO2_SIGN = -1;
const int SERVO3_SIGN = -1;

const float SERVO1_THETA_GAIN = 1.25;
const float SERVO2_THETA_GAIN = 1.25;
const float SERVO3_THETA_GAIN = 1.25;

const int SERVO1_OFFSET = 0;
const int SERVO2_OFFSET = 0;
const int SERVO3_OFFSET = 0;

// Latest verified kinematic theta range from motor_test_ik.ino.
const float THETA_MIN = -60.0;
const float THETA_MAX = 90.0;

// Final hard limit for Servo.write()
const int SERVO_CMD_MIN = 0;
const int SERVO_CMD_MAX = 180;

// =====================
// Motion / timing parameters
// =====================
int defaultStepDelay = 35;      // ms per servo-command step
int suctionDelay = 1000;        // ms. Allow the vacuum cup to seal.
int releaseDelay = 500;         // ms. Increase if stone does not release.
int stateDelay = 100;           // ms

// =====================
// Current state variables
// =====================
float currentTheta1 = 0.0;
float currentTheta2 = 0.0;
float currentTheta3 = 0.0;

int currentCmd1 = SERVO1_CENTER_CMD;
int currentCmd2 = SERVO2_CENTER_CMD;
int currentCmd3 = SERVO3_CENTER_CMD;

bool pumpState = false;
bool cycleRunning = false;

// =====================================================
// State Machine
// =====================================================
enum State {
  IDLE,
  MOVE_ABOVE_PICK,
  MOVE_DOWN_TO_PICK,
  VACUUM_ON_STATE,
  LIFT_FROM_PICK,
  MOVE_ABOVE_PLACE,
  MOVE_DOWN_TO_PLACE,
  VACUUM_OFF_STATE,
  LIFT_FROM_PLACE,
  DONE,
  EMERGENCY_STOP
};

State currentState = IDLE;

// =====================================================
// Function prototypes
// =====================================================
void readSerialCommand();
void runStateMachine();
bool moveToXYZ(float x, float y, float z);
bool solveDeltaIK(float x_mm, float y_mm, float z_mm, float previousTheta[3], float resultTheta[3]);
bool solveSingleArmIK(int armIndex, float x_mm, float y_mm, float z_mm, float previousTheta, float &selectedTheta);

// =====================================================
// Setup / Loop
// =====================================================
void setup() {
  Serial.begin(9600);

  setupPump();
  setupServos();

  printHelp();
}

void loop() {
  readSerialCommand();

  if (cycleRunning) {
    runStateMachine();
  }
}

// =====================================================
// Initialization
// =====================================================
void setupServos() {
  servo1.attach(SERVO1_PIN);
  servo2.attach(SERVO2_PIN);
  servo3.attach(SERVO3_PIN);

  currentTheta1 = 0.0;
  currentTheta2 = 0.0;
  currentTheta3 = 0.0;
  currentCmd1 = SERVO1_CENTER_CMD;
  currentCmd2 = SERVO2_CENTER_CMD;
  currentCmd3 = SERVO3_CENTER_CMD;

  moveToXYZ(BASE_X, BASE_Y, HOME_Z);
  delay(1000);
  Serial.println(F("Servos initialized at HOME."));
}

void setupPump() {
  pinMode(PUMP_PIN, OUTPUT);
  digitalWrite(PUMP_PIN, LOW);
  pumpState = false;
}

// =====================================================
// Utility
// =====================================================
float constrainFloat(float value, float minValue, float maxValue) {
  if (value < minValue) return minValue;
  if (value > maxValue) return maxValue;
  return value;
}

float limitTheta(float theta) {
  return constrainFloat(theta, THETA_MIN, THETA_MAX);
}

int limitServoCommand(int angle) {
  return constrain(angle, SERVO_CMD_MIN, SERVO_CMD_MAX);
}

String stateToString(State s) {
  switch (s) {
    case IDLE: return "IDLE";
    case MOVE_ABOVE_PICK: return "MOVE_ABOVE_PICK";
    case MOVE_DOWN_TO_PICK: return "MOVE_DOWN_TO_PICK";
    case VACUUM_ON_STATE: return "VACUUM_ON_STATE";
    case LIFT_FROM_PICK: return "LIFT_FROM_PICK";
    case MOVE_ABOVE_PLACE: return "MOVE_ABOVE_PLACE";
    case MOVE_DOWN_TO_PLACE: return "MOVE_DOWN_TO_PLACE";
    case VACUUM_OFF_STATE: return "VACUUM_OFF_STATE";
    case LIFT_FROM_PLACE: return "LIFT_FROM_PLACE";
    case DONE: return "DONE";
    case EMERGENCY_STOP: return "EMERGENCY_STOP";
    default: return "UNKNOWN";
  }
}

void changeState(State nextState) {
  currentState = nextState;
  Serial.print(F("STATE -> "));
  Serial.println(stateToString(currentState));
  delay(stateDelay);
}

void printHelp() {
  Serial.println(F("===================================="));
  Serial.println(F("Delta Robot Grid Pick & Place IK Firmware v3"));
  Serial.println(F("Coordinate: z negative = below/downward, same as Python IK/FK"));
  Serial.println(F("Commands:"));
  Serial.println(F("HELP"));
  Serial.println(F("CENTER                  : theta 0,0,0"));
  Serial.println(F("HOME                    : move to safe home XYZ = 0,0,-250"));
  Serial.println(F("START                   : pick all 9 grid points and place outside"));
  Serial.println(F("TESTPICK                : pick center, place outside, return HOME"));
  Serial.println(F("STOP                    : pump off and stop cycle"));
  Serial.println(F("STATE                   : print state/targets/current theta"));
  Serial.println(F("ALL t1 t2 t3            : direct theta move"));
  Serial.println(F("IK x y z                : IK solve only, no movement"));
  Serial.println(F("XYZ x y z               : IK solve and move"));
  Serial.println(F("PICKZ z                 : set common grid pick height"));
  Serial.println(F("PLACE x y z             : set place position"));
  Serial.println(F("TRAVEL z                : set travel height"));
  Serial.println(F("STATIC / CROSS / SQUARE / CIRCLE / GRID"));
  Serial.println(F("PON / POFF              : pump on/off"));
  Serial.println(F("===================================="));
}

// =====================================================
// Mapping: theta -> servo command
// servo_cmd = center_cmd + sign * theta + offset
// =====================================================
int thetaToServoAngle(int id, float theta) {
  theta = limitTheta(theta);

  float servoCmd = 90.0;

  if (id == 1) {
    servoCmd = SERVO1_CENTER_CMD + SERVO1_SIGN * theta * SERVO1_THETA_GAIN + SERVO1_OFFSET;
  }
  else if (id == 2) {
    servoCmd = SERVO2_CENTER_CMD + SERVO2_SIGN * theta * SERVO2_THETA_GAIN + SERVO2_OFFSET;
  }
  else if (id == 3) {
    servoCmd = SERVO3_CENTER_CMD + SERVO3_SIGN * theta * SERVO3_THETA_GAIN + SERVO3_OFFSET;
  }

  return limitServoCommand((int)round(servoCmd));
}

// =====================================================
// Servo control
// =====================================================
void moveServoTheta(int id, float theta) {
  theta = limitTheta(theta);
  int servoCmd = thetaToServoAngle(id, theta);

  if (id == 1) {
    servo1.write(servoCmd);
    currentTheta1 = theta;
    currentCmd1 = servoCmd;
  }
  else if (id == 2) {
    servo2.write(servoCmd);
    currentTheta2 = theta;
    currentCmd2 = servoCmd;
  }
  else if (id == 3) {
    servo3.write(servoCmd);
    currentTheta3 = theta;
    currentCmd3 = servoCmd;
  }
  else {
    Serial.println(F("Invalid servo id."));
    return;
  }

  Serial.print(F("Servo "));
  Serial.print(id);
  Serial.print(F(" theta="));
  Serial.print(theta);
  Serial.print(F(" -> servo cmd="));
  Serial.println(servoCmd);

  delay(300);
}

void moveAllThetaSmooth(float theta1, float theta2, float theta3, int stepDelay) {
  theta1 = limitTheta(theta1);
  theta2 = limitTheta(theta2);
  theta3 = limitTheta(theta3);

  int targetCmd1 = thetaToServoAngle(1, theta1);
  int targetCmd2 = thetaToServoAngle(2, theta2);
  int targetCmd3 = thetaToServoAngle(3, theta3);

  int startCmd1 = currentCmd1;
  int startCmd2 = currentCmd2;
  int startCmd3 = currentCmd3;

  int diff1 = abs(targetCmd1 - startCmd1);
  int diff2 = abs(targetCmd2 - startCmd2);
  int diff3 = abs(targetCmd3 - startCmd3);

  int maxDiff = max(diff1, max(diff2, diff3));

  if (maxDiff == 0) {
    servo1.write(targetCmd1);
    servo2.write(targetCmd2);
    servo3.write(targetCmd3);

    currentTheta1 = theta1;
    currentTheta2 = theta2;
    currentTheta3 = theta3;
    currentCmd1 = targetCmd1;
    currentCmd2 = targetCmd2;
    currentCmd3 = targetCmd3;

    Serial.println(F("Servo target refreshed."));
    return;
  }

  for (int step = 1; step <= maxDiff; step++) {
    int a1 = startCmd1 + (targetCmd1 - startCmd1) * step / maxDiff;
    int a2 = startCmd2 + (targetCmd2 - startCmd2) * step / maxDiff;
    int a3 = startCmd3 + (targetCmd3 - startCmd3) * step / maxDiff;

    servo1.write(a1);
    servo2.write(a2);
    servo3.write(a3);

    delay(stepDelay);
  }

  currentTheta1 = theta1;
  currentTheta2 = theta2;
  currentTheta3 = theta3;

  currentCmd1 = targetCmd1;
  currentCmd2 = targetCmd2;
  currentCmd3 = targetCmd3;

  Serial.print(F("SMOOTH ALL theta -> "));
  Serial.print(theta1);
  Serial.print(F(", "));
  Serial.print(theta2);
  Serial.print(F(", "));
  Serial.print(theta3);

  Serial.print(F(" | servo cmd -> "));
  Serial.print(targetCmd1);
  Serial.print(F(", "));
  Serial.print(targetCmd2);
  Serial.print(F(", "));
  Serial.println(targetCmd3);
}

// =====================================================
// Delta IK
// Uses z directly. No z sign flip here.
// =====================================================
bool solveDeltaIK(
  float x_mm,
  float y_mm,
  float z_mm,
  float previousTheta[3],
  float resultTheta[3]
) {
  for (int arm = 0; arm < 3; arm++) {
    float theta;

    bool ok = solveSingleArmIK(
      arm,
      x_mm,
      y_mm,
      z_mm,
      previousTheta[arm],
      theta
    );

    if (!ok) {
      Serial.print(F("IK failed at arm "));
      Serial.println(arm + 1);
      return false;
    }

    resultTheta[arm] = theta;
  }

  return true;
}

bool solveSingleArmIK(
  int armIndex,
  float x_mm,
  float y_mm,
  float z_mm,
  float previousTheta,
  float &selectedTheta
) {
  float p_i = x_mm * ARM_UX[armIndex] + y_mm * ARM_UY[armIndex];
  float delta_offset = GEOM_uP - GEOM_wB;

  float e_term = -2.0 * GEOM_L * (p_i + delta_offset);
  float f_term =  2.0 * GEOM_L * z_mm;

  float g_term =
    x_mm * x_mm
    + y_mm * y_mm
    + delta_offset * delta_offset
    + 2.0 * delta_offset * p_i
    + z_mm * z_mm
    + GEOM_L * GEOM_L
    - GEOM_l * GEOM_l;

  float discriminant = e_term * e_term + f_term * f_term - g_term * g_term;

  if (discriminant < 0.0) {
    if (discriminant > -1e-5) {
      discriminant = 0.0;
    } else {
      Serial.println(F("IK reject: discriminant negative"));
      return false;
    }
  }

  float sqrtDisc = sqrt(discriminant);
  float denominator = g_term - e_term;

  float t1;
  float t2;
  bool hasT1 = false;
  bool hasT2 = false;

  if (fabs(denominator) < 1e-6) {
    if (fabs(f_term) < 1e-6) {
      Serial.println(F("IK reject: denominator singular"));
      return false;
    }

    t1 = -g_term / (2.0 * f_term);
    hasT1 = true;
  } else {
    t1 = (-f_term + sqrtDisc) / denominator;
    t2 = (-f_term - sqrtDisc) / denominator;
    hasT1 = true;
    hasT2 = true;
  }

  float candidates[2];
  int candidateCount = 0;

  if (hasT1) {
    candidates[candidateCount++] = 2.0 * atan(t1) * 180.0 / PI;
  }

  if (hasT2) {
    candidates[candidateCount++] = 2.0 * atan(t2) * 180.0 / PI;
  }

  bool found = false;
  float bestTheta = 0.0;
  float bestScore = 999999.0;

  for (int i = 0; i < candidateCount; i++) {
    float theta = candidates[i];

    if (theta < THETA_MIN - 1e-5 || theta > THETA_MAX + 1e-5) {
      continue;
    }

    float score = fabs(theta - previousTheta);

    if (!found || score < bestScore) {
      found = true;
      bestScore = score;
      bestTheta = theta;
    }
  }

  if (!found) {
    Serial.println(F("IK reject: angle out of range"));
    return false;
  }

  selectedTheta = bestTheta;
  return true;
}

// =====================================================
// IK move helpers
// =====================================================
bool moveToXYZ(float x, float y, float z) {
  float previousTheta[3] = {currentTheta1, currentTheta2, currentTheta3};
  float resultTheta[3];

  Serial.print(F("Move XYZ -> "));
  Serial.print(x);
  Serial.print(F(", "));
  Serial.print(y);
  Serial.print(F(", "));
  Serial.println(z);

  if (!solveDeltaIK(x, y, z, previousTheta, resultTheta)) {
    Serial.println(F("IK result: reject. No movement."));
    return false;
  }

  Serial.print(F("IK theta -> "));
  Serial.print(resultTheta[0]);
  Serial.print(F(", "));
  Serial.print(resultTheta[1]);
  Serial.print(F(", "));
  Serial.println(resultTheta[2]);

  moveAllThetaSmooth(resultTheta[0], resultTheta[1], resultTheta[2], defaultStepDelay);
  return true;
}

void runIKOnly(float x, float y, float z) {
  float previousTheta[3] = {currentTheta1, currentTheta2, currentTheta3};
  float resultTheta[3];

  Serial.print(F("IK target x y z = "));
  Serial.print(x);
  Serial.print(F(", "));
  Serial.print(y);
  Serial.print(F(", "));
  Serial.println(z);

  if (!solveDeltaIK(x, y, z, previousTheta, resultTheta)) {
    Serial.println(F("IK result: reject"));
    return;
  }

  Serial.print(F("IK theta -> "));
  Serial.print(resultTheta[0]);
  Serial.print(F(", "));
  Serial.print(resultTheta[1]);
  Serial.print(F(", "));
  Serial.println(resultTheta[2]);
}

// =====================================================
// Pump / vacuum control
// =====================================================
void pumpOn() {
  digitalWrite(PUMP_PIN, HIGH);
  pumpState = true;
  Serial.println(F("Pump ON"));
}

void pumpOff() {
  digitalWrite(PUMP_PIN, LOW);
  pumpState = false;
  Serial.println(F("Pump OFF"));
}

void vacuumOn() {
  pumpOn();
  delay(suctionDelay);
  Serial.println(F("Vacuum suction ON"));
}

void vacuumOff() {
  pumpOff();
  delay(releaseDelay);
  Serial.println(F("Vacuum released"));
}

bool testCenterPick() {
  Serial.println(F("TESTPICK START - center pick to configured place"));
  pumpOff();

  if (!moveToXYZ(BASE_X, BASE_Y, travelZ)) {
    Serial.println(F("TESTPICK failed above center"));
    return false;
  }

  if (!moveToXYZ(BASE_X, BASE_Y, pickZ)) {
    Serial.println(F("TESTPICK failed at center pick height"));
    pumpOff();
    return false;
  }

  vacuumOn();

  if (!moveToXYZ(BASE_X, BASE_Y, travelZ)) {
    Serial.println(F("TESTPICK failed while lifting"));
    pumpOff();
    return false;
  }

  if (!moveToXYZ(placeX, placeY, travelZ)) {
    Serial.println(F("TESTPICK failed above place"));
    pumpOff();
    return false;
  }

  if (!moveToXYZ(placeX, placeY, placeZ)) {
    Serial.println(F("TESTPICK failed at place height"));
    pumpOff();
    return false;
  }

  vacuumOff();

  if (!moveToXYZ(placeX, placeY, travelZ)) {
    Serial.println(F("TESTPICK failed while lifting from place"));
    pumpOff();
    return false;
  }

  if (!moveToXYZ(BASE_X, BASE_Y, HOME_Z)) {
    Serial.println(F("TESTPICK placed object but failed to return HOME"));
    return false;
  }

  Serial.println(F("TESTPICK DONE - object placed and pump OFF"));
  return true;
}

void selectGridPick(int index) {
  currentGridIndex = index;
  pickX = GRID_X[index];
  pickY = GRID_Y[index];

  Serial.print(F("Grid pick "));
  Serial.print(currentGridIndex + 1);
  Serial.print(F("/"));
  Serial.print(GRID_POINT_COUNT);
  Serial.print(F(" = "));
  Serial.print(pickX);
  Serial.print(F(", "));
  Serial.print(pickY);
  Serial.print(F(", "));
  Serial.println(pickZ);
}

bool validateGridCycleTargets() {
  float previousTheta[3] = {
    currentTheta1,
    currentTheta2,
    currentTheta3
  };
  float resultTheta[3];

  for (int index = 0; index < GRID_POINT_COUNT; index++) {
    if (!solveDeltaIK(GRID_X[index], GRID_Y[index], travelZ, previousTheta, resultTheta)) {
      Serial.print(F("Preflight failed above grid point "));
      Serial.println(index + 1);
      return false;
    }
    for (int arm = 0; arm < 3; arm++) previousTheta[arm] = resultTheta[arm];

    if (!solveDeltaIK(GRID_X[index], GRID_Y[index], pickZ, previousTheta, resultTheta)) {
      Serial.print(F("Preflight failed at grid pick point "));
      Serial.println(index + 1);
      return false;
    }
    for (int arm = 0; arm < 3; arm++) previousTheta[arm] = resultTheta[arm];

    if (!solveDeltaIK(GRID_X[index], GRID_Y[index], travelZ, previousTheta, resultTheta)) {
      Serial.print(F("Preflight failed lifting grid point "));
      Serial.println(index + 1);
      return false;
    }
    for (int arm = 0; arm < 3; arm++) previousTheta[arm] = resultTheta[arm];

    if (!solveDeltaIK(placeX, placeY, travelZ, previousTheta, resultTheta)) {
      Serial.println(F("Preflight failed above place point"));
      return false;
    }
    for (int arm = 0; arm < 3; arm++) previousTheta[arm] = resultTheta[arm];

    if (!solveDeltaIK(placeX, placeY, placeZ, previousTheta, resultTheta)) {
      Serial.println(F("Preflight failed at place point"));
      return false;
    }
    for (int arm = 0; arm < 3; arm++) previousTheta[arm] = resultTheta[arm];

    if (!solveDeltaIK(placeX, placeY, travelZ, previousTheta, resultTheta)) {
      Serial.println(F("Preflight failed lifting from place point"));
      return false;
    }
    for (int arm = 0; arm < 3; arm++) previousTheta[arm] = resultTheta[arm];
  }

  Serial.println(F("Grid cycle preflight OK"));
  return true;
}

// =====================================================
// Pick & Place State Machine
// =====================================================
void runStateMachine() {
  switch (currentState) {
    case IDLE:
      cycleRunning = false;
      break;

    case MOVE_ABOVE_PICK:
      if (moveToXYZ(pickX, pickY, travelZ)) changeState(MOVE_DOWN_TO_PICK);
      else changeState(EMERGENCY_STOP);
      break;

    case MOVE_DOWN_TO_PICK:
      if (moveToXYZ(pickX, pickY, pickZ)) changeState(VACUUM_ON_STATE);
      else changeState(EMERGENCY_STOP);
      break;

    case VACUUM_ON_STATE:
      vacuumOn();
      changeState(LIFT_FROM_PICK);
      break;

    case LIFT_FROM_PICK:
      if (moveToXYZ(pickX, pickY, travelZ)) changeState(MOVE_ABOVE_PLACE);
      else changeState(EMERGENCY_STOP);
      break;

    case MOVE_ABOVE_PLACE:
      if (moveToXYZ(placeX, placeY, travelZ)) changeState(MOVE_DOWN_TO_PLACE);
      else changeState(EMERGENCY_STOP);
      break;

    case MOVE_DOWN_TO_PLACE:
      if (moveToXYZ(placeX, placeY, placeZ)) changeState(VACUUM_OFF_STATE);
      else changeState(EMERGENCY_STOP);
      break;

    case VACUUM_OFF_STATE:
      vacuumOff();
      changeState(LIFT_FROM_PLACE);
      break;

    case LIFT_FROM_PLACE:
      if (moveToXYZ(placeX, placeY, travelZ)) changeState(DONE);
      else changeState(EMERGENCY_STOP);
      break;

    case DONE:
      Serial.print(F("Grid pick & place item "));
      Serial.print(currentGridIndex + 1);
      Serial.println(F(" DONE"));

      if (currentGridIndex + 1 < GRID_POINT_COUNT) {
        selectGridPick(currentGridIndex + 1);
        changeState(MOVE_ABOVE_PICK);
      } else {
        moveToXYZ(BASE_X, BASE_Y, travelZ);
        pumpOff();
        Serial.println(F("GRID PICK & PLACE DONE"));
        currentState = IDLE;
        cycleRunning = false;
      }
      break;

    case EMERGENCY_STOP:
      pumpOff();
      cycleRunning = false;
      Serial.println(F("Emergency stop"));
      break;
  }
}

// =====================================================
// Waypoint test routines
// =====================================================
void staticTest() {
  Serial.println(F("STATIC TEST START"));
  if (!moveToXYZ(BASE_X, BASE_Y, TEST_Z)) return;
  Serial.println(F("Holding center position..."));
  delay(STATIC_HOLD_MS);
  Serial.println(F("STATIC TEST DONE"));
}

void crossTest() {
  Serial.println(F("CROSS TEST START"));
  float N = TEST_N;
  float Z = TEST_Z;

  moveToXYZ(BASE_X, BASE_Y, Z); delay(HOLD_MS);
  moveToXYZ(BASE_X + N, BASE_Y, Z); delay(HOLD_MS);
  moveToXYZ(BASE_X, BASE_Y, Z); delay(HOLD_MS);
  moveToXYZ(BASE_X - N, BASE_Y, Z); delay(HOLD_MS);
  moveToXYZ(BASE_X, BASE_Y, Z); delay(HOLD_MS);
  moveToXYZ(BASE_X, BASE_Y + N, Z); delay(HOLD_MS);
  moveToXYZ(BASE_X, BASE_Y, Z); delay(HOLD_MS);
  moveToXYZ(BASE_X, BASE_Y - N, Z); delay(HOLD_MS);
  moveToXYZ(BASE_X, BASE_Y, Z); delay(HOLD_MS);

  Serial.println(F("CROSS TEST DONE"));
}

void squareTest() {
  Serial.println(F("SQUARE TEST START"));
  float A = SQUARE_SIZE;
  float Z = TEST_Z;

  moveToXYZ(BASE_X - A, BASE_Y - A, Z); delay(HOLD_MS);
  moveToXYZ(BASE_X + A, BASE_Y - A, Z); delay(HOLD_MS);
  moveToXYZ(BASE_X + A, BASE_Y + A, Z); delay(HOLD_MS);
  moveToXYZ(BASE_X - A, BASE_Y + A, Z); delay(HOLD_MS);
  moveToXYZ(BASE_X - A, BASE_Y - A, Z); delay(HOLD_MS);
  moveToXYZ(BASE_X, BASE_Y, Z); delay(HOLD_MS);

  Serial.println(F("SQUARE TEST DONE"));
}

void circleTest() {
  Serial.println(F("CIRCLE TEST START"));
  float R = CIRCLE_R;
  float Z = TEST_Z;
  const int NUM_POINTS = 24;

  for (int i = 0; i <= NUM_POINTS; i++) {
    float angle = 2.0 * PI * i / NUM_POINTS;
    float x = BASE_X + R * cos(angle);
    float y = BASE_Y + R * sin(angle);

    Serial.print(F("Circle point "));
    Serial.print(i);
    Serial.print(F(": "));
    Serial.print(x);
    Serial.print(F(", "));
    Serial.print(y);
    Serial.print(F(", "));
    Serial.println(Z);

    if (!moveToXYZ(x, y, Z)) {
      Serial.println(F("CIRCLE failed: IK reject"));
      return;
    }
    delay(HOLD_MS);
  }

  moveToXYZ(BASE_X, BASE_Y, Z);
  delay(HOLD_MS);

  Serial.println(F("CIRCLE TEST DONE"));
}

void gridTest() {
  Serial.println(F("GRID TEST START"));
  float N = TEST_N;
  float Z = TEST_Z;
  float points[3] = {-N, 0.0, N};

  for (int iy = 0; iy < 3; iy++) {
    for (int ix = 0; ix < 3; ix++) {
      float x = BASE_X + points[ix];
      float y = BASE_Y + points[iy];

      Serial.print(F("Grid point x y z = "));
      Serial.print(x);
      Serial.print(F(", "));
      Serial.print(y);
      Serial.print(F(", "));
      Serial.println(Z);

      if (!moveToXYZ(x, y, Z)) {
        Serial.println(F("GRID failed: IK reject"));
        return;
      }
      delay(HOLD_MS);
    }
  }

  moveToXYZ(BASE_X, BASE_Y, Z);
  delay(HOLD_MS);

  Serial.println(F("GRID TEST DONE"));
}

// =====================================================
// Serial parsing helpers
// =====================================================
String getToken(String input, int index) {
  input.trim();
  int tokenIndex = 0;
  int startIndex = 0;

  while (startIndex < input.length()) {
    while (startIndex < input.length() && input.charAt(startIndex) == ' ') startIndex++;
    if (startIndex >= input.length()) break;

    int endIndex = input.indexOf(' ', startIndex);
    if (endIndex == -1) endIndex = input.length();

    if (tokenIndex == index) return input.substring(startIndex, endIndex);

    tokenIndex++;
    startIndex = endIndex + 1;
  }
  return "";
}

bool parseThreeFloats(String cmd, float &a, float &b, float &c) {
  String s1 = getToken(cmd, 1);
  String s2 = getToken(cmd, 2);
  String s3 = getToken(cmd, 3);
  if (s1.length() == 0 || s2.length() == 0 || s3.length() == 0) return false;
  a = s1.toFloat();
  b = s2.toFloat();
  c = s3.toFloat();
  return true;
}

bool parseOneFloat(String cmd, float &a) {
  String s1 = getToken(cmd, 1);
  if (s1.length() == 0) return false;
  a = s1.toFloat();
  return true;
}

bool parseMotorThetaCommand(String cmd, int &id, float &theta) {
  String s0 = getToken(cmd, 0);
  String s1 = getToken(cmd, 1);
  if (s0.length() == 0 || s1.length() == 0) return false;

  id = s0.toInt();
  theta = s1.toFloat();

  if (id < 1 || id > 3) return false;
  return true;
}

// =====================================================
// Serial command
// =====================================================
void readSerialCommand() {
  if (Serial.available() == 0) return;

  String cmd = Serial.readStringUntil('\n');
  cmd.trim();
  if (cmd.length() == 0) return;

  if (cmd == "HELP") {
    printHelp();
  }
  else if (cmd == "CENTER") {
    moveAllThetaSmooth(0, 0, 0, defaultStepDelay);
  }
  else if (cmd == "HOME") {
    moveToXYZ(BASE_X, BASE_Y, HOME_Z);
  }
  else if (cmd == "START") {
    Serial.println(F("Start 3x3 Grid Pick & Place Cycle"));
    pumpOff();
    if (!validateGridCycleTargets()) {
      Serial.println(F("START rejected: unsafe or unreachable target"));
      currentState = IDLE;
      cycleRunning = false;
      return;
    }
    selectGridPick(0);
    cycleRunning = true;
    changeState(MOVE_ABOVE_PICK);
  }
  else if (cmd == "TESTPICK") {
    if (cycleRunning) {
      Serial.println(F("TESTPICK rejected: cycle is running"));
    } else {
      testCenterPick();
    }
  }
  else if (cmd == "STOP") {
    Serial.println(F("Stop command received"));
    currentState = EMERGENCY_STOP;
    cycleRunning = true;
  }
  else if (cmd == "STATE") {
    printState();
  }
  else if (cmd == "PON") {
    pumpOn();
  }
  else if (cmd == "POFF") {
    pumpOff();
  }
  else if (cmd == "STATIC") {
    staticTest();
  }
  else if (cmd == "CROSS") {
    crossTest();
  }
  else if (cmd == "SQUARE") {
    squareTest();
  }
  else if (cmd == "CIRCLE") {
    circleTest();
  }
  else if (cmd == "GRID") {
    gridTest();
  }
  else if (cmd.startsWith("ALL")) {
    float t1, t2, t3;
    if (parseThreeFloats(cmd, t1, t2, t3)) {
      moveAllThetaSmooth(t1, t2, t3, defaultStepDelay);
    } else {
      Serial.println(F("Invalid ALL command. Use: ALL 0 0 0"));
    }
  }
  else if (cmd.startsWith("IK")) {
    float x, y, z;
    if (parseThreeFloats(cmd, x, y, z)) {
      runIKOnly(x, y, z);
    } else {
      Serial.println(F("Invalid IK command. Use: IK x y z"));
    }
  }
  else if (cmd.startsWith("XYZ")) {
    float x, y, z;
    if (parseThreeFloats(cmd, x, y, z)) {
      moveToXYZ(x, y, z);
    } else {
      Serial.println(F("Invalid XYZ command. Use: XYZ x y z"));
    }
  }
  else if (cmd.startsWith("PICKZ")) {
    float z;
    if (parseOneFloat(cmd, z)) {
      pickZ = z;
      Serial.print(F("Set GRID PICK_Z = "));
      Serial.println(pickZ);
    } else {
      Serial.println(F("Invalid PICKZ command. Use: PICKZ -263.277"));
    }
  }
  else if (cmd.startsWith("PLACE")) {
    float x, y, z;
    if (parseThreeFloats(cmd, x, y, z)) {
      placeX = x;
      placeY = y;
      placeZ = z;
      Serial.print(F("Set PLACE = "));
      Serial.print(placeX);
      Serial.print(F(", "));
      Serial.print(placeY);
      Serial.print(F(", "));
      Serial.println(placeZ);
    } else {
      Serial.println(F("Invalid PLACE command. Use: PLACE x y z"));
    }
  }
  else if (cmd.startsWith("TRAVEL")) {
    float z;
    if (parseOneFloat(cmd, z)) {
      travelZ = z;
      Serial.print(F("Set TRAVEL_Z = "));
      Serial.println(travelZ);
    } else {
      Serial.println(F("Invalid TRAVEL command. Use: TRAVEL z"));
    }
  }
  else if (cmd.startsWith("TESTN")) {
    float n;
    if (parseOneFloat(cmd, n)) {
      TEST_N = n;
      Serial.print(F("Set TEST_N = "));
      Serial.println(TEST_N);
    } else {
      Serial.println(F("Invalid TESTN command. Use: TESTN 20"));
    }
  }
  else if (cmd.startsWith("TESTZ")) {
    float z;
    if (parseOneFloat(cmd, z)) {
      TEST_Z = z;
      Serial.print(F("Set TEST_Z = "));
      Serial.println(TEST_Z);
    } else {
      Serial.println(F("Invalid TESTZ command. Use: TESTZ -263.277"));
    }
  }
  else {
    int id;
    float theta;
    if (parseMotorThetaCommand(cmd, id, theta)) {
      moveServoTheta(id, theta);
    } else {
      Serial.println(F("Invalid command. Type HELP."));
    }
  }
}

// =====================================================
// State print
// =====================================================
void printState() {
  Serial.println(F("---------- STATE ----------"));
  Serial.print(F("Current state = "));
  Serial.println(stateToString(currentState));

  Serial.print(F("theta = "));
  Serial.print(currentTheta1);
  Serial.print(F(", "));
  Serial.print(currentTheta2);
  Serial.print(F(", "));
  Serial.println(currentTheta3);

  Serial.print(F("servo cmd = "));
  Serial.print(currentCmd1);
  Serial.print(F(", "));
  Serial.print(currentCmd2);
  Serial.print(F(", "));
  Serial.println(currentCmd3);

  Serial.print(F("BASE = "));
  Serial.print(BASE_X);
  Serial.print(F(", "));
  Serial.print(BASE_Y);
  Serial.print(F(", "));
  Serial.println(BASE_Z);

  Serial.print(F("PICK = "));
  Serial.print(pickX);
  Serial.print(F(", "));
  Serial.print(pickY);
  Serial.print(F(", "));
  Serial.println(pickZ);

  Serial.print(F("PLACE = "));
  Serial.print(placeX);
  Serial.print(F(", "));
  Serial.print(placeY);
  Serial.print(F(", "));
  Serial.println(placeZ);

  Serial.print(F("TRAVEL_Z = "));
  Serial.println(travelZ);

  Serial.print(F("TEST_Z = "));
  Serial.println(TEST_Z);

  Serial.print(F("TEST_N = "));
  Serial.println(TEST_N);

  Serial.print(F("pump = "));
  Serial.println(pumpState ? "ON" : "OFF");
  Serial.println(F("---------------------------"));
}
