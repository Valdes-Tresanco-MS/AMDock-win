from PyQt4 import QtGui, QtCore
import sys
from AMDock.splash_screen import SplashScreen
from AMDock.Docking_Program import AMDock
from AMDock.variables import Objects as ob


def run():
    if __name__ == "__main__":
        app = QtGui.QApplication(sys.argv)
        app_icon = QtGui.QIcon()
        # dw = QtGui.QDesktopWidget()
        app_icon.addFile(ob.app_icon_, QtCore.QSize(16, 20))
        app_icon.addFile(ob.app_icon_, QtCore.QSize(24, 30))
        app_icon.addFile(ob.app_icon_, QtCore.QSize(32, 40))
        app_icon.addFile(ob.app_icon_, QtCore.QSize(48, 60))
        app_icon.addFile(ob.app_icon_, QtCore.QSize(223, 283))
        app.setStyle("cleanlooks")
        app.setWindowIcon(app_icon)
        app.setApplicationName('AMDock: Assisted Molecular Docking for AutoDock and AutoDock Vina')
        splash = SplashScreen(QtGui.QPixmap(ob.splashscreen_path), app)
        main = AMDock()
        splash.finish(main)
        main.setMinimumSize(1080, 740)
        # main.resize(1200, int(dw.height() * 0.9))
        main.setWindowTitle('AMDock: Assisted Molecular Docking with AutoDock4 and AutoDock Vina')
        main.setWindowIcon(app_icon)
        main.show()
        if splash.import_error():
            sys.exit(app.exec_())
        else:
            sys.exit(app.exit(1))


run()