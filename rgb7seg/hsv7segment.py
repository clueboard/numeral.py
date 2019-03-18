#!/usr/bin/env python3

import math
from colorsys import hsv_to_rgb

from .is31fl3235a import IS31FL3235A


class RGBSegment(object):
    """A single RGB LED segment on the numeral.
    """
    def __init__(self, led1, led2, led3):
        self.leds = (led1, led2, led3)
        self.hsv = [0, 0, 0]

    def __get__(self, instance, owner):
        return self.hsv

    def __set__(self, instance, value):
        if not isinstance(value, list) or len(list) != 3:
            raise ValueError('RGBSegment objects only accept 3 item lists.')
        self.hsv = value


class HSV7Segment(object):
    """A class that represents the state of a single RGB 7 Segment numeral.

    All colors are specified in the HSV colorspace with a value between 0 and 1. Gamma correction is applied after conversion to HSV and before conversion to PWM, for the highest possible resolution.

    Segment Layout:

        This diagram shows how the segments are laid out on the numeral.

        |--A--|
        F     B
        |--G--|
        E     C
        |--D--| DP

    Options:

        gamma_correction
            A tuple describing gamma correction factors for Red, Green, and Blue channels. To my eye it seems like red needs just a little bit more correction than blue or green.
    """
    def __init__(self, gamma_correction=(2.5, 2.4, 2.4), buffered=False, **is31fl3235a_kwargs):
        """Setup the HSV7Segment state.

        Options:

            buffered
                When True writes are not sent to the IC immediately. You will need to call `self.update()` to update the IC.

            gamma_correction
                A tuple describing gamma correction factors for each channel. Format: (R, G, B)

        For all other options refer to the IS31FL3235A class.
        """
        self.is31fl3235a = IS31FL3235A(buffered=buffered, **is31fl3235a_kwargs)
        self.buffered = buffered

        # Per channel gamma correction values
        self.gamma_r = 2.5
        self.gamma_g = 2.4
        self.gamma_b = 2.4

        # Setup the segment state
        self._a = RGBSegment(17, 16, 15)
        self._b = RGBSegment(22, 21, 20)
        self._c = RGBSegment(26, 27, 28)
        self._d = RGBSegment(1, 2, 3)
        self._e = RGBSegment(4, 5, 6)
        self._f = RGBSegment(9, 7, 8)
        self._g = RGBSegment(14, 13, 12)
        self._dp = RGBSegment(23, 24, 25)
        self.segments = {'a':self._a, 'b':self._b, 'c':self._c, 'd':self._d, 'e':self._e, 'f':self._f, 'g':self._g, 'dp':self._dp}

    @property
    def a(self):
        return self._a

    @a.setter
    def a(self, value):
        if not isinstance(value, list) or len(value) != 3:
            raise ValueError('HSV7Segment segments only accept 3 item lists.')
        self._a.hsv = value
        if not self.buffered:
            self.update()

    @property
    def b(self):
        return self._b

    @b.setter
    def b(self, value):
        if not isinstance(value, list) or len(value) != 3:
            raise ValueError('HSV7Segment segments only accept 3 item lists.')
        self._b.hsv = value
        if not self.buffered:
            self.update()

    @property
    def c(self):
        return self._c

    @c.setter
    def c(self, value):
        if not isinstance(value, list) or len(value) != 3:
            raise ValueError('HSV7Segment segments only accept 3 item lists.')
        self._c.hsv = value
        if not self.buffered:
            self.update()

    @property
    def d(self):
        return self._d

    @d.setter
    def d(self, value):
        if not isinstance(value, list) or len(value) != 3:
            raise ValueError('HSV7Segment segments only accept 3 item lists.')
        self._d.hsv = value
        if not self.buffered:
            self.update()

    @property
    def e(self):
        return self._e

    @e.setter
    def e(self, value):
        if not isinstance(value, list) or len(value) != 3:
            raise ValueError('HSV7Segment segments only accept 3 item lists.')
        self._e.hsv = value
        if not self.buffered:
            self.update()

    @property
    def f(self):
        return self._f

    @f.setter
    def f(self, value):
        if not isinstance(value, list) or len(value) != 3:
            raise ValueError('HSV7Segment segments only accept 3 item lists.')
        self._f.hsv = value
        if not self.buffered:
            self.update()

    @property
    def g(self):
        return self._g

    @g.setter
    def g(self, value):
        if not isinstance(value, list) or len(value) != 3:
            raise ValueError('HSV7Segment segments only accept 3 item lists.')
        self._g.hsv = value
        if not self.buffered:
            self.update()

    @property
    def dp(self):
        return self._dp

    @dp.setter
    def dp(self, value):
        if not isinstance(value, list) or len(value) != 3:
            raise ValueError('HSV7Segment segments only accept 3 item lists.')
        self._dp.hsv = value
        if not self.buffered:
            self.update()

    def gamma_correct(self, rgb):
        return (
            int(math.pow(float(rgb[0]), self.gamma_r)),
            int(math.pow(float(rgb[1]), self.gamma_g)),
            int(math.pow(float(rgb[2]), self.gamma_b)),
        )

    def rgb2pwm(self, rgb):
        """Convert an RGB value (0-1) to PWM (0-255).
        """
        return (
            int((rgb[0] * 255.0) + 0.5),  # Add 0.5 so that we round up when needed
            int((rgb[1] * 255.0) + 0.5),
            int((rgb[2] * 255.0) + 0.5),
        )

    def update(self):
        """Write the current state to the ic.
        """
        for segment in self.segments.values():
            rgb = hsv_to_rgb(*segment.hsv)
            corrected_rgb = self.gamma_correct(rgb)
            pwm = self.rgb2pwm(rgb)
            for color, led in zip(pwm, segment.leds):
                self.is31fl3235a[led] = color

        if self.buffered:
            self.is31fl3235a.update()


if __name__ == '__main__':
    from time import sleep
    myNumeral = HSV7Segment()
    myNumeral.a = [1, 1, 1]
    myNumeral.b = [1, 1, 1]
    myNumeral.c = [1, 1, 1]
    myNumeral.d = [1, 1, 1]
    sleep(1)
    myNumeral.a = [0, 0, 0]
    myNumeral.b = [0, 0, 0]
    myNumeral.c = [0, 0, 0]
    myNumeral.d = [0, 0, 0]
