import libbcm2835._bcm2835 as soc

class CvDriver:
    def __init__(self):
        # The PWM range, determines the resolution
        self.range = 1024
        # The lowest MIDI note, for 0 V
        self.zero_volt_note = 0
        # The highest MIDI note
        self.max_note = self.zero_volt_note + 12 * 4 + 1
        # The PWM value to produce the highest note
        self.max_note_value = self.range

        # Use GPIO 12, header pin 32, PWM0
        # Not sure why this isn't defined, but here's the value
        # pwm_pin = soc.RPI_V2_GPIO_P1_32 
        self.pwm_pin = 12

        self.pwm_channel = 0
        
        # Use GPIO 17, header pin 11
        self.gate_pin = soc.RPI_V2_GPIO_P1_11

        ok = soc.bcm2835_init()
        if not ok:
            raise Exception('bcm2835_init() failed')

        # The BCM2835 library docs say that PWM is on ALT5, but the BCM2711 datasheet says ALT0
        soc.bcm2835_gpio_fsel(self.pwm_pin, soc.BCM2835_GPIO_FSEL_ALT0)


        # Set the PWM clock divider
        # 19.2 MHz / 64 = 300 kHz
        soc.bcm2835_pwm_set_clock(soc.BCM2835_PWM_CLOCK_DIVIDER_64)

        # Set PWM0 to Mark-Space mode (shouldn't matter), enabled
        # Mark-Space mode is normal PWM
        # Balanced mode will distribute the 1s and 0s evenly to achieve a much higher switching frequency
        # This is cool, but probably not necessary.
        # For now, I want to see a normal PWM signal
        soc.bcm2835_pwm_set_mode(self.pwm_channel, 0, True)

        # Set the PWM range to 1024, giving 10-bit resolution
        # 19.2 MHz / 64 / 1024 = 293 Hz
        soc.bcm2835_pwm_set_range(self.pwm_channel, self.range)

        # Set the PWM output to 0
        soc.bcm2835_pwm_set_data(self.pwm_channel, 0)

        # Set the gate pin to output
        soc.bcm2835_gpio_fsel(self.gate_pin, soc.BCM2835_GPIO_FSEL_OUTP)

        # Set the gate pin low
        soc.bcm2835_gpio_write(self.gate_pin, soc.LOW)

    def __del__(self):
        # Set the PWM output to 0
        soc.bcm2835_pwm_set_data(self.pwm_channel, 0)
        # Set the gate pin low
        soc.bcm2835_gpio_write(self.gate_pin, soc.LOW)
        soc.bcm2835_close()

    def note_on(self, note):
        '''note is a MIDI note number'''
        value = (note - self.zero_volt_note) / (self.max_note - self.zero_volt_note) * self.max_note_value
        value = min(value, self.range)
        value = max(value, 0)
        value = int(value)
        # Set the PWM value
        soc.bcm2835_pwm_set_data(self.pwm_channel, value)

        # Set the gate pin high
        soc.bcm2835_gpio_write(self.gate_pin, soc.HIGH)

    def note_off(self):
        # Set the gate pin low
        soc.bcm2835_gpio_write(self.gate_pin, soc.LOW)
