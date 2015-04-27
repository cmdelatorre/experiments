#include <NewPing.h>
 
/*Aqui se configuran los pines donde debemos conectar el sensor*/
#define TRIGGER_PIN  8
#define ECHO_PIN     7
#define MAX_DISTANCE 300
 
/*Crear el objeto de la clase NewPing*/
NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE);
 
void setup() {
  Serial.begin(9600);
}
 
void loop() {
  // Esperar 1 segundo entre mediciones
  // delay(10);
  // Obtener medicion de tiempo de viaje del sonido y guardar en variable uS
  int uS = sonar.ping_median(5);
  // Calcular la distancia con base en una constante
  Serial.println(uS / US_ROUNDTRIP_CM);
}
