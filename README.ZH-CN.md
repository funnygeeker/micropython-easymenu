[English (英语)](./README.md)
# micropython-easymenu
- micropython 的简易菜单库，可以通过简单的配置，构造一个菜单
- 甚至你可以用它来实现一个键盘！！！
![IMG_20231117_152427](https://github.com/funnygeeker/micropython-easymenu/assets/96659329/2c880f4a-1556-4ba6-b919-eb7874c2ea18)

### 已测试的开发板
- esp32c3

#### 已测试的屏幕
- st7789

### 软件依赖

#### 必须
- [micropython-easydisplay](https://github.com/funnygeeker/micropython-easydisplay)

#### 可选
- [micropython-easybutton](https://github.com/funnygeeker/micropython-easybutton)

### 使用示例
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
em = EasyMenu(ed, menu)
time.sleep(3)
em.previous()  # 上一个选项
time.sleep(3)
em.next()  # 下一个选项
print(em.select()) # 输出当前选项的内容
```
有关 EasyDisplay 的示例和说明，请前往：[micropython-easydisplay](https://github.com/funnygeeker/micropython-easydisplay)

### 配置说明
- 提示：您可以在标准的菜单规范中增加额外的数据，配合 `enter()` 和 `select()` 函数，读取里面的扩展数据，从而实现一些功能
- `menu` 参数配置详细说明及示例如下：
```python
menu = {'_len': 1,
        # 当前页菜单长度（由程序自动管理，非必要请勿填写）
        'image': ('/img/text.pbm', 0, 0),
        # 菜单页图像：不填则不显示，元组 ('图像文件路径', x, y)，支持 dat, pbm, bmp 图片，这里的元组也可以替换为列表，图片需要包含后缀名，详细的图片说明详见 micropython-easydisplay
        'title': ('Main Menu', 'center', 0),  # 举例： 'Title' , ('Title', 0, 0)
        # 菜单页标题：不填则不显示，有两种填写格式 元组 ('标题', x, y) 或者 字符串 '标题'（默认居中文字，y坐标为 0），这里的元组也可以替换为列表，标题的 x坐标 支持使用 'center', 'left', 'right' 代替， y坐标 支持使用 'center', 'top', 'bottom' 代替
        'start': (0, 0),
        # 选项的起始点：不填则由程序自动计算，从 (x, y) 开始，每间隔 spacing 的长度显示一个选项
        'clear': (0, 0, 239, 239),
        # 清屏的区域：(x_start, y_start, x_end, y_end) 不填则默认全屏，该选项可以用于实现：同屏幕多个菜单同时存在
        'style': {'border': 0, 'title_line': 1, 'img_reversion': 0},
        # 样式：不填则使用默认值，请填入字典：
        #   border: 外边框的样式，目前版本中，0 为不启用外边框（被选中的选项会反色），1 为启用外边框（被选中的选项会反色）
        #   title_line: 在标题下方增加一条线，0 为不启用，1 为启用
        #   img_reversion: 图像显示时会被反色，仅适用于 bmp 和 pbm 图像
        'layout': (4, 1),
        # 布局：不填则自动计算，但是建议填写，(x, y)，每页 x * y 个选项
        'offset': (0, 0),
        # 偏移：不填默认 (0, 0)，为选项中所有未指定偏移的图像和文字增加偏移
        'spacing': (100, 20),
        # 间隔：不填则自动计算，但是建议填写，每个选项的起始点间隔 (x, y) 坐标显示
        0: {'text': ('option-1', 0, 0),
            # 不填则不显示，有两种填写格式 元组 ('文本', x, y) 或者 字符串 '文本'（默认偏移为(0, 0)），这里的元组也可以替换为列表，text 的偏移暂时只能用数字表示
            'img': ('/img/text.dat', 0, 0),
            # 选项图像：不填则不显示，元组 ('图像文件路径', x, y) 或者 字符串 '图像文件路径'（默认偏移为(0, 0)）支持 dat, pbm, bmp 图片，这里的元组也可以替换为列表，图片需要包含后缀名，详细的图片说明详见 micropython-easydisplay
            'select': True,
            # 是否可被选中：不填默认 False，当 select 为 True 时，该选项或菜单会被显示，但是光标会自动跳过该选项，无法被选中
            },
        # 这是一个普通选项的示例，【只需要选项中包含数字 0 的键，该选项就会被识别为菜单，使用 enter() 函数时，会进入下一级菜单】
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
        # 这是一个包含菜单选项的示例
        }
```

- 典型示例如下：
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
