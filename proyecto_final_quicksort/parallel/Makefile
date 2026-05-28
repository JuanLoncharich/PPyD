# Makefile for Hyperquicksort - CCAD Cluster
MPI_BIN = /ccad/stack/23.02/base/linux-rocky9-broadwell/gcc-12.2.0/openmpi-4.1.4-olpnqaqkqy7xxf26653hwdpsc42tno6w/bin
MPICXX = $(MPI_BIN)/mpicxx
CXXFLAGS = -O3 -std=c++17 -Wall -Wextra

TARGET = hyperquicksort
SRC = hyperquicksort.cpp

.PHONY: all clean run

all: $(TARGET)
$(TARGET): $(SRC)
	$(MPICXX) $(CXXFLAGS) -o $(TARGET) $(SRC)

clean:
	rm -f $(TARGET) *.out *.err

run: $(TARGET)
	@echo "Use: sbatch run.slurm"
	@echo "NO ejecutar directamente en login node"
