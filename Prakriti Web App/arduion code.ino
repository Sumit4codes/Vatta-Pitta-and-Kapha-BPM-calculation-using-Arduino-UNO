#include <LiquidCrystal.h>

LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

void setup() {
  Serial.begin(9600); // Initialize serial communication
  lcd.begin(16, 2);
  // Print initial messages on the LCD
  lcd.print("Collecting Data");
  lcd.setCursor(0, 1); // Move cursor to the second row
  lcd.print("Place on Wrist");
}

void loop() {
  int vattaValue = analogRead(A0); // Read the analog value for Vatta from pin A0
  int pittaValue = analogRead(A1); // Read the analog value for Pitta from pin A1
  int kaphaValue = analogRead(A2); // Read the analog value for Kapha from pin A2

  // Send the sensor values over serial in the format: "Vatta,Pitta,Kapha"
  Serial.print(vattaValue);
  Serial.print(",");
  Serial.print(pittaValue);
  Serial.print(",");
  Serial.println(kaphaValue);

  delay(10); // Add a small delay to avoid overwhelming the serial buffer
}
