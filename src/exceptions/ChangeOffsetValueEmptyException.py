class ChangeOffsetValueEmptyException(Exception):
     def __init__(self, message="Value can not be empty"):
        self.message = message
        super().__init__(self.message)