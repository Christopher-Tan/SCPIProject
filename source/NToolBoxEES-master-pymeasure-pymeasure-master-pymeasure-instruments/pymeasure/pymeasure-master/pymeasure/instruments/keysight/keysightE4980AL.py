from pymeasure.instruments import Instrument
import numpy as np

class KeysightE4980AL(Instrument):
    def __init__(self, adapter, delay=0.02, **kwargs):
        super(KeysightE4980AL, self).__init__(
            adapter, 'Keysight E4980AL LCR Meter', **kwargs
        )

    def getId(self):
        self.ask("*IDN?")

    def setFreq(self, val):
        command = "FREQ " + str(val)
        self.write(command)

    def setVoltLvl(self, val):
        command = "VOLT " + str(val)
        self.write(command)

    # init like before from Matlab
    def initCouplingMeasurement(self, freq=100e3, voltLvl=3):

        # copied from former matlab script
        command_lst = [ "SOUR:DCS:STAT OFF;",
                        "BIAS:STAT OFF;",
                        "COMP:BIN:COUN:CLE;",
                        "LIST:CLE:ALL;",
                        "COMP:BIN:CLE;",
                        "AMPL:ALC OFF;",
                        "APER MED,1;",
                        "BIAS:POL:AUTO OFF;",
                        "BIAS:RANG:AUTO ON;",
                        "BIAS:VOLT:LEV 0;",
                        "COMP:ABIN OFF;",
                        "COMP:BIN:COUN:STAT OFF;",
                        "COMP:MODE PTOL;",
                        "COMP:SLIM -9.9e+037,9.9e+037;",
                        "COMP:STAT OFF;",
                        "COMP:SWAP OFF;",
                        "COMP:TOL:NOM 0;",
                        "DISP:ENAB ON;",
                        # "DISP:LINE ;", # test
                        "DISP:WIND:TEXT1:DATA:FMSD:DATA 1e-009;",
                        "DISP:WIND:TEXT2:DATA:FMSD:DATA 1e-009;",
                        "FORM:ASC:LONG OFF;",
                        "FORM:BORD NORM;",
                        "FORM:DATA ASC,64;",
                        "FREQ:CW "+ str(freq) +";",
                        "FUNC:DEV1:MODE OFF;",
                        "FUNC:DEV1:REF:VAL 0;",
                        "FUNC:DEV2:MODE OFF;",
                        "FUNC:DEV2:REF:VAL 0;",
                        "FUNC:IMP:TYPE LSRS;",
                        "FUNC:SMON:IDC:STAT OFF;",
                        "FUNC:SMON:VDC:STAT OFF;",
                        "INIT:CONT OFF;",
                        "LIST:MODE SEQ;",
                        "LIST:STIM:TYPE FREQ,NONE;",
                        "SOUR:DCS:VOLT:LEV 0;",
                        "TRIG:DEL 0;",
                        "TRIG:SOUR INT;",
                        "TRIG:TDEL 0;",
                        "VOLT:LEV "+ str(voltLvl) +";",
                        "DISP:WIND:TEXT1:DATA:FMSD:STAT OFF;",
                        "DISP:WIND:TEXT2:DATA:FMSD:STAT OFF;",
                        "FUNC:DCR:RANG:VAL 100;",
                        "FUNC:IMP:RANG:VAL 100000;",
                        "OUTP:DC:ISOL:LEV:VAL 2e-005;",
                        "OUTP:DC:ISOL:STAT OFF;",
                        "FUNC:DCR:RANG:AUTO ON;",
                        "FUNC:IMP:RANG:AUTO ON;",
                        "OUTP:DC:ISOL:LEV:AUTO ON;",
                        "DISP:PAGE MEAS;"]
        
        
        # command = ' '.join(command_lst)
        for command in command_lst:
            self.write(command)

    def startMeasurement(self, nofRetVal=1):
        self.write('TRIG')
        ret = self.ask("FETC?")
        [ret1, ret2] = ret.split(',')[:2]
        if(nofRetVal == 1):
            return ret1
        else:
            return ret1, ret2