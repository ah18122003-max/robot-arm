#include <Servo.h>

const byte SERVO_COUNT = 4;
const byte SERVO_PINS[SERVO_COUNT] = {3, 5, 6, 9};

Servo servos[SERVO_COUNT];
int currentAngles[SERVO_COUNT] = {90, 90, 90, 90};

char inputBuffer[64];
byte inputIndex = 0;

void applyAngles(int values[]) {
  for (byte i = 0; i < SERVO_COUNT; i++) {
    values[i] = constrain(values[i], 0, 180);
    currentAngles[i] = values[i];
    servos[i].write(currentAngles[i]);
  }
}

void parseLine(char *line) {
  int values[SERVO_COUNT];
  byte count = 0;
  char *token = strtok(line, ",");

  while (token != NULL && count < SERVO_COUNT) {
    values[count++] = atoi(token);
    token = strtok(NULL, ",");
  }

  if (count == SERVO_COUNT && token == NULL) {
    applyAngles(values);
    Serial.println("OK");
  } else {
    Serial.println("ERR");
  }
}

void setup() {
  Serial.begin(115200);
  for (byte i = 0; i < SERVO_COUNT; i++) {
    servos[i].attach(SERVO_PINS[i]);
    servos[i].write(currentAngles[i]);
  }
  Serial.println("ARM_READY");
}

void loop() {
  while (Serial.available() > 0) {
    char c = Serial.read();

    if (c == '\n' || c == '\r') {
      if (inputIndex > 0) {
        inputBuffer[inputIndex] = '\0';
        parseLine(inputBuffer);
        inputIndex = 0;
      }
    } else if (inputIndex < sizeof(inputBuffer) - 1) {
      inputBuffer[inputIndex++] = c;
    } else {
      inputIndex = 0;
      Serial.println("ERR_BUFFER");
    }
  }
}
