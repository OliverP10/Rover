import logging

class SocketLoggingHandler(logging.StreamHandler):

    def __init__(self, rover) -> None:
        logging.StreamHandler.__init__(self)
        self.rover = rover

    def emit(self, record):
        msg = self.format(record)
        self.rover.communication.send_log(msg)