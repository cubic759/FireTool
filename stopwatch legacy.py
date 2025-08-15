import sys
from datetime import datetime
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
    QTextEdit,
    QCheckBox,
    QGraphicsBlurEffect,
    QToolTip,
)
from PyQt5.QtCore import Qt, QPoint, QRect, QTimer, QSize, QEvent
from PyQt5.QtGui import (
    QIcon,
    QPainter,
    QBrush,
    QColor,
    QRegion,
    QFontDatabase,
    QFont,
    QFontMetrics,
    QCursor,
)
from enum import Enum


class SettingWindowTypes(Enum):
    TRANSPARENCY = 0
    TASK = 1


class FloatingTooltip(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setWindowOpacity(self.parent().transparency)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)

        self.resize(100, 100)
        self.setStyleSheet(
            "background-color: rgb(30, 30, 30); border-radius: 5px; border: 1px solid rgb(80, 80, 80);"
        )

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide)

        """self.wrapper = QWidget(self)
        self.wrapper.setMouseTracking(True)
        self.wrapper.setStyleSheet(
            "background-color: rgb(30, 30, 30); border-radius: 5px; border: 1px solid rgb(80, 80, 80);"
        )
        self.wrapper.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)"""
        font_id = QFontDatabase.addApplicationFont("Roboto-Regular.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.font = QFont(font_family)
        self.font.setPointSize(9)

        # Set up the label
        self.label = QLabel(text, self)
        self.label.setStyleSheet(
            """
            color: white;
            padding: 2px;
        """
        )
        self.label.setFont(self.font)
        self.label.adjustSize()
        # self.resize(self.label.size())
        self.adjustSize()

        # self.setSize()

        # Auto-close after duration
        # QTimer.singleShot(duration_ms, self.close)

    def show_at(self, x, y):
        self.move(x, y)
        self.show()

    def setText(self, text):
        self.label.setText(text)
        self.label.adjustSize()
        # self.resize(self.label.size())
        self.adjustSize()
        print(self.label.size())

    def getTextSize(self):
        return self.label.size()

    def startTimer(self):
        self.timer.start(100)

    def stopTimer(self):
        self.timer.stop()

    def setLabelSize(self, size):
        self.label.setGeometry(size)

    def setFontSize(self, size):
        self.font.setPointSize(size)
        self.label.setFont(self.font)
        self.label.adjustSize()
        # self.resize(self.label.size())
        self.adjustSize()
        print(self.label.size())

    def setTransparency(self, value):
        self.setWindowOpacity(value)

    def enterEvent(self, a0):
        super().enterEvent(a0)
        self.stopTimer()
        QApplication.changeOverrideCursor(Qt.ArrowCursor)

    def leaveEvent(self, a0):
        super().leaveEvent(a0)
        self.startTimer()


class Settings(QWidget):

    def __init__(self, callback, data, typeValue, parent=None):
        super().__init__(parent)
        self.callback = callback
        self.typeValue = typeValue
        self.setWindowFlags(
            Qt.Tool | Qt.WindowStaysOnTopHint
        )  # | Qt.Window | Qt.CustomizeWindowHint| Qt.FramelessWindowHint
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)

        layout = QVBoxLayout(self)

        if self.typeValue == SettingWindowTypes.TRANSPARENCY.value:
            self.setWindowTitle("Set Transparency")
            self.setFixedSize(250, 120)
            self.label = QLabel("<b>Set Transparency (%):</b>")
            self.spinbox = QSpinBox()
            self.spinbox.setRange(0, 100)
            self.spinbox.setValue(int(data["value"] * 100))
            self.checkbox = QCheckBox("Full screen lock to 100%")
            self.checkbox.setChecked(data["flag"])
            self.ok_button = QPushButton("OK")

            self.ok_button.clicked.connect(self.return_value)

            layout.addWidget(self.label)
            layout.addWidget(self.spinbox)
            layout.addWidget(self.checkbox)
            layout.addWidget(self.ok_button)
        else:
            self.setWindowTitle("Set Task")
            self.setFixedSize(500, 300)
            self.label = QLabel("<b>Input your task: (First line for idle state)</b>")
            self.text = QTextEdit()

            self.text.setText("\n".join(data["value"]))
            self.text.setMouseTracking(True)
            self.checkbox = QCheckBox("random display when started")
            self.checkbox.setChecked(data["flag"])
            self.ok_button = QPushButton("OK")

            self.ok_button.clicked.connect(self.return_value)

            layout.addWidget(self.label)
            layout.addWidget(self.text)
            layout.addWidget(self.checkbox)
            layout.addWidget(self.ok_button)
        # self.setLayout(layout)

    def enterEvent(self, event):
        super().enterEvent(event)
        QApplication.changeOverrideCursor(Qt.ArrowCursor)

    def leaveEvent(self, a0):
        super().leaveEvent(a0)
        self.parent().closeTooltip()

    def closeEvent(self, a0):
        super().closeEvent(a0)
        if self.typeValue == SettingWindowTypes.TRANSPARENCY.value:
            self.parent().settingWindowStatus[
                SettingWindowTypes.TRANSPARENCY.value
            ] = False
        else:
            self.parent().settingWindowStatus[SettingWindowTypes.TASK.value] = False

    def return_value(self):
        if self.typeValue == SettingWindowTypes.TRANSPARENCY.value:
            data = {
                "value": self.spinbox.value() / 100.0,
                "flag": self.checkbox.isChecked(),
            }
        else:
            data = {
                "value": self.text.toPlainText().split("\n"),
                "flag": self.checkbox.isChecked(),
            }
        self.callback(data)

        self.close()


class Stopwatch(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.transparency = 0.8
        self.task_index = 0
        self.tasks = ["Take a break", "Drawing", "Music", "Modeling"]
        self.functions = ["⏱", "🕓", "⏳"]
        self.function_labels = []
        self.functionIndex = 0
        self.showingTime = False
        self.stateNow = 0
        self.breakAfter = 60
        self.fullScreenLocked = True
        self.randomTaskDisplay = False
        self.blink_colon_visible = True
        self.is_dragging = False
        self.settingWindowStatus = [False] * len(SettingWindowTypes)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.elapsed_seconds = 0
        self.running = False
        self.paused = False

        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self.resize(140, 120)  # 130 60
        self.setWindowOpacity(self.transparency)
        self.setMinimumSize(40, 20)
        self.wrapper = QWidget(self)
        self.wrapper.setMouseTracking(True)
        self.wrapper.setStyleSheet(
            "background-color: rgb(30, 30, 30); border-radius: 5px; border: 1px solid rgb(80, 80, 80);"
        )
        self.wrapper.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.wrapper.setContentsMargins(20, 20, 20, 20)
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
        self.isMouseDown = False

        self.back_label = QLabel("88:88", self.wrapper)
        self.back_label.setAlignment(Qt.AlignCenter)
        self.back_label.setStyleSheet("color: rgb(40,40,40);background: transparent;")
        self.back_label.setMouseTracking(True)
        self.back_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.back_label.setWordWrap(False)
        self.back_label.setTextInteractionFlags(Qt.NoTextInteraction)

        self.time_label = QLabel("00:00", self.wrapper)
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("color: white;background: transparent;")
        self.time_label.setMouseTracking(True)
        self.time_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.time_label.setWordWrap(False)
        self.time_label.setTextInteractionFlags(Qt.NoTextInteraction)

        self.task_label = QLabel(self.tasks[0], self.wrapper)
        self.task_label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        self.task_label.setStyleSheet("color: white;background: transparent;")
        self.task_label.setMouseTracking(True)
        self.task_label.setWordWrap(False)
        self.task_label.setTextInteractionFlags(Qt.NoTextInteraction)

        for function in self.functions:
            function_label = QLabel(function, self.wrapper)
            function_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
            function_label.setStyleSheet("color: white;background: transparent;")
            function_label.setMouseTracking(True)
            function_label.setWordWrap(False)
            function_label.setTextInteractionFlags(Qt.NoTextInteraction)
            self.function_labels.append(function_label)

        pushButtonStyle = """
            QPushButton {
                background-color: black;
                color: white;
                border: none;
                font-size: 20px;
                padding: 5px 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #333;
            }
            QPushButton:pressed {
                background-color: #555;
            }
        """

        '''self.functionRButton = QPushButton(">", self.wrapper)
        self.functionRButton.setStyleSheet(pushButtonStyle)
        self.functionRButton.setMouseTracking(True)
        self.functionRButton.clicked.connect(self.nextFunction)

        self.functionLButton = QPushButton("<", self.wrapper)
        self.functionLButton.setStyleSheet(pushButtonStyle)
        self.functionLButton.setMouseTracking(True)
        self.functionLButton.clicked.connect(self.lastFunction)'''
        layout = QHBoxLayout(self.wrapper)
        for label in self.function_labels:
            label.adjustSize()
            layout.addWidget(label)

        font_id = QFontDatabase.addApplicationFont("lcd_alarm.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

        self.font1 = QFont(font_family)
        self.time_label.setFont(self.font1)
        self.back_label.setFont(self.font1)
        self.time_label.resize(120, 40)
        self.back_label.resize(120, 40)
        font_id = QFontDatabase.addApplicationFont("Roboto-Regular.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.font2 = QFont(font_family)
        self.font2.setPointSize(10)
        self.task_label.setFont(self.font2)
        #self.function_label.setFont(self.font2)
        #self.function_label.adjustSize()
        self.time_label.hide()
        self.task_label.show()
        print(self.back_label.size())
        self.active_original_size = self.back_label.size()

        self.tooltip = FloatingTooltip(self.tasks[self.task_index], self)
        self.popup = [None] * len(
            SettingWindowTypes
        )  # Settings(self.handleTasks, data, 1)

        self.resizeContent()
        QApplication.setOverrideCursor(Qt.ArrowCursor)

        self.menu = QMenu(self)
        self.menu.addAction("Start", self.toggle_timer)
        self.menu.addAction("Reset", self.reset_timer)
        self.menu.addAction("Set Transparency", self.setTransparency)
        self.menu.addAction("Edit Tasks", self.editTasks)
        self.menu.addAction("Minimize to tray", self.hideToTray)
        self.menu.addAction("Full Screen", self.fullOrNormal)
        self.menu.addAction("Exit", QApplication.quit)
        self.change_action_checkable("Full Screen", True)

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

        self.timer.start(1000)

    """
    -------------------------------------------------------------
    events
    
    -------------------------------------------------------------
    """

    def nextFunction(self):
        self.functionIndex+=1
        self.function_label.setText(self.functions[self.functionIndex])
        if self.functionIndex >= len(self.functions) - 1:
            self.functionRButton.setDisabled(True)
            
        if self.functionIndex >= 0:
            self.functionLButton.setDisabled(False)

    def lastFunction(self):
        self.functionIndex-=1
        self.function_label.setText(self.functions[self.functionIndex])
        if self.functionIndex <= 0:
            self.functionLButton.setDisabled(True)
            
        if self.functionIndex < len(self.functions) - 1:
            self.functionRButton.setDisabled(False)
       

    def changeEvent(self, event):
        if event.type() == QEvent.ActivationChange:
            if self.isActiveWindow():
                # print("Window Activated")
                self.set_shadow(True)
            else:
                # print("Window Deactivated")
                self.set_shadow(False)

    def set_shadow(self, focused: bool):
        if focused:
            self.shadow.setBlurRadius(20)
            # color = QColor(0, 0, 0, 160)  # more transparent when unfocused
        else:
            self.shadow.setBlurRadius(10)
            # color = QColor(0, 0, 0, 80)  # more transparent when unfocused
        # self.shadow.setColor(color)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()

        if delta > 0:
            self.task_index = (self.task_index + 1) % len(self.tasks)
        elif delta < 0:
            self.task_index = (self.task_index - 1) % len(self.tasks)

        self.tooltip.setText(self.tasks[self.task_index])
        event.accept()

    def enterEvent(self, a0):
        super().enterEvent(a0)
        self.tooltip.move(
            widget.mapToGlobal(QPoint(10, self.wrapper.height() + 20))
        )  # Position above the widget
        self.tooltip.show()
        self.tooltip.stopTimer()

    def leaveEvent(self, a0):
        super().leaveEvent(a0)
        widget_under_mouse = QApplication.instance().widgetAt(QCursor.pos())
        print(widget_under_mouse)
        if not self.isFullScreen() and (
            widget_under_mouse is None
            or not (
                widget_under_mouse in (self, self.tooltip, self.menu)
                or widget_under_mouse in self.popup
            )
        ):
            print("yes")
            self.tooltip.startTimer()

    def closeTooltip(self):
        self.tooltip.startTimer()

    def resetTooltip(self):
        self.tooltip.stopTimer()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            edge = self.detect_edge(event.pos())
            if edge:
                self.resizing = True
                self.resize_edge = edge
                self.resize_start_rect = self.geometry()
                self.resize_start_pos = event.globalPos()
            else:
                self.is_dragging = False
                self.isMouseDown = True
                """if not self.running:
                    self.back_label.show()
                    self.time_label.show()
                self.update_display()"""

                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if not self.isFullScreen():
            if self.resizing:
                self.perform_resize(event.globalPos())
                self.tooltip.move(
                    widget.mapToGlobal(QPoint(10, self.wrapper.height() + 20))
                )
                self.is_dragging = True
            elif self.drag_position and event.buttons() == Qt.LeftButton:
                self.move(event.globalPos() - self.drag_position)
                self.tooltip.move(
                    widget.mapToGlobal(QPoint(10, self.wrapper.height() + 20))
                )
                self.is_dragging = True
            else:
                edge = self.detect_edge(event.pos())
                self.update_cursor(edge)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and not self.is_dragging:
            part = self.detect_inside(event.x())
            self.perform_function(part)
            # self.resizeContent()
            self.is_dragging = False
        self.resizing = False
        self.drag_position = None
        self.resize_edge = None
        self.isMouseDown = False

        """if not self.paused and not self.running:
            self.time_label.hide()"""
        self.update_display()
        QApplication.changeOverrideCursor(Qt.ArrowCursor)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            if self.isFullScreen():  # small
                self.change_action_checked("Full Screen", False)
                self.setWindowOpacity(self.transparency)
                self.showNormal()

    """
    -------------------------------------------------------------
    toolkit
    
    -------------------------------------------------------------
    """

    def editTasks(self):
        if not self.settingWindowStatus[SettingWindowTypes.TASK.value]:
            data = {
                "value": self.tasks,
                "flag": self.randomTaskDisplay,
            }
            self.popup[SettingWindowTypes.TASK.value] = Settings(
                self.handleTasks, data, SettingWindowTypes.TASK.value, self
            )
            self.popup[SettingWindowTypes.TASK.value].show()
            self.popup[SettingWindowTypes.TASK.value].activateWindow()
            self.settingWindowStatus[SettingWindowTypes.TASK.value] = True
        else:
            self.popup[SettingWindowTypes.TASK.value].activateWindow()

    def handleTasks(self, data):
        self.tasks = data["value"]

    def setTransparency(self):
        if not self.settingWindowStatus[SettingWindowTypes.TRANSPARENCY.value]:
            data = {
                "value": self.transparency,
                "flag": self.fullScreenLocked,
            }
            self.popup[SettingWindowTypes.TRANSPARENCY.value] = Settings(
                self.handleTransparency,
                data,
                SettingWindowTypes.TRANSPARENCY.value,
                self,
            )
            self.popup[SettingWindowTypes.TRANSPARENCY.value].show()
            self.popup[SettingWindowTypes.TRANSPARENCY.value].activateWindow()
            self.settingWindowStatus[SettingWindowTypes.TRANSPARENCY.value] = True
        else:
            self.popup[SettingWindowTypes.TRANSPARENCY.value].activateWindow()

    def handleTransparency(self, data):
        self.transparency = data["value"]
        print(self.transparency)
        self.fullScreenLocked = data["flag"]
        if self.fullScreenLocked:
            self.setWindowOpacity(1)
            self.tooltip.setTransparency(1)
        else:
            self.setWindowOpacity(self.transparency)
            self.tooltip.setTransparency(self.transparency)
        self.update()

    def fullOrNormal(self):
        if self.isFullScreen():  # small
            self.change_action_checked("Full Screen", False)
            self.setWindowOpacity(self.transparency)
            self.showNormal()
        else:  # fullscreen
            self.change_action_checked("Full Screen", True)
            if self.fullScreenLocked:
                self.setWindowOpacity(1)
            else:
                self.setWindowOpacity(self.transparency)
            # Position above the widget

            self.showFullScreen()

    def toggle_timer(self):
        if self.running:
            # self.timer.stop()
            self.paused = True
            self.change_action_text("Pause", "Start")
        else:
            self.time_label.show()
            # self.timer.start(1000)
            self.paused = False
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
        # self.timer.stop()
        self.time_label.hide()
        self.elapsed_seconds = 0
        self.update_display()
        self.resizeContent()
        self.change_action_text("Pause", "Start")
        self.running = False

    def update_time(self):
        if self.running:
            self.elapsed_seconds += 1
        self.blink_colon_visible = not self.blink_colon_visible
        # self.adjustSize()
        self.update_display()

    def update_display(self):

        if self.showingTime:
            self.show_time_now()
        else:
            hours = self.elapsed_seconds // 3600
            minutes = self.elapsed_seconds // 60 % 60
            seconds = self.elapsed_seconds % 60

            if self.running:
                colon = (
                    ":" if self.blink_colon_visible else "\ue000"
                )  # customized empty space same with colon
            else:
                colon = ":"
            if hours > 0:
                text = f"{hours:0>2}{colon}{minutes:02}{colon}{seconds:02}"
                digit_count = max(2, len(str(hours)))
                self.back_label.setText("8" * digit_count + ":88:88")
                self.time_label.setText(text)
                if self.is_large_power_of_ten(hours) or self.elapsed_seconds == 3600:
                    self.resizeContent()
            else:
                text = f"{minutes:02}{colon}{seconds:02}"
                self.back_label.setText("88:88")
                self.time_label.setText(text)

    def mmmss(self):
        minutes = self.elapsed_seconds // 60
        seconds = self.elapsed_seconds % 60

        if self.running:
            colon = (
                ":" if self.blink_colon_visible else "\ue000"
            )  # customized empty space same with colon
        else:
            colon = ":"
        text = f"{minutes:0>2}{colon}{seconds:02}"
        digit_count = max(2, len(str(minutes)))
        self.back_label.setText("8" * digit_count + ":88")
        self.time_label.setText(text)
        if self.is_large_power_of_ten(minutes):
            self.resizeContent()

    def is_large_power_of_ten(self, n):
        return n >= 100 and str(n).startswith("1") and set(str(n)[1:]) <= {"0"}

    def show_time_now(self):
        now = datetime.now()
        minutes = now.hour  # e.g., 14 for 2 PM
        seconds = now.minute  # e.g., 35
        colon = (
            ":" if self.blink_colon_visible else "\ue000"
        )  # customized empty space same with colon
        text = f"{minutes:02}{colon}{seconds:02}"
        self.back_label.setText("88:88")
        self.time_label.setText(text)

    def contextMenuEvent(self, event):
        self.menu.exec_(event.globalPos())

    def hideToTray(self):
        self.hide()

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
            QApplication.changeOverrideCursor(cursor_map[edge])
        else:
            QApplication.changeOverrideCursor(Qt.ArrowCursor)

    def perform_function(self, part):

        if part == 1:
            pass
        elif part == 2:
            if self.stateNow == 0:
                self.shadow.setBlurRadius(10)
                self.stateNow = 2
            elif self.stateNow == 2:
                self.shadow.setBlurRadius(20)
                self.stateNow = 0
            # self.show_tooltip(self.task_label.text(),1)
            """if self.stateNow == 0 and self.task_label.isHidden():
               self.back_label.hide()
                self.time_label.hide()
                self.task_label.show()

                self.stateNow = 2
            elif self.stateNow == 2:
                self.back_label.show()
                if self.running or self.paused:
                    self.time_label.show()
                self.task_label.hide()
                self.stateNow = 0
            self.resizeContent()"""
        elif part == 3:
            if self.stateNow == 0 and not self.showingTime:
                self.showingTime = True
                if not self.running:
                    self.time_label.show()
                self.update_display()
                self.stateNow = 3
                """
                self.tooltip.move(
                    widget.mapToGlobal(QPoint(10, self.wrapper.height() + 20))
                )  # Position above the widget
                self.tooltip.show()"""
                # self.show_tooltip("Time now",0)
            elif self.stateNow == 3:
                self.showingTime = False
                if not self.running and not self.paused:
                    self.time_label.hide()
                self.update_display()
                self.stateNow = 0
                # self.show_tooltip("Stopwatch",0)
        else:
            pass

    def show_tooltip(self, text, position):
        # Show tooltip at label position
        pos = self.wrapper.mapToGlobal(QPoint(0, 0))
        if position == 0:
            pos.setY(pos.y() - self.height() + 10)
        else:
            pos.setY(pos.y() + self.height() - 20)
        QToolTip.showText(pos, text, self.wrapper)
        QTimer.singleShot(3000, QToolTip.hideText)

    def detect_inside(self, x):
        width = self.width()
        part_width = width / 4

        if x < part_width:
            part = 1
        elif x < part_width * 2:
            part = 2
        elif x < part_width * 3:
            part = 3
        else:
            part = 4
        return part

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

    """
    -------------------------------------------------------------
    misc
    
    -------------------------------------------------------------
    """

    def showTooltip(self):
        if self.isFullScreen():
            self.tooltip.move(
                widget.mapToGlobal(
                    QPoint(
                        0, self.height() - self.tooltip.height()
                    )  # self.width() // 2 - self.tooltip.width() // 2
                )
            )  # Position above the widget

        self.tooltip.show()
        self.tooltip.stopTimer()
        self.tooltip.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resizeContent()

    def resizeContent(self):
        w = self.width()
        h = self.height()

        # Calculate font size based on window height or width
        # base = self.height()  # min(self.width(), self.height())
        # font_size = int((base * 0.99) / 4)

        if self.isFullScreen():
            self.wrapper.setGeometry(0, 0, w, h)
            self.shadow.setBlurRadius(0)
            # self.center_container.setGeometry(0, 0, w, h)
            self.back_label.setGeometry(0, 0, w, h)
            self.time_label.setGeometry(0, 0, w, h)
            self.task_label.setGeometry(0, 0, w, h)
            QTimer.singleShot(500, self.showTooltip)
            """self.tooltip.move(
                widget.mapToGlobal(
                    QPoint(
                        0, self.height() - self.tooltip.height()
                    )  # self.width() // 2 - self.tooltip.width() // 2
                )
            )"""
        else:
            self.wrapper.setGeometry(10, 10, w - 20, h - 20)
            self.shadow.setBlurRadius(20)
            # self.center_container.setGeometry(10, 10, w - 20, h - 20)
            self.back_label.setGeometry(0, 0, w - 20, h - 20)
            self.time_label.setGeometry(0, 0, w - 20, h - 20)
            self.task_label.setGeometry(0, 0, w - 20, h - 20)
           # self.function_label.setGeometry(0, 0, w - 20, h - 20)
            self.tooltip.move(self.mapToGlobal(QPoint(10, self.wrapper.height() + 20)))

        width_ratio = 98 / 120
        height_ratio = 24 / 40
        print(
            self.back_label.width(),
            self.active_original_size.width(),
            self.back_label.height(),
            self.active_original_size.height(),
        )
        size = self.tooltip.getTextSize()
        print(width_ratio, height_ratio, size)
        size = QSize(
            int(self.back_label.width() * width_ratio),
            int(self.back_label.height() * height_ratio),
        )
        print(size)
        font_size = self.getFontSize(size, max(self.tasks, key=len), self.font2)
        print(font_size)
        self.tooltip.setFontSize(font_size)
        point_size = self.getFontSize(
            self.time_label, self.back_label.text(), self.font1
        )
        if point_size >= 1:
            self.font1.setPointSize(point_size)
            self.time_label.setFont(self.font1)
            self.back_label.setFont(self.font1)
            font_size = self.getFontSize(
                self.task_label, max(self.tasks, key=len), self.font2
            )

            self.font2.setPointSize(font_size)
            self.task_label.setFont(self.font2)
        else:
            self.time_label.setText("")

        print(self.back_label.size())

    def getFontSize(self, label, text, font):

        if not text or text == "":
            return 0
        label_width = label.width()
        label_height = label.height()

        low = 5
        high = 500  # max font size
        best_size = low

        while low <= high:
            mid = (low + high) // 2
            font.setPointSize(mid)
            metrics = QFontMetrics(font)
            rect = metrics.tightBoundingRect(text)

            if rect.width() <= label_width and rect.height() <= label_height:
                if mid == 269:
                    print(rect.width(), rect.height(), label_width, label_height, text)
                best_size = mid
                low = mid + 1
            else:
                high = mid - 1
        return best_size

    def closeEvent(self, event):
        QApplication.restoreOverrideCursor()
        self.timer.stop()
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
