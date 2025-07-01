from pymeasure.instruments import Instrument, Channel

class CouplingMeasurement(Channel):
    """A class to represent a single coupling measurement.
    This class holds the properties of a coupling measurement, such as frequency, voltage, and various coupling parameters.
    """
    
    frequency = Channel.measurement(
        "MEASure:COUPling:FREQ? {ch}",
        """A floating point property that returns the frequency of the measurement.""",
    )
    
    voltage = Channel.measurement(
        "MEASure:COUPling:VOLT? {ch}",
        """A floating point property that returns the voltage level of the measurement.""",
    )
        
    k = Channel.measurement(
        "MEASure:COUPling:K? {ch}",
        """A property that returns the coupling coefficient K."""
    )
    
    k1 = Channel.measurement(
        "MEASure:COUPling:K1? {ch}",
        """A property that returns the primary coupling coefficient K1."""
    )
    
    k2 = Channel.measurement(
        "MEASure:COUPling:K2? {ch}",
        """A property that returns the secondary coupling coefficient K2."""
    )
    
    Ls1_prim = Channel.measurement(
        "MEASure:COUPling:LS1Prim? {ch}",
        """A property that returns the primary inductance of the first winding Ls1_prim."""
    )
    
    Lm = Channel.measurement(
        "MEASure:COUPling:LM? {ch}",
        """A property that returns the mutual inductance Lm."""
    )
    
    Ls2_prim = Channel.measurement(
        "MEASure:COUPling:LS2Prim? {ch}",
        """A property that returns the primary inductance of the second winding Ls2_prim."""
    )
    
    Ls = Channel.measurement(
        "MEASure:COUPling:LS? {ch}",
        """A property that returns the self-inductance Ls."""
    )
    
    Lp = Channel.measurement(
        "MEASure:COUPling:LP? {ch}",
        """A property that returns the primary inductance Lp."""
    )
    
    N = Channel.measurement(
        "MEASure:COUPling:N? {ch}",
        """A property that returns the turns ratio N."""
    )
    
    v1 = Channel.measurement(
        "MEASure:COUPling:V1? {ch}",
        """A property that returns the voltage V1."""
    )
    
    v2 = Channel.measurement(
        "MEASure:COUPling:V2? {ch}",
        """A property that returns the voltage V2."""
    )
    
    nPrim = Channel.measurement(
        "MEASure:COUPling:NPRIMary? {ch}",
        """A property that returns the number of primary turns."""
    )
    
    nSec = Channel.measurement(
        "MEASure:COUPling:NSECondary? {ch}",
        """A property that returns the number of secondary turns."""
    )
    
    L1 = Channel.measurement(
        "MEASure:COUPling:L1? {ch}",
        """A property that returns the inductance of the primary winding L1."""
    )
    
    L2 = Channel.measurement(
        "MEASure:COUPling:L2? {ch}",
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
        "MEASure:COUPling:NUMBer?",
        """A property that returns the number of measurements taken."""
    )
    
    channels = Instrument.MultiChannelCreator(CouplingMeasurement, list(range(1, n)))

    frequency = Instrument.setting(
        "MEASure:COUPling:FREQuency %g",
        """Set the frequency for the measurement."""
    )
    
    voltage = Instrument.setting(
        "MEASure:COUPling:VOLTage %g",
        """Set the voltage level for the measurement."""
    )
    
    nPrim = Instrument.setting(
        "MEASure:COUPling:NPRIMary %d",
        """Set the number of primary turns."""
    )
    
    nSec = Instrument.setting(
        "MEASure:COUPling:NSECondary %d",
        """Set the number of secondary turns."""
    )
