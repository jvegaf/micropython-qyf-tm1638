"""
MicroPython TM1638 7-segment LED display driver with keyscan
https://github.com/mcauser/micropython-tm1638

MIT License
Copyright (c) 2018 Mike Causer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# LED&KEY module features:
# 8x 7-segment decimal LED modules
# 8x individual LEDs
# 8x push buttons

# QYF-TM1638 module features:
# 8x 7-segment decimal LED modules
# 16x push buttons

from micropython import const
from machine import Pin
from time import sleep_us, sleep_ms

TM1638_CMD1 = const(64)  # 0x40 data command
TM1638_CMD2 = const(192) # 0xC0 address command
TM1638_CMD3 = const(128) # 0x80 display control command
TM1638_DSP_ON = const(8) # 0x08 display on
TM1638_READ = const(2)   # 0x02 read key scan data
TM1638_FIXED = const(4)  # 0x04 fixed address mode

class TM1638(object):
    FONT = {
        '0': 0b00111111,
        '1': 0b00000110,
        '2': 0b01011011,
        '3': 0b01001111,
        '4': 0b01100110,
        '5': 0b01101101,
        '6': 0b01111101,
        '7': 0b00000111,
        '8': 0b01111111,
        '9': 0b01101111,
        'a': 0b01110111,
        'b': 0b01111100,
        'c': 0b01011000,
        'd': 0b01011110,
        'e': 0b01111001,
        'f': 0b01110001,
        'g': 0b01011111,
        'h': 0b01110100,
        'i': 0b00010000,
        'j': 0b00001110,
        'l': 0b00111000,
        'n': 0b01010100,
        'o': 0b01011100,
        'p': 0b01110011,
        'r': 0b01010000,
        's': 0b01101101,
        't': 0b01111000,
        'u': 0b00111110,
        'y': 0b01101110,

        # added from https://github.com/thilaire/rpi-TM1638/blob/master/rpi_TM1638/Font.py
        ' ': 0b00000000,  # (32) <space>
        '!': 0b10000110,  # (33) !
        '"': 0b00100010,  # (34) "
        '(': 0b00110000,  # (40) (
        ')': 0b00000110,  # (41) )
        ',': 0b00000100,  # (44) ,
        '-': 0b01000000,  # (45) -
        '.': 0b10000000,  # (46) .
        '/': 0b01010010,  # (47) /
        '=': 0b01001000,  # (61) =
        '?': 0b01010011,  # (63) ?
        '@': 0b01011111,  # (64) @
        'A': 0b01110111,  # (65) A
        'B': 0b01111111,  # (66) B
        'C': 0b00111001,  # (67) C
        'D': 0b00111111,  # (68) D
        'E': 0b01111001,  # (69) E
        'F': 0b01110001,  # (70) F
        'G': 0b00111101,  # (71) G
        'H': 0b01110110,  # (72) H
        'I': 0b00000110,  # (73) I
        'J': 0b00011111,  # (74) J
        'K': 0b01101001,  # (75) K
        'L': 0b00111000,  # (76) L
        'M': 0b01010100,  # (77) M (equal to n!)
        #'M': 0b00010101,  # (77) M
        'N': 0b00110111,  # (78) N
        'O': 0b00111111,  # (79) O
        'P': 0b01110011,  # (80) P
        'Q': 0b01100111,  # (81) Q
        'R': 0b00110001,  # (82) R
        'S': 0b01101101,  # (83) S
        'T': 0b01111000,  # (84) T
        'U': 0b00111110,  # (85) U
        'V': 0b00101010,  # (86) V
        'W': 0b00011101,  # (87) W
        'X': 0b01110110,  # (88) X
        'Y': 0b01101110,  # (89) Y
        'Z': 0b01011011,  # (90) Z
        '[': 0b00111001,  # (91) [
        ']': 0b00001111,  # (93) ]
        '_': 0b00001000,  # (95) _
        '`': 0b00100000,  # (96) `
        'k': 0b01110101,  # (107) k
        'm': 0b01010101,  # (109) m
        'q': 0b01100111,  # (113) q
        'v': 0b00101010,  # (118) v
        'w': 0b00011101,  # (119) w
        'x': 0b01110110,  # (120) x
        'z': 0b01000111,  # (122) z
        '{': 0b01000110,  # (123) {
        '|': 0b00000110,  # (124) |
        '}': 0b01110000,  # (125) }
        '~': 0b00000001,  # (126) ~
    }



    """Library for the TM1638 LED display driver."""
    def __init__(self, stb, clk, dio, brightness=7):
        self.stb = stb
        self.clk = clk
        self.dio = dio

        if not 0 <= brightness <= 7:
            raise ValueError("Brightness out of range")
        self._brightness = brightness

        self._on = TM1638_DSP_ON

        self.clk.init(Pin.OUT, value=1)
        self.dio.init(Pin.OUT, value=0)
        self.stb.init(Pin.OUT, value=1)

        self.clear()
        self._write_dsp_ctrl()

    def _write_data_cmd(self):
        # data command: automatic address increment, normal mode
        self._command(TM1638_CMD1)

    def _set_address(self, addr=0):
        # address command: move to address
        self._byte(TM1638_CMD2 | addr)

    def _write_dsp_ctrl(self):
        # display command: display on, set brightness
        self._command(TM1638_CMD3 | self._on | self._brightness)

    def _command(self, cmd):
        self.stb(0)
        self._byte(cmd)
        self.stb(1)

    def _byte(self, b):
        for i in range(8):
            self.clk(0)
            self.dio((b >> i) & 1)
            self.clk(1)

    def _scan_keys(self):
        """Reads one of the four bytes representing which keys are pressed."""
        pressed = 0
        self.dio.init(Pin.IN, Pin.PULL_UP)
        for i in range(8):
            self.clk(0)
            if self.dio.value():
                pressed |= 1 << i
            self.clk(1)
        self.dio.init(Pin.OUT)
        return pressed

    def power(self, val=None):
        """Power up, power down or check status"""
        if val is None:
            return self._on == TM1638_DSP_ON
        self._on = TM1638_DSP_ON if val else 0
        self._write_dsp_ctrl()

    def brightness(self, val=None):
        """Set the display brightness 0-7."""
        # brightness 0 = 1/16th pulse width
        # brightness 7 = 14/16th pulse width
        if val is None:
            return self._brightness
        if not 0 <= val <= 7:
            raise ValueError("Brightness out of range")
        self._brightness = val
        self._write_dsp_ctrl()

    def clear(self):
        """Write zeros to each address"""
        self._write_data_cmd()
        self.stb(0)
        self._set_address(0)
        for i in range(16):
            self._byte(0x00)
        self.stb(1)

    def write(self, data, pos=0):
        """Write to all 16 addresses from a given position.
        Order is left to right, 1st segment, 1st LED, 2nd segment, 2nd LED etc."""
        if not 0 <= pos <= 15:
            raise ValueError("Position out of range")
        self._write_data_cmd()
        self.stb(0)
        self._set_address(pos)
        for b in data:
            self._byte(b)
        self.stb(1)

    def led(self, pos, val):
        """Set the value of a single LED"""
        self.write([val], (pos << 1) + 1)

    def leds(self, val):
        """Set all LEDs at once. LSB is left most LED.
        Only writes to the LED positions (every 2nd starting from 1)"""
        self._write_data_cmd()
        pos = 1
        for i in range(8):
            self.stb(0)
            self._set_address(pos)
            self._byte((val >> i) & 1)
            pos += 2
            self.stb(1)

    def segments(self, segments, pos=0):
        """Set one or more segments at a relative position.
        Only writes to the segment positions (every 2nd starting from 0)"""
        if not 0 <= pos <= 7:
            raise ValueError("Position out of range")
        self._write_data_cmd()
        for seg in segments:
            self.stb(0)
            self._set_address(pos << 1)
            self._byte(seg)
            pos += 1
            self.stb(1)

    def keys(self):
        """Return a 16-bit value representing which keys are pressed. LSB is SW1"""
        keys = 0
        self.stb(0)
        self._byte(TM1638_CMD1 | TM1638_READ)
        for i in range(4):
            i_keys = self._scan_keys()
            for k in range(2):
                for j in range(2):
                    x = (0x04 >> k) << j*4
                    if i_keys & x == x:
                        keys |= (1 << (j + k*8 + 2*i))
        self.stb(1)
        return keys

    def send_data(self, addr, data):
        self._write_data_cmd()
        self.stb(0)
        self._byte(0xC0 | addr)
        self._byte(data)
        self.stb(1)

    def send_char(self, pos, data, dot=False):
        self.send_data(pos << 1, data | (128 if dot else 0))

    def set_digit(self, pos, digit, dot=False):
        for i in range(0, 6):
            self.send_char(i, self._bit_mask(pos, digit, i), dot)

    def _bit_mask(self, pos, digit, bit):
        return ((self.FONT[digit] >> bit) & 1) << pos

    def show(self, text, pos=0):
        """Displays a string"""
        dots = 0b00000000
        dpos = text.find('.')
        if dpos != -1:
            # For my boards, the dot-order is non-linear:
            # 8 4 2 1 128 64 32 16
            realPos = dpos+(8-len(text))
            if realPos < 0:
              print("not possible to render: " + str(realPos) + ": " + str(dpos) + ": " + text)
            elif realPos >= 4:
              dots = dots | (128 >> realPos-4)
            else:
              dots = dots | (8 >> realPos)
            text = text.replace('.', '')

        self.send_char(7, self.rotate_bits(dots))
        text = text[0:8]
        text = self.rev(text)
        text += " "*(8-len(text))

        # my TM1638 board has the two 4-char displays exchanged
        text = text[4:8] + text[0:4]

        for i in range(0, 7):
            byte = 0b00000000
            for position in range(8):
                c = text[position]
                if c != ' ':
                    byte = (byte | self._bit_mask(position, c, i))
            self.send_char(i, self.rotate_bits(byte))

    def rotate_bits(self, num):
        for i in range(0, 4):
            num = self.rotr(num, 8)
        return num

    def rotr(self, num, bits):
        num &= (2**bits-1)
        bit = num & 1
        num >>= 1
        if bit:
            num |= (1 << (bits-1))
        return num

    def rev(self, s):
        r = ""
        for c in s:
            r = c + r
        return r
