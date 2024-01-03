# Github: https://github.com/funnygeeker/micropython-easymenu
# Author: funnygeeker
# Licence: MIT
# Date: 2023/1/3

def _call(func, *args) -> str:
    """
    调用函数并传递参数

    Args:
        func: 函数或函数元组
        *args: 传递给函数的参数

    Returns:
        如果 func 是可调用对象，则返回 func(*args) 的字符串结果
        如果 func 是元组且第一个元素为可调用对象，则返回 func[0](*(func[1] + args)) 的字符串结果
        否则返回 func 的字符串形式
    """
    if callable(func):
        result = func(*args)
    elif type(func) is tuple and callable(func[0]):
        in_args = func[1] if type(func[1]) is tuple or type(func[1]) is list else (func[1],)
        result = func[0](*tuple(list(in_args) + list(args)))
    else:
        result = func
    return '' if result is None else str(result)


class EasyMenu:
    def __init__(self, ed, menu):
        """
        初始化 EasyMenu 实例

        Args:
            ed: micropython-easydisplay 实例
            menu: 菜单，生成方式详见使用文档
        """
        self.ed = ed
        self.menu = menu
        self._update_conf()

    def _update_conf(self):
        """
        更新当前子菜单数据
        """
        menu = self.menu
        if menu.parent:  # 继承上级设置
            # 清屏区域
            menu.clear = menu.clear if menu.clear else menu.parent.clear
            # 起始点
            menu.start = menu.start if menu.start else menu.parent.start
            # 样式
            menu.style = menu.style if menu.style else menu.parent.style
            # 布局
            menu.layout = menu.layout if menu.layout else menu.parent.layout
            # 间距
            menu.spacing = menu.spacing if menu.spacing else menu.parent.spacing
        # 页面长度和布局
        self._menu_len = len(menu.items)
        _page_len = menu.layout[0] * menu.layout[1]
        self._page_len = _page_len if _page_len <= self._menu_len else self._menu_len  # 实际页面长度应少于当前菜单长度
        # 起始点
        if menu.start is None:
            if menu.title[0]:
                menu.start = [0, self.ed.size + 3]
            else:
                menu.start = [0, 0]
        # 默认样式
        style = {'title-line': 1, 'img-invert': 0, 'text-invert': 1, 'border': 1, 'border-pixel': 1,
                 'name': ['l', 'c'], 'title': ['c', 't'], 'value': ['r', 'c'], 'img': [0, 0]}
        style.update(menu.style if menu.style is not None else {})
        menu.style = style

    def reset(self):
        """
        重置索引为 0
        """
        self.menu.page_index = 0
        self.menu.option_index = 0
        self.show()

    def move(self, num):
        """
        移动索引

        Args:
            num: 移动的次数（正整数或负整数）
        """
        if num >= 0:
            func = self.next
        else:
            func = self.prev
        if num != 0:
            num = abs(num)
            for _ in range(num - 1):
                func(False, False)
            func()

    def prev_line(self):
        """移到 上一行"""
        self.move(-self.menu.layout[0])

    def next_line(self):
        """移到 下一行"""
        self.move(self.menu.layout[0])

    def prev(self, show=True, check=True):
        """
        移到 上一项

        Args:
            show: 立即显示更改
            check: 启用检查-该项是否可被选中
        """
        i = True
        while i:
            self.menu.option_index -= 1
            if self.menu.option_index < 0:  # 向前翻页
                self.prev_page(show=False, check=False)
            i = self.get_option().skip if check else False
        if show:
            self.show()

    def next(self, show=True, check=True):
        """
        移动索引到 下一项

        Args:
            show: 立即显示更改
            check: 启用检查-该项是否可被选中
        """
        i = True
        menu = self.menu
        while i:
            last_page_len = self._menu_len % self._page_len
            if not last_page_len:
                last_page_len = self._page_len
            menu.option_index += 1
            if (menu.option_index >= self._page_len or
                    (menu.page_index + self._page_len > self._menu_len and
                     menu.option_index > last_page_len - 1)):  # 选项超出页面索引 或者 当前为最后一页，且超出当前页索引
                self.next_page(show=False, check=False)
            i = self.get_option().skip if check else False
        if show:
            self.show()

    def prev_page(self, show=True, check=True):
        """
       移到 上一页

        Args:
            show: 立即显示更改
            check: 启用检查-该项是否可被选中
        """
        menu = self.menu
        menu.page_index -= self._page_len  # 减小索引值
        if menu.page_index < 0:  # 索引是否超出（小于）菜单有效索引
            last_page_len = self._menu_len % self._page_len  # 计算最后一页的长度
            if not last_page_len:  # 菜单只有一页，且刚好等于最大页面长度的情况
                last_page_len = self._page_len
            page_index = self._menu_len - last_page_len + 1
            menu.page_index = page_index - 1 if page_index else 0
            menu.option_index = last_page_len - 1  # 索引指向当前页最后一项
        else:
            menu.option_index = self._page_len - 1
        if check and self.get_option().skip:
            self.prev(show, check)
        else:
            if show:
                self.show()

    def next_page(self, show=True, check=True):
        """
        移到 下一页

        Args:
            show: 立即显示更改
            check: 启用检查-该项是否可被选中
        """
        menu = self.menu
        menu.option_index = 0
        menu.page_index += self._page_len  # 增加索引值
        if menu.page_index > self._menu_len - 1:  # 索引是否超出（大于）菜单有效索引
            menu.page_index = 0
        if check and self.get_option().skip:
            self.next(show, check)
        else:
            if show:
                self.show()

    def _text_len(self, text: str, size: int = None) -> int:
        """
        计算文本所占 x 坐标的像素数量

        Args:
            text: 文本
            size: 字体大小
        """
        _len = 0
        if size is None:
            size = self.ed.size
        for _ in text:  # 在 16 像素的情况下，ASCII字符宽度为 8，而中文宽度为 16
            if len(_.encode()) == 1:
                _len += 1
            else:
                _len += 2
        return int(size / 2 * _len)

    def _center_x(self, text: str, size: int = None, start=None, end=None) -> int:
        """
        将字符串居中后的 x 起始坐标

        Args:
            text: 文本
            size: 字体大小
            start: 起始 x 坐标（默认为 0）
            end: 结束 x 坐标（默认为 屏幕宽度）
        """
        if start is None:
            start = 0
        if end is None:
            end = self.ed.display.width - 1
        return int((end - start - self._text_len(text, size)) / 2 + start)  # (128 - 1 - length * (16 / 2)) / 2

    def _center_y(self, size: int = None, start=None, end=None) -> int:
        """
        将字符串居中后的 y 起始坐标
        Args:
            size: 字体大小
            start: 起始 y 坐标（默认为 0）
            end: 结束 y 坐标（默认为 屏幕高度）
        """
        if start is None:
            start = 0
        if end is None:
            end = self.ed.display.height - 1
        if size is None:
            size = self.ed.size
        return int((end - start - size) / 2 + start)

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
        elif fmt == 'ppm':
            self.ed.ppm(file, x, y, clear=False, show=False, invert=invert)
        elif fmt == 'dat':
            self.ed.dat(file, x, y, clear=False, show=False)
        else:
            raise ValueError(
                '[ERROR] EasyMenu: Unsupported image format! "Check if the file extension is supported: pbm, bmp, dat')

    def text(self, text: str, x=None, y=None, color: int = None, bg_color: int = None, size: int = None,
             invert: bool = False, start: list = None, spacing: tuple = None):
        """
        显示文本

        Args:
           text: 文本
           x: 文本在屏幕中的起始 x 坐标，除 int 外，还可为 'center', 'left', 'right'
           y: 文本在屏幕中的起始 y 坐标，除 int 外，还可为 'center', 'top', 'bottom'
           color: 文本颜色
           bg_color: 文本背景颜色
           size: 文本大小
           invert: 反色显示
           start: 显示选项时，文本起始坐标，用于计算对齐方式（可选）
           spacing: 显示选项时，文本的 X Y间距，用于计算对齐方式（可选）
        """
        if start is None:
            start = (0, 0)
        if isinstance(x, str):  # 对齐方式识别
            end = self.ed.display.width if spacing is None else start[0] + spacing[0]
            if x == 'c':
                x = self._center_x(text, size, start=start[0], end=end)
            elif x == 'r':
                max_end = int(self.ed.display.width - self.ed.size / 2)
                if end > max_end:  # 限制最大结束位，防止 ASCII 字符溢出
                    end = max_end
                x = end - self._text_len(text, size)
            elif x == 'l':
                x = start[0]
            else:
                raise TypeError("Unsupported X alignment: {}".format(x))

        if isinstance(y, str):
            end = self.ed.display.height if spacing is None else start[1] + spacing[1]
            if y == 'c':
                y = self._center_y(size, start=start[1], end=end)
            elif y == 't':
                y = start[1]
            elif y == 'b':
                if size is None:
                    size = self.ed.size
                y = end - size
            else:
                raise TypeError("Unsupported Y alignment: {}".format(y))

        if color is None:
            color = self.ed.color
        if bg_color is None:
            bg_color = self.ed.bg_color
        self.ed.text(text, x, y, color=color, bg_color=bg_color, size=size, invert=invert, auto_wrap=True, clear=False,
                     show=False, key=color if invert else bg_color)

    def clear(self):
        """
        清理屏幕
        """
        menu = self.menu
        self.ed.display.fill_rect(menu.clear[0], menu.clear[1], menu.clear[2] - menu.clear[0] + 1,
                                  menu.clear[3] - menu.clear[1] + 1, 0)

    def back(self, show: bool = True):
        """
        返回上级菜单

        Args:
            show: 是否刷新屏幕
        """
        if self.menu.parent:
            self.menu = self.menu.parent
            self._update_conf()
            if self.get_option().skip:  # 避免索引为 0 的选项设为不选则时被选中
                self.next(show=False)
            if show:
                self.show()

    def click(self, show: bool = True):
        """
        点击，执行当前项的回调函数，进入下级菜单，若无下级菜单则返回当前选项

        Args:
            show: 是否刷新屏幕
        Returns:
            (None) 菜单
            (Object) 当前选项对象
        """
        item = self.get_option()
        _call(item.callback)  # 执行当前项的回调函数，可以在回调函数中用于生成子菜单
        if len(item.items) > 0:  # 存在选项（menu 不为空）则存在菜单
            self.menu = item
            self.menu.page_index = 0
            self.menu.option_index = 0
            self._update_conf()
            if self.get_option().skip:  # 避免索引为 0 的选项设为不选则时被选中
                self.next(show=False)
            if show:
                self.show()
            return None
        elif (type(item) == ValueItem or type(item) == ToggleItem) and show:  # 刷新页面数据
            self.show()
            return item
        elif type(item) == BackItem:
            self.back(show)
        else:
            return item

    def show(self):
        """
        将对菜单的更改输出到屏幕
        """
        menu = self.menu
        dp = self.ed.display
        ms = menu.style
        # 清理屏幕
        if menu.clear:
            mc = menu.clear
            dp.fill_rect(mc[0], mc[1], mc[2] - mc[0] + 1,
                         mc[3] - mc[1] + 1, 0)
        else:
            dp.fill(0)
        # 显示菜单元素
        # 标题
        title = _call(menu.title[0])
        if title:
            menu_x = ms['title'][0] if menu.title[1] is None else menu.title[1]
            menu_y = ms['title'][1] if menu.title[2] is None else menu.title[2]
            self.text(title, menu_x, menu_y)
            # 标题下的横线
            if ms.get('title-line'):
                dp.hline(0, self.ed.size + 1, dp.width, self.ed.color)
        # 显示选项内容
        layout_x = 0
        layout_y = 0
        for index, option in enumerate(self.get_page()):  # 逐个显示选项
            # 元素在布局中的坐标
            if layout_x > menu.layout[0] - 1:
                layout_y += 1
                layout_x = 0
            # 元素的起始坐标
            start_x = menu.start[0] + menu.spacing[0] * layout_x
            start_y = menu.start[1] + menu.spacing[1] * layout_y
            invert = False  # 文本颜色反转

            # 名称
            name = _call(option.name[0])
            n_offset_x = ms['name'][0] if option.name[1] is None else option.name[1]
            n_offset_y = ms['name'][1] if option.name[2] is None else option.name[2]
            # name 是否使用了 Align 对齐
            name_start = [0, 0]
            if isinstance(n_offset_x, int):
                name_x = start_x + n_offset_x
            else:
                name_x = n_offset_x
                name_start[0] = start_x
            if isinstance(n_offset_y, int):
                name_y = start_y + n_offset_y
            else:
                name_y = n_offset_y
                name_start[1] = start_y

            # 数值
            value = _call(option.value[0])
            v_offset_x = ms['value'][0] if option.value[1] is None else option.value[1]
            v_offset_y = ms['value'][1] if option.value[2] is None else option.value[2]
            # value 是否使用了 Align 对齐
            value_start = [0, 0]
            if isinstance(v_offset_x, int):
                value_x = start_x + v_offset_x
            else:
                value_x = v_offset_x
                value_start[0] = start_x
            if isinstance(v_offset_y, int):
                value_y = start_y + v_offset_y
            else:
                value_y = v_offset_y
                value_start[1] = start_y

            if index == menu.option_index and ms.get('text-invert'):  # 被选中的选项文字反色
                invert = True
                # 显示选中的外边框
                if ms.get('border'):
                    dp.fill_rect(start_x, start_y, menu.spacing[0], menu.spacing[1], self.ed.color)
                self.text(name, name_x, name_y, invert=invert, start=name_start,
                          spacing=menu.spacing)  # 为正常显示英文结尾的背景像素点，必须放在像素点绘制前显示文字
                self.text(value, value_x, value_y, invert=invert, start=value_start, spacing=menu.spacing)
                if ms.get('border-pixel'):
                    for _x in [start_x, start_x + menu.spacing[0] - 1]:
                        for _y in [start_y, start_y + menu.spacing[1] - 1]:
                            dp.pixel(_x, _y, self.ed.bg_color)
            else:
                self.text(name, name_x, name_y, invert=invert, start=name_start, spacing=menu.spacing)
                self.text(value, value_x, value_y, invert=invert, start=value_start, spacing=menu.spacing)

            # 显示选项图片
            img = _call(option.img[0])
            if img:
                invert = False
                if ms.get('img-invert') and index == menu.option_index:  # 启用图片反色且选项被选中
                    invert = True
                i_offset_x = option.img[1] if option.img[1] is not None else ms['img'][0]
                i_offset_y = option.img[2] if option.img[2] is not None else ms['img'][1]
                self.img(img, start_x + i_offset_x, start_y + i_offset_y, invert=invert)

            layout_x += 1
        try:
            dp.show()
        except AttributeError:
            pass
        return True

    def get_index(self) -> list:
        """
        获取当前选项的绝对索引
        """
        return self.menu.page_index + self.menu.option_index

    def get_menu(self) -> list:
        """
        返回当前菜单
        """
        return self.menu.items

    def get_page(self) -> list:
        """
        返回当前页面
        """
        return self.menu.items[self.menu.page_index: self.menu.page_index + self._page_len]

    def get_option(self):
        """
        获取当前选项
        """
        menu = self.menu
        return menu.items[menu.page_index + menu.option_index]


class MenuItem:
    def __init__(self,
                 name='',
                 title='',
                 img='',
                 value='',
                 skip: bool = False,
                 items: list = None,
                 clear: tuple = None,
                 parent=None,
                 start: list = None,
                 style: dict = None,
                 layout: list = None,
                 spacing: list = None,
                 callback: callable = None,
                 data=None):
        """
        通用菜单项

        Args:
            name: 作为选项时：显示的名称
            title: 作为菜单时：显示的标题
            img: 作为选项时：显示的图片
            value: 作为选项时：显示的值
            skip: 作为选项时：跳过此选项，使其无法被框选
            items: 作为菜单时：保存每个选项的列表
            clear: 作为菜单时：清理屏幕的区域
            parent: 作为菜单时：上级菜单
            start: 作为菜单时：选项显示起始点
            style: 作为菜单时：菜单显示时的样式参数 和 默认的对齐设置
            layout: 作为菜单时：(x, y) 布局
            spacing: 作为菜单时：(x, y) 选项间隔
            callback: 被点击时调用的函数
            data: 附加数据
        """
        if not isinstance(name, tuple) and not isinstance(name, list):
            name = [name, None, None]
        if not isinstance(title, tuple) and not isinstance(title, list):
            title = [title, None, None]
        if not isinstance(img, tuple) and not isinstance(img, list):
            img = [img, None, None]
        if not isinstance(value, tuple) and not isinstance(value, list):
            value = [value, None, None]
        if items is None:
            items = []
        self.name = name
        self.title = title
        self.img = img
        self.skip = skip
        self.value = value
        self.items = items
        self.clear = clear
        self.parent = parent
        self.start = start
        self.style = style
        self.layout = layout
        self.spacing = spacing
        self.page_index = 0
        self.option_index = 0
        self.callback = callback
        self.data = data

    def add(self, item, parent=None):
        """
        添加选项

        Args:
            item: MenuItem, BackItem, ValueItem 或 ToggleItem 实例
            parent: 父菜单实例
        """
        item.parent = parent if parent else self
        self.items.append(item)

    def clear(self):
        """清除所有条目"""
        self.items = []


class BackItem(MenuItem):
    def __init__(self, name='', img='', callback=None):
        """
        返回菜单项

        Args:
            name: 显示的名称
            img: 显示的图片
            callback: 被点击时调用的函数
        """
        super().__init__(name=name, img=img, callback=callback)


class ValueItem(MenuItem):
    def __init__(self, name='', value='', img='', skip: bool = False, callback=None, data=None):
        """
        值显示选项

        Args:
            name: 显示的名称
            value: 显示的值
            img: 显示的图片
            skip: 作为选项时：跳过此选项，使其无法被框选
            callback: 被点击时调用的函数
            data: 附加数据
        """
        super().__init__(name=name, value=value, img=img, skip=skip, callback=callback, data=data)


class ToggleItem(ValueItem):
    def __init__(self, name, status_callback, change_callback=None, value_t='[*]', value_f='[ ]', img_t='', img_f='',
                 skip: bool = False, data=None):
        """
        可以切换状态的菜单项

        Args:
            name: 显示的名称
            status_callback: 获取状态的回调函数
            change_callback: 被点击时执行的回调函数
            value_t: status_callback 返回为 True 时显示的值
            value_f: status_callback 返回为 False 时显示的值
            img_t: status_callback 返回为 True 时显示的图像
            img_f: status_callback 返回为 False 时显示的图像
            skip: 作为选项时：跳过此选项，使其无法被框选
            data: 附加数据
        """
        if not isinstance(value_t, tuple) and not isinstance(value_t, list):
            value_t = [value_t, None, None]
        if not isinstance(value_f, tuple) and not isinstance(value_f, list):
            value_f = [value_f, None, None]
        if not isinstance(img_t, tuple) and not isinstance(img_t, list):
            img_t = [img_t, None, None]
        if not isinstance(img_f, tuple) and not isinstance(img_f, list):
            img_f = [img_f, None, None]
        self.value_t = value_t
        self.value_f = value_f
        self.img_t = img_t
        self.img_f = img_f
        self.status_callback = status_callback
        self.change_callback = change_callback
        super().__init__(name=name, value=self._value, img=self._img, skip=skip, callback=self.change_callback,
                         data=data)

    def _value(self):
        return self.value_t[0] if self._get_status() else self.value_f[0]

    def _img(self):
        return self.img_t[0] if self._get_status() else self.img_f[0]

    def _get_status(self):
        return self.status_callback()
