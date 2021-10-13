
// define motor outputs
#define LMP 3
#define LMN 4

#define RMP 6
#define RMN 7

void setup() {
  // put your setup code here, to run once:
  pinMode(LMP, OUTPUT);
  pinMode(LMN, OUTPUT);
  pinMode(RMP, OUTPUT);
  pinMode(RMN, OUTPUT);

}

void loop() {
  // put your main code here, to run repeatedly:
  spinLeft();
  delay(5000);
  //spinRight();
  delay(5000);
  //goForward();
  delay(5000);
  //goBackward();
  delay(5000);
  //stopHere();
  delay(5000);
}


void spinLeft() {
  digitalWrite(LMP, 1);
  digitalWrite(LMN, 0);
  digitalWrite(RMP, 1);
  digitalWrite(RMN, 0);
}

void spinRight() {
  digitalWrite(LMP, 0);
  digitalWrite(LMN, 1);
  digitalWrite(RMP, 0);
  digitalWrite(RMN, 1);
}

void goForward() {
  digitalWrite(LMP, 0);
  digitalWrite(LMN, 1);
  digitalWrite(RMP, 1);
  digitalWrite(RMN, 0);
}

void goBackward() {
  digitalWrite(LMP, 1);
  digitalWrite(LMN, 0);
  digitalWrite(RMP, 0);
  digitalWrite(RMN, 1);
}

void stopHere() {
  digitalWrite(LMP, 0);
  digitalWrite(LMN, 0);
  digitalWrite(RMP, 0);
  digitalWrite(RMN, 0);
}
