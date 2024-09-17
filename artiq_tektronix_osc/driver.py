import pyvisa
import datetime
import time
import logging
from time import sleep


logger = logging.getLogger("tektronix_osc")


class Tektronix4SeriesScope:

    def __init__(self, ip_address, simulation: bool=False):
        self.ip_address = ip_address
        self._simulation = simulation
        self.op_queue = []
    
    def __enter__(self):
        if self._simulation:
            logger.info("Running in simulation mode")
            return self
        rm = pyvisa.ResourceManager()
        self.scope = rm.open_resource(f"TCPIP::{self.ip_address}::INSTR")
        logger.info(f"Connected to scope at {self.ip_address}")
        logger.info(f"Scope identification: {self.identify()}")
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        if self._simulation:
            logger.info("Running in simulation mode")
            return self
        self.scope.close()
    
    def debug(self, msg, queue):
        logger.debug(f"{'[QUEUE] ' if queue else ''}{msg}")

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
        if self._simulation:
            return True
        idn = self.identify()
        if idn.startswith("TEKTRONIX"):
            return True
        else:
            logger.error(f"Ping failed, invalid identification: {idn}")

    def reset(self, queue=False):
        self.debug("Resetting scope", queue)
        if queue:
            self.op_queue.append('*RST')
            self.op_queue.append('*WAI')
        else:
            self.scope.write('*RST')
            self.wait_for_idle(20)

    def get_screen_png(self):
        self.debug("Saving screen to PNG", False)
        self.scope.write(";".join([
            "SAVe:IMAGe:FILEFormat PNG",
            "SAVe:IMAGe:INKSaver OFF",
            "HARDCopy STARt"]))
        return self.scope.read_raw()
    
    def set_current_datetime(self, queue=False):
        current_datetime = datetime.datetime.now()
        current_date = current_datetime.strftime('%Y-%m-%d')
        current_time = current_datetime.strftime('%H:%M:%S')
        self.debug(f"Setting scope date and time to {current_date} {current_time}", queue)
        ops = [
            f"DATE \"{current_date}\"",
            f"TIME \"{current_time}\""
        ]
        if queue:
            self.op_queue.extend(ops)
        else:
            self.scope.write(";".join())

    # Acquisition operations

    def start_acquisition(self, queue=False):
        self.debug("Preparing acquisition", queue)
        ops = [
            "ACQuire:STOPAfter SEQuence",
            "ACQuire:STATE ON"
        ]
        if queue:
            self.op_queue.extend(ops)
        else:
            self.scope.write(";".join(ops))

    def stop_acquisition(self, queue=False):
        self.debug("Stopping acquisition", queue)
        if queue:
            self.op_queue.append("ACQuire:STATE OFF")
        else:
            self.scope.write("ACQuire:STATE OFF")

    # Channel operations

    def set_channel_vertical_scale(self, channel, scale, queue=False):
        self.debug(f"Setting vertical scale of channel {channel} to {scale}", queue)
        command = f"CH{channel}:SCAle {scale:.3g}"
        if queue:
            self.op_queue.append(command)
        else:
            self.scope.write(command)
    
    def set_channel_vertical_position(self, channel, position, queue=False):
        self.debug(f"Setting vertical position of channel {channel} to {position}", queue)
        command = f"CH{channel}:POSition {position:.3g}"
        if queue:
            self.op_queue.append(command)
        else:
            self.scope.write(command)

    def set_channel_termination(self, channel, fifty_ohms=False, queue=False):
        impedance = "FIFty" if fifty_ohms else "MEG"
        self.debug(f"Setting termination of channel {channel} to {impedance}", queue)
        command = f"CH{channel}:IMPedance {impedance}"
        if queue:
            self.op_queue.append(command)
        else:
            self.scope.write(command)

    def set_channel_label(self, channel, label, queue=False):
        self.debug(f"Setting label of channel {channel} to {label}", queue)
        command = f"CH{channel}:LABel \"{label}\""
        if queue:
            self.op_queue.append(command)
        else:
            self.scope.write(command)

    def set_channel_coupling(self, channel, ac=False, queue=False):
        coupling = "AC" if ac else "DC"
        self.debug(f"Setting coupling of channel {channel} to {coupling}", queue)
        command = f"CH{channel}:COUPling {coupling}"
        if queue:
            self.op_queue.append(command)
        else:
            self.scope.write(command)

    def enable_channel_display(self, channel, queue=False):
        self.debug(f"Enabling display of channel {channel}", queue)
        command = f"SELect:CH{channel} ON"
        if queue:
            self.op_queue.append(command)
        else:
            self.scope.write(command)
    
    def disable_channel_display(self, channel, queue=False):
        self.debug(f"Disabling display of channel {channel}", queue)
        command = f"SELect:CH{channel} OFF"
        if queue:
            self.op_queue.append(command)
        else:
            self.scope.write(command)

    def set_channel(self, channel, enabled=True, vertical_scale=1.0, 
                    vertical_position=0.0, termination_fifty_ohms=False, 
                    label="", ac_coupling=False, queue=False):
        self.set_channel_vertical_scale(channel, vertical_scale, queue)
        self.set_channel_vertical_position(channel, vertical_position, queue)
        self.set_channel_termination(channel, termination_fifty_ohms, queue)
        self.set_channel_label(channel, label, queue)
        self.set_channel_coupling(channel, ac_coupling, queue)
        if enabled:
            self.enable_channel_display(channel, queue)
        else:
            self.disable_channel_display(channel, queue)

    # Timing and triggering operations

    def set_horizontal_scale(self, scale, queue=False):
        self.debug(f"Setting horizontal scale to {scale}", queue)
        command = f"HORizontal:SCAle {scale:.3g}"
        if queue:
            self.op_queue.append(command)
        else:
            self.scope.write(command)

    def set_horizontal_position(self, position, queue=False):
        self.debug(f"Setting horizontal position to {position}", queue)
        command = f"HORizontal:DELay:TIMe {position:.3g}"
        if queue:
            self.op_queue.append(command)
        else:
            self.scope.write(command)

    def set_trigger(self, channel, level=0.0, slope="RISE", mode="NORMAL", queue=False):
        assert mode in ['NORMAL', 'AUTO'], "Invalid trigger mode"
        assert slope in ['RISE', 'FALL'], "Invalid trigger slope"
        self.debug(f"Setting trigger to channel {channel}, level {level}, slope {slope}, mode {mode}", queue)
        commands = [
            f"TRIGger:A:MODE {mode}",
            f"TRIGger:A:EDGE:SLOPe {slope}",
            f"TRIGger:A:EDGE:SOURce CH{channel}",
            f"TRIGger:A:LEVel {level:.3g}"
        ]
        if queue:
            self.op_queue.extend(commands)
        else:
            self.stop_acquisition()
            self.scope.write(";".join(commands))

    # One to rule them all

    def setup(self, channel_configs, horizontal_scale, horizontal_position, trigger_config, queue=False):
        self.reset(queue)
        self.set_current_datetime(queue)

        for ch_cfg in channel_configs:
            self.set_channel(**ch_cfg, queue=queue)
        
        # Waveform time will be 10*horizontal scale
        self.set_horizontal_scale(horizontal_scale, queue)
        self.set_horizontal_position(horizontal_position, queue)

        # Slope: RISE/FALL
        # Mode: NORMAL/AUTO
        self.set_trigger(**trigger_config, queue=queue)
        self.start_acquisition(queue)

        if not queue:
            # Wait for the scope to be ready
            sleep(3)

    def clear_queue(self):
        self.op_queue = []

    def run_queue(self):
        self.debug("Running queued operations", False)
        if self._simulation:
            logger.info("Running in simulation mode")
            return
        self.scope.write(";".join(self.op_queue))
        self.clear_queue()
        sleep(3)
