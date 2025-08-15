import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextBrowser,
    QPushButton, QFileDialog, QMessageBox
)
from bs4 import BeautifulSoup

class HtmlLinkExtractor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HTML Full Link Extractor")
        self.resize(800, 600)

        self.browser = QTextBrowser()
        self.load_button = QPushButton("Load HTML File")
        self.copy_button = QPushButton("Copy Selected Links")

        layout = QVBoxLayout()
        layout.addWidget(self.load_button)
        layout.addWidget(self.browser)
        layout.addWidget(self.copy_button)
        self.setLayout(layout)

        self.load_button.clicked.connect(self.load_html)
        self.copy_button.clicked.connect(self.copy_selected_links)

    def load_html(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open HTML File", "", "HTML Files (*.html *.htm);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    html = f.read()
                self.browser.setHtml(html)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def copy_selected_links(self):
        selected_html = self.browser.textCursor().selection().toHtml()
        links = self.extract_links(selected_html)
        if links:
            QApplication.clipboard().setText("\n".join(links))
            QMessageBox.information(self, "Copied", f"Copied {len(links)} link(s) to clipboard.")
        else:
            QMessageBox.information(self, "No Links", "No valid links found in the selection.")

    def extract_links(self, html):
        soup = BeautifulSoup(html, "html.parser")
        hrefs = [a.get("href") for a in soup.find_all("a", href=True)]
        return list(dict.fromkeys(hrefs))  # remove duplicates, preserve order

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HtmlLinkExtractor()
    window.show()
    sys.exit(app.exec_())
