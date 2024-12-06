#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include <WebServer.h>
#include "camera_pins.h"

#define CAMERA_MODEL_AI_THINKER // Defina o modelo da câmera
#define LED_BUILTIN 4

const char* ssid = "SSID";
const char* password = "PASSWORD";

const char* apiUrl = "API_ADDRESS/upload";

void setup() {

  Serial.begin(115200);

  pinMode (LED_BUILTIN, OUTPUT);

  // camera settings
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_QVGA; // resolution
  config.pixel_format = PIXFORMAT_JPEG; // JPEG format
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 20; // image quality from 0 to 63
  config.fb_count = 1;

  // Camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Error: 0x%x\n", err);
    return;
  }

  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Conectando ao Wi-Fi...");
  }
  Serial.println("Conectado ao Wi-Fi.");
}

void loop() {
  if (Serial.available()) {
    char command = Serial.read();
    if (command == 'C') { // command to capture and send photo, sent by the arduino
      digitalWrite(LED_BUILTIN, HIGH);
      for (int i = 0; i < 5; i++) {
       
        if (takeAndSendPhoto()) {
          Serial.printf("Photo %d sent successfuly.\n", i + 1);
        } else {
          Serial.printf("Errr sending %d.\n", i + 1);
        }
        delay(1000); // wait 1 second before taking the next photo
      }
      digitalWrite(LED_BUILTIN, LOW);
    }
  }
}


// send photo to the server
bool sendPhoto(camera_fb_t* fb) {
  if (!fb || WiFi.status() != WL_CONNECTED) return false;

  HTTPClient http;
  http.begin(apiUrl);
  http.addHeader("Content-Type", "application/octet-stream");

  int httpResponseCode = http.POST(fb->buf, fb->len);
  if (httpResponseCode <= 0) {
    Serial.printf("Erro HTTP: %d\n", httpResponseCode);
  }
  http.end();

  if (httpResponseCode > 0) {
    Serial.printf("Server response: %d\n", httpResponseCode);
    return true;
  } else {
    Serial.println("Fail sending image.");
    return false;
  }
}

// capture and send photo
bool takeAndSendPhoto() {

  camera_fb_t* fb = takePhoto();
  if (!fb) {
    return false;
  }

  bool result = sendPhoto(fb);
  esp_camera_fb_return(fb); // free the memory used by the photo

  // verify if the photo was sent
  if (!result) {
    Serial.println("Fail sending photo. Try again...");
    return false;
  }

  return true;
}
