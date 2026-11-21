#include <Keyboard.h>

void setup() {
  Serial.begin(115200);
  Keyboard.begin();
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command.startsWith("PRESS:")) {
      char key = command.charAt(6);
      
      // Имитация человеческого зажатия клавиши (30–80 мс)
      Keyboard.press(key);
      delay(random(30, 80));
      Keyboard.release(key);
      
      Serial.println("OK");
    }
  }
}
