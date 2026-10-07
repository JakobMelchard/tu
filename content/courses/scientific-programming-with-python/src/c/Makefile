# Builds the shared library used by src/py/interfaces.py (note 09) and its C test.
# `make` -> libvecops.dylib (macOS) or libvecops.so (Linux); `make test`; `make clean`.
CC      = cc
CFLAGS  ?= -O2 -Wall -Wextra -std=c11 -fPIC
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
  LIB = libvecops.dylib
  # @rpath install name + @loader_path rpath: the test binary finds the
  # library next to itself whatever the working directory is
  LDFLAGS = -dynamiclib -install_name @rpath/$(LIB)
  RPATH   = -Wl,-rpath,@loader_path
else
  LIB = libvecops.so
  LDFLAGS = -shared
  RPATH   = -Wl,-rpath,'$$ORIGIN'
endif

all: $(LIB)

$(LIB): vecops.c vecops.h
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $< -lm

test_vecops.out: test_vecops.c vecops.h $(LIB)
	$(CC) $(CFLAGS) -o $@ $< -L. -lvecops -lm $(RPATH)

test: test_vecops.out
	./test_vecops.out

clean:
	rm -f libvecops.dylib libvecops.so test_vecops.out

.PHONY: all test clean
