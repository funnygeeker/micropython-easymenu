# Github: https://github.com/funnygeeker/micropython-easymenu
# Author: funnygeeker
# Licence: MIT
# Date: 2023/11/17

class EasyMenu:
    def __init__(self, ed, menu: dict):
        """
        初始化 EasyMenu 实例

        Args:
            ed: micropython-easydisplay 实例
            menu: 菜单，详见本文件开头的注释
        """
        self.ed = ed
        self.menu = menu
        '所有菜单'
        self.sub_menu = menu
        '当前菜单'
        self.page_index = [0]
        '菜单中页面的索引（相对于当前菜单）'
        self.option_index = [0]
        '页面中选项的索引（相对于当前页面）'
        self.menu_len = None
        '当前页面的菜单长度'
        self.page_len = None
        '当前子菜单的最大页面长度'
        self.refresh_conf()  # 刷新配置文件并初始化默认值

    def home(self):
        """返回首页"""
        self.page_index[-1] = 0
        self.option_index[-1] = 0
        self.show()

    def prev_line(self):
        """移到菜单上一行"""
        for _ in range(self.sub_menu['layout'][0] - 1):
            self.prev(False, False)
        self.prev()

    def next_line(self):
        """移到菜单下一行"""
        for _ in range(self.sub_menu['layout'][0] - 1):
            self.next(False, False)
        self.next()

    def prev(self, show=True, check=True):
        """
        移到上一项

        Args:
            show: 立即显示更改
            check: 启用检查-该项是否可被选中
        """
        i = False
        while not i:
            self.option_index[-1] -= 1
            if self.option_index[-1] < 0:  # 向前翻页
                self.prev_page(show=False, check=False)
            if check:
                i = self.select().get('select', True)
            else:
                i = True
        if show:
            self.show()

    def next(self, show=True, check=True):
        """
        移到下一项

        Args:
            show: 立即显示更改
            check: 启用检查-该项是否可被选中
        """
        i = False
        while not i:
            last_page_len = self.menu_len % self.page_len
            if not last_page_len:
                last_page_len = self.page_len
            self.option_index[-1] += 1
            if (self.option_index[-1] >= self.page_len or
                    (self.page_index[-1] + self.page_len > self.menu_len and
                     self.option_index[-1] > last_page_len - 1)):  # 选项超出页面索引 或者 当前为最后一页，且超出当前页索引
                self.next_page(show=False, check=False)
            if check:
                i = self.select().get('select', True)
            else:
                i = True
        if show:
            self.show()

    def prev_page(self, show=True, check=True):
        """
       移到上一页

        Args:
            show: 立即显示更改
            check: 启用检查-该项是否可被选中
        """
        self.page_index[-1] -= self.page_len  # 减小索引值
        if self.page_index[-1] < 0:  # 索引是否超出（小于）菜单有效索引
            last_page_len = self.menu_len % self.page_len  # 计算最后一页的长度
            if not last_page_len:  # 菜单只有一页，且刚好等于最大页面长度的情况
                last_page_len = self.page_len
            page_index = self.menu_len - last_page_len + 1
            self.page_index[-1] = page_index - 1 if page_index else 0
            self.option_index[-1] = last_page_len - 1  # 索引指向当前页最后一项
        else:
            self.option_index[-1] = self.page_len - 1
        if check and not self.select().get('select', True):
            self.prev(show, check)
        else:
            if show:
                self.show()

    def next_page(self, show=True, check=True):
        """
        移到下一页

        Args:
            show: 立即显示更改
            check: 启用检查-该项是否可被选中
        """
        self.option_index[-1] = 0
        self.page_index[-1] += self.page_len  # 增加索引值
        if self.page_index[-1] > self.menu_len - 1:  # 索引是否超出（大于）菜单有效索引
            self.page_index[-1] = 0
        if check and not self.select().get('select', True):
            self.next(show, check)
        else:
            if show:
                self.show()

    def _text_len(self, text: str, size: int = None) -> int:
        """计算文本所占 x 坐标的像素数量"""
        _len = 0
        if size is None:
            size = self.ed.size
        for _ in text:  # 在 16 像素的情况下，ASCII字符宽度为 8，而中文宽度为 16
            if len(_.encode()) == 1:
                _len += 1
            else:
                _len += 2
        return size / 2 * _len

    def _center_x(self, text: str, size: int = None) -> int:
        """将字符串居中后的 x 起始坐标"""
        return int(
            (self.ed.display.width - 1 - self._text_len(text, size)) / 2)  # (128 - 1 - length * (16 / 2)) / 2

    def _center_y(self, size: int = None) -> int:
        """将字符串居中后的 y 起始坐标"""
        if size is None:
            size = self.ed.size
        return int((self.ed.display.height - 1 - size) / 2)

    def img(self, file: str, x, y, invert=False):
        """
        显示图片

        Args:
            file: 图片所在的路径
            x: 图片在屏幕中的起始 x 坐标
            y: 图片在屏幕中的起始 y 坐标
            invert: 反色显示图片（仅适用于 bmp 和 pbm 图像）
        """
        fmt = file.split('.')[-1]  # 简单的格式判断
        if fmt == 'bmp':
            self.ed.bmp(file, x, y, clear=False, show=False, invert=invert)
        elif fmt == 'pbm':
            self.ed.pbm(file, x, y, clear=False, show=False, invert=invert)
        elif fmt == 'dat':
            self.ed.dat(file, x, y, clear=False, show=False)
        else:
            raise TypeError('Unsupported image format! "Check if the file extension is supported: pbm, bmp, dat')

    def text(self, text: str, x, y, color: int = None, bg_color: int = None, size: int = None, invert: bool = False):
        """
        显示文本

        Args:
           text: 文本
           x: 文本在屏幕中的起始 x 坐标，除 int 外，还可为 'center', 'left', 'right'，只适用于标题显示
           y: 文本在屏幕中的起始 y 坐标，除 int 外，还可为 'center', 'top', 'bottom'，只适用于标题显示
           color: 文本颜色
           bg_color: 文本背景颜色
           size: 文本大小
           invert: 反色显示
        """
        if isinstance(x, str):  # 对齐方式识别
            if x == 'center':
                x = self._center_x(text, size)
            elif x.lower() == 'right':
                x = self.sub_menu['start'][1] - self._text_len(text, size)
            else:
                x = self.sub_menu['start'][0]
        if isinstance(y, str):
            if y == 'center':
                y = self._center_y(size)
            elif y == 'top':
                y = 0
            elif y == 'bottom':
                if size is None:
                    size = self.ed.size
                y = self.sub_menu['start'][4] - size
            else:
                raise TypeError("Unsupported alignment!")
        if color is None:
            color = self.ed.color
        if bg_color is None:
            bg_color = self.ed.bg_color
        self.ed.text(text, x, y, color=color, bg_color=bg_color, size=size, invert=invert, auto_wrap=True, clear=False,
                     show=False, key=color if invert else bg_color)

    def refresh_conf(self):
        """刷新当前菜单配置：继承上级菜单设置，并更新选项数量"""
        menu = self.get_menu()  # 获取当前菜单（在此之前请确保已完成对索引的操作）
        # 将修改写入菜单
        if len(self.page_index) > 1:  # 当前菜单为子菜单
            index = [x + y for x, y in zip(self.page_index[:-1], self.option_index[:-1])]  # 当前选项的绝对索引为两项相对索引之和
            prev_menu = self.get_menu(index).copy()  # 继承上级菜单的选项
            prev_menu_conf = {}
            for k, v in prev_menu.items():  # 过滤出字典中所有非数字开头值
                if not isinstance(k, int):
                    prev_menu_conf[k] = v
            prev_menu_conf.update(menu)  # 合并并继承菜单选项
            self.sub_menu = prev_menu_conf  # 刷新子菜单
            self.refresh_menu(refresh=True)
            self.modify_menu(self.menu, index, self.sub_menu)  # 将子菜单的修改写入父菜单
        else:  # 当前菜单为父菜单
            self_dp = self.ed.display
            # 若参数不存在，则自动补充
            if menu.get('text'):  # 用于设置默认模板
                x = 1
            else:
                x = 0
            menu['start'] = menu.get('start', (0, self.ed.size * x, self_dp.width - 1, self_dp.height - 1))
            menu['clear'] = menu.get('clear', (0, 0, self_dp.width - 1, self_dp.height - 1))
            menu['layout'] = menu.get('layout', (1, (int(self_dp.height / self.ed.size - x))))
            menu['spacing'] = menu.get('spacing', (int(self_dp.width / menu['layout'][0]),
                                                   self.ed.size))
            menu['style'] = menu.get('style', {'border': 1, 'title_line': 1})
            self.sub_menu = menu
            self.refresh_menu(refresh=True)  # 将菜单数量的更改情况写入菜单
            self.menu = self.sub_menu

    def refresh_menu(self, refresh=False):
        """
        更新当前菜单的长度

        Notes:
            在菜单被更改时调用，建议将动态的菜单参数设置为 refresh，该菜单将会被刷新
        """
        menu = self.sub_menu
        if menu.get('_len') is None or refresh:  # 未缓存菜单长度或强制指定刷新时更新菜单长度
            menu = self.sub_menu  # 更新当前菜单排序和数量
            new_menu = {}
            num = 0
            for k, v in menu.items():
                if isinstance(k, int):
                    new_menu[num] = v
                    num += 1
                else:
                    new_menu[k] = v
            new_menu['_len'] = num
            menu = self.sub_menu = new_menu
        self.menu_len = menu['_len']
        page_len = menu['layout'][0] * menu['layout'][1]
        self.page_len = page_len if page_len <= self.menu_len else self.menu_len  # 实际页面长度应少于当前菜单长度
        while menu['_len'] < self.page_index[-1] + self.option_index[-1] + 1:  # 若超出菜单索引范围则尝试修正
            self.prev(show=False)

    def select(self) -> dict:
        """
        选择当前项

        Returns:
            当前项的 dict
        """
        try:
            return self.sub_menu[self.page_index[-1] + self.option_index[-1]]
        except KeyError:  # 自动纠错部分对菜单的外部更改和菜单id的不规范配置
            self.refresh_menu(refresh=True)
            return self.sub_menu[self.page_index[-1] + self.option_index[-1]]

    def back(self):
        """
        返回上级菜单
        """
        if len(self.page_index) > 1:
            del self.page_index[-1]
            del self.option_index[-1]
            self.refresh_conf()
            if not self.select().get('select', True):  # 避免索引为 0 的选项设为不选则时被选中
                self.next(show=False)
            self.show()

    def enter(self, show: bool = True):
        """
        进入下级菜单，若无下级菜单则选择当前项

        Returns:
            None 菜单
            dict 当前项内容
        """
        result = self.select()
        menu = result.get(0)
        if menu:  # 存在选项（键为数字）则存在菜单
            self.page_index.append(0)  # 为菜单创建索引
            self.option_index.append(0)
            self.refresh_conf()  # 刷新当前菜单的配置文件
            if not self.select().get('select', True):  # 避免索引为 0 的选项设为不选则时被选中
                self.next(show=False)
            if show:
                self.show()
            return None
        else:
            return result

    def show(self):
        """
        将对菜单的更改输出到屏幕
        """
        menu = self.sub_menu
        dp = self.ed.display
        # 清理屏幕
        dp.fill_rect(menu['clear'][0], menu['clear'][1], menu['clear'][2] - menu['clear'][0] + 1,
                     menu['clear'][3] - menu['clear'][1] + 1, 0)
        # 显示菜单元素
        if menu.get('image'):  # 图片
            self.img(menu['image'][0], menu['image'][1], menu['image'][2])
        if menu.get('title'):  # 标题
            if isinstance(menu['title'], tuple) or isinstance(menu['title'], list):
                self.text(menu['title'][0], menu['title'][1], menu['title'][2])
            else:
                self.text(menu['title'], 'center', 0)
            if menu['style'].get('title_line', 1):
                title_y = menu['title'][2] if isinstance(menu['title'], tuple) or isinstance(menu['title'], list) else 0
                if isinstance(title_y, str):
                    if title_y == 'center':
                        title_y = self._center_y(self.ed.size)
                    elif title_y == 'top':
                        title_y = 0
                    elif title_y == 'bottom':
                        title_y = self.sub_menu['start'][4] - self.ed.size
                    else:
                        raise TypeError("Unsupported alignment!")
                dp.hline(0, title_y + self.ed.size + 2, dp.width, self.ed.color)

        # 显示选项内容
        layout_x = 0
        layout_y = 0
        layout = menu['layout']
        for index, option in enumerate(self.get_page()):  # 逐个显示选项
            if layout_x > layout[0] - 1:  # 当前元素在布局中的坐标
                layout_y += 1
                layout_x = 0
            # 元素的起始坐标
            x = menu['start'][0] + menu['spacing'][0] * layout_x
            y = menu['start'][1] + menu['spacing'][1] * layout_y
            if option.get('text'):  # 存在文本则显示
                if isinstance(option['text'], tuple) or isinstance(option['text'], list):  # 对元素的位置进行偏移补偿
                    text = option['text'][0]
                    offset_x = option['text'][1]
                    offset_y = option['text'][2]
                elif isinstance(option['text'], str):
                    text = option['text']
                    offset_x, offset_y = menu.get('offset') or (0, 0)
                else:
                    raise TypeError("The configuration format of the menu is incorrect!")
                invert = False
                text_x = x + offset_x
                text_y = y + offset_y
                if index == self.option_index[-1]:  # 不启用样式，则默认被选中的选项文字反色
                    invert = True
                    # 显示选中的外边框
                    if menu['style'].get('border', 1):
                        dp.fill_rect(x, y, menu['spacing'][0], menu['spacing'][1], self.ed.color)
                        self.text(text, text_x, text_y, invert=invert)  # 为了正常显示四角的背景像素点，必须放在此位置
                        for _x in [x, x + menu['spacing'][0] - 1]:
                            for _y in [y, y + menu['spacing'][1] - 1]:
                                dp.pixel(_x, _y, self.ed.bg_color)
                    else:
                        self.text(text, text_x, text_y, invert=invert)
                else:
                    self.text(text, text_x, text_y, invert=invert)
            if option.get('img'):  # 存在图片则显示
                invert = False
                if menu['style'].get('img_invert', 0) and index == self.option_index[-1]:  # 启用图片反色且选项被选中
                    invert = True
                if isinstance(option['img'], tuple) or isinstance(option['img'], list):
                    self.img(option['img'][0], x + option['img'][1], y + option['img'][2], invert=invert)
                elif isinstance(option['img'], str):
                    offset_x, offset_y = menu.get('offset') or (0, 0)  # 对元素的位置进行偏移补偿
                    self.img(option['img'], x + offset_x, y + offset_y, invert=invert)
                else:
                    raise TypeError("The configuration format of the menu is incorrect!")
            layout_x += 1
        try:
            dp.show()
        except AttributeError:
            pass

        return True

    def get_menu(self, index: list = None) -> dict:
        """
        返回菜单
        Args:
            index: 默认为当前层菜单，可指定索引获取指定位置菜单
        """
        if not index:
            index = [x + y for x, y in zip(self.page_index, self.option_index)]
        if len(index) <= 1:
            return self.menu.copy()
        else:
            menu = self.menu.copy()
            for _ in index[:-1]:
                menu = menu[_]
            return menu

    def get_page(self, all_page: bool = False) -> list:
        """
        返回页面列表

        Args:
            all_page: 是否返回当前菜单全部选项，否则仅返回当前页面的选项

        Returns:
            page_option
        """
        p = []
        for k, v in self.sub_menu.items():
            if isinstance(k, int):
                p.append(v)
        if all_page:
            return p
        else:
            return p[self.page_index[-1]: self.page_index[-1] + self.page_len]

    def modify_menu(self, menu, keys, value):
        """
        递归修改嵌套菜单

        Args:
            menu (dict): 要修改的嵌套字典。
            keys (list): 表示要修改的值的键列表。
            value: 字典的新值

        Raises:
            KeyError: 如果键不在字典中，将引发 KeyError。
        """
        if len(keys) == 1:
            menu[keys[0]] = value
        else:
            self.modify_menu(menu[keys[0]], keys[1:], value)


class NumSet:
    def __init__(self, ed, title: str = '', num: int = 0, step: int = 1,
                 num_max: int = None, num_min: int = None):
        self.ed = ed
        self.y = int((self.ed.display.height - self.ed.font_size) / 2)
        self.title = title
        self.num = num
        self.max = num_max
        self.min = num_min
        self.step = step
        if num_max is not None and num_min is not None and num_max < num_min:
            raise Exception("The Max parameter must be greater than the Min parameter.")

    def prev(self):
        """
        减小数字（上一项）
        """
        if self.min is None or self.num > self.min:
            self.num -= self.step
        self.show()

    def next(self):
        """
        增加数字（下一项）
        """
        if self.max is None or self.num < self.max:
            self.num += self.step
        self.show()

    def center_text(self, text: str, y):
        """居中显示文本

        Args:
            text: 要显示的文本
            y: 文本所在的 y 坐标
        """
        length = 0
        for _ in text:  # 在 16 像素的情况下，ASCII字符宽度为 8，而中文宽度为 16
            if len(_.encode()) == 1:
                length += 1
            else:
                length += 2
        x = int((self.ed.display.width - length * (self.ed.font_size / 2)) / 2)  # (128 - length * (16 / 2)) / 2
        self.ed.text(text, x, y, clear=False, show=False)

    def show(self):
        """
        将当前的内容显示到屏幕
        """
        self.ed.clear()
        if self.min is not None and self.num < self.min:
            self.num = self.min
        elif self.max is not None and self.num > self.max:
            self.num = self.max
        if self.title:
            self.center_text(self.title, 1)
        if len(str(self.num)) == 1:
            text = "0{}".format(self.num)
        else:
            text = self.num
        self.center_text("- {} +".format(text), self.y)
        self.ed.show()

    def select(self) -> int:
        """
        选择当前项

        Returns:
            当前项的数字
        """
        return self.num


class KeyBoard(EasyMenu):
    def __init__(self, ed, layout: tuple, start: tuple = None, spacing: tuple = None, offset: tuple = None):
        """
        初始化键盘实例

        Args:
            ed: micropython-easydisplay 实例
            layout: 布局：每页的选项数：(x, y)
            start: 起始点：(x, y)
            spacing: 间距：每个选项的 (x, y) 间距
            offset: 偏移量：未单独设置偏移的选项，每个选项的偏移量
        """
        self.ed = ed
        size = ed.size
        _size = int(size * 0.75)
        if not spacing:
            _ = int(size * 2.5)
            spacing = (_, _)
        if not start:
            start = (size, size * 2)
        if not offset:
            offset = (size, _size)
        menu = {0: {'text': (' 123', 0, _size),
                    0: {'text': ('Back', 0, _size)}, 1: {'text': '0'}, 2: {'text': '1'}, 3: {'text': '2'},
                    4: {'text': '3'},
                    5: {'text': '4'},
                    6: {'text': '5'}, 7: {'text': '6'}, 8: {'text': '7'}, 9: {'text': '8'}, 10: {'text': '9'}},
                1: {'text': (' abc', 0, _size),
                    0: {'text': ('Back', 0, _size)}, 1: {'text': 'a'}, 2: {'text': 'b'}, 3: {'text': 'c'},
                    4: {'text': 'd'},
                    5: {'text': 'e'},
                    6: {'text': 'f'}, 7: {'text': 'g'}, 8: {'text': 'h'}, 9: {'text': 'i'}, 10: {'text': 'j'},
                    11: {'text': 'k'}, 12: {'text': 'l'}, 13: {'text': 'm'}, 14: {'text': 'n'}, 15: {'text': 'o'},
                    16: {'text': 'p'}, 17: {'text': 'q'}, 18: {'text': 'r'}, 19: {'text': 's'}, 20: {'text': 't'},
                    21: {'text': 'u'}, 22: {'text': 'v'}, 23: {'text': 'w'}, 24: {'text': 'x'}, 25: {'text': 'y'},
                    26: {'text': 'z'}},
                2: {'text': (' ABC', 0, _size),
                    0: {'text': ('Back', 0, _size)}, 1: {'text': 'A'}, 2: {'text': 'B'}, 3: {'text': 'C'},
                    4: {'text': 'D'},
                    5: {'text': 'E'},
                    6: {'text': 'F'}, 7: {'text': 'G'}, 8: {'text': 'H'}, 9: {'text': 'I'}, 10: {'text': 'J'},
                    11: {'text': 'K'}, 12: {'text': 'L'}, 13: {'text': 'M'}, 14: {'text': 'N'}, 15: {'text': 'O'},
                    16: {'text': 'P'}, 17: {'text': 'Q'}, 18: {'text': 'R'}, 19: {'text': 'S'}, 20: {'text': 'T'},
                    21: {'text': 'U'}, 22: {'text': 'V'}, 23: {'text': 'W'}, 24: {'text': 'X'}, 25: {'text': 'Y'},
                    26: {'text': 'Z'}},
                3: {'text': (' !@#', 0, _size),
                    0: {'text': ('Back', 0, _size)}, 1: {'text': '~'},
                    2: {'text': '`'}, 3: {'text': '!'}, 4: {'text': '@'},
                    5: {'text': '#'},
                    6: {'text': '$'}, 7: {'text': '%'}, 8: {'text': '^'}, 9: {'text': '&'}, 10: {'text': '*'},
                    11: {'text': '('}, 12: {'text': ')'}, 13: {'text': '-'}, 14: {'text': '_'}, 15: {'text': '+'},
                    16: {'text': '='}, 17: {'text': '{'}, 18: {'text': '}'}, 19: {'text': '['}, 20: {'text': ']'},
                    21: {'text': '|'}, 22: {'text': '\\'}, 23: {'text': ':'}, 24: {'text': ';'}, 25: {'text': '"'},
                    26: {'text': "'"}, 27: {'text': '<'}, 28: {'text': ','}, 29: {'text': '>'}, 30: {'text': '.'},
                    31: {'text': '?'}, 32: {'text': '/'}, 33: {'text': ('Space', 0, _size)},
                    34: {'text': (' ', 0, _size), 'select': False}},
                4: {'text': ('Done', 0, _size)},
                5: {'text': (' Esc', 0, _size)}, 6: {'text': (' Del', 0, _size)}, 7: {'text': ('Clear', 0, _size)},
                8: {'text': (' ', 0, _size), 'select': False},
                'title': ['', ed.size, int(ed.size / 2)],
                'start': start,
                'style': {'title_line': 0},
                'offset': offset,
                'layout': layout,
                'spacing': spacing}
        super().__init__(ed, menu)

    def up(self):
        """选项光标向上"""
        self.prev_line()

    def down(self):
        """选项光标向下"""
        self.next_line()

    def left(self):
        """选项光标向左"""
        self.prev()

    def right(self):
        """选项光标向右"""
        self.next()

    def input(self):
        """
        输入当前选中的字符

        Returns:
            str: 已完成输入的内容（Done）
            None: 执行对内容的操作（Back，Del，Clear）
            False: 请求退出键盘
        """
        option = self.enter(show=False)
        if option:
            option = option.copy()
            if option['text'] == 'Back' or option['text'][0] == 'Back':
                self.back()
                return None
            elif option['text'] == ' Esc' or option['text'][0] == ' Esc':
                return False
            elif option['text'] == ' Del' or option['text'][0] == ' Del':
                self.delete()
                return None
            elif option['text'] == 'Done' or option['text'][0] == 'Done':
                return self.menu['title']
            elif option['text'] == 'Space' or option['text'][0] == 'Space':
                option['text'] = ' '
            elif option['text'] == 'Clear' or option['text'][0] == 'Clear':
                self.menu['title'][0] = ''
                self.sub_menu['title'] = self.menu['title']
                self.show()
                return None
            self.menu['title'][0] = self.menu['title'][0] + option['text']
            self.sub_menu['title'] = self.menu['title']
        self.show()

    def delete(self):
        """
        删除最后一个字符
        """
        self.menu['title'][0] = self.menu['title'][0][:-1]
        self.sub_menu['title'] = self.menu['title']
        self.show()
