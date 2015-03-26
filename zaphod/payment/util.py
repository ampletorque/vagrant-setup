import time
from contextlib import contextmanager


@contextmanager
def timed(log, s, *args):
    start = time.time()
    yield
    end = time.time()
    elapsed = (end - start) * 1000.
    elapsed_s = ' %0.2f ms elapsed' % elapsed
    log.info('timed: ' + s + elapsed_s, *args)
