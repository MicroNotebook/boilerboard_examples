import machine
import utime
import uhashlib
from micropython import const
from ssd1306 import SSD1306_I2C

class PCF8574:
    def __init__(self, i2c, address):
        self._i2c = i2c
        self._address = address
        self._input = 0 
        self._input_mask = 0xFF
        self._output = 0 
        self._write()

    def _read(self):
        self._input = self._i2c.readfrom(self._address, 1)[0] & self._input_mask

    def _write(self):
        self._i2c.writeto(self._address, bytes([self._output | self._input_mask]))

    def read(self, pin):
        bit_mask = 1 << pin
        self._input_mask |= bit_mask
        self._output &= ~bit_mask
        self._write()
        self._read()
        return (self._input & bit_mask) >> pin

    def read8(self):
        self._input_mask = 0xFF
        self._output = 0
        self._write()
        self._read()
        return self._input

    def write(self, pin, value):
        bit_mask = 1 << pin
        self._input_mask &= ~bit_mask
        self._output = self._output | bit_mask if value else self._output & (~bit_mask)
        self._write()

    def write8(self, value):
        self._input_mask = 0
        self._output = value
        self._write()

    def set(self):
        self.write8(0xFF)

    def clear(self):
        self.write8(0x0)

    def toggle(self, pin):
        bit_mask = 1 << pin
        self._input_mask &= ~bit_mask
        self._output ^= bit_mask
        self._write()

class Buttons:
    UP = const(0)
    RIGHT = const(1)
    DOWN = const(2)
    LEFT = const(3)
    START = const(4)
    B = const(5)
    A = const(6)

    def __init__(self, i2c):
        self.pcf = PCF8574(i2c, 32)
        self.set_led_state(0)

    def read_pressed_button(self):
        b = self.pcf.read8()
        self.set_led_state(0)
        if not (b & 0b1000000):
            return UP
        if not (b & 0b0100000):
            return RIGHT
        if not (b & 0b0010000):
            return DOWN
        if not (b & 0b0001000):
            return LEFT
        if not(b & 0b0000100):
            return START
        if not(b & 0b0000010):
            return B
        if not(b & 0b0000001):
            return A

    def get_led_state(self):
        return self.pcf.read(7)

    def set_led_state(self, val):
        self.pcf.write(7, val)

    def toggle_led_state(self):
        self.set_led_state(0 if self.get_led_state() else 1)

class IRQ:
    def __init__(self, i2c):
        self.b = Buttons(i2c)
        self.buttonBuffer = []
        self.prevButton = None
        self.debounceDelay = 50
        self.lastDebounceTime = 0
        self.p5 = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
        self.p5.irq(trigger=machine.Pin.IRQ_FALLING, handler=self.button_callback)

    def button_callback(self, p):
        pressedButton = self.b.read_pressed_button()

        if pressedButton is None:
            return

        debounce = False
        if (utime.ticks_ms() - self.lastDebounceTime) <= self.debounceDelay:
            debounce = True

        self.lastDebounceTime = utime.ticks_ms()

        if debounce:
            return

        self.buttonBuffer.append(pressedButton)

    def get_pressed_button(self):
        """
        Returns a button press.
        Note: Can be None
        """
        pressedButton = None

        irq_state = machine.disable_irq()
        if len(self.buttonBuffer) > 0:
            pressedButton = self.buttonBuffer.pop()
        machine.enable_irq(irq_state)

        return pressedButton

    def clear_buffer(self):
        self.buttonBuffer.clear()

class Screen:
    def __init__(self,  i2c):
        self.lcd = SSD1306_I2C(128, 64, i2c)

    def hline(self, xs, xd, y, color):
        """
        Draws a horizontal line on the screen from xs to xd at y 
        For color, 1 is filled, 0 is not
        """
        for i in range(xs, xd+1):
            self.lcd.pixel(i, y, color)

    def vline(self, x, ys, yd, color):
        """
        Draws a verticle line on the screen from ys to yd at x
        For color, 1 is filled, 0 is not
        """
        for i in range(ys, yd+1):
           self. lcd.pixel(x, i, color)

    def rect(self, xs, ys, xd, yd, option):
        """
        Draws a (filled) rectangle on the screen from xs to xd and from ys to yd
        For color, 1 is filled, 0 is not
        """
        for i in range(ys, yd+1):
            for j in range(xs, xd+1):
                self.lcd.pixel(j, i, option)

    def box(self, xs, ys, xd, yd, color):
        """
        Draws a box on the screen from xs to xd and from ys to yd
        For color, 1 is filled, 0 is not
        """
        self.hline(xs, xd, ys, color)
        self.hline(xs, xd, yd, color)
        self.vline(xs, ys, yd, color)
        self.vline(xd, ys, yd, color)

    def clear(self, color):
        """
        Clears the entire screen to color (1 for filled, 0 for not)
        """
        self.lcd.fill(color)

class Boilerboard:

    def __init__(self):
        """
        Initialize interface to boilerboard
        """
        self.i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4))
        self.irq = IRQ(self.i2c)
        self.screen = Screen(self.i2c)


