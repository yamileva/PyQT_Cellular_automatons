import PyQt5.QtWidgets as Widgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon
import json
from modules.CentralWidget import MainWidget
from modules.PropertiesWindow import PropertiesWindow, ChangePropsEvent


class MainWindow(Widgets.QMainWindow):
    def __init__(self, parent=None):
        Widgets.QMainWindow.__init__(self, parent, flags=Qt.Window)
        self.properties = {'dim': 50,
                           'torusBound': True,
                           'symmetryH': False,
                           'symmetryV': False,
                           'animationFreq': 200,
                           'meshLines': True,
                           'colorLive': QColor(255, 150, 0),
                           'colorDead': QColor(240, 240, 240)
                           }
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Клеточные автоматы типа "Жизнь"')
        self.icon = QIcon('files/icon.png')
        self.setWindowIcon(self.icon)
        self.setMinimumWidth(700)
        self.resize(810, 550)
        self.centralWidget = MainWidget(self)
        self.setCentralWidget(self.centralWidget)
        menuBar = Widgets.QMenuBar(self)
        self.setMenuBar(menuBar)
        menuBar.setVisible(True)
        menuFile = menuBar.addMenu("&Файл")
        action = menuFile.addAction("&Новый", self.centralWidget.clear, Qt.CTRL + Qt.Key_N)
        action.setStatusTip("Очистка поля")

        menuFile = menuBar.addMenu("&Дополнительно")
        action = menuFile.addAction("&Настройки", self.loadPropWindow, Qt.CTRL + Qt.Key_P)
        action.setStatusTip("Настройки поля")
        menuFile.addSeparator()
        action = menuFile.addAction("&Справка", self.loadHelpWindow, Qt.CTRL + Qt.Key_H)
        action.setStatusTip("Справка")

    def loadPropWindow(self):
        self.propWindow = PropertiesWindow(self)
        self.propWindow.show()

    def loadHelpWindow(self):
        text = "Программа выполняет анимацию работы клеточных автоматов типа \"Жизнь\"." + \
               " Подробнее о клеточных автоматах:<br>" + \
               " <a href=\"https://en.wikipedia.org/wiki/Life-like_cellular_automaton\">" + \
               "https://en.wikipedia.org/wiki/Life-like_cellular_automaton</a><br><br>" + \
               "Правила перехода клеточного автомата могут быть заданы вручную или выбраны из имеющихся.<br><br>" + \
               "Начальная конфигурация может быть задана вручную или случайно с заданной вероятностью.<br><br>" + \
               "Возможна загрузка конфигураций из базы данных на поле в заданную ячейку" + \
               " и сохранение конфигурации, изображенной на поле, в базу данных. <br><br>" + \
               "В настройках можно задать параметры поля."
        Widgets.QMessageBox.about(self, "Справка", text)

    def customEvent(self, event):
        if event.type() == ChangePropsEvent.idType:
            if event.get_data():
                self.centralWidget.fieldWidget.updateProperties()

    def closeEvent(self, event):
        result = Widgets.QMessageBox.question(self, "Подтверждение закрытия окна",
                                              "Вы действительно хотите закрыть окно?",
                                              Widgets.QMessageBox.Yes | Widgets.QMessageBox.No,
                                              Widgets.QMessageBox.No)
        if result == Widgets.QMessageBox.Yes:
            event.accept()
            Widgets.QWidget.closeEvent(self, event)
        else:
            event.ignore()
