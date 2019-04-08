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

class SerialConnection(flx.PyComponent):
    def init(self):
        self.con = serial.Serial('/dev/ttyACM0')

    def waitAnswer(self,response):
        reply = ''
        while True:
            x = self.con.readline().decode('UTF-8')
            reply += x.strip()
            if reply == response:
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
        else:
            return 'Command not supported'
    
class SlowControlGUI(flx.PyComponent):
    led = flx.IntProp(0, settable=True)
    hv = flx.IntProp(0, settable=True)
    vsel = flx.IntProp(0, settable=True)
    sercon =  flx.ComponentProp()
    ledcon =  flx.ComponentProp()

    def init(self):
        super().init()
        self._mutate_sercon(SerialConnection())
        self._mutate_ledcon(LedPulser())

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
            self.but1 = flx.Button(text='Led Pulser',css_class="border-black",style='left:10px; top:10px; width:180px;height:100px;')
            self.but2 = flx.Button(text='HV',css_class="border-black",style='left:200px; top:10px; width:150px;height:100px;')
            self.but3 = flx.Button(text='VSEL',css_class="border-black",style='left:360px; top:10px; width:100px;height:100px;')

#            self.label = flx.Label(text='', flex=1)  # take all remaining space


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
#        self.label.set_text('LED is ' + str(self.led) + ' HV is ' +  str(self.hv) + ' VSEL is ' + str(self.vsel))

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

flx.config.port = 8888
app = flx.App(SlowControlGUI)
#app.launch('browser')  # show it now in a browser
app.serve('')
flx.start()  # enter the mainloop
