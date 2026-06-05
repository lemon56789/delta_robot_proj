#include <Servo.h>
#include <math.h>

// =====================================================
// Delta Robot Arduino IK + Servo Control Firmware
// Input: target position x y z [mm]
// Output: theta1 theta2 theta3 [deg] -> servo command
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

const int PUMP_PIN = 6;

// =====================
// Geometry constants [mm]
// Python geometry.py의 NOMINAL_DELTA_GEOMETRY와 동일
// =====================
const float GEOM_L  = 125.0;   // upper_arm_length_mm
const float GEOM_l  = 300.0;   // parallelogram_link_length_mm
const float GEOM_wB = 46.0;    // base_center_to_side_mm
const float GEOM_uP = 27.177;  // platform_center_to_vertex_mm
const float base_x = 0;
const float base_y = 0;
const float base_z = -263.277;
// 원점 좌표(플랫폼 기준) --> (0, 0, -263.277) --> 보정필요하긴 함.

// =====================
// Parameter 정리
float TEST_Z = base_z;       // 테스트 높이
float TEST_N = 40.0;         // grid/cross 기본 이동량
float SQUARE_SIZE = 40.0;    // square 반변 길이 또는 이동 크기
float CIRCLE_R = 40.0;       // circle radius, 60 이하 권장
int HOLD_MS = 5000;          // 각 waypoint 정지 시간
int STATIC_HOLD_MS = 15000; // STATIC POINT 정지시간

// =====================
// Arm outward unit vectors
// Python 코드의 ARM_OUTWARD_UNIT_VECTORS와 동일
// =====================
const float SQRT_3_OVER_2 = 0.8660254038;

const float ARM_UX[3] = {
  0.0,
  SQRT_3_OVER_2,
  -SQRT_3_OVER_2
};

const float ARM_UY[3] = {
  -1.0,
  0.5,
  0.5
};

// =====================
// Kinematic theta to servo command mapping
// theta = 0 deg일 때 각 서보가 수평 기준 자세가 되는 실제 명령각
// =====================
const int SERVO1_CENTER_CMD = 88;
const int SERVO2_CENTER_CMD = 86;
const int SERVO3_CENTER_CMD = 88;

// upside down 장착 기준. 방향 반대면 해당 모터만 +1로 수정.
const int SERVO1_SIGN = -1;
const int SERVO2_SIGN = -1;
const int SERVO3_SIGN = -1;

const int SERVO1_OFFSET = 0;
const int SERVO2_OFFSET = 0;
const int SERVO3_OFFSET = 0;

// 실제 기구학 theta 허용 범위
// 현재 upside down 장착 기준으로 설정
const float THETA_MIN = -60.0;
const float THETA_MAX = 90.0;

// Servo.write() 최종 안전 제한
const int SERVO_CMD_MIN = 0;
const int SERVO_CMD_MAX = 180;

// =====================
// Current state
// =====================
float currentTheta1 = 0.0;
float currentTheta2 = 0.0;
float currentTheta3 = 0.0;

int currentCmd1 = SERVO1_CENTER_CMD;
int currentCmd2 = SERVO2_CENTER_CMD;
int currentCmd3 = SERVO3_CENTER_CMD;

// motion parameter
int defaultStepDelay = 20;

// pump state
bool pumpState = false;

// =====================================================
// Setup / Loop
// =====================================================
void setup() {
  Serial.begin(9600);

  servo1.attach(SERVO1_PIN);
  servo2.attach(SERVO2_PIN);
  servo3.attach(SERVO3_PIN);

  servo1.write(SERVO1_CENTER_CMD);
  servo2.write(SERVO2_CENTER_CMD);
  servo3.write(SERVO3_CENTER_CMD);

  currentTheta1 = 0.0;
  currentTheta2 = 0.0;
  currentTheta3 = 0.0;

  currentCmd1 = SERVO1_CENTER_CMD;
  currentCmd2 = SERVO2_CENTER_CMD;
  currentCmd3 = SERVO3_CENTER_CMD;

  pinMode(PUMP_PIN, OUTPUT);
  digitalWrite(PUMP_PIN, LOW);

  Serial.println("Delta Robot IK Firmware Start");
  Serial.println("Commands:");
  Serial.println("CENTER");
  Serial.println("ALL theta1 theta2 theta3");
  Serial.println("XYZ x y z        -> IK solve and move");
  Serial.println("IK x y z         -> IK solve only, no move");
  Serial.println("1 theta / 2 theta / 3 theta");
  Serial.println("SWEEP");
  Serial.println("STATE");
  Serial.println("PON / POFF");
  Serial.println("Ready. Initial HOME command sent.");
}

void loop() {
  readSerialCommand();
}

// =====================================================
// Utility
// =====================================================
float constrainFloat(float value, float minValue, float maxValue) {
  if (value < minValue) return minValue;
  if (value > maxValue) return maxValue;
  return value;
}

int limitServoCommand(int angle) {
  return constrain(angle, SERVO_CMD_MIN, SERVO_CMD_MAX);
}

float limitTheta(float theta) {
  return constrainFloat(theta, THETA_MIN, THETA_MAX);
}

// =====================================================
// Mapping: theta -> servo command
// servo_angle_i = center_cmd_i + sign_i * theta_i + offset_i
// =====================================================
int thetaToServoAngle(int id, float theta) {
  theta = limitTheta(theta);

  float servoCmd = 90.0;

  if (id == 1) {
    servoCmd = SERVO1_CENTER_CMD + SERVO1_SIGN * theta + SERVO1_OFFSET;
  }
  else if (id == 2) {
    servoCmd = SERVO2_CENTER_CMD + SERVO2_SIGN * theta + SERVO2_OFFSET;
  }
  else if (id == 3) {
    servoCmd = SERVO3_CENTER_CMD + SERVO3_SIGN * theta + SERVO3_OFFSET;
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
    Serial.println("Invalid servo id.");
    return;
  }

  Serial.print("Servo ");
  Serial.print(id);
  Serial.print(" theta=");
  Serial.print(theta);
  Serial.print(" -> servo cmd=");
  Serial.println(servoCmd);

  delay(300);
}

void moveAllTheta(float theta1, float theta2, float theta3) {
  theta1 = limitTheta(theta1);
  theta2 = limitTheta(theta2);
  theta3 = limitTheta(theta3);

  int cmd1 = thetaToServoAngle(1, theta1);
  int cmd2 = thetaToServoAngle(2, theta2);
  int cmd3 = thetaToServoAngle(3, theta3);

  servo1.write(cmd1);
  servo2.write(cmd2);
  servo3.write(cmd3);

  currentTheta1 = theta1;
  currentTheta2 = theta2;
  currentTheta3 = theta3;

  currentCmd1 = cmd1;
  currentCmd2 = cmd2;
  currentCmd3 = cmd3;

  Serial.print("ALL theta -> ");
  Serial.print(theta1);
  Serial.print(", ");
  Serial.print(theta2);
  Serial.print(", ");
  Serial.print(theta3);

  Serial.print(" | servo cmd -> ");
  Serial.print(cmd1);
  Serial.print(", ");
  Serial.print(cmd2);
  Serial.print(", ");
  Serial.println(cmd3);

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

    Serial.print("SMOOTH ALL theta -> ");
    Serial.print(theta1);
    Serial.print(", ");
    Serial.print(theta2);
    Serial.print(", ");
    Serial.print(theta3);

    Serial.print(" | servo cmd -> ");
    Serial.print(targetCmd1);
    Serial.print(", ");
    Serial.print(targetCmd2);
    Serial.print(", ");
    Serial.println(targetCmd3);

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

  Serial.print("SMOOTH ALL theta -> ");
  Serial.print(theta1);
  Serial.print(", ");
  Serial.print(theta2);
  Serial.print(", ");
  Serial.print(theta3);

  Serial.print(" | servo cmd -> ");
  Serial.print(targetCmd1);
  Serial.print(", ");
  Serial.print(targetCmd2);
  Serial.print(", ");
  Serial.println(targetCmd3);
}

// =====================================================
// Delta IK
// Returns true if success
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
      Serial.print("IK failed at arm ");
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
      Serial.println("IK reject: discriminant negative");
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
      Serial.println("IK reject: denominator singular");
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
    float theta = 2.0 * atan(t1) * 180.0 / PI;
    candidates[candidateCount++] = theta;
  }

  if (hasT2) {
    float theta = 2.0 * atan(t2) * 180.0 / PI;
    candidates[candidateCount++] = theta;
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
    Serial.println("IK reject: angle out of range");
    return false;
  }

  selectedTheta = bestTheta;
  return true;
}

// =====================================================
// Pump control
// =====================================================
void pumpOn() {
  digitalWrite(PUMP_PIN, HIGH);
  pumpState = true;
  Serial.println("Pump ON");
}

void pumpOff() {
  digitalWrite(PUMP_PIN, LOW);
  pumpState = false;
  Serial.println("Pump OFF");
}

// =====================================================
// Serial parsing helpers
// =====================================================
String getToken(String input, int index) {
  input.trim();

  int tokenIndex = 0;
  int startIndex = 0;

  while (startIndex < input.length()) {
    while (startIndex < input.length() && input.charAt(startIndex) == ' ') {
      startIndex++;
    }

    if (startIndex >= input.length()) break;

    int endIndex = input.indexOf(' ', startIndex);
    if (endIndex == -1) endIndex = input.length();

    if (tokenIndex == index) {
      return input.substring(startIndex, endIndex);
    }

    tokenIndex++;
    startIndex = endIndex + 1;
  }

  return "";
}

bool parseThreeFloats(String cmd, float &a, float &b, float &c) {
  String s1 = getToken(cmd, 1);
  String s2 = getToken(cmd, 2);
  String s3 = getToken(cmd, 3);

  if (s1.length() == 0 || s2.length() == 0 || s3.length() == 0) {
    return false;
  }

  a = s1.toFloat();
  b = s2.toFloat();
  c = s3.toFloat();

  return true;
}

// =====================================================
// Commands
// =====================================================
void readSerialCommand() {
  if (Serial.available() == 0) return;

  String cmd = Serial.readStringUntil('\n');
  cmd.trim();

  if (cmd.length() == 0) return;

// Basic Motion Commands
  if (cmd == "HOME") {
    moveAllThetaSmooth(0, 0, 0, defaultStepDelay);
  }

  else if (cmd == "STATE") {
    printState();
  }

  else if (cmd == "SWEEP") {
    sweepTest();
  }

  else if (cmd == "XYTEST"){
    xyMoveTest();
  }

// Waypoint Test Commands
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

// Pump Commands
  else if (cmd == "PON") {
    pumpOn();
  }

  else if (cmd == "POFF") {
    pumpOff();
  }

// =========================
// Direct theta commands
// Format : ALL theta1 theta2 theta3
// =========================
  else if (cmd.startsWith("ALL")) {
    float t1, t2, t3;

    if (parseThreeFloats(cmd, t1, t2, t3)) {
      moveAllThetaSmooth(t1, t2, t3, defaultStepDelay);
    } else {
      Serial.println("Invalid ALL command. Use: ALL 0 0 0");
    }
  }

// ========================
// IK calculation only
// Format: IK x y z
// ========================
  else if (cmd.startsWith("IK")) {
    float x, y, z;

    if (parseThreeFloats(cmd, x, y, z)) {
      runIKOnly(x, y, z);
    } else {
      Serial.println("Invalid IK command. Use: IK x y z");
    }
  }

// ========================
// IK calculation + movement
// Format: XYZ x y z
// ========================
  else if (cmd.startsWith("XYZ")) {
    float x, y, z;

    if (parseThreeFloats(cmd, x, y, z)) {
      runIKAndMove(x, y, z);
    } else {
      Serial.println("Invalid XYZ command. Use: XYZ x y z");
    }
  }

// ==========================
// Individual motor theta command
// Format: motor_id theta
// ==========================
  else {
    int id;
    float theta;

    if (parseMotorThetaCommand(cmd, id, theta)) {
      moveServoTheta(id, theta);
    } else {
      Serial.println("Invalid command.");
    }
  }
}

bool parseMotorThetaCommand(String cmd, int &id, float &theta) {
  String s0 = getToken(cmd, 0);
  String s1 = getToken(cmd, 1);

  if (s0.length() == 0 || s1.length() == 0) {
    return false;
  }

  id = s0.toInt();
  theta = s1.toFloat();

  if (id < 1 || id > 3) {
    return false;
  }

  return true;
}

void runIKOnly(float x, float y, float z) {
  float previousTheta[3] = {
    currentTheta1,
    currentTheta2,
    currentTheta3
  };

  float resultTheta[3];

  Serial.print("IK target x y z = ");
  Serial.print(x);
  Serial.print(", ");
  Serial.print(y);
  Serial.print(", ");
  Serial.println(z);

  if (!solveDeltaIK(x, y, z, previousTheta, resultTheta)) {
    Serial.println("IK result: reject");
    return;
  }

  Serial.print("IK theta -> ");
  Serial.print(resultTheta[0]);
  Serial.print(", ");
  Serial.print(resultTheta[1]);
  Serial.print(", ");
  Serial.println(resultTheta[2]);
}

void runIKAndMove(float x, float y, float z) {
  float previousTheta[3] = {
    currentTheta1,
    currentTheta2,
    currentTheta3
  };

  float resultTheta[3];

  Serial.print("XYZ target x y z = ");
  Serial.print(x);
  Serial.print(", ");
  Serial.print(y);
  Serial.print(", ");
  Serial.println(z);

  if (!solveDeltaIK(x, y, z, previousTheta, resultTheta)) {
    Serial.println("IK result: reject. No movement.");
    return;
  }

  Serial.print("IK theta -> ");
  Serial.print(resultTheta[0]);
  Serial.print(", ");
  Serial.print(resultTheta[1]);
  Serial.print(", ");
  Serial.println(resultTheta[2]);

  moveAllThetaSmooth(
    resultTheta[0],
    resultTheta[1],
    resultTheta[2],
    defaultStepDelay
  );
}

void xyMoveTest() {
  Serial.println("XYTEST START");
  Serial.println("Path: THETA HOME -> +X -> THETA HOME -> +Y -> THETA HOME");

  const float Z = TEST_Z;
  const float N = TEST_N;

  Serial.println("[1] Move to theta HOME: 0,0,0");
  moveAllThetaSmooth(0, 0, 0, defaultStepDelay);
  delay(HOLD_MS);

  Serial.println("[2] Move to +X");
  if (!moveToXYZ(base_x + N, base_y, Z)) {
    Serial.println("XYTEST failed at +X");
    return;
  }
  delay(HOLD_MS);

  Serial.println("[3] Return to theta HOME: 0,0,0");
  moveAllThetaSmooth(0, 0, 0, defaultStepDelay);
  delay(HOLD_MS);

  Serial.println("[4] Move to +Y");
  if (!moveToXYZ(base_x, base_y + N, Z)) {
    Serial.println("XYTEST failed at +Y");
    return;
  }
  delay(HOLD_MS);

  Serial.println("[5] Return to theta HOME: 0,0,0");
  moveAllThetaSmooth(0, 0, 0, defaultStepDelay);
  delay(HOLD_MS);

  Serial.println("XYTEST DONE");
}

bool moveToXYZ(float x, float y, float z) {
  float previousTheta[3] = {
    currentTheta1,
    currentTheta2,
    currentTheta3
  };

  float resultTheta[3];

  Serial.print("moveToXYZ target x y z = ");
  Serial.print(x);
  Serial.print(", ");
  Serial.print(y);
  Serial.print(", ");
  Serial.println(z);

  // 현재 좌표계 기준:
  // 플랫폼 기준 아래 방향이 z 음수이므로 z를 뒤집지 않고 그대로 IK에 넣음
  if (!solveDeltaIK(x, y, z, previousTheta, resultTheta)) {
    Serial.println("moveToXYZ failed: IK reject");
    return false;
  }

  Serial.print("moveToXYZ IK theta -> ");
  Serial.print(resultTheta[0]);
  Serial.print(", ");
  Serial.print(resultTheta[1]);
  Serial.print(", ");
  Serial.println(resultTheta[2]);

  moveAllThetaSmooth(
    resultTheta[0],
    resultTheta[1],
    resultTheta[2],
    defaultStepDelay
  );

  return true;
}

void sweepTest() {
  Serial.println("SWEEP TEST START");

  moveAllThetaSmooth(0, 0, 0, defaultStepDelay);
  delay(500);

  moveAllThetaSmooth(THETA_MIN, THETA_MIN, THETA_MIN, defaultStepDelay);
  delay(500);

  moveAllThetaSmooth(0, 0, 0, defaultStepDelay);
  delay(500);

  moveAllThetaSmooth(THETA_MAX, THETA_MAX, THETA_MAX, defaultStepDelay);
  delay(500);

  moveAllThetaSmooth(0, 0, 0, defaultStepDelay);
  delay(500);

  Serial.println("SWEEP TEST END");
}

void staticTest() { // 1. 정지오차 확인용 STATIC TEST
  Serial.println("STATIC TEST START");

  Serial.println("Move to theta HOME: 0,0,0");
  moveAllThetaSmooth(0, 0, 0, defaultStepDelay);

  Serial.println("Holding HOME position...");
  delay(STATIC_HOLD_MS);

  Serial.println("STATIC TEST DONE");
}

void crossTest() { //2. 궤적 확인용 CROSS TEST
  Serial.println("CROSS TEST START");

  const float N = TEST_N;
  const float Z = TEST_Z;

  moveToXYZ(base_x, base_y, Z);
  delay(HOLD_MS);

  moveToXYZ(base_x + N, base_y, Z);
  delay(HOLD_MS);

  moveToXYZ(base_x, base_y, Z);
  delay(HOLD_MS);

  moveToXYZ(base_x - N, base_y, Z);
  delay(HOLD_MS);

  moveToXYZ(base_x, base_y, Z);
  delay(HOLD_MS);

  moveToXYZ(base_x, base_y + N, Z);
  delay(HOLD_MS);

  moveToXYZ(base_x, base_y, Z);
  delay(HOLD_MS);

  moveToXYZ(base_x, base_y - N, Z);
  delay(HOLD_MS);

  moveToXYZ(base_x, base_y, Z);
  delay(HOLD_MS);

  Serial.println("CROSS TEST DONE");
}

void squareTest() { // 3. 궤적 확인용 SQUARE TEST
  Serial.println("SQUARE TEST START");

  const float A = SQUARE_SIZE;
  const float Z = TEST_Z;

  moveToXYZ(base_x - A, base_y - A, Z);
  delay(HOLD_MS);

  moveToXYZ(base_x + A, base_y -A, Z);
  delay(HOLD_MS);

  moveToXYZ(base_x + A, base_y + A, Z);
  delay(HOLD_MS);

  moveToXYZ(base_x - A, base_y + A, Z);
  delay(HOLD_MS);

  moveToXYZ(base_x - A, base_y - A, Z);
  delay(HOLD_MS);

  moveToXYZ(base_x, base_y, Z);
  delay(HOLD_MS);

  Serial.println("SQUARE TEST DONE");
}

void circleTest() { // 4. 궤적 확인용 CIRCLE TEST
  Serial.println("CIRCLE TEST START");

  const float R = CIRCLE_R;
  const float Z = TEST_Z;
  const int NUM_POINTS = 24;

  for (int i = 0; i <= NUM_POINTS; i++) {
    float angle = 2.0 * PI * i / NUM_POINTS;

    float x = R * cos(angle);
    float y = R * sin(angle);

    Serial.print("Circle point ");
    Serial.print(i);
    Serial.print(": ");
    Serial.print(x);
    Serial.print(", ");
    Serial.print(y);
    Serial.print(", ");
    Serial.println(Z);

    if (!moveToXYZ(x, y, Z)) {
      Serial.println("CIRCLE failed: IK reject");
      return;
    }

    delay(HOLD_MS);
  }

  moveToXYZ(base_x, base_y, Z);
  delay(HOLD_MS);

  Serial.println("CIRCLE TEST DONE");
}

void gridTest() { // 5. 학습용 데이터 쌓기용 GRID TEST
  Serial.println("GRID TEST START");

  const float N = TEST_N;
  const float Z = TEST_Z;

  float points[3] = {-N, 0.0, N};

  for (int iy = 0; iy < 3; iy++) {
    for (int ix = 0; ix < 3; ix++) {
      float x = points[ix];
      float y = points[iy];

      Serial.print("Grid point x y z = ");
      Serial.print(x);
      Serial.print(", ");
      Serial.print(y);
      Serial.print(", ");
      Serial.println(Z);

      if (!moveToXYZ(x, y, Z)) {
        Serial.println("GRID failed: IK reject");
        return;
      }

      delay(HOLD_MS);
    }
  }

  moveToXYZ(0, 0, Z);
  delay(HOLD_MS);

  Serial.println("GRID TEST DONE");
}

void printState() {
  Serial.println("Current State:");

  Serial.print("theta = ");
  Serial.print(currentTheta1);
  Serial.print(", ");
  Serial.print(currentTheta2);
  Serial.print(", ");
  Serial.println(currentTheta3);

  Serial.print("servo cmd = ");
  Serial.print(currentCmd1);
  Serial.print(", ");
  Serial.print(currentCmd2);
  Serial.print(", ");
  Serial.println(currentCmd3);

  Serial.print("pump = ");
  Serial.println(pumpState ? "ON" : "OFF");
}
