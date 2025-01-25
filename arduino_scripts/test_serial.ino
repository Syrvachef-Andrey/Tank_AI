#include <Servo.h>
#include <SoftwareSerial.h>

#define BT_RX 18
#define BT_TX 19

Servo servox;
Servo servoy;

String dataFromBluetooth = "Enemy";  // Переменная для хранения текущего значения от Bluetooth
String currentBluetoothState = "";   // Переменная для хранения текущего состояния

int MaxSpd = 130;

int ind_of_object;

int past_angle_x = 90;
int past_angle_y = 90;
int angle_x;
int angle_y;

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

void setup() {
  servox.attach(10);  // Сервопривод X на пин 10
  servoy.attach(11);   // Сервопривод Y на пин 11

  pinMode(FwdPin_A, OUTPUT);
  pinMode(BwdPin_A, OUTPUT);

  Serial.begin(115200);
  delay(3000);

  Serial1.begin(9600);

  // Инициализация массивов для скользящего среднего
  for (int i = 0; i < numReadings; i++) {
    readings_x[i] = 90;
    readings_y[i] = 90;
    total_x += readings_x[i];
    total_y += readings_y[i];
  }
}

void loop() {
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
    Serial.print("Received values: ");
    for (int i = 0; i < 3; i++) {
      Serial.print(values[i]);
      if (i < 2) Serial.print(", ");
    }
    Serial.println();

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

    // Плавное движение сервопривода X
    int step_x = (average_x > past_angle_x) ? 1 : -1; // Шаг изменения угла
    for (int i = past_angle_x; i != average_x; i += step_x) {
      servox.write(i);
      delay(15); // Задержка для плавности
    }
    past_angle_x = average_x;

    // Плавное движение сервопривода Y
    int step_y = (average_y > past_angle_y) ? 1 : -1; // Шаг изменения угла
    for (int i = past_angle_y; i != average_y; i += step_y) {
      servoy.write(i);
      delay(15); // Задержка для плавности
    }
    past_angle_y = average_y;
  }

  // Обработка данных от Bluetooth
  if (Serial1.available()) {
    dataFromBluetooth = Serial1.readString();
    dataFromBluetooth.trim();  // Убираем лишние пробелы и символы

    // Если новое значение отличается от текущего
    if (dataFromBluetooth != currentBluetoothState) {
      currentBluetoothState = dataFromBluetooth;  // Обновляем текущее состояние
      Serial1.print("New Bluetooth state: ");
      Serial1.println(currentBluetoothState);

      // Выполняем действия в зависимости от нового состояния
      if (currentBluetoothState == "Enemy" && (ind_of_object == 0 || ind_of_object == 2 || ind_of_object == 3)) {
        analogWrite(BwdPin_A, 0);
        analogWrite(FwdPin_A, MaxSpd);
        delay(1000);
        analogWrite(FwdPin_A, 0);
      } else if (currentBluetoothState == "Dont shoot") {
        analogWrite(FwdPin_A, 0);
      } else if (currentBluetoothState == "Ours") {
        analogWrite(BwdPin_A, 0);
        analogWrite(FwdPin_A, MaxSpd);
        delay(300);
        analogWrite(FwdPin_A, 0);
      } else {
        analogWrite(FwdPin_A, 0);
      }
    }
  }
}