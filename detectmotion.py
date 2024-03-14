import time
import RPi.GPIO as GPIO
from time import sleep
import os
import dropbox
import zipfile

import base64
import requests
import json


APP_KEY = 'pi4z3n7afg5hlcm'


APP_SECRET = '9rk3llz4akzaq3v'
ACCESS_CODE_GENERATED = 'nqoXqBbYmDMAAAAAAAAAiuHlFBF7iaU9sCeg-pGClSA'

BASIC_AUTH = base64.b64encode(f'{APP_KEY}:{APP_SECRET}'.encode())

headers = {
    'Authorization': f"Basic {BASIC_AUTH}",
    'Content-Type': 'application/x-www-form-urlencoded',
}

data = f'code={ACCESS_CODE_GENERATED}&grant_type=authorization_code'

response = requests.post('https://api.dropboxapi.com/oauth2/token',
                         data=data,
                         auth=(APP_KEY, APP_SECRET))
#print(response.text)
print(json.dumps(json.loads(response.text), indent=2))
oauth_result = json.dumps(json.loads(response.text), indent=2)
data = json.loads(oauth_result)
access_token = data.get('access_token')
#access = oauth_result['access_token']
#print(access)

#with dropbox.Dropbox(oauth2_access_token=oauth_result.access_token) as dbx:
#    dbx.users_get_current_account()
#    print("Successfully set up client!")


from picamera import PiCamera
import picamera

def mainfunc():

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(21,GPIO.IN) #Replace 21 with the input pin you use in the Raspberry Pi GPIO
    
    counter = 0
    zipnum = 1
    camera = PiCamera()
    
    try:
        while True:
                input=GPIO.input(21)
                
                if input==0:
                    print("Looking for Intruder: " + str(counter))
                    counter = counter + 1
                    time.sleep(1)
                
                elif input==1:
                    print("Intruder detected, shoo them away!")
                    
                    camera.start_preview()
                    
                    for i in range(2):
                        sleep(1)
                        camera.capture('/home/ayush/Desktop/SmartSurveillance/Captured/image%s.jpg' % i) #Here replace with the path with your own path where the file would be present
                    
                    camera.stop_preview()
                    time.sleep(1)

                    #This part of the code is zipping the images that are stored in a folder called testImage.
                    def zipdir(path,ziph):
                        for root, dirs, files in os.walk(path):
                            for file in files:
                                ziph.write(os.path.join(root,file))
                    zipf = zipfile.ZipFile('Zipped_file.zip','w',zipfile.ZIP_DEFLATED)
                    zipdir('./testImage',zipf)
                    zipf.close()
                    print("Successfully Zipped")

                    #This part of the code is sending the file to dropbox
                    f = open('/home/ayush/Desktop/Zipped_file.zip', "rb") #Here replace with the path with your own path where the file would be present
                    #print(oauth2_access_token=oauth_result.access_token)
                    dbx = dropbox.Dropbox(oauth2_access_token= access_token)
                    dbx.files_upload(f.read(),'/motionsenseCamPi%s.zip'%zipnum, mute = True)
                    zipnum = zipnum + 1
                    print("Successfully uploaded to Cloud!")
                    f.close()
                    time.sleep(2)



    finally:
            GPIO.cleanup()



if __name__ == "__main__":
    mainfunc()

