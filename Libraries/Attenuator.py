#Code to connect and talk to the JDSU Attenuator using the Prologix TCP/IP GPIB device#
from plx_gpib_ethernet import PrologixGPIBEthernet

class Attenuator:
    def open_port(self, ip,channel):
        #connect to Keithley using its IP address#
        print('connecting')
        self.plx=PrologixGPIBEthernet(ip)
        self.plx.connect()
        self.plx.select(channel)
        print('done')

    def setAtt(self,att):
        #set attenuation in dB#
        self.plx.write('ATT %s' % str(att))

    def getAtt(self):
        #get attenuation in dB#
        return float(self.plx.query('ATT?'))

    def setWVL(self,wvl):
        #set WVL in nm#
        self.plx.write('WVL %sNM' % str(wvl))

    def getWVL(self):
        #get set WVL in nm#
        return float(self.plx.query('WVL?'))*10**9

    def getWVLbound(self):
        #get WVK boundries of device in nm#
        minwvl=int(float(self.plx.query('WVL? MIN'))*10**9)
        maxwvl=int(float(self.plx.query('WVL? MAX'))*10**9)
        return minwvl,maxwvl

    def write(self,text):
        #write custom command to Attenuator#
        self.plx.write('%s' % text)

    def ask(self,text):
        #Ask custom command to Attenuator#
        return self.plx.query('%s' % text)
        
    def close(self):
        self.plx.close()