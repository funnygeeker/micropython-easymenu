[English (英语)](./README.md)
# micropython-easymenu
- micropython 的简易菜单库，可以通过简单的配置，构造一个菜单
- 甚至你可以用它来实现一个键盘！！！
![IMG_20231117_152427](https://github.com/funnygeeker/micropython-easymenu/assets/96659329/2c880f4a-1556-4ba6-b919-eb7874c2ea18)

### 已测试的开发板
- esp32c3, esp32s3, esp01s

#### 已测试的屏幕
- st7789, st7735, ssd1306

### 软件依赖

#### 必须
- [micropython-easydisplay](https://github.com/funnygeeker/micropython-easydisplay)

#### 可选
- [micropython-easybutton](https://github.com/funnygeeker/micropython-easybutton)

### 使用示例
有关 EasyDisplay 的示例和说明，请前往：[micropython-easydisplay](https://github.com/funnygeeker/micropython-easydisplay)

```python
from machine import SPI, Pin
from driver import st7735_buf
from lib.easydisplay import EasyDisplay
from lib.easymenu import EasyMenu, MenuItem, BackItem, ValueItem, ToggleItem

spi = SPI(1, baudrate=20000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(17))
dp = st7735_buf.ST7735(width=128, height=128, spi=spi, cs=14, dc=15, res=16, rotate=1, bl=13, invert=False, rgb=False)
ed = EasyDisplay(display=dp, font="/text_lite_16px_2312.v3.bmf", show=True, color=0xFFFF, clear=True,
                 color_type="RGB565")

status = True


def get_ip():
    return "0.0.0.0"


def get_status():
    global status
    return status


def change_status():
    global status
    status = not status


menu = MenuItem(title=('Menu', 'c', 0), layout=[1, 3], spacing=[128, 16])  # 为父菜单指定：标题，布局，选项间隔

menu1 = MenuItem('Menu-1')  # 设置 Menu-1 菜单的选项
menu1.add(ValueItem('Time: ', '123'))
menu1.add(ValueItem(('TEST', 'c', 'c')))
menu1.add(ToggleItem('Select:', get_status, change_status, value_t='[*]', value_f='[ ]'))
menu1.add(BackItem('Back'))

menu.add(menu1)  # 将选项添加到菜单
menu.add(MenuItem('Menu-2'))
menu.add(MenuItem(('Menu-3', 5, 0)))
menu.add(ValueItem('Status:', 'OK'))
menu.add(ValueItem('IP:', (get_ip, 'r', 'c'), skip=True))  # 光标不会指向设为跳过的函数

em = EasyMenu(ed, menu)
em.show()

# 最后，可以尝试着手动执行一下：
# em.prev()
# em.next()
# em.click()
# em.next()
# em.next()
# em.click()
# em.back()

# 其他示例代码请访问 /example 文件夹
"""
MenuItem 父菜单设置的参数，子菜单如果不单独设置，则会继承父菜单参数

1. title / value / img 参数：可以传入 tuple, list ,str 或者 函数，主要有以下几种用法：
    'Menu' # 普通的字符串
    func # 一个函数，被调用时的返回值将作为显示的内容
    ('Menu', 0, 0)  # 0 分别为 x轴偏移 和 y轴偏移, 以当前选项的左上角起始位置作为参照
    ['Menu', 0, 0]
    (func, 0, 0)
    [func, 0, 0]
    (func, 'c', 'c') # 'c' 指 'center', 在当前的选项范围居中显示，注意：只有文字: title / value 支持使用, img 暂不支持
    ('Menu', 'c', 'c')
   支持的 align 参数有:
   X轴: 'l': left, 'r': right, 'c': center
   Y轴: 't': top, 'b': bottom, 'c': center

2. skip 参数：
    当该参数为 True 时，该选项不会被框选，而是直接跳过

3. items 参数：
    传入一个包含 MenuItem, ValueItem 或者 ToggleItem 实例的列表，如果该选项下级存在选项，则该选项会作为菜单，另外也可以通过 MenuItem 实例的
    add 函数为当前菜单添加项目

4. clear 参数：
    指定一个屏幕清理区域：(x_start, y_start, x_end, y_end)，当菜单需要更新时，会清理该区域的图像。
    合理地使用这个参数，可以实现在一个屏幕中同时显示多个菜单

5. parent 参数：
    该选项的父级菜单实例，如果需要手动设置，可以填入该参数，也可以利用父级菜单的 add 函数来代替

6. start 参数：
    菜单显示的起点坐标 (x_start, y_start)，从这个位置开始生成选项

7. style 参数，可以通过 style 参数更改默认的菜单样式：
    title-line: 菜单标题下横线，默认为 1，不启用请设置为 0
    img-invert: 当该选项被框选时，反转 img 图像的颜色，默认为 0，启用请设置为 1
    text-invert: 当该选项被框选时，反转 text 文本的颜色，默认为 1，不启用请设置为 0
    border: 当该选项被框选时，为指定区域生成与背景颜色相反的填充正方形作为文字或图片的背景
    border-pixel: border 生成后，在 border 的边角的位置，绘制像素点，使 border 表现的更为圆润
    name: name 参数未设置对齐方式时，默认的对齐方式或者偏移量，默认值为 ['l', 'c']
    title: title 参数未设置对齐方式时，默认的对齐方式或者偏移量，默认值为 ['c', 't']
    value: value 参数未设置对齐方式时，默认的对齐方式或者偏移量，默认值为 ['r', 'c'],
    img: img 参数未设置对齐方式时，默认的对齐方式或者偏移量，默认值为 [0, 0]

8. layout 参数：
    菜单以每个页面 (x, y) 的布局进行显示

9. spacing 参数：
    每个选项左上角起始点之间的 (x, y) 距离间隔

10. callback 参数：
    当 EasyMenu 的 click() 函数被调用的时候，如果当前选项被框选，则会执行的函数

11. data 参数：
    可以加入一些附加数据，需要时获取，暂时并没有特别的作用
"""
```