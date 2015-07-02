import smbus
import RPi.GPIO as GPIO

I2C_ADDRESS = 0x4c

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.OUT)

# 2. get current temperature
bus = smbus.SMBus(0)
value = bus.read_i2c_block_data(I2C_ADDRESS,0)
intVal = (value[1] + (256 * value[0])) >> 2
#print intValue #Debug
volts = 3.3 * intVal / 1024.0
#print volts #Debug
rtwo = 100.0 * ((3.3 / volts) - 1.0)
#print rtwo #Debug
tempC = (rtwo - 100.0) / 0.39
#print tempC #Debug
tempF = 9.0 / 5.0 * tempC + 32.0
tempF = tempF - 15.0 #Adjustment
tempF = round(tempF * 10.0) / 10.0
print tempF

# 3. Determine what to do
if(tempF<=32):
	GPIO.output(18,GPIO.LOW)
	print "EMERGENCY STOP - TEMPERATURE BELOW 32"

