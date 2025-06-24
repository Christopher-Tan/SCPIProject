from pymeasure.instruments import Instrument

class CouplingMeasurer(Instrument):
    def __init__(self, adapter, name="Coupling Measurer", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )
        
    frequency = Instrument.control(
        "FREQ?",
        "FREQ %g",
        """A floating point property that controls the frequency of the measurement.""",
    )
    
    voltage = Instrument.control(
        "VOLT?",
        "VOLT %g",
        """A floating point property that controls the voltage level of the measurement.""",
    )
    
    def measure(self):
        self.write("MEAS")
    
    k = Instrument.measurement(
        "K?",
        """A property that returns the coupling coefficient K."""
    )
    
    k1 = Instrument.measurement(
        "K1?",
        """A property that returns the primary coupling coefficient K1."""
    )
    
    k2 = Instrument.measurement(
        "K2?",
        """A property that returns the secondary coupling coefficient K2."""
    )
    
    Ls1_prim = Instrument.measurement(
        "LS1Prim?",
        """A property that returns the primary inductance of the first winding Ls1_prim."""
    )
    
    Lm = Instrument.measurement(
        "LM?",
        """A property that returns the mutual inductance Lm."""
    )
    
    Ls2_prim = Instrument.measurement(
        "LS2Prim?",
        """A property that returns the primary inductance of the second winding Ls2_prim."""
    )
    
    Ls = Instrument.measurement(
        "LS?",
        """A property that returns the self-inductance Ls."""
    )
    
    Lp = Instrument.measurement(
        "LP?",
        """A property that returns the primary inductance Lp."""
    )
    
    N = Instrument.measurement(
        "N?",
        """A property that returns the turns ratio N."""
    )