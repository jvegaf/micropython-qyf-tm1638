import tm1638
from machine import Pin
from time import sleep_ms

tm = tm1638.TM1638(stb=Pin(13), clk=Pin(14), dio=Pin(15))

# MS_SLEEP = 1000

# tm.show('olakease')

# for i in range(8):
#     sleep_ms(MS_SLEEP)
#     tm.brightness(i)
#     print(f"brightness: {i}")


while True:
    pressed = tm.keys()
    if pressed > 0:
        print(pressed)
        tm.show(str(pressed))
    sleep_ms(100)
