import smbus
import RPi.GPIO as GPIO
import sqlite3
import datetime
import time

DATABASE_PATH = '/var/www/db/fermpi.db'
I2C_ADDRESS = 0x4c

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

	cPlan = conn.cursor()
	cPlan.execute("SELECT fermScheduleId, profileName, primaryDays, primaryTemp, diacetylRestDays, diacetylRestTemp, lagerDays, lagerTemp FROM fermSchedules WHERE fermScheduleId = ?",(eventID,))
	plan = cPlan.fetchall()

	cTime = time.time()
	enlapsedTime = datetime.timedelta(seconds=cTime-startTimeStamp)
	priTime = plan[0][2]
	diaTime = plan[0][4]
	lagTime = plan[0][6]

	if(enlapsedTime.days<=priTime):
		print "In Primary"
		sVal = plan[0][3]
	elif(enlapsedTime.days<=(priTime+diaTime)):
		print "In diacetyl rest"
		sVal = plan[0][5]
	elif(enlapsedTime.days<=(priTime+diaTime+lagTime)):
		print "In Lager"
		sVal = plan[0][7]
	else:
		print "past lager"
		sVal = plan[0][7]
		#Holds to the lager temperature
else:
	sVal = 70
	
print sVal

# 2. get current temperature
bus = smbus.SMBus(0)
value = bus.read_i2c_block_data(I2C_ADDRESS,0)
intValue = (value[1] + (256 * value[0])) >> 2
volts = 3.3 * intValue / 1024.0
rtwo = 100.0* ((3.3 / volts) - 1.0)

tempC = (rtwo - 100.0) / 0.39

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
