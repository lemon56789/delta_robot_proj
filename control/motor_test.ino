#include <Servo.h>

// =====================
// Servo object bhjkfj
// =====================
Servo servo1;
Servo servo2;
Servo servo3;

// =====================
// Pin setting
// =====================
const int PUMP_PIN = 6;
const int VALVE_PIN = 7;
const int SERVO1_PIN = 9;
const int SERVO2_PIN = 10;
const int SERVO3_PIN = 11;

// =====================
// Safe angle range
// 처음 테스트는 좁은 범위에서
// 실제 조립 완료 후 물리적 허용 범위 체크
// =====================
const int SERVO_MIN = 50;
const int SERVO_MAX = 130;
const int SERVO_CENTER = 90;

// =====================
// Last commanded angles
// =====================
int current1 = SERVO_CENTER;
int current2 = SERVO_CENTER;
int current3 = SERVO_CENTER;

void setup() {
  Serial.begin(9600);
  
  pinMode(PUMP_PIN, OUTPUT);
  pinMode(VALVE_PIN, OUTPUT);

  digitalWrite(PUMP_PIN, LOW);
  digitalWrite(VALVE_PIN, LOW);

  setupServos();

  Serial.println("FT5330M Servo Test Start");
  Serial.println("Commands:");
  Serial.println("1 angle       ex) 1 100");
  Serial.println("2 angle       ex) 2 80");
  Serial.println("3 angle       ex) 3 120");
  Serial.println("ALL a1 a2 a3  ex) ALL 90 90 90");
  Serial.println("SWEEP");
  Serial.println("CENTER");
  Serial.println("PON / POFF");
  Serial.println("VON / VOFF");
}

void loop() {
  readSerialCommand();
}

void setupServos() { // Initial posture for all motors
  servo1.attach(SERVO1_PIN);
  servo2.attach(SERVO2_PIN);
  servo3.attach(SERVO3_PIN);

  moveAllServos(SERVO_CENTER, SERVO_CENTER, SERVO_CENTER);

  delay(1000);
}

int limitAngle(int angle) { // Limit the angle for all motors
  if (angle < SERVO_MIN) return SERVO_MIN;
  if (angle > SERVO_MAX) return SERVO_MAX;
  return angle;
}

void moveServo(int id, int angle) { // Motor angle control
  angle = limitAngle(angle);

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
    Serial.println("Invalid servo id. Use 1, 2, or 3.");
    return;
  }

  Serial.print("Servo ");
  Serial.print(id);
  Serial.print(" -> ");
  Serial.println(angle);
}

void moveAllServos(int a1, int a2, int a3) {
  a1 = limitAngle(a1);
  a2 = limitAngle(a2);
  a3 = limitAngle(a3);

  servo1.write(a1);
  servo2.write(a2);
  servo3.write(a3);

  current1 = a1;
  current2 = a2;
  current3 = a3;

  Serial.print("ALL -> ");
  Serial.print(a1);
  Serial.print(", ");
  Serial.print(a2);
  Serial.print(", ");
  Serial.println(a3);
}

void moveAllServosSmooth(int target1, int target2, int target3, int stepDelay) {
  target1 = limitAngle(target1);
  target2 = limitAngle(target2);
  target3 = limitAngle(target3);

  int start1 = current1;
  int start2 = current2;
  int start3 = current3;

  int maxDiff = max(abs(target1 - start1), max(abs(target2 - start2), abs(target3 - start3)));

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

  Serial.print("SMOOTH ALL -> ");
  Serial.print(target1);
  Serial.print(", ");
  Serial.print(target2);
  Serial.print(", ");
  Serial.println(target3);
}

void readSerialCommand() {
  if (Serial.available() == 0) return;

  String cmd = Serial.readStringUntil('\n');
  cmd.trim();

  if (cmd.length() == 0) return;

  if (cmd == "CENTER") {
    moveAllServosSmooth(SERVO_CENTER, SERVO_CENTER, SERVO_CENTER, 15);
  }

  else if (cmd == "SWEEP") {
    sweepTest();
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

  else if (cmd.startsWith("ALL")) {
    int a1, a2, a3;
    int parsed = sscanf(cmd.c_str(), "ALL %d %d %d", &a1, &a2, &a3);

    if (parsed == 3) {
      moveAllServosSmooth(a1, a2, a3, 15);
    } else {
      Serial.println("Invalid ALL command. Use: ALL 90 90 90");
    }
  }

  else {
    int id, angle;
    int parsed = sscanf(cmd.c_str(), "%d %d", &id, &angle);

    if (parsed == 2) {
      moveServo(id, angle);
    } else {
      Serial.println("Invalid command.");
    }
  }
}

void sweepTest() { // Sweep Test (가동범위 체크용)
  Serial.println("Sweep test start");

  moveAllServosSmooth(70, 70, 70, 20);
  delay(500);

  moveAllServosSmooth(110, 110, 110, 20);
  delay(500);

  moveAllServosSmooth(90, 90, 90, 20);
  delay(500);

  Serial.println("Sweep test end");
}

void pumpOn() { // Pump on 코드
  digitalWrite(PUMP_PIN, HIGH);
  Serial.println("Pump ON");
}

void pumpOff() { // Pump off 코드(기본모드)
  digitalWrite(PUMP_PIN, LOW);
  Serial.println("Pump OFF");
}

void valveOn() { // Open the valve
  digitalWrite(VALVE_PIN, HIGH);
  Serial.println("Valve ON");
}

void valveOff() { // Close the valve(기본모드)
  digitalWrite(VALVE_PIN, LOW);
  Serial.println("Valve OFF");
}
