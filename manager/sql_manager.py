"""These module handles SQL and Plot"""
import sqlite3
from model.task import Task

class SqlManager:

    def __init__(self):
        self.cursor = None
        self.sql_connection = None
        self.connect_sql()

    def get_all_tasks(self) -> list:
        """Get All saved tasks from SQL DB"""
        queury = "SELECT * FROM tasks"
        self.cursor.execute(queury)
        rows = self.cursor.fetchall()
        tasks = []
        for row in rows:
            task = Task(_id = row[0],
                        _title= row[1],
                        _description= row[2],
                        _start_date= row[3],
                        _start_time= row[4],
                        _end_time= row[5],
                        _current_process= row[6]
                    )
            tasks.append(task)
        return tasks

    def get_all_open_tasks(self) -> list:
        """Get All open tasks from SQL DB"""
        self.cursor.execute("SELECT * FROM tasks WHERE current_process < ?", (100,))
        rows = self.cursor.fetchall()
        tasks = []
        for row in rows:
            task = Task(_id = row[0],
                        _title= row[1],
                        _description= row[2],
                        _start_date= row[3],
                        _start_time= row[4],
                        _end_time= row[5],
                        _current_process= row[6]
                    )
            tasks.append(task)
        return tasks

    def get_all_done_tasks(self) -> list:
        """Get All open tasks from SQL DB"""
        self.cursor.execute("SELECT * FROM tasks WHERE current_process = ?", (100,))
        rows = self.cursor.fetchall()
        tasks = []
        for row in rows:
            task = Task(_id = row[0],
                        _title= row[1],
                        _description= row[2],
                        _start_date= row[3],
                        _start_time= row[4],
                        _end_time= row[5],
                        _current_process= row[6]
                    )
            tasks.append(task)
        return tasks

    def get_tasks_one_date(self, date):
        """Get Tasks for certain date"""
        self.cursor.execute("SELECT * FROM tasks WHERE start_date = ?", (date,))
        rows = self.cursor.fetchall()
        tasks = []
        for row in rows:
            task = Task(_id = row[0],
                        _title= row[1],
                        _description= row[2],
                        _start_date= row[3],
                        _start_time= row[4],
                        _end_time= row[5],
                        _current_process= row[6]
                    )
            tasks.append(task)
        return tasks

    def add_new_task(self, new_task: Task):
        """Add new Task to task DB"""
        if new_task.id is not None:
            query = '''
                UPDATE tasks
                SET title = ?, description = ?, start_date = ?, start_time = ?, end_time = ?, current_process = ?
                WHERE id = ?
            '''
            start_date_str = new_task.start_date.isoformat()  
            start_time_str = new_task.start_time.strftime("%H:%M:%S")
            end_time_str = new_task.end_time.strftime("%H:%M:%S")
            self.cursor.execute(query, (
                new_task.title,
                new_task.description,
                start_date_str,
                start_time_str,
                end_time_str,
                new_task.current_process,
                new_task.id
            ))
        else:
            query = '''
                INSERT INTO tasks (title, description, start_date, start_time, end_time, current_process)
                VALUES (?, ?, ?, ?, ?, ?)
            '''
            start_date_str = new_task.start_date.isoformat()  # z.B. '2000-01-01'
            start_time_str = new_task.start_time.strftime("%H:%M:%S")  # z.B. '00:00:00'
            end_time_str = new_task.end_time.strftime("%H:%M:%S")

            params = (
                new_task.title,
                new_task.description,
                start_date_str,
                start_time_str,
                end_time_str,
                new_task.current_process
            )
            self.cursor.execute(query, params)
        self.sql_connection.commit()

    def connect_sql(self):
        """Connect to SQL DB"""
        self.sql_connection = sqlite3.connect("tasks.db")
        self.cursor = self.sql_connection.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                start_date TEXT,
                start_time TEXT,
                end_time TEXT,
                current_process INTEGER
            )
        ''')
        self.sql_connection.commit()

    def delete_task_by_id(self, task_id):
        """Delete Task from DB by ID"""
        query = "DELETE FROM tasks WHERE id = ?"
        self.cursor.execute(query, (task_id,))
        self.sql_connection.commit()
