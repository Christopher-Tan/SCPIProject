#get temp debug
from pymeasure.instruments.agilent import Agilent34465A
#from pymeasure.instruments.rohdeschwarz import HMP4030
from pymeasure.instruments.rohdeschwarz import Hmc804X
from pymeasure.instruments.keysight import KeysightE4980AL
#from pymeasureauxiliary.dynplot import Dynplt
import matplotlib.pyplot as plt
import time
import numpy as np

import yaml
import os

from datetime import datetime

try:
    import lgpio
except ImportError:
    print("lgpio module not found. Please install it to use GPIO functionality.")
    lgpio = None

def float_attempt(value):
    """Convert a value to float if possible, otherwise return as string."""
    try:
        return float(value)
    except ValueError:
        return value
    
from utils import *
config = read_config()

class Measurements:
    """Class to hold the measurements of a transformer coupling measurement."""
    def __init__(self):
        self.freq = config['properties']['freq']['default']
        self.voltLvl = config['properties']['voltLvl']['default']
        self.k = ''
        self.k1 = ''
        self.k2 = ''
        self.Ls1_prim = ''
        self.Lm = ''
        self.Ls2_prim = ''
        self.Ls = ''
        self.Lp = ''
        self.N = ''
        self.nPrim = config['properties']['nPrim']['default']
        self.nSec = config['properties']['nSec']['default']
        self.v1_prim = ''
        self.v2_prim = ''
        self.v1_sec = ''
        self.v2_sec = ''
        self.L1 = ''
        self.L2 = ''
        self.time = ''
        
    def __str__(self):
        """Return a string representation of the measurements."""
        return ';'.join([f"{k}:{v}" for k, v in vars(self).items()])
            
    def measure(self):
        """Perform the measurement and update the attributes."""
        global config
        config = read_config()
        measurements = measure(self.freq, self.voltLvl, self.nPrim, self.nSec)
        for key, value in measurements.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.time = str(datetime.now())

    def __copy__(self):
        """Create a copy of the measurements."""
        new_measurements = Measurements()
        for key, value in vars(self).items():
            setattr(new_measurements, key, value)
        return new_measurements
    
        
def measure(freq=config['properties']['freq']['default'], voltLvl=config['properties']['voltLvl']['default'], nPrim=config['properties']['nPrim']['default'], nSec=config['properties']['nSec']['default']):
    """Measure the coupling of a transformer with given primary and secondary turns.
    
    Args:
        freq (float): Frequency for the measurement in Hz.
        voltLvl (float): Voltage level for the measurement in V.
        Prim (int): Number of primary turns.
        Sec (int): Number of secondary turns.
    
    Returns:
        tuple: A tuple containing the measured values:
            - L1: Inductance of the primary side in H.
            - L2: Inductance of the secondary side in H.
            - v1: Voltage on the primary side in V.
            - v2: Voltage on the secondary side in V.
            - k: Coupling factor.
            - k1: Coupling factor for primary to secondary.
            - k2: Coupling factor for secondary to primary.
            - Ls1_prim: Stray inductance on the primary side in H.
            - Lm: Magnetizing inductance in H.
            - Ls2_prim: Stray inductance on the secondary side reflected to primary in H.
            - Ls: Total stray inductance in H.
            - Lp: Primary inductance in H.
            - N: Winding ratio (secondary to primary).
    """
    coupMeas_DMM1 = Agilent34465A(config['measurement_devices']['_DMM1'])
    coupMeas_DMM2 = Agilent34465A(config['measurement_devices']['_DMM2'])
    coupMeas_LCR = KeysightE4980AL(config['measurement_devices']['_LCR'])

    coupMeas_DMM1.resetError()
    coupMeas_DMM2.resetError()
    
    chip = lgpio.gpiochip_open(4)
    
    def initCouplingMeasurement(freq=config['properties']['freq']['default'], voltLvl=config['properties']['voltLvl']['default']):
        # init LCR meter
        coupMeas_LCR.initCouplingMeasurement(freq=freq, voltLvl=voltLvl)

        # init power supply
        # coupMeas_PS.write('*RST')
        # init channels 1-n
        channels = [18,15,14]
        for c in channels:
            lgpio.gpio_claim_output(chip, c)
            lgpio.gpio_write(chip, c, 1)
        
        # init digital multimeter
        multimeters = [coupMeas_DMM1, coupMeas_DMM2]
        labels = ["DMM 1", "DMM 2"]
        for idx, dmm in enumerate(multimeters):
            dmm.reset()
            dmm.confVolt(ACDC="AC")
            dmm.setLabel(labels[idx])
            dmm.initTrigger(source="BUS", delay="MIN")
            # dmm.write("TRIG:DEL:AUTO ON")
            dmm.startMeasurement(samples=2)


    def startMeasurement(nPrim=config['properties']['nPrim']['default'], nSec=config['properties']['nSec']['default']):
        def setVoltage(channels, voltages):
            for c, v in zip(channels, voltages):
                lgpio.gpio_write(chip, c, v)
        
        def getDMMmeasurements(samples=5):
            coupMeas_DMM1.startMeasurement(samples=samples)
            coupMeas_DMM2.startMeasurement(samples=samples)

            val_dmm1 = coupMeas_DMM1.getMeasurement()
            val_dmm2 = coupMeas_DMM2.getMeasurement()

            return val_dmm1, val_dmm2

    # step 1: perform LCR measurement
        delay = 0.5
        channels = [18,15,14]
        voltages = [0,0,0]
        setVoltage(channels, voltages)
        time.sleep(delay)

        print('Raw values from measurement')

        L1 = float(coupMeas_LCR.startMeasurement()) # return inductance in SI-unit
        print('L1 = %3.3f uH' %(L1*1e6))    

    # step 2: perform DMM1 and DMM2 measurement
        channels = [14]
        voltages = [1]
        setVoltage(channels, voltages)
        time.sleep(0.8) # prevent error
        [v1_1, v2_1] = getDMMmeasurements()

    # step 3: swap DMMs and perform measurement again (DMM1 <-> DMM2)
        channels = [15]
        voltages = [1]
        setVoltage(channels, voltages)
        time.sleep(delay)
        [v1_2, v2_2] = getDMMmeasurements()

        # turn off all channels
        channels = [18,15,14]
        voltages = [0,0,0]
        setVoltage(channels, voltages)

        # calculate coupling factor
        v1_prim = (v1_1 + v2_2)/2
        v2_prim = (v2_1 + v1_2)/2
        k1 = v2_prim/v1_prim*nPrim/nSec
        print(v1_prim)
        print(v2_prim)
        print('k1 = %3.4f' %(k1))

    # step 4: perform LCR measurement on secondary side (same as step 1)
        channels = [18]
        voltages = [1]
        setVoltage(channels, voltages)
        time.sleep(delay)

        L2 = float(coupMeas_LCR.startMeasurement())
        print('L2 = %3.3f uH' %(L2*1e6))

    # step 5: perform DMM1 and DMM2 measurement (same as step 2)
        channels = [14]
        voltages = [1]
        setVoltage(channels, voltages)
        time.sleep(delay)
        [v1_1, v2_1] = getDMMmeasurements()

    # step 6: swap DMMs and perform measurement again (DMM1 <-> DMM2) (same as step 3)
        channels = [15]
        voltages = [1]
        setVoltage(channels, voltages)
        time.sleep(delay)
        [v1_2, v2_2] = getDMMmeasurements()

        # turn off all channels
        channels = [18,15,14]
        voltages = [0,0,0]
        setVoltage(channels, voltages)

        # calculate coupling factor
        v1_sec = (v1_1 + v2_2)/2
        v2_sec = (v2_1 + v1_2)/2
        k2 = v1_sec/v2_sec*nSec/nPrim
        print('k2 = %3.4f' %(k2))

    # calculation Party 
        print('\nT-Model (reflected to primary side)')
        k = np.sqrt(k1*k2)

        Ls1_prim = L1*(1-k1)
        Ls2_sec  =L2*(1-k2)
        Lm = L1*k1
        Ls2_prim = Ls2_sec / (nSec/nPrim)**2 # reflect stray inductance from secondary to primary side


        print("Ls1_prim = %f uH" %(Ls1_prim*1e6))
        print("Lm = %f uH" %(Lm*1e6))
        print("Ls2_prim = %f uH" %(Ls2_prim*1e6))

        print('\nGamma-Model (representation on primary side)')
        Ls = Ls1_prim + Ls2_prim*Lm/(Ls2_prim+Lm) # stray inductance
        Lp = Lm**2/(Ls2_prim + Lm) # magnetizing inductance


        print("Ls = %f uH" %(Ls*1e6))
        print("Lp = %f uH" %(Lp*1e6))
        print('Coupling k = %3.3f %% / k1 = %3.3f %% / k2 = %3.3f %%' %(k*100, k1*100, k2*100))

        # winding ratio
        N = nSec/nPrim*(1+Ls2_prim/Lm)
        print("N = %f" %(N))
        print("1/N = %f" %(1/N))
        
        return {
            "L1": L1,
            "L2": L2,
            "v1_prim": v1_prim,
            "v2_prim": v2_prim,
            "v1_sec": v1_sec,
            "v2_sec": v2_sec,
            "k": k,
            "k1": k1,
            "k2": k2,
            "Ls1_prim": Ls1_prim,
            "Lm": Lm,
            "Ls2_prim": Ls2_prim,
            "Ls": Ls,
            "Lp": Lp,
            "N": N
        }

    try:
        initCouplingMeasurement(freq, voltLvl)
        measurements = startMeasurement(nPrim, nSec)
    except:
        pass
    
    lgpio.gpiochip_close(chip)
    
    return measurements

if __name__ == '__main__':
    measure()