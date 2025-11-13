# Date: 12/112025
# DEV: Martinez
# Cloud Optimizer v1 Free Utility by Martinez

import sys
from PyQt6 import QtWidgets
from cloud_optimizer.utils import run_as_admin
from cloud_optimizer.main_window import MainWindow


def main():
    """Entry point mínimo para iniciar a aplicação."""
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())


