#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <SoftwareSerial.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

SoftwareSerial BT(10, 11);   // Arduino RX, TX

String message = "";
String currentMessage = "";

unsigned long lastReceive = 0;

void setup() {

  Serial.begin(9600);
  BT.begin(9600);

  lcd.init();
  lcd.backlight();

  lcd.setCursor(0, 0);
  lcd.print("Bluetooth Ready");

  delay(2000);
  lcd.clear();
}

void loop() {

  // -----------------------------
  // Check for new Bluetooth data
  // -----------------------------

  while (BT.available()) {

    char c = BT.read();

    message += c;

    lastReceive = millis();

    Serial.print(c);
  }


  // -----------------------------
  // New message received
  // -----------------------------

  if (message.length() > 0 &&
      millis() - lastReceive > 500) {

    message.trim();

    if (message.length() > 0) {
      currentMessage = message;
    }

    message = "";
  }


  // -----------------------------
  // Keep scrolling current message
  // -----------------------------

  if (currentMessage.length() > 0) {

    scrollMessage(currentMessage);
  }
}


// ==========================================
// SCROLL MESSAGE
// ==========================================

void scrollMessage(String text) {

  String scrollText = "                ";
  scrollText += text;
  scrollText += "                ";

  int totalLength = scrollText.length();


  // Scroll from right to left
  for (int i = 0; i <= totalLength - 16; i++) {

    // --------------------------------
    // Check if a NEW Bluetooth message
    // has arrived
    // --------------------------------

    if (BT.available()) {
      return;
    }

    lcd.clear();

    lcd.setCursor(0, 0);

    lcd.print(scrollText.substring(i, i + 16));

    delay(300);
  }

  // Function finishes and loop()
  // starts it again automatically
}