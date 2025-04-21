#include <Servo.h>
#include <SoftwareSerial.h>

#define BT_RX 18
#define BT_TX 19

Servo servox;
Servo servoy;

String dataFromBluetooth = "dont shoot";  // Переменная для хранения текущего значения от Bluetooth
String currentBluetoothState = "";   // Переменная для хранения текущего состояния

int MaxSpd = 160;

int ind_of_object;

int past_angle_x = 90;
int past_angle_y = 90;
int angle_x;
int angle_y;

const int sveto_pin = 13;

const int FwdPin_A = 6;
const int BwdPin_A = 7;

const int numReadings = 5; // Количество значений для скользящего среднего

int readings_x[numReadings]; // Массив для хранения значений angle_x
int readings_y[numReadings]; // Массив для хранения значений angle_y

int readIndex_x = 0;         // Текущий индекс для angle_x
int readIndex_y = 0;         // Текущий индекс для angle_y

int total_x = 0;             // Сумма значений angle_x
int total_y = 0;             // Сумма значений angle_y

int average_x = 0;           // Среднее значение angle_x
int average_y = 0;           // Среднее значение angle_y

unsigned long lastBluetoothCheckTime = 0;  // Время последнего выполнения блока Bluetooth
const unsigned long bluetoothCheckInterval = 5000;  // Интервал проверки Bluetooth (5 секунд)

void setup() {
  servox.attach(10);  // Сервопривод X на пин 10
  servoy.attach(11);   // Сервопривод Y на пин 11

  pinMode(FwdPin_A, OUTPUT);
  pinMode(BwdPin_A, OUTPUT);

  Serial.begin(115200);
  delay(3000);
  Serial1.begin(9600);

  pinMode(sveto_pin, 1);

  digitalWrite(sveto_pin, 1);

  // Инициализация массивов для скользящего среднего
  for (int i = 0; i < numReadings; i++) {
    readings_x[i] = 90;
    readings_y[i] = 90;
    total_x += readings_x[i];
    total_y += readings_y[i];
  }
}

void loop() {
  // Обработка данных от Serial (как в оригинальном коде)
  if (Serial.available() > 0) {
    String message = Serial.readStringUntil('\n');
    message.trim();

    int values[3];  // Массив для хранения значений: servo_x, servo_y, индекс объекта
    int index = 0;
    int start = 0;
    int end = message.indexOf(',');

    // Разделяем строку на значения
    while (end != -1 && index < 3) {
      values[index] = message.substring(start, end).toInt();
      start = end + 1;
      end = message.indexOf(',', start);
      index++;
    }

    // Если значений меньше 3, берем оставшуюся часть строки
    if (index < 3) {
      values[index] = message.substring(start).toInt();
    }

    // Выводим полученные значения для отладки
    for (int i = 0; i < 3; i++) {
      Serial.print(values[i]);
      if (i < 2) Serial.print(",");
    }
    Serial.print(",");
    Serial.println(dataFromBluetooth);

    // Извлекаем углы
    angle_x = values[0];
    angle_y = values[1];
    ind_of_object = values[2];

    // Сглаживание angle_x
    total_x = total_x - readings_x[readIndex_x]; // Убираем старое значение
    readings_x[readIndex_x] = angle_x;           // Добавляем новое значение
    total_x = total_x + readings_x[readIndex_x]; // Обновляем сумму
    readIndex_x = (readIndex_x + 1) % numReadings; // Переходим к следующему индексу
    average_x = total_x / numReadings;           // Вычисляем среднее

    // Сглаживание angle_y
    total_y = total_y - readings_y[readIndex_y]; // Убираем старое значение
    readings_y[readIndex_y] = angle_y;           // Добавляем новое значение
    total_y = total_y + readings_y[readIndex_y]; // Обновляем сумму
    readIndex_y = (readIndex_y + 1) % numReadings; // Переходим к следующему индексу
    average_y = total_y / numReadings;           // Вычисляем среднее

    int step_x = (average_x > past_angle_x) ? 1 : -1;
    for (int i = past_angle_x; i != average_x; i += step_x) {
      servox.write(i);
      delay(10); // Задержка для плавности
    }
    past_angle_x = average_x;

    int step_y = (average_y > past_angle_y) ? 1 : -1;
    for (int i = past_angle_y; i != average_y; i += step_y) {
      servoy.write(i);
      delay(10);
    }
    past_angle_y = average_y;
  }

  // Обновление значения от Bluetooth (выполняется сразу при получении данных)
  if (Serial1.available()) {
    dataFromBluetooth = Serial1.readString();
    dataFromBluetooth.trim();

    if (dataFromBluetooth != currentBluetoothState) {
      currentBluetoothState = dataFromBluetooth;
      Serial1.print("New Bluetooth state: ");
      Serial1.println(currentBluetoothState);
    }
  }

  // Выполнение блока условий раз в 5 секунд
  unsigned long currentMillis = millis();
  if (currentMillis - lastBluetoothCheckTime >= bluetoothCheckInterval) {
    lastBluetoothCheckTime = currentMillis;  // Обновляем время последней проверки

    if (currentBluetoothState == "enemy" && (ind_of_object == 0 || ind_of_object == 2 || ind_of_object == 3)) {
      Serial1.println("Shooting enemy");
      analogWrite(BwdPin_A, 0);
      analogWrite(FwdPin_A, MaxSpd);
      delay(600);
      analogWrite(FwdPin_A, 0);
    } else if (currentBluetoothState == "dont shoot") {
      analogWrite(FwdPin_A, 0);
      Serial1.println("Dont shooting");
    } else if (currentBluetoothState == "ours" && (ind_of_object == 0 || ind_of_object == 1)) {
      Serial1.println("Shooting ours and enemy");
      analogWrite(BwdPin_A, 0);
      analogWrite(FwdPin_A, MaxSpd);
      delay(600);
      analogWrite(FwdPin_A, 0);
    } else {
      analogWrite(FwdPin_A, 0);
      Serial1.println("Dont shooting");
    }
//    dataFromBluetooth = "dont shoot";  // Сброс состояния после выполнения
  }
}