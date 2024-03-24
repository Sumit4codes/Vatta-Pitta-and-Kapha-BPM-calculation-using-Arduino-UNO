//#include <Wire.h>
//#include <LiquidCrystal.h>

const int vatta_pin = A0;
const int pitta_pin = A1;
const int kapha_pin = A3;

const int vatta_threshold = 200;
const int pitta_threshold = 200;
const int kapha_threshold = 200;

int vatta_beats = 0;
int pitta_beats = 0;
int kapha_beats = 0;

unsigned long previousmillis_vatta = 0;
unsigned long previousmillis_pitta = 0;
unsigned long previousmillis_kapha = 0;

const int interval = 10000;

//LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

void setup() {
  Serial.begin(9600);
  //lcd.begin(16, 2);
}

void loop() {
  int vatta_value = analogRead(vatta_pin);
  int pitta_value = analogRead(pitta_pin);
  int kapha_value = analogRead(kapha_pin);

  unsigned long currentmillis_vatta = millis();
  unsigned long currentmillis_pitta = millis();
  unsigned long currentmillis_kapha = millis();

  if (currentmillis_vatta - previousmillis_vatta >= interval) {
    //float vatta_bpm = (vatta_beats * 60.0) / (currentmillis_vatta - previousmillis_vatta);
    float vatta_bpm = (10/vatta_beats)*60;
    Serial.println("Vatta: " + String(vatta_bpm));
    previousmillis_vatta = currentmillis_vatta;
    vatta_beats = 0;
  }

  if (currentmillis_pitta - previousmillis_pitta >= interval) {
    //float pitta_bpm = (pitta_beats * 60.0) / (currentmillis_pitta - previousmillis_pitta);
    float pitta_bpm = (10/pitta_beats)*60;
    Serial.println("Pitta: " + String(pitta_bpm));
    previousmillis_pitta = currentmillis_pitta;
    pitta_beats = 0;
  }

  if (currentmillis_kapha - previousmillis_kapha >= interval) {
    //float kapha_bpm = (kapha_beats * 60.0) / (currentmillis_kapha - previousmillis_kapha);
    float kapha_bpm = (10/kapha_beats)*60;
    Serial.println("Kapha: " + String(kapha_bpm));
    previousmillis_kapha = currentmillis_kapha;
    kapha_beats = 0;
  }

  if (vatta_value >= vatta_threshold) {
    vatta_beats++;
  }
  if (pitta_value >= pitta_threshold) {
    pitta_beats++;
  }
  if (kapha_value >= kapha_threshold) {
    kapha_beats++;
  }
}