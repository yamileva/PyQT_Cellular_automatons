import PyQt5.QtWidgets as Widgets
from PyQt5.QtCore import QEvent, QCoreApplication, Qt


class PropertiesWindow(Widgets.QWidget):
    def __init__(self, parent):
        Widgets.QWidget.__init__(self)
        self.parent = parent
        self.initUI()
        self.spinDimension.setValue(self.parent.properties['dim'])
        self.radioBoundTorus.setChecked(self.parent.properties['torusBound'])
        self.radioBoundDeath.setChecked(not self.parent.properties['torusBound'])
        self.checkSymmetryH.setChecked(self.parent.properties['symmetryH'])
        self.checkSymmetryV.setChecked(self.parent.properties['symmetryV'])
        self.spinAnimRate.setValue(self.parent.properties['animationFreq'])
        self.buttonColorLiveCell.setStyleSheet("background-color: {}".format(
            self.parent.properties['colorLive'].name()))
        self.colorLiveCell = self.parent.properties['colorLive']
        self.buttonColorDeadCell.setStyleSheet("background-color: {}".format(
            self.parent.properties['colorDead'].name()))
        self.colorDeadCell = self.parent.properties['colorDead']
        self.checkMesh.setChecked(self.parent.properties['meshLines'])
        self.setWindowModality(Qt.ApplicationModal)


    def initUI(self):
        self.setWindowTitle("Настройки")
        self.setWindowIcon(self.parent.icon)
        # tab 1 - Поле
        self.labelDimension = Widgets.QLabel("Размерность поля")
        self.spinDimension = Widgets.QSpinBox()
        self.spinDimension.setRange(10, 100)
        self.spinDimension.setSingleStep(5)
        self.labelAnimRate = Widgets.QLabel("Период обновления кадров, мс")
        self.spinAnimRate = Widgets.QSpinBox()
        self.spinAnimRate.setRange(50, 1000)
        self.spinAnimRate.setSingleStep(50)
        self.radioBoundTorus = Widgets.QRadioButton("Зацикленность (тор)")
        self.radioBoundDeath = Widgets.QRadioButton("Мертвая граница")
        self.checkSymmetryH = Widgets.QCheckBox("Симметричность по-горизонтали")
        self.checkSymmetryV = Widgets.QCheckBox("Симметричность по-вертикали")

        radioVBox = Widgets.QVBoxLayout()
        radioVBox.setContentsMargins(10, 10, 10, 10)
        radioVBox.addWidget(self.radioBoundTorus)
        radioVBox.addWidget(self.radioBoundDeath)
        self.radioGroupBox = Widgets.QGroupBox("Тип границ")
        self.radioGroupBox.setLayout(radioVBox)

        checkVBox = Widgets.QVBoxLayout()
        checkVBox.setContentsMargins(10, 10, 10, 10)
        checkVBox.addWidget(self.checkSymmetryH)
        checkVBox.addWidget(self.checkSymmetryV)
        self.checkGroupBox = Widgets.QGroupBox("Симметричность случайного поля")
        self.checkGroupBox.setLayout(checkVBox)

        fieldTabLayot = Widgets.QGridLayout()
        fieldTabLayot.setContentsMargins(10, 10, 10, 10)
        fieldTabLayot.setSpacing(20)
        i = 0
        fieldTabLayot.addWidget(self.labelDimension, i, 0)
        fieldTabLayot.addWidget(self.spinDimension, i, 1)
        i = i + 1
        fieldTabLayot.addWidget(self.radioGroupBox, i, 0, 1, 2)
        i = i + 1
        fieldTabLayot.addWidget(self.checkGroupBox, i, 0, 1, 2)
        i = i + 1
        fieldTabLayot.addWidget(self.labelAnimRate, i, 0)
        fieldTabLayot.addWidget(self.spinAnimRate, i, 1)

        fieldTab = Widgets.QWidget()
        fieldTab.setLayout(fieldTabLayot)

        # tab 2 - Графика
        # tab 1 - Поле
        self.checkMesh = Widgets.QCheckBox("Отображение сетки")
        self.labelColorLiveCell = Widgets.QLabel('Цвет "живой" ячейки')
        self.labelColorDeadCell = Widgets.QLabel('Цвет "мертвой" ячейки')
        self.buttonColorLiveCell = Widgets.QPushButton()
        self.buttonColorLiveCell.clicked.connect(self.clickColorLiveCell)
        self.buttonColorDeadCell = Widgets.QPushButton()
        self.buttonColorDeadCell.clicked.connect(self.clickColorDeadCell)

        designTabLayot = Widgets.QGridLayout()
        designTabLayot.setContentsMargins(10, 10, 10, 10)
        designTabLayot.setSpacing(20)
        i = 0
        designTabLayot.addWidget(self.checkMesh, i, 0, 1, 2)
        i = i + 1
        designTabLayot.addWidget(self.labelColorLiveCell, i, 0)
        designTabLayot.addWidget(self.buttonColorLiveCell, i, 1)
        i = i + 1
        designTabLayot.addWidget(self.labelColorDeadCell, i, 0)
        designTabLayot.addWidget(self.buttonColorDeadCell, i, 1)
        i = i + 1
        designTabLayot.addWidget(Widgets.QWidget(self), i, 0, 1, 2)
        designTabLayot.setRowStretch(i, 1)

        designTab = Widgets.QWidget()
        designTab.setLayout(designTabLayot)

        # Panel
        tabWidget = Widgets.QTabWidget(self)
        tabWidget.addTab(fieldTab, "Поле")
        tabWidget.addTab(designTab, "Графика")

        tabWidget.setCurrentIndex(0)
        totalLayot = Widgets.QGridLayout(self)
        totalLayot.addWidget(tabWidget, 0, 0, 1, 2)
        okButton = Widgets.QPushButton("ОК", self)
        okButton.clicked.connect(self.clickOK)
        cancelButton = Widgets.QPushButton("Отмена", self)
        cancelButton.clicked.connect(self.close)
        totalLayot.addWidget(okButton, 1, 0)
        totalLayot.addWidget(cancelButton, 1, 1)

        self.setLayout(totalLayot)

    def clickOK(self):
        self.parent.properties['dim'] = self.spinDimension.value()
        self.parent.properties['torusBound'] = self.radioBoundTorus.isChecked()
        self.parent.properties['symmetryH'] = self.checkSymmetryH.isChecked()
        self.parent.properties['symmetryV'] = self.checkSymmetryV.isChecked()
        self.parent.properties['animationFreq'] = self.spinAnimRate.value()
        self.parent.properties['colorLive'] = self.colorLiveCell
        self.parent.properties['colorDead'] = self.colorDeadCell
        self.parent.properties['meshLines'] = self.checkMesh.isChecked()
        QCoreApplication.sendEvent(self.parent, ChangePropsEvent(True))
        self.close()

    def clickColorLiveCell(self):
        color = Widgets.QColorDialog.getColor()
        if color.isValid():
            self.buttonColorLiveCell.setStyleSheet("background-color: {}".format(
                color.name()))
            self.colorLiveCell = color

    def clickColorDeadCell(self):
        color = Widgets.QColorDialog.getColor()
        if color.isValid():
            self.buttonColorDeadCell.setStyleSheet("background-color: {}".format(
                color.name()))
            self.colorDeadCell = color


class ChangePropsEvent(QEvent):
    idType = QEvent.registerEventType()
    def __init__(self, allChanged):
        QEvent.__init__(self, ChangePropsEvent.idType)
        self.allChanged = allChanged

    def get_data(self):
        return self.allChanged
