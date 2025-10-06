#!/usr/bin/env python3
"""
Simple launcher script for MIM HyperControl.

This script provides an easy way to run the application from the project root.
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtGui import QFont
    import sys
    
    app = QApplication(sys.argv)
    font = QFont("Calibri")
    font.setPointSize(14)
    app.setFont(font)
    
    from gui.main import MainWindow
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())
