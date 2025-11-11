class Task:
    """Todo Task class"""

    def __init__(self, _id, _title, _description, _start_date,
                _start_time, _end_time, _current_process):
        self.id = _id
        self.title = _title
        self.description = _description
        self.start_date = _start_date
        self.start_time = _start_time
        self.end_time = _end_time
        self.current_process = _current_process
