from machine import Pin

# Debug LED on the board itself.
led = Pin("LED", Pin.OUT)


def on():
    led.on()


def off():
    led.off()


def toggle():
    led.toggle()
