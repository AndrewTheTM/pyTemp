import smbus
import RPi.GPIO as GPIO
import sqlite3
import datetime
import time
import os

DATABASE_PATH = '/var/www/html/db/fermpi.db'
I2C_ADDRESS = 0x4e
I2C_KEEZER = 0x4a
OUTFILE = '/var/www/html/current_temperature'

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)

enlapsedHours = 0

# 1. get current set point
conn = sqlite3.connect(DATABASE_PATH)
cStatus = conn.cursor()
cStatus.execute("SELECT eventID, timeStamp FROM fermStatus")
status = cStatus.fetchall()

if(len(status)>0):
	eventID = status[0][0]
	startTimeStamp = status[0][1] #timestamp in seconds
	#print startTimeStamp

	cPlan = conn.cursor()
	cPlan.execute("SELECT fermScheduleId, profileName, primaryDays, primaryTemp, diacetylRestDays, diacetylRestTemp, lagerDays, lagerTemp FROM fermSchedules WHERE fermScheduleId = ?",(eventID,))
	plan = cPlan.fetchall()

	cTime = time.time()
	enlapsedTime = cTime-startTimeStamp
	profileName = plan[0][1]
	enlapsedHours = 0

	if profileName != "Fast Lager":
		priTime = plan[0][2]*24*60*60
		diaTime = plan[0][4]*24*60*60
		lagTime = plan[0][6]*24*60*60
		#print enlapsedTime
		enlapsedHours = enlapsedTime / 60 / 60

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
		print sVal
	else:
		# Fast lager program
		enlapsedHours = enlapsedTime / 60 / 60
		print "Fast lager", enlapsedHours
		if enlapsedHours < 168:
			sVal = 50
		elif enlapsedHours < 180:
			sVal = 55
		elif enlapsedHours < 192:
			sVal = 60
		elif enlapsedHours < 204:
			sVal = 65
		elif enlapsedHours < 264:
			sVal = 68
		elif enlapsedHours < 276:
			sVal = 63
		elif enlapsedHours < 288:
			sVal = 58
		elif enlapsedHours < 300:
			sVal = 53
		elif enlapsedHours < 312:
			sVal = 48
		elif enlapsedHours < 324:
			sVal = 43
		elif enlapsedHours < 336:
			sVal = 38
		elif enlapsedHours < 348:
			sVal = 33
		else:
			sVal = 32

else:
	sVal = -999

print "Set to: " + str(sVal) + " Hours: " + str(enlapsedHours)

# 2. get current temperature
# Read temperature from bus
bus = smbus.SMBus(0)
value = bus.read_byte_data(I2C_ADDRESS, 0x00)
if value > 127:
        value -= 256
tempF = 9.0 / 5.0 * value + 32.0
print("Current temp: {0}".format(tempF))

valueKZ = bus.read_byte_data(I2C_KEEZER, 0x00)
if valueKZ > 127:
	valueKZ -= 256
tempFKZ = 9.0 / 5.0 * valueKZ + 32.0
print("Current Keezer Temp: {0}".format(tempFKZ))

# 3. Determine what to do
if(tempF>sVal and sVal != -999):
	GPIO.output(24, GPIO.HIGH)
	print "Ferm Chamber Turned on"
else:
	GPIO.output(24, GPIO.LOW)
	print "Ferm Chamber Turned off"

if tempFKZ > 39:
	GPIO.output(18, GPIO.HIGH)
	print "Keezer Turned On"
else:
	GPIO.output(18, GPIO.LOW)
	print "Keezer Turned Off"

# 4. File for internal website
with open(OUTFILE, 'w') as the_file:
    the_file.write(str(tempF))
