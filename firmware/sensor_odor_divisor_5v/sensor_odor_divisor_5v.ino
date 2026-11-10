#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <Preferences.h>

// --- Rede Wi-Fi Padrão (pode ser trocada pela Dashboard via USB sem regravar) ---
const char* DEFAULT_SSID = "SUA_REDE_WIFI_2.4G";
const char* DEFAULT_PASS = "SUA_SENHA_WIFI";

// --- Configurações do Broker MQTT ---
const char* mqtt_server = "broker.hivemq.com";
const int mqtt_port = 1883;
const char* mqtt_topic_data = "projeto/sensor_odor/banheiro_01/dados";
const char* device_label = "esp32_sensor_odor_01";

// Pino Analógico do Sensor MQ-137 (após divisor de tensão 10k + 10k)
const int mq137Pin = 34;

WiFiClient espClient;
PubSubClient client(espClient);
Preferences prefs;

String wifiSsid;
String wifiPass;
String mqttClientId;

unsigned long lastReadMs = 0;
unsigned long lastWifiTryMs = 0;
unsigned long lastMqttTryMs = 0;
unsigned long readingSeq = 0;

void connectWifiNonBlocking(bool forceRestart = false) {
  if (WiFi.status() == WL_CONNECTED && !forceRestart) return;
  if (forceRestart) {
    WiFi.disconnect(true);
    delay(100);
  }
  WiFi.mode(WIFI_STA);
  WiFi.begin(wifiSsid.c_str(), wifiPass.c_str());
  Serial.print("[WIFI] Tentando conectar em: ");
  Serial.println(wifiSsid);
}

void checkSerialCommands() {
  if (!Serial.available()) return;
  String line = Serial.readStringUntil('\n');
  line.trim();
  // Permite configurar Wi-Fi direto pela Dashboard: WIFI:NomeDaRede|Senha
  if (line.startsWith("WIFI:")) {
    String rest = line.substring(5);
    int sep = rest.indexOf('|');
    if (sep > 0) {
      wifiSsid = rest.substring(0, sep);
      wifiPass = rest.substring(sep + 1);
      prefs.begin("odor_cfg", false);
      prefs.putString("ssid", wifiSsid);
      prefs.putString("pass", wifiPass);
      prefs.end();
      Serial.print("[WIFI] Nova rede salva na memoria: ");
      Serial.println(wifiSsid);
      connectWifiNonBlocking(true);
    }
  } else if (line == "WIFI_RESET") {
    prefs.begin("odor_cfg", false);
    prefs.clear();
    prefs.end();
    wifiSsid = DEFAULT_SSID;
    wifiPass = DEFAULT_PASS;
    connectWifiNonBlocking(true);
  }
}

void maintainConnections() {
  unsigned long now = millis();

  if (WiFi.status() != WL_CONNECTED) {
    if (now - lastWifiTryMs >= 12000) {
      lastWifiTryMs = now;
      WiFi.reconnect();
    }
    return;
  }

  if (!client.connected()) {
    if (now - lastMqttTryMs >= 5000) {
      lastMqttTryMs = now;
      if (client.connect(mqttClientId.c_str())) {
        Serial.println("[MQTT] Conectado ao broker HiveMQ!");
      }
    }
  } else {
    client.loop();
  }
}

void setup() {
  Serial.begin(115200);
  delay(300);

  analogReadResolution(12);
  analogSetPinAttenuation(mq137Pin, ADC_11db);

  // Carrega Wi-Fi salvo na flash (Preferences) ou usa o padrão
  prefs.begin("odor_cfg", true);
  wifiSsid = prefs.getString("ssid", DEFAULT_SSID);
  wifiPass = prefs.getString("pass", DEFAULT_PASS);
  prefs.end();

  uint64_t chipid = ESP.getEfuseMac();
  mqttClientId = "esp32_mq137_" + String((uint32_t)(chipid >> 32), HEX) + String((uint32_t)chipid, HEX);

  client.setServer(mqtt_server, mqtt_port);

  Serial.println("=================================================");
  Serial.println("Firmware MQ-137 (5V + Divisor 10k/10k -> Pino D34)");
  Serial.println("Envio simultaneo via USB Serial e Wi-Fi MQTT");
  Serial.println("=================================================");

  connectWifiNonBlocking(false);
  // Aguarda até 3s no boot pelo Wi-Fi, mas NÃO trava caso o roteador esteja desligado
  unsigned long t0 = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - t0 < 3000) {
    delay(250);
    Serial.print(".");
  }
  Serial.println();
  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("[WIFI] Conectado! IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("[WIFI] Sem rede no momento — transmitindo via USB e tentando Wi-Fi em segundo plano.");
  }
}

void loop() {
  checkSerialCommands();
  maintainConnections();

  unsigned long now = millis();
  if (now - lastReadMs < 3000) {
    delay(20);
    return;
  }
  lastReadMs = now;
  readingSeq++;

  // 1. Média de 20 amostras no pino D34 para eliminar ruído
  long sum_adc = 0;
  for (int i = 0; i < 20; i++) {
    sum_adc += analogRead(mq137Pin);
    delay(5);
  }
  int raw_adc = sum_adc / 20;

  // 2. Matemática do Divisor de Tensão 10k + 10k (fator 2.0x)
  //    Tensão no pino D34: 0.00 a 2.50 V (limite seguro ESP32 = 3.30 V)
  //    Tensão real no AOUT do sensor: 0.00 a 5.00 V
  float pin_voltage = (raw_adc / 4095.0) * 3.3;
  float sensor_voltage = pin_voltage * 2.0;
  if (sensor_voltage > 5.0) sensor_voltage = 5.0;
  if (sensor_voltage < 0.0) sensor_voltage = 0.0;

  int intensity_percent = (int)round((sensor_voltage / 5.0) * 100.0);
  if (intensity_percent > 100) intensity_percent = 100;
  if (intensity_percent < 0) intensity_percent = 0;

  bool wifiOk = (WiFi.status() == WL_CONNECTED);
  bool mqttOk = (wifiOk && client.connected());

  // 3. Monta JSON compatível com a Dashboard (USB + MQTT)
  JsonDocument doc;
  doc["seq"] = readingSeq;
  doc["device_id"] = device_label;
  doc["raw_adc"] = raw_adc;
  doc["pin_v"] = serialized(String(pin_voltage, 2));
  doc["voltage_v"] = serialized(String(sensor_voltage, 2));
  doc["intensity_percent"] = intensity_percent;
  doc["sensor_status"] = "OK";
  doc["wifi_ok"] = wifiOk;
  doc["mqtt_ok"] = mqttOk;
  doc["wifi_ssid"] = wifiSsid;

  String payload;
  serializeJson(doc, payload);

  // Linha estruturada para leitura instantânea pela Dashboard via USB
  Serial.print("[TELEMETRIA_JSON] ");
  Serial.println(payload);

  // Saída legível para o Monitor Serial
  Serial.print("ADC: "); Serial.print(raw_adc);
  Serial.print(" | Pino D34: "); Serial.print(pin_voltage, 2); Serial.print("V");
  Serial.print(" | Sensor AOUT: "); Serial.print(sensor_voltage, 2); Serial.print("V");
  Serial.print(" | Odor: "); Serial.print(intensity_percent); Serial.print("%");
  Serial.print(" | WiFi: "); Serial.print(wifiOk ? "ON" : "OFF");
  Serial.print(" | MQTT: "); Serial.println(mqttOk ? "ON" : "OFF");

  // 4. Publica no HiveMQ caso o Wi-Fi esteja ativo
  if (mqttOk) {
    client.publish(mqtt_topic_data, payload.c_str());
  }
}
