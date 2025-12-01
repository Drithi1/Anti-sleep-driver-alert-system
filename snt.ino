#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <TinyGPS++.h>


#define BUZZER_PIN 23

#define OLED_SCL 22


#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64


// --- OBJECT INITIALIZATION ---

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);


TinyGPSPlus gps;

void setup() {

  Serial.begin(9600);


  Serial2.begin(9600);

  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW); 
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;); 
  }

  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  display.println("Drowsiness Alert System");
  display.println("System Ready");
  display.println("Waiting for GPS signal...");
  display.display();
  delay(2000);
}

void loop() {
  
  if (Serial.available() > 0) {
    char command = Serial.read();
    if (command == 'A') {
      trigger_alert();
    }
  }

 
  while (Serial2.available() > 0) {
    gps.encode(Serial2.read());
  }

 
  if (gps.location.isUpdated()) {
    display_gps_info();
  }
}


void trigger_alert() {
  Serial.println("Alert received! Triggering actuators.");

  // Turn buzzer on
  digitalWrite(BUZZER_PIN, HIGH);

  display.clearDisplay();
  display.setTextSize(2);
  display.setCursor(10, 10);
  display.println("WAKE UP!");
  display.setTextSize(1);
  display.setCursor(10, 40);

  display.print("Lat: "); display.println(gps.location.lat(), 6);
  display.print("Lng: "); display.println(gps.location.lng(), 6);
  display.display();

 
  delay(3000);

  
  digitalWrite(BUZZER_PIN, LOW);
  
  
  display.clearDisplay();
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println("System Ready");
  display.display();
}

void display_gps_info() {
  display.clearDisplay();
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println("System Ready");
  display.println("GPS Lock Acquired");
  display.println("---------------------");
  display.print("Lat: ");
  display.println(gps.location.lat(), 6);
  display.print("Lng: ");
  display.println(gps.location.lng(), 6);
  display.print("Satellites: ");
  display.println(gps.satellites.value());
  display.display();
}