import PyQt5.QtWidgets as Widgets
from PyQt5.QtCore import Qt
from functools import partial
import sqlite3
from modules.FieldWidget import Field
from modules.DBWindow import DBWindow, ReturnPatternEvent


class MainWidget(Widgets.QWidget):
    def __init__(self, parent):
        Widgets.QWidget.__init__(self, parent)
        self.parent = parent
        self.con = sqlite3.connect('files/Life_like_automatons.db')
        self.cur = self.con.cursor()
        request = "SELECT * FROM automatons"
        self.automatons = self.cur.execute(request).fetchall()

        self.run = False
        self.birth = [False] * 10
        self.survival = [False] * 10
        self.checkByHand = True
        self.chooseByHand = True
        self.timer_id = 0
        self.importInfo = {}

        self.initUI()
        self.comboAutomatons.setCurrentIndex(5)

        # self.show()

    def initUI(self):
        desktop = Widgets.QApplication.desktop()
        self.setWindowTitle('Клеточные автоматы')
        # объекты GUI
        # поле для отрисовки
        self.fieldWidget = Field(self, self.parent)
        self.labelAutomatons = Widgets.QLabel("Клеточный автомат:")
        self.labelAutomatons.setFixedHeight(10)
        self.comboAutomatons = Widgets.QComboBox(self)
        self.comboAutomatons.addItem("Задать вручную")
        self.comboAutomatons.addItems([line[1] for line in self.automatons])
        self.comboAutomatons.currentIndexChanged.connect(self.chooseAutomaton)

        self.birthChecks = [Widgets.QCheckBox(str(i), self) for i in range(9)]
        self.survivalChecks = [Widgets.QCheckBox(str(i), self) for i in range(9)]

        self.clearBtn = Widgets.QPushButton("Очистить", self)
        self.clearBtn.clicked.connect(self.clear)
        self.probDigit = Widgets.QDoubleSpinBox(self)
        self.probDigit.setValue(0.3)
        self.probDigit.setRange(0, 1)
        self.probDigit.setSingleStep(0.05)
        self.randBtn = Widgets.QPushButton("Случайно", self)
        self.randBtn.clicked.connect(self.random)
        self.startPauseBtn = Widgets.QPushButton("Пуск", self)
        self.startPauseBtn.clicked.connect(self.startPause)
        self.stopBtn = Widgets.QPushButton("Сбросить", self)
        self.stopBtn.clicked.connect(self.stop)
        self.nextBtn = Widgets.QPushButton("Следующий шаг", self)
        self.nextBtn.clicked.connect(self.next)
        self.openBtn = Widgets.QPushButton("Загрузить", self)
        self.openBtn.clicked.connect(self.loadDBWindow)
        self.saveBtn = Widgets.QPushButton("Сохранить", self)
        self.saveBtn.clicked.connect(self.saveToDB)

        # выравнивание check_box в две колонки
        self.leftVBox = Widgets.QVBoxLayout(self)
        self.leftVBox.setContentsMargins(10, 10, 10, 10)
        self.rightVBox = Widgets.QVBoxLayout(self)
        self.rightVBox.setContentsMargins(10, 10, 10, 10)
        for i in range(9):
            self.leftVBox.addWidget(self.birthChecks[i])
            self.birthChecks[i].toggled.connect(partial(self.checkBirth, i))
            self.rightVBox.addWidget(self.survivalChecks[i])
            self.survivalChecks[i].toggled.connect(partial(self.checkSurvival, i))
        self.leftVBox.addStretch(1)
        self.rightVBox.addStretch(1)
        self.birthBox = Widgets.QGroupBox("Рождение", self)
        self.survivalBox = Widgets.QGroupBox("Выживание", self)
        self.birthBox.setLayout(self.leftVBox)
        self.survivalBox.setLayout(self.rightVBox)

        # выравнивание всех виджетов на сетке
        btnsGrid = Widgets.QGridLayout(self)
        btnsGrid.setContentsMargins(10, 10, 10, 10)
        btnsGrid.setSpacing(20)
        i = 0
        btnsGrid.addWidget(self.openBtn, i, 0)
        btnsGrid.addWidget(self.saveBtn, i, 1)
        i = i + 1
        btnsGrid.addWidget(self.clearBtn, i, 0)
        btnsGrid.addWidget(self.stopBtn, i, 1)
        i = i + 1
        btnsGrid.addWidget(self.probDigit, i, 0)
        btnsGrid.addWidget(self.randBtn, i, 1)
        i = i + 1
        btnsGrid.addWidget(self.startPauseBtn, i, 0)
        btnsGrid.addWidget(self.nextBtn, i, 1)
        i = i + 1
        btnsGrid.addWidget(self.labelAutomatons, i, 0, 1, 2)
        i = i + 1
        btnsGrid.addWidget(self.comboAutomatons, i, 0, 1, 2)
        i = i + 1
        btnsGrid.addWidget(self.birthBox, i, 0)
        btnsGrid.addWidget(self.survivalBox, i, 1)
        i = i + 1
        btnsGrid.addWidget(self.fieldWidget, 0, 2, i, 4)

        self.setLayout(btnsGrid)

    def loadDBWindow(self):
        self.dbWindow = DBWindow(self)
        self.dbWindow.show()

    def customEvent(self, event):
        if event.type() == ReturnPatternEvent.idType:
            self.comboAutomatons.setCurrentIndex(event.get_data()[-1] + 1)
            self.fieldWidget.loadPattern(event.get_data())

    def saveToDB(self):
        string = str(self.fieldWidget)
        if string == '':
            Widgets.QMessageBox.critical(self, "Ошибка сохранения",
                                            "Не обнаружена конфигурация \nдля сохранения\n")
            return
        rows, cols, pattern = string.split("_")
        if self.comboAutomatons.currentIndex():
            saveInfo = [self.comboAutomatons.currentIndex() - 1, int(rows), int(cols), pattern]
        else:
            saveInfo = [4, int(rows), int(cols), pattern]
        self.dbWindow = DBWindow(self, saveInfo)
        self.dbWindow.show()

    def startPause(self):
        self.run = not self.run
        if self.run:
            self.startPauseBtn.setText("Пауза")
            self.timer_id = self.startTimer(self.fieldWidget.timerPeriod, timerType=Qt.CoarseTimer)
            self.fieldWidget.setRules(self.birth, self.survival)
            self.nextBtn.setEnabled(False)
            self.saveBtn.setEnabled(False)
            self.openBtn.setEnabled(False)
            self.randBtn.setEnabled(False)
        else:
            self.startPauseBtn.setText("Пуск")
            self.killTimer(self.timer_id)
            self.timer_id = 0
            self.nextBtn.setEnabled(True)
            self.saveBtn.setEnabled(True)
            self.openBtn.setEnabled(True)
            self.randBtn.setEnabled(True)

    def timerEvent(self, event):
        self.fieldWidget.nextMove()

    def stop(self):
        if self.run:
            self.startPause()
        self.fieldWidget.resetBoard()

    def clear(self):
        if self.run:
            self.startPause()
        self.fieldWidget.clearButton()

    def random(self):
        self.fieldWidget.randomInit(self.probDigit.value())

    def next(self):
        self.fieldWidget.setRules(self.birth, self.survival)
        self.fieldWidget.nextMove()

    def checkBirth(self, i, value):
        self.birth[i] = value
        if self.checkByHand:
            self.chooseByHand = False
            self.comboAutomatons.setCurrentIndex(0)
            self.chooseByHand = True

    def checkSurvival(self, i, value):
        self.survival[i] = value
        if self.checkByHand:
            self.chooseByHand = False
            self.comboAutomatons.setCurrentIndex(0)
            self.chooseByHand = True

    def chooseAutomaton(self, index):
        if index != 0:
            self.checkByHand = False
            for i in range(9):
                self.birthChecks[i].setChecked(str(i) in self.automatons[index - 1][2])
                self.survivalChecks[i].setChecked(str(i) in self.automatons[index - 1][3])
            self.checkByHand = True
        elif self.chooseByHand:
            self.checkByHand = False
            for i in range(9):
                self.birthChecks[i].setChecked(False)
                self.survivalChecks[i].setChecked(False)
            self.checkByHand = True
