"""
This program is used as compression benchmark
"""

import time
import zlib
import gzip
import bz2

FILE_PATH = "compress_Except_example/enwik8"

COMPRESS_LEVEL = 8
COMPRESS_METHOD = "bz2"

with open(FILE_PATH, 'rb') as f_in:
    data = f_in.read()
    start = time.time()
    RES = b"compressed result"
    if COMPRESS_METHOD == "bz2":
        RES = bz2.compress(data, COMPRESS_LEVEL)
    elif COMPRESS_METHOD == "zlib":
        RES = zlib.compress(data, COMPRESS_LEVEL)
    elif COMPRESS_METHOD == "gzip":
        RES = gzip.compress(data, COMPRESS_LEVEL)
    end = time.time()

    print("time = %f" % (end - start))
    print("compress_ratio = %f" % (len(data) / len(RES)))
