from keras import backend

import ctypes

def tf_init():
    backend.clear_session()
    try:
        ctypes.CDLL("/usr/lib/libtensorflowlite_flex.so", mode=ctypes.RTLD_GLOBAL)
        
    except:
        pass