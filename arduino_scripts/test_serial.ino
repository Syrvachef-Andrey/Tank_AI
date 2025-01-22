// sudo chmod a+rw /dev/ttyUSB0
void setup() {
  // ????????????? ????????????????? ????? ?? ???????? 9600 ???
  Serial.begin(9600);
}

void loop() {

  if (Serial.available() > 0) {

    String message = Serial.readStringUntil('\n'); 
    message.trim(); 

    int values[2]; 
    int index = 0;
    int start = 0;
    int end = message.indexOf(',');

    while (end != -1 && index < 2) {
      values[index] = message.substring(start, end).toInt();
      start = end + 1;
      end = message.indexOf(',', start);
      index++;
    }

    if (index < 2) {
      values[index] = message.substring(start).toInt();
    }

    Serial.print("Received values: ");
    for (int i = 0; i < 2; i++) {
      Serial.print(values[i]);
      if (i < 1) Serial.print(", ");
    }
    Serial.println();
    
  }
}
