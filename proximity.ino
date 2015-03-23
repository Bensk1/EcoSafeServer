const int pwPin = 3; 
long pulse, inches, cm;

void setup() {
  Serial.begin(9600);
  Serial.print("GO");
  Serial.println();
}

void loop() {
  pinMode(pwPin, INPUT);
  pulse = pulseIn(pwPin, HIGH);
  inches = pulse/147;
  cm = inches * 2.54;
  if (cm < 20) {
    Serial.print(cm);
    Serial.print("cm");
    Serial.println();
    delay(2000);
  }
  delay(100);
}
