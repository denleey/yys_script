# !/usr/bin/dev python
# -*- coding:utf-8 -*-

import sys
from PyQt5.QtWidgets import QApplication
from mainwin import YysWin

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = YysWin()
    main_win.show()
    sys.exit(app.exec_())
