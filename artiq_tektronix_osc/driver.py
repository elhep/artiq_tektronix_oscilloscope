import pyvisa
import datetime
import time
import logging


logger = logging.getLogger("tektronix_osc")


class Tektronix4SeriesScope:

    def __init__(self, ip_address):
        self.ip_address = ip_address
    
    def __enter__(self):
        rm = pyvisa.ResourceManager()
        self.scope = rm.open_resource(f"TCPIP::{self.ip_address}::INSTR")
        logger.info(f"Connected to scope at {self.ip_address}")
        logger.info(f"Scope identification: {self.identify()}")
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.scope.close()

    def identify(self):
        return self.scope.query('*IDN?')

    def wait_for_idle(self, timeout=10):
        start = time.time()
        while True:
            busy = self.scope.query('BUSY?').split(' ')[-1].strip()
            if busy == '0':
                return
            if time.time() - start > timeout:
                raise TimeoutError("Scope did not become idle within the timeout period")
            time.sleep(0.1)

    def ping(self):
        idn = self.identify()
        if idn.startswith("TEKTRONIX"):
            return True
        else:
            logger.error(f"Ping failed, invalid identification: {idn}")

    def reset(self):
        self.debug("Resetting scope")
        self.scope.write('*RST')
        self.wait_for_idle(20)

    def get_screen_png(self):
        self.debug("Saving screen to PNG")
        self.scope.write("SAVe:IMAGe:FILEFormat PNG")
        self.scope.write("SAVe:IMAGe:INKSaver OFF")
        self.scope.write("HARDCopy STARt")
        return self.scope.read_raw()
    
    def set_current_datetime(self):
        current_datetime = datetime.datetime.now()
        current_date = current_datetime.strftime('%Y-%m-%d')
        current_time = current_datetime.strftime('%H:%M:%S')
        logger.debug(f"Setting scope date and time to {current_date} {current_time}")
        self.scope.write(f"DATE \"{current_date}\"")
        self.scope.write(f"TIME \"{current_time}\"")

    # Channel operations

    def set_channel_vertical_scale(self, channel, scale):
        logger.debug(f"Setting vertical scale of channel {channel} to {scale}")
        self.scope.write(f"CH{channel}:SCAle {scale:.3g}")
    
    def set_channel_vertical_position(self, channel, position):
        logger.debug(f"Setting vertical position of channel {channel} to {position}")
        self.scope.write(f"CH{channel}:POSition {position:.3g}")

    def set_channel_termination(self, channel, fifty_ohms=False):
        impedance = "FIFty" if fifty_ohms else "MEG"
        logger.debug(f"Setting termination of channel {channel} to {impedance}")
        self.scope.write(f"CH{channel}:IMPedance {impedance}")

    def set_channel_label(self, channel, label):
        logger.debug(f"Setting label of channel {channel} to {label}")
        self.scope.write(f"CH{channel}:LABel \"{label}\"")

    def set_channel_coupling(self, channel, ac=False):
        coupling = "AC" if ac else "DC"
        logger.debug(f"Setting coupling of channel {channel} to {coupling}")
        self.scope.write(f"CH{channel}:COUPling {coupling}")

    def enable_channel_display(self, channel):
        logger.debug(f"Enabling display of channel {channel}")
        self.scope.write(f"SELect:CH{channel} ON")
    
    def disable_channel_display(self, channel):
        logger.debug(f"Disabling display of channel {channel}")
        self.scope.write(f"SELect:CH{channel} OFF")

    def set_channel(self, channel, enabled=True, vertical_scale=1.0, 
                    vertical_position=0.0, termination_fifty_ohms=False, 
                    label="", ac_coupling=False):
        self.set_channel_vertical_scale(channel, vertical_scale)
        self.set_channel_vertical_position(channel, vertical_position)
        self.set_channel_termination(channel, termination_fifty_ohms)
        self.set_channel_label(channel, label)
        self.set_channel_coupling(channel, ac_coupling)
        if enabled:
            self.enable_channel_display(channel)
        else:
            self.disable_channel_display(channel)

    # Timing and triggering operations

    def set_horizontal_scale(self, scale):
        logger.debug(f"Setting horizontal scale to {scale}")
        self.scope.write(f"HORizontal:SCAle {scale:.3g}")

    def set_trigger(self, channel, level=0.0, slope="RISE", mode="NORMAL"):
        assert mode in ['NORMAL', 'AUTO'], "Invalid trigger mode"
        assert slope in ['RISE', 'FALL'], "Invalid trigger slope"
        logger.debug(f"Setting trigger to channel {channel}, level {level}, slope {slope}, mode {mode}")
        self.scope.write(f"TRIGger:A:MODE {mode}")
        self.scope.write(f"TRIGger:A:EDGE:SLOPe {slope}")
        self.scope.write(f"TRIGger:A:EDGE:SOURce CH{channel}")
        self.scope.write(f"TRIGger:A:LEVel {level:.3g}")
