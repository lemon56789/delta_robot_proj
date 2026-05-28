#include <Servo.h>

// =====================================================
// FT5330M Delta Robot Pick & Place State Machine
// Test/Prototype Firmware
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
const int VALVE_PIN = 7;  // MOSFET SIG for solenoid valve

// =====================
// Safe angle range
// 조립 직후에는 반드시 좁게 시작
// 실제 안전범위 측정 후 수정
// =====================
const int SERVO1_MIN = 70;
const int SERVO1_MAX = 110;

const int SERVO2_MIN = 70;
const int SERVO2_MAX = 110;

const int SERVO3_MIN = 70;
const int SERVO3_MAX = 110;

const int SERVO1_CENTER = 90;
const int SERVO2_CENTER = 90;
const int SERVO3_CENTER = 90;

// =====================
// Last commanded angles
// 실제 피드백값 아님. 마지막 명령값 저장용.
// =====================
int current1 = SERVO1_CENTER;
int current2 = SERVO2_CENTER;
int current3 = SERVO3_CENTER;

// =====================
// Motion parameters
// =====================
int defaultStepDelay = 20;      // ms, 처음에는 느리게
int suctionDelay = 200;         // ms, 흡착 안정화 시간
int releaseDelay = 200;         // ms, 배출 안정화 시간
int stateDelay = 100;           // ms, 상태 전환 사이 여유 시간

// =====================================================
// Temporary Pick & Place angle sets
// 실제 조립 후 반드시 수정해야 함
// =====================================================

// Home / safe pose
int HOME_A1 = 90;
int HOME_A2 = 90;
int HOME_A3 = 90;

// Pick upper position
int PICK_UP_A1 = 90;
int PICK_UP_A2 = 90;
int PICK_UP_A3 = 90;

// Pick lower position
int PICK_DOWN_A1 = 95;
int PICK_DOWN_A2 = 95;
int PICK_DOWN_A3 = 95;

// Place upper position
int PLACE_UP_A1 = 85;
int PLACE_UP_A2 = 95;
int PLACE_UP_A3 = 90;

// Place lower position
int PLACE_DOWN_A1 = 90;
int PLACE_DOWN_A2 = 100;
int PLACE_DOWN_A3 = 95;

// =====================================================
// State Machine
// =====================================================
enum State {
  IDLE,
  MOVE_TO_PICK_UP,
  MOVE_TO_PICK_DOWN,
  VACUUM_ON_STATE,
  LIFT_FROM_PICK,
  MOVE_TO_PLACE_UP,
  MOVE_TO_PLACE_DOWN,
  VACUUM_OFF_STATE,
  LIFT_FROM_PLACE,
  DONE,
  EMERGENCY_STOP
};

State currentState = IDLE;
bool cycleRunning = false;

// =====================================================
// Setup / Loop
// =====================================================
void setup() {
  Serial.begin(9600);

  setupVacuum();
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

  moveToHome();
  delay(1000);
}

void setupVacuum() {
  pinMode(PUMP_PIN, OUTPUT);
  pinMode(VALVE_PIN, OUTPUT);

  // 기본 OFF
  digitalWrite(PUMP_PIN, LOW);
  digitalWrite(VALVE_PIN, LOW);
}

// =====================================================
// Utility
// =====================================================
void printHelp() {
  Serial.println("====================================");
  Serial.println("Delta Robot Pick & Place Firmware");
  Serial.println("Commands:");
  Serial.println("HOME  : move to home position");
  Serial.println("START : run one pick & place cycle");
  Serial.println("STOP  : stop cycle and turn vacuum off");
  Serial.println("PON   : pump on");
  Serial.println("POFF  : pump off");
  Serial.println("VON   : valve on");
  Serial.println("VOFF  : valve off");
  Serial.println("STATE : print current state");
  Serial.println("====================================");
}

String stateToString(State s) {
  switch (s) {
    case IDLE: return "IDLE";
    case MOVE_TO_PICK_UP: return "MOVE_TO_PICK_UP";
    case MOVE_TO_PICK_DOWN: return "MOVE_TO_PICK_DOWN";
    case VACUUM_ON_STATE: return "VACUUM_ON_STATE";
    case LIFT_FROM_PICK: return "LIFT_FROM_PICK";
    case MOVE_TO_PLACE_UP: return "MOVE_TO_PLACE_UP";
    case MOVE_TO_PLACE_DOWN: return "MOVE_TO_PLACE_DOWN";
    case VACUUM_OFF_STATE: return "VACUUM_OFF_STATE";
    case LIFT_FROM_PLACE: return "LIFT_FROM_PLACE";
    case DONE: return "DONE";
    case EMERGENCY_STOP: return "EMERGENCY_STOP";
    default: return "UNKNOWN";
  }
}

void changeState(State nextState) {
  currentState = nextState;
  Serial.print("STATE -> ");
  Serial.println(stateToString(currentState));
  delay(stateDelay);
}

void printCurrentAngles() {
  Serial.print("Angles: ");
  Serial.print(current1);
  Serial.print(", ");
  Serial.print(current2);
  Serial.print(", ");
  Serial.println(current3);
}

// =====================================================
// Angle limit
// =====================================================
int limitAngle(int id, int angle) {
  if (id == 1) return constrain(angle, SERVO1_MIN, SERVO1_MAX);
  if (id == 2) return constrain(angle, SERVO2_MIN, SERVO2_MAX);
  if (id == 3) return constrain(angle, SERVO3_MIN, SERVO3_MAX);
  return angle;
}

// =====================================================
// Servo control
// =====================================================
void moveServo(int id, int angle) {
  angle = limitAngle(id, angle);

  if (id == 1) {
    servo1.write(angle);
    current1 = angle;
  } 
  else if (id == 2) {
    servo2.write(angle);
    current2 = angle;
  } 
  else if (id == 3) {
    servo3.write(angle);
    current3 = angle;
  } 
  else {
    Serial.println("Invalid servo id");
    return;
  }

  Serial.print("Servo ");
  Serial.print(id);
  Serial.print(" -> ");
  Serial.println(angle);
}

void moveAllServos(int a1, int a2, int a3) {
  a1 = limitAngle(1, a1);
  a2 = limitAngle(2, a2);
  a3 = limitAngle(3, a3);

  servo1.write(a1);
  servo2.write(a2);
  servo3.write(a3);

  current1 = a1;
  current2 = a2;
  current3 = a3;

  Serial.print("Move ALL -> ");
  Serial.print(a1);
  Serial.print(", ");
  Serial.print(a2);
  Serial.print(", ");
  Serial.println(a3);
}

void moveAllServosSmooth(int target1, int target2, int target3, int stepDelay) {
  target1 = limitAngle(1, target1);
  target2 = limitAngle(2, target2);
  target3 = limitAngle(3, target3);

  int start1 = current1;
  int start2 = current2;
  int start3 = current3;

  int diff1 = abs(target1 - start1);
  int diff2 = abs(target2 - start2);
  int diff3 = abs(target3 - start3);

  int maxDiff = max(diff1, max(diff2, diff3));

  if (maxDiff == 0) return;

  for (int step = 1; step <= maxDiff; step++) {
    int a1 = start1 + (target1 - start1) * step / maxDiff;
    int a2 = start2 + (target2 - start2) * step / maxDiff;
    int a3 = start3 + (target3 - start3) * step / maxDiff;

    servo1.write(a1);
    servo2.write(a2);
    servo3.write(a3);

    delay(stepDelay);
  }

  current1 = target1;
  current2 = target2;
  current3 = target3;

  Serial.print("Smooth Move -> ");
  Serial.print(target1);
  Serial.print(", ");
  Serial.print(target2);
  Serial.print(", ");
  Serial.println(target3);
}

// =====================================================
// Vacuum control
// MOSFET 모듈이 active LOW면 HIGH/LOW 반대로 수정
// =====================================================
void pumpOn() {
  digitalWrite(PUMP_PIN, HIGH);
  Serial.println("Pump ON");
}

void pumpOff() {
  digitalWrite(PUMP_PIN, LOW);
  Serial.println("Pump OFF");
}

void valveOn() {
  digitalWrite(VALVE_PIN, HIGH);
  Serial.println("Valve ON");
}

void valveOff() {
  digitalWrite(VALVE_PIN, LOW);
  Serial.println("Valve OFF");
}

// 실제 흡착 시퀀스
void vacuumOn() {
  // N.O 밸브 배관 기준은 실제 테스트 후 수정 필요
  pumpOn();
  valveOff();
  delay(suctionDelay);
  Serial.println("Vacuum suction ON");
}

void vacuumOff() {
  // 대기압 유입용 밸브 ON
  valveOn();
  delay(releaseDelay);

  // 시연 속도 높일 때는 pumpOff()를 제거하고 펌프 계속 ON 유지 가능
  pumpOff();

  Serial.println("Vacuum released");
}

// =====================================================
// Position presets
// =====================================================
void moveToHome() {
  Serial.println("Move to HOME");
  moveAllServosSmooth(HOME_A1, HOME_A2, HOME_A3, defaultStepDelay);
}

void moveToPickUp() {
  Serial.println("Move to PICK_UP");
  moveAllServosSmooth(PICK_UP_A1, PICK_UP_A2, PICK_UP_A3, defaultStepDelay);
}

void moveToPickDown() {
  Serial.println("Move to PICK_DOWN");
  moveAllServosSmooth(PICK_DOWN_A1, PICK_DOWN_A2, PICK_DOWN_A3, defaultStepDelay);
}

void moveToPlaceUp() {
  Serial.println("Move to PLACE_UP");
  moveAllServosSmooth(PLACE_UP_A1, PLACE_UP_A2, PLACE_UP_A3, defaultStepDelay);
}

void moveToPlaceDown() {
  Serial.println("Move to PLACE_DOWN");
  moveAllServosSmooth(PLACE_DOWN_A1, PLACE_DOWN_A2, PLACE_DOWN_A3, defaultStepDelay);
}

// =====================================================
// State Machine
// =====================================================
void runStateMachine() {
  switch (currentState) {
    case IDLE:
      cycleRunning = false;
      break;

    case MOVE_TO_PICK_UP:
      moveToPickUp();
      changeState(MOVE_TO_PICK_DOWN);
      break;

    case MOVE_TO_PICK_DOWN:
      moveToPickDown();
      changeState(VACUUM_ON_STATE);
      break;

    case VACUUM_ON_STATE:
      vacuumOn();
      changeState(LIFT_FROM_PICK);
      break;

    case LIFT_FROM_PICK:
      moveToPickUp();
      changeState(MOVE_TO_PLACE_UP);
      break;

    case MOVE_TO_PLACE_UP:
      moveToPlaceUp();
      changeState(MOVE_TO_PLACE_DOWN);
      break;

    case MOVE_TO_PLACE_DOWN:
      moveToPlaceDown();
      changeState(VACUUM_OFF_STATE);
      break;

    case VACUUM_OFF_STATE:
      vacuumOff();
      changeState(LIFT_FROM_PLACE);
      break;

    case LIFT_FROM_PLACE:
      moveToPlaceUp();
      changeState(DONE);
      break;

    case DONE:
      Serial.println("Pick & Place cycle DONE");
      moveToHome();
      currentState = IDLE;
      cycleRunning = false;
      break;

    case EMERGENCY_STOP:
      pumpOff();
      valveOff();
      cycleRunning = false;
      Serial.println("Emergency stop");
      break;
  }
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

  else if (cmd == "HOME") {
    cycleRunning = false;
    currentState = IDLE;
    moveToHome();
  }

  else if (cmd == "START") {
    Serial.println("Start Pick & Place Cycle");
    cycleRunning = true;
    changeState(MOVE_TO_PICK_UP);
  }

  else if (cmd == "STOP") {
    Serial.println("Stop command received");
    currentState = EMERGENCY_STOP;
    cycleRunning = true;
  }

  else if (cmd == "STATE") {
    Serial.print("Current State: ");
    Serial.println(stateToString(currentState));
    printCurrentAngles();
  }

  else if (cmd == "PON") {
    pumpOn();
  }

  else if (cmd == "POFF") {
    pumpOff();
  }

  else if (cmd == "VON") {
    valveOn();
  }

  else if (cmd == "VOFF") {
    valveOff();
  }

  else {
    Serial.println("Invalid command. Type HELP.");
  }
}