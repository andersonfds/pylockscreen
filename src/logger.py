class Logger:
    def __init__(self, display: bool):
        self.display = display

    def log(self, message):
        if self.display:
            print(message)
