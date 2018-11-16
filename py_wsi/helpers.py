'''

Various helper functions.

Author: @ysbecca

'''

import time
from datetime import timedelta


# Helper timing functions.
def start_timer():
    return time.time()

def end_timer(start_time):
    end_time = time.time()
    print("Time usage: " + str(timedelta(seconds=int(round(end_time - start_time)))))
