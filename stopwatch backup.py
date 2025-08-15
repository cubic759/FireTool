"""
#TODO task list
draw a logo,

edit task:
display remaining hours (increasing and decreasing), display project name in checklist
past over specific time and take a break,
edit task settings enrich,
add task link(start the default timer, and change to that task)

main:
move both list and timer
(snapping window seems buggy)

schedule content

fix checkbox range
fix hyperlink scrolled
snap parent windows to edge when popup addingwindow then move back

fix topbar bug and shrink error,
save and read settings (countdown time settings),

clear code,
fine position,

memo task: 按照即兴教程练习吉他、贝斯和键盘：选择一个和弦，然后唱出一段包含6-9个音符的旋律，然后在乐器上弹奏出来，换不同把位弹
"""

import time
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
    QGraphicsDropShadowEffect,
    QSizePolicy,
    QSpinBox,
    QTextEdit,
    QCheckBox,
    QToolTip,
    QButtonGroup,
    QMessageBox,
    QTimeEdit,
    QComboBox,
    QScrollArea,
    QFrame,
    QSpacerItem,
    QStyleOptionButton,
    QStyle,
    QLineEdit,
    QFileDialog,
)
from PyQt5.QtCore import (
    Qt,
    QPoint,
    QRect,
    QTimer,
    QSize,
    QEvent,
    QTime,
    pyqtSignal,
    QSizeF,
    QObject,
    QRectF,
)
from PyQt5.QtGui import (  # ANCHOR import
    QIcon,
    QColor,
    QFontDatabase,
    QFont,
    QFontMetrics,
    QCursor,
    QPainter,
    QTextCharFormat,
    QTextFormat,
    QTextObjectInterface,
    QTextCursor,
)
import time
import webbrowser
import os
import tldextract
from urllib.parse import urlparse
from enum import Enum


class SettingWindowTypes(Enum):  # ANCHOR enum
    TRANSPARENCY = 0
    TASK = 1
    DEFAULT = 2


class AddingWindowTypes(Enum):
    HYPERLINK = 0


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


class MyScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.verticalScrollBar().setMouseTracking(True)
        self.horizontalScrollBar().setMouseTracking(True)

        # Install event filters
        self.verticalScrollBar().installEventFilter(self)
        self.horizontalScrollBar().installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseMove:
            if obj == self.verticalScrollBar() or obj == self.horizontalScrollBar():
                QApplication.changeOverrideCursor(Qt.ArrowCursor)

        return super().eventFilter(obj, event)


class MyTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)

    def contextMenuEvent(self, event):
        QApplication.changeOverrideCursor(Qt.ArrowCursor)
        super().contextMenuEvent(event)

    def mouseMoveEvent(self, e):
        QApplication.changeOverrideCursor(Qt.IBeamCursor)
        super().mouseMoveEvent(e)


class MyButton(QPushButton):
    middleClicked = pyqtSignal()

    def __init__(self, parent=None, text=""):
        super().__init__(parent)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.middleClicked.emit()
        else:
            super().mouseReleaseEvent(event)


class DraggableButton(QPushButton):  # ANCHOR --DraggableButton
    rightClicked = pyqtSignal()
    wheelScrolled = pyqtSignal(str)
    dragged = pyqtSignal()

    def __init__(self, parent=None, text=""):
        super().__init__(parent)
        self.btnText = text
        self.isRightClicked = False
        self.dragging = False
        self.moved = False
        self.drag_start_pos = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.isRightClicked = True
            # self.rightClicked.emit()
            event.accept()
        elif event.button() == Qt.LeftButton:
            if not widget.window().isFullScreen():
                self.dragging = True
                self.drag_start_pos = event.globalPos()
            super().mousePressEvent(event)  # Still triggers clicked()

    def mouseMoveEvent(self, event):
        QApplication.changeOverrideCursor(Qt.ArrowCursor)
        if self.dragging and not widget.window().isFullScreen():
            delta = event.globalPos() - self.drag_start_pos
            self.window().move(self.window().pos() + delta)
            self.drag_start_pos = event.globalPos()
            self.moved = True
            self.dragged.emit()

    def mouseReleaseEvent(self, event):
        self.dragging = False
        if self.moved:
            event.ignore()
            self.moved = False
            self.setDown(False)  # Reset pressed state
            self.clearFocus()  # Optional: clear focus if stuck
            self.update()
        else:
            if self.isRightClicked and not widget.window().isFullScreen():
                self.rightClicked.emit()
                self.isRightClicked = False
                event.accept()
            else:
                super().mouseReleaseEvent(event)

    def wheelEvent(self, a0):
        delta = a0.angleDelta().y()
        if delta > 0:
            self.wheelScrolled.emit("up")
        elif delta < 0:
            self.wheelScrolled.emit("down")
        a0.accept()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.btnText != "":
            painter = QPainter(self)
            metrics = QFontMetrics(self.font())
            text = self.btnText
            rect = self.rect()
            text_width = metrics.horizontalAdvance(text)
            text_height = metrics.height()
            painter.drawText(
                (rect.width() - text_width) // 2,
                (rect.height() + text_height) // 2 - metrics.descent(),
                text,
            )


class Addings(QWidget):  # ANCHOR --Addings
    def __init__(self, typeValue, callback=None, data=None, parent=None):
        super().__init__(parent)
        self.callback = callback
        self.typeValue = typeValue
        self.setWindowFlags(
            Qt.Tool
        )  # | Qt.Window | Qt.CustomizeWindowHint| Qt.FramelessWindowHint| Qt.WindowStaysOnTopHint
        self.setMouseTracking(True)

        layout = QVBoxLayout(self)

        if self.typeValue == AddingWindowTypes.HYPERLINK.value:  # ANCHOR adding window
            if data:
                pass
            else:
                self.selectedIndex = 1
                self.textLineNumber = 0
                self.urlLineNumber = 0
                self.textLastContained = ""
                self.texts = []
                self.urls = []
                self.setWindowTitle("Add hyperlink")
                self.setFixedSize(500, 600)
                self.label1 = QLabel("<b>Text(lines:0):</b>")
                self.text = QTextEdit()
                self.text.textChanged.connect(self.onTextChanged)
                self.label2 = QLabel("<b>Type:</b>")
                self.combo1 = QComboBox()
                self.textList = ["Task", "Websites", "Single Local Folder/File"]
                self.combo1.addItems(self.textList)
                """if data["value"] in self.valueList:
                    self.combo.setCurrentIndex(self.valueList.index(data["value"]) + 1)
                else:"""
                self.combo1.setCurrentIndex(1)

                self.combo1.currentIndexChanged.connect(self.on_changed)
                self.label3 = QLabel("<b>Link to(lines:0):</b>")
                self.url = QTextEdit()
                self.url.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                self.url.textChanged.connect(self.onUrlChanged)
                self.fileButton = QPushButton("📄")
                self.fileButton.hide()
                self.fileButton.setFixedWidth(30)
                self.fileButton.clicked.connect(self.openFileExplorer)
                self.folderButton = QPushButton("📁")
                self.folderButton.setFixedWidth(30)
                self.folderButton.hide()
                self.folderButton.clicked.connect(self.openFolderExplorer)
                hlayout = QHBoxLayout()
                hlayout.setContentsMargins(0, 0, 0, 0)
                hlayout.setSpacing(2)
                hlayout.addWidget(self.url, stretch=3)
                hlayout.addWidget(self.folderButton, stretch=0)
                hlayout.addWidget(self.fileButton, stretch=0)
                self.combo2 = QComboBox()
                self.combo2.hide()
                # self.checkbox = QCheckBox("Full screen lock to 100%")
                # self.checkbox.setChecked(data["flag"])
                self.ok_button = DraggableButton(text="OK")

                self.ok_button.clicked.connect(self.return_value)

                layout.addWidget(self.label2)
                layout.addWidget(self.combo1)
                layout.addWidget(self.label3)
                layout.addLayout(hlayout)
                layout.addWidget(self.combo2)
                layout.addWidget(self.label1)
                layout.addWidget(self.text)
                layout.addWidget(self.ok_button)

    def on_changed(self, index):
        self.selectedIndex = index
        if index == 0:
            self.combo2.show()
            self.url.hide()
            self.fileButton.hide()
            self.folderButton.hide()
            currentText = self.combo2.currentText()
            self.text.setText("Task: " + currentText)
            """self.time_edit.blockSignals(True)
            self.time_edit.setTime(QTime(0, 0, 0).addSecs(self.valueList[index - 1]))
            self.time_edit.blockSignals(False)"""
        elif index == 1:
            self.combo2.hide()
            self.url.show()
            self.fileButton.hide()
            self.folderButton.hide()
        elif index == 2:
            self.combo2.hide()
            self.url.show()
            self.fileButton.show()
            self.folderButton.show()

    def onUrlChanged(self):  # ANCHOR onUrlChanged
        self.urls = self.get_clean_lines(self.url)
        self.urlLineNumber = len(self.urls)
        self.label3.setText(f"<b>Link to(lines:{self.urlLineNumber}):</b>")
        if (
            self.selectedIndex == 1
            and self.text.toPlainText() == self.textLastContained
        ):
            self.domains = []
            for url in self.urls:
                ext = tldextract.extract(url)
                self.domains.append(f"{ext.domain}.{ext.suffix}")
            if self.textLastContained != "":
                self.domains.insert(0, self.textLastContained)
            self.textLastContained = "\n".join(self.domains)
            self.text.setText(self.textLastContained)

    def onTextChanged(self):
        self.texts = self.get_clean_lines(self.text)
        self.textLineNumber = len(self.texts)
        self.label1.setText(f"<b>Text(lines:{self.textLineNumber}):</b>")

    def openFileExplorer(self):
        # Open file dialog and get file path
        file_path, _ = QFileDialog.getOpenFileName(None, "Select a File")

        if file_path:
            url = "\n".join([self.url.toPlainText(), file_path])
            self.url.setText(url)
            filename = os.path.basename(file_path)
            text = "\n".join([self.text.toPlainText(), filename])
            if self.text.toPlainText() == self.textLastContained:
                self.textLastContained = text
            self.text.setText(text)

    def openFolderExplorer(self):
        # Open folder dialog and get folder path
        folder_path = QFileDialog.getExistingDirectory(None, "Select a Folder")

        if folder_path:
            url = "\n".join([self.url.toPlainText(), folder_path])
            self.url.setText(url)
            foldername = os.path.basename(folder_path)
            text = "\n".join([self.text.toPlainText(), "/" + foldername])
            if self.text.toPlainText() == self.textLastContained:
                self.textLastContained = text
            self.text.setText(text)

    def get_clean_lines(self, textEdit):
        text = textEdit.toPlainText()
        lines = [line for line in text.splitlines() if line.strip()]
        strList = "\n".join(lines)
        return strList.splitlines()

    def enterEvent(self, event):
        super().enterEvent(event)
        QApplication.changeOverrideCursor(Qt.ArrowCursor)

    def leaveEvent(self, a0):
        super().leaveEvent(a0)

    def return_value(self):  # ANCHOR Return value
        if self.typeValue == AddingWindowTypes.HYPERLINK.value:
            if self.urlLineNumber != self.textLineNumber:
                QMessageBox.warning(
                    self,
                    "Length Mismatch",
                    "The number of urls and texts do not match.",
                    QMessageBox.Ok,
                )
                return
            combined = []

            for i in range(self.urlLineNumber):
                combined.append([self.urls[i], self.texts[i]])  # One list per item
            data = {
                "value": combined,
                # "flag": None,
            }

        self.callback(data)

        self.close()


class CheckBoxTextObject(QObject, QTextObjectInterface):
    ObjectType = QTextFormat.UserObject + 1

    def __init__(self, parent=None):
        super().__init__(parent)
        self.checkbox_states = {}

    def drawObject(self, painter, rect, doc, posInDocument, format):
        key = format.property(1)
        checked = self.checkbox_states.get(key, False)
        style = QApplication.style()

        option = QStyleOptionButton()
        option.rect = rect.toRect()
        option.state = QStyle.State_Enabled
        option.state |= QStyle.State_On if checked else QStyle.State_Off

        checkbox_size = style.sizeFromContents(
            QStyle.CT_CheckBox, option, QSize(), None
        )

        # Align checkbox to font baseline
        font = doc.defaultFont()
        metrics = QFontMetrics(font)
        ascent = metrics.ascent()

        # Compute vertical offset to baseline
        y_offset = rect.y() + (ascent - checkbox_size.height() / 2) - 2

        # Horizontal center
        x = rect.x() + (rect.width() - checkbox_size.width()) / 2

        option.rect = QRectF(
            x, y_offset, checkbox_size.width(), checkbox_size.height()
        ).toRect()

        style.drawControl(QStyle.CE_CheckBox, option, painter)

    def intrinsicSize(self, doc, posInDocument, format):
        font = doc.defaultFont()
        metrics = QFontMetrics(font)
        return QSizeF(metrics.height(), metrics.height())

    def toggle(self, key):
        self.checkbox_states[key] = not self.checkbox_states.get(key, False)


class CustomTextEdit(QTextEdit):  # ANCHOR --CustomTextEdit
    def __init__(self):
        super().__init__()
        self.setAcceptRichText(True)  # Allow HTML for hyperlink
        self.setMouseTracking(True)
        self._last_cursor_shape = None
        self.hyperlink_rects = []
        self.data = []
        self.checkbox_obj = CheckBoxTextObject(self)
        self.addingWindowStatus = [False] * len(AddingWindowTypes)
        self.popup = [None] * len(
            AddingWindowTypes
        )  # Addings(self.handleTasks, data, 1)
        self.document().documentLayout().registerHandler(
            CheckBoxTextObject.ObjectType, self.checkbox_obj
        )
        self.document().setDefaultStyleSheet("""
            a {
                color: aqua; 
                text-decoration: none;
            }
        """)

        self.insertTextWithCheckbox("Task 1", "cb1")
        self.append("")
        self.insertTextWithCheckbox("Task 2", "cb2")
        self.append("")  # Add spacing
        self.insertHyperlink("https://www.youtube.com/", "Open YouTube")
        self.append("")  # Add spacing
        self.insertHyperlink("https://www.bing.com/", "Open bing")
        self.append("")  # Add spacing
        self.insertTextWithCheckbox("", "cb3")
        self.insertHyperlink("https://www.baidu.com/", "Open baidu")
        # self._suppress_html_update = False
        self.document().contentsChanged.connect(self.onContentChanged)

    def addHyperLink(self):  # ANCHOR addHyperlink
        if not self.addingWindowStatus[AddingWindowTypes.HYPERLINK.value]:
            data = None
            """{
                "value": self.transparency,
                "flag": self.fullScreenLocked,
            }"""
            self.popup[AddingWindowTypes.HYPERLINK.value] = Addings(
                AddingWindowTypes.HYPERLINK.value,
                self.handleHyperlinkData,
                data,
            )
            self.popup[AddingWindowTypes.HYPERLINK.value].setWindowFlags(Qt.Tool)
            self.popup[AddingWindowTypes.HYPERLINK.value].show()
            self.popup[AddingWindowTypes.HYPERLINK.value].activateWindow()
            self.addingWindowStatus[AddingWindowTypes.HYPERLINK.value] = True
        else:
            self.popup[AddingWindowTypes.HYPERLINK.value].activateWindow()

    def handleHyperlinkData(self, data):
        combined = data["value"]
        for i in range(len(combined)):
            self.insertHyperlink(combined[i][0], combined[i][1])
            if i != len(combined) - 1:
                self.append("")  # Add spacing
        self.onContentChanged()
        self.addingWindowStatus[AddingWindowTypes.HYPERLINK.value] = False

    def insertCheckbox(self):
        cursor = self.textCursor()
        fmt = QTextCharFormat()
        fmt.setObjectType(CheckBoxTextObject.ObjectType)
        fmt.setProperty(1, cursor.position())
        cursor.insertText("\ufffc", fmt)

    def onContentChanged(self):  # ANCHOR onContentChanged
        self.hyperlink_rects = []
        self.data = []
        doc = self.document()
        block = doc.begin()
        cursor = QTextCursor(doc)

        while block.isValid():
            line_items = []
            it = block.begin()
            while not it.atEnd():
                frag = it.fragment()
                if frag.isValid():
                    fmt = frag.charFormat()
                    text = frag.text()
                    if fmt.objectType() == CheckBoxTextObject.ObjectType:
                        key = fmt.property(1)
                        checkbox_state = self.checkbox_obj.checkbox_states.get(
                            key, False
                        )
                        line_items.append(checkbox_state)

                    elif fmt.isAnchor():
                        url = fmt.anchorHref()
                        line_items.append((text, url))

                        start = frag.position()
                        end = start + frag.length()
                        rect = None
                        for i in range(start, end + 1):
                            cursor.setPosition(i)
                            char_rect = self.cursorRect(cursor)
                            if rect is None:
                                rect = char_rect
                            else:
                                rect = rect.united(char_rect)
                        if rect:
                            self.hyperlink_rects.append((rect, start, text, url))
                    else:
                        line_items.append(text)

                it += 1
            self.data.append(line_items)
            block = block.next()

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self.onContentChanged)

    def insertHyperlink(self, url, text=None):
        if text is None:
            text = url
        cursor = self.textCursor()
        cursor.insertHtml(
            f'<a href="{url}">{text}</a>'
        )

    def insertTextWithCheckbox(self, text, key):
        cursor = self.textCursor()
        fmt = QTextCharFormat()
        fmt.setObjectType(CheckBoxTextObject.ObjectType)
        fmt.setProperty(1, key)
        cursor.insertText("\ufffc", fmt)
        cursor.insertText(f" {text}")

    def insertFromMimeData(self, source):
        text = source.text()
        cursor = self.textCursor()

        for i, part in enumerate(text.split("- [ ] ")):
            if part:
                cursor.insertText(part)
            if i < text.count("- [ ] "):
                self.insert_checkbox(cursor)

    def insert_checkbox(self, cursor=None):
        if cursor is None:
            cursor = self.textCursor()

        fmt = QTextCharFormat()
        fmt.setObjectType(CheckBoxTextObject.ObjectType)
        key = str(cursor.position())
        fmt.setProperty(1, key)
        cursor.insertText('\uFFFC', fmt)

    def createMimeDataFromSelection(self):
        mime = super().createMimeDataFromSelection()
        text = mime.text()

        cursor = self.textCursor()
        doc = self.document()
        selection_start = cursor.selectionStart()
        selection_end = cursor.selectionEnd()

        cursor.setPosition(selection_start)
        plain_text = ''

        while cursor.position() < selection_end:
            cursor.movePosition(cursor.Right, cursor.KeepAnchor)
            char = cursor.selectedText()

            fmt = cursor.charFormat()
            if fmt.objectType() == CheckBoxTextObject.ObjectType:
                plain_text += "- [ ] "
            else:
                plain_text += char

            cursor.clearSelection()

        mime.setText(plain_text)
        return mime


    def mousePressEvent(self, event):  # ANCHOR mouseEvent
        if event.pos().y() <= 5:
            return  # Ignore clicks within top 2 pixels
        cursor = self.cursorForPosition(event.pos())
        fmt = cursor.charFormat()
        if fmt.objectType() == CheckBoxTextObject.ObjectType:
            key = fmt.property(1)
            self.checkbox_obj.toggle(key)
            self.onContentChanged()
            self.viewport().update()
            return
        elif fmt.isAnchor():
            for min_rect, _, _, _ in self.hyperlink_rects:
                if min_rect.contains(event.pos()):
                    return
                else:
                    self.blink_cursor_now()
        else:
            self.blink_cursor_now()

        super().mousePressEvent(event)

    def blink_cursor_now(self):
        cursor = self.textCursor()
        if cursor.atEnd():
            # Temporarily hide and show the cursor
            cursor.movePosition(QTextCursor.Right)
            self.setTextCursor(cursor)
        else:
            # Reset blink by moving right and back
            cursor.movePosition(QTextCursor.Right)
            cursor.movePosition(QTextCursor.Left)
            self.setTextCursor(cursor)

    def mouseDoubleClickEvent(self, event):
        if event.pos().y() <= 5:
            return  # Ignore clicks within top 2 pixels
        # Avoid text selection on double-click on checkbox
        cursor = self.cursorForPosition(event.pos())
        fmt = cursor.charFormat()
        if fmt.objectType() == CheckBoxTextObject.ObjectType:
            key = fmt.property(1)
            self.checkbox_obj.toggle(key)
            self.onContentChanged()
            self.viewport().update()
            return
        super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event):
        if event.pos().y() <= 5:
            return  # Ignore clicks within top 2 pixels
        if event.buttons():  # Don't interfere with drag selection
            super().mouseMoveEvent(event)
            return
        cursor = self.cursorForPosition(event.pos())
        fmt = cursor.charFormat()

        if fmt.objectType() == CheckBoxTextObject.ObjectType:
            QApplication.changeOverrideCursor(Qt.PointingHandCursor)
            super().mouseMoveEvent(event)
            return

        # Dynamically check if mouse is inside a current hyperlink region
        hovered = False
        for min_rect, _, _, _ in self.hyperlink_rects:
            if min_rect.contains(event.pos()):
                hovered = True
                break

        new_cursor = Qt.PointingHandCursor if hovered else Qt.IBeamCursor
        QApplication.changeOverrideCursor(new_cursor)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        for min_rect, start, text, url in self.hyperlink_rects:
            if min_rect.contains(event.pos()):
                if event.button() == Qt.LeftButton:
                    if url.startswith("http://") or url.startswith("https://"):
                        webbrowser.open(url)
                    elif url.startswith("Task:"):
                        pass
                    else:
                        os.startfile(url)
                    return  # Prevent default behavior
                else:
                    print(start, text, url)
                    # event.accept()
                    return

        super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event):
        QApplication.changeOverrideCursor(Qt.ArrowCursor)
        for min_rect, _, _, _ in self.hyperlink_rects:
            if min_rect.contains(event.pos()):
                return
        super().contextMenuEvent(event)
        
    def deleteHyperlinkFragment(self, backward=True):
        cursor = self.textCursor()
        pos = cursor.position()
    
        if backward and pos == 0:
            return  # Nothing to delete before start
    
        check_pos = pos - 1 if backward else pos
        doc = self.document()
        block = doc.findBlock(check_pos)
    
        it = block.begin()
        while not it.atEnd():
            frag = it.fragment()
            if frag.contains(check_pos):
                if frag.charFormat().isAnchor():
                    start = frag.position()
                    end = start + frag.length()
    
                    temp_cursor = QTextCursor(doc)
                    temp_cursor.setPosition(start)
                    temp_cursor.setPosition(end, QTextCursor.KeepAnchor)
                    temp_cursor.removeSelectedText()
                    return True  # Deleted
            it += 1
        return False  # Not deleted



    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Backspace:
            if self.deleteHyperlinkFragment(backward=True):
                return
        elif event.key() == Qt.Key_Delete:
            if self.deleteHyperlinkFragment(backward=False):
                return
        else:
            cursor = self.textCursor()
            fmt = cursor.charFormat()
            if fmt.isAnchor():
                plain_fmt = QTextCharFormat()
                cursor.setCharFormat(plain_fmt)
                self.setTextCursor(cursor)

        super().keyPressEvent(event)


class Settings(QWidget):  # ANCHOR --Settings
    def __init__(self, callback, data, typeValue, parent=None):
        super().__init__(parent)
        self.callback = callback
        self.typeValue = typeValue
        self.setWindowFlags(
            Qt.Tool | Qt.WindowStaysOnTopHint
        )  # | Qt.Window | Qt.CustomizeWindowHint| Qt.FramelessWindowHint
        self.setMouseTracking(True)

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
            self.ok_button = DraggableButton(text="OK")

            self.ok_button.clicked.connect(self.return_value)

            layout.addWidget(self.label)
            layout.addWidget(self.spinbox)
            layout.addWidget(self.checkbox)
            layout.addWidget(self.ok_button)
        elif self.typeValue == SettingWindowTypes.TASK.value:
            self.setWindowTitle("Set Task")
            self.setFixedSize(500, 300)
            self.label = QLabel("<b>Input your task: (First line for idle state)</b>")
            self.text = QTextEdit()

            self.text.setText("\n".join(data["value"]))
            self.text.setMouseTracking(True)
            self.checkbox = QCheckBox("random display when started")
            self.checkbox.setChecked(data["flag"])
            self.ok_button = DraggableButton(text="OK")

            self.ok_button.clicked.connect(self.return_value)

            layout.addWidget(self.label)
            layout.addWidget(self.text)
            layout.addWidget(self.checkbox)
            layout.addWidget(self.ok_button)
        elif self.typeValue == SettingWindowTypes.DEFAULT.value:
            self.setWindowTitle("Set Default")
            self.setFixedSize(250, 150)
            self.label = QLabel("<b>Default countdown time:</b>")
            self.combo = QComboBox()
            self.textList = [
                "Custom",
                "10min",
                "20min",
                "30min",
                "1h",
                "1h 30min",
                "2h",
            ]
            self.valueList = [600, 1200, 1800, 3600, 5400, 7200]
            self.combo.addItems(self.textList)
            if data["value"] in self.valueList:
                self.combo.setCurrentIndex(self.valueList.index(data["value"]) + 1)
            else:
                self.combo.setCurrentIndex(0)

            self.combo.currentIndexChanged.connect(self.on_changed)

            self.time_edit = QTimeEdit()
            self.time_edit.setDisplayFormat("HH:mm:ss")

            self.time_edit.setMinimumTime(QTime(0, 0, 1))
            self.time_edit.setMaximumTime(QTime(999, 59, 0))
            self.time_edit.setTime(
                QTime(0, 0, 0).addSecs(data["value"])
            )  # Default time
            self.time_edit.timeChanged.connect(self.on_time_changed)

            self.time_edit.setMouseTracking(True)
            # self.favorite_value = None  # stored favorite

            self.fav_btn = QPushButton("☆")  # hollow star (can use emoji or icon)
            self.fav_btn.setFixedWidth(30)
            self.fav_btn.clicked.connect(self.on_favorite_clicked)

            # Layout
            hbox = QHBoxLayout()
            hbox.addWidget(self.time_edit)
            hbox.addWidget(self.fav_btn)
            hbox.setContentsMargins(0, 0, 0, 0)
            hbox.setSpacing(4)

            self.checkbox = QCheckBox("Default control stopwatch")
            self.checkbox.setChecked(data["flag"])
            self.ok_button = DraggableButton(text="OK")

            self.ok_button.clicked.connect(self.return_value)
            # print("ok")
            layout.addWidget(self.label)
            layout.addWidget(self.combo)
            layout.addLayout(hbox)
            layout.addWidget(self.checkbox)
            layout.addWidget(self.ok_button)
        # self.setLayout(layout)

    def on_changed(self, index):
        if index > 0:
            self.time_edit.blockSignals(True)
            self.time_edit.setTime(QTime(0, 0, 0).addSecs(self.valueList[index - 1]))
            self.time_edit.blockSignals(False)

    def on_time_changed(self, time):
        seconds = QTime(0, 0, 0).secsTo(time)
        self.combo.blockSignals(True)
        if seconds in self.valueList:
            self.combo.setCurrentIndex(self.valueList.index(seconds) + 1)
        else:
            self.combo.setCurrentIndex(0)
        self.combo.blockSignals(False)

    def on_favorite_clicked(self):
        currentText = self.combo.currentText()
        currentIndex = self.combo.currentIndex()
        currentTime = QTime(0, 0, 0).secsTo(self.time_edit.time())

        if currentText != "Custom" and self.valueList[currentIndex - 1] == currentTime:
            # remove favorite
            index = self.combo.findText(currentText)
            if index != -1:
                self.combo.blockSignals(True)
                self.combo.removeItem(index)
                self.combo.setCurrentIndex(0)
                self.textList.remove(currentText)
                self.valueList.remove(currentTime)
                self.combo.blockSignals(False)
                self.fav_btn.setText("☆")
        else:
            # Save favorite
            import bisect

            index = bisect.bisect_left(self.valueList, currentTime)
            self.valueList.insert(index, currentTime)
            text = self.time_to_text(currentTime)
            self.textList.insert(index + 1, text)
            self.combo.insertItem(index + 1, text)  # insert at index
            self.combo.setCurrentIndex(index + 1)
            self.fav_btn.setText("★")  # filled star

    def time_to_text(self, value) -> str:
        if isinstance(value, QTime):
            total_seconds = QTime(0, 0).secsTo(value)
        elif isinstance(value, int):
            total_seconds = value
        else:
            raise TypeError("Argument must be QTime or int")

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}min")
        if seconds > 0 and hours == 0:  # only show seconds if <1h
            parts.append(f"{seconds}s")

        return " ".join(parts) if parts else "0s"

    """def text_to_qtime(text: str) -> QTime:
        hours = minutes = seconds = 0
        # Use regex to find time components
        match_h = re.search(r'(\d+)\s*h', text)
        match_m = re.search(r'(\d+)\s*min', text)
        match_s = re.search(r'(\d+)\s*s', text)

        if match_h:
            hours = int(match_h.group(1))
        if match_m:
            minutes = int(match_m.group(1))
        if match_s:
            seconds = int(match_s.group(1))

        return QTime(hours, minutes, seconds)"""

    def enterEvent(self, event):
        super().enterEvent(event)
        QApplication.changeOverrideCursor(Qt.ArrowCursor)

    def leaveEvent(self, a0):
        super().leaveEvent(a0)

    def return_value(self):  # ANCHOR ReturnValue
        if self.typeValue == SettingWindowTypes.TRANSPARENCY.value:
            data = {
                "value": self.spinbox.value() / 100.0,
                "flag": self.checkbox.isChecked(),
            }
        elif self.typeValue == SettingWindowTypes.TASK.value:
            data = {
                "value": self.text.toPlainText().split("\n"),
                "flag": self.checkbox.isChecked(),
            }
        elif self.typeValue == SettingWindowTypes.DEFAULT.value:
            current_time = self.time_edit.time()
            seconds = QTime(0, 0, 0).secsTo(current_time)
            data = {
                "value": seconds,
                "flag": self.checkbox.isChecked(),
            }
        self.callback(data)

        self.close()


class CheckList(QWidget):  # ANCHOR --CheckList
    hided = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.DOCK_POSITIONS = [
            "top-right",
            "right",
            "bottom-right",
            "bottom",
            "bottom-left",
            "left",
            "top-left",
            "top",
        ]

        self.isDocking = False
        self.dockIndex = 0
        self.originalPos = None
        self.lastPos = None
        self.transparency = 0.8
        self.task_index = 0
        self.tasks = ["Take a break", "Drawing", "Music", "Modeling"]
        self.functionIcon = ["📅", "🌐", "✅", "📋"]
        self.controlIcons = [
            QIcon("add bold white.svg"),
            QIcon("close bold white.svg"),
        ]
        self.function_buttons = []
        self.control_buttons = []
        self.functionIndex = 2
        self.is_dragging = False

        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self.resize(240, 300)  # 130 60
        self.setWindowOpacity(self.transparency)
        self.setMinimumSize(40, 20)
        self.wrapper = QWidget(self)
        self.wrapper.setObjectName("mainContainer")
        self.wrapper.setMouseTracking(True)
        self.wrapper.setStyleSheet(
            "QWidget#mainContainer {background-color: rgb(30, 30, 30); border-radius: 5px; border: 1px solid rgb(80, 80, 80);}"
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
        self.top_widget = QWidget()
        # self.top_widget.setStyleSheet("border: 2px solid red;")
        # self.top_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        # self.top_widget.setFixedWidth(120)
        self.top_widget.setMouseTracking(True)
        self.top_widget.resize(220, 16)

        font_id = QFontDatabase.addApplicationFont("Roboto-Regular.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.font = QFont(font_family)
        self.font.setPointSize(10)

        self.center_widget = QWidget()
        # self.center_widget.setStyleSheet("border: 2px solid red;")
        self.center_widget.setProperty("class", "outer")
        self.center_widget.setStyleSheet(
            """QWidget[class="outer"] {border-top: 1px solid rgb(80, 80, 80);border-bottom: 1px solid rgb(80, 80, 80);}"""
        )
        self.center_widget.setMouseTracking(True)
        self.center_widget.resize(220, 50)

        self.bottom_widget = QWidget()
        # self.bottom_widget.setStyleSheet("border: 2px solid red;")
        self.bottom_widget.setMouseTracking(True)
        self.bottom_widget.resize(220, 24)

        self.main_layout = QVBoxLayout(self.wrapper)

        layout = QHBoxLayout(self.top_widget)
        layout.setContentsMargins(1, 1, 1, 1)  # No padding around the edges
        layout.setSpacing(0)  # No spacing between widgets

        leftLayout = QHBoxLayout()
        leftLayout.setContentsMargins(0, 0, 0, 0)  # No padding around the edges
        leftLayout.setSpacing(0)  # No spacing between widgets

        rightLayout = QHBoxLayout()
        rightLayout.setContentsMargins(0, 0, 0, 0)  # No padding around the edges
        rightLayout.setSpacing(0)  # No spacing between widgets

        oLayout = QVBoxLayout(self.center_widget)
        oLayout.setContentsMargins(1, 1, 1, 1)  # No padding around the edges
        oLayout.setSpacing(0)

        # ANCHOR toolbar

        self.toolbarContainer = QWidget()
        self.toolbarContainer.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )
        self.toolbarContainer.setStyleSheet("border-bottom:1px solid rgb(80,80,80);")
        self.toolbarContainer.setFixedHeight(25)
        self.toolbarContainer.setMouseTracking(True)

        self.toolBarLayout = QHBoxLayout(self.toolbarContainer)
        self.toolBarLayout.setContentsMargins(0, 0, 0, 0)  # No padding around the edges
        self.toolBarLayout.setSpacing(0)

        self.checkboxBtn = DraggableButton(self.toolbarContainer, "✅")
        self.checkboxBtn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        self.checkboxBtn.setMouseTracking(True)
        self.checkboxBtn.setFixedWidth(25)
        self.checkboxBtn.setProperty("class", "toolbar")
        # checkboxBtn.middleClicked.connect(self.deleteClip)
        self.checkboxBtn.setStyleSheet(
            """
            QPushButton[class="toolbar"]{
                background-color: rgb(30, 30, 30);
                color: white;
                line-height: 100%;
                text-align: center;
                border:1px solid rgb(80, 80, 80);
                border-left:0px;
                border-top:0px;
            }
            QPushButton[class="toolbar"]:hover{
                background:#333;
            }
            QPushButton[class="toolbar"]:pressed{
                background:#555;
            }
        """
        )
        self.addBtn = DraggableButton(self.toolbarContainer, "➕")

        self.addBtn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.addBtn.setMouseTracking(True)
        self.addBtn.setFixedWidth(25)
        self.addBtn.setProperty("class", "toolbar")
        # addBtn.middleClicked.connect(self.deleteClip)
        self.addBtn.setStyleSheet(
            """
            QPushButton[class="toolbar"]{
                background-color: rgb(30, 30, 30);
                color: white;
                line-height: 100%;
                text-align: center;
                border:1px solid rgb(80, 80, 80);
                border-left:0px;
                border-top:0px;
            }
            QPushButton[class="toolbar"]:hover{
                background:#333;
            }
            QPushButton[class="toolbar"]:pressed{
                background:#555;
            }
        """
        )
        self.toolBarLayout.addWidget(self.checkboxBtn)
        self.toolBarLayout.addWidget(self.addBtn)
        # self.toolBarLayout.addWidget(self.toolbarContainer)
        self.toolBarLayout.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )
        oLayout.addWidget(self.toolbarContainer)
        self.checkList = CustomTextEdit()
        self.checkList.setProperty("class", "checkList")
        self.checkList.setFont(self.font)
        self.checkList.setStyleSheet(
            """
            QTextEdit[class="checkList"]{
                background-color: rgb(30,30,30);
                color: white;
                border-bottom-left-radius: 5px; 
                border: 0px solid rgb(80, 80, 80);
                border-top:0px;
            }
            a {
                color: red;  /* or any color you want */
                text-decoration: underline;
            }
        """
        )
        oLayout.addWidget(self.checkList)

        self.checkboxBtn.clicked.connect(self.checkList.insertCheckbox)
        self.addBtn.clicked.connect(self.checkList.addHyperLink)
        # ANCHOR Scroll Area
        self.scroll_area = MyScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.verticalScrollBar().rangeChanged.connect(
            self.update_left_margin
        )
        self.scroll_area.verticalScrollBar().valueChanged.connect(
            self.update_left_margin
        )

        # Container widget inside scroll area
        self.clipboardContainer = QWidget()
        self.clipboardContainer.setMouseTracking(True)
        self.clipboardLayout = QVBoxLayout(self.clipboardContainer)
        self.clipboardLayout.setContentsMargins(8, 0, 0, 0)
        self.clipboardLayout.setSpacing(0)

        # Add buttons
        self.clipboardText = ["self.", "window", "widget"]
        for i in range(20):
            btn = MyButton()
            if i < len(self.clipboardText):
                btn.setText(self.clipboardText[i])
            else:
                btn.setText("self.")
            btn.clicked.connect(self.copy)
            btn.setFont(self.font)
            btn.setMouseTracking(True)
            btn.setProperty("class", "clip")
            btn.middleClicked.connect(self.deleteClip)
            btn.setStyleSheet(
                """
                QPushButton[class="clip"]{
                    text-align:left;
                    padding:4px;
                    background:transparent;
                    color:white;
                }
                QPushButton[class="clip"]:hover{
                    background:#333;
                }
                QPushButton[class="clip"]:pressed{
                    background:#555;
                }
            """
            )
            self.clipboardLayout.addWidget(btn, alignment=Qt.AlignTop)
        self.clipboardLayout.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

        self.clipboardContainer.setLayout(self.clipboardLayout)
        self.scroll_area.setProperty("class", "scroll")
        self.scroll_area.setMouseTracking(True)
        self.clipboardContainer.setStyleSheet(
            """
            QWidget {
                background-color: rgb(30, 30, 30);
                color: white;
        }"""
        )
        self.scroll_area.setViewportMargins(0, 0, 0, 0)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet(
            """
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                margin: 0px;
            }

            QScrollBar::handle:vertical {
                background: white;
                min-height: 10px;
                border-radius: 4px;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }

            QScrollBar:horizontal {
                background: transparent;
                height: 12px;
                margin: 0px;
            }

            QScrollBar::handle:horizontal {
                background: black;
                min-width: 20px;
                border-radius: 6px;
            }

            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                width: 0px;
            }

            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {
                background: transparent;
        }
        """
        )
        self.scroll_area.setWidget(self.clipboardContainer)

        # Add scroll area to main layout
        oLayout.addWidget(self.scroll_area)
        # ANCHOR addClip
        addClipLayout = QHBoxLayout(self.bottom_widget)
        addClipLayout.setContentsMargins(0, 0, 0, 0)  # No padding around the edges
        addClipLayout.setSpacing(0)  # No spacing between widgets
        self.clip_input = MyTextEdit()
        self.clip_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.clip_input.setProperty("class", "addClipText")
        self.clip_input.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.clip_input.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.clip_input.setFont(self.font)

        self.clip_input.setStyleSheet(
            """
            QTextEdit[class="addClipText"]{
                background-color: rgb(30,30,30);
                color: white;
                border-bottom-left-radius: 5px; 
                border: 1px solid rgb(80, 80, 80);
                border-top:0px;
            }
        """
        )
        self.addClip = QPushButton("Add")
        self.addClip.setFont(self.font)
        self.addClip.setMouseTracking(True)
        self.addClip.setProperty("class", "addClip")
        self.addClip.setStyleSheet(
            """
            QPushButton[class="addClip"]{
                background:transparent;
                color:white;
                border-bottom-right-radius: 5px; 
                border:0px 0px 1px 1px solid rgb(80, 80, 80);
            }
            QPushButton[class="addClip"]:hover{
                background:#333;
            }
            QPushButton[class="addClip"]:pressed{
                background:#555;
            }
        """
        )
        self.addClip.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.addClip.clicked.connect(self.addClips)
        addClipLayout.addWidget(self.clip_input, stretch=3)
        addClipLayout.addWidget(self.addClip, stretch=1)
        pushButtonStyle = """
            QPushButton[class="function"] {
                background-color: rgb(30, 30, 30);
                color: white;
                line-height: 100%;
                text-align: center;
                border-right:1px solid rgb(80, 80, 80);
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QPushButton[class="pos"] {
                background-color: rgb(29, 173, 245);
            }
            QPushButton[class="pos"]:hover {
                background-color: rgb(96, 200, 252);
            }
            QPushButton[class="pos"]:pressed {
                background-color: rgb(140, 213, 250);
            }
            QPushButton[class="pos"]:checked {
                background-color: rgb(140, 213, 250);
                border: 1px solid white;
            }
            QPushButton[class="control"] {
                background-color: rgb(30, 30, 30);
                color: white;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QPushButton:hover {
                background-color: #333;
            }
            QPushButton:pressed {
                background-color: #555;
            }
            
            QPushButton:checked {
                background-color: #555;
                border: 1px solid white;
            }
        """
        # ANCHOR function button
        group = QButtonGroup(self)
        group.setExclusive(True)
        group.buttonClicked[int].connect(self.functionAction)

        self.functionFont = QFont()
        for text in self.functionIcon:
            function_Button = DraggableButton(self.top_widget, text)
            # function_Button.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
            function_Button.setStyleSheet(pushButtonStyle)
            function_Button.setMouseTracking(True)
            function_Button.setCheckable(True)
            self.functionFont.setPointSize(12)
            function_Button.setProperty("class", "function")
            function_Button.setFont(self.functionFont)
            # function_Button.resize(40, 10)
            function_Button.setFixedWidth(52)
            function_Button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            function_Button.rightClicked.connect(self.functionRightClick)
            function_Button.wheelScrolled.connect(self.functionWheelScroll)
            function_Button.dragged.connect(self.functionDrag)
            # function_Button.setMaximumWidth(30)
            # function_Button.clicked.connect(self.functionAction)

            # function_label.setWordWrap(False)
            # function_label.setTextInteractionFlags(Qt.NoTextInteraction)

            # function_Button.adjustSize()
            self.function_buttons.append(function_Button)
            group.addButton(function_Button, self.functionIcon.index(text))
            leftLayout.addWidget(function_Button, stretch=2)

        for icon in self.controlIcons:
            control_Button = DraggableButton(self.top_widget)
            """if self.controlIcons.index(icon) == 0:
                control_Button.setIcon(icon[0])
                # control_Button.setStyleSheet("margin-left: 10px;")
            else:"""
            control_Button.setIcon(icon)
            # control_Button.resize(10,10)
            control_Button.setIconSize(QSize(20, 20))
            # control_Button.setMaximumWidth(30)
            # control_Button.setFixedWidth(20)
            control_Button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
            control_Button.clicked.connect(self.controlAction)
            control_Button.wheelScrolled.connect(self.functionWheelScroll)
            # function_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
            control_Button.setProperty("class", "control")
            control_Button.setStyleSheet(pushButtonStyle)
            control_Button.setMouseTracking(True)

            # function_label.setWordWrap(False)
            # function_label.setTextInteractionFlags(Qt.NoTextInteraction)

            # control_Button.adjustSize()
            self.control_buttons.append(control_Button)
            rightLayout.addWidget(control_Button, stretch=0)

        layout.addLayout(leftLayout)
        layout.addStretch()
        layout.addLayout(rightLayout)

        """self.functionRButton = QPushButton(">", self.wrapper)
        self.functionRButton.setStyleSheet(pushButtonStyle)
        self.functionRButton.setMouseTracking(True)
        self.functionRButton.clicked.connect(self.nextFunction)

        self.functionLButton = QPushButton("<", self.wrapper)
        self.functionLButton.setStyleSheet(pushButtonStyle)
        self.functionLButton.setMouseTracking(True)
        self.functionLButton.clicked.connect(self.lastFunction)"""
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # No padding around the edges
        self.main_layout.setSpacing(0)  # No spacing between widgets

        self.main_layout.addWidget(
            self.top_widget, stretch=1
        )  # stretch = 0 Fixed height (like 50px)
        self.main_layout.addWidget(self.center_widget, stretch=2)  # Expands to fill
        self.main_layout.addWidget(
            self.bottom_widget, stretch=1
        )  # Fixed height (like 50px)

        """font_id = QFontDatabase.addApplicationFont("lcd_alarm.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

        self.font1 = QFont(font_family)"""

        # self.tooltip = FloatingTooltip(self.tasks[self.task_index], self)
        self.popup = [None] * len(
            SettingWindowTypes
        )  # Settings(self.handleTasks, data, 1)

        self.resizeContent()
        QApplication.setOverrideCursor(Qt.ArrowCursor)

        self.menu = QMenu(self)
        # self.menu.addAction("Start", self.toggle_timer)
        # self.menu.addAction("Reset", self.reset_timer)
        self.menu.addAction("Edit Tasks", self.editTasks)
        self.menu.addAction("Transparency", self.setTransparency)
        self.menu.addAction("Exit", QApplication.quit)

        self.functionIndex = 2
        self.functionAction(self.functionIndex)
        self.function_buttons[self.functionIndex].setChecked(True)

    """
    -------------------------------------------------------------
    events
    
    -------------------------------------------------------------
    """

    def update_left_margin(self):
        scrollbar = self.scroll_area.verticalScrollBar()
        visible = scrollbar.maximum() > 0  # scrollbar visible if max > 0
        right_margin = 0 if visible else 8
        margins = self.clipboardLayout.contentsMargins()
        if margins.right() != right_margin:
            self.clipboardLayout.setContentsMargins(
                margins.left(), margins.top(), right_margin, margins.bottom()
            )

    def deleteClip(self):
        self.clipboardLayout.removeWidget(self.sender())
        self.clipboardContainer.adjustSize()

    def showEvent(self, event):
        self.clip_input.activateWindow()
        self.clip_input.setFocus()

        super().showEvent(event)

    def addClips(self):  # ANCHOR addClip function
        text = self.clip_input.toPlainText()
        if text != "":
            displayText = text.splitlines()[0].lstrip()
            btn = MyButton()
            btn.setText(displayText)
            btn.clicked.connect(self.copy)
            btn.middleClicked.connect(self.deleteClip)
            btn.setFont(self.font)
            btn.setMouseTracking(True)
            btn.setProperty("class", "clip")
            btn.setProperty("data", text)
            btn.setStyleSheet(
                """
                    QPushButton[class="clip"]{
                        text-align:left;
                        padding:4px;
                        background:transparent;
                        color:white;
                    }
                    QPushButton[class="clip"]:hover{
                        background:#333;
                    }
                    QPushButton[class="clip"]:pressed{
                        background:#555;
                    }
                """
            )
            self.clipboardLayout.insertWidget(0, btn, alignment=Qt.AlignTop)
            self.clipboardContainer.adjustSize()
            self.clip_input.setText("")
        self.clip_input.activateWindow()
        self.clip_input.setFocus()

    def copy(self):
        button = self.sender()
        clipboard = QApplication.clipboard()
        data = button.property("data")
        if data:
            clipboard.setText(data)
        else:
            clipboard.setText(button.text())
        time.sleep(0.05)

    def functionDrag(self):
        self.clip_input.activateWindow()
        self.clip_input.setFocus()
        if self.isDocking:
            self.isDocking = False
            button = self.sender()
            button.setProperty("class", "function")
            button.style().unpolish(button)
            button.style().polish(button)

    def snap_to_nearest(self):
        screen = QApplication.primaryScreen().geometry()
        win_geo = widget.frameGeometry()
        center = win_geo.center()

        snap_points = [
            QPoint(screen.right() - win_geo.width(), screen.top()),  # 1: top-right
            QPoint(
                screen.right() - win_geo.width(), center.y() - win_geo.height() // 2
            ),  # 5: right
            QPoint(
                screen.right() - win_geo.width(), screen.bottom() - win_geo.height()
            ),  # 3: bottom-right
            QPoint(
                center.x() - win_geo.width() // 2, screen.bottom() - win_geo.height()
            ),  # 7: bottom
            QPoint(screen.left(), screen.bottom() - win_geo.height()),  # 2: bottom-left
            QPoint(screen.left(), center.y() - win_geo.height() // 2),  # 4: left
            QPoint(screen.left(), screen.top()),  # 0: top-left
            QPoint(center.x() - win_geo.width() // 2, screen.top()),  # 6: top
        ]

        def distance(p1: QPoint, p2: QPoint):
            return (p1.x() - p2.x()) ** 2 + (p1.y() - p2.y()) ** 2

        current_pos = win_geo.topLeft()
        distances = [distance(current_pos, pt) for pt in snap_points]
        nearest_index = distances.index(min(distances))

        # Move window
        widget.move(snap_points[nearest_index])

        # Store the index
        self.dockIndex = nearest_index  # You can access this later

    def functionWheelScroll(self, direction):
        button = self.sender()
        if (
            button == self.function_buttons[0]
            and not self.isFullScreen()
            and self.isDocking
        ):
            if direction == "up":
                self.dockIndex = (self.dockIndex - 1) % len(self.DOCK_POSITIONS)
            else:
                self.dockIndex = (self.dockIndex + 1) % len(self.DOCK_POSITIONS)

            self.lastPos = self.pos()
            self.dock_to_position(self.DOCK_POSITIONS[self.dockIndex])
            pos = self.pos()
            delta = pos - self.lastPos
            cursor_pos = QCursor.pos()
            QCursor.setPos(cursor_pos + QPoint(delta.x(), delta.y()))
        else:
            if direction == "up":
                if self.functionIndex > 0:
                    self.functionIndex -= 1
                    self.function_buttons[self.functionIndex].setChecked(True)
                    self.functionAction(self.functionIndex)
                # self.task_index = (self.task_index + 1) % len(self.tasks)
            else:
                if self.functionIndex < 3:
                    self.functionIndex += 1
                    self.function_buttons[self.functionIndex].setChecked(True)
                    self.functionAction(self.functionIndex)
                # self.task_index = (self.task_index - 1) % len(self.tasks)

    def functionRightClick(self):
        button = self.sender()
        if button == self.function_buttons[0] and not self.isFullScreen():
            if not self.isDocking:
                self.isDocking = True
                button.setProperty("class", "pos")
                button.style().unpolish(button)
                button.style().polish(button)
                # button.setObjectName("pos")
                # button.setStyleSheet("""#pos{border-bottom:2px solid rgb(29, 173, 245);background:transparent;}""")
                self.dockIndex = (self.dockIndex - 1) % len(self.DOCK_POSITIONS)
                self.originalPos = self.pos()
                self.lastPos = self.pos()
                self.snap_to_nearest()
                pos = self.pos()
                delta = pos - self.lastPos
                cursor_pos = QCursor.pos()
                QCursor.setPos(cursor_pos + QPoint(delta.x(), delta.y()))
            else:
                self.isDocking = False
                self.lastPos = self.pos()
                button.setProperty("class", "function")
                button.style().unpolish(button)
                button.style().polish(button)
                self.move(self.originalPos)
                pos = self.pos()
                delta = pos - self.lastPos
                cursor_pos = QCursor.pos()
                QCursor.setPos(cursor_pos + QPoint(delta.x(), delta.y()))

    def dock_to_position(self, position: str):
        screen = QApplication.primaryScreen().availableGeometry()
        w, h = self.width(), self.height()

        x = y = 0

        if "left" in position:
            x = screen.left()
        elif "right" in position:
            x = screen.right() - w
        else:  # center horizontally
            x = screen.left() + (screen.width() - w) // 2

        if "top" in position:
            y = screen.top()
        elif "bottom" in position:
            y = screen.bottom() - h
        else:  # center vertically
            y = screen.top() + (screen.height() - h) // 2

        self.move(x, y)

    def controlAction(self):
        index = self.control_buttons.index(self.sender())
        if index == len(self.control_buttons) - 1:
            self.hide()
        """funcIndex = 0
        if self.defaultStopwatch:
            if self.functionIndex == 0:
                funcIndex = 0
            else:
                funcIndex = 1
        else:
            if self.functionIndex == 1:
                funcIndex = 1
            else:
                funcIndex = 0
        if funcIndex == 0:
            if index == 0:
                # print("start")
                if not self.reducing and not self.pausedReducing and not self.running and not self.paused:
                    self.task_label.setText(self.getNextTask())
                if self.reducing:

                    self.pausedReducing = True
                    self.change_action_text("Pause", "Start")
                else:
                    self.time_label.show()
  
                    self.pausedReducing = False
                    # self.time_label.setStyleSheet("color: Lime; ")
                    self.change_action_text("Start", "Pause")

                self.reducing = not self.reducing
                if self.reducing:
                    self.sender().setIcon(self.controlIcons[0][1])
                    self.function_buttons[0].setChecked(True)
                    self.functionAction(0)
                else:
                    self.sender().setIcon(self.controlIcons[0][0])
            else:
                # print("reset")
                if not self.reducing and not self.pausedReducing:
                    self.reset_timer()
                else:
                    self.countdownTime = self.setCountdown
                    self.update_display()
                    self.resizeContent()
                    # self.change_action_text("Pause", "Start")
                    self.reducing = False
                    self.pausedReducing = False
                if not self.reducing and not self.pausedReducing and not self.running and not self.paused:
                    self.control_buttons[0].setIcon(self.controlIcons[0][0])

        else:
            if index == 0:
                # print("start")
                if not self.reducing and not self.pausedReducing and not self.running and not self.paused:
                    self.task_label.setText(self.getNextTask())
                self.toggle_timer()

                if self.running:
                    self.sender().setIcon(self.controlIcons[0][1])
                    self.function_buttons[1].setChecked(True)
                    self.functionAction(1)
                else:
                    self.sender().setIcon(self.controlIcons[0][0])
            else:
                # print("reset")
                
                if not self.running and not self.paused:
                    self.countdownTime = self.setCountdown
                    self.update_display()
                    self.resizeContent()
                    # self.change_action_text("Pause", "Start")
                    self.reducing = False
                    self.pausedReducing = False
                else:
                    self.reset_timer()
                if not self.reducing and not self.pausedReducing and not self.running and not self.paused:
                    self.control_buttons[0].setIcon(self.controlIcons[0][0])"""

    def functionAction(self, index):  # ANCHOR functionAction
        # self.function_buttons.index(self.sender())
        # button.setChecked(True)
        if index == 0:
            self.functionIndex = 0
            self.scroll_area.hide()
            self.addClip.hide()
            self.clip_input.hide()
            self.checkList.hide()
            self.checkboxBtn.hide()
            self.addBtn.hide()
            self.toolbarContainer.hide()
        elif index == 1:
            self.functionIndex = 1
            self.scroll_area.hide()
            self.addClip.hide()
            self.clip_input.hide()
            self.checkList.show()
            self.checkList.activateWindow()
            self.checkList.setFocus()
            self.checkboxBtn.show()
            self.addBtn.show()
            self.toolbarContainer.show()
            """if self.reducing:
                self.control_buttons[0].setIcon(self.controlIcons[0][1])
            else:
                self.control_buttons[0].setIcon(self.controlIcons[0][0])"""
            # self.time_label.show()
            # self.update_display()
        elif index == 2:
            self.functionIndex = 2
            self.scroll_area.hide()
            self.addClip.hide()
            self.clip_input.hide()
            self.checkList.show()
            self.checkList.activateWindow()
            self.checkList.setFocus()
            self.checkboxBtn.show()
            self.addBtn.show()
            self.toolbarContainer.show()
            # print(self.running, self.paused)
            """if self.running:
                self.control_buttons[0].setIcon(self.controlIcons[0][1])
            else:
                self.control_buttons[0].setIcon(self.controlIcons[0][0])
            if not self.running and not self.paused:
                self.time_label.hide()
            self.update_display()"""
            # self.stateNow = 0
            # self.show_tooltip("Stopwatch",0)
        elif index == 3:
            # self.showingTime = True
            self.functionIndex = 3
            self.scroll_area.show()
            self.addClip.show()
            self.clip_input.show()
            self.checkList.hide()
            self.checkboxBtn.hide()
            self.addBtn.hide()
            self.toolbarContainer.hide()
            self.clip_input.activateWindow()
            self.clip_input.setFocus()
            """if self.reducing or self.running:
                self.control_buttons[0].setIcon(self.controlIcons[0][1])
            else:
                self.control_buttons[0].setIcon(self.controlIcons[0][0])
            if not self.running:
                self.time_label.show()
            self.update_display()"""
            # self.stateNow = 3

    def changeEvent(self, event):
        if event.type() == QEvent.ActivationChange:
            if self.isActiveWindow():
                # print("Window Activated")
                self.set_shadow(True)
                if self.functionIndex == 2:
                    self.clip_input.activateWindow()
                    self.clip_input.setFocus()
            else:
                # print("Window Deactivated")
                if self.functionIndex == 2:
                    self.clip_input.clearFocus()
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
        widget_under_mouse = QApplication.instance().widgetAt(QCursor.pos())
        delta = event.angleDelta().y()
        if widget_under_mouse in [self.top_widget]:
            if delta > 0:
                if self.functionIndex > 0:
                    self.functionIndex -= 1
                    self.function_buttons[self.functionIndex].setChecked(True)
                    self.functionAction(self.functionIndex)
                # self.task_index = (self.task_index + 1) % len(self.tasks)
            elif delta < 0:
                if self.functionIndex < 3:
                    self.functionIndex += 1
                    self.function_buttons[self.functionIndex].setChecked(True)
                    self.functionAction(self.functionIndex)
                # self.task_index = (self.task_index - 1) % len(self.tasks)

            # self.tooltip.setText(self.tasks[self.task_index])
        event.accept()

    def enterEvent(self, a0):
        super().enterEvent(a0)

    def leaveEvent(self, a0):
        super().leaveEvent(a0)

    def mousePressEvent(self, event):  # ANCHOR mouseEvent
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
                widget_under_mouse = QApplication.instance().widgetAt(QCursor.pos())
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self.functionIndex == 2 and self.isActiveWindow():
            self.clip_input.activateWindow()
            self.clip_input.setFocus()
        if not self.isFullScreen():
            if self.resizing:
                self.perform_resize(event.globalPos())
                self.checkList.onContentChanged()
                self.is_dragging = True
            elif self.drag_position and event.buttons() == Qt.LeftButton:
                if self.isDocking:
                    self.isDocking = False
                    self.function_buttons[0].setProperty("class", "function")
                    self.function_buttons[0].style().unpolish(self.function_buttons[0])
                    self.function_buttons[0].style().polish(self.function_buttons[0])
                self.move(event.globalPos() - self.drag_position)
                self.is_dragging = True
            else:
                edge = self.detect_edge(event.pos())
                self.update_cursor(edge)

    def mouseReleaseEvent(self, event):
        widget_under_mouse = QApplication.instance().widgetAt(QCursor.pos())

        if event.button() == Qt.LeftButton and not self.is_dragging:
            # self.task_label.setText(self.getNextTask())
            # import subprocess
            # Run a .exe file (Windows)
            # subprocess.Popen(["C:/Windows/SysWOW64/notepad.exe"])
            pass

        self.resizing = False
        self.drag_position = None
        self.resize_edge = None
        self.isMouseDown = False
        QApplication.changeOverrideCursor(Qt.ArrowCursor)

    def getNextTask(self):
        if self.randomTaskDisplay:
            import random

            n = random.choices([1, 2, 3], weights=[0.5, 0.3, 0.2])[0]
            self.task_index = n
            return self.tasks[self.task_index]
        else:
            self.task_index = (self.task_index + 1) % len(self.tasks)
            if self.task_index == 0:
                self.task_index = 1
            return self.tasks[self.task_index]

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
        self.randomTaskDisplay = data["flag"]

    def setDefault(self):
        if not self.settingWindowStatus[SettingWindowTypes.DEFAULT.value]:
            data = {
                "value": self.setCountdown,
                "flag": self.defaultStopwatch,
            }
            self.popup[SettingWindowTypes.DEFAULT.value] = Settings(
                self.handledDefault,
                data,
                SettingWindowTypes.DEFAULT.value,
                self,
            )
            self.popup[SettingWindowTypes.DEFAULT.value].show()
            self.popup[SettingWindowTypes.DEFAULT.value].activateWindow()
            self.settingWindowStatus[SettingWindowTypes.DEFAULT.value] = True
        else:
            self.popup[SettingWindowTypes.DEFAULT.value].activateWindow()

    def handledDefault(self, data):
        self.setCountdown = data["value"]
        if not self.reducing and not self.pausedReducing:
            self.countdownTime = self.setCountdown
        self.defaultStopwatch = data["flag"]

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
        self.fullScreenLocked = data["flag"]
        if self.fullScreenLocked and self.isFullScreen():
            self.setWindowOpacity(1)
            # self.tooltip.setTransparency(1)
        else:
            self.setWindowOpacity(self.transparency)
            # self.tooltip.setTransparency(self.transparency)
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
        QTimer.singleShot(100, self.resizeContent)

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

    def contextMenuEvent(self, event):
        widget_under_mouse = QApplication.instance().widgetAt(QCursor.pos())
        # print(widget_under_mouse)
        if (
            widget_under_mouse is not None
            and not widget_under_mouse in self.function_buttons
        ):
            self.menu.exec_(event.globalPos())

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
        min_width = (
            40  # self.time_label.sizeHint().width() + 20  # Add padding if needed
        )
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

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resizeContent()

    def resizeContent(self):
        w = self.width()
        h = self.height()

        if self.isFullScreen():
            self.wrapper.setGeometry(0, 0, w, h)
            self.shadow.setBlurRadius(0)

            self.top_widget.setFixedHeight(int(h * 0.2))
            self.bottom_widget.setFixedHeight(int(h * 0.2))
            self.center_widget.setGeometry(
                0,
                self.top_widget.height(),
                w,
                h - self.top_widget.height() - self.bottom_widget.height(),
            )

            for button in self.control_buttons:
                button.setFixedWidth(self.top_widget.height())
                button.setIconSize(
                    QSize(self.top_widget.height(), self.top_widget.height())
                )
            for button in self.function_buttons:
                button.setFixedWidth(
                    int(
                        (self.top_widget.width() - 2 - 2 * self.top_widget.height()) / 4
                    )
                )
        else:
            self.wrapper.setGeometry(10, 10, w - 20, h - 20)
            self.shadow.setBlurRadius(20)

            self.top_widget.setFixedHeight(int(h * 0.1))
            self.bottom_widget.setFixedHeight(int(h * 0.2))
            self.center_widget.setGeometry(
                0,
                self.top_widget.height(),
                w - 20,
                h - 20 - self.top_widget.height() - self.bottom_widget.height(),
            )

            for button in self.control_buttons:
                button.setFixedWidth(self.top_widget.height())
                button.setIconSize(
                    QSize(self.top_widget.height(), self.top_widget.height())
                )
            for button in self.function_buttons:
                button.setFixedWidth(
                    int(
                        (self.top_widget.width() - 2 - 2 * self.top_widget.height()) / 4
                    )
                )

        size = QSize(
            self.bottom_widget.width() - 10,
            self.bottom_widget.height(),
        )
        size = QSize(
            int((self.top_widget.width() - 2 - 2 * self.top_widget.height()) / 3),
            self.top_widget.height() - 2,
        )
        icon_size = self.getFontSize(size, self.functionIcon[0], self.functionFont)
        if icon_size >= 1:
            self.functionFont.setPointSize(icon_size)
            for button in self.function_buttons:
                button.setFont(self.functionFont)

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
            rect = metrics.boundingRect(
                0, 0, label.width(), label.height(), Qt.TextWordWrap, text
            )  # tightBoundingRect

            if rect.width() <= label_width and rect.height() <= label_height:
                best_size = mid
                low = mid + 1
            else:
                high = mid - 1
        return best_size

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

    def hideEvent(self, event):
        self.hided.emit()
        super().hideEvent(event)


class Stopwatch(QWidget):  # ANCHOR --Stopwatch
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.DOCK_POSITIONS = [
            "top-right",
            "right",
            "bottom-right",
            "bottom",
            "bottom-left",
            "left",
            "top-left",
            "top",
        ]

        self.isDocking = False
        self.dockIndex = 0
        self.originalPos = None
        self.lastPos = None
        self.transparency = 0.8
        self.defaultStopwatch = True
        self.countdownTime = 600
        self.setCountdown = 600
        self.reducing = False
        self.pausedReducing = False
        self.task_index = 0
        self.tasks = ["Take a break", "Drawing", "Music", "Modeling"]
        self.functionIcon = ["⏳", "⏱", "🕓"]
        self.controlIcons = [
            [QIcon("play white.svg"), QIcon("pause white.svg")],
            QIcon("reset white.svg"),
        ]
        self.function_buttons = []
        self.control_buttons = []
        self.functionIndex = 1
        self.showingTime = False
        self.stateNow = 0
        self.breakAfter = 60
        self.fullScreenLocked = True
        self.randomTaskDisplay = True
        self.blink_colon_visible = True
        self.is_dragging = False
        self.checkListStatus = False
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
        self.wrapper.setObjectName("mainContainer")
        self.wrapper.setMouseTracking(True)
        self.wrapper.setStyleSheet(
            "QWidget#mainContainer {background-color: rgb(30, 30, 30); border-radius: 5px; border: 1px solid rgb(80, 80, 80);}"
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
        self.top_widget = QWidget()
        # self.top_widget.setStyleSheet("border: 2px solid red;")
        # self.top_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        # self.top_widget.setFixedWidth(120)

        # ANCHOR widgets
        self.top_widget.setMouseTracking(True)
        self.top_widget.resize(120, 24)

        self.center_widget = QWidget()
        # self.center_widget.setStyleSheet("border: 2px solid red;")
        self.center_widget.setProperty("class", "outer")
        self.center_widget.setStyleSheet(
            """QWidget[class="outer"] {border-top: 1px solid rgb(80, 80, 80);border-bottom: 1px solid rgb(80, 80, 80);}"""
        )
        self.center_widget.setMouseTracking(True)
        self.center_widget.resize(120, 50)

        self.bottom_widget = QWidget()
        # self.bottom_widget.setStyleSheet("border: 2px solid red;")
        self.bottom_widget.setMouseTracking(True)
        self.bottom_widget.resize(120, 24)

        self.main_layout = QVBoxLayout(self.wrapper)

        # ANCHOR back label
        self.back_label = QLabel("88:88", self.center_widget)
        self.back_label.setAlignment(Qt.AlignCenter)
        self.back_label.setStyleSheet(
            "color: rgb(40,40,40);background: transparent;"  # margin-left:2px;margin-right:2px;
        )
        self.back_label.setMouseTracking(True)
        # self.back_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.back_label.setWordWrap(False)
        # self.back_label.setTextInteractionFlags(Qt.NoTextInteraction)

        self.time_label = QLabel("00:00", self.center_widget)
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("color: white;background: transparent;")
        self.time_label.setMouseTracking(True)
        # self.time_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.time_label.setWordWrap(False)
        # self.time_label.setTextInteractionFlags(Qt.NoTextInteraction)

        self.task_label = QLabel(self.tasks[0], self.bottom_widget)
        self.task_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.task_label.setObjectName("taskWidget")
        self.task_label.setStyleSheet(
            """
            #taskWidget{
                color: white;
                background-color: transparent;
                padding-left: 2px;
                border-bottom-left-radius:5px;
                border-bottom-right-radius:5px;
            }
            #taskWidget:hover {
                background-color: #333;
            }
            """
        )

        self.task_label.setMouseTracking(True)
        self.task_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.task_label.setWordWrap(False)
        self.task_label.setTextInteractionFlags(Qt.NoTextInteraction)

        """
        self.task_button = QPushButton(self.tasks[0], self.bottom_widget)
        self.task_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.task_label.setStyleSheet(
            "color: white;background: transparent;padding-left: 2px"
        )
        self.task_label.setMouseTracking(True)
        self.task_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.task_label.setWordWrap(False)
        self.task_label.setTextInteractionFlags(Qt.NoTextInteraction)"""

        layout = QHBoxLayout(self.top_widget)
        layout.setContentsMargins(1, 1, 1, 1)  # No padding around the edges
        layout.setSpacing(0)  # No spacing between widgets

        leftLayout = QHBoxLayout()
        leftLayout.setContentsMargins(0, 0, 0, 0)  # No padding around the edges
        leftLayout.setSpacing(0)  # No spacing between widgets

        rightLayout = QHBoxLayout()
        rightLayout.setContentsMargins(0, 0, 0, 0)  # No padding around the edges
        rightLayout.setSpacing(0)  # No spacing between widgets

        pushButtonStyle = """
            QPushButton[class="function"] {
                background-color: rgb(30, 30, 30);
                color: white;
                line-height: 100%;
                text-align: center;
                border-right:1px solid rgb(80, 80, 80);
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QPushButton[class="pos"] {
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                background-color: rgb(29, 173, 245);
            }
            QPushButton[class="pos"]:hover {
                background-color: rgb(96, 200, 252);
            }
            QPushButton[class="pos"]:pressed {
                background-color: rgb(140, 213, 250);
            }
            QPushButton[class="pos"]:checked {
                background-color: rgb(140, 213, 250);
                border: 1px solid white;
            }
            QPushButton[class="control"] {
                background-color: rgb(30, 30, 30);
                color: white;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QPushButton:hover {
                background-color: #333;
            }
            QPushButton:pressed {
                background-color: #555;
            }
            
            QPushButton:checked {
                background-color: #555;
                border: 1px solid white;
            }
        """
        group = QButtonGroup(self)
        group.setExclusive(True)
        group.buttonClicked[int].connect(self.functionAction)

        # ANCHOR function button
        self.functionFont = QFont()
        for text in self.functionIcon:
            function_Button = DraggableButton(self.top_widget, text)
            # function_Button.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
            function_Button.setStyleSheet(pushButtonStyle)
            function_Button.setMouseTracking(True)
            function_Button.setCheckable(True)
            self.functionFont.setPointSize(8)
            function_Button.setProperty("class", "function")
            function_Button.setFont(self.functionFont)
            # function_Button.resize(40, 10)
            function_Button.setFixedWidth(24)
            function_Button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            function_Button.rightClicked.connect(self.functionRightClick)
            function_Button.wheelScrolled.connect(self.functionWheelScroll)
            function_Button.dragged.connect(self.functionDrag)
            # function_Button.setMaximumWidth(30)
            # function_Button.clicked.connect(self.functionAction)

            # function_label.setWordWrap(False)
            # function_label.setTextInteractionFlags(Qt.NoTextInteraction)

            # function_Button.adjustSize()
            self.function_buttons.append(function_Button)
            group.addButton(function_Button, self.functionIcon.index(text))
            leftLayout.addWidget(function_Button, stretch=2)

        for icon in self.controlIcons:
            control_Button = DraggableButton(self.top_widget)
            if self.controlIcons.index(icon) == 0:
                control_Button.setIcon(icon[0])
                # control_Button.setStyleSheet("margin-left: 10px;")
            else:
                control_Button.setIcon(icon)
            # control_Button.resize(10,10)
            control_Button.setIconSize(QSize(20, 20))
            # control_Button.setMaximumWidth(30)
            # control_Button.setFixedWidth(20)
            control_Button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
            control_Button.clicked.connect(self.controlAction)
            control_Button.wheelScrolled.connect(self.functionWheelScroll)
            # function_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
            control_Button.setProperty("class", "control")
            control_Button.setStyleSheet(pushButtonStyle)
            control_Button.setMouseTracking(True)

            # function_label.setWordWrap(False)
            # function_label.setTextInteractionFlags(Qt.NoTextInteraction)

            # control_Button.adjustSize()
            self.control_buttons.append(control_Button)
            rightLayout.addWidget(control_Button, stretch=0)

        layout.addLayout(leftLayout)
        layout.addStretch()
        layout.addLayout(rightLayout)
        self.function_buttons[2].setChecked(True)

        """self.functionRButton = QPushButton(">", self.wrapper)
        self.functionRButton.setStyleSheet(pushButtonStyle)
        self.functionRButton.setMouseTracking(True)
        self.functionRButton.clicked.connect(self.nextFunction)

        self.functionLButton = QPushButton("<", self.wrapper)
        self.functionLButton.setStyleSheet(pushButtonStyle)
        self.functionLButton.setMouseTracking(True)
        self.functionLButton.clicked.connect(self.lastFunction)"""
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # No padding around the edges
        self.main_layout.setSpacing(0)  # No spacing between widgets

        self.main_layout.addWidget(
            self.top_widget, stretch=1
        )  # stretch = 0 Fixed height (like 50px)
        self.main_layout.addWidget(self.center_widget, stretch=2)  # Expands to fill
        self.main_layout.addWidget(
            self.bottom_widget, stretch=1
        )  # Fixed height (like 50px)

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
        self.task_label.adjustSize()
        # self.function_label.setFont(self.font2)
        # self.function_label.adjustSize()
        self.time_label.show()

        self.task_label.show()
        # print(self.back_label.size())
        self.active_original_size = self.back_label.size()

        # self.tooltip = FloatingTooltip(self.tasks[self.task_index], self)
        self.popup = [None] * len(
            SettingWindowTypes
        )  # Settings(self.handleTasks, data, 1)

        self.resizeContent()
        QApplication.setOverrideCursor(Qt.ArrowCursor)

        self.checkList = CheckList(self)
        self.checkList.hided.connect(self.on_check_list_hided)
        # ANCHOR menu
        self.menu = QMenu(self)
        self.menu.addAction("Start", self.toggle_timer)
        self.menu.addAction("Reset", self.reset_timer)
        self.menu.addAction("Default Settings", self.setDefault)
        self.menu.addAction("Edit Tasks", self.editTasks)
        self.menu.addAction("Transparency", self.setTransparency)
        self.menu.addAction("Minimize to tray", self.hideToTray)
        self.menu.addAction("Full Screen", self.fullOrNormal)
        self.menu.addAction("Add to Starup", self.add_to_startup)
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
        self.functionAction(2)

    """
    -------------------------------------------------------------
    events
    
    -------------------------------------------------------------
    """

    def functionDrag(self):
        if self.isDocking:
            self.isDocking = False
            button = self.sender()
            button.setProperty("class", "function")
            button.style().unpolish(button)
            button.style().polish(button)

    def snap_to_nearest(self):
        screen = QApplication.primaryScreen().geometry()
        win_geo = widget.frameGeometry()
        center = win_geo.center()

        snap_points = [
            QPoint(screen.right() - win_geo.width(), screen.top()),  # 1: top-right
            QPoint(
                screen.right() - win_geo.width(), center.y() - win_geo.height() // 2
            ),  # 5: right
            QPoint(
                screen.right() - win_geo.width(), screen.bottom() - win_geo.height()
            ),  # 3: bottom-right
            QPoint(
                center.x() - win_geo.width() // 2, screen.bottom() - win_geo.height()
            ),  # 7: bottom
            QPoint(screen.left(), screen.bottom() - win_geo.height()),  # 2: bottom-left
            QPoint(screen.left(), center.y() - win_geo.height() // 2),  # 4: left
            QPoint(screen.left(), screen.top()),  # 0: top-left
            QPoint(center.x() - win_geo.width() // 2, screen.top()),  # 6: top
        ]

        def distance(p1: QPoint, p2: QPoint):
            return (p1.x() - p2.x()) ** 2 + (p1.y() - p2.y()) ** 2

        current_pos = win_geo.topLeft()
        distances = [distance(current_pos, pt) for pt in snap_points]
        nearest_index = distances.index(min(distances))

        # Move window
        widget.move(snap_points[nearest_index])

        # Store the index
        self.dockIndex = nearest_index  # You can access this later

    def functionWheelScroll(self, direction):
        button = self.sender()
        if (
            button == self.function_buttons[0]
            and not self.isFullScreen()
            and self.isDocking
        ):
            if direction == "up":
                self.dockIndex = (self.dockIndex - 1) % len(self.DOCK_POSITIONS)
            else:
                self.dockIndex = (self.dockIndex + 1) % len(self.DOCK_POSITIONS)

            self.lastPos = self.pos()
            self.dock_to_position(self.DOCK_POSITIONS[self.dockIndex])
            pos = self.pos()
            delta = pos - self.lastPos
            cursor_pos = QCursor.pos()
            QCursor.setPos(cursor_pos + QPoint(delta.x(), delta.y()))
        else:
            if direction == "up":
                if self.functionIndex > 0:
                    self.functionIndex -= 1
                    self.function_buttons[self.functionIndex].setChecked(True)
                    self.functionAction(self.functionIndex)
                # self.task_index = (self.task_index + 1) % len(self.tasks)
            else:
                if self.functionIndex < 2:
                    self.functionIndex += 1
                    self.function_buttons[self.functionIndex].setChecked(True)
                    self.functionAction(self.functionIndex)
                # self.task_index = (self.task_index - 1) % len(self.tasks)

    def functionRightClick(self):
        button = self.sender()
        if button == self.function_buttons[0] and not self.isFullScreen():
            if not self.isDocking:
                self.isDocking = True
                button.setProperty("class", "pos")
                button.style().unpolish(button)
                button.style().polish(button)
                # button.setObjectName("pos")
                # button.setStyleSheet("""#pos{border-bottom:2px solid rgb(29, 173, 245);background:transparent;}""")
                self.dockIndex = (self.dockIndex - 1) % len(self.DOCK_POSITIONS)
                self.originalPos = self.pos()
                self.lastPos = self.pos()
                self.snap_to_nearest()
                pos = self.pos()
                delta = pos - self.lastPos
                cursor_pos = QCursor.pos()
                QCursor.setPos(cursor_pos + QPoint(delta.x(), delta.y()))
            else:
                self.isDocking = False
                self.lastPos = self.pos()
                button.setProperty("class", "function")
                button.style().unpolish(button)
                button.style().polish(button)
                self.move(self.originalPos)
                pos = self.pos()
                delta = pos - self.lastPos
                cursor_pos = QCursor.pos()
                QCursor.setPos(cursor_pos + QPoint(delta.x(), delta.y()))

    def dock_to_position(self, position: str):
        screen = QApplication.primaryScreen().availableGeometry()
        w, h = self.width(), self.height()

        x = y = 0

        if "left" in position:
            x = screen.left()
        elif "right" in position:
            x = screen.right() - w
        else:  # center horizontally
            x = screen.left() + (screen.width() - w) // 2

        if "top" in position:
            y = screen.top()
        elif "bottom" in position:
            y = screen.bottom() - h
        else:  # center vertically
            y = screen.top() + (screen.height() - h) // 2

        self.move(x, y)

    def controlAction(self):
        index = self.control_buttons.index(self.sender())
        funcIndex = 0
        if self.defaultStopwatch:
            if self.functionIndex == 0:
                funcIndex = 0
            else:
                funcIndex = 1
        else:
            if self.functionIndex == 1:
                funcIndex = 1
            else:
                funcIndex = 0
        if funcIndex == 0:
            if index == 0:
                # print("start")
                if (
                    not self.reducing
                    and not self.pausedReducing
                    and not self.running
                    and not self.paused
                ):
                    self.task_label.setText(self.getNextTask())
                if self.reducing:
                    # self.timer.stop()
                    self.pausedReducing = True
                    self.change_action_text("Pause", "Start")
                else:
                    self.time_label.show()
                    # self.timer.start(1000)
                    self.pausedReducing = False
                    # self.time_label.setStyleSheet("color: Lime; ")
                    self.change_action_text("Start", "Pause")

                self.reducing = not self.reducing
                if self.reducing:
                    self.sender().setIcon(self.controlIcons[0][1])
                    self.function_buttons[0].setChecked(True)
                    self.functionAction(0)
                else:
                    self.sender().setIcon(self.controlIcons[0][0])
            else:
                # print("reset")
                if not self.reducing and not self.pausedReducing:
                    self.reset_timer()
                else:
                    self.countdownTime = self.setCountdown
                    self.update_display()
                    self.resizeContent()
                    # self.change_action_text("Pause", "Start")
                    self.reducing = False
                    self.pausedReducing = False
                if (
                    not self.reducing
                    and not self.pausedReducing
                    and not self.running
                    and not self.paused
                ):
                    self.control_buttons[0].setIcon(self.controlIcons[0][0])

        else:
            if index == 0:
                # print("start")
                if (
                    not self.reducing
                    and not self.pausedReducing
                    and not self.running
                    and not self.paused
                ):
                    self.task_label.setText(self.getNextTask())
                self.toggle_timer()

                if self.running:
                    self.sender().setIcon(self.controlIcons[0][1])
                    self.function_buttons[1].setChecked(True)
                    self.functionAction(1)
                else:
                    self.sender().setIcon(self.controlIcons[0][0])
            else:
                # print("reset")

                if not self.running and not self.paused:
                    self.countdownTime = self.setCountdown
                    self.update_display()
                    self.resizeContent()
                    # self.change_action_text("Pause", "Start")
                    self.reducing = False
                    self.pausedReducing = False
                else:
                    self.reset_timer()
                if (
                    not self.reducing
                    and not self.pausedReducing
                    and not self.running
                    and not self.paused
                ):
                    self.control_buttons[0].setIcon(self.controlIcons[0][0])

    def functionAction(self, index):  # ANCHOR function action
        # self.function_buttons.index(self.sender())
        # button.setChecked(True)
        if index == 0:
            self.functionIndex = 0
            if self.reducing:
                self.control_buttons[0].setIcon(self.controlIcons[0][1])
            else:
                self.control_buttons[0].setIcon(self.controlIcons[0][0])
            self.time_label.show()
            self.update_display()
        elif index == 1:
            self.functionIndex = 1
            self.showingTime = False
            # print(self.running, self.paused)
            if self.running:
                self.control_buttons[0].setIcon(self.controlIcons[0][1])
            else:
                self.control_buttons[0].setIcon(self.controlIcons[0][0])
            if not self.running and not self.paused:
                self.time_label.hide()
            self.update_display()
            # self.stateNow = 0
            # self.show_tooltip("Stopwatch",0)
        else:
            self.showingTime = True
            self.functionIndex = 2
            if self.reducing or self.running:
                self.control_buttons[0].setIcon(self.controlIcons[0][1])
            else:
                self.control_buttons[0].setIcon(self.controlIcons[0][0])
            if not self.running:
                self.time_label.show()
            self.update_display()
            # self.stateNow = 3

    def nextFunction(self):
        self.functionIndex += 1
        self.function_label.setText(self.functionIcon[self.functionIndex])
        if self.functionIndex >= len(self.functionIcon) - 1:
            self.functionRButton.setDisabled(True)

        if self.functionIndex >= 0:
            self.functionLButton.setDisabled(False)

    def lastFunction(self):
        self.functionIndex -= 1
        self.function_label.setText(self.functionIcon[self.functionIndex])
        if self.functionIndex <= 0:
            self.functionLButton.setDisabled(True)

        if self.functionIndex < len(self.functionIcon) - 1:
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
        widget_under_mouse = QApplication.instance().widgetAt(QCursor.pos())
        delta = event.angleDelta().y()
        if widget_under_mouse in [self.task_label]:

            if delta > 0:
                self.task_index = (self.task_index + 1) % len(self.tasks)
            elif delta < 0:
                self.task_index = (self.task_index - 1) % len(self.tasks)

            self.task_label.setText(self.tasks[self.task_index])
        else:

            if delta > 0:
                if self.functionIndex > 0:
                    self.functionIndex -= 1
                    self.function_buttons[self.functionIndex].setChecked(True)
                    self.functionAction(self.functionIndex)
                # self.task_index = (self.task_index + 1) % len(self.tasks)
            elif delta < 0:
                if self.functionIndex < 2:
                    self.functionIndex += 1
                    self.function_buttons[self.functionIndex].setChecked(True)
                    self.functionAction(self.functionIndex)
                # self.task_index = (self.task_index - 1) % len(self.tasks)

            # self.tooltip.setText(self.tasks[self.task_index])
        event.accept()

    def enterEvent(self, a0):
        super().enterEvent(a0)
        widget_under_mouse = QApplication.instance().widgetAt(QCursor.pos())
        # print(widget_under_mouse)
        if not self.isFullScreen() and not (
            widget_under_mouse is None
            or not (
                widget_under_mouse in (self, self.menu)  # self.tooltip,
                or widget_under_mouse in self.popup
            )
        ):
            self.functionIndex = 2
            self.function_buttons[self.functionIndex].setChecked(True)
            self.functionAction(2)
        """self.tooltip.move(
            widget.mapToGlobal(QPoint(10, self.wrapper.height() + 20))
        )  # Position above the widget
        self.tooltip.show()
        self.tooltip.stopTimer()"""

    def leaveEvent(self, a0):
        super().leaveEvent(a0)
        widget_under_mouse = QApplication.instance().widgetAt(QCursor.pos())
        # print(widget_under_mouse)
        if not self.isFullScreen() and (
            widget_under_mouse is None
            or not (
                widget_under_mouse in (self, self.menu)  # self.tooltip,
                or widget_under_mouse in self.popup
            )
        ):
            pass  # print("yes")
            # self.tooltip.startTimer()
        if self.reducing:
            self.functionIndex = 0
            self.function_buttons[self.functionIndex].setChecked(True)
            self.functionAction(0)
        elif self.running:
            self.functionIndex = 1
            self.function_buttons[self.functionIndex].setChecked(True)
            self.functionAction(1)
        else:
            self.functionIndex = 2
            self.function_buttons[self.functionIndex].setChecked(True)
            self.functionAction(2)

    def closeTooltip(self):
        self.tooltip.startTimer()

    def resetTooltip(self):
        self.tooltip.stopTimer()

    def mousePressEvent(self, event):  # ANCHOR Mouse Event
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
                widget_under_mouse = QApplication.instance().widgetAt(QCursor.pos())
                if widget_under_mouse in [self.task_label]:
                    self.task_label.setStyleSheet(
                        """
                                                  #taskWidget{
                color: white;
                background-color: #555;
                padding-left: 2px;
                border-bottom-left-radius:5px;
                border-bottom-right-radius:5px;
            }
            """
                    )

                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if not self.isFullScreen():
            if self.resizing:
                self.perform_resize(event.globalPos())
                """self.tooltip.move(
                    widget.mapToGlobal(QPoint(10, self.wrapper.height() + 20))
                )"""
                self.is_dragging = True
            elif self.drag_position and event.buttons() == Qt.LeftButton:
                if self.isDocking:
                    self.isDocking = False
                    self.function_buttons[0].setProperty("class", "function")
                    self.function_buttons[0].style().unpolish(self.function_buttons[0])
                    self.function_buttons[0].style().polish(self.function_buttons[0])
                self.move(event.globalPos() - self.drag_position)
                """self.tooltip.move(
                    widget.mapToGlobal(QPoint(10, self.wrapper.height() + 20))
                )"""
                self.is_dragging = True
            else:
                edge = self.detect_edge(event.pos())
                self.update_cursor(edge)

    def mouseReleaseEvent(self, event):
        widget_under_mouse = QApplication.instance().widgetAt(QCursor.pos())
        if event.button() == Qt.LeftButton and not self.is_dragging:
            if widget_under_mouse in [self.task_label]:
                self.task_label.setStyleSheet(
                    """
                    #taskWidget{
                        color: white;
                        background-color: transparent;
                        padding-left: 2px;
                        border-bottom-left-radius:5px;
                        border-bottom-right-radius:5px;
                    }
                    #taskWidget:hover {
                        background-color: #333;
                    }
                """
                )

                # self.task_label.setText(self.getNextTask())
                import subprocess

                # Run a .exe file (Windows)
                subprocess.Popen(["C:/Windows/SysWOW64/notepad.exe"])
            elif widget_under_mouse in [self.time_label, self.back_label]:
                """part = self.detect_inside(event.x())
                self.perform_function(part)
                # self.resizeContent()
                self.is_dragging = False"""
                if not self.checkListStatus:
                    self.checkList.show()
                    self.checkListStatus = True
        self.resizing = False
        self.drag_position = None
        self.resize_edge = None
        self.isMouseDown = False

        """if not self.paused and not self.running:
            self.time_label.hide()"""
        self.update_display()
        QApplication.changeOverrideCursor(Qt.ArrowCursor)

    def on_check_list_hided(self):
        self.checkListStatus = False

    def getNextTask(self):
        if self.randomTaskDisplay:
            import random

            n = random.choices([1, 2, 3], weights=[0.5, 0.3, 0.2])[0]
            self.task_index = n
            return self.tasks[self.task_index]
        else:
            self.task_index = (self.task_index + 1) % len(self.tasks)
            if self.task_index == 0:
                self.task_index = 1
            return self.tasks[self.task_index]

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

    def editTasks(self):  # ANCHOR edit tasks
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
        self.randomTaskDisplay = data["flag"]
        self.settingWindowStatus[SettingWindowTypes.TASK.value] = False

    def setDefault(self):
        if not self.settingWindowStatus[SettingWindowTypes.DEFAULT.value]:
            data = {
                "value": self.setCountdown,
                "flag": self.defaultStopwatch,
            }
            self.popup[SettingWindowTypes.DEFAULT.value] = Settings(
                self.handledDefault,
                data,
                SettingWindowTypes.DEFAULT.value,
                self,
            )
            self.popup[SettingWindowTypes.DEFAULT.value].show()
            self.popup[SettingWindowTypes.DEFAULT.value].activateWindow()
            self.settingWindowStatus[SettingWindowTypes.DEFAULT.value] = True
        else:
            self.popup[SettingWindowTypes.DEFAULT.value].activateWindow()

    def handledDefault(self, data):
        self.setCountdown = data["value"]
        if not self.reducing and not self.pausedReducing:
            self.countdownTime = self.setCountdown
        self.defaultStopwatch = data["flag"]
        self.settingWindowStatus[SettingWindowTypes.DEFAULT.value] = False

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
        self.fullScreenLocked = data["flag"]
        if self.fullScreenLocked and self.isFullScreen():
            self.setWindowOpacity(1)
            # self.tooltip.setTransparency(1)
        else:
            self.setWindowOpacity(self.transparency)
            # self.tooltip.setTransparency(self.transparency)
        self.update()
        self.settingWindowStatus[SettingWindowTypes.TRANSPARENCY.value] = False

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
        QTimer.singleShot(100, self.resizeContent)

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
        if self.functionIndex == 1:
            self.time_label.hide()
        self.elapsed_seconds = 0
        self.update_display()
        self.resizeContent()
        self.change_action_text("Pause", "Start")
        self.running = False
        self.paused = False

    def update_time(self):  # ANCHOR updateTime
        if self.reducing:
            if self.countdownTime > 0:
                self.countdownTime -= 1
            else:
                self.reducing = False
                if self.functionIndex == 0:
                    self.control_buttons[0].setIcon(self.controlIcons[0][0])
                    self.countdownTime = self.setCountdown
                    self.update_display()
                    self.resizeContent()
                    # self.change_action_text("Pause", "Start")
                    self.reducing = False
                    self.pausedReducing = False

                QMessageBox.information(self, "Information", "Time up!", QMessageBox.Ok)
        if self.running:
            self.elapsed_seconds += 1
        self.blink_colon_visible = not self.blink_colon_visible
        # self.adjustSize()
        self.update_display()

    def update_display(self):
        """if self.showingTime:
        self.show_time_now()"""
        if self.functionIndex == 0:
            hours = self.countdownTime // 3600
            minutes = self.countdownTime // 60 % 60
            seconds = self.countdownTime % 60

            if self.reducing:
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
        elif self.functionIndex == 1:
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
        else:
            self.show_time_now()

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
        widget_under_mouse = QApplication.instance().widgetAt(QCursor.pos())
        # print(widget_under_mouse)
        if (
            widget_under_mouse is not None
            and not widget_under_mouse in self.function_buttons
        ):
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
        min_width = (
            40  # self.time_label.sizeHint().width() + 20  # Add padding if needed
        )
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

    def add_to_startup(self):
        import sys

        if sys.platform == "win32":
            import winshell
            import os

            from win32com.client import Dispatch

            shortcut_name = "Stopwatch"
            startup = winshell.startup()
            path = sys.executable if getattr(sys, "frozen", False) else sys.argv[0]
            path = os.path.abspath(path)

            shortcut_path = os.path.join(startup, f"{shortcut_name}.lnk")

            shell = Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = path
            shortcut.WorkingDirectory = os.path.dirname(path)
            shortcut.IconLocation = path
            shortcut.Description = shortcut_name
            shortcut.save()

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
            # self.back_label.setGeometry(0, 0, w, h)
            # self.time_label.setGeometry(0, 0, w, h)
            self.task_label.setGeometry(
                0, 0, self.bottom_widget.width(), self.bottom_widget.height()
            )
            # QTimer.singleShot(500, self.showTooltip)
            """self.tooltip.move(
                widget.mapToGlobal(
                    QPoint(
                        0, self.height() - self.tooltip.height()
                    )  # self.width() // 2 - self.tooltip.width() // 2
                )
            )"""

            self.top_widget.setFixedHeight(int(h * 0.2))
            self.bottom_widget.setFixedHeight(int(h * 0.2))
            self.center_widget.setGeometry(
                0,
                self.top_widget.height(),
                w,
                h - self.top_widget.height() - self.bottom_widget.height(),
            )
            # print(self.top_widget.height(),self.bottom_widget.height())
            self.back_label.setGeometry(
                5, 5, self.center_widget.width() - 10, self.center_widget.height() - 10
            )
            # print("Center", self.center_widget.width(), self.center_widget.height())
            self.time_label.setGeometry(
                5, 5, self.center_widget.width() - 10, self.center_widget.height() - 10
            )
            for button in self.control_buttons:
                button.setFixedWidth(self.top_widget.height())
                button.setIconSize(
                    QSize(self.top_widget.height(), self.top_widget.height())
                )
            for button in self.function_buttons:
                button.setFixedWidth(
                    int(
                        (self.top_widget.width() - 2 - 2 * self.top_widget.height()) / 3
                    )
                )
        else:
            self.wrapper.setGeometry(10, 10, w - 20, h - 20)
            self.shadow.setBlurRadius(20)

            self.task_label.setGeometry(
                0, 0, self.bottom_widget.width(), self.bottom_widget.height()
            )
            # self.function_label.setGeometry(0, 0, w - 20, h - 20)
            # self.tooltip.move(self.mapToGlobal(QPoint(10, self.wrapper.height() + 20)))
            self.top_widget.setFixedHeight(int(h * 0.2))
            self.bottom_widget.setFixedHeight(int(h * 0.2))
            self.center_widget.setGeometry(
                0,
                self.top_widget.height(),
                w - 20,
                h - 20 - self.top_widget.height() - self.bottom_widget.height(),
            )
            # print(self.top_widget.height(),self.bottom_widget.height())
            self.back_label.setGeometry(
                5, 5, self.center_widget.width() - 10, self.center_widget.height() - 10
            )
            # print("Center", self.center_widget.width(), self.center_widget.height())
            self.time_label.setGeometry(
                5, 5, self.center_widget.width() - 10, self.center_widget.height() - 10
            )
            for button in self.control_buttons:
                button.setFixedWidth(self.top_widget.height())
                button.setIconSize(
                    QSize(self.top_widget.height(), self.top_widget.height())
                )
            for button in self.function_buttons:
                button.setFixedWidth(
                    int(
                        (self.top_widget.width() - 2 - 2 * self.top_widget.height()) / 3
                    )
                )
                # print(self.top_widget.width(),self.top_widget.height())
        """width_ratio = 98 / 120
        height_ratio = 24 / 40
        print(
            self.back_label.width(),
            self.active_original_size.width(),
            self.back_label.height(),
            self.active_original_size.height(),
        )
        # size = self.tooltip.getTextSize()
        # print(width_ratio, height_ratio, size)"""
        size = QSize(
            self.bottom_widget.width() - 10,
            self.bottom_widget.height(),
        )
        font_size = self.getFontSize(size, max(self.tasks, key=len), self.font2)
        # self.tooltip.setFontSize(font_size)
        size = QSize(
            self.back_label.width(),
            self.back_label.height(),
        )
        point_size = self.getFontSize(size, self.back_label.text(), self.font1)
        size = QSize(
            int((self.top_widget.width() - 2 - 2 * self.top_widget.height()) / 3),
            self.top_widget.height() - 2,
        )
        icon_size = self.getFontSize(size, self.functionIcon[0], self.functionFont)
        if point_size >= 1:
            self.font1.setPointSize(point_size)
            self.time_label.setFont(self.font1)
            self.back_label.setFont(self.font1)
            """font_size = self.getFontSize(
                self.task_label, max(self.tasks, key=len), self.font2
            )"""

            self.font2.setPointSize(font_size)
            self.functionFont.setPointSize(icon_size)
            for button in self.function_buttons:
                button.setFont(self.functionFont)
            self.task_label.setFont(self.font2)
        else:
            self.time_label.setText("")

        # print(self.back_label.size())

    def getFontSize(self, label, text, font):

        if not text or text == "":
            return 0
        label_width = label.width()
        label_height = label.height()
        # if label==self.function_buttons[0]:
        # print("yes",label_width,label_height)
        low = 5
        high = 500  # max font size
        best_size = low

        while low <= high:
            mid = (low + high) // 2
            font.setPointSize(mid)
            metrics = QFontMetrics(font)
            rect = metrics.boundingRect(
                0, 0, label.width(), label.height(), Qt.TextWordWrap, text
            )  # tightBoundingRect

            if rect.width() <= label_width and rect.height() <= label_height:
                # if label==self.function_buttons[0]:
                # print("yes",rect.width(), rect.height(), label_width, label_height, text)
                # if mid == 269:
                # print(rect.width(), rect.height(), label_width, label_height, text)
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
