import PyQt5.QtWidgets as Widgets
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt
import numpy as np


class Field(Widgets.QWidget):
    def __init__(self, parent=None, mainWindow=None):
        Widgets.QWidget.__init__(self, parent)
        self.mainWindow = mainWindow
        self.updateProperties()
        # создание доски внутри
        #self.board = np.zeros((self.dim, self.dim), dtype=np.uint8)
        self.birth = []
        self.save = []
        self.needSave = True
        self.clickPaste = False
        self.update()
        self.setFocus()
        # glider
        self.board[2, 1] = 1
        self.board[3, 2] = 1
        self.board[1:4, 3] = 1
        self.pastedPattern = None

    def updateProperties(self):
        self.dim = self.mainWindow.properties['dim']
        self.is_torus = self.mainWindow.properties['torusBound']
        self.symH = self.mainWindow.properties['symmetryH']
        self.symV = self.mainWindow.properties['symmetryV']
        self.timerPeriod = self.mainWindow.properties['animationFreq']
        self.colorLive = self.mainWindow.properties['colorLive']
        self.colorDead = self.mainWindow.properties['colorDead']
        self.meshLines = self.mainWindow.properties['meshLines']
        self.clear()
        self.update()

    def setDimension(self, dim):
        self.dim = dim
        self.mainWindow.properties['dim'] = dim
        self.clear()
        self.update()

    def setRules(self, birth, save):
        self.birth = [i for i in range(10) if birth[i]]
        self.save = [i for i in range(10) if save[i]]

    def clear(self):
        self.board = np.zeros((self.dim, self.dim), dtype=np.uint8)
        self.update()

    def clearButton(self):
        self.initBoard = self.board.copy()
        self.clear()

    def randomInit(self, prob_limit):
        self.board = (np.random.sample(self.board.shape) < prob_limit).astype(np.uint8)
        if not self.is_torus:
            self.dim -= 1
        if self.symH:
            self.board[:, self.dim - 1:(self.dim - 1) // 2:-1] = self.board[:, 0:self.dim // 2]
        if self.symV:
            self.board[self.dim - 1:(self.dim - 1) // 2:-1, :] = self.board[0:self.dim // 2, :]
        if not self.is_torus:
            self.dim += 1
            self.board[-1, :] = 0
            self.board[:, -1] = 0
        self.update()
        self.needSave = True

    def resetBoard(self):
        self.needSave = False
        self.board = self.initBoard.copy()
        self.update()

    # отрисовка
    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        pen = QPen()
        if self.meshLines:
            pen.setStyle(Qt.SolidLine)
            pen.setColor(QColor(255, 255, 255))
        else:
            pen.setStyle(Qt.NoPen)
        qp.setPen(pen)
        cell_size_h = self.width() // self.dim
        cell_size_v = self.height() // self.dim
        if not self.meshLines:
            qp.setBrush(self.colorDead)
            qp.drawRect(0, 0, self.width(), self.height())
        for row in range(self.dim):
            for col in range(self.dim):
                if self.board[col, row]:
                    qp.setBrush(self.colorLive)
                    qp.drawRect(col * cell_size_h, row * cell_size_v,
                                cell_size_v, cell_size_h)
                else:
                    qp.setBrush(self.colorDead)
                    qp.drawRect(col * cell_size_h, row * cell_size_v,
                                cell_size_v, cell_size_h)
        qp.end()

    def nextMove(self):
        if self.needSave:
            if not self.is_torus:
                self.board[-1, :] = 0
                self.board[:, -1] = 0
            self.initBoard = self.board.copy()
        self.needSave = False

        neighbors = sum([np.roll(np.roll(self.board, -1, 1), 1, 0),
                         np.roll(np.roll(self.board, 1, 1), -1, 0),
                         np.roll(np.roll(self.board, 1, 1), 1, 0),
                         np.roll(np.roll(self.board, -1, 1), -1, 0),
                         np.roll(self.board, 1, 1),
                         np.roll(self.board, -1, 1),
                         np.roll(self.board, 1, 0),
                         np.roll(self.board, -1, 0)])
        self.board = (((self.board == 0) & np.sum(neighbors == val for val in self.birth)) | \
                     ((self.board == 1) & np.sum(neighbors == val for val in self.save))).astype(np.uint8)
        if not self.is_torus:
            self.board[-1, :] = 0
            self.board[:, -1] = 0
        self.update()

    def getCell(self, mousePos):
        cell_size_h = self.width() // self.dim
        cell_size_v = self.height() // self.dim

        col = mousePos.x() // cell_size_h
        row = mousePos.y() // cell_size_v
        if 0 <= row < self.dim and 0 <= col < self.dim:
            return col, row
        return None

    def onClick(self, cellCoords):
        if self.clickPaste:
            self.board = np.roll(np.roll(self.board, -cellCoords[1], 1),
                                 -cellCoords[0], 0)
            self.board[0:self.pastedPattern.shape[0],
                       0:self.pastedPattern.shape[1]] = self.pastedPattern
            self.board = np.roll(np.roll(self.board, cellCoords[1], 1),
                                 cellCoords[0], 0)
            self.clickPaste = False
        else:
            self.board[cellCoords] = 1 - self.board[cellCoords]
        self.needSave = True
        self.update()

    def mousePressEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            cell = self.getCell(event.pos())
            if cell:
                self.onClick(cell)
        event.accept()
        return Widgets.QWidget.mousePressEvent(self, event)

    def __str__(self):
        i = 0
        while i < self.dim and self.board[i].any() == 0:
            i += 1
        if i == self.dim:
            return ""
        top = i

        i = self.dim - 1
        while i >= 0 and self.board[i].any() == 0:
            i -= 1
        bottom = i + 1

        i = 0
        tboard = self.board.transpose()
        while tboard[i].any() == 0 and i < self.dim:
            i += 1
        left = i

        i = self.dim - 1
        while tboard[i].any() == 0 and i >= 0:
            i -= 1
        right = i + 1
        return (str(bottom - top) + "_" + str(right - left) + "_P" +
                "".join(["".join([str(elem) for elem in row])
                        for row in self.board[top:bottom, left:right]]))

    def loadPattern(self, patternInfo):
        self.pastedPattern = np.fromiter(map(int, list(patternInfo[2])),
                                         dtype=np.uint8).reshape(patternInfo[0],
                                                                 patternInfo[1])
        self.clickPaste = True
        if max(*patternInfo[:2]) > self.dim - 1:
            Widgets.QMessageBox.information(self, "Вставка",
                                            "Размер конфигурации превышает размер поля. Поле будет изменено и очищено.")
            self.setDimension(max(*patternInfo[:2]) + 1)
