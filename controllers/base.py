from database.connection import SessionLocal


class BaseController:
    def __init__(self):
        super().__init__()
        self.session = SessionLocal()
