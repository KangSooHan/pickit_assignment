from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer

class mainWindow(QWidget):
    def __init__(self, parent=None):
        super(mainWindow, self).__init__(parent)
        self.elements = ["x", "y", "z", "R", "P", "Y"]
        self.initUI()

    def initUI(self):
        def UI(self, name):
            # Make Coords Layout
            Layout = QGridLayout()

            def CreateDSpinBox(self, name, values):
                minimum, maximum, singlestep = values
                setattr(self, name+"Box", QDoubleSpinBox())
                getattr(self, name+"Box").setMinimum(minimum)
                getattr(self, name+"Box").setMaximum(maximum)
                getattr(self, name+"Box").setValue(0)
                getattr(self, name+"Box").setSingleStep(singlestep)

            xyzCLabel = QLabel(name+" xyz")
            Layout.addWidget(xyzCLabel, 0, 0)
            rpyCLabel = QLabel(name+" rpy")
            Layout.addWidget(rpyCLabel, 2, 0)

            for idx, e in enumerate(self.elements):
                if idx>2:
                    values = (-3.14, 3.14, 0.1)
                else:
                    if name=="Coords":
                        values = (-5, 5, 0.1)
                    elif name=="Trans":
                        values = (-10, 10, 0.1)
                subname = name + e
                CreateDSpinBox(self, subname, values)
                Layout.addWidget(getattr(self, subname+"Box"), idx//3*2+1, idx%3)

            if name=="Coords":
                setattr(self, name+"Button", QPushButton("Create"))
            elif name=="Trans":
                setattr(self, name+"Button", QPushButton("Transform"))
            getattr(self, name+"Button").setDefault(True)
            Layout.addWidget(getattr(self, name+"Button"), 4, 2)

            return Layout

        def opUI(self):
            Layout = QGridLayout()

            self.itemList = QListWidget()
            self.itemList.setSelectionMode(QAbstractItemView.MultiSelection)
            self.itemCombo = QComboBox()
            self.calcButton = QPushButton("Calc")
            self.calcButton.setDefault(True)
            self.removeButton = QPushButton("Remove")
            self.removeButton.setDefault(True)
            self.infoButton = QPushButton("Info")
            self.infoButton.setDefault(True)

            Layout.addWidget(self.itemList, 0, 0, 4, 1)
            Layout.addWidget(self.itemCombo, 0, 3)
            Layout.addWidget(self.calcButton, 1, 3)
            Layout.addWidget(self.removeButton, 2, 3)
            Layout.addWidget(self.Button, 3, 3)

            return Layout

        self.setWindowTitle("Pickit Qt UI")
        self.resize(320, 240)

        # Make Main Layout
        Layout = QVBoxLayout()

        CoordsLayout = UI(self, "Coords")
        Layout.addLayout(CoordsLayout)
        Layout.addStretch(1)

        TransLayout = UI(self, "Trans")
        Layout.addLayout(TransLayout)
        Layout.addStretch(1)

        OpLayout = opUI(self)
        Layout.addLayout(OpLayout)

        self.setLayout(Layout)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    mainWindow_ = mainWindow()
    mainWindow_.show()
    sys.exit(app.exec())
