#!/usr/bin/env python3

import math
import rospy
import PyKDL
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread

import pickit_gui

from visualization_msgs.msg import MarkerArray, Marker
from std_msgs.msg import ColorRGBA, Bool
from geometry_msgs.msg import Point, Vector3, Quaternion

class Main(pickit_gui.mainWindow):
    create_signal = pyqtSignal()
    select_signal = pyqtSignal()
    show_signal = pyqtSignal()
    calc_signal = pyqtSignal()
    trans_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.CoordsButton.clicked.connect(self.create)
        self.calcButton.clicked.connect(self.calc)
        self.removeButton.clicked.connect(self.remove)
        self.itemList.itemClicked.connect(self.select)
        self.TransButton.clicked.connect(self.trans)
        self.InfoButton.clicked.connect(self.info)
        
        self.xyzRPY = None
        self.select_item = None
        self.transform = None

        self.th = Worker(parent=self)
        self.th.start()
        self.create_signal.connect(lambda: self.th.create(self.xyzRPY))
        self.select_signal.connect(lambda: self.th.select(self.select_item))
        self.calc_signal.connect(lambda: self.th.calc(self.select_item, self.itemCombo.currentText()))
        self.trans_signal.connect(lambda: self.th.trans(self.select_item, self.transform))

        self.show()

    def create(self):
        self.itemList.addItem(str(self.th.ids))
        self.itemCombo.addItem(str(self.th.ids))
        self.xyzRPY = [self.CoordsxBox.value(), self.CoordsyBox.value(), self.CoordszBox.value(), self.CoordsRBox.value(), self.CoordsPBox.value(), self.CoordsYBox.value()]
        self.create_signal.emit()

    def select(self):
        self.select_item = self.itemList.selectedItems()
        self.select_signal.emit()

    def calc(self):
        self.calc_signal.emit()

    def info(self):

    def trans(self):
        self.transform = [self.TransxBox.value(), self.TransyBox.value(), self.TranszBox.value(), self.TransRBox.value(), self.TransPBox.value(), self.TransYBox.value()]
        self.trans_signal.emit()

    def remove(self):
        if self.select_item == None:
            return

        for idx, item in enumerate(self.select_item):
            self.th.marker_dict.pop(str(item.text()))
            self.itemList.takeItem(self.itemList.row(item))
            self.itemCombo.removeItem(self.itemCombo.findText(item.text()))

        self.select_item = None
        self.select_signal.emit()


class Worker(QThread):
    worker = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__()
        self.main = parent
        self.marker_dict = dict()
        self.ids = 0

        self.align_y = PyKDL.Rotation.RPY(0, 0, math.pi/2)
        self.align_z = PyKDL.Rotation.RPY(0, -math.pi/2, 0)
        self.marker_pub = rospy.Publisher("marker_array", MarkerArray, queue_size=1)
        self.markers = MarkerArray()

    def __del__(self):
        self.wait()
    
    def run(self):
        while not rospy.is_shutdown():
            self.worker.emit()
            self.marker_pub.publish(self.markers)


    @pyqtSlot()
    def create(self, xyzRPY):
        if xyzRPY==None:
            return
        self.marker_dict[str(self.ids)]= xyzRPY
        self.ids+=1

    @pyqtSlot()
    def trans(self, select_item, transform):
        if select_item == None:
            return
        t_x, t_y, t_z, t_R, t_P, t_Y = transform
        tvec = PyKDL.Vector(t_x, t_y, t_z)
        trot = PyKDL.Rotation.RPY(t_R,t_P,t_Y)
        tframe = PyKDL.Frame(trot, tvec)
        for idx, item in enumerate(select_item):
            x,y,z,R,P,Y=self.marker_dict[str(item.text())]
            vec = PyKDL.Vector(x, y, z)
            rot = PyKDL.Rotation.RPY(R, P, Y)
            frame = PyKDL.Frame(rot, vec)
            new_frame = frame*tframe

            self.marker_dict.update({str(item.text()) : [new_frame.p.x(), new_frame.p.y(), new_frame.p.z(), new_frame.M.GetRPY()[0], new_frame.M.GetRPY()[1], new_frame.M.GetRPY()[2]]})

        self.select(select_item)


    @pyqtSlot()
    def select(self, select_item):
        self.markers = MarkerArray()

        clear_msg = Marker()
        clear_msg.header.frame_id = "map"
        clear_msg.action = Marker.DELETEALL
        clear_msg.header.stamp = rospy.Time()
        self.markers.markers.append(clear_msg)

        if select_item==None:
            return

        for idx, item in enumerate(select_item):
            item = str(item.text())
            self.show_(idx, item)

    @pyqtSlot()
    def calc(self, select_item, combo_item):
        if select_item == None:
            return
        msgBox = QMessageBox()
        b_x, b_y, b_z, b_R, b_P, b_Y = self.marker_dict[combo_item]

        text = ""
        for idx, item in enumerate(select_item):
            item = str(item.text())
            x,y,z,R,P,Y = self.marker_dict[item]

            text += f"{combo_item} -> {item} = [{x-b_x}, {y-b_y}, {z-b_z}, {R-b_R}, {P-b_P}, {Y-b_Y}]\n\n"
        msgBox.setText(text)
        msgBox.exec_()

    @pyqtSlot()
    def show_(self, idx, item):
        x,y,z,R,P,Y = self.marker_dict[item]
        vec = PyKDL.Vector(x, y, z)
        rot = PyKDL.Rotation.RPY(R,P,Y)

        for i, axis in enumerate(["x", "y", "z"]):
            arrow = Marker()
            arrow.header.frame_id = "map"
            arrow.ns = f"axis_{axis}_{self.ids}"
            arrow.id = idx*3+i+1

            arrow.type = Marker.ARROW
            arrow.action = Marker.ADD

            if i==0:
                arrow.color = ColorRGBA(1, 0, 0, 1)
                arot = rot
            elif i==1:
                arrow.color = ColorRGBA(0, 1, 0, 1)
                arot = rot * self.align_y
            else:
                arrow.color = ColorRGBA(0, 0, 1, 1)
                arot = rot * self.align_z
            arrow.scale = Vector3(0.5, 0.05, 0.05)

            qx, qy, qz, qw = list(PyKDL.Rotation.GetQuaternion(arot))

            arrow.pose.position = Point(vec.x(), vec.y(), vec.z())
            arrow.pose.orientation = Quaternion(qx, qy, qz, qw)
            self.markers.markers.append(arrow)




if __name__ == "__main__":
    import sys
    rospy.init_node("pickit_assignment")
    app = QApplication(sys.argv)
    main = Main()
    sys.exit(app.exec_())
