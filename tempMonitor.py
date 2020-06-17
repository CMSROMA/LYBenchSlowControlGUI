import os
import serial
import time

class SerialConnectionSensirion():
    def __init__(self,port):
        self.con = serial.Serial(port,9600,timeout=2)
#        self.con.timeout = 5

    def waitAnswer(self,response):
        reply = ''
        time.sleep(0.5)
        #        while True:
        try:
            x = self.con.readline().decode('UTF-8')
            reply += x.strip()
            if reply == response:
                return reply
        except Exception as e:
            logging.error('Exception while reading sensor:'+str(e))
            return ''

    def returnAnswer(self):
        reply = ''
        #        while True:
        x = self.con.readline().decode('UTF-8')
        reply += x.strip()
        return reply

    def sendCommand(self,command):
        if (command.lower()) == 't' :
            self.con.write('t'.encode())
            time.sleep(0.5)
            return self.returnAnswer()
        else:
            return 'Command not supported'

from datetime import datetime
import logging
import requests

thingspeak_key='YNRB0GNUGK9H5MK7'
t_bench,t_ext,h_bench=0,0,0


def logThingSpeak(message):
    print(message)
    try:
        conn = requests.post("http://api.thingspeak.com/update",data=message)
    except:
        logging.error("Thingspeak connection failed")

def refreshThingSpeak():
    global t_bench,t_ext,h_bench
    params = {'field1': t_bench, 'field2': t_ext, 'field3': h_bench, 'key': thingspeak_key}
    logThingSpeak(params)

def refreshSensirion(sercon):
    global t_bench,t_ext,h_bench
    reply=sercon.sendCommand('t')
    if (len(reply.split(' ')) == 8):
        t_bench=reply.split(' ')[1]
        t_ext=reply.split(' ')[3]
        h_bench=reply.split(' ')[5]
        dew=reply.split(' ')[7]
        logging.info('T_BENCH:'+t_bench+' T_EXT:'+t_ext+' H_BENCH:'+h_bench+' DEW:'+dew)
    else:
        logging.error('Wrong reply from sensor '+reply)

from optparse import OptionParser
parser = OptionParser()
parser.add_option("-l","--log")
(options,args)=parser.parse_args()

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S',filename=options.log,level=logging.INFO)
sercon = SerialConnectionSensirion('/dev/sensor_1') 
reply=sercon.sendCommand('t')

try:
    while(True):
        refreshSensirion(sercon)
        refreshThingSpeak()
        time.sleep(30)
except KeyboardInterrupt:
    logging.info('Bye')
