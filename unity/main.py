from machine import UART
from boilerboard import Boilerboard

uart = UART(0, 115200)
b = Boilerboard()

while True:
    button = b.irq.get_pressed_button()

    if button is not None:
        uart.write(str(button))
