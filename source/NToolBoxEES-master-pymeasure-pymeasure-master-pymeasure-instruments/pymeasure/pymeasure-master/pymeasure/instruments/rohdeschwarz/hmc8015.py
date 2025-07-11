from os import write
import string
from pymeasure.instruments import Instrument

class Hmc8015(Instrument):
	"""
	Represent the HMC8015 Power Analyzer
	There are four measurement windows with 6 cells each available
	Command is "VIEW:NUMeric:PAGE<n>:CELL<m>:FUNCtion?"

	Where <n> is number of page (1...4)
	and   <m> is number of cell (1...6-10)
	With functions

	P Active power P (Watt)
	S Apparent power S (VA)
	Q Reactive power Q (var)
	LAMBda Power factor λ (PF)
	PHI Phase difference Φ ( ° )
	FU Voltage frequency fU (V)
	FI Current frequency fI (A)
	URMS True rms voltage Urms (V)
	UAVG Voltage average (V)
	IRMS True rms current Irms (A)
	IAVG Current average (A)
	UTHD Total harmonic distortion of voltage Uthd (THD %)
	ITHD Total harmonic distortion of current Ithd (THD %)
	FPLL PLL source frequency fPLL (Hz)
	TIME Integration time
	WH Watt hour (Wh)
	WHP Positive watt hour (Wh)
	WHM Negative watt hour (Wh)
	AH Ampere hour (Ah)
	AHP Positive ampere hour (Ah)
	AHM Negative ampere hour (Ah)
	URANge Voltage range
	IRANge Current range
	EMPTy Empty cell
	"""

	
	#only the most simple functions are implemented
	measOrderDef = "URMS,IRMS,UTHD,ITHD,P,Q,S,LAMB,FU,UAVG"#"URMS,IRMS,UTHD,FU,P,Q,S"
	measOrder = ""
	dictMeas = {}

	#URMS 	= Instrument.measurement("CHAN:MEAS:DATA? 1", "Root mean square voltage, in Volts")

	def __init__(self, adapter, delay=0.02, **kwargs):
		super(Hmc8015, self).__init__(
			adapter, "HMC8015 Power Analyzer", **kwargs
		)
		
		if(kwargs.get("measOrder") != None):
			self.measOrder = kwargs.get("measOrder")
		else:
			self.measOrder = self.measOrderDef
		self.initializeMeasurement()
		self.initializeScope()

	def initializeMeasurement(self):
		command = "CHAN:MEAS:FUNC " + self.measOrder
		self.write(command)

	def initializeScope(self):
		self.write("VIEW:NUM 1")
		self.write("CHAN:VOLT:RANG:AUTO 1")
		self.write("CHAN:CURR:RANG:AUTO 1")
		
		dataM = self.measOrder.split(",") 
		if len(dataM) > 10:
			print("To many measurment data, only first 10 available")

		if len(dataM) <= 6:
			scope = 6
			self.write("VIEW:NUM:PAGE1:SIZE 6")
		else:
			scope = 10
			self.write("VIEW:NUM:PAGE1:SIZE 10")

		for idx,m in enumerate(dataM):
			command = "VIEW:NUM:PAGE1:CELL" + str(idx+1) +":FUNC " + m
			self.dictMeas[m] = str(idx+1)
			self.write(command)
			if idx == 10:
				break

		for i in range(len(dataM),scope):
			command = "VIEW:NUM:PAGE1:CELL" + str(i+1) +":FUNC EMPT" 
			self.write(command)

	def getMeasurementData(self, key):
		if key in self.dictMeas.keys():
			cmdSCPI = "CHAN:MEAS:DATA? " + self.dictMeas[key]
			dat = float(self.ask(cmdSCPI))
			return dat
		return None

	def getP(self):
		return self.getMeasurementData("P")

	def getS(self):
		return self.getMeasurementData("S")

	def getQ(self):
		return self.getMeasurementData("Q")

	def getLAMB(self):
		return self.getMeasurementData("LAMB")

	def getPHI(self):
		return self.getMeasurementData("PHI")

	def getFU(self):
		return self.getMeasurementData("FU")

	def getFI(self):
		return self.getMeasurementData("FI")

	def getURMS(self):
		return self.getMeasurementData("URMS")

	def getUAVG(self):
		return self.getMeasurementData("UAVG")

	def getIRMS(self):
		return self.getMeasurementData("IRMS")

	def getIAVG(self):
		return self.getMeasurementData("IAVG")
	
	def getUTHD(self):
		return self.getMeasurementData("UTHD")
	
	def getITHD(self):
		return self.getMeasurementData("ITHD")
	
	def getFPLL(self):
		return self.getMeasurementData("FPLL")
	
	def getTIME(self):
		return self.getMeasurementData("TIME")
	
	def getWH(self):
		return self.getMeasurementData("WH")
	
	def getWHP(self):
		return self.getMeasurementData("WHP")
	
	def getWHM(self):
		return self.getMeasurementData("WHM")

	def getAH(self):
		return self.getMeasurementData("AH")

	def getAHP(self):
		return self.getMeasurementData("AHP")

	def getAHM(self):
		return self.getMeasurementData("AHM")

