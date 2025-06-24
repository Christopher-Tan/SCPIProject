from pymeasure.instruments import Instrument

class CouplingMeasurer(Instrument):
    def __init__(self, adapter, name="Coupling Measurer", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )
        
    frequency = Instrument.control(
        "MEASure:COUPling:FREQ?",
        "MEASure:COUPling:FREQ %g",
        """A floating point property that controls the frequency of the measurement.""",
    )
    
    voltage = Instrument.control(
        "MEASure:COUPling:VOLT?",
        "MEASure:COUPling:VOLT %g",
        """A floating point property that controls the voltage level of the measurement.""",
    )
    
    def measure(self):
        self.write("MEAS")
    
    k = Instrument.measurement(
        "MEASure:COUPling:K?",
        """A property that returns the coupling coefficient K."""
    )
    
    k1 = Instrument.measurement(
        "MEASure:COUPling:K1?",
        """A property that returns the primary coupling coefficient K1."""
    )
    
    k2 = Instrument.measurement(
        "MEASure:COUPling:K2?",
        """A property that returns the secondary coupling coefficient K2."""
    )
    
    Ls1_prim = Instrument.measurement(
        "MEASure:COUPling:LS1Prim?",
        """A property that returns the primary inductance of the first winding Ls1_prim."""
    )
    
    Lm = Instrument.measurement(
        "MEASure:COUPling:LM?",
        """A property that returns the mutual inductance Lm."""
    )
    
    Ls2_prim = Instrument.measurement(
        "MEASure:COUPling:LS2Prim?",
        """A property that returns the primary inductance of the second winding Ls2_prim."""
    )
    
    Ls = Instrument.measurement(
        "MEASure:COUPling:LS?",
        """A property that returns the self-inductance Ls."""
    )
    
    Lp = Instrument.measurement(
        "MEASure:COUPling:LP?",
        """A property that returns the primary inductance Lp."""
    )
    
    N = Instrument.measurement(
        "MEASure:COUPling:N?",
        """A property that returns the turns ratio N."""
    )
    
    v1 = Instrument.measurement(
        "MEASure:COUPling:V1?",
        """A property that returns the voltage V1."""
    )
    
    v2 = Instrument.measurement(
        "MEASure:COUPling:V2?",
        """A property that returns the voltage V2."""
    )
    
    nPrim = Instrument.control(
        "MEASure:COUPling:NPRIMary?",
        "MEASure:COUPling:NPRIMary %g",
        """An integer property that controls the number of primary turns.""",
    )
    
    nSec = Instrument.control(
        "MEASure:COUPling:NSECondary?",
        "MEASure:COUPling:NSECondary %g",
        """An integer property that controls the number of secondary turns.""",
    )