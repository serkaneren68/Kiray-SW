// Basit Step Motor Kontrolü - ENA pinsiz
// Step ve Direction pinleri tanımlamaları
#define YAW_STEP_PIN 6
#define YAW_DIR_PIN 7
#define PITCH_STEP_PIN 2
#define PITCH_DIR_PIN 3

// Değişkenler
String inputString = "";
boolean stringComplete = false;
int delayTime = 1000; // Mikrosaniye cinsinden adım gecikmesi

void setup() {
  Serial.begin(9600);
  
  // Pin modlarını ayarla
  pinMode(YAW_STEP_PIN, OUTPUT);
  pinMode(YAW_DIR_PIN, OUTPUT);
  pinMode(PITCH_STEP_PIN, OUTPUT);
  pinMode(PITCH_DIR_PIN, OUTPUT);
  
  // Başlangıç durumu
  digitalWrite(YAW_STEP_PIN, LOW);
  digitalWrite(YAW_DIR_PIN, LOW);
  digitalWrite(PITCH_STEP_PIN, LOW);
  digitalWrite(PITCH_DIR_PIN, LOW);
  
  Serial.println("Arduino hazır - ENA pinsiz mod");
}

void loop() {
  // Seri porttan komut geldi mi?
  if (stringComplete) {
    processCommand(inputString);
    inputString = "";
    stringComplete = false;
  }
}

void processCommand(String cmd) {
  cmd.trim();
  Serial.print("Gelen komut: ");
  Serial.println(cmd);
  
  if (cmd == "X") {
    // DUR - Zaten duruyoruz, bir şey yapmaya gerek yok
    Serial.println("Motorlar durduruldu");
  }
  else if (cmd == "H") {
    // HOME - Basit bir home hareketi
    Serial.println("Home pozisyonuna dönülüyor");
    // Home için örnek hareket (isteğe bağlı)
  }
  else if (cmd.startsWith("V")) {
    // Hız ayarı
    int speed = cmd.substring(1).toInt();
    // Hızı delay'e çevir (ters orantılı)
    delayTime = map(speed, 0, 100, 5000, 500);
    Serial.print("Hız ayarlandı: ");
    Serial.println(speed);
  }
  else if (cmd.startsWith("M")) {
    // Direkt hareket: M100,-50
    int commaIndex = cmd.indexOf(',');
    if (commaIndex > 1) {
      int yawSteps = cmd.substring(1, commaIndex).toInt();
      int pitchSteps = cmd.substring(commaIndex + 1).toInt();
      
      Serial.print("Hareket başlatılıyor - Yaw: ");
      Serial.print(yawSteps);
      Serial.print(", Pitch: ");
      Serial.println(pitchSteps);
      
      // Aynı anda iki motoru hareket ettir
      moveMotors(yawSteps, pitchSteps);
    }
  }
  else if (cmd == "U") {
    moveMotors(0, 10);  // Sadece pitch yukarı
  }
  else if (cmd == "D") {
    moveMotors(0, -10); // Sadece pitch aşağı
  }
  else if (cmd == "L") {
    moveMotors(-10, 0); // Sadece yaw sol
  }
  else if (cmd == "R") {
    moveMotors(10, 0);  // Sadece yaw sağ
  }
}

void moveMotors(int yawSteps, int pitchSteps) {
  // Yön ayarla
  digitalWrite(YAW_DIR_PIN, yawSteps >= 0 ? LOW : HIGH);  // HIGH ve LOW yer değiştirdi
  digitalWrite(PITCH_DIR_PIN, pitchSteps >= 0 ? HIGH : LOW);
  
  // Mutlak değerleri al
  int absYaw = abs(yawSteps);
  int absPitch = abs(pitchSteps);
  
  // Hangi motor daha fazla adım atacak?
  int maxSteps = max(absYaw, absPitch);
  
  // Her iki motoru aynı anda hareket ettir
  for (int i = 0; i < maxSteps; i++) {
    // Yaw motoru adım at
    if (i < absYaw) {
      digitalWrite(YAW_STEP_PIN, HIGH);
    }
    
    // Pitch motoru adım at
    if (i < absPitch) {
      digitalWrite(PITCH_STEP_PIN, HIGH);
    }
    
    delayMicroseconds(delayTime);
    
    // Pinleri LOW yap
    digitalWrite(YAW_STEP_PIN, LOW);
    digitalWrite(PITCH_STEP_PIN, LOW);
    
    delayMicroseconds(delayTime);
  }
  
  Serial.println("Hareket tamamlandı");
}

// Tek motor hareketi için yardımcı fonksiyon
void stepMotor(int stepPin, int dirPin, int steps) {
  digitalWrite(dirPin, steps >= 0 ? HIGH : LOW);
  int absSteps = abs(steps);
  
  for (int i = 0; i < absSteps; i++) {
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(delayTime);
    digitalWrite(stepPin, LOW);
    delayMicroseconds(delayTime);
  }
}

// Seri port veri alma
void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar == '\n') {
      stringComplete = true;
    } else {
      inputString += inChar;
    }
  }
}