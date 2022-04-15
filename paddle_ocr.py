from paddleocr import PaddleOCR
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys


class ScreenShotWindow(QMainWindow):
    def __init__(self):
        super(ScreenShotWindow, self).__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet('background-color:black;')
        self.setWindowOpacity(0.6)
        desktopRect = QDesktopWidget().screenGeometry()
        self.setGeometry(desktopRect)
        self.setCursor(Qt.CrossCursor)
        self.blackMask = QBitmap(desktopRect.size())
        self.blackMask.fill(Qt.black)
        self.mask = self.blackMask.copy()
        self.isDrawing = False
        self.startPoint = QPoint()
        self.endPoint = QPoint()

    def paintEvent(self, event):
        if self.isDrawing:
            self.mask = self.blackMask.copy()
            pp = QPainter(self.mask)
            pen = QPen()
            pen.setStyle(Qt.NoPen)
            pp.setPen(pen)
            brush = QBrush(Qt.white)
            pp.setBrush(brush)
            pp.drawRect(QRect(self.startPoint, self.endPoint))
            self.setMask(QBitmap(self.mask))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.startPoint = event.pos()
            self.endPoint = self.startPoint
            self.isDrawing = True

    def mouseMoveEvent(self, event):
        if self.isDrawing:
            self.endPoint = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.endPoint = event.pos()
            screenshot = QApplication.primaryScreen().grabWindow(QApplication.desktop().winId())
            rect = QRect(self.startPoint, self.endPoint)
            outputRegion = screenshot.copy(rect)
            outputRegion.save('ScreenShot.jpg', format='JPG', quality=100)
            self.close()
            self.__init__()
            ocr()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.layout = QVBoxLayout()
        self.textEdit = QPlainTextEdit()
        self.layout.addWidget(self.textEdit)
        self.button = QPushButton('ScreenShot')
        self.layout.addWidget(self.button)
        self.button.clicked.connect(onClick)
        self.font = QFont()
        self.font.setPointSize(10)
        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.widget.setFont(self.font)
        self.setCentralWidget(self.widget)


def ocr():
    window.showNormal()
    paddle = PaddleOCR(use_angle_cls=True, lang='ch')
    result = paddle.ocr('ScreenShot.jpg', cls=True)
    window.textEdit.setPlainText('')
    txts = [line[1][0] for line in result]
    for txt in txts:
        window.textEdit.appendPlainText(txt)


def onClick():
    window.showMinimized()
    ssWindow.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle('JACK')
    window.resize(500, 400)
    ssWindow = ScreenShotWindow()
    window.show()
    app.exec_()
