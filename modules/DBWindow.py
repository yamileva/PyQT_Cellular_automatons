import PyQt5.QtWidgets as Widgets
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QEvent, QCoreApplication
import sqlite3


class DBWindow(Widgets.QWidget):
    def __init__(self, parent, saveInfo=None):
        Widgets.QWidget.__init__(self)
        self.saveFlag = saveInfo is not None
        self.saveInfo = saveInfo
        self.tablerow = -1
        self.parent = parent
        self.con = sqlite3.connect('files/Life_like_automatons.db')
        self.cur = self.con.cursor()
        self.initUI()
        self.setWindowModality(Qt.ApplicationModal)

    def initUI(self):
        self.setWindowTitle("База данных")
        self.setWindowIcon(self.parent.parent.icon)

        self.automatons = self.cur.execute("SELECT * FROM automatons").fetchall()
        self.patternTypes = self.cur.execute("SELECT * FROM pattern_types").fetchall()

        self.tableWidget = Widgets.QTableWidget(self)
        self.tableWidget.cellClicked.connect(self.selectTableItem)

        self.comboAutomatons = Widgets.QComboBox(self)
        if not self.saveFlag:
            self.comboAutomatons.addItem("Все")
        self.comboAutomatons.addItems([line[1] for line in self.automatons])
        self.labelAutomatons = Widgets.QLabel(self)
        self.labelAutomatons.setText("Автомат")

        self.comboTypes = Widgets.QComboBox(self)
        if not self.saveFlag:
            self.comboTypes.addItem("Все")
        self.comboTypes.addItems([line[1] for line in self.patternTypes])
        self.comboTypes.setCurrentIndex(0)
        self.labelTypes = Widgets.QLabel(self)
        self.labelTypes.setText("Тип")

        self.lineEdit = Widgets.QLineEdit(self)
        self.lineEdit.setFocus()
        self.labelName = Widgets.QLabel(self)
        self.labelName.setText("Название")
        self.tableButton = Widgets.QPushButton("Просмотр \nбазы", self)
        self.tableButton.clicked.connect(self.loadFromDB)
        self.pushReturnButton = Widgets.QPushButton(self)

        self.preview = PreviewWidget(self)
        self.preview.setFrameStyle(Widgets.QFrame.StyledPanel)
        self.preview.setMinimumWidth(self.width() // 2)

        if self.saveFlag:
            self.pushReturnButton.setText("Сохранить")
            self.pushReturnButton.clicked.connect(self.saveData)
            self.comboAutomatons.setCurrentIndex(self.saveInfo[0])
            self.tableWidget.setVisible(False)
            self.tableButton.setVisible(False)
            self.preview.update()
            self.tablerow = -2
        else:
            self.pushReturnButton.setText("Вставить \nна поле")
            self.pushReturnButton.setEnabled(False)
            self.pushReturnButton.clicked.connect(self.returnToMain)
            self.comboAutomatons.setCurrentIndex(0)

        grid = Widgets.QGridLayout(self)
        grid.setContentsMargins(10, 10, 10, 10)
        grid.setSpacing(20)
        i = 0
        grid.addWidget(self.tableWidget, i, 0, 1, 4)
        i = i + 1
        grid.addWidget(self.labelAutomatons, i, 0)
        grid.addWidget(self.comboAutomatons, i, 1)
        grid.addWidget(self.tableButton, i, 2, 2, 1)
        i = i + 1
        grid.addWidget(self.labelTypes, i, 0)
        grid.addWidget(self.comboTypes, i, 1)
        i = i + 1
        grid.addWidget(self.labelName, i, 0)
        grid.addWidget(self.lineEdit, i, 1)
        grid.addWidget(self.preview, 1, 3, i, 1)
        grid.addWidget(self.pushReturnButton, i, 2)
        if not self.saveFlag:
            i = i + 1
            grid.addWidget(Widgets.QLabel(
                "Место вставки следует указать на поле после нажатия кнопки \"Вставить на поле\""), i, 0, 1, 4)

        self.setLayout(grid)

    def loadFromDB(self):
        self.tableWidget.clear()
        self.data = self.getData()
        if not self.data:
            self.data = [[""] * 7]
            self.data[0][4] = "Данных нет"
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setRowCount(len(self.data))
        self.tableWidget.setHorizontalHeaderItem(0, Widgets.QTableWidgetItem("ID"))
        self.tableWidget.setHorizontalHeaderItem(1, Widgets.QTableWidgetItem("Автомат"))
        self.tableWidget.setHorizontalHeaderItem(2, Widgets.QTableWidgetItem("Строки"))
        self.tableWidget.setHorizontalHeaderItem(3, Widgets.QTableWidgetItem("Столбцы"))
        self.tableWidget.setHorizontalHeaderItem(4, Widgets.QTableWidgetItem("Название"))
        self.tableWidget.setHorizontalHeaderItem(5, Widgets.QTableWidgetItem("Тип"))
        for i, elem in enumerate(self.data):
            for j, val in enumerate(elem[:-1]):
                self.tableWidget.setItem(i, j, Widgets.QTableWidgetItem(str(val)))
        self.tableWidget.resizeColumnsToContents()
        self.tablerow = -1
        self.preview.update()

    def getData(self):
        automaton = self.comboAutomatons.currentIndex()
        type = self.comboTypes.currentIndex()
        name = self.lineEdit.text()
        request = "SELECT * FROM patterns"
        command = []
        if automaton:
            command += ['automaton=' + str(automaton - 1)]
        if type:
            command += ['type=' + str(type - 1)]
        if name:
            command += ['name=' + '"' + str(name) + '"']
        if command:
            request += '\nWHERE ' + ' AND '.join(command)
        return [[row[0]] + [self.automatons[row[1]][1]] + list(row[2:5]) +
                [self.patternTypes[row[6]][1]] + [row[1]] + [row[5]]
                for row in self.cur.execute(request).fetchall()]

    def selectTableItem(self):
        self.tableWidget.clearSelection()
        self.tableWidget.setSelectionMode(Widgets.QAbstractItemView.MultiSelection)
        self.tablerow = self.tableWidget.currentRow()
        self.tableWidget.selectRow(self.tablerow)
        self.pushReturnButton.setEnabled(True)
        self.preview.update()

    def returnToMain(self):
        if self.tablerow != -1:
            pwidth, pheight = self.data[self.tablerow][2:4]
            pattern = self.data[self.tablerow][-1][1:]
            automaton = self.data[self.tablerow][-2]
            patternInfo = [pwidth, pheight, pattern, automaton]
            QCoreApplication.sendEvent(self.parent, ReturnPatternEvent(patternInfo))
        self.close()

    def saveData(self):
        automaton = self.comboAutomatons.currentIndex()
        type = self.comboTypes.currentIndex()
        name = self.lineEdit.text()
        if not name:
            Widgets.QMessageBox.information(self, "Ошибка сохранения", "Нужно ввести название конфигурации")
            return
        request = "INSERT INTO patterns" + \
              "(automaton,rows,columns,name,pattern,type) VALUES(" + \
              "," .join([str(automaton),
                         str(self.saveInfo[1]),
                         str(self.saveInfo[2]),
                         '"' + name + '"',
                         '"' + str(self.saveInfo[3]) + '"',
                         str(type)]) + ")"
        self.cur.execute(request)
        self.con.commit()
        self.close()


class PreviewWidget(Widgets.QFrame):
    def __init__(self, parent):
        Widgets.QWidget.__init__(self, parent)
        self.parent = parent

    def paintEvent(self, event):
        if self.parent.tablerow == -1:
            return
        if self.parent.saveFlag:
            pwidth = self.parent.saveInfo[1]
            pheight = self.parent.saveInfo[2]
            pattern = self.parent.saveInfo[3][1:]
        else:
            pwidth, pheight = self.parent.data[self.parent.tablerow][2:4]
            pattern = self.parent.data[self.parent.tablerow][-1][1:]
        qp = QPainter()
        qp.begin(self)
        pen = QPen()
        pen.setStyle(Qt.NoPen)
        #pen.setColor(QColor(255, 255, 255))
        qp.setPen(pen)
        cell_size = min(self.width() // pwidth, self.height() // pheight, 25)
        left = (self.width() - pwidth * cell_size) // 2
        top = (self.height() - pheight * cell_size) // 2

        for row in range(pheight):
            for col in range(pwidth):
                if pattern[col * pheight + row] == '1':
                    qp.setBrush(QColor(0, 0, 0))
                    qp.drawRect(col * cell_size + left, row * cell_size + top, cell_size, cell_size)
                #elif pattern[col * pheight + row] == '0':
                    #qp.setBrush(QColor(255, 255, 150))
                    #qp.drawRect(col * cell_size + left, row * cell_size + top, cell_size, cell_size)
        qp.end()


class ReturnPatternEvent(QEvent):
    idType = QEvent.registerEventType()
    def __init__(self, saveInfo):
        QEvent.__init__(self, ReturnPatternEvent.idType)
        self.saveInfo = saveInfo

    def get_data(self):
        return self.saveInfo
