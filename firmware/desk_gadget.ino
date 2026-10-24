// ============================================================
// ESP32 Desk Gadget — clock + indoor DHT11 + outdoor weather
// Board: ESP32-C3 SuperMini. Arduino IDE: "ESP32C3 Dev Module" with
// Tools > USB CDC On Boot: Enabled so Serial shows over the native USB-C
// connection (compile-verified on arduino-esp32 2.0.17). "Nologo ESP32C3
// Super Mini" (core 3.x, CDC on by default) is untested with this sketch.
// OLED SSD1306 128x64 I2C (0x3C) | encoder pages | pot dimming
// Weather: Open-Meteo (no API key). Time: NTP, configurable zone.
// See README.md and docs/ in this repo for wiring and build order.
// Pins are SuperMini-specific: I2C on GPIO 4/5 (NOT the risky
// strapping pins GPIO 8/9), encoder on 6/7/10, pot on ADC1 GPIO 1.
// ============================================================
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <DHT.h>
#include <WiFiClientSecure.h>
#include "time.h"

// ---------- Configuration: edit these before uploading ----------
// WiFi: must be a 2.4 GHz network (the ESP32-C3 has no 5 GHz radio).
const char* WIFI_SSID = "YOUR_WIFI_NAME";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
// Location: decimal degrees, IANA time-zone name, and the short label
// shown on the outdoor screen. The values below are an example
// (Toronto, Canada) — replace them with the target location.
const float LOCATION_LAT = 43.65;
const float LOCATION_LON = -79.36;
const char* LOCATION_TZ = "America/Toronto";
const char* LOCATION_NAME = "TORONTO";
// Local clock time: POSIX time-zone string for the location above
// (Eastern Time example). See docs/libraries-and-setup.md.
const char* TIMEZONE_POSIX = "EST5EDT,M3.2.0,M11.1.0";
#define WIFI_LOW_TX_POWER 0  // set to 1 if the board fails to join WiFi (common SuperMini antenna issue)

// ---------- Pins, ESP32-C3 SuperMini (see docs/wiring.md) ----------
#define OLED_SDA 4   // I2C via GPIO matrix; NOT GPIO 8 (strapping + onboard LED)
#define OLED_SCL 5   // NOT GPIO 9 (strapping + BOOT button)
#define DHT_PIN 3
#define ENC_CLK 6
#define ENC_DT 7
#define ENC_SW 10
#define POT_PIN 1    // ADC1_CH1. Do NOT use GPIO 5 (ADC2) for the pot: ADC2 is unreliable while WiFi is on.
#define PIR_PIN 0    // optional, only if USE_PIR is 1; GPIO 0-5 are RTC GPIOs
#define USE_PIR 0    // set to 1 after wiring the PIR

// ---------- Weather: Open-Meteo (no key), URL built from config ----------
String weatherUrl() {
  String url = "https://api.open-meteo.com/v1/forecast?latitude=";
  url += String(LOCATION_LAT, 4);
  url += "&longitude=";
  url += String(LOCATION_LON, 4);
  url += "&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m";
  url += "&timezone=";
  url += LOCATION_TZ;  // IANA names contain no characters needing encoding here
  return url;
}

// ---------- Objects ----------
Adafruit_SSD1306 display(128, 64, &Wire, -1);
DHT dht(DHT_PIN, DHT11);

// ---------- State ----------
int page = 0;  // 0 clock, 1 indoor, 2 weather, 3 summary
float inTemp = NAN, inHum = NAN;  // last GOOD DHT11 readings
float outTemp = NAN, outHum = NAN, outWind = NAN;
int outCode = -1;
bool weatherOK = false;
int contrast = 200;  // current OLED contrast 0-255
unsigned long lastDHT = 0, lastDraw = 0, lastPot = 0;
unsigned long lastWeatherTry = 0, lastWeatherOk = 0, lastStep = 0;
unsigned long lastBtn = 0, bootMs = 0;
bool weatherTried = false, lastFetchOk = false;
const time_t MIN_VALID_EPOCH = 1700000000;  // time(nullptr) below this means NTP has not synced
#if USE_PIR
unsigned long lastMotion = 0;
#endif
int lastCLK;
int lastSw = HIGH;  // previous encoder-button state, for edge detection

// ---------- WMO weather code -> text ----------
const char* codeText(int c) {
  switch (c) {
    case 0: return "Clear sky";
    case 1: return "Mainly clear";
    case 2: return "Partly cloudy";
    case 3: return "Overcast";
    case 45: return "Fog";
    case 48: return "Depositing rime fog";
    case 51: return "Light drizzle";
    case 53: return "Moderate drizzle";
    case 55: return "Dense drizzle";
    case 56: return "Light freezing drizzle";
    case 57: return "Dense freezing drizzle";
    case 61: return "Slight rain";
    case 63: return "Moderate rain";
    case 65: return "Heavy rain";
    case 66: return "Light freezing rain";
    case 67: return "Heavy freezing rain";
    case 71: return "Slight snowfall";
    case 73: return "Moderate snowfall";
    case 75: return "Heavy snowfall";
    case 77: return "Snow grains";
    case 80: return "Slight rain showers";
    case 81: return "Moderate rain showers";
    case 82: return "Violent rain showers";
    case 85: return "Slight snow showers";
    case 86: return "Heavy snow showers";
    case 95: return "Thunderstorm";
    case 96: return "Thunderstorm, slight hail";
    case 97: return "Heavy thunderstorm";
    case 99: return "Thunderstorm, heavy hail";
    default: return "-";
  }
}

void setContrast(int v) {
  v = constrain(v, 0, 255);
  display.ssd1306_command(SSD1306_SETCONTRAST);
  display.ssd1306_command(v);
}

// ---------- Weather fetch (MakerGuides pattern, Open-Meteo data) ----------
bool fetchWeather() {
  if (WiFi.status() != WL_CONNECTED) return false;
  bool ok = false;
  WiFiClientSecure client;
  client.setInsecure();  // TLS encrypts but does not verify the server certificate
  client.setHandshakeTimeout(4);  // seconds; the core default is 120 s
  HTTPClient http;
  http.setConnectTimeout(4000);
  http.setTimeout(4000);
  http.begin(client, weatherUrl());
  int code = http.GET();
  if (code == 200) {
    JsonDocument doc;  // ArduinoJson v7
    if (!deserializeJson(doc, http.getString())) {
      JsonObject cur = doc["current"];
      if (cur["temperature_2m"].is<float>() && cur["weather_code"].is<int>()) {
        outTemp = cur["temperature_2m"];
        outHum = cur["relative_humidity_2m"] | NAN;
        outWind = cur["wind_speed_10m"] | NAN;
        outCode = cur["weather_code"];
        weatherOK = true;
        lastWeatherOk = millis();
        ok = true;
      } else {
        Serial.println("Weather: missing fields");
      }
    } else {
      Serial.println("Weather: JSON parse failed");
    }
  } else {
    Serial.printf("Weather: HTTP %d\n", code);
  }
  http.end();
  return ok;
}

// ---------- Page drawing ----------
void header(const char* title) {
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  display.print(title);
  display.drawLine(0, 11, 127, 11, WHITE);
}

void drawPage() {
  struct tm t;
  time_t nowSec = time(nullptr);
  localtime_r(&nowSec, &t);
  bool haveTime = nowSec > MIN_VALID_EPOCH;
  display.clearDisplay();
  if (page == 0) {
    // ---- CLOCK ----
    header("CLOCK");
    display.setTextSize(3);
    display.setCursor(10, 20);
    if (haveTime) {
      display.printf("%02d:%02d", t.tm_hour, t.tm_min);
    } else {
      display.print("--:--");
    }
    display.setTextSize(1);
    display.setCursor(100, 34);
    if (haveTime) display.printf(":%02d", t.tm_sec);
    display.setCursor(0, 52);
    if (haveTime) {
      char buf[32];
      strftime(buf, sizeof(buf), "%a %d %b %Y", &t);
      display.print(buf);
    }
  } else if (page == 1) {
    // ---- INDOOR ----
    header("INDOOR - DHT11");
    display.setTextSize(2);
    display.setCursor(0, 18);
    if (isnan(inTemp)) {
      display.print("No reading");
    } else {
      display.printf("%.1f C", inTemp);
    }
    display.setCursor(0, 42);
    if (!isnan(inHum)) display.printf("%.0f %% RH", inHum);
  } else if (page == 2) {
    // ---- OUTDOOR ----
    {
      char buf[32];
      snprintf(buf, sizeof(buf), "%s - OPEN-METEO", LOCATION_NAME);
      header(buf);
    }
    display.setTextSize(1);
    display.setCursor(0, 16);
    if (!weatherOK) {
      display.print("Waiting for first fetch...");
    } else {
      display.printf("%.1f C", outTemp);
      if (!isnan(outHum)) display.printf("  %.0f %% RH", outHum);
      display.setCursor(0, 28);
      display.setTextWrap(true);
      display.print(codeText(outCode));
      display.setTextWrap(false);
      display.setCursor(0, 46);
      if (isnan(outWind)) display.print("Wind --");
      else display.printf("Wind %.0f km/h", outWind);
      display.setCursor(0, 54);
      display.printf("Updated %lu min ago", (millis() - lastWeatherOk) / 60000UL);
    }
  } else {
    // ---- SUMMARY / SETTINGS ----
    header("SUMMARY");
    display.setTextSize(1);
    display.setCursor(0, 13);
    if (haveTime) display.printf("Time %02d:%02d", t.tm_hour, t.tm_min);
    else display.print("Time --:--");
    display.setCursor(0, 21);
    if (isnan(inTemp) || isnan(inHum)) {
      display.print("In --");
    } else {
      display.printf("In %.1f C  %.0f %%", inTemp, inHum);
    }
    display.setCursor(0, 29);
    if (!weatherOK) display.print("Out --");
    else if (isnan(outHum)) display.printf("Out %.1f C", outTemp);
    else display.printf("Out %.1f C  %.0f %%", outTemp, outHum);
    display.setCursor(0, 37);
    display.printf("Bright %d / 255", contrast);
    display.setCursor(0, 45);
    display.printf("WiFi %s", WiFi.status() == WL_CONNECTED ? "connected" : "DOWN");
    display.setCursor(0, 53);
    display.printf("Up %lu min", (millis() - bootMs) / 60000UL);
  }
  // page dots
  for (int i = 0; i < 4; ++i) {
    display.fillRect(52 + i * 8, 61, 5, 2, i == page ? WHITE : BLACK);
  }
  display.display();
}

// ---------- Setup ----------
void setup() {
  Serial.begin(115200);
  bootMs = millis();
  Wire.begin(OLED_SDA, OLED_SCL);
  Wire.beginTransmission(0x3C);
  if (Wire.endTransmission() != 0) {
    while (true) {
      Serial.println("OLED not found at 0x3C - check wiring/address");
      delay(2000);
    }
  }
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C, true, false)) {  // false: keep Wire on GPIO 4/5
    while (true) {
      Serial.println("OLED init failed (out of memory)");
      delay(2000);
    }
  }
  display.setTextWrap(false);
  display.clearDisplay();
  display.display();
  setContrast(contrast);
  dht.begin();
  pinMode(ENC_CLK, INPUT_PULLUP);
  pinMode(ENC_DT, INPUT_PULLUP);
  pinMode(ENC_SW, INPUT_PULLUP);
  lastCLK = digitalRead(ENC_CLK);
#if USE_PIR
  pinMode(PIR_PIN, INPUT_PULLDOWN);
#endif
  // WiFi (30 s timeout, then continue), then NTP. The clock never blocks;
  // loop() starts the weather fetch as soon as WiFi is up (no NTP wait)
  // and retries every 60 s until it succeeds.
  display.clearDisplay();
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.print("Connecting WiFi...");
  display.display();
  Serial.println("WiFi: connecting...");
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
#if WIFI_LOW_TX_POWER
  WiFi.setTxPower(WIFI_POWER_8_5dBm);
#endif
  unsigned long wifiStart = millis();
  while (WiFi.status() != WL_CONNECTED &&
         millis() - wifiStart < 30000UL) {
    delay(250);
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("WiFi: connected");
  } else {
    Serial.println("WiFi: connection failed (30 s timeout) - continuing without WiFi");
  }
  configTzTime(TIMEZONE_POSIX, "pool.ntp.org", "time.nist.gov");
  drawPage();
}

// ---------- Loop: everything on millis() timers, never blocking ----------
void loop() {
  unsigned long now = millis();

  // --- Encoder rotation (polling: watch CLK, read DT for direction) ---
  int clk = digitalRead(ENC_CLK);
  if (clk != lastCLK && clk == LOW && now - lastStep >= 3) {  // CLK falling edge = one detent; 3 ms bounce guard
    lastStep = now;
    if (digitalRead(ENC_DT) != clk) {
      page = (page + 1) % 4;  // clockwise
    } else {
      page = (page + 3) % 4;  // counter-clockwise
    }
#if USE_PIR
    lastMotion = now;
#endif
    drawPage();
  }
  lastCLK = clk;

  // --- Encoder press (edge-triggered, 200 ms guard): jump to/from summary ---
  // Act only on the HIGH -> LOW transition, so holding the button
  // down does NOT re-trigger every 200 ms. A press jumps to Summary;
  // a second press returns to Clock. It does not step through pages.
  int sw = digitalRead(ENC_SW);
  if (sw == LOW && lastSw == HIGH && now - lastBtn > 200) {
    lastBtn = now;
    page = (page == 3) ? 0 : 3;
#if USE_PIR
    lastMotion = now;
#endif
    drawPage();
  }
  lastSw = sw;

  // --- Pot -> contrast (only touch the register when it changes) ---
  if (now - lastPot >= 50) {
    lastPot = now;
    int mv = constrain((int)analogReadMilliVolts(POT_PIN), 0, 2500);  // C3 ADC tops out at ~2.5 V
    int target = map(mv, 0, 2500, 8, 255);
    if (abs(target - contrast) > 4) {
      contrast = target;
      setContrast(contrast);
    }
  }

  // --- DHT11 every 2.5 s; keep last good values on a failed read ---
  if (now - lastDHT >= 2500) {
    lastDHT = now;
    float h = dht.readHumidity();
    float t = dht.readTemperature();
    if (!isnan(h) && !isnan(t)) {
      inHum = h;
      inTemp = t;
    }
  }

  // --- Weather: once WiFi is up; every 10 min after success, 60 s after a failure ---
  if (WiFi.status() == WL_CONNECTED &&
      (!weatherTried || now - lastWeatherTry >= (lastFetchOk ? 600000UL : 60000UL))) {
    weatherTried = true;
    lastWeatherTry = now;
    lastFetchOk = fetchWeather();
  }

#if USE_PIR
  // --- PIR: blank the panel 60 s after the room goes quiet ---
  if (digitalRead(PIR_PIN) == HIGH) lastMotion = now;
  bool awake = (now - lastMotion < 60000UL);
  static bool wasAwake = true;
  if (awake != wasAwake) {
    wasAwake = awake;
    display.ssd1306_command(awake ? SSD1306_DISPLAYON : SSD1306_DISPLAYOFF);
  }
#endif

  // --- Redraw once a second (the clock's seconds need it) ---
  if (now - lastDraw >= 1000) {
    lastDraw = now;
#if USE_PIR
    if (awake)
#endif
      drawPage();
  }

  delay(1);  // yield so IDLE/WiFi tasks run on the single-core C3
}
