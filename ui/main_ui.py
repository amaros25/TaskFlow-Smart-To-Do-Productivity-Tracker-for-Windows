from PySide6.QtWidgets import ( # pylint: disable=no-name-in-module
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QPushButton,
    QLineEdit, QDateEdit, QTimeEdit, QTextEdit, QCalendarWidget,
    QGraphicsDropShadowEffect, QSlider, QSizePolicy, QFrame
)
 
from PySide6.QtCore import Qt, QDate, QTime # pylint: disable=no-name-in-module
from PySide6.QtGui import QTextCharFormat, QColor # pylint: disable=no-name-in-module
from model.task import Task
from manager.sql_manager import SqlManager
from ui.clickable_label import ClickableLabel
import matplotlib.pyplot as plt
import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas  # Qt5 Backend
from manager.tasks_enum import TasksEnum

class MainUi(QWidget):
    """Main GUI Class"""
    def __init__(self, sql_manager: SqlManager):
        super().__init__()
        self.sql_manager = sql_manager
        self.current_task_process = 0
        self.fig = None
        self.setWindowTitle("My TODO")
        self.setGeometry(100, 100, 820, 600)
        self.setStyleSheet("background-color: #EFEFEF; color: gray;")
        self.calendar = QCalendarWidget(self)

        self.uperh_layout = QHBoxLayout()
        self.initial_left_views()

        #Scroll Are for Tasks
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        task_list_widget = QWidget()
        self.scroll_layout = QVBoxLayout(task_list_widget)
        scroll_area.setWidget(task_list_widget)
        self.uperh_layout.addWidget(scroll_area)

        self.scroll_layout.setSpacing(0)  # Keine Abstände zwischen den Widgets
 
        # Horizental Box for the Buttons
        buttons_widgets = QHBoxLayout()
        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.uperh_layout)
        self.main_layout.addLayout(buttons_widgets)
        self.setLayout(self.main_layout)

        # self.set_widget_style_sheets()
 
        self.show_all_tasks(TasksEnum.All)
        self.show_task_efficiency_plot()


    def initial_left_views(self):
        v_left_widjet = QVBoxLayout()
        v_left_widjet.addSpacing(5)
        new_task_label = ClickableLabel("New Task")
        new_task_label.setStyleSheet("font-size: 13px; color: #007acc; font-weight:bold;")
        new_task_label.setCursor(Qt.PointingHandCursor)
        new_task_label.clicked.connect(self.add_task)
        v_left_widjet.addWidget(new_task_label, alignment=Qt.AlignHCenter)

        v_left_widjet.addSpacing(5)

        line = QFrame(self)
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: white;")
        v_left_widjet.addWidget(line)
        v_left_widjet.addSpacing(10)


        self.calendar.setFixedSize(300, 200)

        today = QDate.currentDate()
        today_format = QTextCharFormat()
        today_format.setBackground(QColor("lightblue"))
        today_format.setForeground(QColor("black"))
        today_format.setFontWeight(75)
        self.calendar.setDateTextFormat(today, today_format)
        self.calendar.clicked [QDate].connect(self.on_date_clicked)
        v_left_widjet.addWidget(self.calendar, alignment=Qt.AlignTop)
        v_left_widjet.addSpacing(10)

        line = QFrame(self)
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: white;")
        v_left_widjet.addWidget(line)
        v_left_widjet.addSpacing(10)

        h_tasks_box = QHBoxLayout()
        self.all_tasks_label = ClickableLabel(f"Tasks: {len(self.sql_manager.get_all_tasks())}")
        self.all_tasks_label.clicked.connect(lambda: self.show_all_tasks(TasksEnum.All))
        self.all_tasks_label.setStyleSheet("font-size: 13px; color: #007acc;")
        self.all_tasks_label.setCursor(Qt.PointingHandCursor)
        
        self.open_tasks_label = ClickableLabel(f"Open Tasks: {len(self.sql_manager.get_all_open_tasks())}")
        self.open_tasks_label.clicked.connect(lambda: self.show_all_tasks(TasksEnum.OPEN))
        self.open_tasks_label.setStyleSheet("font-size: 13px; color: #007acc;")
        self.open_tasks_label.setCursor(Qt.PointingHandCursor)

        self.done_tasks_label = ClickableLabel(f"Done Tasks: {len(self.sql_manager.get_all_open_tasks())}")
        self.done_tasks_label.clicked.connect(lambda: self.show_all_tasks(TasksEnum.DONE))
        self.done_tasks_label.setStyleSheet("font-size: 13px; color: #007acc;")
        self.done_tasks_label.setCursor(Qt.PointingHandCursor)
        
        h_tasks_box.addWidget(self.all_tasks_label)
        h_tasks_box.addWidget(self.open_tasks_label)
        h_tasks_box.addWidget(self.done_tasks_label)
        label_width = 40
        for label in [self.all_tasks_label, self.open_tasks_label, self.done_tasks_label]:
            label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            label.setMinimumWidth(label_width)
            label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
             
        v_left_widjet.addLayout(h_tasks_box)
        v_left_widjet.addSpacing(10)

        line = QFrame(self)
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: white;")
        v_left_widjet.addWidget(line)
        v_left_widjet.addSpacing(10)

        analyze_tasks_label = QLabel("📊 Average Task Efficiency")
        analyze_tasks_label.setStyleSheet("font-size: 12px; color: #000000; font-weight:bold;")
        analyze_tasks_label.setCursor(Qt.PointingHandCursor)
        v_left_widjet.addWidget(analyze_tasks_label, alignment=Qt.AlignTop)

        v_left_widjet.addSpacing(5)

        v_left_widjet.addStretch()
        self.uperh_layout.addLayout(v_left_widjet)
        plot_widget = QWidget()
        plot_widget.setFixedSize(300, 200)
        self.canvas = FigureCanvas(plt.figure(figsize=(5, 3)))
        
        v_left_widjet.addWidget(self.canvas)


    def show_all_tasks(self, type: TasksEnum):
        self.clear_scroll_layout()
        if type == TasksEnum.OPEN:
            self.open_tasks_label.setStyleSheet("font-size: 13px; color: #007acc; font-weight:bold;")
            self.done_tasks_label.setStyleSheet("font-size: 13px; color: #007acc; font-weight:normal;")
            self.all_tasks_label.setStyleSheet("font-size: 13px; color: #007acc; font-weight:normal;")
            tasks = self.sql_manager.get_all_open_tasks()
        elif type == TasksEnum.DONE:
            self.open_tasks_label.setStyleSheet("font-size: 13px; color: #007acc; font-weight:normal;")
            self.done_tasks_label.setStyleSheet("font-size: 13px; color: #007acc; font-weight:bold;")
            self.all_tasks_label.setStyleSheet("font-size: 13px; color: #007acc; font-weight:normal;")
            tasks = self.sql_manager.get_all_done_tasks()
        else:
            self.open_tasks_label.setStyleSheet("font-size: 13px; color: #007acc; font-weight:normal;")
            self.done_tasks_label.setStyleSheet("font-size: 13px; color: #007acc; font-weight:normal;")
            self.all_tasks_label.setStyleSheet("font-size: 13px; color: #007acc; font-weight:bold;")
            tasks = self.sql_manager.get_all_tasks()

        tasks_sorted = sorted(tasks, key=lambda task: task.id, reverse=True)
        for task in tasks_sorted:
            self.create_single_task_row(task)


    def set_widget_style_sheets(self):
        """Set style sheets"""
        self.setStyleSheet("""
            QWidget{
                background_color = #f5f5f5;
                font-family:Arial;
                font-size: 14px;
            }
            QPushButton{
                background_color : #4CAF50;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px
            }
            QPushButton:hover{
                backgound-color: #45a049;
            }
        """)

    def add_task(self):
        """Add Task Clicked"""
        print("add task")
        self.show_task_form()

    def clear_scroll_layout(self):
        """Clear Scroll Layout"""
        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def show_task_form(self, edit_task=None):
        """Show Task Form for new Task"""
        self.clear_scroll_layout()
        self.title_input = QLineEdit()
        if edit_task is not None:
            self.title_input.setText(edit_task.title)
        else:
            self.title_input.setPlaceholderText("Task Title")

 
        self.description_input = QTextEdit()

        if edit_task is not None:
            self.description_input.setText(edit_task.description)
        else:
            self.description_input.setPlaceholderText("Task Description")

        self.description_input.setFixedHeight(60)

        self.start_date_input = QDateEdit()
        self.start_date_input.setDisplayFormat("dd.MM.yyyy")
        if edit_task is not None:
            date = QDate.fromString(edit_task.start_date, "yyyy-MM-dd")
            self.start_date_input.setDate(date)
        else:
            self.start_date_input.setDate(QDate.currentDate())

        self.start_time_input = QTimeEdit()
        self.start_time_input.setDisplayFormat("HH:mm")
        if edit_task is not None:
            start_time = QTime.fromString(edit_task.start_time, "HH:mm:ss")
            self.start_time_input.setTime(start_time)
        else:
            self.start_time_input.setTime(QTime.currentTime())

        self.end_time_input = QTimeEdit()
        self.end_time_input.setDisplayFormat("HH:mm")

        if edit_task is not None:
            end_time = QTime.fromString(edit_task.end_time, "HH:mm:ss")
            self.end_time_input.setTime(end_time)
        else:
            self.end_time_input.setTime(QTime.currentTime())

        self.scroll_layout.addWidget(QLabel("Title"))
        self.scroll_layout.addWidget(self.title_input)
        self.scroll_layout.addWidget(QLabel("Descrpition"))
        self.scroll_layout.addWidget(self.description_input)
        v_date_box_start = QVBoxLayout()
        v_date_box_start.addWidget(QLabel("Start Date"))
        v_date_box_start.addWidget(self.start_date_input)
        start_end_time = QHBoxLayout()
        v_time_box_start = QVBoxLayout()
        v_time_box_start.addWidget(QLabel("Start Time"))
        v_time_box_start.addWidget(self.start_time_input)
        v_time_box_end = QVBoxLayout()
        v_time_box_end.addWidget(QLabel("End Time"))
        v_time_box_end.addWidget(self.end_time_input)
        start_end_time.addLayout(v_time_box_start)
        start_end_time.addLayout(v_time_box_end)

        submit_button = QPushButton("Save Task")
        if edit_task is not None:
            submit_button.clicked.connect(lambda checked=False, task_id = edit_task.id: self.save_task(task_id))
        else:
            submit_button.clicked.connect(lambda checked=False: self.save_task(None))

        start_date_container = QWidget()
        start_date_container.setLayout(v_date_box_start)
        start_end_time_container = QWidget()
        start_end_time_container.setLayout(start_end_time)
        self.scroll_layout.addWidget(start_date_container)
        self.scroll_layout.addWidget(start_end_time_container)
        if edit_task is not None:
            self.current_task_process = edit_task.current_process
            self.slider = QSlider(Qt.Horizontal)
            self.slider.setMinimum(0)
            self.slider.setMaximum(100)
            self.slider.setValue(edit_task.current_process)
            self.slider.setTickPosition(QSlider.TicksBelow)
            self.slider.setTickInterval(10)
            self.label_process = QLabel(f"Process: {edit_task.current_process}")
            self.slider.valueChanged.connect(self.update_label)
            self.scroll_layout.addWidget(self.slider)
            self.scroll_layout.addWidget(self.label_process)
        else:
            self.current_task_process = 0
        self.scroll_layout.addWidget(submit_button)
        if edit_task is not None:
            self.update_views_after_charges()

    def update_label(self, value):
        self.label_process.setText(f"Process: {value}")
        self.current_task_process = value

    def save_task(self, task_id):
        """ Read User Input and try to save the task"""
        title = self.title_input.text()
        description = self.description_input.toPlainText()
        start_date = self.start_date_input.date().toPython()
        start_time = self.start_time_input.time().toPython()
        end_time = self.end_time_input.time().toPython()
        new_task = Task(task_id, title, description, start_date, start_time, end_time, self.current_task_process)
        self.sql_manager.add_new_task(new_task)
        self.clear_scroll_layout()
        self.show_all_tasks(TasksEnum.All)
        self.update_views_after_charges()

    def create_single_task_row(self, task):
        task_widget = QWidget()

        task_widget.setMinimumHeight(100)
        task_widget.setMaximumHeight(200)
        task_widget.setStyleSheet("""
            background-color: #ffffff;
            border-radius: 12px;
            padding: 0px;
            margin-bottom: 10px;
            border: none;
        """)
        # Optional: Shadow-Effekt über QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 60))  # leicht transparentes Schwarz
        task_widget.setGraphicsEffect(shadow)

        vertical_layout = QVBoxLayout(task_widget)
        vertical_layout.setSpacing(8)

        title_label = QLabel(task.title)
        title_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #333;")

        description_label = QLabel(task.description)
        description_label.setWordWrap(True)
        description_label.setStyleSheet("font-size: 13px; color: #666;")

        datetime_layout = QHBoxLayout()
        datetime_layout.setSpacing(10)

        date = QDate.fromString(task.start_date, "yyyy-MM-dd")
        formatted_date = date.toString("dd.MM.yyyy")

        date_label = QLabel(f"📅 {formatted_date}")
        start_time = QTime.fromString(task.start_time, "HH:mm:ss")
        formatted_start_time = start_time.toString("HH:mm")
        start_label = QLabel(f"🕒 {formatted_start_time}")

        end_time = QTime.fromString(task.end_time, "HH:mm:ss")
        formatted_end_time = end_time.toString("HH:mm")
        end_label = QLabel(f"⏰ {formatted_end_time}")
        for lbl in (date_label, start_label, end_label):
            lbl.setStyleSheet("font-size: 12px; color: #444;")

        datetime_layout.addWidget(date_label)
        datetime_layout.addWidget(start_label)
        datetime_layout.addWidget(end_label)

        bottom_layout = QHBoxLayout()
        process_label = QLabel(f"⚙️ {task.current_process}%")
        process_label.setStyleSheet("font-size: 12px; color: #007acc;")

        edit_label = ClickableLabel("📄 Edit")
        edit_label.setStyleSheet("font-size: 12px; color: #007acc;")
        edit_label.setCursor(Qt.PointingHandCursor)
        edit_label.clicked.connect(lambda checked=False: self.show_task_form(task))

        delete_label = ClickableLabel("🧹 Delete")
        delete_label.setStyleSheet("font-size: 12px; color: #007acc;")
        delete_label.setCursor(Qt.PointingHandCursor)
        delete_label.clicked.connect(
            lambda checked=False, task_id = task.id: self.delete_task(task_id)
        )
        bottom_layout.addWidget(process_label)
        bottom_layout.addWidget(edit_label)
        bottom_layout.addWidget(delete_label)
        vertical_layout.addWidget(title_label)
        vertical_layout.addLayout(datetime_layout)
        vertical_layout.addWidget(description_label)
        vertical_layout.addLayout(bottom_layout)
        self.scroll_layout.addWidget(task_widget, alignment=Qt.AlignTop)
        # self.scroll_layout.addStretch(1)

    def delete_task(self, task_id):
        """Delete Task by ID"""
        self.sql_manager.delete_task_by_id(task_id)
        self.clear_scroll_layout()
        self.show_all_tasks(TasksEnum.All)
        self.update_views_after_charges()

    def on_date_clicked(self, date):
        date_str = date.toString('yyyy-MM-dd')
        tasks= self.sql_manager.get_tasks_one_date(date_str)
        self.clear_scroll_layout()
        tasks_sorted = sorted(tasks, key=lambda task: task.id, reverse=True)
        for task in tasks_sorted:
            self.create_single_task_row(task)

    def update_views_after_charges(self):
        self.all_tasks_label.setText(f"Tasks: {len(self.sql_manager.get_all_tasks())}")
        self.open_tasks_label.setText(f"Open Tasks: {len(self.sql_manager.get_all_open_tasks())}")
        self.done_tasks_label.setText(f"Done Tasks: {len(self.sql_manager.get_all_done_tasks())}")
        self.show_task_efficiency_plot()


    def show_task_efficiency_plot(self):
        """Show Task Efficienty Plot"""
        tasks = self.sql_manager.get_all_tasks()
        avg_progress = 0
        if tasks:
            progresses = [task.current_process for task in tasks]
            avg_progress = sum(progresses) / len(progresses)
 
        labels = ['Done', 'TODO']
        values = [avg_progress, 100 - avg_progress]
        colors = ['#4caf50', '#e0e0e0']
        if self.fig is None: 
            self.fig, ax = plt.subplots(facecolor='none')
            self.canvas.figure = self.fig
        else:
            ax = self.canvas.figure.axes[0] 
            ax.clear()
        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            wedgeprops=dict(width=0.5)  # macht einen Donut
        )
           
        self.canvas.draw()