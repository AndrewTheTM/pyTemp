import smbus,rsa,requests,datetime,json
from pytz import timezone

# Important Variables
I2C_ADDRESS = 0x4c
KEY_FILE = "/home/pi/keynp.pem"
API_URL = "http://api.siliconcreek.net/index.php"

# Don't Change Variables
USER_AGENT = "Python API Writer by Andrew"

# Read temperature from bus
bus = smbus.SMBus(0)
value = bus.read_i2c_block_data(I2C_ADDRESS,0)
intValue = (value[1] + (256 * value[0])) >> 2
#print intValue #Debug
volts = 3.3 * intValue / 1024.0
#print volts #Debug
rtwo = 100.0 * ((3.3 / volts) - 1.0)
#print rtwo #Debug
tempC = (rtwo - 100.0) / 0.39
#print tempC #Debug
tempF = 9.0 / 5.0 * tempC + 32.0
tempF = tempF - 15.0 #Adjustment
tempF = round(tempF * 10.0) / 10.0
print tempF

# Assemble JSON
current_time = str(datetime.datetime.now(timezone('US/Eastern')))
#print current_time #Debug

listData = {'time':current_time, 'temp':tempF}
jsonData = json.dumps(listData)
print jsonData #Debug


# Encrypt Data
with open(KEY_FILE) as pkFile:
	keydata = pkFile.read()
key = rsa.PrivateKey.load_pkcs1(keydata)
enc = rsa.encrypt(jsonData,key)

headers = {
	'User-Agent': USER_AGENT,
	'content-type': 'application/x-www-form-urlencoded',
	'charset':'US-ASCII'
}

files = {'file': ('encr.txt',enc)}

response = requests.post(API_URL,files=files) #,headers=headers)
#print response.headers
#print response.text


