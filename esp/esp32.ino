// ESP8266 için optimize edilmiş 2 step motor kontrolü
// Pin tanımları (NodeMCU LoLin V3'e göre)
#define YAW_STEP_PIN D1
#define YAW_DIR_PIN  D2
#define PITCH_STEP_PIN D5
#define PITCH_DIR_PIN  D6

// Değişkenler
String inputString = "";
bool stringComplete = false;
int delayTime = 1000; // Mikrosaniye cinsinden adım gecikmesi

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
    delayTime = map(speed, 0, 100, 5000, 500);
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
}

// ESP8266 için geliştirilmiş versiyon
void moveMotors(int yawSteps, int pitchSteps) {
  // Yön ayarla
  digitalWrite(YAW_DIR_PIN, yawSteps >= 0 ? LOW : HIGH);
  digitalWrite(PITCH_DIR_PIN, pitchSteps >= 0 ? HIGH : LOW);

  int absYaw = abs(yawSteps);
  int absPitch = abs(pitchSteps);
  int maxSteps = max(absYaw, absPitch);

  // Hız dengeleme için oran hesapla
  float yawRatio = maxSteps > 0 ? (float)absYaw / maxSteps : 0;
  float pitchRatio = maxSteps > 0 ? (float)absPitch / maxSteps : 0;
  
  float yawAccum = 0;
  float pitchAccum = 0;

  for (int i = 0; i < maxSteps; i++) {
    // Oransal adım atma (daha yumuşak hareket)
    yawAccum += yawRatio;
    pitchAccum += pitchRatio;
    
    if (yawAccum >= 1.0 && absYaw > 0) {
      digitalWrite(YAW_STEP_PIN, HIGH);
      yawAccum -= 1.0;
      absYaw--;
    }
    
    if (pitchAccum >= 1.0 && absPitch > 0) {
      digitalWrite(PITCH_STEP_PIN, HIGH);
      pitchAccum -= 1.0;
      absPitch--;
    }

    delayMicroseconds(delayTime);

    digitalWrite(YAW_STEP_PIN, LOW);
    digitalWrite(PITCH_STEP_PIN, LOW);

    delayMicroseconds(delayTime);
    
    // ESP8266 watchdog için
    if (i % 100 == 0) yield();
  }

  Serial.println("Hareket tamamlandı.");
}