import sys, os, time, random, pandas as pd, sqlite3, pyqtgraph as pg
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from pyqtgraph import PlotWidget
from 实时程序3 import Ui_mainWindow


class PlotWindow(QWidget):
    def __init__(self, x_data, y_data, title):
        super().__init__()
        self.setWindowTitle(title)

        # 创建绘图控件
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setTitle(title)
        self.plot_widget.plot(x_data, y_data)

        # 设置布局
        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget)
        self.setLayout(layout)


class MainWindow(QMainWindow, Ui_mainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        self.saveDir = 'history2'
        self.dbf = 'rkdb.db'
        cur = None
        con = None

        layout = QVBoxLayout(self.widget_2)
        self.plotWidget_ted = PlotWidget(self)
        layout.addWidget(self.plotWidget_ted)
        layout.setContentsMargins(0, 0, 0, 0)
        self.lineEdit.setValidator(QIntValidator(1, 9999))

        self.loadTableNames()

        self.pushButton_4.clicked.connect(self.startTrial)
        self.pushButton_2.clicked.connect(self.selectAll)
        self.pushButton.clicked.connect(self.deselectAll)
        self.pushButton_3.clicked.connect(self.inverseSelection)
        self.pushButton_5.clicked.connect(self.loadTableNames)
        self.pushButton_7.clicked.connect(self.modifyData)
        self.pushButton_6.clicked.connect(self.deleteRow)
        self.pushButton_9.clicked.connect(self.insertRow)
        self.pushButton_8.clicked.connect(self.dataPlot)

        self.comboBox.currentIndexChanged.connect(self.refreshCurrent)
        self.comboBox_2.currentIndexChanged.connect(self.refreshCurrent)

        self.listView.clicked.connect(self.on_listView_clicked)

        self.checkbox_list = [self.checkBox, self.checkBox_2, self.checkBox_3, self.checkBox_4,
                              self.checkBox_5, self.checkBox_6, self.checkBox_7, self.checkBox_8,
                              self.checkBox_9, self.checkBox_10, self.checkBox_11, self.checkBox_12,
                              self.checkBox_13, self.checkBox_14, self.checkBox_15, self.checkBox_16]

    def selectAll(self):
        for cb in self.checkbox_list:
            cb.setChecked(True)

    def deselectAll(self):
        for cb in self.checkbox_list:
            cb.setChecked(False)

    def inverseSelection(self):
        for cb in self.checkbox_list:
            cb.setChecked(False if cb.isChecked() else True)

    def startTrial(self):
        if self.pushButton_4.text() == "开始实验":
            try:
                self._time = int(self.lineEdit.text()) * 60
            except:
                QMessageBox.warning(self, "警告", "实验时长输入错误！")
                return
            self.data1 = {}

            _status = 0
            for cb in self.checkbox_list:
                if cb.isChecked():
                    self.data1[cb.text()] = {"通道一": [], "通道二": [], "通道三": [], "通道四": [], "通道五": []}
                    _status += 1
            if _status == 0:
                QMessageBox.warning(self, "警告", "未选择设备")
                return

            self.stackedWidget.setCurrentIndex(1)
            self.pushButton_4.setText("停止实验")
            self.lineEdit.setEnabled(False)

            self.initTime = 0
            self.label_3.setText(f'已运行：  {self.initTime}s')

            self.timer = QTimer()
            self.timer.timeout.connect(self.refreshData)
            self.timer.start(1000)

            self.comboBox_2.clear()
            self.comboBox_2.addItems(["通道一", "通道二", "通道三", "通道四", "通道五"])

            self.comboBox.clear()
            self.comboBox.addItems(list(self.data1.keys()))

            self.curve1 = self.plotWidget_ted.plot([], name="mode1")

            self._current = time.strftime("%Y%m%d_%H%M%S", time.localtime())
            self.label_2.setText(f'开始时间：{self._current}')
            os.makedirs(os.path.join(self.saveDir, self._current))


        else:
            self.stackedWidget.setCurrentIndex(0)
            self.pushButton_4.setText("开始实验")
            self.lineEdit.setEnabled(True)

            self.timer.stop()
            self.label_2.setText('开始时间：None')
            self.label_3.setText('已运行：None')

            self.deselectAll()

            self.saveData()

    def saveData(self):
        con = sqlite3.connect(self.dbf)
        for keys, values in self.data1.items():
            # 将值转换为DataFrame
            df = pd.DataFrame(values)

            # 保存为CSV文件
            csv_path = os.path.join(self.saveDir, self._current + "/" + keys + ".csv")
            df.to_csv(csv_path, encoding='gbk')

            # 创建SQLite3表格名
            table_name = f"{keys}_{self._current}"

            # 将DataFrame写入SQLite3数据库的表格
            # 如果表格不存在，则自动创建
            df.to_sql(table_name, con, if_exists='replace', index=False)

            # 关闭数据库连接
        con.close()

    def refreshData(self):
        self.initTime += 1
        self.label_3.setText(f'已运行：  {self.initTime}s')
        for keys, values in self.data1.items():
            self.data1[keys]["通道一"].append(random.randint(90, 100))
            self.data1[keys]["通道二"].append(random.randint(90, 100))
            self.data1[keys]["通道三"].append(random.randint(90, 100))
            self.data1[keys]["通道四"].append(random.randint(90, 100))
            self.data1[keys]["通道五"].append(random.randint(90, 100))

        self.refreshCurrent()
        if self.initTime == self._time:
            self.stackedWidget.setCurrentIndex(0)
            self.pushButton_4.setText("开始实验")
            self.lineEdit.setEnabled(True)

            self.timer.stop()
            self.label_2.setText('开始时间：None')
            self.label_3.setText('已运行：None')

            self.deselectAll()
            self.saveData()

    def refreshCurrent(self):
        _name = self.comboBox.currentText()
        _td = self.comboBox_2.currentText()
        try:
            self.curve1.setData(self.data1[_name][_td])
            self.plotWidget_ted.setXRange(len(self.data1[_name][_td]) - 20, len(self.data1[_name][_td]))

            _info = ''
            for index, key in enumerate(list(self.data1.keys())):
                _info += f'{index + 1}.{key}\n'
                _info += f'当前:{self.data1[key]["通道一"][-1]} 极值:{min(self.data1[key]["通道一"])} 平均:{round(sum(self.data1[key]["通道一"]) / len(self.data1[key]["通道一"]), 2)}\n'
                _info += f'当前:{self.data1[key]["通道二"][-1]} 极值:{min(self.data1[key]["通道二"])} 平均:{round(sum(self.data1[key]["通道二"]) / len(self.data1[key]["通道二"]), 2)}\n'
                _info += f'当前:{self.data1[key]["通道三"][-1]} 极值:{min(self.data1[key]["通道三"])} 平均:{round(sum(self.data1[key]["通道三"]) / len(self.data1[key]["通道三"]), 2)}\n'
                _info += f'当前:{self.data1[key]["通道四"][-1]} 极值:{min(self.data1[key]["通道四"])} 平均:{round(sum(self.data1[key]["通道四"]) / len(self.data1[key]["通道四"]), 2)}\n'
                _info += f'当前:{self.data1[key]["通道五"][-1]} 极值:{min(self.data1[key]["通道五"])} 平均:{round(sum(self.data1[key]["通道五"]) / len(self.data1[key]["通道五"]), 2)}\n'
                _info += '\n\n'
            self.textEdit.setText(_info)

        except:
            pass

    def loadTableNames(self):
        # 获取所有表格名称
        con = sqlite3.connect(self.dbf)
        cursor = con.cursor()
        sql = "SELECT name FROM sqlite_master WHERE type='table';"
        cursor.execute(sql)
        table_names = cursor.fetchall()

        # 将表格名称转换为字符串列表
        table_names = [name[0] for name in table_names]

        # 设置listView的模型
        self.listView.setModel(QStringListModel(table_names))

    def on_listView_clicked(self, index):
        # 获取被点击的表格名称
        table_name = self.listView.model().data(self.listView.currentIndex(), Qt.ItemDataRole.DisplayRole)

        # 清除tableWidget中的旧数据
        self.tableWidget.clear()

        # 设置tableWidget的列标题（如果表格结构已知）
        # 这里假设每个表格都有相同的列标题，你可以根据具体表格结构调整
        self.tableWidget.setHorizontalHeaderLabels(['通道一', '通道二', '通道三', '通道四', '通道五'])

        # 从数据库中读取表格数据
        con = sqlite3.connect(self.dbf)
        cursor = con.cursor()
        sql = f"SELECT * FROM {table_name};"
        cursor.execute(sql)
        alldata = cursor.fetchall()

        # 将数据添加到tableWidget中
        self.tableWidget.setRowCount(len(alldata))
        self.tableWidget.setColumnCount(len(alldata[0]))
        for row_index, row in enumerate(alldata):
            for column_index, data in enumerate(row):
                item = QTableWidgetItem(str(data))
                self.tableWidget.setItem(row_index, column_index, item)

                # 调整tableWidget的列宽以适应内容
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)

    def modifyData(self):
        # 获取当前选中的单元格位置
        row, col = self.tableWidget.currentRow(), self.tableWidget.currentColumn()
        if row < 0 or col < 0:
            # 如果没有选中单元格，则显示错误消息或返回
            print("请选择一个单元格以进行修改")
            return

            # 弹出对话框让用户输入新数据
        dialog = QDialog()
        dialog.setWindowTitle('输入新数据')
        layout = QVBoxLayout()
        label = QLabel(f"请输入第 {row + 1} 行，第 {col + 1} 列的新数据：")
        lineEdit = QLineEdit()
        okButton = QPushButton('确定')
        okButton.clicked.connect(dialog.accept)
        cancelButton = QPushButton('取消')
        cancelButton.clicked.connect(dialog.reject)

        layout.addWidget(label)
        layout.addWidget(lineEdit)
        layout.addWidget(okButton)
        layout.addWidget(cancelButton)
        dialog.setLayout(layout)

        if dialog.exec() == 1:
            new_data = lineEdit.text()

            modifyData_table_name = self.listView.model().data(self.listView.currentIndex(),
                                                               Qt.ItemDataRole.DisplayRole)
            column_name = self.tableWidget.horizontalHeaderItem(col).text()

            # 更新self.tableWidget中的数据
            item = QTableWidgetItem(new_data)
            self.tableWidget.setItem(row, col, item)

            con = sqlite3.connect(self.dbf)
            cursor = con.cursor()
            cursor.execute(f"UPDATE {modifyData_table_name} SET {column_name}=? WHERE rowid=?",
                           (int(new_data), row + 1))
            con.commit()
        else:
            print("Dialog not accepted")

    def deleteRow(self):
        currentIndex = self.tableWidget.currentRow()
        if currentIndex < 0:
            QMessageBox.information(self, "提醒", "请选择删除位置")
        else:
            self.tableWidget.removeRow(currentIndex)

            con = sqlite3.connect(self.dbf)
            cursor = con.cursor()
            deleteRow_table_name = self.listView.model().data(self.listView.currentIndex(), Qt.ItemDataRole.DisplayRole)

            row_index_in_db = currentIndex + 1
            sql = f"DELETE FROM {deleteRow_table_name} WHERE rowid={row_index_in_db}"
            cursor.execute(sql)
            con.commit()

    def insertRow(self):
        # 获取当前选中的行，用于确定新行的位置
        selectedRow = self.tableWidget.currentRow()
        if selectedRow != -1:  # 如果没有选中的行，则在最后添加

            # 在表格中插入新行
            self.tableWidget.insertRow(selectedRow)

            inputs, ok = QInputDialog.getText(self, '输入新行数据', '请输入新行的值（用逗号分隔）：')
            if ok:
                values = inputs.strip().split(',')
                header_labels = [self.tableWidget.horizontalHeaderItem(i).text() for i in
                                 range(self.tableWidget.columnCount())]
                if len(values) == len(header_labels):
                    for column, value in enumerate(values):
                        item = QTableWidgetItem(value)
                        self.tableWidget.setItem(selectedRow, column, item)

                    con = sqlite3.connect(self.dbf)
                    cursor = con.cursor()

                    insertRow_table_name = self.listView.model().data(self.listView.currentIndex(),
                                                                      Qt.ItemDataRole.DisplayRole)
                    columns = ', '.join(header_labels)  # 假设列名与表头标签相同
                    placeholders = ', '.join(['?'] * len(values))
                    sql = f"INSERT INTO {insertRow_table_name} ({columns}) VALUES ({placeholders})"
                    # 执行插入操作
                    cursor.execute(sql, values)
                    con.commit()
                    print('数据插入成功')
                else:
                    print("输入的值数量与列数不匹配")
        else:
            print("请先选择一行")

    def dataPlot(self):

        selectedColumn = self.tableWidget.currentColumn()
        if selectedColumn != -1:
            x_data = list(range(self.tableWidget.rowCount()))
            y_data = []
            for row in range(self.tableWidget.rowCount()):
                item = self.tableWidget.item(row, selectedColumn)
                if item:
                    y_data.append(float(item.text()))
            plot_window = PlotWindow(x_data, y_data, f"Column {selectedColumn + 1} Data")
            plot_window.show()
        else:
            print("请先选择一列数据")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
