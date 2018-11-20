# chunk_logger

## Description

SafeTimedChunksFileHandler is concurrent safe FileHandler that splits logs into N-minute chunks. It  also creates a directories in path if they are missing. Used some code from [safe_logger](https://github.com/cybergrind/safe_logger)


## Usage

```python
import os
import logging
from chunk_logger import SafeTimedChunksFileHandler

LOG_FILE = '/tmp/debug.log'

logging.basicConfig(level=logging.DEBUG)
root = logging.root
log_handler = SafeTimedChunksFileHandler(LOG_FILE, minutesInterval=10, oldCount=(60/10)*24*31)  # 10min chunks, 31d retention
log_handler.setLevel(logging.DEBUG)
root.addHandler(log_handler)


```