import RPi.GPIO as GPIO
import time
from threading import *
import yagmail
   
yag_mail = yagmail.SMTP(user='yaz.from.iot@gmail.com', password="kmay ukqs tugt hjfx", host='smtp.gmail.com')
  
To= "alexv3796@gmail.com" # Use temp-mail.org for testing this code
Subject = "YOU LEFT YOUR CANDLE ON!!"
Body = """
        TWO OPTIONS:
         
        1. Come back and blow the candle out.
        2. Let the timer run out, fan will blow the candle out after 4 hours

        """


TRIG = 16
ECHO = 15
RedLED = 12 #Red LED
GreenLED = 11 #Green LED
IN1 = 38
IN2 = 40
ENA = 36
Flame = 33

timeElapsed = 0
threshold = 25 # distance in centimeters
mins = 0.5

GPIO.setmode(GPIO.BOARD)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(Flame, GPIO.IN)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
    
power = GPIO.PWM(ENA,1500)
power.start(0)

def setup():
    

    GPIO.setup(RedLED, GPIO.OUT)
    GPIO.setup(GreenLED, GPIO.OUT)
    

def flame():
    while True:
        print(GPIO.input(Flame))
        time.sleep(0.1)
        
            
    
def distance():
    while True:
    #GPIO.output(IN1, GPIO.HIGH)
    #GPIO.output(IN2, GPIO.LOW)
    
        GPIO.output(TRIG, 0)
        time.sleep(0.000002)
        GPIO.output(TRIG, 1)
        time.sleep(0.00001)
        GPIO.output(TRIG, 0)

    
        while GPIO.input(ECHO) == 0:
            time1 = time.time()
            
        while GPIO.input(ECHO) == 1:
            time2 = time.time()

        during = time2 - time1
        dist = during * 340 / 2 * 100 #Returns distance in cm

        global threshold
        if(dist<threshold):
            yag_mail.send(to=To, subject=Subject, contents=Body)
            print("Email has been sent successfully to the receiver's address.")
    
        time.sleep(0.1)

#def callback(Flame):
#    print("flame detected")

#class FuncThread(threading.Thread):
#    def __init__(self, target, *args):
#        self._target = target
#        self._args = args
#        threading.Thread.__init__(self)

#    def run(self):
#        self._target()


def ultrasonic():
    while True:
        dist = distance()
        #print(dist, 'cm')
        #print('')
        time.sleep(0.1)
                    
        global threshold
        if(dist<threshold):
            yag_mail.send(to=To, subject=Subject, contents=Body)
            print("Email has been sent successfully to the receiver's address.")
            
        #print(dist, 'cm')
        #print('')
        #GPIO.add_event_detect(Flame, GPIO.BOTH, bouncetime=300)
        #GPIO.add_event_callback(Flame, callback)
        #print(GPIO.input(Flame))
        #time.sleep(0.1)

        #time.sleep(0.1)
        
        
        
        #global threshold, power
        #if(dist<threshold):
        #    GPIO.output(IN1, True)
        #    GPIO.output(IN2, False)
        #    power.ChangeDutyCycle(50)
        
        #else:
        #    GPIO.output(IN1, False)
        #    GPIO.output(IN2, False)
        #    power.ChangeDutyCycle(0)
        
        #GPIO.output(IN1, GPIO.LOW)
        #GPIO.output(IN2, GPIO.HIGH)
        
def motor():
    print("Start timer of", mins, "minutes until auto extinguish")
    time.sleep(60*mins)
    print("start fan")
    GPIO.output(IN1, True)
    GPIO.output(IN2, False)
    power.ChangeDutyCycle(80)
    time.sleep(5)
    GPIO.output(IN1, False)
    GPIO.output(IN2, False)
    power.ChangeDutyCycle(0)
    print("flame extinguished!")



def loop():
    while True:
        while GPIO.input(Flame) == 0:
            print("flame on!")
            # Create and start the threads
            motor_thread = Thread(target=motor)
            sensor_thread = Thread(target=distance)

            motor_thread.start()
            sensor_thread.start()

            # Keep the main thread running
            motor_thread.join()
            sensor_thread.join()
            #thread1 = FuncThread(ultrasonic())
            #thread1.start()
            #motor()
            #thread1.join()
            
            
            

def destroy():
    GPIO.cleanup()
    
if __name__ == '__main__':
    setup()
    try:
        loop()
    except KeyboardInterrupt: #Quits out on ctrl+c
        destroy()
    finally:
	    destroy()
