# Form implementation generated from reading ui file 'pyaudicle.ui'
#
# Created by: PyQt6 UI code generator 6.5.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.
from PyQt6 import QtCore, QtGui, QtWidgets, Qsci

import sys
import os.path

import pychuck


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(960, 960)
        MainWindow.setStyleSheet("QTabWidget::tab-bar {\n"
                                 "    left: 5px;\n"
                                 "}")
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.pushButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton.setCheckable(True)
        self.pushButton.setChecked(False)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_3.addWidget(self.pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.tabWidget = QtWidgets.QTabWidget(parent=self.centralwidget)
        self.tabWidget.setMaximumSize(QtCore.QSize(300, 16777215))
        self.tabWidget.setStyleSheet("")
        self.tabWidget.setObjectName("tabWidget")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.tab_3)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.treeView = QtWidgets.QTreeView(parent=self.tab_3)
        self.treeView.setObjectName("treeView")
        self.verticalLayout_3.addWidget(self.treeView)
        self.tabWidget.addTab(self.tab_3, "")
        self.verticalLayout.addWidget(self.tabWidget, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.tabWidget_2 = QtWidgets.QTabWidget(parent=self.centralwidget)
        self.tabWidget_2.setMaximumSize(QtCore.QSize(300, 300))
        self.tabWidget_2.setObjectName("tabWidget_2")
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.tab_4)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.tableWidget = QtWidgets.QTableWidget(parent=self.tab_4)
        self.tableWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tableWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.tableWidget.setRowCount(12)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(4)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        self.tableWidget.verticalHeader().setVisible(False)
        self.verticalLayout_4.addWidget(self.tableWidget)
        self.tabWidget_2.addTab(self.tab_4, "")
        self.verticalLayout.addWidget(self.tabWidget_2, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushButton_2 = QtWidgets.QPushButton(parent=self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setStyleSheet("color: rgb(91, 199, 94);")
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_2.addWidget(self.pushButton_2)
        self.pushButton_3 = QtWidgets.QPushButton(parent=self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        self.pushButton_3.setFont(font)
        self.pushButton_3.setStyleSheet("color: rgb(101, 158, 208);")
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout_2.addWidget(self.pushButton_3)
        self.pushButton_4 = QtWidgets.QPushButton(parent=self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        self.pushButton_4.setFont(font)
        self.pushButton_4.setStyleSheet("color: rgb(237, 107, 98);")
        self.pushButton_4.setObjectName("pushButton_4")
        self.horizontalLayout_2.addWidget(self.pushButton_4)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding,
                                           QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.pushButton_5 = QtWidgets.QPushButton(parent=self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        self.pushButton_5.setFont(font)
        self.pushButton_5.setStyleSheet("color: rgb(245, 192, 92);")
        self.pushButton_5.setObjectName("pushButton_5")
        self.horizontalLayout_2.addWidget(self.pushButton_5)
        self.pushButton_6 = QtWidgets.QPushButton(parent=self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        self.pushButton_6.setFont(font)
        self.pushButton_6.setObjectName("pushButton_6")
        self.horizontalLayout_2.addWidget(self.pushButton_6)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.tabWidget_3 = QtWidgets.QTabWidget(parent=self.centralwidget)
        self.tabWidget_3.setTabsClosable(True)
        self.tabWidget_3.setObjectName("tabWidget_3")
        self.verticalLayout_2.addWidget(self.tabWidget_3)
        self.tabWidget_4 = QtWidgets.QTabWidget(parent=self.centralwidget)
        self.tabWidget_4.setMaximumSize(QtCore.QSize(16777215, 300))
        self.tabWidget_4.setObjectName("tabWidget_4")
        self.tab_5 = QtWidgets.QWidget()
        self.tab_5.setObjectName("tab_5")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.tab_5)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.textBrowser = QtWidgets.QTextBrowser(parent=self.tab_5)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout_5.addWidget(self.textBrowser)
        self.tabWidget_4.addTab(self.tab_5, "")
        self.verticalLayout_2.addWidget(self.tabWidget_4)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 960, 24))
        self.menubar.setObjectName("menubar")
        self.menuNew_File = QtWidgets.QMenu(parent=self.menubar)
        self.menuNew_File.setObjectName("menuNew_File")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionNew_File = QtGui.QAction(parent=MainWindow)
        self.actionNew_File.setObjectName("actionNew_File")
        self.actionOpen = QtGui.QAction(parent=MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionOpen_Folder = QtGui.QAction(parent=MainWindow)
        self.actionOpen_Folder.setObjectName("actionOpen_Folder")
        self.actionSave = QtGui.QAction(parent=MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionSave_As = QtGui.QAction(parent=MainWindow)
        self.actionSave_As.setObjectName("actionSave_As")
        self.actionClose_Editor = QtGui.QAction(parent=MainWindow)
        self.actionClose_Editor.setObjectName("actionClose_Editor")
        self.menuNew_File.addAction(self.actionNew_File)
        self.menuNew_File.addSeparator()
        self.menuNew_File.addAction(self.actionOpen)
        self.menuNew_File.addAction(self.actionOpen_Folder)
        self.menuNew_File.addSeparator()
        self.menuNew_File.addAction(self.actionSave)
        self.menuNew_File.addAction(self.actionSave_As)
        self.menuNew_File.addSeparator()
        self.menuNew_File.addAction(self.actionClose_Editor)
        self.menubar.addAction(self.menuNew_File.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget_2.setCurrentIndex(0)
        self.tabWidget_3.setCurrentIndex(-1)
        self.tabWidget_4.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "Start Virtual Machine"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "Explorer"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "shred"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "name"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "time"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "-"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_4), _translate("MainWindow", "Virtual Machine"))
        self.pushButton_2.setToolTip(_translate("MainWindow", "Add Shred"))
        self.pushButton_2.setText(_translate("MainWindow", "+"))
        self.pushButton_3.setToolTip(_translate("MainWindow", "Replace Shred"))
        self.pushButton_3.setText(_translate("MainWindow", "="))
        self.pushButton_4.setToolTip(_translate("MainWindow", "Remove Shred"))
        self.pushButton_4.setText(_translate("MainWindow", "-"))
        self.pushButton_5.setToolTip(_translate("MainWindow", "Remove Last Shred"))
        self.pushButton_5.setText(_translate("MainWindow", "--"))
        self.pushButton_6.setToolTip(_translate("MainWindow", "Clear Virtual Machine"))
        self.pushButton_6.setText(_translate("MainWindow", "x"))
        self.tabWidget_4.setTabText(self.tabWidget_4.indexOf(self.tab_5), _translate("MainWindow", "Console"))
        self.menuNew_File.setTitle(_translate("MainWindow", "File"))
        self.actionNew_File.setText(_translate("MainWindow", "New File"))
        self.actionNew_File.setShortcut(_translate("MainWindow", "Ctrl+N"))
        self.actionOpen.setText(_translate("MainWindow", "Open..."))
        self.actionOpen.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.actionOpen_Folder.setText(_translate("MainWindow", "Open Folder..."))
        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionSave.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.actionSave_As.setText(_translate("MainWindow", "Save As..."))
        self.actionSave_As.setShortcut(_translate("MainWindow", "Ctrl+Shift+S"))
        self.actionClose_Editor.setText(_translate("MainWindow", "Close Editor"))
        self.actionClose_Editor.setShortcut(_translate("MainWindow", "Ctrl+W"))


'''================================================================================'''
'''|                                  EDITOR                                      |'''
'''================================================================================'''


class ScintillaEditor(Qsci.QsciScintilla):

    def __init__(self):
        super(ScintillaEditor, self).__init__()
        self.path = None

        # -------------------------------- #
        #     QScintilla editor setup      #
        # -------------------------------- #

        self.setText("")
        self.setLexer(None)  # We install lexer later
        self.setUtf8(True)  # Set encoding to UTF-8

        # 1. Text wrapping
        # -----------------
        self.setWrapMode(Qsci.QsciScintilla.WrapMode.WrapWord)
        self.setWrapVisualFlags(Qsci.QsciScintilla.WrapVisualFlag.WrapFlagByText)
        self.setWrapIndentMode(Qsci.QsciScintilla.WrapIndentMode.WrapIndentIndented)

        # 2. End-of-line mode
        # --------------------
        self.setEolMode(Qsci.QsciScintilla.EolMode.EolWindows)
        self.setEolVisibility(False)

        # 3. Indentation
        # ---------------
        self.setIndentationsUseTabs(False)
        self.setTabWidth(4)
        self.setIndentationGuides(True)
        self.setTabIndents(True)
        self.setAutoIndent(True)

        # 4. Caret
        # ---------
        self.setCaretForegroundColor(QtGui.QColor("#ff0000ff"))
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QtGui.QColor("#1f0000ff"))
        self.setCaretWidth(2)

        # 5. Margins
        # -----------
        self.setMarginType(0, Qsci.QsciScintilla.MarginType.NumberMargin)
        self.setMarginWidth(0, "0000")
        self.setMarginsForegroundColor(QtGui.QColor("#ff888888"))

        # -------------------------------- #
        #          Install lexer           #
        # -------------------------------- #
        self.__lexer = Qsci.QsciLexerPython(self)
        self.setLexer(self.__lexer)

    def read(self, path):
        self.path = path
        self.setText(open(path).read())

    def clear(self):
        self.path = None
        self.setText("")

    def save(self):
        with open(self.path, "w") as f:
            f.write(self.text())


'''=== end class ==='''


class TabMaster:
    def __init__(self, tab_widget):
        self.tab_widget = tab_widget
        self.tab_widget.addTab(ScintillaEditor(), "Untitled")

    def add_tab(self, file_path):
        file_name = os.path.basename(file_path)
        n_tab = self.tab_widget.count()
        if self.tab_widget.tabText(0) == "Untitled" and len(self.tab_widget.widget(0).text()) == 0:
            self.tab_widget.setTabText(0, file_name)
            self.tab_widget.widget(0).read(file_path)
            return
        for i in range(n_tab):
            if self.tab_widget.widget(i).path == file_path:
                self.tab_widget.setCurrentIndex(i)
                return
        self.tab_widget.addTab(ScintillaEditor(), file_name)
        self.tab_widget.widget(n_tab).read(file_path)
        self.tab_widget.setCurrentIndex(n_tab)

    def remove_tab(self, index):
        if self.tab_widget.count() == 1:
            self.tab_widget.setTabText(0, "Untitled")
            self.tab_widget.widget(0).clear()
        else:
            tab = self.tab_widget.widget(index)
            tab.deleteLater()
            self.tab_widget.removeTab(index)

    def add_new_tab(self):
        count = 1
        n_tab = self.tab_widget.count()
        for i in range(n_tab):
            if self.tab_widget.tabText(i).startswith("Untitled"):
                count += 1
        tab_name = "Untitled" if count == 1 else f"Untitled {count}"
        self.tab_widget.addTab(ScintillaEditor(), tab_name)
        self.tab_widget.setCurrentIndex(n_tab)

    def save_file(self):
        if self.tab_widget.currentWidget().path is None:
            return self.save_file_as()
        self.tab_widget.currentWidget().save()

    def save_file_as(self):
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self.tab_widget, "Save File", "", "Python Files (*.py)")
        if file_path:
            file_name = os.path.basename(file_path)
            self.tab_widget.setTabText(self.tab_widget.currentIndex(), file_name)
            self.tab_widget.currentWidget().path = file_path
            self.tab_widget.currentWidget().save()

    def close_editor(self):
        self.remove_tab(self.tab_widget.currentIndex())

    def curr_tab_name(self):
        return self.tab_widget.tabText(self.tab_widget.currentIndex())

    def curr_tab_code(self):
        return self.tab_widget.currentWidget().text()


class StreamToTextBrowser:
    def __init__(self, text_browser):
        self.text_browser = text_browser

    def write(self, message):
        self.text_browser.append(message)

    def flush(self):
        pass


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("PyAudicle")

        # console
        sys.stdout = sys.stderr = StreamToTextBrowser(self.textBrowser)

        # button
        self.pushButton.clicked.connect(self.change_vm_state)
        self.pushButton_2.clicked.connect(self.add_shred)
        self.pushButton_3.clicked.connect(self.replace_shred)
        self.pushButton_4.clicked.connect(self.remove_shred)
        self.pushButton_5.clicked.connect(self.remove_last_shred)
        self.pushButton_6.clicked.connect(self.clear_vm)

        # explorer
        self.file_system_model = QtGui.QFileSystemModel(self)
        self.file_system_model.setRootPath(QtCore.QDir.rootPath())
        self.treeView.setModel(self.file_system_model)
        self.treeView.setRootIndex(self.file_system_model.index(QtCore.QDir.currentPath()))
        self.treeView.header().hide()
        for i in range(1, self.treeView.header().count()):
            self.treeView.hideColumn(i)
        self.treeView.doubleClicked.connect(self.treeView_doubleClicked)

        # virtual machine
        self.tableWidget.setColumnWidth(0, 50)
        self.tableWidget.setColumnWidth(1, 120)
        self.tableWidget.setColumnWidth(2, 65)
        self.tableWidget.setColumnWidth(3, 20)
        for i in range(self.tableWidget.rowCount()):
            self.tableWidget.setRowHeight(i, 20)
            for j in range(3):
                self.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem())
            button = QtWidgets.QPushButton("-")
            button.clicked.connect(lambda _, row=i: self.remove_row(row))
            self.tableWidget.setCellWidget(i, 3, button)
        self.refresh_table_timer = QtCore.QTimer()
        self.refresh_table_timer.timeout.connect(self.refresh_table)
        self.refresh_table_timer.start(500)

        # editor
        self.tab_master = TabMaster(self.tabWidget_3)
        self.tabWidget_3.tabCloseRequested.connect(self.tab_master.remove_tab)

        # action
        self.actionNew_File.triggered.connect(self.tab_master.add_new_tab)
        self.actionOpen.triggered.connect(self.open_file)
        self.actionOpen_Folder.triggered.connect(self.open_folder)
        self.actionSave.triggered.connect(self.tab_master.save_file)
        self.actionSave_As.triggered.connect(self.tab_master.save_file_as)
        self.actionClose_Editor.triggered.connect(self.tab_master.close_editor)

    def change_vm_state(self):
        if self.pushButton.text() == "Start Virtual Machine":
            self.pushButton.setText("Stop Virtual Machine")
            print("Starting Virtual Machine...")
            pychuck.VM.start()
        else:
            self.pushButton.setText("Start Virtual Machine")
            print("Stopping Virtual Machine...")
            pychuck.VM.stop()

    def add_shred(self):
        pychuck.VM.add_shred(self.tab_master.curr_tab_code(), self.tab_master.curr_tab_name())

    def replace_shred(self):
        name = self.tab_master.curr_tab_name()
        pychuck.VM.remove_shred(name)
        pychuck.VM.add_shred(self.tab_master.curr_tab_code(), name)

    def remove_shred(self):
        pychuck.VM.remove_shred(self.tab_master.curr_tab_name())

    def remove_last_shred(self):
        pychuck.VM.remove_last_shred()

    def clear_vm(self):
        pychuck.VM.clear_vm()

    def treeView_doubleClicked(self, index):
        file_path = self.file_system_model.filePath(index)
        if QtCore.QFileInfo(file_path).isFile():
            self.tab_master.add_tab(file_path)

    def open_file(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", "",
                                                             "All Files (*);;Python Files (*.py)")
        if file_path:
            self.tab_master.add_tab(file_path)

    def open_folder(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Open Folder", "")
        if folder_path:
            self.treeView.setRootIndex(self.file_system_model.index(folder_path))

    def refresh_table(self):
        for i in range(self.tableWidget.rowCount()):
            for j in range(3):
                self.tableWidget.item(i, j).setText("")
        for i, shred in enumerate(pychuck.VM._shreds):
            self.tableWidget.item(i, 0).setText(str(shred._id))
            self.tableWidget.item(i, 1).setText(shred._name)
            seconds = shred._samples_computed // pychuck.VM._sample_rate
            min, sec = divmod(seconds, 60)
            self.tableWidget.item(i, 2).setText(f'{min:02}:{sec:02}')

    def change_shred_state(self, row):
        self.tableWidget.cellWidget(row, 3).setCheckState(QtCore.Qt.CheckState.Unchecked)

    def remove_row(self, row):
        id_str = self.tableWidget.item(row, 0).text()
        if len(id_str) > 0:
            pychuck.VM.remove_shred(id=int(id_str))