
from pymeasure.instruments import Instrument
import numpy as np


class KeysightE4990A(Instrument):
    '''
    Represent the Keysight E4990A Impedance Analyzer.

    '''

    def __init__(self, adapter, delay=0.02, **kwargs):
        super(KeysightE4990A, self).__init__(
            adapter, 'Keysight E4990A Impedance Analyzer', **kwargs
        )
    def init(self):
        # Clear the event status registers and empty the error queue
        self.write('*CLS')
        # Clear the display status bar cautions / error messages
        self.write('DISP:CCL')
    
    def reset(self):
        # This command presets the setting state of the E4990A to the original factory setting (Default Conditions)
        self.write(':SYST:PRES')     
    
    def getCal(self):
        def print_status(st):
            return "ON" if st else "OFF"
        fixture = self.ask(':SENS:FIXT:SEL?').strip()
        print(f"Fixture: {fixture}")
        print("Fixture compensation status:")
        cmp_status_open = (int)(self.ask(':SENS1:CORR2:OPEN?'))
        print(f"\tOpen fixture compensation: {print_status(cmp_status_open)}")
        cmp_status_short = (int)(self.ask(':SENS1:CORR2:SHOR?'))
        print(f"\tShort fixture compensation: {print_status(cmp_status_short)}")
        cmp_status_load = (int)(self.ask(':SENS1:CORR2:LOAD?'))
        print(f"\tLoad fixture compensation: {print_status(cmp_status_load)}")

    def setOscillator(self, voltage=1.0):
        '''Configure voltage of oscillator. Signal level (5 mVrms to 1 Vrms)'''
        self.write(':SOUR1:MODE VOLT')
        self.write(':SOUR1:VOLT ' + str(voltage))

    # def run_fixture_compensation(inst, cfg):
    #     '''Execute the fixture compensation procedure.'''
    #     self.write(':SYST:PRES')
    #     configure_sweep_parameters(inst, cfg)
    #     self.write(':SENS1:CORR:COLL:FPO USER')
    #     # Per manual (https://bit.ly/2Llu3lW), oscillator voltage should be
    #     # 500 mV during short correction.

    #     setOscillator(inst, 0.5)
    #     print('Starting fixture compensation procedure')
    #     input('Put the test fixture's device contacts in the OPEN state '
    #           'and press [ENTER]')
    #     inst.write(':SENS1:CORR2:COLL:ACQ:OPEN')
    #     inst.query('*OPC?')
    #     input('Put the test fixture's device contacts in the SHORT state '
    #           'and press [ENTER]')
    #     inst.write(':SENS1:CORR2:COLL:ACQ:SHOR')
    #     inst.query('*OPC?')

    def instrSetup(self, trace1MeasType='Z', trace2MeasType='TZ', startFrequency='20', stopFrequency='50e6', numberOfPoints='201', measTime='1'):
        ''' Measurement parameters Z: Absolute impedance value
        Y: Absolute admittance
        R: Equivalent series resistance
        X: Equivalent series reactance
        G: Equivalent parallel conductance
        B: Equivalent parallel susceptance
        LS: Equivalent series inductance
        LP: Equivalent parallel inductance
        CS: Equivalent series capacitance
        CP: Equivalent parallel capacitance
        RS: Equivalent series resistance
        RP: Equivalent parallel resistance
        Q: Q value
        D: Dissipation factor
        TZ: Impedance phase
        TY: Absolute phase
        VAC: OSC level (Voltage)
        IAC: OSC level (Current)
        VDC: DC Bias (Voltage)
        IDC: DC Bias (Current)
        IMP: Impedance (complex value)
        ADM: Admittance (complex value)
        Perform a system preset with hold-off  '''
        
        #self.ask('SYSTem:PRESet;*OPC?')

        # Set the aperture which affects trace noise and repeatability, i.e. averaging
        self.write('SENSe:APERture '+str(measTime))
        
        # Set the start and stop frequencies via concatenated string and use of SCPI SENSe FREQuency branch
        self.write('SENSe:FREQuency:STARt '+str(startFrequency) +
                   ';STOP '+str(stopFrequency))
        # Set the number of trace points (2 to 1601)
        self.write('SENSe:SWEep:POINts '+str(numberOfPoints))
        # Select trace 1 and set measurement format
        self.write('CALCulate:PARameter1:DEFine '+trace1MeasType)
        # Select trace 2 and set measurement format
        self.write('CALCulate:PARameter2:DEFine '+trace2MeasType)
        
    def triggerSingle(self):
        # Abort and reset sweep if active
        self.write('ABORt')
        # Force single trigger with hold-off. Note high aperture counts may result
        # in sweep times in excess of 40s. For these conditions the timeout setting
        # must be altered to allow for this long duration else timeout errors will occur.
        self.write('TRIG:SING')
        self.ask('*OPC?')
        

    def initTrigger(self, source='INT'):
        '''This command sets/gets the trigger source from the following 4 types: 
        INT   	Uses the internal trigger to generate continuous triggers automatically.
        EXT	    Generates a trigger when the trigger signal is inputted externally via the Ext Trig connector or the handler interface.
        BUS   	Generates a trigger when the *TRG is executed.
        MAN   	Generates a trigger when the key operation of Trigger > Trigger is executed from the front panel.
        '''      
        command = 'TRIG:SOUR ' + source
        # MODE: This command turns ON/OFF the continuous initiation mode (setting by which the trigger system initiates continuously) in the trigger
        self.write('INIT1:CONT ON')
        self.write(command)  
        self.ask('*OPC?') 

    def setMarker(self, number='1', type='MAX'):
        ''' Sets marker 1 to 9 (Mk) and reference marker (Mk:10) with function 
        MAX: Sets the search type to the maximum value.
        MIN: Sets the search type to the minimum value.
        PEAK: Sets the search type to the peak search.
        LPEak: Sets the search type to the peak search to the left from the marker position.
        RPEak: Sets the search type to the peak search to the right from the marker position.
        TARGet: Sets the search type to the target search.
        LTARget: Sets the search type to the target search to the left from the marker position.
        RTARget: Sets the search type to the target search to the right from the marker position '''

        self.write(':CALC1:MARK'+number+' ON')
        self.write(':CALC1:MARK'+number+':FUNC:TYPE '+type)
        self.write(':CALC1:MARK'+number+':FUNC:EXEC')

    def setAutoScale(self, trace='1'):
        self.write(':DISPl:WIND1:TRAC1:Y:AUTO')
        self.write(':DISPl:WIND1:TRAC1:Y:AUTO') 

    def setScale(self, trace='1', scalediv=1.0, refvalue=1.0):
        self.write(':DISP:WIND1:TRAC'+trace+':Y:PDIV ' +str(scalediv))
        self.write(':DISP:WIND1:TRAC'+trace+':Y:RLEV ' +str(refvalue))
    def setFormat(self, type='LOG'):
        # This command sets the display type of the graph vertical axis (Y-axis). (LIN / LOG)
        self.write('DISP:WIND1:TRAC1:Y:SPAC '+type)  
    def setDisplay(self, traces='2', split='D1_2'): 
        #  This command sets/gets the number of traces.
        #  Equivalent Softkey Display > Num Of Traces
        self.write('CALC1:PAR:COUN '+traces) 
        #  This command split the traces of the channel display layout on the LCD display.
        #  Equivalent Softkey Display > Allocate Traces > {Display Layout }
        # :DISPlay:WINDow<Ch>:SPLit {D1|D1_2|D12|D1_2_3|D12_34|D1_1_2|D112|D12_33|D13_23|D123|D11_23|D12_13|D1234|D1_2_3_4}
        self.write('DISP:WIND1:SPL '+split)  
         
    def Errcheck(self):
        myError = []
        ErrorList = self.ask('SYST:ERR?').split(',')
        Error = ErrorList[0]
        if int(ErrorList[0]) == 0:
            myError = ErrorList[1]
        else:
            while int(Error) != 0:
                print('Error #: ' + ErrorList[0])
                print('Error Description: ' + ErrorList[1])
                myError.append(ErrorList[0])
                myError.append(ErrorList[1])
                ErrorList = self.ask('SYST:ERR?').split(',')
                Error = ErrorList[0]
                myError = list(myError)
        return myError
