# compiler and flags
CC = clang
CFLAGS = -Wall -std=c99 -pedantic

PYTHON_VERSION = 3.11
PYTHON_INCLUDE = /usr/include/python$(PYTHON_VERSION)
PYTHON_LIB = /usr/lib/python$(PYTHON_VERSION) 

# libary
LIB = libphylib.so

# source files 
SOURCES = phylib.c phylib_wrap.c
OBJECTS = $(SOURCES:.c=.o)

all: $(LIB) _phylib.so

swig: phylib.i
	swig -python phylib.i

phylib_wrap.o: phylib_wrap.c
	$(CC) $(CFLAGS) -I$(PYTHON_INCLUDE) -fPIC -c phylib_wrap.c -o phylib_wrap.o

# shared library targets
$(LIB): phylib.o
	$(CC) -shared -o $(LIB) phylib.o

_phylib.so: phylib_wrap.o
	$(CC) $(CFLAGS) -shared phylib_wrap.o -L. -L$(PYTHON_LIB) -lpython$(PYTHON_VERSION) -lphylib -o _phylib.so

phylib.o: phylib.c phylib.h
	$(CC) $(CFLAGS) -fPIC -c phylib.c -o phylib.o

clean:
	rm -f *.o *.so phylib_wrap.c phylib.py *.svg
