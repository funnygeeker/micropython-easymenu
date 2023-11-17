menu = {
     'img': ('/ing/text.dat', 0, 0),
     'func': {'show': None, 'back': None, 'move': None, 'up': None, 'down': None, 'left': None, 'right': None, 'enter': None},
     'text': ('TEXT', 'center', 0),  # 'top', 'bottom'
     'border': {'reversion': 1, 'func': func},  # func(x0, y0, x1, y1) # 外边框起始和结束点
     'select': True,
     'layout': (4, 1),
     'spacing': (100, 20),
    0: {'text': ('TEXT', 0, 0),  # align:left or right, only text support
        'img': ('/ing/text.dat', 0, 0),  # or str
        'select': True}
     }