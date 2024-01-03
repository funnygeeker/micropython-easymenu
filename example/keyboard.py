from lib.easymenu import EasyMenu, MenuItem, BackItem, ValueItem


class KeyBoard(EasyMenu):
    def __init__(self, ed, start=None, layout=None, spacing=(40, 32), esc=None, done=None):
        """
        初始化键盘实例

        Args:
            ed: micropython-easydisplay 实例
            layout: 布局：每页的选项数：(x, y)
            start: 起始点：(x, y)
            spacing: 间距：每个选项的 (x, y) 间距
            esc:
            done:
        """
        if start is None:
            start = [4, 28]
        if layout is None:
            layout = [3, 3]
        self.ed = ed
        self.esc = esc
        self.done = done
        menu = MenuItem('', start=start, layout=layout, spacing=spacing,
                        style={'title-line': 0, 'name': ['c', 'c'], 'title': [0, 4]})
        self.parent_menu = menu
        back_opt = BackItem('Back')

        num_menu = MenuItem(title=self.get_title, name='123')
        num_menu.add(back_opt)

        for s in '1234567890':
            num_menu.add(ValueItem(s, callback=self.input))
        eng_menu = MenuItem(title=self.get_title, name='abc')
        eng_menu.add(back_opt)

        for s in 'abcdefghijklmnopqrstuvwxyz':
            eng_menu.add(ValueItem(s, callback=self.input))
        cap_eng_menu = MenuItem(title=self.get_title, name='ABC')
        cap_eng_menu.add(back_opt)

        for s in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            cap_eng_menu.add(ValueItem(s, callback=self.input))
        symbol_menu = MenuItem(title=self.get_title, name='!@#')
        symbol_menu.add(back_opt)

        for s in '~`!@#$%^&*()-_+={}[]|\\:;"' + "'<>,.?/":
            symbol_menu.add(ValueItem(s, callback=self.input))
        symbol_menu.add(ValueItem('Space', callback=(self.input, ' ')))

        del_opt = ValueItem('Del', callback=self.delete)
        done_opt = ValueItem('Done', callback=self.done)
        esc_opt = ValueItem('Esc', callback=self.esc)
        clear_opt = ValueItem('Clear', callback=self.clear)

        for f in (num_menu, eng_menu, cap_eng_menu, symbol_menu, back_opt, del_opt, done_opt, esc_opt, clear_opt):
            menu.add(f)

        super().__init__(self.ed, menu)

    def get_title(self):
        return self.parent_menu.title[0]

    def clear(self):
        self.parent_menu.title[0] = ''
        # self.show()

    def delete(self):
        """
        删除最后一个字符
        """
        self.parent_menu.title[0] = self.parent_menu.title[0][:-1]
        self.show()

    def input(self, string: str = None):
        """
        输入当前选中的字符

        Returns:
            str: 已完成输入的内容 (Done)
            None: 执行对内容的操作 (Back，Del，Clear)
            False: 请求退出键盘
        """
        if string is None:
            string = self.get_option().name[0]
        self.parent_menu.title[0] += string
        self.show()


if __name__ == "__main__":
    from machine import SPI, Pin
    from driver import st7735_buf
    from lib.easydisplay import EasyDisplay

    spi = SPI(1, baudrate=20000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(17))
    dp = st7735_buf.ST7735(width=128, height=128, spi=spi, cs=14, dc=15, res=16, rotate=1, bl=13,
                           invert=False, rgb=False)
    ed = EasyDisplay(display=dp, font="/text_lite_16px_2312.v3.bmf", show=True, color=0xFFFF, clear=True,
                     color_type="RGB565")


    def d():
        print('Content:', kb.get_title())


    kb = KeyBoard(ed, done=d, esc=(print, "ESC"))
    kb.show()
    # kb.prev()
    # kb.click()
    # kb.back()
