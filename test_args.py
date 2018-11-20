import logging
from chunk_logger import SafeTimedChunksFileHandler

"""
Send logs for 10 minutes from 50 threads to single handler. 2min chunks, 6min retention (3x2min)
"""

try:
    print('-\n- Too low minutesInterval')
    SafeTimedChunksFileHandler('logs/foo.bar', minutesInterval=0)
except:
    logging.exception('')

try:
    print('-\n- Negitive minutesInterval')
    SafeTimedChunksFileHandler('logs/foo.bar', minutesInterval=-1)
except:
    logging.exception('')

try:
    print('-\n- Too high minutesInterval')
    SafeTimedChunksFileHandler('logs/foo.bar', minutesInterval=61)
except:
    logging.exception('')

try:
    print('-\n- Prime minutesInterval')
    SafeTimedChunksFileHandler('logs/foo.bar', minutesInterval=7)
except:
    logging.exception('')
