[简体中文 (Chinese)](./README.ZH-CN.md)
# micropython-easymenu
- A simple menu library for Micropython that allows you to construct a menu through simple configuration.
- You can even use it to implement a keyboard!!!

![IMG_20231117_152427](https://github.com/funnygeeker/micropython-easymenu/assets/96659329/2c880f4a-1556-4ba6-b919-eb7874c2ea18)
![IMG_20240103_171254](https://github.com/funnygeeker/micropython-easymenu/assets/96659329/5fd0e46c-50e4-4441-8dc2-64247ca8383a)

### Tested Development Boards
- esp32c3, esp32s3, esp01s

#### Tested Screens
- st7789, st7735, ssd1306

### Software Dependencies

#### Required
- [micropython-easydisplay](https://github.com/funnygeeker/micropython-easydisplay)

#### Optional
- [micropython-easybutton](https://github.com/funnygeeker/micropython-easybutton)

### Usage Examples
For examples and instructions regarding EasyDisplay, please visit: [micropython-easydisplay](https://github.com/funnygeeker/micropython-easydisplay)

```python
from machine import SPI, Pin
from driver import st7735_buf
from lib.easydisplay import EasyDisplay
from lib.easymenu import EasyMenu, MenuItem, BackItem, ValueItem, ToggleItem

spi = SPI(1, baudrate=20000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(17))
dp = st7735_buf.ST7735(width=128, height=128, spi=spi, cs=14, dc=15, res=16, rotate=1, bl=13, invert=False, rgb=False)
ed = EasyDisplay(dp, "RGB565", font="/text_lite_16px_2312.v3.bmf", show=True, color=0xFFFF, clear=True)

status = True


def get_ip():
    return "0.0.0.0"


def get_status():
    global status
    return status


def change_status():
    global status
    status = not status


menu = MenuItem(title=('Menu', 'c', 0), layout=[1, 3], spacing=[128, 16])  # Specify title, layout, and spacing for parent menu

menu1 = MenuItem('Menu-1')  # Set options for Menu-1
menu1.add(ValueItem('Time: ', '123'))
menu1.add(ValueItem(('TEST', 'c', 'c')))
menu1.add(ToggleItem('Select:', get_status, change_status, value_t='[*]', value_f='[ ]'))
menu1.add(BackItem('Back'))

menu.add(menu1)  # Add options to the menu
menu.add(MenuItem('Menu-2'))
menu.add(MenuItem(('Menu-3', 5, 0)))
menu.add(ValueItem('Status:', 'OK'))
menu.add(ValueItem('IP:', (get_ip, 'r', 'c'), skip=True))  # Skip the function for the cursor

em = EasyMenu(ed, menu)
em.show()

# Finally, you can try manually executing:
# em.prev()
# em.next()
# em.click()
# em.next()
# em.next()
# em.click()
# em.back()

# For other example codes, please visit the /example folder
"""
Parameters for parent menu of MenuItem will be inherited by child menus if not explicitly set

1. Parameters for title / value / img: You can pass a tuple, list, string, or function, with the following usage options:
    'Menu' # Ordinary string
    func # A function that returns the content to be displayed when called
    ('Menu', 0, 0)  # 0 for the x-axis offset and y-axis offset, using the top-left corner of the current option as the reference
    ['Menu', 0, 0]
    (func, 0, 0)
    [func, 0, 0]
    (func, 'c', 'c') # 'c' indicates 'center', and the content is centered within the current option area. Note: Only applicable to title / value, img is not supported
    ('Menu', 'c', 'c')

    Supported alignment parameters:
    X-axis: 'l': left, 'r': right, 'c': center
    Y-axis: 't': top, 'b': bottom, 'c': center

2. skip parameter:
    When this parameter is True, the option will not be selected, it will be skipped directly

3. items parameter:
    Pass a list of MenuItem, ValueItem, or ToggleItem instances. If the option has sub-options, it will act as a menu. Additionally, you can use the `add` function of the MenuItem instance to add items to the current menu

4. clear parameter:
    Specify an area to clear the screen: (x_start, y_start, x_end, y_end). When the menu needs to be refreshed, the image in this area will be cleared. 
    Proper use of this parameter allows for displaying multiple menus on one screen.

5. parent parameter:
    Parent menu instance of the option. If needed, you can fill in this parameter manually, or use the `add` function of the parent menu instead

6. start parameter:
    The starting coordinates for displaying the menu (x_start, y_start), generating options from this position

7. style parameter: 
    The default menu style can be changed through the style parameter:
        title-line: A horizontal line under the menu title, default is 1 (enabled), set to 0 to disable
        img-invert: Invert the color of the img image when the option is selected, default is 0 (disabled), set to 1 to enable
        text-invert: Invert the color of the text when the option is selected, default is 1 (enabled), set to 0 to disable
        border: When the option is selected, generate a filled square with a background color that is the reverse of the color of the text or image
        border-pixel: After the border is generated, draw pixels at the corners of the border to give it a more rounded appearance
        name: Default alignment or offset when the name parameter is not set, default value is ['l', 'c']
        title: Default alignment or offset when the title parameter is not set, default value is ['c', 't']
        value: Default alignment or offset when the value parameter is not set, default value is ['r', 'c']
        img: Default alignment or offset when the img parameter is not set, default value is [0, 0]

8. layout parameter:
    Display the menu with the layout of each page (x, y)

9. spacing parameter:
    Distance between the top-left corner of each option

10. callback parameter:
    When the click() function of EasyMenu is called, if the current option is selected, the specified function will be executed

11. data parameter:
    Additional data that can be added and retrieved when needed, currently does not have a specific purpose
"""
```
