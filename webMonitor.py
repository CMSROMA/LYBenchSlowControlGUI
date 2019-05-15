from flexx import flx
import os
import serial

#class Main(flx.PyComponent):
#    def init(self):
#        self.sercon = SerialConnection()
#        self.widget = SlowControlGUI(self.sercon)
#
#    self.sercon.sendCommand('o')

BASE_DIR = os.getcwd()

with open(BASE_DIR + '/static/css/style.css') as f:
    style = f.read()

with open(BASE_DIR + '/static/js/script.js') as f:
    script = f.read()

flx.assets.associate_asset(__name__, 'style.css', style)
flx.assets.associate_asset(__name__, 'script.js', script)


class LedPulser(flx.PyComponent):
    def ledSwitch(self, status):
        ret=0
        if (status==1):
            ret+=os.system("echo 'C1:OUTP ON'>/dev/usbtmc0")
            ret+=os.system("echo 'C2:OUTP ON'>/dev/usbtmc0")
        elif (status==0):
            ret+=os.system("echo 'C1:OUTP OFF'>/dev/usbtmc0")
            ret+=os.system("echo 'C2:OUTP OFF'>/dev/usbtmc0")
        return ret

import time

class SerialConnection(flx.PyComponent):
    def init(self,port):
        self.con = serial.Serial(port)

    def waitAnswer(self,response):
        reply = ''
        while True:
            x = self.con.readline().decode('UTF-8')
            reply += x.strip()
            if reply == response:
                return reply

    def returnAnswer(self):
        reply = ''
        while True:
            x = self.con.readline().decode('UTF-8')
            reply += x.strip()
            return reply

    def sendCommand(self,command):
        if (command.lower()) == 'i' :
            self.con.write("i".encode())
            return self.waitAnswer('INH')
        elif (command.lower()) == 'o' :
            self.con.write("o".encode())
            return self.waitAnswer('ON')
        elif command == '1':
            self.con.write("1".encode())
            return self.waitAnswer('V1')
        elif command == '0':
            self.con.write("0".encode())
            return self.waitAnswer('V0')
        elif (command.lower()) == 't':
            self.con.write("t".encode())
            time.sleep(1)
            return self.returnAnswer()
        else:
            return 'Command not supported'

class SerialConnectionChiller(flx.PyComponent):
    def init(self,port):
        self.con = serial.Serial(port)

    def waitAnswer(self,response):
        reply = ''
        while True:
            x = self.con.readline().decode('UTF-8')
            reply += x.strip()
            if reply == response:
                return reply

    def returnAnswer(self):
        reply = ''
        while True:
            x = self.con.readline().decode('UTF-8')
            reply += x.strip()
            return reply

    def sendCommand(self,command):
        if (command.lower()) == 't' :
            self.con.write('IN_PV_00\r\n'.encode())
            time.sleep(0.5)
            return self.returnAnswer()
        if (command.lower()) == 'g' :
            self.con.write('IN_SP_00\r\n'.encode())
            time.sleep(0.5)
            return self.returnAnswer()
        if (command.lower()) == 'p' :
            self.con.write('IN_SP_01\r\n'.encode())
            time.sleep(0.5)
            return self.returnAnswer()
        elif (command.lower()) == 's' :
            self.con.write('STATUS\r\n'.encode())
            time.sleep(0.5)
            return self.returnAnswer()
        else:
            return 'Command not supported'

from datetime import datetime
import asyncio
import logging

class SlowControlGUI(flx.PyComponent):
    led = flx.IntProp(0, settable=True)
    hv = flx.IntProp(0, settable=True)
    vsel = flx.IntProp(0, settable=True)
    sercon =  flx.ComponentProp()
    serconChiller =  flx.ComponentProp()
    ledcon =  flx.ComponentProp()

    def init(self):
        super().init()
        self._mutate_sercon(SerialConnection('/dev/ttyACM0'))
        self._mutate_serconChiller(SerialConnectionChiller('/dev/ttyUSB0'))
        self._mutate_ledcon(LedPulser())
        self.t0 = datetime.now()
        #Always start in inhbit mode
        reply=self.sercon.sendCommand('i')
        if (reply!='INH'):
            print('Please check serial connection')

        reply=self.sercon.sendCommand('0')
        if (reply!='V0'):
            print('Please check serial connection')

        ret=self.ledcon.ledSwitch(0)
        if (ret!=0):
            print('Please check led pulser connection')

#        with flx.HBox(flex=0, spacing=10):


        with flx.PinboardLayout():
            self.tempText = flx.Label(text='T: XX.XX H: YY.YY',style='left:10px; top:120px; width:300px;height:20px;')
            self.chillerText = flx.Label(text='CHILLER TBATH:XXX.XX TSET:YYY.YY PUMP:ZZ',style='left:10px; top:140px; width:400px;height:20px;')
            self.but1 = flx.Button(text='Led Pulser',css_class="border-black",style='left:10px; top:10px; width:180px;height:100px;')
            self.but2 = flx.Button(text='HV',css_class="border-black",style='left:200px; top:10px; width:150px;height:100px;')
            self.but3 = flx.Button(text='VSEL',css_class="border-black",style='left:360px; top:10px; width:100px;height:100px;')
            self.chillerStatus = flx.Button(text='COOLING OK',css_class="border-black",style='left:470px; top:10px; width:250px;height:100px;')
#            self.label = flx.Label(text='', flex=1)  # take all remaining space

        self.refreshTemperature()
        self.refreshChiller()

    def refreshTemperature(self):
        reply=self.sercon.sendCommand('t')
        self.tempText.set_text(reply)
        logging.info(reply)
        asyncio.get_event_loop().call_later(5, self.refreshTemperature)

    def refreshChiller(self):
        tbath=self.serconChiller.sendCommand('t')
        tset=self.serconChiller.sendCommand('g')
        pump=self.serconChiller.sendCommand('p')
        status=self.serconChiller.sendCommand('s')
        self.chillerText.set_text('CHILLER TBATH:'+tbath+' TSET:'+tset+' PUMP:'+pump)

        if (status == '0' ):
            self.chillerStatus.set_text('COOLING OK')
            self.chillerStatus.apply_style('background:green;')
        else:
            self.chillerStatus.set_text('COOLING KO')
            self.chillerStatus.apply_style('background:red;')

        logging.info('CHILLER TBATH: '+tbath+' STATUS: '+status+' TSET:'+tset+' PUMP:'+pump)
        asyncio.get_event_loop().call_later(10, self.refreshChiller)

    @flx.action
    def hv_switch(self):
        if (self.hv==0):
            reply=self.sercon.sendCommand('o')
            if (reply=='ON'):
                self._mutate_hv(1)
        elif (self.hv==1):
            reply=self.sercon.sendCommand('i')
            if (reply=='INH'):
                self._mutate_hv(0)

    @flx.action
    def led_switch(self):
        if (self.led==0):
            ret=self.ledcon.ledSwitch(1)
            if (ret==0):
                self._mutate_led(1)
        elif (self.led==1):
            ret=self.ledcon.ledSwitch(0)
            if (ret==0):
                self._mutate_led(0)
        
    @flx.action
    def vsel_switch(self):
        if (self.vsel==0):
            reply=self.sercon.sendCommand('1')
            if (reply=='V1'):
                self._mutate_vsel(1)
        elif (self.vsel==1):
            reply=self.sercon.sendCommand('0')
            if (reply=='V0'):
                self._mutate_vsel(0)

    @flx.reaction('but1.pointer_click')
    def but1_clicked(self, *events):
        self.led_switch()

    @flx.reaction('but2.pointer_click')
    def but2_clicked(self, *events):
        self.hv_switch()

    @flx.reaction('but3.pointer_click')
    def but3_clicked(self, *events):
        self.vsel_switch()

#    @flx.reaction
#    def update_label(self, *events):
 
    @flx.reaction
    def update_buttons(self, *events):
        if (self.hv==1):
            self.but2.set_text('HV ON')
            self.but2.apply_style('background:red;')
        if (self.hv==0):
            self.but2.set_text('HV OFF')
            self.but2.apply_style('background:yellow;')
        if (self.led==1):
            self.but1.set_text('LED ON')
            self.but1.apply_style('background:red;')
        if (self.led==0):
            self.but1.set_text('LED OFF')
            self.but1.apply_style('background:yellow;')
        if (self.vsel==1):
            self.but3.set_text('V1')
        if (self.vsel==0):
            self.but3.set_text('V0')

from optparse import OptionParser
parser = OptionParser()
parser.add_option("-l","--log")
parser.add_option("-p","--port")
(options,args)=parser.parse_args()

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S',filename=options.log,level=logging.DEBUG)
flx.config.port = options.port

app = flx.App(SlowControlGUI)
#app.launch('browser')  # show it now in a browser
app.serve('')
flx.start()  # enter the mainloop
