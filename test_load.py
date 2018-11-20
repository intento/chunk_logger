import os
import time
import logging
from threading import Thread
from chunk_logger import SafeTimedChunksFileHandler

"""
Send logs for 10 minutes from 50 threads to single handler. 2min chunks, 6min retention (3x2min)
"""

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

    def write(self, *args, **kwargs):
        pass


LOG_FILE = 'logs/debug1.log'
ERR_FILE = 'logs/error1.log'

FORMAT = '[%(asctime)s] [%(levelname)s] [PID: ' + str(
    os.getpid()) + '] [%(name)s]:  %(message)s'
FORMATTER = logging.Formatter(FORMAT)

logging.basicConfig(level=logging.DEBUG, stream=NullHandler())
root = logging.root
log_handler = SafeTimedChunksFileHandler(
    LOG_FILE, minutesInterval=2, oldCount=3)
log_handler.setLevel(logging.DEBUG)
log_handler.setFormatter(FORMATTER)
root.addHandler(log_handler)

err_handler = SafeTimedChunksFileHandler(
    ERR_FILE, minutesInterval=2, oldCount=3)
err_handler.setLevel(logging.ERROR)
err_handler.setFormatter(FORMATTER)
root.addHandler(err_handler)


def run(thread_num):
    def _run():
        lg = logging.getLogger('n{}'.format(thread_num))
        for i in range(10 * 60 * 10):  # 10 minutes
            if i % (10 * 10) == 0:  # every 10 sec
                print('thread {}, {}'.format(thread_num, i))
            lg.debug('test debug: ')
            lg.error('test error: ')
            time.sleep(0.1)

    return _run


for i in range(50):
    Thread(target=run(i)).start()

input()
