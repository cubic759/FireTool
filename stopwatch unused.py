import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QSystemTrayIcon,
    QMenu,
    QAction,
    QLabel,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QStackedLayout,
    QGraphicsDropShadowEffect,
    QSizePolicy,
    QSpinBox,
)
from PyQt5.QtCore import Qt, QPoint, QRect, QTimer, QSize
from PyQt5.QtGui import QIcon, QPainter, QBrush, QColor, QRegion, QFontDatabase, QFont


class NumberPopup(QWidget):
    def __init__(self, callback, val):
        super().__init__()
        self.callback = callback

        self.setWindowTitle("Set Value")
        self.setFixedSize(200, 120)
        QApplication.changeOverrideCursor(Qt.ArrowCursor)

        layout = QVBoxLayout()
        self.label = QLabel("<b>Set Transparency (%):</b>")
        self.spinbox = QSpinBox()
        self.spinbox.setRange(0, 100)
        self.spinbox.setValue(int(val * 100))
        self.ok_button = QPushButton("OK")

        self.ok_button.clicked.connect(self.return_value)

        layout.addWidget(self.label)
        layout.addWidget(self.spinbox)
        layout.addWidget(self.ok_button)
        self.setLayout(layout)

    def return_value(self):
        value = self.spinbox.value() / 100.0
        self.callback(value)
        self.close()


class Stopwatch(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )  # | Qt.Window | Qt.CustomizeWindowHint
        self.transparency = 0.8
        self.blink_colon_visible = True
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)
        # self.resize(130, 60)
        self.resize(400, 200)
        self.setWindowOpacity(self.transparency)
        self.setWindowOpacity(self.transparency)
        self.setMinimumHeight(20)
        self.wrapper = QWidget(self)
        self.wrapper.setMouseTracking(True)
        self.wrapper.setStyleSheet(
            "background-color: rgb(30, 30, 30); border-radius: 5px;"
        )
        self.wrapper.setGeometry(0, 0, self.width(), self.height())

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setOffset(0, 0)
        self.shadow.setColor(QColor(0, 0, 0, 160))
        self.wrapper.setGraphicsEffect(self.shadow)
        self.resize_margin = 10
        self.corner_margin = 20

        self.drag_position = None
        self.resizing = False
        self.resize_edge = None
        # self.wrapper.setGeometry(0, 0, self.width(), self.height())
        # Container widget to center everything
        self.center_container = QWidget(self.wrapper)
        self.center_container.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        self.center_container.setMouseTracking(True)
        # Time display

        self.back_label = QLabel("88:88", self.center_container)
        # self.back_label.setAlignment(Qt.AlignCenter)
        self.back_label.setStyleSheet("color: rgb(45,45,45);background: transparent;")
        self.back_label.setMouseTracking(True)
        self.back_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.back_label.setWordWrap(False)
        self.back_label.setTextInteractionFlags(Qt.NoTextInteraction)

        self.time_label = QLabel("00:00", self.center_container)
        # self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("color: white;background: transparent;")
        self.time_label.setMouseTracking(True)
        self.time_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.time_label.setWordWrap(False)
        self.time_label.setTextInteractionFlags(Qt.NoTextInteraction)
        # self.time_label.setContentsMargins(10, 0, 0, 0)  # (left, top, right, bottom)
        self.font = QFont()
        font_id = QFontDatabase.addApplicationFont("Untitled1.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

        self.font = QFont(font_family)
        self.time_label.setFont(self.font)
        self.back_label.setFont(self.font)
        # self.back_label.raise_()
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        # Buttons
        # self.toggle_button.clicked.connect(self.toggle_timer)
        
        """
        stack_layout = QStackedLayout(self.center_container)
        stack_layout.addWidget(self.back_label)
        stack_layout.addWidget(self.time_label)"""
        
        

        self.menu = QMenu(self)
        self.menu.addAction("Start", self.toggle_timer)
        self.menu.addAction("Reset", self.reset_timer)
        self.menu.addAction("Set Transparency", self.setTransparency)
        self.menu.addAction("Minimize to tray", self.hideToTray)
        self.menu.addAction("Full Screen", self.fullOrNormal)
        self.menu.addAction("Exit", QApplication.quit)
        self.change_action_checkable("Full Screen", True)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.elapsed_seconds = 0
        self.running = False
        # self.task_label.setContentsMargins(1, 1, 0, 0)  # (left, top, right, bottom)
        # self.time_label.setContentsMargins(10, 0, 0, 0)  # (left, top, right, bottom)
        #self.time_label.setGraphicsEffect(self.blur1)
        #self.back_label.setGraphicsEffect(self.blur2)
        # self.time_label.move(0,300)
        """
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        

        # Container widget to center everything
        self.center_container = QWidget()
        self.center_container.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        self.center_container.setMouseTracking(True)
        # Time display
        main_layout.addWidget(self.center_container)"""
        
        # self.wrapper.setParent(self)
        # Layout

        # main_layout = QVBoxLayout(self)
        # main_layout.setAlignment(Qt.AlignCenter)
        # main_layout.addWidget(self.center_container)

        print(
            self.time_label.width()
        )
        # self.setLayout(main_layout)
        # self.wrapper.width(),self.center_container.width(),
        # Tray icon and menu
        self.tray_icon = QSystemTrayIcon(QIcon("stopwatch.png"), self)
        tray_menu = QMenu()

        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()

    def setTransparency(self):
        self.popup = NumberPopup(self.handleTransparency, self.transparency)
        self.popup.show()

    def handleTransparency(self, val):
        self.transparency = val
        self.setWindowOpacity(self.transparency)

    def fullOrNormal(self):
        if self.isFullScreen():  # small
            self.change_action_checked("Full Screen", False)
            # self.change_action_text(3, "FullScreen")
            self.setWindowOpacity(self.transparency)
            # self.wrapper.show()
            self.showNormal()
        else:  # fullscreen
            # self.change_action_text(3, "Normal")
            self.change_action_checked("Full Screen", True)
            self.setWindowOpacity(1)
            # self.wrapper.hide()
            self.showFullScreen()

    def toggle_timer(self):
        if self.running:
            self.timer.stop()
            self.change_action_text("Pause", "Start")
        else:
            self.timer.start(1000)
            # self.time_label.setStyleSheet("color: Lime; ")
            self.change_action_text("Start", "Pause")
        self.running = not self.running

    def change_action_text(self, text, val):
        for action in self.menu.actions():
            if action.text() == text:
                action.setText(val)
                break

    def change_action_checked(self, text, val):
        for action in self.menu.actions():
            if action.text() == text:
                action.setChecked(val)
                break

    def change_action_checkable(self, text, val):
        for action in self.menu.actions():
            if action.text() == text:
                action.setCheckable(val)
                break

    def reset_timer(self):
        self.timer.stop()
        self.elapsed_seconds = 0
        self.update_display()
        self.change_action_text(0, "Start")
        self.running = False

    def update_time(self):
        self.elapsed_seconds += 1
        self.blink_colon_visible = not self.blink_colon_visible
        self.update_display()

    def update_display(self):
        minutes = self.elapsed_seconds // 60
        seconds = self.elapsed_seconds % 60
        # colon_color = "white" if self.blink_colon_visible else "transparent"

        # Format the full string using HTML span for colon
        # text = f'{minutes:02}<span style="color:{colon_color}">:</span>{seconds:02}'
        # self.time_label.setText(f"{minutes:02}:{seconds:02}")
        
        colon = ":" if self.blink_colon_visible else "\ue000"#customized empty space same with colon
        text = f'{minutes:02}{colon}{seconds:02}'
        self.time_label.setText(text)
        
        #self.time_text = f"{minutes:02d}{{colon}}{seconds:02d}"
        #self.apply_blink_colon()
        

    def apply_blink_colon(self):
        colon_html = (
            '<span style="color:white">:</span>'
            if self.blink_colon_visible
            else '<span style="color:transparent">:</span>'
        )
        full_text = self.time_text.replace("{colon}", colon_html)
        self.time_label.setText(full_text)

    def minimumSizeHint(self):
        return QSize(1, 1)

    def contextMenuEvent(self, event):
        """menu = QMenu(self)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(QApplication.quit)
        menu.addAction(exit_action)
        menu.exec_(event.globalPos())"""
        self.menu.exec_(event.globalPos())
        
    """def paintEvent(self, event):
        from PyQt5.QtGui import QPainter, QBrush

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        brush = QBrush(QColor(30, 30, 30))
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        if self.isFullScreen():
            rect = self.rect()
            painter.drawRect(rect)
        else:
            padding = 10
            rect = self.rect().adjusted(padding, padding, -padding, -padding)
            painter.drawRoundedRect(rect, 5, 5)"""

    def hideToTray(self):
        self.hide()
        # show windows notification
        """self.tray_icon.showMessage(
            "App Minimized",
            "Application was minimized to tray.",
            QSystemTrayIcon.Information,
            2000
        )"""

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            edge = self.detect_edge(event.pos())
            if edge:
                self.resizing = True
                self.resize_edge = edge
                self.resize_start_rect = self.geometry()
                self.resize_start_pos = event.globalPos()
            else:
                if not self.isFullScreen():
                    self.drag_position = (
                        event.globalPos() - self.frameGeometry().topLeft()
                    )

    def mouseMoveEvent(self, event):
        if self.isFullScreen():
            pass
        elif self.resizing:
            self.perform_resize(event.globalPos())
        elif self.drag_position and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
        else:
            edge = self.detect_edge(event.pos())
            self.update_cursor(edge)

    def mouseReleaseEvent(self, event):
        self.resizing = False
        self.drag_position = None
        self.resize_edge = None
        # QApplication.setOverrideCursor(Qt.ArrowCursor)
        # QApplication.restoreOverrideCursor()
        QApplication.changeOverrideCursor(Qt.ArrowCursor)
        # self.setCursor(Qt.ArrowCursor)

    def update_cursor(self, edge):
        cursor_map = {
            "left": Qt.SizeHorCursor,
            "right": Qt.SizeHorCursor,
            "top": Qt.SizeVerCursor,
            "bottom": Qt.SizeVerCursor,
            "top-left": Qt.SizeFDiagCursor,
            "bottom-right": Qt.SizeFDiagCursor,
            "top-right": Qt.SizeBDiagCursor,
            "bottom-left": Qt.SizeBDiagCursor,
        }
        if edge:
            # QApplication.restoreOverrideCursor()
            # QApplication.setOverrideCursor(cursor_map[edge])
            QApplication.changeOverrideCursor(cursor_map[edge])
            # self.setCursor(cursor_map[edge])
        else:
            # print("moving")
            # QApplication.restoreOverrideCursor()
            # self.setCursor(Qt.ArrowCursor)
            QApplication.changeOverrideCursor(Qt.ArrowCursor)

    def detect_edge(self, pos):
        x, y = pos.x(), pos.y()
        w, h = self.width(), self.height()
        rm = self.resize_margin
        cm = self.corner_margin

        # Corners first
        if x <= cm and y <= cm:
            return "top-left"
        if x >= w - cm and y <= cm:
            return "top-right"
        if x <= cm and y >= h - cm:
            return "bottom-left"
        if x >= w - cm and y >= h - cm:
            return "bottom-right"

        # Edges
        if x <= rm:
            return "left"
        if x >= w - rm:
            return "right"
        if y <= rm:
            return "top"
        if y >= h - rm:
            return "bottom"
        return None

    def perform_resize(self, global_pos):
        delta = global_pos - self.resize_start_pos
        geom = QRect(self.resize_start_rect)
        """print("Δx:", delta.x(), "Δy:", delta.y())
        print("New Width:", geom.width(), "New Height:", geom.height())
        print(
            "Minimum Width:",
            self.minimumWidth(),
            "Minimum Height:",
            self.minimumHeight(),
        )"""
        min_width = self.time_label.sizeHint().width() + 20  # Add padding if needed
        if "right" in self.resize_edge:
            geom.setWidth(max(min_width, geom.width() + delta.x()))
        if "bottom" in self.resize_edge:
            geom.setHeight(max(40, geom.height() + delta.y()))
        if "left" in self.resize_edge:
            new_x = geom.x() + delta.x()
            new_width = geom.width() - delta.x()
            if new_width >= self.minimumWidth():
                geom.setX(new_x)
                geom.setWidth(new_width)
        if "top" in self.resize_edge:
            new_y = geom.y() + delta.y()
            new_height = geom.height() - delta.y()
            if new_height >= self.minimumHeight():
                geom.setY(new_y)
                geom.setHeight(new_height)

        self.setGeometry(geom)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w = self.width()
        h = self.height()
        if self.isFullScreen():
            self.wrapper.setGeometry(0, 0, w, h)
            self.center_container.setGeometry(0, 0, w, h)
            self.back_label.setGeometry(0, 0, w, h)
            self.time_label.setGeometry(0, 0, w, h)
        else:
            self.wrapper.setGeometry(10, 10, w - 20, h - 20)
            self.center_container.setGeometry(10, 10, w - 20, h - 20)
            self.back_label.setGeometry(10, 10, w - 20, h - 20)
            self.time_label.setGeometry(10, 10, w - 20, h - 20)

        """
            if self.isFullScreen():
                self.wrapper.resize(self.width(), self.height())
            else:
                self.time_label.resize(self.width() - 20, self.height() - 20)
                self.back_label.resize(self.width() - 20, self.height() - 20)
                self.wrapper.resize(self.width() - 20, self.height() - 20)"""
        
        # Calculate font size based on window height or width
        base = min(self.width(), self.height())
        font_size = base // 3
        if font_size >= 1:
            self.font.setPointSize(font_size)
            self.time_label.setFont(self.font)
            self.back_label.setFont(self.font)
            self.update_display()
        else:
            self.time_label.setText("")

    def closeEvent(self, event):
        QApplication.restoreOverrideCursor()
        """event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Minimized",
            "Widget is hidden in the tray.",
            QSystemTrayIcon.Information,
            1500,
        )"""

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    widget = Stopwatch()
    widget.show()

    sys.exit(app.exec_())
