from PyQt5.QtCore import Qt, QPropertyAnimation, QRect
from PyQt5.QtWidgets import QApplication, QWidget
import sys

GAP = 2
HIDDEN_SIZE = 5   # visible pixels when hidden
ANIM_TIME = 300   # ms

class EdgeAutoHideWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(200, 150)
        self.snapped_edge = None   # "left", "right", "top", "bottom"
        self.state = "shown"       # "shown" or "hidden"
        self.animation = QPropertyAnimation(self, b"geometry", self)

    def snap_to_edge(self, edge):
        """Call this after your snap logic"""
        self.snapped_edge = edge

    def animate_to(self, rect, new_state):
        self.animation.stop()
        self.animation.setDuration(ANIM_TIME)
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(rect)
        self.animation.start()
        self.state = new_state

    def leaveEvent(self, event):
        if self.state != "shown" or not self.snapped_edge:
            return

        geo = self.geometry()
        screen = QApplication.primaryScreen().availableGeometry()

        if self.snapped_edge == "left":
            hidden = QRect(screen.left() - geo.width() + HIDDEN_SIZE,
                           geo.y(), geo.width(), geo.height())
        elif self.snapped_edge == "right":
            hidden = QRect(screen.right() - HIDDEN_SIZE,
                           geo.y(), geo.width(), geo.height())
        elif self.snapped_edge == "top":
            hidden = QRect(geo.x(), screen.top() - geo.height() + HIDDEN_SIZE,
                           geo.width(), geo.height())
        elif self.snapped_edge == "bottom":
            hidden = QRect(geo.x(), screen.bottom() - HIDDEN_SIZE,
                           geo.width(), geo.height())
        else:
            return

        self.animate_to(hidden, "hidden")

    def enterEvent(self, event):
        if self.state != "hidden" or not self.snapped_edge:
            return

        geo = self.geometry()
        screen = QApplication.primaryScreen().availableGeometry()

        if self.snapped_edge == "left":
            shown = QRect(screen.left() + GAP, geo.y(), geo.width(), geo.height())
        elif self.snapped_edge == "right":
            shown = QRect(screen.right() - geo.width() - GAP,
                          geo.y(), geo.width(), geo.height())
        elif self.snapped_edge == "top":
            shown = QRect(geo.x(), screen.top() + GAP,
                          geo.width(), geo.height())
        elif self.snapped_edge == "bottom":
            shown = QRect(geo.x(), screen.bottom() - geo.height() - GAP,
                          geo.width(), geo.height())
        else:
            return

        self.animate_to(shown, "shown")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = EdgeAutoHideWindow()
    w.show()
    w.snap_to_edge("left")  # for testing
    sys.exit(app.exec_())
