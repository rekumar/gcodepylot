from gcodepylot import RobotXYZ


class Ender3(RobotXYZ):
    POLLINGDELAY = 0.001
    TIMEOUT = 0.1
    POSITIONTOLERANCE = 0.1
    ZHOP_HEIGHT = 5
    XLIM = 235
    YLIM = 235
    ZLIM = 250
    MAX_XY_FEEDRATE = 10000  # mm/min
    MAX_Z_FEEDRATE = 25 * 60  # mm/min
