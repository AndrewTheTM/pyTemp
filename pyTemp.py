import smbus,rsa,requests,datetime,json
from pytz import timezone

# Important Variables
I2C_ADDRESS_KEEZ = 0x4a
I2C_ADDRESS_FERM = 0x4e
KEY_FILE = "/home/pi/keynp.pem"
API_URL = "https://www.runningonbeer.net/iot/api/index.php"

# Don't Change Variables
USER_AGENT = "Python API Writer by Andrew"

# Read temperature from bus
bus = smbus.SMBus(0)
valueKeez = bus.read_byte_data(I2C_ADDRESS_KEEZ,0x00)
if valueKeez > 127:
	valueKeez -= 256 
tempF = 9.0 / 5.0 * valueKeez + 32.0

valueFerm = bus.read_byte_data(I2C_ADDRESS_FERM, 0x00)
if valueFerm > 127:
	valueFerm -= 256
tempFFerm = 9.0 / 5.0 * valueFerm + 32.0

# Assemble JSON
current_time = str(datetime.datetime.now(timezone('US/Eastern')))

listData = {'time':current_time, 'temp':tempF, 'tempFerm': tempFFerm}
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
