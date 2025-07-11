#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2017 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from pymeasure.instruments import Instrument
import numpy as np

class Agilent34461A(Instrument):
    """
    Represent the HP/Agilent/Keysight 34461A and related multimeters.

    Implemented measurements: voltage_dc, voltage_ac, current_dc, current_ac, resistance, resistance_4w
    """
    #only the most simple functions are implemented
    voltage_dc = Instrument.measurement("MEAS:VOLT:DC? DEF,DEF", "DC voltage, in Volts")
    
    voltage_ac = Instrument.measurement("MEAS:VOLT:AC? DEF,DEF", "AC voltage, in Volts")
    
    current_dc = Instrument.measurement("MEAS:CURR:DC? DEF,DEF", "DC current, in Amps")
    
    current_ac = Instrument.measurement("MEAS:CURR:AC? DEF,DEF", "AC current, in Amps")
    
    #temp = Instrument.measurement("MEAS:TEMP? DEF,DEF", "temp, in Degree")

    resistance = Instrument.measurement("MEAS:RES? DEF,DEF", "Resistance, in Ohms")
    
    resistance_4w = Instrument.measurement("MEAS:FRES? DEF,DEF", "Four-wires (remote sensing) resistance, in Ohms")
    
    def __init__(self, adapter, delay=0.02, **kwargs):
        super(Agilent34465A, self).__init__(
            adapter, "HP/Agilent/Keysight 34465A Multimiter", **kwargs
        )
    
    def initMeasurement(self):
        self.write("INIT") 

    def initTrigger(self, source="BUS", delay="MIN"):
        # SOURCE: 
            # IMM   	The trigger signal is always present. When you place the instrument in the "wait-for-trigger" state, the trigger is issued immediately.
            # BUS	    The instrument is triggered by *TRG over the remote interface once the DMM is in the "wait-for-trigger" state
            # EXT   	The instrument accepts hardware triggers applied to the rear-panel Ext Trig input and takes the specified number of measurements (SAMPle:COUNt), each time a TTL pulse specified by OUTPut:TRIGger:SLOPe is received. If the instrument receives an external trigger before it is ready, it buffers one trigger.       
        command = "TRIG:SOUR " + source +";DEL "+ delay
        self.write(command)

    def startMeasurement(self, samples=5, trgsrc="BUS",trgdel="MIN"):
        self.initTrigger(trgsrc,trgdel)
        command = "SAMP:COUN " + str(samples)
        self.write(command)
        self.initMeasurement()
        if(trgsrc=="BUS"):
            self.write("*TRG")


    def getMeasurement(self, average=True):
        ret = self.ask("FETC?")
        ret = ret.split(",")
        ret_arr = [float(x) for x in ret]
        self.write("TRIG:SOUR IMM")
        if(average):
            return np.mean(ret_arr)
        else:
            return ret_arr

    def confTemp(self, type="FRTD",subtype="100", unit="C", NPLC="1"):
        """type: RTD(2 wire resistance temperature detector), FRTD(4 wire), FTHermistor(4 wire), THERmistor(2 wire), TCouple(2wire)
           subtype: for RTD/FTD: nominal resistor value,  for TCouple type: (E, J, K, N, R, T) 
           unit: C, F, K """
        if(type=="FRTD" or type=="RTD"):
            command="CONF:TEMP "+type+",85;:TEMP:TRAN:"+type+":RES "+subtype
        elif(type=="FTH" or type =="THER"):
            command="CONF:TEMP "+type+",5000"
        else:
            command="CONF:TEMP "+type+","+subtype #TODO: Unterscheidung TCoupletypen: J, K, N, R, T 
        self.write(command)
        self.write("TEMP:NPLC "+ NPLC+";:UNIT:TEMP " + unit)        

    def confCurr(self, mode="AUTO", ACDC = "DC", NPLC= "1"):
        # mode:
        # ACDC: AC or DC
        command = "CONF:CURR:" + ACDC + " " + mode +";:" "CURR:" + ACDC + ":NPLC " + NPLC
        self.write(command)

    def confVolt(self, mode="AUTO", ACDC = "DC", NPLC= "1"):
        # mode:
        # ACDC: AC or DC
        command = "CONF:VOLT:" + ACDC + " " + mode +";:" "VOLT:" + ACDC + ":NPLC " + NPLC
        self.write(command)

    def confRes2(self, mode="AUTO"):
        # mode:
        command = "CONF:RES:DC " + mode
        self.write(command)
    
    def confRes4(self, mode="AUTO"):
        # mode:
        command = "CONF:FRES:DC " + mode
        self.write(command)

    def setLabel(self, text="hacked"):
        command = "SYST:LAB '" + str(text) + "'"
        self.write(command)

    def setText(self, text="hacked"):
        command = "DISP:TEXT '" + str(text) + "'"
        self.write(command)

    def clearText(self):
        command = "DISP:TEXT:CLE"
        self.write(command)

    def setView(self, view="NUM"):
        # options: NUMeric, HISTogram,TCHart, METer
        command = "DISP:VIEW " + view
        self.write(command)

    def getError(self):
        return self.ask("SYST:ERR?")

    def beepbeep(self):
        self.write("SYST:BEEP")

    def resetError(self):
        while True:
            err = self.ask("SYST:ERR:NEXT?")
            print(err)
            if "No error" in err:
                break