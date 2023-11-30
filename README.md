[简体中文 (Chinese)](./README.ZH-CN.md)
# micropython-easymenu
- A simple menu library for Micropython that allows you to construct a menu through simple configuration.
- Can even be used to implement a keyboard!!!
![IMG_20231117_152427](https://github.com/funnygeeker/micropython-easymenu/assets/96659329/2c880f4a-1556-4ba6-b919-eb7874c2ea18)


### Tested Development Boards
- esp32c3

#### Tested Screens
- st7789

### Software Dependencies

#### Mandatory
- [micropython-easydisplay](https://github.com/funnygeeker/micropython-easydisplay)

#### Optional
- [micropython-easybutton](https://github.com/funnygeeker/micropython-easybutton)

### Usage Example

```python
# This is an example of usage
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
```

For examples and explanations about EasyDisplay, please visit: [micropython-easydisplay](https://github.com/funnygeeker/micropython-easydisplay)

### Configuration Explanation
- Note: You can add extra data in the standard menu specification and use the `enter()` and `select()` functions to read the extended data to achieve certain functionalities.
- The detailed explanation and an example of the `menu` parameter configuration are as follows:
```python
menu = {'_len': 1,
        # Current page menu length (automatically managed by the program, please do not fill in if unnecessary)
        'image': ('/img/text.pbm', 0, 0),
        # Menu page image: If not filled in, it will not be displayed. Tuple ('image file path', x, y) 
        # is supported, either as a tuple or as a list. Images can be dat, pbm, or bmp format. 
        # The tuple can also be replaced with a list. Images need to include the file extension. 
        # For detailed image instructions, please refer to micropython-easydisplay.
        'title': ('Main Menu', 'center', 0),
        # Menu page title: If not filled in, it will not be displayed. There are two formats:
        # Tuple ('title', x, y) or a string 'title' (default centered text, y-coordinate is 0).
        # The tuple can also be replaced with a list. The x-coordinate of the title supports using 
        # 'center', 'left', 'right' instead, and the y-coordinate supports using 'center', 'top', 
        # 'bottom' instead.
        'start': (0, 0),
        # Starting point of options: If not filled in, it will be automatically calculated. Starting
        # from (x, y), each option is displayed at a length equal to the spacing.
        'clear': (0, 0, 239, 239),
        # Clearing the screen area: (x_start, y_start, x_end, y_end) If not filled in, default to full screen. 
        # This option can be used to implement multiple menus on the same screen simultaneously.
        'style': {'border': 0, 'title_line': 1, 'img_invert': 0},
        # Style: If not filled in, default values will be used. Please fill in a dictionary:
        # border: Style of the outer border. In the current version, 0 means no outer border 
        # (the selected option will be highlighted), and 1 means having an outer border 
        # (the selected option will be highlighted).
        # title_line: Add a line below the title, 0 for disable and 1 for enable.
        # img_invert: Images will be displayed with reversed colors. Only applicable to bmp and pbm images.
        'layout': (4, 1),
        # Layout: If not filled in, it will be automatically calculated, but it is recommended to fill in.
        # (x, y), x * y options per page.
        'offset': (0, 0),
        # Offset: Default is (0, 0). Adds an offset to all images and texts in the options that have not 
        # specified an offset.
        'spacing': (100, 20),
        # Spacing: If not filled in, it will be automatically calculated, but it is recommended to fill in. 
        # Coordinates (x, y) for the starting point interval of each option.
        0: {'text': ('option-1', 0, 0),
            # If not filled in, it will not be displayed. There are two formats: 
            # Tuple ('text', x, y) or a string 'text' (default offset is (0, 0)).
            # The tuple can also be replaced with a list. The offset of text can only be expressed as a number.
            'img': ('/img/text.dat', 0, 0),
            # Option image: If not filled in, it will not be displayed. Tuple ('image file path', x, y) 
            # or a string 'image file path' (default offset is (0, 0)) is supported. 
            # Images can be dat, pbm, or bmp format. The tuple can also be replaced with a list. 
            # Images need to include the file extension. For detailed image instructions, please refer 
            # to micropython-easydisplay.
            'select': True,
            # Whether it can be selected: If not filled in, default to False. When select is True, 
            # the option or menu will be displayed, but the cursor will automatically skip this option and 
            # cannot be selected.
            },
        # This is an example of a regular option. If an option contains a key with the number 0, 
        # the option will be recognized as a menu, and when the enter() function is used, 
        # it will enter the next level menu.
        1: {'title': 'Sub Menu',
            'text': 'option-2',
            'img': '/img/text.dat',
            'image': ('/img/text.pbm', 0, 0),
            0: {
                'text': 'option-2-1'
                },
            1: {
                'text': 'option-2-2'
                }
            },
        # This is an example of a menu containing menu options.
        }
```

- A typical example is as follows:
```python
menu = {
    'offset':(16,16),
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
```
