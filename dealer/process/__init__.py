""" Process module for logging methods and stuff """
# TO-DO: Rename the module from process to someeethhhhinnnng
from time import time
import logging

def open_file(file_path):
    with open(file_path, 'r') as f:
        return f.read()

def log_method(begin, end):
    def decorate(fn):
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(args[0].logger.name)
            logger.info(begin)
            start_time = time()

            ret = fn(*args, **kwargs)

            logger.info('{}, {}s'.format(end, round(time() - start_time, 2)))
            if ret is not None:
                return ret

        return wrapper
    return decorate

def log_init(name, level):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    fmt = logging.Formatter('%(asctime)s | %(name)-24s | %(levelname)8s | %(message)s')

    # TO-DO: Incorporate handlers as args for specification at init
    sh = logging.StreamHandler()
    sh.setLevel(level)
    sh.setFormatter(fmt)

    # fh = logging.FileHandler(LOG_PATH)
    # fh.setLevel(level)
    # fh.setFormatter(fmt)

    logger.addHandler(sh)
    # logger.addHandler(fh)

    return logger


Logger = log_init('dealer', logging.DEBUG)
