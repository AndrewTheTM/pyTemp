import rsa, requests, datetime, json, urllib2
from pytz import timezone

# Important Variables
I2C_ADDRESS = 0x4a
KEY_FILE = "/home/pi/keynp.pem"
API_URL = "http://api.siliconcreek.net/insip.php"

# Don't Change Variables
USER_AGENT = "Python API Writer by Andrew"

req = urllib2.Request('http://ipecho.net/plain')
response = urllib2.urlopen(req)
the_page = response.read()

listData = {'ip':the_page}
jsonData = json.dumps(listData)

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

response = requests.post(API_URL,files=files)
