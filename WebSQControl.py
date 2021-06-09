#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
The MIT License (MIT)

Copyright (c) 2016 Single Quantum B. V. and Andreas Fognini

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import socket
import json
import threading
import time
import numpy as np
import re
import ast
import sys
#from sync import synchronized_method, synchronized_with_attr

# Next part (Start -> End) based on: http://www.theorangeduck.com/page/synchronized-python 2016-June-1st
# Which is released under BSD3 license
# Start
def synchronized_method(method, *args, **kws):
    outer_lock = threading.Lock()
    lock_name = "__"+method.__name__+"_lock"+"__"
    def sync_method(self, *args, **kws):
        with outer_lock:
            if not hasattr(self, lock_name):
                setattr(self, lock_name, threading.Lock())
            lock = getattr(self, lock_name)
            with lock:
                return method(self, *args, **kws)
    sync_method.__name__   = method.__name__
    sync_method.__doc__    = method.__doc__
    sync_method.__module__ = method.__module__
    return sync_method

def _synchronized_method(method):
    return decorate(method,_synchronized_method)

def synchronized_with_attr(lock_name):
    def decorator(method):
        def synced_method(self, *args, **kws):
            lock = getattr(self, lock_name)
            with lock:
                return method(self, *args, **kws)
        synced_method.__name__   = method.__name__
        synced_method.__doc__    = method.__doc__
        synced_method.__module__ = method.__module__
        return synced_method
    return decorator
# End

class SQTalk(threading.Thread):
    def __init__(self, TCP_IP_ADR = 'localhost', TCP_IP_PORT = 12000, error_callback=None):
        threading.Thread.__init__(self)
        self.TCP_IP_ADR  = TCP_IP_ADR
        self.TCP_IP_PORT = TCP_IP_PORT

        self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.TCP_IP_ADR, self.TCP_IP_PORT))
        self.socket.settimeout(.1)
        self.BUFFER =10000000
        self.shutdown =False
        self.labelProps = dict()

        self.error_callback = error_callback

        self.lock = threading.Lock()

    @synchronized_method
    def close(self):
        #print("Closing Socket")
        self.socket.close()
        self.shutdown = True

    @synchronized_method
    def send(self, msg):
        if sys.version_info.major == 3:
            self.socket.send(bytes(msg,"utf-8"))
        if sys.version_info.major == 2:
            self.socket.send(msg)

    def sub_jsons(self, msg):
        """Return sub json strings.
        {}{} will be returned as [{},{}]
        """
        i = 0
        result = []
        split_msg = msg.split('}{')
        for s in range(len(split_msg)):
            if i==0 and len(split_msg)==1:
                result.append(split_msg[s])
            elif i==0 and len(split_msg)>1:
                result.append(split_msg[s]+"}")
            elif i==len(split_msg)-1 and len(split_msg)>1:
                result.append("{"+split_msg[s])
            else:
                result.append("{"+split_msg[s]+"}")
            i+=1
        return result

    @synchronized_method
    def add_labelProps(self, data):
        if "label" in data.keys():
            #After get labelProps, queries also bounds, units etc...
            if isinstance(data["value"],(dict)):
                self.labelProps[data["label"]]=data["value"]
            #General label communication, for example from broadcasts
            else:
                try:
                    self.labelProps[data["label"]]["value"]=data["value"]
                except:
                    None

    @synchronized_method
    def check_error(self,data):
        if "label" in data.keys():
            if "Error" in data["label"]:
                self.error_callback(data["value"])

    @synchronized_method
    def get_label(self,label):
        timeout = 10
        dt = .1
        i = 0
        while True:
            if i*dt>timeout:
                raise IOError("Could not aquire label")
            try:
                return self.labelProps[label]
                break
            except:
                time.sleep(dt)
            i+=1

    @synchronized_method
    def get_all_labels(self,label):
        return self.labelProps

    def run(self):

        self.send(json.dumps({"request": "labelProps", "value": "None"}))
        rcv_msg=[]

        while self.shutdown == False:
            try:
                rcv=""+rcv_msg[1]

            except:
                rcv=""
            data = {}
            r=""
            while "\x17" not in rcv:
                try:
                    if sys.version_info.major == 3:
                        r =str(self.socket.recv(self.BUFFER),'utf-8')
                    elif sys.version_info.major == 2:
                        r =self.socket.recv(self.BUFFER)
                except:
                    None
                rcv = rcv + r

            rcv_msg =rcv.split("\x17")

            for rcv_line in rcv_msg:
                rcv_split = self.sub_jsons(rcv_line)
                for msg in rcv_split:
                    try:
                        data = json.loads(msg)
                    except Exception as e:
                        None

                    with self.lock:
                        self.add_labelProps(data)
                        self.check_error(data)

class SQCounts(threading.Thread):
    def __init__(self, TCP_IP_ADR = 'localhost', TCP_IP_PORT = 12345, CNTS_BUFFER =100):
        threading.Thread.__init__(self)
        self.lock =threading.Lock()
        self.rlock =threading.RLock()
        self.TCP_IP_ADR  = TCP_IP_ADR
        self.TCP_IP_PORT = TCP_IP_PORT

        self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.TCP_IP_ADR, self.TCP_IP_PORT))
        #self.socket.settimeout(.1)
        self.BUFFER =1000000
        self.shutdown =False

        self.cnts =[]
        self.CNTS_BUFFER =CNTS_BUFFER
        self.n = 0

    @synchronized_method
    def close(self):
        #print("Closing Socket")
        self.socket.close()
        self.shutdown =True

    @synchronized_method
    def get_n(self, n):
        n0 = self.n
        while self.n <= n0+n:
            time.sleep(0.001)
        cnts = self.cnts
        return cnts[-n:]

    def run(self):
        data=[]
        while self.shutdown == False:
            if sys.version_info.major == 3:
                data_raw =str(self.socket.recv(self.BUFFER),'utf-8')
            elif sys.version_info.major == 2:
                data_raw =self.socket.recv(self.BUFFER)

            data_newline =data_raw.split('\n')

            v =[]
            for d in data_newline[0].split(','):
                v.append(float(d))

            with self.lock:
                self.cnts.append(np.array(v))
                #Keep Size of self.cnts
                l = len(self.cnts)
                if l>self.CNTS_BUFFER:
                    self.cnts =self.cnts[l-self.CNTS_BUFFER:]
                self.n += 1

class WebSQControl(object):
    def __init__(self, TCP_IP_ADR = 'localhost', CONTROL_PORT = 12000, COUNTS_PORT = 12345):
        self.TCP_IP_ADR  = TCP_IP_ADR
        self.CONTROL_PORT = CONTROL_PORT
        self.COUNTS_PORT = COUNTS_PORT
        self.NUMBER_OF_DETECTORS = 0

    def connect(self):
        self.talk = SQTalk(TCP_IP_ADR=self.TCP_IP_ADR,  TCP_IP_PORT = self.CONTROL_PORT, error_callback = self.error)
        #Daemonic Thread close when main progam is closed
        self.talk.daemon =True
        self.talk.start()

        self.cnts =SQCounts(TCP_IP_ADR=self.TCP_IP_ADR, TCP_IP_PORT=self.COUNTS_PORT)
        #Daemonic Thread close when main progam is closed
        self.cnts.daemon =True
        self.cnts.start()

        self.NUMBER_OF_DETECTORS = self.talk.get_label("NumberOfDetectors")["value"]


    def close(self):
        self.talk.close()
        #self.talk.join()
        self.cnts.close()
        #self.cnts.join()

    def error(self, error_msg):
        """Called in case of an error"""
        print("ERROR DETECTED")
        print(error_msg)

    def aquire_cnts(self,n):
        """Aquire n count measurments.
        Args:
             n (int): number of count measurments
        Return (numpy_array): Aquired counts with timestamp in first column.
        """
        return self.cnts.get_n(n)

    def set_measurement_periode(self, t_in_ms):
        msg = json.dumps(dict(command="SetMeasurementPeriod", label= "InptMeasurementPeriod", value=t_in_ms))
        self.talk.send(msg)

    def get_number_of_detectors(self):
        return self.talk.get_label("NumberOfDetectors")["value"]

    def get_measurement_periode(self):
        """Get measurment periode in ms.
        Return (float): time
        """
        return self.talk.get_label("InptMeasurementPeriod")["value"]

    def get_bias_current(self):
        return self.talk.get_label("BiasCurrent")["value"]

    def get_trigger_level(self):
        return self.talk.get_label("TriggerLevel")["value"]

    def get_bias_voltage(self):
        msg = json.dumps(dict(request="BiasVoltage"))
        self.talk.send(msg)
        return self.talk.get_label("BiasVoltage")["value"]

    def set_bias_current(self, current_in_uA):
        array = current_in_uA
        msg = json.dumps(dict(command="SetAllBiasCurrents", label= "BiasCurrent", value=array))
        self.talk.send(msg)

    def set_trigger_level(self, trigger_level_mV):
        array = trigger_level_mV
        msg =json.dumps(dict(command="SetAllTriggerLevels", label= "TriggerLevel", value=array))
        self.talk.send(msg)

    def enable_detectors(self,state = True):
        msg = json.dumps(dict(command="DetectorEnable", label="DetectorEnable", value=state))
        self.talk.send(msg)

    def set_dark_counts_auto_iv(self, dark_counts):
        """
        Set the dark counts for the automatic detector calibration.
        After this command execute: self.auto_cali_bias_currents()
        """
        if self.NUMBER_OF_DETECTORS != len(dark_counts):
            raise ValueError('Dark counts not the same lenght as number of detectors')
        else:
            msg =json.dumps(dict(command="DarkCountsAutoIV", label="DarkCountsAutoIV", value=dark_counts))
            self.talk.send(msg)

    def auto_cali_bias_currents(self):
        """
        Performs the automatic bias calibration. Make sure that no light reaches the detectors during this procedure.
        To check if this function has finished use self.auto_cali_finished() which return true or false.
        """
        msg =json.dumps(dict(command="AutoCaliBiasCurrents", value=True))
        self.talk.send(msg)

    def auto_cali_finished(self):
        """
        Check if auto calibration of the bias currents to find a given dark count value has finished.
        Returns: True if finished, False otherwise
        """
        msg =json.dumps(dict(request="StartAutoIV"))
        self.talk.send(msg)
        return not(self.talk.get_label("StartAutoIV")["value"])

if __name__ == "__main__":
    websq = WebSQControl(TCP_IP_ADR="localhost")
    websq.connect()
    websq.set_measurement_periode(10)
    websq.enable_detectors(True)

    while True:
        websq.set_bias_current(current_in_uA=[12.0,8.0,3.0,8.0])
        websq.set_trigger_level(trigger_level_mV=[23.0,24.0,25.0,26.0])
        print("N_Measurements: " + str(websq.aquire_cnts(10)))
        print(websq.get_measurement_periode())
        print(websq.get_bias_current())
        print(websq.get_trigger_level())
        print("Bias Voltage: " + str(websq.get_bias_voltage()))
    websq.close()
