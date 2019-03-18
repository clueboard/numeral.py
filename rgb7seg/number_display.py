#!/usr/bin/env python3

import random
from time import sleep, time

import smbus

from .hsv7segment import HSV7Segment

start_time = time()

HTML_COLORS = {
    # name      hue         sat  val
    'white':   (0,          0,   0.25),
    'black':   (0,          0,   0),
    'red':     (0,          1,   0.5),
    'maroon':  (0,          1,   0.25),
    'yellow':  (0.16666666, 1,   0.5),
    'olive':   (0.16666666, 1,   0.25),
    'lime':    (0.33333333, 1,   0.5),
    'green':   (0.33333333, 1,   0.25),
    'aqua':    (0.5,        1,   0.5),
    'teal':    (0.5,        1,   0.25),
    'blue':    (0.66666666, 1,   0.5),
    'navy':    (0.66666666, 1,   0.25),
    'fuchsia': (0.83333333, 1,   0.5),
    'purple':  (0.83333333, 1,   0.25)
}


class NumberDisplay(object):
    def __init__(self, i2c_bus=None, ic_address=None, colors=HTML_COLORS):
        self.hsv7seg = HSV7Segment(i2c_bus=i2c_bus, ic_address=ic_address, buffered=True)
        self.segments_enabled = {'a':False, 'b':False, 'c':False, 'd':False, 'e':False, 'f':False, 'g':False, 'dp':False}
        self.color = colors['white']
        self.color_off = colors['black']
        self.colors = colors
        self.characters = {
            '': {'a':False, 'b':False, 'c':False, 'd':False, 'e':False, 'f':False, 'g':False},
            '0': {'a':True, 'b':True, 'c':True, 'd':True, 'e':True, 'f':True, 'g':False},
            '1': {'a':False, 'b':True, 'c':True, 'd':False, 'e':False, 'f':False, 'g':False},
            '2': {'a':True, 'b':True, 'c':False, 'd':True, 'e':True, 'f':False, 'g':True},
            '3': {'a':True, 'b':True, 'c':True, 'd':True, 'e':False, 'f':False, 'g':True},
            '4': {'a':False, 'b':True, 'c':True, 'd':False, 'e':False, 'f':True, 'g':True},
            '5': {'a':True, 'b':False, 'c':True, 'd':True, 'e':False, 'f':True, 'g':True},
            '6': {'a':True, 'b':False, 'c':True, 'd':True, 'e':True, 'f':True, 'g':True},
            '7': {'a':True, 'b':True, 'c':True, 'd':False, 'e':False, 'f':False, 'g':False},
            '8': {'a':True, 'b':True, 'c':True, 'd':True, 'e':True, 'f':True, 'g':True},
            '9': {'a':True, 'b':True, 'c':True, 'd':True, 'e':False, 'f':True, 'g':True},
            'A': {'a':True, 'b':True, 'c':True, 'd':False, 'e':True, 'f':True, 'g':True},
            'C': {'a':True, 'b':False, 'c':False, 'd':True, 'e':True, 'f':True, 'g':False},
            'E': {'a':True, 'b':False, 'c':False, 'd':True, 'e':True, 'f':True, 'g':True},
            'F': {'a':True, 'b':False, 'c':False, 'd':False, 'e':True, 'f':True, 'g':True},
            'H': {'a':False, 'b':True, 'c':True, 'd':False, 'e':True, 'f':True, 'g':True},
            'J': {'a':False, 'b':True, 'c':True, 'd':True, 'e':True, 'f':False, 'g':False},
            'L': {'a':False, 'b':False, 'c':False, 'd':True, 'e':True, 'f':True, 'g':False},
            'P': {'a':True, 'b':True, 'c':False, 'd':False, 'e':True, 'f':True, 'g':True},
            'R': {'a':True, 'b':True, 'c':True, 'd':False, 'e':True, 'f':True, 'g':True},
            'U': {'a':False, 'b':True, 'c':True, 'd':True, 'e':True, 'f':True, 'g':False},
        }
        self.characters['B'] = self.characters['8']
        self.characters['D'] = self.characters['0']
        self.characters['G'] = self.characters['6']
        self.characters['I'] = self.characters['1']
        self.characters['K'] = self.characters['H']
        self.characters['M'] = self.characters['H']
        self.characters['N'] = self.characters['H']
        self.characters['O'] = self.characters['0']
        self.characters['Q'] = self.characters['0']
        self.characters['S'] = self.characters['5']
        self.characters['T'] = self.characters['7']
        self.characters['V'] = self.characters['U']
        self.characters['W'] = self.characters['U']
        self.characters['X'] = self.characters['H']
        self.characters['Y'] = self.characters['4']
        self.characters['Z'] = self.characters['2']

    def update(self):
        for segment in self.hsv7seg.segments:
            if not self.segments_enabled[segment]:
                self.hsv7seg.segments[segment].hsv = self.color_off
            else:
                self.hsv7seg.segments[segment].hsv = self.color
        self.hsv7seg.update()

    def set_color(self, color):
        if not isinstance(color, tuple) and len(color) != 3:
            raise ValueError('set_color(color) must be passed a tuple consisting of (hue, saturation, value)')
        if not (0 <= color[0] <= 1):
            raise ValueError('set_color(color): hue must be between 0 and 1.')
        if not (0 <= color[1] <= 1):
            raise ValueError('set_color(color): saturation must be between 0 and 1.')
        if not (0 <= color[2] <= 1):
            raise ValueError('set_color(color): value must be between 0 and 1.')

        self.color = color
        self.update()
        
    def display(self, character='', color=None):
        character = str(character).upper()
        if character not in self.characters:
            #print('Warning: Character not found!')
            character = ''

        if color:
            self.set_color(color)

        self.segments_enabled.update(self.characters[character])
        self.update()

    def breathing(self):
        """Implementation of an LED breathing effect.

        This function blocks and should be called in a thread or something.
        """
        color = list(self.color)
        top_pause_time = .2
        bottom_pause_time = .4

        while True:
            print('Color:', color)
            x = 0
            while x < 1:
                color[2] = x
                self.set_color(color)
                x += 0.00390625
            sleep(top_pause_time)
            while x >= 0:
                color[2] = x
                self.set_color(color)
                x -= 0.00390625
            sleep(bottom_pause_time)
            color = [random.random(), random.random(), 0]


if __name__ == '__main__':
    import random
    display = NumberDisplay()

    # Display the alphabet in random colors
    if False:
        for c in 'abcdefghijklmnopqrstuvwxyz':
            while True:
                color = random.choice(list(display.colors.keys()))
                if color != 'black':
                    break
            display.display(c, display.colors[color])
            sleep(.5)
        display.display()


    # Fade a number in and out
    if True:
        color = (1, 0, 0)
        display.display(8, color)
        display.breathing()


    # Display our colors
    if False:
        for color in sorted(HTML_COLORS):
            if color == 'black':
                continue
            display.display('A', HTML_COLORS[color])
            raw_input('This color is %s. Press enter for the next color.' % color)
        display.display('')
        

    # Countdown from 9 to 0 in progressively worrying colors
    if False:
        for i in range(9, -1, -1):
            if i > 6:
                display.display(i, display.colors['green'])
            elif i > 3:
                display.display(i, display.colors['yellow'])
            else:
                display.display(i, display.colors['red'])
            sleep(1)

        sleep(4)
        display.display()


    # Count from 0 to 9 in random colors
    if False:
        for i in range(10):
            while True:
                color = random.choice(list(display.colors.keys()))
                if color != 'black':
                    break
            display.display(i, display.colors[color])
            sleep(1)
        display.display()
