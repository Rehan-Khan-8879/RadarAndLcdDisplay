#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <SoftwareSerial.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

SoftwareSerial BT(10, 11);   // we use arduino pin 10 RX and 11 as TX

String message = "";
String currentMessage = "";

unsigned long lastReceive = 0;

// setup
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


//    Loop code
void loop() {


  while (BT.available()) { //cheack for bluetooth

    char c = BT.read();

    message += c;

    lastReceive = millis();

    Serial.print(c);
  }




  if (message.length() > 0 &&
      millis() - lastReceive > 500) {

    message.trim();

    if (message.length() > 0) {
      currentMessage = message;
    }

    message = "";
  }




  if (currentMessage.length() > 0) {

    scrollMessage(currentMessage);
  }
}



// defined function for scrolling message to left
void scrollMessage(String text) {

  String scrollText = "                ";
  scrollText += text;
  scrollText += "                ";

  int totalLength = scrollText.length();


  // Scroll from right to left
  for (int i = 0; i <= totalLength - 16; i++) {



    if (BT.available()) {
      return;
    }

    lcd.clear();

    lcd.setCursor(0, 0);

    lcd.print(scrollText.substring(i, i + 16));

    delay(300);
  }


}
