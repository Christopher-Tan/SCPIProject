from pymeasure.instruments import Instrument, Channel

class CouplingMeasurement(Channel):
    """A class to represent a single coupling measurement.
    This class holds the properties of a coupling measurement, such as frequency, voltage, and various coupling parameters.
    """
    
    frequency = Channel.measurement(
        "MEASure:HISTory:COUPling:FREQ? {ch}",
        """A floating point property that returns the frequency of the measurement.""",
    )
    
    voltage = Channel.measurement(
        "MEASure:HISTory:COUPling:VOLT? {ch}",
        """A floating point property that returns the voltage level of the measurement.""",
    )
        
    k = Channel.measurement(
        "MEASure:HISTory:COUPling:K? {ch}",
        """A property that returns the coupling coefficient K."""
    )
    
    k1 = Channel.measurement(
        "MEASure:HISTory:COUPling:K1? {ch}",
        """A property that returns the primary coupling coefficient K1."""
    )
    
    k2 = Channel.measurement(
        "MEASure:HISTory:COUPling:K2? {ch}",
        """A property that returns the secondary coupling coefficient K2."""
    )
    
    Ls1_prim = Channel.measurement(
        "MEASure:HISTory:COUPling:LS1Prim? {ch}",
        """A property that returns the primary inductance of the first winding Ls1_prim."""
    )
    
    Lm = Channel.measurement(
        "MEASure:HISTory:COUPling:LM? {ch}",
        """A property that returns the mutual inductance Lm."""
    )
    
    Ls2_prim = Channel.measurement(
        "MEASure:HISTory:COUPling:LS2Prim? {ch}",
        """A property that returns the primary inductance of the second winding Ls2_prim."""
    )
    
    Ls = Channel.measurement(
        "MEASure:HISTory:COUPling:LS? {ch}",
        """A property that returns the self-inductance Ls."""
    )
    
    Lp = Channel.measurement(
        "MEASure:HISTory:COUPling:LP? {ch}",
        """A property that returns the primary inductance Lp."""
    )
    
    N = Channel.measurement(
        "MEASure:HISTory:COUPling:N? {ch}",
        """A property that returns the turns ratio N."""
    )
    
    v1 = Channel.measurement(
        "MEASure:HISTory:COUPling:V1? {ch}",
        """A property that returns the voltage V1."""
    )
    
    v2 = Channel.measurement(
        "MEASure:HISTory:COUPling:V2? {ch}",
        """A property that returns the voltage V2."""
    )
    
    nPrim = Channel.measurement(
        "MEASure:HISTory:COUPling:NPRIMary? {ch}",
        """A property that returns the number of primary turns."""
    )
    
    nSec = Channel.measurement(
        "MEASure:HISTory:COUPling:NSECondary? {ch}",
        """A property that returns the number of secondary turns."""
    )
    
    L1 = Channel.measurement(
        "MEASure:HISTory:COUPling:L1? {ch}",
        """A property that returns the inductance of the primary winding L1."""
    )
    
    L2 = Channel.measurement(
        "MEASure:HISTory:COUPling:L2? {ch}",
        """A property that returns the inductance of the secondary winding L2."""
    )

class CouplingMeasurer(Instrument):
    """A class to interface with a coupling measurement instrument.
    This class provides methods to control the instrument and retrieve measurement data.
    It allows setting the frequency and voltage for measurements, and retrieving various coupling parameters.
    """
    def __init__(self, adapter, name="Coupling Measurer", **kwargs):
        """Initialize the CouplingMeasurer with the specified adapter and name.
        
        Args:
            adapter: The communication adapter for the instrument.
            name (str): The name of the instrument, default is "Coupling Measurer".
            **kwargs: Additional keyword arguments for the Instrument class.
        """
        super().__init__(
            adapter,
            name,
            **kwargs
        )
    
    def measure(self):
        self.write("MEAS")
    
    n = Instrument.measurement(
        "MEASure:HISTory:COUPling:NUMBer?",
        """A property that returns the number of measurements taken."""
    )
    
    channels = Instrument.MultiChannelCreator(CouplingMeasurement, list(range(1, n)))

    frequency = Instrument.control(
        "MEASure:COUPling:FREQuency?",
        "MEASure:COUPling:FREQuency %g",
        """A property that controls the frequency for the measurement."""
    )
    
    voltage = Instrument.control(
        "MEASure:COUPling:VOLTage?",
        "MEASure:COUPling:VOLTage %g",
        """A property that controls the voltage level for the measurement."""
    )
    
    nPrim = Instrument.control(
        "MEASure:COUPling:NPRIMary?",
        "MEASure:COUPling:NPRIMary %d",
        """A property that controls the number of primary turns."""
    )
    
    nSec = Instrument.control(
        "MEASure:COUPling:NSECondary?",
        "MEASure:COUPling:NSECondary %d",
        """A property that controls the number of secondary turns."""
    )
