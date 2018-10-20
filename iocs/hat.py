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


class IOC(PVGroup):
    def __init__(self, *, pins, **kwargs):
        super().__init__(**kwargs)
        self.pins = pins
        self.pwm = {}

    async def write_state(self, instance, value):
        if value:
            value = GPIO.HIGH
        else:
            value = GPIO.LOW
        for pin in self.pins:
            GPIO.output(pin, value)
        return value

    state = pvproperty(value=0, put=write_state)

    @state.startup
    async def state(self, instance, async_lib):
        GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)  # LOW -> off

    @state.shutdown
    async def state(self, instance, async_lib):
        for pin in self.pins:
            GPIO.output(pin, GPIO.LOW)    # Turn off all leds
        GPIO.cleanup()


if __name__ == '__main__':
    parser, split_args = template_arg_parser(
        default_prefix='rpi:',
        desc='Run an IOC for hats.',
        supported_async_libs=('asyncio',))

    parser.add_argument('--pins',
                        help=f'The BOARD pins to run on',
                        required=True, type=str)

    args = parser.parse_args()
    pins = [int(pin) for pin in args.pins.split(',')]
    ioc_options, run_options = split_args(args)
    ioc = IOC(pins=pins, **ioc_options)
    run(ioc.pvdb, **run_options)
