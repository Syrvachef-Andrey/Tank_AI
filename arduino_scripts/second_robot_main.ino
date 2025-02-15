#include <IRremote.hpp>         // Подключаем библиотеку
#define IR_RECEIVE_PIN 2
#define main_engine_in1 3
#define main_engine_in2 4
#define main_engine_in3 6
#define main_engine_in4 5
#define second_engine_in1 7
#define second_engine_in2 8
#define ena 9
#define enb 10

uint32_t data_from_ir_module = 0;

void setup()
{
  Serial.begin(9600);
  IrReceiver.begin(IR_RECEIVE_PIN); // Инициализация приемника
  pinMode(main_engine_in1, 1);
  pinMode(main_engine_in2, 1);
  pinMode(main_engine_in3, 1);
  pinMode(main_engine_in4, 1);
  pinMode(second_engine_in1, 1);
  pinMode(second_engine_in2, 1);
}

void loop() {
  if (IrReceiver.decode()) {
      data_from_ir_module = IrReceiver.decodedIRData.decodedRawData;
      Serial.println(data_from_ir_module, HEX);
      if (data_from_ir_module == 0xB946FF00){
        Serial.println("forward");
        analogWrite(ena, 130);
        analogWrite(enb, 130);
        digitalWrite(main_engine_in1, 0);
        digitalWrite(main_engine_in2, 1);
        digitalWrite(main_engine_in3, 0);
        digitalWrite(main_engine_in4, 1);
      }
      else if(data_from_ir_module == 0xEA15FF00){
        Serial.println("backward");
        analogWrite(ena, 130);
        analogWrite(enb, 130);
        digitalWrite(main_engine_in1, 1);
        digitalWrite(main_engine_in2, 0);
        digitalWrite(main_engine_in3, 1);
        digitalWrite(main_engine_in4, 0);
        }
      else if(data_from_ir_module == 0xBB44FF00){
        Serial.println("left");
        analogWrite(second_engine_in1, 0);
        analogWrite(second_engine_in2, 130);
        }
      else if(data_from_ir_module == 0xBC43FF00){
        Serial.println("right");
        analogWrite(second_engine_in1, 130);
        analogWrite(second_engine_in2, 0);
        }
      else if(data_from_ir_module == 0xBF40FF00)
      {
        Serial.println("STOP");
        analogWrite(ena, 0);
        analogWrite(enb, 0);
        digitalWrite(main_engine_in1, 0);
        digitalWrite(main_engine_in2, 0);
        digitalWrite(main_engine_in3, 0);
        digitalWrite(main_engine_in4, 0);
        analogWrite(second_engine_in1, 0);
        analogWrite(second_engine_in2, 0);
       }
      IrReceiver.resume();
  }
}

