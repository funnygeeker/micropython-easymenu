import time
import framebuf
from machine import SPI, Pin
from drivers import st7789_spi
from libs.easydisplay import EasyDisplay
from libs.easymenu import EasyMenu

# ESP32C3 & ST7789
spi = SPI(1, baudrate=20000000, polarity=0, phase=0, sck=Pin(19), mosi=Pin(18))
dp = st7789_spi.ST7789(width=240, height=240, spi=spi, cs=0, dc=1, rst=11, rotation=1)
ed = EasyDisplay(display=dp, font="/font/text_lite_16px_2311.v3.bmf", show=True, color=0xFFFF, clear=True,
                 color_type=framebuf.RGB565)
menu = {
    'offset': (16, 16),
    'title': ('Test Menu', 'center', 0),
    'start': (0, 22),
    'layout': (2, 2),
    'spacing': (60, 20),
    0: {'text': 'TEXT0'},
    1: {'text': 'TEXT1',
        0: {'text': ('TEXT1-0', 0, 0)},
        1: {'text': ('TEXT1-1', 0, 0)}
        },
    2: {'text': ('TEXT2', 0, 0)},
    3: {'text': ('TEXT3', 0, 0)},
    4: {'text': ('TEXT4', 0, 0)},
    5: {'text': ('TEXT5', 0, 0)}
}
em = EasyMenu(ed, menu)
time.sleep(3)
em.prev()  # Previous option
time.sleep(3)
em.next()  # Next option
print(em.select())  # Outputs the content of the current option
