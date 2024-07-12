const int mosfetGatePin = 9;

void setup() {
  pinMode(mosfetGatePin, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    if (c == '1') {
      digitalWrite(mosfetGatePin, HIGH);
      delay(1000);
      digitalWrite(mosfetGatePin, LOW);
    } else if (c == '0') {
      digitalWrite(mosfetGatePin, LOW);
    }
  }
}
