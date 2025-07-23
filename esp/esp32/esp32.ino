
#include <Servo.h>

Servo myServo;

// ESP8266 için optimize edilmiş 2 step motor kontrolü
// Pin tanımları (NodeMCU LoLin V3'e göre)
#define YAW_STEP_PIN D1
#define YAW_DIR_PIN  D2
#define PITCH_STEP_PIN D5
#define PITCH_DIR_PIN  D6

// Değişkenler
String inputString = "";
bool stringComplete = false;
int delayTime = 500; // Mikrosaniye cinsinden adım gecikmesi


// Global değişken ekle
int dynamicDelay = 500;  // Varsayılan

void setup() {
  Serial.begin(9600);

  // Pin modları
  pinMode(YAW_STEP_PIN, OUTPUT);
  pinMode(YAW_DIR_PIN, OUTPUT);
  pinMode(PITCH_STEP_PIN, OUTPUT);
  pinMode(PITCH_DIR_PIN, OUTPUT);

  // Başlangıç durumu
  digitalWrite(YAW_STEP_PIN, LOW);
  digitalWrite(YAW_DIR_PIN, LOW);
  digitalWrite(PITCH_STEP_PIN, LOW);
  digitalWrite(PITCH_DIR_PIN, LOW);

  myServo.attach(2);

  Serial.println("ESP Hazır - Motor kontrol bekleniyor...");
}

void loop() {
  // Seri veriyi oku
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar == '\n') {
      stringComplete = true;
    } else {
      inputString += inChar;
    }
  }

  if (stringComplete) {
    processCommand(inputString);
    inputString = "";
    stringComplete = false;
  }
}

void processCommand(String cmd) {
  cmd.trim(); // boşlukları sil
  Serial.print("Gelen komut: ");
  Serial.println(cmd);

  if (cmd == "X") {
    Serial.println("Motorlar durduruldu.");
  }
  else if (cmd == "H") {
    Serial.println("Home pozisyonuna dönülüyor...");
    // İsteğe bağlı home hareketi
  }
  else if (cmd.startsWith("V")) {
    int speed = cmd.substring(1).toInt();
    delayTime = map(speed, 0, 100, 2000, 200);
    Serial.print("Hız ayarlandı: ");
    Serial.println(speed);
  }
  else if (cmd.startsWith("M")) {
    int commaIndex = cmd.indexOf(',');
    if (commaIndex > 1) {
      int yawSteps = cmd.substring(1, commaIndex).toInt();
      int pitchSteps = cmd.substring(commaIndex + 1).toInt();
      Serial.print("Hareket: Yaw=");
      Serial.print(yawSteps);
      Serial.print(", Pitch=");
      Serial.println(pitchSteps);
      moveMotors(yawSteps, pitchSteps);
    }
  }
  else if (cmd == "U") {
    moveMotors(0, 80);
  }
  else if (cmd == "D") {
    moveMotors(0, -80);
  }
  else if (cmd == "L") {
    moveMotors(-80, 0);
  }
  else if (cmd == "R") {
    moveMotors(80, 0);
  }
  else if (cmd == "S") {
    myServo.write(180);      // Saat yönünde dön
    delay(2000);             // ~1 saniye döndür (ayar yapman gerekebilir)
    myServo.write(90);       // Durdur
  }
}

void moveMotors(int yawSteps, int pitchSteps) {
  // Büyük hareketler için hızlı, küçük hareketler için yavaş
  int totalSteps = abs(yawSteps) + abs(pitchSteps);
  
  if (totalSteps > 100) {
    dynamicDelay = 300;  // Hızlı
  } else if (totalSteps < 30) {
    dynamicDelay = 800;  // Yavaş (hassas)
  } else {
    dynamicDelay = 500;  // Normal
  }
  
  digitalWrite(YAW_DIR_PIN, yawSteps >= 0 ? LOW : HIGH);
  digitalWrite(PITCH_DIR_PIN, pitchSteps >= 0 ? HIGH : LOW);

  int absYaw = abs(yawSteps);
  int absPitch = abs(pitchSteps);
  int maxSteps = max(absYaw, absPitch);

  for (int i = 0; i < maxSteps; i++) {
    if (i < absYaw) digitalWrite(YAW_STEP_PIN, HIGH);
    if (i < absPitch) digitalWrite(PITCH_STEP_PIN, HIGH);

    delayMicroseconds(dynamicDelay);

    digitalWrite(YAW_STEP_PIN, LOW);
    digitalWrite(PITCH_STEP_PIN, LOW);

    delayMicroseconds(dynamicDelay);
    
    if (i % 100 == 0) yield();
  }

  Serial.print("Hareket tamamlandı. Hız: ");
  Serial.println(dynamicDelay);
}