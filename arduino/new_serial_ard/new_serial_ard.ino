// Really terrible code in classic hackathon style.

#define MOTOR_PIN 10
#define STEERING_PIN 9
#define THROTTLE_INPUT_PIN 3
#define STEERING_INPUT_PIN 2

#define RGB1_PINR 13
#define RGB1_PING 12
#define RGB1_PINB 11

#define RGB2_PINR 5
#define RGB2_PING 6
#define RGB2_PINB 7

#define ENCODER_PIN A0

//For serial connection***
#define THROTTLE_FLAG 't'
#define STEERING_FLAG 's'
#define KILLALL_FLAG 'k'
#define HEARTBEAT 'h'
#define NO_SERIAL_AVAL 9
#define HEARTBEAT_THRESHOLD 200
String temp_str = "";
short crt_code = -1;
int crt_value = -1;
int heartbeat_cnt = 0;
//************************

#include <EnableInterrupt.h>

volatile long pwm_value = 0;
volatile long prev_time = 0;

volatile long throtPwmValue = 0;
volatile long throtPrevValue = 0;

volatile long steeringPwmValue = 0;
volatile long steeringPrevValue = 0;

volatile long robotMode = 0;

int stringReferences[10];
int numReferences = 0;

void setup() 
{
  setPwmFrequency(MOTOR_PIN, 256);
  setPwmFrequency(STEERING_PIN, 256);

  pinMode(RGB1_PINR, OUTPUT);
  pinMode(RGB1_PING, OUTPUT);
  pinMode(RGB1_PINB, OUTPUT);

  pinMode(RGB2_PINR, OUTPUT);
  pinMode(RGB2_PING, OUTPUT);
  pinMode(RGB2_PINB, OUTPUT);

  pinMode(A1, INPUT);

  digitalWrite(RGB1_PINR, LOW);
  digitalWrite(RGB1_PINB, LOW);
  digitalWrite(RGB1_PING, LOW);

  digitalWrite(RGB2_PINR, LOW);
  digitalWrite(RGB2_PINB, LOW);
  digitalWrite(RGB2_PING, LOW);
  
  enableInterrupt(ENCODER_PIN, __rising, RISING);
  enableInterrupt(THROTTLE_INPUT_PIN, __risingThrottle, RISING);
  enableInterrupt(STEERING_INPUT_PIN, __risingSteering, RISING);
  prev_time = micros();
  Serial.begin(115200);
}

void get_serial_command()
{
	for (int i = 0; i < 100; i++)
	{
		if (Serial.available() > 0)
		{            

            
	        char b = Serial.read();

          if (b == '3')
          {
            digitalWrite(RGB2_PINR, HIGH);
            digitalWrite(RGB2_PINB, HIGH);
            digitalWrite(RGB2_PING, HIGH);
          }
	        
	        if (b != '!')
	        {
           
	            temp_str += b;
	        }
          
	        else if (b == '!')
	        {
         
	            crt_code = temp_str[0];
	            temp_str[0] = '0';
	            crt_value = stringToNumber(temp_str);
              temp_str = "";
	            return;
	        }
	    }
	}
	crt_code = NO_SERIAL_AVAL;
}

double normalize_serial_input(int in)
{
  double normalized = in;
  normalized = normalized / 100.0;
  normalized = normalized + 1;
  return normalized;
}

int debounce = 0;

void loop() 
{
  int batteryValue = analogRead(A5);

  if (batteryValue < 340)
    robotMode = 99;
  
  // This is autodrive mode
  if (robotMode == -1)
  {
    int buttonState = digitalRead(A1);

    if (buttonState == HIGH) {
      digitalWrite(RGB2_PINB, HIGH);
    }
    else
    {
      digitalWrite(RGB2_PINB, LOW);
      Serial.write("g!");
      robotMode = 0;
    }

    if ((throtPwmValue < 1700 && throtPwmValue > 1600) || (throtPwmValue < 1400 && throtPwmValue > 1300))
      robotMode = 1;
  }
  else if (robotMode == 0)
  {
    digitalWrite(RGB2_PINR, LOW);
        digitalWrite(RGB2_PINB, LOW);
        digitalWrite(RGB2_PING, LOW);

       int buttonState = digitalRead(A1);

    if (buttonState == HIGH) {
      digitalWrite(RGB2_PINB, HIGH);
    }
    else
    {
      digitalWrite(RGB2_PINB, LOW);
      Serial.write("g!");
      robotMode = 0;
    }
    
    double num = 4.0;
    get_serial_command();
    switch (crt_code)
    {
    	case HEARTBEAT:
    		heartbeat_cnt = 0;
    		break;
    	case NO_SERIAL_AVAL:
    		heartbeat_cnt++;
    		//if (heartbeat_cnt > HEARTBEAT_THRESHOLD) { robotMode = 1; }
    		break;
    	case THROTTLE_FLAG:
    		heartbeat_cnt = 0;
    		__setPWM(MOTOR_PIN, normalize_serial_input(crt_value));
        digitalWrite(RGB2_PINR, HIGH);
        digitalWrite(RGB2_PINB, HIGH);
        digitalWrite(RGB2_PING, HIGH);
        delay(10);
    		break;
    	case STEERING_FLAG:
    		heartbeat_cnt = 0;
        num = normalize_serial_input(crt_value);
    		__setPWM(STEERING_PIN, normalize_serial_input(crt_value));
    		break;
    	case KILLALL_FLAG:
    		heartbeat_cnt = 0;
    		__setPWM(MOTOR_PIN, 1.5);
    		__setPWM(STEERING_PIN, 1.5);
        robotMode = 98;
    		break;
    }

    digitalWrite(RGB1_PINR, HIGH);
    digitalWrite(RGB1_PINB, LOW);
    digitalWrite(RGB1_PING, LOW);
    
    if ((throtPwmValue < 1700 && throtPwmValue > 1600) || (throtPwmValue < 1400 && throtPwmValue > 1300))
      robotMode = 1;
  }
  // This is drive by controller mode.  To return back to the previous mode, reset the arduino.
  else if (robotMode == 1) 
  {
    digitalWrite(RGB1_PINR, LOW);
    digitalWrite(RGB1_PING, HIGH);
    digitalWrite(RGB1_PINB, LOW);
    if (throtPwmValue > 800 && throtPwmValue < 2200)
    {
      __setPWM(MOTOR_PIN, (float)throtPwmValue/1000.0);
    }
    else
    {
      __setPWM(MOTOR_PIN, 1.5);
    }
  
    if (steeringPwmValue > 800 && steeringPwmValue < 2200)
    {
      __setPWM(STEERING_PIN, (float)steeringPwmValue/1000.0);
    }
    else
    {
      __setPWM(STEERING_PIN, 1.5);
    }
  }
  // KillAll Mode
  else if (robotMode == 98)
  {
    __setPWM(MOTOR_PIN, 1.5);
    __setPWM(STEERING_PIN, 1.5);
    digitalWrite(RGB1_PINR, HIGH);
    digitalWrite(RGB2_PINR, HIGH);
    digitalWrite(RGB1_PINB, HIGH);
    digitalWrite(RGB1_PING, HIGH);
    digitalWrite(RGB2_PINB, HIGH);
    digitalWrite(RGB2_PING, HIGH);
    delay(50);
    digitalWrite(RGB1_PINR, LOW);
    digitalWrite(RGB2_PINR, LOW);
    digitalWrite(RGB1_PING, LOW);
    digitalWrite(RGB2_PING, LOW);
    digitalWrite(RGB1_PINB, LOW);
    digitalWrite(RGB2_PINB, LOW);
    delay(50);
  }
  // Battery Dead Mode
  else if (robotMode == 99)
  {
    __setPWM(MOTOR_PIN, 1.5);
    __setPWM(STEERING_PIN, 1.5);
    digitalWrite(RGB1_PINR, HIGH);
    digitalWrite(RGB2_PINR, HIGH);
    digitalWrite(RGB1_PINB, LOW);
    digitalWrite(RGB1_PING, LOW);
    delay(50);
    digitalWrite(RGB1_PINR, LOW);
    digitalWrite(RGB2_PINR, LOW);
    delay(50);
  }
  
}

void __risingThrottle()
{
  enableInterrupt(THROTTLE_INPUT_PIN, __fallingThrottle, FALLING);
  throtPrevValue = micros();
}

void __fallingThrottle()
{
  enableInterrupt(THROTTLE_INPUT_PIN, __risingThrottle, RISING);
  throtPwmValue = micros() - throtPrevValue;
}

void __risingSteering()
{
  enableInterrupt(STEERING_INPUT_PIN, __fallingSteering, FALLING);
  steeringPrevValue = micros();
}

void __fallingSteering()
{
  enableInterrupt(STEERING_INPUT_PIN, __risingSteering, RISING);
  steeringPwmValue = micros() - steeringPrevValue;
}

void __rising()
{
  enableInterrupt(ENCODER_PIN, __falling, FALLING);
}

void __falling()
{
  enableInterrupt(ENCODER_PIN, __rising, RISING);
  pwm_value = micros() - prev_time;
  prev_time = micros();
  //Serial.println(pwm_value);
}

void __setPWM(int pin, float ms) // 1.5ms = stop, 1ms->2ms is reverse->forward
{
  float msPerPeriod = 8.192; // 256 [from setPwmFrequency(..., 256)] / 31250Hz = 8.192ms
  float maxAnalogValue = 255;
  int analogValue = (ms / msPerPeriod) * maxAnalogValue + 1;
  analogWrite(pin, analogValue);
}

/** 
 *  This code was found here:
 *  http://playground.arduino.cc/Code/PwmFrequency
 */
void setPwmFrequency(int pin, int divisor) {
  byte mode;
  if(pin == 5 || pin == 6 || pin == 9 || pin == 10) {
    switch(divisor) {
      case 1: mode = 0x01; break;
      case 8: mode = 0x02; break;
      case 64: mode = 0x03; break;
      case 256: mode = 0x04; break;
      case 1024: mode = 0x05; break;
      default: return;
    }
    if(pin == 5 || pin == 6) {
      TCCR0B = TCCR0B & 0b11111000 | mode;
    } else {
      TCCR1B = TCCR1B & 0b11111000 | mode;
    }
  } else if(pin == 3 || pin == 11) {
    switch(divisor) {
      case 1: mode = 0x01; break;
      case 8: mode = 0x02; break;
      case 32: mode = 0x03; break;
      case 64: mode = 0x04; break;
      case 128: mode = 0x05; break;
      case 256: mode = 0x06; break;
      case 1024: mode = 0x7; break;
      default: return;
    }
    TCCR2B = TCCR2B & 0b11111000 | mode;
  }
}

int stringToNumber(String thisString) {
  thisString[0] = '0';
  int length = thisString.length();

  return thisString.toInt();
}


