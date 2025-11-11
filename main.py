import sys
from PySide6.QtWidgets import QApplication
from ui.main_ui import MainUi
from manager.sql_manager import SqlManager

if __name__ == "__main__":
    todo_app = QApplication(sys.argv)
    task_manager = SqlManager()
    main_ui = MainUi(task_manager)
    main_ui.show()
    sys.exit(todo_app.exec())
