#include <Servo.h>
#include <NewPing.h>



#define TRIG_PIN 3
#define ECHO_PIN 4
#define SERVO_PIN 9



#define MAX_DISTANCE 40   // Maximum distance in cm
#define MIN_DISTANCE 2     // Minimum valid distance



#define NUM_SAMPLES 5




Servo radarServo;

NewPing sonar(
  TRIG_PIN,
  ECHO_PIN,
  MAX_DISTANCE
);



int getStableDistance()
{
  int readings[NUM_SAMPLES];

  int validCount = 0;


  // Take multiple readings
  for (int i = 0; i < NUM_SAMPLES; i++)
  {
    unsigned int distance = sonar.ping_cm();

    if (distance >= MIN_DISTANCE &&
        distance <= MAX_DISTANCE)
    {
      readings[validCount] = distance;
      validCount++;
    }

    delay(5);
  }


  // No valid reading
  if (validCount == 0)
  {
    return MAX_DISTANCE;
  }



  for (int i = 0; i < validCount - 1; i++)
  {
    for (int j = i + 1; j < validCount; j++)
    {
      if (readings[j] < readings[i])
      {
        int temp = readings[i];

        readings[i] = readings[j];

        readings[j] = temp;
      }
    }
  }




  int median;

  if (validCount % 2 == 1)
  {
    median = readings[validCount / 2];
  }
  else
  {
    median =
      (readings[validCount / 2 - 1] +
       readings[validCount / 2]) / 2;
  }


  return median;
}




void sendRadarData(
  int angle,
  int distance
)
{
  Serial.print(angle);
  Serial.print(",");
  Serial.println(distance);
}




void setup()
{
  Serial.begin(115200);

  radarServo.attach(SERVO_PIN);

  radarServo.write(90);

  delay(1000);
}




void loop()
{



  for (int angle = 0;
       angle <= 180;
       angle++)
  {

    radarServo.write(angle);

    // Wait for servo to reach position
    delay(25);

    int distance = getStableDistance();

    sendRadarData(
      angle,
      distance
    );
  }




  for (int angle = 180;
       angle >= 0;
       angle--)
  {

    radarServo.write(angle);

    delay(25);

    int distance = getStableDistance();

    sendRadarData(
      angle,
      distance
    );
  }
}