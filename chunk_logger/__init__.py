import fcntl
import logging
import logging.handlers
import os
import re
import time
from datetime import datetime, timedelta

MIN_MINUTES = 1
MAX_MINUTES = 60
MINUTES_IN_HOUR = 60
SECONDS_IN_MINUTE = 60


class SafeTimedChunksFileHandler(logging.handlers.BaseRotatingHandler):
    """
    SafeTimedChunksFileHandler is concurrent safe FileHandler that splits logs into N-minute chunks
    """

    def __init__(self,
                 filename,
                 minutesInterval=10,
                 oldCount=0,
                 encoding=None,
                 delay=False,
                 utc=False):
        if minutesInterval < MIN_MINUTES or minutesInterval > MAX_MINUTES or MINUTES_IN_HOUR % minutesInterval:
            raise ValueError(
                "minutesInterval should be in [{},{}] range and be divisor of {}"
                .format(MIN_MINUTES, MAX_MINUTES, MINUTES_IN_HOUR))

        self.minutesInterval = minutesInterval
        self.oldCount = oldCount
        self.utc = utc
        self.suffix = "%Y-%m-%d_%H-%M"
        self.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}$")

        self._mkdir_p(filename)
        logging.handlers.BaseRotatingHandler.__init__(
            self, filename, mode='a', encoding=encoding, delay=delay)
        self.rolloverAt = self.computeRollover()

    def open_with_dt(self):
        """
        Open file with current datetime label
        """
        t = int(self.computeChunkDatetime().timestamp())
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
        newFilename = self.baseFilename + "." + time.strftime(
            self.suffix, timeTuple)
        return open(newFilename, self.mode, encoding=self.encoding)

    # https://github.com/cybergrind/safe_logger/blob/master/safe_logger/__init__.py#L12
    def _open(self):
        """
        Wrap open_with_dt() with lock
        """
        if getattr(self, '_lockf', None) and not self._lockf.closed:
            return self.open_with_dt()
        while True:
            try:
                self._aquire_lock()
                return self.open_with_dt()
            except IOError:
                self._lockf.close()
            finally:
                self._release_lock()

    # https://github.com/python/cpython/blob/3.7/Lib/logging/handlers.py#L328
    def shouldRollover(self, record):
        """
        Determine if rollover should occur
        """
        t = int(time.time())
        if t >= self.rolloverAt:
            return 1
        return 0

    def computeChunkDatetime(self):
        """
        Get the beginning of current chunk as datetime
        """
        currentTS = int(time.time())
        currentDT = datetime.fromtimestamp(currentTS)

        minute = currentDT.minute - currentDT.minute % self.minutesInterval
        return datetime(currentDT.year, currentDT.month, currentDT.day,
                        currentDT.hour, minute, 0)

    def computeRollover(self):
        """
        Get the end of current chunk as int timestamp
        """
        resultDT = self.computeChunkDatetime()
        resultDT += timedelta(minutes=self.minutesInterval)
        return int(resultDT.timestamp())

    # https://github.com/python/cpython/blob/3.7/Lib/logging/handlers.py#L340
    def getFilesToDelete(self):
        """
        Determine the files to delete when rolling over
        """
        dirName, baseName = os.path.split(self.baseFilename)
        fileNames = os.listdir(dirName)
        result = []
        prefix = baseName + "."
        plen = len(prefix)
        for fileName in fileNames:
            if fileName[:plen] == prefix:
                suffix = fileName[plen:]
                if self.extMatch.match(suffix):
                    result.append(os.path.join(dirName, fileName))
        result.sort()
        if len(result) < self.oldCount:
            result = []
        else:
            result = result[:len(result) - self.oldCount]
        return result

    # https://github.com/cybergrind/safe_logger/blob/master/safe_logger/__init__.py#L39
    def doRollover(self):
        """
        Do a rollover. Create new file, remove obsolete files
        """

        try:
            self._aquire_lock()
        except IOError:
            # cant aquire lock, return
            self._lockf.close()
            return

        t = self.rolloverAt
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
        dfn = self.baseFilename + "." + time.strftime(self.suffix, timeTuple)

        if self.oldCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)

        self.mode = 'a'
        self.stream = self._open()

        newRolloverAt = self.computeRollover()

        self.rolloverAt = newRolloverAt
        self._release_lock()

    # https://github.com/cybergrind/safe_logger/blob/master/safe_logger/__init__.py#L24
    def _aquire_lock(self):
        try:
            self._lockf = open(self.baseFilename + '_lock', 'a')
        except PermissionError:
            name = './{}_lock'.format(os.path.basename(self.baseFilename))
            self._lockf = open(name, 'a')
        fcntl.flock(self._lockf, fcntl.LOCK_EX | fcntl.LOCK_NB)

    # https://github.com/cybergrind/safe_logger/blob/master/safe_logger/__init__.py#L32
    def _release_lock(self):
        self._lockf.close()

    def _mkdir_p(self, _path):
        path = os.path.dirname(_path)
        try:
            os.makedirs(path, exist_ok=True)  # Python>3.2
        except TypeError:
            try:
                os.makedirs(path)
            except OSError as exc:  # Python >2.5
                if exc.errno == errno.EEXIST and os.path.isdir(path):
                    pass
                else:
                    raise
