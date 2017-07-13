"""
Logger.py

Anytime there would be a print statement we will send it to the log
Can allow logs to go to a file or other place
"""

class Logger(object):
    def __init__(self, model, log_type="Console", options = {}):
        self.model = model
        self._loggers = [eval("Logger" + log_type)(options = options)]

    def add_logger(self, log_type, options):
        self._loggers.append(eval("Logger" + log_type)(options))

    def log(self, log_level, message):
        for logger in self._loggers:
            logger.log(log_level, message)

class LoggerConsole(object):
    def __init__(self, options = {}):
        self.threshold = options['threshold'] if 'threshold' in options else 0

    def log(self, log_level, message):
        if self.threshold <= log_level:
            print ("(%d): %s" % (log_level, message))
