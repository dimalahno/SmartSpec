import sys

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QListWidget, QFileDialog, QRadioButton, QButtonGroup
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SmartSpec – умная спецификация")
        self.setGeometry(200, 200, 600, 400)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        # Список файлов
        self.file_list = QListWidget()
        layout.addWidget(self.file_list)

        # Кнопка "Добавить файл"
        add_file_btn = QPushButton("Добавить файл")
        add_file_btn.clicked.connect(self.add_file)
        layout.addWidget(add_file_btn)

        # Режимы (умный / упрощённый)
        self.mode_group = QButtonGroup()
        mode_simple = QRadioButton("Упрощённое распределение")
        mode_smart = QRadioButton("Умное распределение")
        mode_smart.setChecked(True)
        self.mode_group.addButton(mode_simple, 0)
        self.mode_group.addButton(mode_smart, 1)
        layout.addWidget(mode_simple)
        layout.addWidget(mode_smart)

        # Кнопка "Запустить"
        run_btn = QPushButton("Запустить обработку")
        run_btn.clicked.connect(self.run_processing)
        layout.addWidget(run_btn)

        central_widget.setLayout(layout)

    def add_file(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Выберите файлы",
            "",
            "Документы (*.txt *.pdf *.docx *.xlsx);;Все файлы (*)"
        )
        for file in files:
            self.file_list.addItem(file)

    def run_processing(self):
        mode = self.mode_group.checkedId()
        print("Выбран режим:", "Упрощённый" if mode == 0 else "Умный")
        files = [self.file_list.item(i).text() for i in range(self.file_list.count())]
        print("Файлы на обработку:", files)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
