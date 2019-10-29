'''
  Smart Vision

  Monitoring of person standing in front of device which is made of raspberry pi and camera module

  The circuit:
  - Camera module is attached to raspberry pi.
  - Pir module connected to Raspberry Pi
  - Solenoid door lock connected to Raspberry Pi

  created 2019
  by Adamaya Sharma
  modified 29 October 2019
  by Adamaya Sharma

  This example code is in the public domain.

'''


import RPi.GPIO as GPIO
import picamera
from time import sleep
import imaplib
import email
import smtplib
import crd
import email.mime as MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import os


mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
crd1 = crd.data()
mail.login(crd1['from'], crd1['password'])


def send_mail(ImgFileName):
    img_data = open(ImgFileName, 'rb').read()
    msg = MIMEMultipart()
    msg['Subject'] = 'Testing'
    msg['From'] = crd1['from']
    msg['To'] = crd1['to']

    text = MIMEText("May I let him/her in?")
    msg.attach(text)
    image = MIMEImage(img_data, name=os.path.basename(ImgFileName))
    msg.attach(image)

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(crd1['from'], crd1['password'])
    s.sendmail(crd1['from'], crd1['to'], msg.as_string())
    s.quit()


def read_mail():
    mail.list()
    mail.select('inbox')

    result, data = mail.uid('search', None, "ALL")

    i = len(data[0].split())
    for x in range(i):
        latest_email_uid = data[0].split()[x]
        result, email_data = mail.uid('fetch', latest_email_uid, '(RFC822)')

        raw_email = email_data[0][1]

    raw_email_string = raw_email.decode('utf-8')

    email_message = email.message_from_string(raw_email_string)

    for part in email_message.walk():
        if part.get_content_type() == "text/plain":
            body = part.get_payload(decode=True)

            myfile = open("Dumpgmailemail.txt", 'w')
            myfile.write(body.decode('utf-8'))

            myfile.close()
        else:
            continue


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(3, GPIO.OUT)
GPIO.setup(11, GPIO.IN)
GPIO.setup(16,GPIO.OUT)
cam = picamera.PiCamera()
img = 1

while True:
    pinput = GPIO.input(11)
    print(pinput)
    if pinput == 1:
        cam.capture('/home/pi/CameraModule/Intruder%s.jpg' % str(img))
        img += 1
        sleep(3)
        try:
            send_mail('Intruder%s.jpg' % str(img))
            print("Image has been sent")
            sleep(60)
            read_mail()
        except Exception as e:
            print('Image not sent')
        try:
            fp=open("Dumpgmailemail.txt","r")
            response=fp.read()
        except Exception as e:
            print("file does not exist")
            response="null"
        if response.lower()=='yes':
            print("Access Granted")
            GPIO.output(16,GPIO.HIGH)
            sleep(10)
            GPIO.output(16,GPIO.LOW)
        elif response.lower()=='no':
            print("Access Denied")
        else:
            print("invailid response")