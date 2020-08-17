"""
This program is used as compression benchmark
"""

import time
import zlib
import gzip
import bz2

file_path = "/root/A-Tune/examples/tuning/compress/enwik8"

compressLevel=6
compressMethod="zlib"

with open(file_path, 'rb') as f_in:
    data = f_in.read()
    start = time.time()
    c = b"compressed result"
    if compressMethod == "bz2":
        c = bz2.compress(data, compressLevel)
    elif compressMethod == "zlib":
        c = zlib.compress(data, compressLevel)
    elif compressMethod == "gzip":
        c = gzip.compress(data, compressLevel)
    end = time.time()

    print("time = %f" % (end - start))
    print("compress_ratio = %f" % (len(data) / len(c)))
