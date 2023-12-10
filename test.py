import spidev
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont
from sh1122 import SH1122
import time

WIDTH = 256  # OLED display width
HEIGHT = 64  # OLED display height

# SPI and GPIO setup
spi = spidev.SpiDev()
spi.open(0, 0)  # SPI bus 0, device 0 (can adjust as needed)
spi.max_speed_hz = 100000  # Adjust as needed

GPIO.setmode(GPIO.BCM)
dc = 26    # Data/Command
res = 6   # Reset
cs = 18    # Chip Select

GPIO.setup(dc, GPIO.OUT)
GPIO.setup(res, GPIO.OUT)
GPIO.setup(cs, GPIO.OUT)

# Initialize the display
oled = SH1122(WIDTH, HEIGHT, spi, dc, res, cs)

# Create an image for the Raspberry Pi logo
logo = Image.new('1', (32, 40))
# Here, you need to draw the Raspberry Pi logo onto 'logo'
# The provided byte array can be used to draw the logo

# Create a drawing object
draw = ImageDraw.Draw(logo)
# Draw the logo (replace with actual logo drawing code)

# Create a blank image for drawing
# This will be used for text and blitting the logo
image = Image.new('1', (WIDTH, HEIGHT))
draw = ImageDraw.Draw(image)

# Clear the display
oled.clear()

# Draw the logo on the display
image.paste(logo, (112, 0))

# Add some text
font = ImageFont.load_default()
draw.text((5, 5), "Raspberry Pi", font=font, fill=255)
draw.text((5, 15), "Pico", font=font, fill=255)

if HEIGHT > 32:
    draw.text((5, 25), "This display", font=font, fill=255)
    draw.text((5, 35), "has more than", font=font, fill=255)
    draw.text((5, 45), " 32 lines", font=font, fill=255)

if WIDTH > 128:
    draw.text((149, 25), "This display", font=font, fill=255)
    draw.text((149, 35), "has more than", font=font, fill=255)
    draw.text((149, 45), " 128 pixels", font=font, fill=255)

# Transfer the image to the OLED buffer and display it
oled.display(image)

# Add a loop to keep the display on
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    # Clean up
    spi.close()
    GPIO.cleanup()
