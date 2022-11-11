import serial
import time
import re
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QPushButton
import PyQt5
from functools import partial


class Robot:
    POLLINGDELAY = 0.05  # seconds between sending a message and polling for a reply
    TIMEOUT = 10  # seconds
    POSITIONTOLERANCE = 0.1  # tolerance (mm) between target and actual position
    ZHOP_HEIGHT = (
        5  # height (mm) to raise gantry between movements. This is to avoid collisions.
    )
    XLIM = [0, 235]  # mm
    YLIM = [0, 235]
    ZLIM = [0, 250]

    def __init__(self, port):
        # communication variables
        self.port = port
        self.position = [
            None,
            None,
            None,
        ]  # start at None's to indicate stage has not been homed.
        self.__targetposition = [None, None, None]
        self.connect()  # connect by default

    # communication methods
    def connect(self):
        self._handle = serial.Serial(port=self.port, timeout=1, baudrate=115200)
        self.update()
        # self.update_gripper()
        if self.position == [
            self.XLIM[1],
            self.YLIM[1],
            self.ZLIM[1],
        ]:  # this is what it shows when initially turned on, but not homed
            self.position = [
                None,
                None,
                None,
            ]  # start at None's to indicate stage has not been homed.
        # self.write('M92 X40.0 Y26.77 Z400.0')
        # self.set_defaults()
        print("Connected!")

    def disconnect(self):
        self._handle.close()
        del self._handle

    def write(self, msg):
        self._handle.write(f"{msg}\n".encode())
        time.sleep(self.POLLINGDELAY)
        output = []
        while self._handle.in_waiting:
            line = self._handle.readline().decode("utf-8").strip()
            if line != "ok":
                output.append(line)
            time.sleep(self.POLLINGDELAY)
        return output

    def _enable_steppers(self):
        self.write("M17")

    def _disable_steppers(self):
        self.write("M18")

    def update(self):
        found_coordinates = False
        while not found_coordinates:
            output = self.write("M114")  # get current position
            for line in output:
                if line.startswith("X:"):
                    x = float(re.findall(r"X:(\S*)", line)[0])
                    y = float(re.findall(r"Y:(\S*)", line)[0])
                    z = float(re.findall(r"Z:(\S*)", line)[0])
                    found_coordinates = True
                    break
        self.position = [x, y, z]

    # gantry methods

    def gohome(self):
        self.write("G28 X Y Z")
        self.update()

    def premove(self, x, y, z):
        """
        checks to confirm that all target positions are valid
        """
        if self.position == [None, None, None]:
            raise Exception(
                "Stage has not been homed! Home with self.gohome() before moving please."
            )
        if x is None:
            x = self.position[0]
        if y is None:
            y = self.position[1]
        if z is None:
            y = self.position[2]

        # check if we are transitioning between workspace/gantry, if so, handle it
        return x, y, z

    def moveto(self, x=None, y=None, z=None, zhop=True, speed=None):
        """
        moves to target position in x,y,z (mm)
        """
        try:
            if len(x) == 3:
                x, y, z = x  # split 3 coordinates into appropriate variables
        except:
            pass
        x, y, z = self.premove(x, y, z)  # will error out if invalid move
        if speed is None:
            speed = self.speed
        if (x == self.position[0]) and (y == self.position[1]):
            zhop = False  # no use zhopping for no lateral movement
        if zhop:
            z_ceiling = max(self.position[2], z) + self.ZHOP_HEIGHT
            z_ceiling = min(
                z_ceiling, self.ZLIM[1]
            )  # cant z-hop above build volume. mostly here for first move after homing.
            self.moveto(z=z_ceiling, zhop=False, speed=speed)
            self.moveto(x, y, z_ceiling, zhop=False, speed=speed)
            self.moveto(z=z, zhop=False, speed=speed)
        else:
            self._movecommand(x, y, z, speed)

    def _movecommand(self, x: float, y: float, z: float, speed: float):
        """internal command to execute a direct move from current location to new location"""
        if self.position == [x, y, z]:
            return True  # already at target position
        else:
            self.__targetposition = [x, y, z]
            self.write(f"G0 X{x} Y{y} Z{z} F{speed}")
            return self._waitformovement()

    def moverel(self, x=0, y=0, z=0, zhop=True, speed=None):
        """
        moves by coordinates relative to the current position
        """
        try:
            if len(x) == 3:
                x, y, z = x  # split 3 coordinates into appropriate variables
        except:
            pass
        x += self.position[0]
        y += self.position[1]
        z += self.position[2]
        self.moveto(x, y, z, zhop, speed)

    def _waitformovement(self):
        """
        confirm that gantry has reached target position. returns False if
        target position is not reached in time allotted by self.GANTRYTIMEOUT
        """
        self.inmotion = True
        start_time = time.time()
        time_elapsed = time.time() - start_time
        self._handle.write(f"M400\n".encode())
        self._handle.write(f"M118 E1 FinishedMoving\n".encode())
        reached_destination = False
        while not reached_destination and time_elapsed < self.GANTRYTIMEOUT:
            time.sleep(self.POLLINGDELAY)
            while self._handle.in_waiting:
                line = self._handle.readline().decode("utf-8").strip()
                if line == "echo:FinishedMoving":
                    self.update()
                    if (
                        np.linalg.norm(
                            [
                                a - b
                                for a, b in zip(self.position, self.__targetposition)
                            ]
                        )
                        < self.POSITIONTOLERANCE
                    ):
                        reached_destination = True
                time.sleep(self.POLLINGDELAY)
            time_elapsed = time.time() - start_time

        self.inmotion = ~reached_destination
        self.update()
        return reached_destination

    # GUI
    def gui(self):
        GantryGUI(gantry=self)  # opens blocking gui to manually jog motors


class GantryGUI:
    def __init__(self, gantry):
        AlignHCenter = PyQt5.QtCore.Qt.AlignHCenter
        self.gantry = gantry
        self.app = PyQt5.QtCore.QCoreApplication.instance()
        if self.app is None:
            self.app = QApplication([])
        # self.app = QApplication(sys.argv)
        self.app.aboutToQuit.connect(self.app.deleteLater)
        self.win = QWidget()
        self.grid = QGridLayout()
        self.stepsize = 1  # default step size, in mm

        ### axes labels
        for j, label in enumerate(["X", "Y", "Z"]):
            temp = QLabel(label)
            temp.setAlignment(AlignHCenter)
            self.grid.addWidget(temp, 0, j)

        ### position readback values
        self.xposition = QLabel("0")
        self.xposition.setAlignment(AlignHCenter)
        self.grid.addWidget(self.xposition, 1, 0)

        self.yposition = QLabel("0")
        self.yposition.setAlignment(AlignHCenter)
        self.grid.addWidget(self.yposition, 1, 1)

        self.zposition = QLabel("0")
        self.zposition.setAlignment(AlignHCenter)
        self.grid.addWidget(self.zposition, 1, 2)

        self.update_position()

        ### status label
        self.gantrystatus = QLabel("Idle")
        self.gantrystatus.setAlignment(AlignHCenter)
        self.grid.addWidget(self.gantrystatus, 5, 4)

        ### jog motor buttons
        self.jogback = QPushButton("Back")
        self.jogback.clicked.connect(partial(self.jog, y=-1))
        self.grid.addWidget(self.jogback, 3, 1)

        self.jogforward = QPushButton("Forward")
        self.jogforward.clicked.connect(partial(self.jog, y=1))
        self.grid.addWidget(self.jogforward, 2, 1)

        self.jogleft = QPushButton("Left")
        self.jogleft.clicked.connect(partial(self.jog, x=-1))
        self.grid.addWidget(self.jogleft, 3, 0)

        self.jogright = QPushButton("Right")
        self.jogright.clicked.connect(partial(self.jog, x=1))
        self.grid.addWidget(self.jogright, 3, 2)

        self.jogup = QPushButton("Up")
        self.grid.addWidget(self.jogup, 2, 3)
        self.jogup.clicked.connect(partial(self.jog, z=1))

        self.jogdown = QPushButton("Down")
        self.jogdown.clicked.connect(partial(self.jog, z=-1))
        self.grid.addWidget(self.jogdown, 3, 3)

        ### step size selector buttons
        self.steppt1 = QPushButton("0.1 mm")
        self.steppt1.clicked.connect(partial(self.set_stepsize, stepsize=0.1))
        self.grid.addWidget(self.steppt1, 5, 0)
        self.step1 = QPushButton("1 mm")
        self.step1.clicked.connect(partial(self.set_stepsize, stepsize=1))
        self.grid.addWidget(self.step1, 5, 1)
        self.step10 = QPushButton("10 mm")
        self.step10.clicked.connect(partial(self.set_stepsize, stepsize=10))
        self.grid.addWidget(self.step10, 5, 2)
        self.step50 = QPushButton("50 mm")
        self.step50.clicked.connect(partial(self.set_stepsize, stepsize=50))
        self.grid.addWidget(self.step50, 6, 0)
        self.step100 = QPushButton("100 mm")
        self.step100.clicked.connect(partial(self.set_stepsize, stepsize=100))
        self.grid.addWidget(self.step100, 6, 1)

        self.stepsize_options = {
            0.1: self.steppt1,
            1: self.step1,
            10: self.step10,
            50: self.step50,
            100: self.step100,
        }

        self.set_stepsize(self.stepsize)

        self.run()

    def set_stepsize(self, stepsize):
        self.stepsize = stepsize
        for setting, button in self.stepsize_options.items():
            if setting == stepsize:
                button.setStyleSheet("background-color: #a7d4d2")
            else:
                button.setStyleSheet("background-color: None")

    def jog(self, x=0, y=0, z=0):
        self.gantrystatus.setText("Moving")
        self.gantrystatus.setStyleSheet("color: red")
        self.gantry.moverel(x * self.stepsize, y * self.stepsize, z * self.stepsize)
        self.update_position()
        self.gantrystatus.setText("Idle")
        self.gantrystatus.setStyleSheet("color: None")

    def update_position(self):
        for position, var in zip(
            self.gantry.position, [self.xposition, self.yposition, self.zposition]
        ):
            var.setText(f"{position:.2f}")

    def run(self):
        self.win.setLayout(self.grid)
        self.win.setWindowTitle("PASCAL Gantry GUI")
        self.win.setGeometry(300, 300, 500, 150)
        self.win.show()
        self.app.setQuitOnLastWindowClosed(True)
        self.app.exec_()
        # self.app.quit()
        # sys.exit(self.app.exec_())
        # self.app.exit()
        # sys.exit(self.app.quit())
        return
