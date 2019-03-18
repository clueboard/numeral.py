#!/usr/bin/env python3

from smbus import SMBus

class IS31FL3235A(object):
    """A low-level class that represents a single is31fl3235a.
    """
    def __init__(self, ic_address=None, i2c_bus=None, buffered=False, pmw_33kHz=True, skip_init=False):
        """Sets up the state for the is31fl3235a driver.

            ic_address
                The i2c address for the IC. This is typically one of 4 values: 0x3C, 0x3D, 0x3E, 0x3F

            i2c_bus
                The raspberry pi i2c bus to use. Defaults to 1. Use 0 on early model raspberry pi.

            pwm_33kHz
                Whether or not to switch to 33kHz PWM frequency. True by default. If you set this to False you may get noise in the audible hearing range on VCC.

            skip_init
                When True `self.init_ic()` will not be called.

            buffered
                When True changes to the LED state will not be written immediately. You must call `self.update()` before changes will be reflected by the LEDs.
        """
        self.i2c_bus = SMBus(i2c_bus or 1)
        self.ic_address = ic_address or 0x3F
        self.buffered = buffered
        self.pwm_33kHz = True

        # Registers
        self.led_register_start = 0x2A         # On/Off state for OUT1 (Values: 0/1)
        self.led_register_end = 0x45           # On/Off state for OUT28 (Values: 0/1)
        self.pwm_update_register = 0x25        # Write 0 to update live PWM values with register values (Values: 0)
        self.pwm_register_start = 0x05         # PWM control for OUT1 (Values: 0-255)
        self.pwm_register_end = 0x20           # PWM control for OUT28 (Values: 0-255)
        self.shutdown_register = 0x00          # 0 = software shutdown, 1 = normal operation (Values: 0/1)
        self.global_control_register = 0x4A    # 0 = normal operation, 1 = shutdown all LEDs (Values: 0/1)
        self.output_frequency_register = 0x4B  # Set PWM frequency, 0 = 3kHz, 1 = 22kHz (Values: 0/1)
        self.reset_register = 0x4F             # Write 0 to reset all registers to their default value (Values: 0)

        # LED state. 
        # Index 0 controls whether all LEDs are on or off (0/1)
        # Index 1-28 sets the non-corrected PWM brightness level for an LED
        self.leds = [0 for i in range(-2, self.pwm_register_end - self.pwm_register_start)]
        self.leds[0] = True

        # Prepare for operation
        if not skip_init:
            self.init_ic()

    def __getitem__(self, index):
        if index not in self.leds:
            raise ValueError('%s is not a valid LED!' % index)
        return self.leds[index]

    def __setitem__(self, index, value):
        if index < 0 or index > len(self.leds):
            raise ValueError('(%s)%s is not a valid LED!' % (type(index), index))

        if index == 0:
            if value:
                self.leds[0] = True
                self.write_register(self.global_control_register, 0)  # Normal operation
            else:
                self.leds[0] = False
                self.write_register(self.global_control_register, 1)  # Shutdown all LEDs

            if not self.buffered:
                self.flush()
        else:
            if 0 > value or value > 255:
                raise ValueError('LED brightness must be between 0 and 255! (%s)' % (value,))

            self.leds[index] = int(value + .5)
            if not self.buffered:
                self.update()


    def update(self):
        """Write the current LED status to the IC.
        """
        self.write_register(self.pwm_register_start, self.leds[1:])
        self.flush()

    def flush(self):
        """Make the pending LED changes live.
        """
        self.write_register(self.pwm_update_register, 0)

    def init_ic(self):
        """Setup the led controller.
        """
        # Reset the IC to its default state
        self.write_register(self.reset_register, 0)

        # Set all PWM values to 0 (off)
        for i in range(self.pwm_register_start, self.pwm_register_end):
            self.write_register(i, 0x00)

        # Turn on all LEDs
        for i in range(self.led_register_start, self.led_register_end + 1):
            self.write_register(i, 0xFF)

        # Housekeeping
        self.update()
        if self.pwm_33kHz:
            self.write_register(0x4B, 0x01)  # Set frequency to 33kHz
        self.write_register(0x00, 0x01)  # Start normal operation

    def reset(self):
        """Reset the IC to its startup state.
        """
        self.write_register(self.reset_register, 0)

    def write_register(self, register, value):
        """Write one or more bytes to the i2c bus.

        `register`: The register to write

        `value`: A single byte to write, or a list of bytes to write in succession.
        """
        if not isinstance(value, (int, list, tuple)):
            raise ValueError('value must be an integer, or list/tuple of integers!')

        if isinstance(value, int):
            self.i2c_bus.write_byte_data(self.ic_address, register, value)
        else:
            self.i2c_bus.write_i2c_block_data(self.ic_address, register, value)


if __name__ == '__main__':
    from time import sleep

    display = is31fl3235a()

    # Turn on the Red LEDs
    print('red on')
    red_leds = [1, 4, 9, 14, 17, 22, 23, 26]
    for led in red_leds:
        display[led] = 128
    sleep(2)

    # Blink the LEDs
    print('global off')
    display[0] = False
    sleep(2)
    print('global on')
    display[0] = True
    sleep(2)

    # Turn off the Red LEDs
    print('red off')
    for led in red_leds:
        display[led] = 0
