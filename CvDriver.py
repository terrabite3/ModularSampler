import libbcm2835._bcm2835 as soc
import math

class CvDriver:
    def __init__(self):
        # The PWM range, determines the resolution
        self._range = 2 ** 16
        # The lowest MIDI note, for 0 V
        self._zero_volt_note = 0 # not supported yet
        
        # The voltage at 100% duty cycle, found experimentally
        self._max_voltage = 8.815

        # Find the maximum producable note, which is the highest multiple of 1/12
        self._max_note = math.floor(self._max_voltage * 12)
        max_note_voltage = self._max_note / 12
        self._max_note_value = math.floor(max_note_voltage / self._max_voltage * self._range)

        # Use GPIO 12, header pin 32, PWM0
        # Not sure why this isn't defined, but here's the value
        # pwm_pin = soc.RPI_V2_GPIO_P1_32 
        self.pwm_pin = 12

        self._pwm_channel = 0
        
        # Use GPIO 17, header pin 11
        self._gate_pin = 16

        ok = soc.bcm2835_init()
        if not ok:
            raise Exception('bcm2835_init() failed')

        # The BCM2835 library docs say that PWM is on ALT5, but the BCM2711 datasheet says ALT0
        soc.bcm2835_gpio_fsel(self.pwm_pin, soc.BCM2835_GPIO_FSEL_ALT0)


        # Set the PWM clock divider
        # 19.2 MHz / 2 = 9.6 MHz
        soc.bcm2835_pwm_set_clock(soc.BCM2835_PWM_CLOCK_DIVIDER_2)

        # TODO: Look at this!
        # Set PWM0 to Balanced mode, enabled
        # Mark-Space mode is normal PWM
        # Balanced mode will distribute the 1s and 0s evenly to achieve a much higher switching frequency
        # This is cool, but probably not necessary.
        # For now, I want to see a normal PWM signal
        soc.bcm2835_pwm_set_mode(self._pwm_channel, 0, True)

        # Set the PWM range to 65536, giving 16-bit resolution
        # 19.2 MHz / 2 / 65536 = 146 Hz, but balanced mode makes this ok
        soc.bcm2835_pwm_set_range(self._pwm_channel, self._range)

        # Set the PWM output to 0
        soc.bcm2835_pwm_set_data(self._pwm_channel, 0)

        # Set the gate pin to output
        soc.bcm2835_gpio_fsel(self._gate_pin, soc.BCM2835_GPIO_FSEL_OUTP)

        # Set the gate pin low
        soc.bcm2835_gpio_write(self._gate_pin, soc.LOW)

    def __del__(self):
        # Set the PWM output to 0
        soc.bcm2835_pwm_set_data(self._pwm_channel, 0)
        # Set the gate pin low
        soc.bcm2835_gpio_write(self._gate_pin, soc.LOW)
        # Set the gate pin to high impedance
        soc.bcm2835_gpio_fsel(self._gate_pin, soc.BCM2835_GPIO_FSEL_INPT)
        
        soc.bcm2835_close()

    def note_on(self, note):
        '''note is a MIDI note number'''
        value = (note - self._zero_volt_note) / (self._max_note - self._zero_volt_note) * self._max_note_value
        value = min(value, self._range)
        value = max(value, 0)
        value = int(value)
        # Set the PWM value
        soc.bcm2835_pwm_set_data(self._pwm_channel, value)
        # print(value)

        # Set the gate pin high
        soc.bcm2835_gpio_write(self._gate_pin, soc.HIGH)

    def note_off(self):
        # Set the gate pin low
        soc.bcm2835_gpio_write(self._gate_pin, soc.LOW)
