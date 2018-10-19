#!/usr/bin/env python3
"""
This is a caproto IOC that exposes one PV named 'rpi:color' by default. It
expects a HEX color code like 'ffffff'. It updates the duty cycle of a PWM
signal to three color channels accordingly. The IOC requires parameters to
configure which GPIO pin corresponds to each color channel, for example:

./rgb.py --red 15 --green 22 --blue 11

For general options, like debug logging, see help:

./rgb.py -h
"""
import asyncio
from caproto.server import pvproperty, PVGroup, template_arg_parser, run
import RPi.GPIO as GPIO


def rescale(x):
    # Put on a 0-100 (duty cycle) scale, and apply gamma.
    # The gamma value (2.8) comes from the vendor of the RGB LED, which
    # cites it with the caveat, "The default of 2.8 isn't super-scientific,
    # just tested a few numbers and this seemed to produce a sufficiently
    # uniform brightness ramp along an LED strip."
    # https://learn.adafruit.com/led-tricks-gamma-correction/the-longer-fix
    return 100 * (x / 255)**2.8


def duty_cycle(color):
    """Given a HEX color, Compute PWM duty cycle percentage each channel."""
    rgb255 = {'red': (color & 0xff0000) >> 16,
              'green': (color & 0x00ff00) >> 8,
              'blue': (color & 0x0000ff) >> 0}

    return {channel: rescale(val)
            for channel, val in rgb255.items()}


class IOC(PVGroup):
    def __init__(self, *, red, green, blue, **kwargs):
        super().__init__(**kwargs)
        self.pins = {'red': int(red), 'green': int(green), 'blue': int(blue)}
        self.pwm = {}

    async def write_color(self, instance, value):
        color_base10 = int(value[0], 16)
        for channel, val in duty_cycle(color_base10).items():
            self.pwm[channel].ChangeDutyCycle(val)
        return value

    color = pvproperty(value=['000000'], put=write_color)

    @color.startup
    async def color(self, instance, async_lib):
        GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
        for pin in self.pins.values():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)  # LOW -> off

        for channel, pin in self.pins.items():
            self.pwm[channel] = GPIO.PWM(pin, 2000)  # set frequency to 2KHz

        # Initial duty Cycle = 0(leds off)
        for pwm in self.pwm.values():
            pwm.start(0)

    @color.shutdown
    async def color(self, instance, async_lib):
        for pwm in self.pwm.values():
            pwm.ChangeDutyCycle(0)
        for pwm in self.pwm.values():
            pwm.stop(0)
        for pin in self.pins.values():
            GPIO.output(pin, GPIO.LOW)    # Turn off all leds
        GPIO.cleanup()


if __name__ == '__main__':
    parser, split_args = template_arg_parser(
        default_prefix='rpi:',
        desc='Run an IOC that colors RGB LEDs.',
        supported_async_libs=('asyncio',))

    for channel in ('red', 'green', 'blue'):
        parser.add_argument(f'--{channel}',
                            help=f'The BOARD pin for the {channel} channel',
                            required=True, type=str)

    args = parser.parse_args()
    ioc_options, run_options = split_args(args)
    ioc = IOC(red=args.red, green=args.green, blue=args.blue, **ioc_options)
    run(ioc.pvdb, **run_options)
