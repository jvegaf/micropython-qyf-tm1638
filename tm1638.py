"""
MicroPython TM1638 7-segment LED display driver with keyscan
https://github.com/jvegaf/micropython-qyf-tm1638

MIT License
...
"""

from micropython import const
from machine import Pin

TM1638_CMD1 = const(64)  # 0x40 data command
TM1638_CMD2 = const(192) # 0xC0 address command
TM1638_CMD3 = const(128) # 0x80 display control command
TM1638_DSP_ON = const(8) # 0x08 display on
TM1638_READ = const(2)   # 0x02 read key scan data
TM1638_FIXED = const(4)  # 0x04 fixed address mode

class TM1638:
    FONT = {
        '0': 0b00111111, '1': 0b00000110, '2': 0b01011011, '3': 0b01001111,
        '4': 0b01100110, '5': 0b01101101, '6': 0b01111101, '7': 0b00000111,
        '8': 0b01111111, '9': 0b01101111, 'a': 0b01110111, 'b': 0b01111100,
        'c': 0b01011000, 'd': 0b01011110, 'e': 0b01111001, 'f': 0b01110001,
        'g': 0b01011111, 'h': 0b01110100, 'i': 0b00010000, 'j': 0b00001110,
        'l': 0b00111000, 'n': 0b01010100, 'o': 0b01011100, 'p': 0b01110011,
        'r': 0b01010000, 's': 0b01101101, 't': 0b01111000, 'u': 0b00111110,
        'y': 0b01101110, ' ': 0b00000000, '!': 0b10000110, '"': 0b00100010,
        '(': 0b00110000, ')': 0b00000110, ',': 0b00000100, '-': 0b01000000,
        '.': 0b10000000, '/': 0b01010010, '=': 0b01001000, '?': 0b01010011,
        '@': 0b01011111, 'A': 0b01110111, 'B': 0b01111111, 'C': 0b00111001,
        'D': 0b00111111, 'E': 0b01111001, 'F': 0b01110001, 'G': 0b00111101,
        'H': 0b01110110, 'I': 0b00000110, 'J': 0b00011111, 'K': 0b01101001,
        'L': 0b00111000, 'M': 0b01010100, 'N': 0b00110111, 'O': 0b00111111,
        'P': 0b01110011, 'Q': 0b01100111, 'R': 0b00110001, 'S': 0b01101101,
        'T': 0b01111000, 'U': 0b00111110, 'V': 0b00101010, 'W': 0b00011101,
        'X': 0b01110110, 'Y': 0b01101110, 'Z': 0b01011011, '[': 0b00111001,
        ']': 0b00001111, '_': 0b00001000, '`': 0b00100000, 'k': 0b01110101,
        'm': 0b01010101, 'q': 0b01100111, 'v': 0b00101010, 'w': 0b00011101,
        'x': 0b01110110, 'z': 0b01000111, '{': 0b01000110, '|': 0b00000110,
        '}': 0b01110000, '~': 0b00000001,
    }

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
        self._command(TM1638_CMD1)

    def _set_address(self, addr=0):
        self._byte(TM1638_CMD2 | addr)

    def _write_dsp_ctrl(self):
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
        if val is None:
            return self._on == TM1638_DSP_ON
        self._on = TM1638_DSP_ON if val else 0
        self._write_dsp_ctrl()

    def brightness(self, val=None):
        if val is None:
            return self._brightness
        if not 0 <= val <= 7:
            raise ValueError("Brightness out of range")
        self._brightness = val
        self._write_dsp_ctrl()

    def clear(self):
        self._write_data_cmd()
        self.stb(0)
        self._set_address(0)
        for _ in range(16):
            self._byte(0x00)
        self.stb(1)

    def write(self, data, pos=0):
        if not 0 <= pos <= 15:
            raise ValueError("Position out of range")
        self._write_data_cmd()
        self.stb(0)
        self._set_address(pos)
        for b in data:
            self._byte(b)
        self.stb(1)

    def segments(self, segments, pos=0):
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
        keys = 0
        self.stb(0)
        self._byte(TM1638_CMD1 | TM1638_READ)
        for i in range(4):
            i_keys = self._scan_keys()
            for k in range(2):
                for j in range(2):
                    x = (0x04 >> k) << j * 4
                    if i_keys & x == x:
                        keys |= (1 << (j + k * 8 + 2 * i))
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
        for i in range(6):
            self.send_char(i, self._bit_mask(pos, digit, i), dot)

    def _bit_mask(self, pos, digit, bit):
        return ((self.FONT[digit] >> bit) & 1) << pos

    def show(self, text, pos=0):
        dots = 0b00000000
        dpos = text.find('.')
        if dpos != -1:
            real_pos = dpos + (8 - len(text))
            if real_pos < 0:
                print(f"not possible to render: {real_pos}: {dpos}: {text}")
            elif real_pos >= 4:
                dots |= (128 >> (real_pos - 4))
            else:
                dots |= (8 >> real_pos)
            text = text.replace('.', '')

        self.send_char(7, self.rotate_bits(dots))
        text = text[:8]
        text = self.rev(text)
        text += " " * (8 - len(text))

        text = text[4:8] + text[0:4]

        for i in range(7):
            byte = 0b00000000
            for position in range(8):
                c = text[position]
                if c != ' ':
                    byte |= self._bit_mask(position, c, i)
            self.send_char(i, self.rotate_bits(byte))

    def rotate_bits(self, num):
        for _ in range(4):
            num = self.rotr(num, 8)
        return num

    def rotr(self, num, bits):
        num &= (2 ** bits - 1)
        bit = num & 1
        num >>= 1
        if bit:
            num |= (1 << (bits - 1))
        return num

    def rev(self, s):
        r = ""
        for c in s:
            r = c + r
        return r
