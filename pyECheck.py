import smbus
import RPi.GPIO as GPIO

I2C_ADDRESS = 0x4a

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.OUT)

# 2. get current temperature
bus = smbus.SMBus(0)
value = bus.read_byte_data(I2C_ADDRESS,0x00)
if value > 127:
        value -= 256
tempF = 9.0 / 5.0 * value + 32.0
print "Current Temp: " + str(tempF)

f = open('/var/www/current_temperature','w')
f.write(str(tempF))
f.close()

# 3. Determine what to do
if(tempF<=32):
	GPIO.output(18,GPIO.LOW)
	print "EMERGENCY STOP - TEMPERATURE BELOW 32"

