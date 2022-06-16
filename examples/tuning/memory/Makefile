CC = gcc

OPENMP=-fopenmp
OLEVEL=-O2
DSTREAM_ARRAY_SIZE=500000000
DNTIMES=90
MCMODEL=large


ftree-vectorize=
ffast-math=-ffast-math
fpeel-loops=-fpeel-loops
DAARCH64_QUADMATH=-DAARCH64_QUADMATH





CFLAGS = $(OPENMP)  $(OLEVEL) -DSTREAM_ARRAY_SIZE=$(DSTREAM_ARRAY_SIZE) -DNTIMES=$(DNTIMES) -mcmodel=$(MCMODEL) $(ftree-vectorize) $(ffast-math) $(fpeel-loops) $(DAARCH64_QUADMATH) 

all:  stream_c.exe
stream_c.exe: stream.c
	$(CC) $(CFLAGS) stream.c
clean:
	rm -f stream_f.exe stream_c.exe *.o
