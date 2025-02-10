import tm1638
from machine import Pin
# from time import sleep_ms
tm = tm1638.TM1638(stb=Pin(13), clk=Pin(14), dio=Pin(15))


# count = 0
# while True:
#     count += 1
#     for i in range(8):
#         tm.send_char(i, count)
# #        for i in range(len(count)):
# #            display.set_digit(8-len(text)+i, int(text[i]), i==dotpos)
#     sleep_ms(100)

# for i in range(8):
#     for j in range(7):
#         m = 128 >> j
#         tm.send_char(i-1, m)
#         sleep_ms(20)
#
# count = 0
# while True:
#     tm.set_text(str(count))
#     count += 100
#     sleep_ms(20)

# tm.set_text('olakease')


# every 2nd LED on
# tm.leds(0b01010101)

# # all LEDs off
# tm.leds(0)
#
# # segments

# MS_SLEEP = 1000
tm.clear()
tm.show('1/32')
while True:
    pressed = tm.qyf_keys()
    if pressed > 0:
        print(pressed)
        tm.show(str(pressed))
    sleep_ms(10)

# tm.show('abcd')


# """ brightness loop """
# for i in range(8):
#     sleep_ms(MS_SLEEP)
#     tm.brightness(i)
#     print(f"brightness: {i}")

# tm.number(-1234567)
# tm.number(1234)
# tm.write(b'\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00')
# tm.write(b'\x80\x00\x80\x00\x80\x00\x80\x00\x80\x00\x80\x00\x80\x00\x80\x00')
# tm.number(5678, 4)
# tm.hex(0xdeadbeef)
#
# # dim both LEDs and segments
# tm.brightness(0)
#
# # all LEDs and segments off
# tm.clear()
#
# # get which buttons are pressed on LED&KEY module
# tm.keys()
#
# # get which buttons are pressed on QYF-TM1638 module
# tm.qyf_keys()
