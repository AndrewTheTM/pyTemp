import smbus
import RPi.GPIO as GPIO
import sqlite3

DATABASE_PATH = '/var/www/db/fermpi.db'
I2C_ADDRESS = 0x4c

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.OUT)

# 1. get current set point
conn = sqlite3.connect(DATABASE_PATH)
cStatus = conn.cursor()
cStatus.execute("SELECT * FROM fermStatus")
status = cStatus.fetchall()

cPlan = conn.cursor()
cPlan.execute("SELECT * FROM fermSchedules") #WHERE...
plan = cPlan.fetchall()

#print plan

sVal=50 #Debugging

# 2. get current temperature
bus = smbus.SMBus(0)
value = bus.read_i2c_block_data(I2C_ADDRESS,0)
intValue = (value[1] + (256 * value[0])) >> 2
#print value #Debug
print intValue #Debug
volts = 3.3 * intValue / 1024.0
#print volts #Debug
rtwo = 100.0* ((3.3 / volts) - 1.0)
#print rtwo #Debug

tempC = (rtwo - 100.0) / 0.39
#print tempC #Debug

tempF = 9.0 / 5.0 * tempC + 32.0
tempF = round(tempF * 10.0) / 10.0
tempF = tempF - 15.0 #adjustment
print tempF #Debug

# 3. Determine what to do
if(tempF>sVal):
	GPIO.output(18,GPIO.HIGH)
	print "Turned on"
else:
	GPIO.output(18,GPIO.LOW)
	print "Turn off"

