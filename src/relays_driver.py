import time
import os
import serial
from serial.serialutil import SerialBase

# relay driver is controlled by a pi pico 2

class relay_driver():
    port: str
    
    def __init__(
        self, 
        port='COM3',#: str, 
        cmd_wait=0.2,#: float, #| int,
        time_out=2.0,#: float # | int,
    ):
        self.port = port
        self._cmd_wait = cmd_wait
        self._timeout = time_out
        self._pins = [7, 11, 15]
        
    def open(self):
        # connect to pi pico 2 and check connection to servo drive 
        try: 
            self._RP2350 = serial.Serial(self.port, 
                                         baudrate=115200,
                                         timeout=self._timeout)
            # clear buffer
            time.sleep(self._cmd_wait)
            bytesToRead = self._RP2350.inWaiting()
            resp = self._RP2350.read(bytesToRead).decode("utf-8")
            print(resp)
            
            # Now check connection by reading the idn
            resp = self.idn(self._RP2350,).decode("utf-8")
            print("Id: {}".format(resp))
            if not resp:
                RuntimeError("No reponse from pi pico 2.")                         
        except serial.serialutil.SerialException:
            print("Error opening relay driver")
            return(False, 'Error opening pi pico 2')
        
    def close(self):
        self._RP2350.close()
        
    def idn(self, ser: SerialBase) -> str:
        return self.query_command(ser, command="idn")    
    
    def write_command(self, ser: SerialBase, command: str) -> str:
        ser.write(bytes((command + "\n").encode('ascii')))
        time.sleep(self._cmd_wait)
    
    def query_command(self, ser, command: str):
        self.write_command(ser, command)
        time.sleep(self._cmd_wait)
        bytesToRead = self._RP2350.inWaiting()
        return self._RP2350.read(bytesToRead)
    
    def pulse_gpio(self, gpio: int):
        return self.query_command(self._RP2350, 'pulse_'+str(gpio))
    
    def high_gpio(self, gpio: int):
        return self.query_command(self._RP2350, 'high_'+str(gpio))
    
    def low_gpio(self, gpio: int):
        return self.query_command(self._RP2350, 'low_'+str(gpio))
    
    def read_adc(self):
        self._RP2350.read(self._RP2350.inWaiting())
        return self.query_command(self._RP2350, 'get_adc')
    
    def read_adc_raw(self):
        self._RP2350.read(self._RP2350.inWaiting())
        adc_raw = self.query_command(self._RP2350, 'get_adc_raw')
        return [float(i) for i in adc_raw.decode("utf-8").strip().split(',')]
    
    def update_gpio(self, gpio_pin1=7, gpio_pin2=11, gpio_pin3=15):
        return self.query_command(self._RP2350, 
                                  f'gpio_update:{gpio_pin1,gpio_pin2,gpio_pin3}')
    
    def get_states(self):
        # state 1 is led on, NO is closed
        return [1 if x < 1.5 else 0 for x in self.read_adc_raw()]
                 
    def force_state(self, state: int, pin: int):
        # Determine pin index to ascertain which adc voltage to use to discern state
        try:
            idx = self._pins.index(pin)
        except ValueError:
            print("Pin is not in the pin list provided by user")
       
        state_i = self.get_states()[idx]
        cnt = 0
        attempts = 3
        if state_i == state:
            pass
        else:
            while (cnt <= attempts) & (state_i != state):
                self.pulse_gpio(pin)
                time.sleep(1) # was 1 s puslses for trigger
                state_i = self.get_states()[idx]
                cnt += 1
        if cnt > attempts:
            print("no state change")
        return state_i
        
    def force_state_all(self, state: int):
        # can speed this up by moving it to pi and using asyncio
        for pin in self._pins:
            self.force_state(state, pin)
