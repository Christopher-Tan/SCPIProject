import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.instruments import Instrument

class Hmc804X(Instrument):
    """
    Rohde & Schwarz HMC8041 device is initiatied with a vxi connection, and is used to read power supply values. A 
    """
    #-----------------------------------
    #           command
    #-----------------------------------
    def get_command_id(self):
        """Retrieve the IDN from the device"""
        command = "*IDN?"
        response = self.ask(command).strip('\n')
        return response

    #-----------------------------------
    def command(self, command):
        """Simply performs command"""
        value = self.ask(command)
        return value

    #-----------------------------------
    #       SETTING UP
    #-----------------------------------

    #-----------------------------------
    def enable_reset_energy_meas(self):
        """Turns on and resets the energy measurement
        Page 39 of HMC804x SCPI manual"""
        
        # Loop over all channels
        for channel_number in range(1, self.mult_channel+1):
            
            self.select_channel(channel_number)                 # Select the channel
            
            # Turn on measurement
            command = "MEAS:ENER:STAT ON;*OPC?"
            response = int(self.ask(command)[0])

            # Reset if possible
            if response == 1:
                command = "MEAS:ENER:RES;*OPC?"
                response = self.ask(command)
            else:
                raise Exception("Energy measurement could not be turned on")
    
    #-----------------------------------
    def select_channel(self, channel_number):
        """Selects the channel, in case there are more than 1"""
        if self.mult_channel > 1:

            command = f"INST:NSEL {channel_number}"
            self.write(command)

        else:
            pass # Command does not work for single channeled HMC8041, so pass

    
    #-----------------------------------
    #       READING DATA
    #-----------------------------------
    # Page 38 of HMC804XSCPI manual
    def read_voltage(self):
        """Reads voltage from previously selected channel"""
        command = 'MEAS:SCAL:VOLT?'
        value = self.ask(command)
                    

    #-----------------------------------
    def read_current(self):
        """Reads current from previously selected channel"""
        command = 'MEAS:SCAL:CURR?'
        value = self.ask(command)
                    

    #-----------------------------------
    def read_power(self):
        """Reads power from previously selected channel"""
        command = 'MEAS:SCAL:POW?'
        value = self.ask(command)    
                    
    
    #-----------------------------------
    def read_energy(self):
        """Reads energy from previously selected channel since it was resetted"""
        # Must be turned on first!
        command = 'MEAS:SCAL:ENER?'
        value = self.ask(command)
                    

    #-----------------------------------
    def read_measurement_values(self):
        """Faster way of reading all measurement data, with one request.
        Read all the measurement values at the same time, using the self.data_request_string 
        formatted in __init__.
        Returns a list in the form of four strings containing the values of ['V', 'I', 'W','Ws'] """

        response = self.ask(self.data_request_string)
        list_volt_curr_pow_ener = response.strip('\n').split('\n')
        return list_volt_curr_pow_ener
    
    def set_voltage(self, voltage=0):
        command = "VOLT "+str(voltage)
        self.write(command)
    def set_current(self, current=0):
        command = "CURR "+str(current)
        self.write(command)
    def master_enable(self):
        self.write("OUTP:MAST ON")
    def master_disable(self):
        self.write("OUTP:MAST OFF")      
    def set_output(self, state=0):
        command = "OUTP:CHAN "+str(state)
        self.write(command)
    def set_master(self, state=0):
        command = "OUTP:MAST "+str(state)
        self.write(command)      
    def output_disable(self):
        self.write("OUTP:CHAN OFF")
    #-----------------------------------
    #       FORMATTING DATA
    #-----------------------------------
    def append_measurement_values(self):
        """Perform measurement and format add to the data list, can be used easily
        in a loop."""
        values_all_channels = []    # All measurements
        # Loop over all channel numbers
        for channel_number in range(1, self.mult_channel+1):
            self.select_channel(channel_number)                 # Select the channel
            
            values = self.read_measurement_values()             # Read all values of channel
            values_all_channels.extend(values)                  # Add these to the list of all value
         
        self.data.append(values_all_channels)
        return values_all_channels

    #-----------------------------------
    def add_data_to_df(self):
        """Add all the measured data to a dataframe."""
        df = DataFrame(self.data, columns=self.column_names)
        return df

    #-----------------------------------
    def define_column_names(self):
        """Defines column names for the dataframe that can be made"""
        # Loop over all channel numbers
        col_names = []
        for channel_number in range(1, self.mult_channel+1):
            col_name = [f"{self.device_name} - CH{channel_number} Voltage [V]", 
                        f"{self.device_name} - CH{channel_number} Current [A]", 
                        f"{self.device_name} - CH{channel_number} Power [W]", 
                        f"{self.device_name} - CH{channel_number} Energy since inception [J]"]
            col_names.extend(col_name)
        return col_names
    def __init__(self, adapter, **kwargs):
        super(Hmc804X, self).__init__(
            adapter, "Rohde&Schwarz HMC804X power supply", **kwargs
        )
            #-----------------------------------      
        # NAMING
        # Device name, dataframe column names,
        self.command_id = self.get_command_id()
        self.device_name = self.command_id[14:21]
        self.mult_channel = int(self.device_name[-1])   # The last number of the device name is the amount of channels
        self.column_names = self.define_column_names()  
        # DATA
        # Data list, request string for data
        self.data = []
        self.data_request_string = "MEAS:SCAL:VOLT?;\n;MEAS:SCAL:CURR?;\n;MEAS:SCAL:POW?;\n;MEAS:SCAL:ENER?"      
        # SETUP 
        # Energy reset and channel selection
        self.enable_reset_energy_meas()
        self.select_channel(1)                          # preset channel to 1 at start
                                 
                                                                                                             
             

    def check_errors(self):
        """ Read all errors from the instrument."""
        while True:
            err = self.values(":SYST:ERR?")
            if int(err[0]) != 0:
                errmsg = "Rohde&Schwarz HMC804X: %s: %s" % (err[0],err[1])
                log.error(errmsg + '\n')
            else:
                break
