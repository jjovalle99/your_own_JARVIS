import sys

import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5 import QtCore, QtWidgets


class WaveformVisualizer:
    def __init__(self, x=None, y=None):
        self.app = QtWidgets.QApplication.instance()
        if not self.app:
            self.app = QtWidgets.QApplication(sys.argv)

        self.window = QtWidgets.QMainWindow()
        self.window.setWindowTitle("Agent powered by SambaNova")
        self.window.resize(800, 400)

        # Set window position if specified
        if x is not None and y is not None:
            self.window.move(x, y)
        else:
            # Center the window on the screen by default
            screen = QtWidgets.QApplication.primaryScreen().geometry()
            window_geometry = self.window.geometry()
            x = (screen.width() - window_geometry.width()) // 2
            y = (screen.height() - window_geometry.height()) // 2
            self.window.move(x, y)

        self.canvas = WaveformCanvas()
        self.window.setCentralWidget(self.canvas)

        # Keep window on top
        self.window.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Window)

    def show(self):
        self.window.show()
        # Process any pending events
        self.app.processEvents()

    def update_waveform(self, audio_chunk: np.ndarray):
        self.canvas.update_with_data(audio_chunk)
        # Process events to ensure UI updates
        self.app.processEvents()

    def move_window(self, x: int, y: int):
        """Move the window to a specific position on the screen."""
        self.window.move(x, y)
        self.app.processEvents()


class WaveformCanvas(FigureCanvas):
    AMPLIFICATION = 15
    SHRINK_FACTOR = 3

    def __init__(self):
        self.fig = Figure(facecolor="black")
        super().__init__(self.fig)

        # Setup plot
        self.ax = self.fig.add_subplot(111)
        self.ax.set_axis_off()

        # Single line for visualization
        self.line = self.ax.plot([], [], color="#FF00FF", linewidth=2)[0]

        # Adjust figure margins
        self.fig.tight_layout(pad=0)

    def update_with_data(self, audio_chunk: np.ndarray):
        # Process audio data
        data = audio_chunk * self.AMPLIFICATION

        # Update plot
        x_data = np.arange(len(data))
        self.line.set_data(x_data, data)

        # Set limits
        self.ax.set_xlim(0, len(data))
        self.ax.set_ylim(-32768 * self.SHRINK_FACTOR, 32768 * self.SHRINK_FACTOR)

        # Redraw
        self.draw()
