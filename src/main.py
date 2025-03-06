import select
import sys
import machine
import utime
from machine import Pin
import uasyncio as asyncio
import os
import re

gpio_pins = {7: machine.Pin(7, machine.Pin.OUT), 
             11: machine.Pin(11, machine.Pin.OUT), 
             15: machine.Pin(15, machine.Pin.OUT)}

adc_pin_1 = machine.ADC(26)  # GPIO 26 (ADC0)
adc_pin_2 = machine.ADC(27)  # GPIO 27 (ADC1)
adc_pin_3 = machine.ADC(28)  # GPIO 28 (ADC2)

for pin in gpio_pins:
    gpio_pins[pin].low()

async def idn():
    _SYSNAME = os.uname().sysname
    sys.stdout.write(_SYSNAME)
    await asyncio.sleep_ms(10)
    
# Function to send pulse on GPIO 10
async def send_pulse(pin):
    pin.value(1)  # Set pin HIGH
    await asyncio.sleep(0.2)  # Wait for 1 second
    pin.value(0)  # Set pin LOW

async def pulse_gpio(gpio_pin_number):
    if gpio_pin_number in gpio_pins:
        gpio_pin = gpio_pins[gpio_pin_number]  # Get the correct GPIO pin object
        gpio_pin.high()  # Set the GPIO pin high (pulse start)
        sys.stdout.write(f"GPIO {gpio_pin_number} set HIGH.\n")
        await asyncio.sleep(1)  # Wait for 1 second
        gpio_pin.low()  # Set the GPIO pin low (pulse end)
        sys.stdout.write(f"GPIO {gpio_pin_number} set LOW.\n")
    else:
        sys.stdout.write(f"Error: GPIO pin {gpio_pin_number} is not available for pulsing.\n")
        
async def high_gpio(gpio_pin_number):
    if gpio_pin_number in gpio_pins:
        gpio_pin = gpio_pins[gpio_pin_number]  # Get the correct GPIO pin object
        gpio_pin.high()  # Set the GPIO pin high (pulse start)
        sys.stdout.write(f"GPIO {gpio_pin_number} set HIGH.\n")
    else:
        sys.stdout.write(f"Error: GPIO pin {gpio_pin_number} is not available for pulsing.\n")

async def low_gpio(gpio_pin_number):
    if gpio_pin_number in gpio_pins:
        gpio_pin = gpio_pins[gpio_pin_number]  # Get the correct GPIO pin object
        gpio_pin.low()  # Set the GPIO pin high (pulse start)
        sys.stdout.write(f"GPIO {gpio_pin_number} set LOW.\n")
    else:
        sys.stdout.write(f"Error: GPIO pin {gpio_pin_number} is not available for pulsing.\n")
        
# Function to read ADC values from GPIOs 26, 27, and 28
async def read_adc():
    while True:
        # Read ADC values asynchronously 
        await asyncio.sleep(0.1)
        # Read analog values (0-65535)
        adc_value_1 = adc_pin_1.read_u16()  # Read from GPIO 26
        adc_value_2 = adc_pin_2.read_u16()  # Read from GPIO 27
        adc_value_3 = adc_pin_3.read_u16()  # Read from GPIO 28

        adc_to_v = 3.3 / (65535) 
        v_divider_corr = adc_to_v * 10/(10+6.2)
        # a voltage divider is used to get the 5 V to below 3.3 V
        
        # Convert to voltage
        voltage_1 = adc_value_1 * adc_to_v
        voltage_2 = adc_value_2 * adc_to_v
        voltage_3 = adc_value_3 * adc_to_v
        return voltage_1, voltage_2, voltage_3
        
    
# Function to read commands from the serial port (e.g., from the computer)
async def handle_serial():
    while True:
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:  # Check if data is available
            command = sys.stdin.readline().strip()  # Read the command from serial input

            if command == "get_adc":
                # Read ADC values asynchronously
                voltage_1, voltage_2, voltage_3 = await read_adc()

                # Send the ADC values and voltages back to the serial port
                response = (f"Voltage 26: {voltage_1:.2f} V, Voltage 27: {voltage_2:.2f} V, Voltage 28: {voltage_3:.2f} V")
                sys.stdout.write(response + "\n")
                
            elif command == "get_adc_raw":
                # Read ADC values asynchronously
                voltage_1, voltage_2, voltage_3 = await read_adc()
                response = f"{voltage_1:.2f}, {voltage_2:.2f}, {voltage_3:.2f}"
                sys.stdout.write(response + "\n")
                
            elif command.lower() == "idn" or command.lower() == "*idn?":
                await idn()
                
            elif command.startswith("pulse_"):
                # Extract the GPIO pin number from the command (e.g., "pulse_10")
                try:
                    gpio_pin_number = int(command.split("_")[1])  # Get the number after "pulse_"
                    await pulse_gpio(gpio_pin_number)
                except (IndexError, ValueError):
                    sys.stdout.write("Error: Invalid pulse command. Please use 'pulse_x' where x is a valid GPIO number.\n")
                    
            elif command.startswith("high_"):
                # Extract the GPIO pin number from the command (e.g., "pulse_10")
                try:
                    gpio_pin_number = int(command.split("_")[1])  # Get the number after "pulse_"
                    await high_gpio(gpio_pin_number)
                except (IndexError, ValueError):
                    sys.stdout.write("Error: Invalid high command. Please use 'high_x' where x is a valid GPIO number.\n")
                    
            elif command.startswith("low_"):
                # Extract the GPIO pin number from the command (e.g., "pulse_10")
                try:
                    gpio_pin_number = int(command.split("_")[1])  # Get the number after "pulse_"
                    await low_gpio(gpio_pin_number)
                except (IndexError, ValueError):
                    sys.stdout.write("Error: Invalid low command. Please use 'low_x' where x is a valid GPIO number.\n")
                    
            elif command.startswith("gpio_update"):
                # Extract the GPIO pin number from the command (e.g., "pulse_10")
                try:
                    txt = command.split(':')[1]
                    pins_new = [int(re.findall("\d+", s)[0]) for s in txt]
                    if (len(pins_new) == len(set(pins_new))) and max(pins_new < 40) and min(pins_new >= 0):
                        gpio_pins = {pins_new[0]: machine.Pin(pins_new[0], machine.Pin.OUT), 
                                     pins_new[1]: machine.Pin(pins_new[1], machine.Pin.OUT), 
                                     pins_new[2]: machine.Pin(pins_new[2], machine.Pin.OUT)}
                    else:
                        sys.stdout.write("Error: pins not updated.\n")  # lazy but shouldnt use this
                except (IndexError, ValueError):
                    sys.stdout.write("Error: pins not updated.\n") 
            else:
                sys.stdout.write("Invalid command.\n")

        await asyncio.sleep(0.1)  # Wait briefly before checking again

# Main entry point to start the asyncio event loop
async def main():
    sys.stdout.write("Waiting for commands...\n")
    
    # Start serial command handler
    asyncio.create_task(handle_serial())
    
    # Keep running the event loop
    await asyncio.Event().wait()

# Run the main asyncio event loop
asyncio.run(main())

