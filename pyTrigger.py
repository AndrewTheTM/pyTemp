import smbus
import RPi.GPIO as GPIO
import sqlite3
import datetime
import time

DATABASE_PATH = '/var/www/db/fermpi.db'
I2C_ADDRESS = 0x4a

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.OUT)

# 1. get current set point
conn = sqlite3.connect(DATABASE_PATH)
cStatus = conn.cursor()
cStatus.execute("SELECT eventID, timeStamp FROM fermStatus")
status = cStatus.fetchall()

if(len(status)>0):
	eventID = status[0][0]
	startTimeStamp = status[0][1] #timestamp in seconds
	print startTimeStamp

	cPlan = conn.cursor()
	cPlan.execute("SELECT fermScheduleId, profileName, primaryDays, primaryTemp, diacetylRestDays, diacetylRestTemp, lagerDays, lagerTemp FROM fermSchedules WHERE fermScheduleId = ?",(eventID,))
	plan = cPlan.fetchall()

	cTime = time.time()
	enlapsedTime = cTime-startTimeStamp

	priTime = plan[0][2]*24*60*60
	diaTime = plan[0][4]*24*60*60
	lagTime = plan[0][6]*24*60*60
	print enlapsedTime

	if(enlapsedTime<=priTime):
		print "In Primary"
		sVal = plan[0][3]
	elif(enlapsedTime<=(priTime+diaTime)):
		print "In diacetyl rest"
		sVal = plan[0][5]
	elif(enlapsedTime<=(priTime+diaTime+lagTime)):
		print "In Lager"
		sVal = plan[0][7]
	else:
		print "past lager"
		sVal = plan[0][7]
		#Holds to the lager temperature
else:
	sVal = 70
	
print "Set to: " + str(sVal)

# 2. get current temperature
# Read temperature from bus
bus = smbus.SMBus(0)
value = bus.read_byte_data(I2C_ADDRESS,0x00)
if value > 127:
        value -= 256
tempF = 9.0 / 5.0 * value + 32.0
print "Current temp: " + str(tempF)

# 3. Determine what to do
if(tempF>sVal):
	GPIO.output(18,GPIO.HIGH)
	print "Turned on"
else:
	GPIO.output(18,GPIO.LOW)
	print "Turned off"

GPIO.output(18, GPIO.HIGH)
