import logging

LOG_FILE = "ipc2api.log"

class log(object):
    """
    Logging Class
    @logfile: filename used to write log.
    """
    def __init__(self,logfile):
        self.logfile = logfile
        self.initial()
    
    def initial(self):
        self.logger = logging.getLogger()
        self.handler = logging.FileHandler(self.logfile)
        formatter = logging.Formatter("%(levelname)s [%(asctime)s]: %(message)s\n","%Y-%m-%d %H:%M:%S")
        self.handler.setFormatter(formatter)
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.NOTSET)
    
    def info(self,msg):
        self.logger.info(msg)
        self.removehandler()
    
    def error(self,msg):
        self.logger.error(msg)
        self.removehandler()
    
    def warnning(self,msg):
        self.logger.warning(msg)
        self.removehandler()
    
    def debug(self,msg):
        self.logger.debug(msg)
        self.removehandler()
    
    def critical(self,msg):
        self.logger.critical(msg)
        self.removehandler()
    
    def exception(self,msg):
        self.logger.exception(msg)
        self.removehandler()
    
    def removehandler(self):
        self.logger.removeHandler(self.handler)


logger = log(LOG_FILE)
