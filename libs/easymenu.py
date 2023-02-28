class ImgMenu:
    def __init__(self, ed, menu: list,
                 img_x: int = 0, img_y: int = 0,
                 text_x: int = None, text_y: int = 0):
        """
        图片和文字的菜单，图像格式支持：pbm[P4(1-bit), P6(24-bit)] 和 bmp[24-bit]

        Args:
            ed: `micropython-easydisplay` 实例
            menu: 菜单字典，格式为 [{'name': 'title', 'img': '/img/1.pbm', 'xxx': xxx}, ...]
            img_x: 图像显示的 x 坐标
            img_y: 图像显示的 y 坐标
            text_x: 文本显示的 x 坐标，为 None 时居中显示
            text_y: 文本显示的 y 坐标
        """
        self.ed = ed
        self.menu = menu
        self.index = 0
        self.img_x = img_x
        self.img_y = img_y
        self.text_x = text_x
        self.text_y = text_y

    def show_text(self, text: str):
        """
        显示文本

        Args:
            text: 要显示的文本
        """
        if self.text_x is None:  # 居中显示
            length = 0
            for _ in text:  # 在 16 像素的情况下，ASCII字符宽度为 8，而中文宽度为 16
                if len(_.encode()) == 1:
                    length += 1
                else:
                    length += 2
            x = int((self.ed.display.width - length * (self.ed.font_size / 2)) / 2)  # (128 - length * (16 / 2)) / 2
            self.ed.text(text, x, self.text_y, clear=False, show=False)
        else:
            self.ed.text(text, self.text_x, self.text_y, clear=False, show=False)

    def last(self):
        """
        菜单中的上一项
        """
        self.index -= 1
        if self.index < 0:
            self.index = len(self.menu) - 1  # 越过最前面则加载菜单的最后一项
        self.show()

    def next(self):
        """
        菜单中的下一项
        """
        self.index += 1
        if self.index > len(self.menu) - 1:  # 越过最后面则加载菜单的第一项
            self.index = 0
        self.show()

    def show(self):
        """
        将当前的内容显示到屏幕
        """
        self.ed.clear()
        fmt = self.menu[self.index]['img'].split('.')[-1]
        if fmt == 'bmp':
            self.ed.bmp(self.menu[self.index]['img'], self.img_x, self.img_y, clear=False, show=False)
        elif fmt == 'pbm':
            self.ed.pbm(self.menu[self.index]['img'], self.img_x, self.img_y, clear=False, show=False)
        else:
            raise TypeError('Unsupported picture format!')
        self.show_text(self.menu[self.index]['name'])
        self.ed.show()

    def select(self) -> dict:
        """
        选择当前项

        Returns:
            当前项的 dict
        """
        return self.menu[self.index]


class TextMenu:
    def __init__(self, ed, menu: list,
                 x: int = None, y: int = None,
                 title: str = None):
        """
        Args:
            ed: `micropython-easydisplay` 实例
            menu: [{'name': 'title', 'xxx': xxx}, ...]
            x: 菜单文字的起始 x 坐标（不填写则自动设置）
            y: 标题下面，菜单文字的起始 y 坐标（不填写则自动设置）
            title: 菜单标题（不填写则不显示）
        """
        self.ed = ed
        self.menu = menu
        self.index = 0
        if x is None:
            self.x = ed.font_size
        else:
            self.x = x
        if title and y is None:
            self.y = ed.font_size + 7
        elif y is None:
            self.y = 2
        else:
            self.y = y
        self.title = title
        # 仅用于纯文字模式
        if title:
            self.page_len = int((self.ed.display.height - self.y) / (self.ed.font_size + 4))
        else:
            self.page_len = int((self.ed.display.height - self.y) / (self.ed.font_size + 4))
        if self.page_len > len(self.menu):
            self.page_len = len(self.menu)
        self.page_index = 0

    def _center_text(self, text: str, y) -> None:
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

    def last(self):
        """
        菜单中的上一项
        """
        self.page_index -= 1
        if self.page_index < 0:
            self.index -= 1
            if self.index < 0:  # 越过最前面则加载菜单的最后一页
                self.index = len(self.menu) - self.page_len
                self.page_index = self.page_len - 1
            else:
                self.page_index = 0
        self.show()

    def next(self):
        """
        菜单中的下一项
        """
        self.page_index += 1
        if self.page_index >= self.page_len:
            self.index += 1
            self.page_index -= 1
            if self.index > len(self.menu) - self.page_len:  # 越过最后面则加载菜单的第一页
                self.index = 0
                self.page_index = 0
        self.show()

    def show(self):
        """
        将当前的内容显示到屏幕
        """
        self.ed.clear()
        # 标题
        if self.title:
            self._center_text(self.title, 1)
            self.ed.display.line(0, self.ed.font_size + 4, self.ed.display.width,
                                 self.ed.font_size + 4, self.ed.font_color)
        # 文本
        for _ in range(self.page_len):
            if _ == self.page_index:
                self.ed.text(self.menu[self.index + _]['name'],
                             self.x, _ * (self.ed.font_size + 4) + self.y, clear=False,
                             reverse=not self.ed.any_reverse, show=False)
            else:
                self.ed.text(self.menu[self.index + _]['name'],
                             self.x, _ * (self.ed.font_size + 4) + self.y, clear=False, show=False)
        self.ed.show()

    def select(self) -> dict:
        """
        选择当前项

        Returns:
            当前项的 dict
        """
        return self.menu[self.index + self.page_index]


class NumMenu:
    def __init__(self, ed, title: str = '', num: int = 0, step: int = 1, max: int = None, min: int = None):
        self.ed = ed
        self.y = int((self.ed.display.height - self.ed.font_size) / 2)
        self.title = title
        self.num = num
        self.max = max
        self.min = min
        self.step = step
        if max is not None and min is not None and max < min:
            raise Exception("The Max parameter must be greater than the Min parameter.")

    def last(self):
        """
        菜单中的上一项
        """
        if self.min is None or self.num > self.min:
            self.num -= self.step
        self.show()

    def next(self):
        """
        菜单中的下一项
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
