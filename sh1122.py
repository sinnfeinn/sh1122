import spidev
import RPi.GPIO as GPIO
import time

# Constants for the SH1122 display
SET_COL_ADR_LSB = 0x00
SET_COL_ADR_MSB = 0x10
SET_DISP_START_LINE = 0x40
SET_CONTRAST = 0x81
SET_SEG_REMAP = 0xA0
SET_ENTIRE_ON = 0xA4
SET_NORM_INV = 0xA6
SET_MUX_RATIO = 0xA8
SET_CTRL_DCDC = 0xAD
SET_DISP = 0xAE
SET_ROW_ADR = 0xB0
SET_COM_OUT_DIR = 0xC0
SET_DISP_OFFSET = 0xD3
SET_DISP_CLK_DIV = 0xD5
SET_PRECHARGE = 0xD9
SET_VCOM_DESEL = 0xDB
SET_VSEG_LEVEL = 0xDC
SET_DISCHARGE_LEVEL = 0x30

class SH1122:
    def __init__(self, width, height, spi, dc, res, cs):
        self.width = width
        self.height = height
        self.spi = spi
        self.dc = dc
        self.res = res
        self.cs = cs
        self.buffer = bytearray(self.width * self.height // 8)
        self.init_display()

    def init_display(self):
        # Hardware reset
        GPIO.output(self.res, GPIO.HIGH)
        time.sleep(0.010)  # 1ms delay
        GPIO.output(self.res, GPIO.LOW)
        time.sleep(0.010)  # 10ms delay
        GPIO.output(self.res, GPIO.HIGH)

        # Initialization sequence for the display
        commands = [
            SET_DISP | 0x00,  # Display off
            SET_COL_ADR_LSB,
            SET_COL_ADR_MSB,
            SET_DISP_START_LINE | 0x00,
            SET_SEG_REMAP,
            SET_MUX_RATIO, self.height - 1,
            SET_COM_OUT_DIR,
            SET_DISP_OFFSET, 0x00,
            SET_CONTRAST, 0x80,  # You might need to adjust this
            SET_ENTIRE_ON,
            SET_NORM_INV,
            SET_DISP | 0x01,  # Display on
        ]
        for cmd in commands:
            self.write_cmd(cmd)

    def write_cmd(self, cmd):
        GPIO.output(self.cs, GPIO.LOW)
        GPIO.output(self.dc, GPIO.LOW)
        self.spi.writebytes([cmd])
        GPIO.output(self.cs, GPIO.HIGH)

    def write_data(self, data):
        GPIO.output(self.cs, GPIO.LOW)
        GPIO.output(self.dc, GPIO.HIGH)
        self.spi.writebytes(data)
        GPIO.output(self.cs, GPIO.HIGH)

    def display(self, image):
        if image.mode != '1':
            raise ValueError("Image must be in mode 1.")

        # Convert image to 1-bit data
        width, height = image.size
        pixels = list(image.getdata())
        buffer = bytearray(width * height // 8)

        for y in range(height):
            for x in range(width):
                if pixels[x + y * width]:
                    page = y // 8
                    buffer[x + width * page] |= (0x80 >> (y % 8))

        self.buffer = buffer
        self.show()

    def show(self):
        self.write_cmd(SET_COL_ADR_LSB)
        self.write_cmd(SET_COL_ADR_MSB)
        for page in range(self.height // 8):
            self.write_cmd(SET_ROW_ADR + page)
            start = page * self.width
            end = start + self.width
            self.write_data(self.buffer[start:end])

    def clear(self):
        self.buffer = bytearray(self.width * self.height // 8)
        self.show()
