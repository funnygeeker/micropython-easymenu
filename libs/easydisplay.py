# EasyDisplay_1.1.0 https://github.com/funnygeeker/micropython-easydisplay
# 基于以下项目整合和二次开发：
# https://github.com/AntonVanke/MicroPython-Chinese-Font
# https://github.com/boochow/MicroPython-ST7735/blob/master/tftbmp.py
# 参考资料：
# PBM图像显示：https://www.bilibili.com/video/av798158808
# PBM文件格式：https://www.cnblogs.com/SeekHit/p/7055748.html
# PBM文件转换：https://blog.csdn.net/jd3096/article/details/121319042
# 灰度化、二值化：https://blog.csdn.net/li_wen01/article/details/72867057

import struct
import framebuf


class EasyDisplay:
    """
    基于一些开源项目，对适用于 MicroPython 的一些常用的显示功能进行了整合和封装，采用 Framebuf 缓冲区的驱动才能够使用，
    可通过导入字库支持中文显示，支持 P4/P6 PBM 图片显示在黑白或彩色屏幕，
    已通过测试的驱动：SSD1306，ST7735，已通过测试的开发板：ESP32C3，
    支持 24位彩色 BMP 图片显示在黑白或彩色屏幕

        - Author: funnygeeker
        - License: MIT
    """

    def __init__(self,
                 display,
                 reverse: bool = False,
                 clear: bool = False,
                 show: bool = False,
                 font_file: str = None,
                 font_color: int = 0xFF,
                 font_size: int = 16,
                 font_half_char: bool = True,
                 font_auto_wrap: bool = False,
                 font_alpha_bg: bool = False,
                 img_alpha: int = -1,
                 img_color: int = 0xFFFF,
                 img_format: int = framebuf.MONO_HLSB):
        """
        初始化 EasyUI，默认的设置适用于单色 OLED

        Args:
            display: 显示实例
            reverse: 默认是否反转颜色
            clear: 默认是否清除之前显示的内容
            show: 默认是否立刻显示
            font_file: 字体文件所在位置
            font_color: 默认字体颜色
            font_size: 默认字体大小（像素）
            font_half_char: 默认是否半字节显示 ASCII 字符
            font_auto_wrap: 默认自动换行
            img_alpha: 默认显示图像时不显示的颜色
            img_format: 默认显示图像时使用的模式：framebuf.MONO_HLSB（单色显示），framebuf.RGB565（彩色显示）
        """
        self.display = display
        self.any_reverse = reverse
        self.any_clear = clear
        self.any_show = show
        if font_file:
            self._font = BMFont(font_file)  # 字体显示
        self.font_color = font_color
        self.font_size = font_size
        self.font_half_char = font_half_char
        self.font_auto_wrap = font_auto_wrap
        self.font_alpha_bg = font_alpha_bg
        self.img_alpha = img_alpha
        self.img_color = img_color
        self.img_format = img_format

    @staticmethod
    def rgb(r, g, b):  # 感谢 ChatGPT 对代码的性能优化，性能提升 30%
        c = ((b & 0xF8) << 8) | ((g & 0xFC) << 3) | (r >> 3)
        return (c >> 8) | ((c & 0xFF) << 8)

    def clear(self):
        """
        清屏
        """
        self.display.fill(0)

    def show(self):
        """
        立即显示缓冲区的内容
        """
        self.display.show()

    def text(self, s: str, x: int, y: int, c: int = None, size: int = None, show: bool = None, clear: bool = None,
             reverse: bool = None, half_char: bool = None, auto_wrap: bool = None, alpha_bg: int = None):
        """
        显示字体中的文字（请确保初始化时已加载字体文件）

        Args:
            s: 字符串
            x: 字体左上角 x 轴
            y: 字体左上角 y 轴
            c: 颜色
            size: 字号
            reverse: 是否反转背景
            clear: 是否清除之前显示的内容
            show: 是否立刻显示
            half_char: 是否半字节显示 ASCII 字符
            auto_wrap: 自动换行
            alpha_bg: 背景透明
        """
        if c is None:
            c = self.font_color
        if size is None:
            size = self.font_size
        if reverse is None:
            reverse = self.any_reverse
        if clear is None:
            clear = self.any_clear
        if show is None:
            show = self.any_show
        if half_char is None:
            half_char = self.font_half_char
        if auto_wrap is None:
            auto_wrap = self.font_auto_wrap
        if alpha_bg is None:
            alpha_bg = self.font_alpha_bg

        self._font.text(
            display=self.display,  # 显示对象 必要
            string=s,  # 显示的文字 必要
            x=x,  # x 轴
            y=y,  # y 轴
            color=c,  # 颜色 默认是 1(黑白)
            font_size=size,  # 字号(像素)
            reverse=reverse,  # 逆置(墨水屏会用到)
            clear=clear,  # 显示前清屏
            show=show,  # 是否立即显示
            half_char=half_char,  # 是否半字节显示 ASCII 字符
            auto_wrap=auto_wrap,  # 自动换行
            alpha_bg=alpha_bg  # 背景透明
        )

    def pbm(self, file: str, x, y, show: bool = None, clear: bool = None, color: int = None, alpha: int = None,
            reverse: bool = None, format: int = None):
        """
        显示 pbm 图片

        # 您可以通过使用 python3 的 pillow 库将图片转换为 pbm 格式，比如：
        # convert_type = "1"  # 1 为黑白图像，RGBA 为24位彩色图像
        # from PIL import Image
        # with Image.open("文件名.png", "r") as img:
        #   img2 = img.convert(convert_type)
        #   img2.save("文件名.pbm")

        Args:
            file: pbm 文件所在位置
            x: 显示器上显示图片位置的 x 坐标
            y: 显示器上示图片位置的 y 坐标
            show: 是否立即显示
            clear: 是否清除之前显示的内容
            color: 显示黑白图像或将彩色图像以黑白模式显示时的默认颜色
            alpha: 显示图像时不显示的颜色
            reverse: 是否反转颜色
            format: 显示图像时使用的模式：framebuf.MONO_HLSB（单色显示），framebuf.RGB565（彩色显示）
        """
        if show is None:
            show = self.any_show
        if clear is None:
            clear = self.any_clear
        if color is None:
            color = self.img_color
        if alpha is None:
            alpha = self.img_alpha
        if reverse is None:
            reverse = self.any_reverse
        if format is None:
            format = self.img_format
        if clear:  # 清屏
            self.clear()
        with open(file, "rb") as f:
            file_format = f.readline()  # 读取用于表示文件格式的第一行数据
            _width, _height = [int(value) for value in f.readline().split()]  # 获取第二行数据，即图片的宽度和高度
            if file_format == b"P4\n":  # P4 位图 二进制
                _color = 0  # 当前像素的颜色
                for _y in range(_height):
                    for _x in range(_width):
                        _color = f.read(1)
                        if reverse:  # 颜色反转
                            if _color:  # 反转颜色
                                _color = 0
                            else:
                                _color = color
                        else:
                            if _color:  # 颜色不为零
                                _color = color
                            else:
                                _color = 0
                        if _color != alpha:  # 不显示指定颜色
                            self.display.pixel(_x + x, _y + y, _color)

            elif file_format == b"P6\n":  # P6 像素图 二进制
                max_pixel_value = f.readline()  # 读取第三行：最大像素值
                _color = 0  # 当前像素的颜色
                for _y in range(_height):
                    for _x in range(_width):
                        color_bytearray = f.read(3)
                        r, g, b = color_bytearray[0], color_bytearray[1], color_bytearray[2]
                        if format == framebuf.RGB565:  # 彩色显示
                            if reverse:  # 颜色反转
                                r = 255 - r
                                g = 255 - g
                                b = 255 - b
                            _color = self.rgb(r, g, b)
                        elif format == framebuf.MONO_HLSB:  # 单色显示
                            _color = int((r + g + b) / 3) >= 127
                            if reverse:
                                if _color:
                                    _color = 0
                                else:
                                    _color = color
                            else:
                                if _color:
                                    _color = color
                                else:
                                    _color = 0
                        if _color != alpha:  # 不显示指定颜色
                            self.display.pixel(_x + x, _y + y, _color)
            else:
                raise TypeError("Unsupported File Format Type.")
        if show:  # 立即显示
            self.show()

    def bmp(self, file: str, x, y, show: bool = None, clear: bool = None, color: int = None, alpha: int = None,
            reverse: bool = None, format: int = None):
        """
        显示 bmp 图片

        # 您可以通过使用 windows 的 画图 将图片转换为 `24-bit` 的 `bmp` 格式
        # 也可以使用 `Image2Lcd` 这款软件将图片转换为 `24-bit` 的 `bmp` 格式（水平扫描，包含图像头数据，灰度二十四位）

        Args:
            file: pbm 文件所在位置
            x: 显示器上显示图片位置的 x 坐标
            y: 显示器上示图片位置的 y 坐标
            show: 是否立即显示
            clear: 是否清除之前显示的内容
            color: 显示黑白图像或将彩色图像以黑白模式显示时的默认颜色
            alpha: 显示图像时不显示的颜色
            reverse: 是否反转颜色
            format: 显示图像时使用的模式：framebuf.MONO_HLSB（单色显示），framebuf.RGB565（彩色显示）
                """
        if show is None:
            show = self.any_show
        if clear is None:
            clear = self.any_clear
        if color is None:
            color = self.img_color
        if alpha is None:
            alpha = self.img_alpha
        if reverse is None:
            reverse = self.any_reverse
        if format is None:
            format = self.img_format
        with open(file, 'rb') as f:
            if f.read(2) == b'BM':  # 检查文件头来判断是否为支持的文件类型
                dummy = f.read(8)  # 文件大小占四个字节，文件作者占四个字节，file size(4), creator bytes(4)
                offset = int.from_bytes(f.read(4), 'little')  # 像素存储位置占四个字节
                hdrsize = int.from_bytes(f.read(4), 'little')  # DIB header 占四个字节
                _width = int.from_bytes(f.read(4), 'little')  # 图像宽度
                _height = int.from_bytes(f.read(4), 'little')  # 图像高度
                if int.from_bytes(f.read(2), 'little') == 1:  # 色彩平面数 planes must be 1
                    depth = int.from_bytes(f.read(2), 'little')  # 像素位数
                    # 转换时只支持二十四位彩色，不压缩的图像
                    if depth == 24 and int.from_bytes(f.read(4), 'little') == 0:  # compress method == uncompressed
                        # print("Image size:", _width, "x", _height)
                        rowsize = (_width * 3 + 3) & ~3
                        if _height < 0:
                            _height = -_height
                            flip = False
                        else:
                            flip = True
                        if _width > self.display.width:  # 限制图像显示的最大大小（多余部分将被舍弃）
                            _width = self.display.width
                        if _height > self.display.height:
                            _height = self.display.height
                        _color = 0  # 像素的颜色
                        _color_byte = bytes(3)  # 像素的二进制颜色
                        if clear:  # 清屏
                            self.clear()
                        for _y in range(_height):
                            if flip:
                                pos = offset + (_height - 1 - _y) * rowsize
                            else:
                                pos = offset + _y * rowsize
                            if f.tell() != pos:
                                f.seek(pos)  # 调整指针位置
                            for _x in range(_width):
                                _color_byte = f.read(3)
                                r, g, b = _color_byte[2], _color_byte[1], _color_byte[0]
                                if format == framebuf.RGB565:  # 彩色显示
                                    if reverse:  # 颜色反转
                                        r = 255 - r
                                        g = 255 - g
                                        b = 255 - b
                                    _color = self.display.rgb(r, g, b)
                                elif format == framebuf.MONO_HLSB:  # 单色显示
                                    _color = int((r + g + b) / 3) >= 127
                                    if reverse:
                                        if _color:
                                            _color = 0
                                        else:
                                            _color = color
                                    else:
                                        if _color:
                                            _color = color
                                        else:
                                            _color = 0
                                if _color != alpha:  # 不显示指定颜色
                                    self.display.pixel(_x + x, _y + y, _color)
                        if show:  # 立即显示
                            self.show()
                    else:
                        raise TypeError("Unsupported file type: only 24-bit uncompressed BMP images are supported.")
            else:
                raise TypeError("Unsupported file type: only BMP images are supported.")


class BMFont:
    """
    MicroPython 的字符显示库，用于显示文字
    注：这里对源码进行了大部分修改，源仓库：
    https://github.com/AntonVanke/MicroPython-Chinese-Font

        - Author: AntonVanke, Funnygeeker, ChatGPT（性能优化）
        - License: MIT
    """

    def __init__(self, font_file):
        self.font_file = font_file
        self.font = open(font_file, "rb", buffering=0xff)
        self.bmf_info = self.font.read(16)
        if self.bmf_info[0:2] != b"BM":
            raise TypeError("字体文件格式不正确: " + font_file)
        self.version = self.bmf_info[2]
        if self.version != 3:
            raise TypeError("字体文件版本不正确: " + str(self.version))
        self.map_mode = self.bmf_info[3]  # 映射方式
        self.start_bitmap = struct.unpack(">I", b'\x00' + self.bmf_info[4:7])[0]  # 位图开始字节
        self.font_size = self.bmf_info[7]  # 字体大小
        self.bitmap_size = self.bmf_info[8]  # 点阵所占字节

    @staticmethod
    def _bit_list_to_byte_data(bit_list) -> bytearray:
        """将点阵转换为字节数据"""
        bytearray_data = bytearray()
        for _col in bit_list:
            for i in range(0, len(_col), 8):
                bytearray_data.extend(sum(_col[i:i + 8]).to_bytes(2, 'little'))
        return bytearray_data

    def _to_bit_list(self, byte_data, font_size):
        """将字节数据转换为点阵数据，根据 font_size 进行缩放

        Args:
            byte_data: 字节数据
            font_size: 字号大小"""
        _height = self.font_size
        _width = self.bitmap_size // self.font_size * 8
        new_bitarray = [[0 for j in range(font_size)] for i in range(font_size)]
        font_size_height = font_size / _height
        font_size_width = font_size / _width
        for _col in range(len(new_bitarray)):
            col_font_size_height = int(_col / font_size_height)
            for _row in range(len(new_bitarray[_col])):
                _index = col_font_size_height * _width + int(_row / font_size_width)
                new_bitarray[_col][_row] = byte_data[_index // 8] >> (7 - _index % 8) & 1
        return new_bitarray

    @staticmethod
    def _color_render(bit_list, color):
        """将二值点阵图像转换为 RGB565 彩色字节图像"""
        color_array = bytearray()
        _color = struct.pack("<H", color)
        for col in range(len(bit_list)):
            for row in range(len(bit_list[0])):
                color_array.extend(_color if bit_list[col][row] else b'\x00\x00')
        return color_array

    def _get_index(self, word):
        """获取索引

        Args:
            word: 字符
        """
        word_code = ord(word)
        start = 0x10
        end = self.start_bitmap

        while start <= end:
            mid = ((start + end) // 4) * 2
            self.font.seek(mid, 0)
            target_code = struct.unpack(">H", self.font.read(2))[0]
            if word_code == target_code:
                return (mid - 16) >> 1
            elif word_code < target_code:
                end = mid - 2
            else:
                start = mid + 2
        return -1

    def get_bitmap(self, word) -> bytes:
        """获取点阵图

        Args:
            word: 字符

        Returns:
            字符点阵
        """
        index = self._get_index(word)
        if index == -1:
            return b'\xff\xff\xff\xff\xff\xff\xff\xff\xf0\x0f\xcf\xf3\xcf\xf3\xff\xf3\xff\xcf\xff?\xff?\xff\xff\xff' \
                   b'?\xff?\xff\xff\xff\xff'  # 问号字符
        self.font.seek(self.start_bitmap + index * self.bitmap_size, 0)
        return self.font.read(self.bitmap_size)

    def text(self, display, string, x, y, color=1, *, font_size=None, reverse=False, clear=False, show=False,
             half_char=True, auto_wrap=False, alpha_bg: bool = None):
        """通过显示屏显示文字

        使用此函数显示文字，必须先确认显示对象是否继承与 framebuf.FrameBuffer。
        如果显示对象没有 clear 方法，需要自行调用 fill 清屏

        Args:
            display: 显示实例
            string: 字符串
            x: 字体左上角 x 轴
            y: 字体左上角 y 轴
            color: 颜色
            font_size: 字号
            reverse: 是否反转背景
            clear: 是否清除之前显示的内容
            show: 是否立刻显示
            half_char: 是否半字节显示 ASCII 字符
            auto_wrap: 自动换行
            alpha_bg: 透明颜色
        """
        font_size = font_size or self.font_size
        initial_x = x

        # 清屏
        if clear:
            display.fill(0)

        for char in range(len(string)):
            # 是否自动换行
            if auto_wrap and ((x + font_size // 2 >= display.width and ord(string[char]) < 128 and half_char) or
                              (x + font_size >= display.width and (not half_char or ord(string[char]) > 128))):
                y += font_size
                x = initial_x

            # 回车
            if string[char] == '\n':
                y += font_size
                x = initial_x
                continue
            # Tab
            elif string[char] == '\t':
                x = ((x // font_size) + 1) * font_size + initial_x % font_size
                continue
            # 其它的控制字符不显示
            elif ord(string[char]) < 16:
                continue

            # 超范围字符不显示
            if x > display.width or y > display.height:
                continue

            bytearray_data = bytearray(self.get_bitmap(string[char]))
            # 反转
            if reverse:
                for _pixel in range(len(bytearray_data)):
                    bytearray_data[_pixel] = ~bytearray_data[_pixel] & 0xff

            # 透明背景
            if alpha_bg:
                if reverse:
                    alpha_color = color
                else:
                    alpha_color = 0
            else:
                alpha_color = -1

            # 缩放和色彩
            if color != 1 or font_size != self.font_size:
                bit_data = self._to_bit_list(bytearray_data, font_size)
                if color != 1:
                    display.blit(
                        framebuf.FrameBuffer(self._color_render(bit_data, color), font_size, font_size,
                                             framebuf.RGB565), x, y, alpha_color)
                else:
                    display.blit(
                        framebuf.FrameBuffer(self._bit_list_to_byte_data(bit_data), font_size, font_size,
                                             framebuf.MONO_HLSB), x, y, alpha_color)
            else:
                display.blit(framebuf.FrameBuffer(bytearray_data, font_size, font_size, framebuf.MONO_HLSB), x, y,
                             alpha_color)

            # 英文字符半格显示
            if half_char and ord(string[char]) < 128:
                x += font_size // 2
            else:
                x += font_size

        if show:
            display.show()
