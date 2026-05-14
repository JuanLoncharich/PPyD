# Makefile for Hyperquicksort and Sequential Quicksort

MPICXX = mpicxx
CXX = g++
CXXFLAGS = -O3 -std=c++17 -Wall -Wextra

PARALLEL_TARGET = hyperquicksort
SEQ_TARGET = quicksort_seq

PARALLEL_SRC = hyperquicksort.cpp
SEQ_SRC = quicksort_seq.cpp

.PHONY: all clean run run-seq compare benchmark graphs

all: $(PARALLEL_TARGET) $(SEQ_TARGET)

$(PARALLEL_TARGET): $(PARALLEL_SRC)
	$(MPICXX) $(CXXFLAGS) -o $(PARALLEL_TARGET) $(PARALLEL_SRC)

$(SEQ_TARGET): $(SEQ_SRC)
	$(CXX) $(CXXFLAGS) -o $(SEQ_TARGET) $(SEQ_SRC)

clean:
	rm -f $(PARALLEL_TARGET) $(SEQ_TARGET)
	rm -rf results/*.csv results/*.png

# Run parallel version with 4 processors
run: $(PARALLEL_TARGET)
	mpiexec -np 4 ./$(PARALLEL_TARGET)

# Run sequential version
run-seq: $(SEQ_TARGET)
	./$(SEQ_TARGET)

# Run both for comparison
compare: all
	@echo "========================================="
	@echo "Sequential Quicksort"
	@echo "========================================="
	./$(SEQ_TARGET)
	@echo ""
	@echo "========================================="
	@echo "Parallel Hyperquicksort (4 processors)"
	@echo "========================================="
	mpiexec -np 4 ./$(PARALLEL_TARGET)

# Benchmark from 1 to 64 processors (powers of 2)
benchmark: all
	@echo "Running benchmark..."
	@mkdir -p results
	@> results/benchmark.csv
	@echo "Sequential (3 runs)..."
	@for i in 1 2 3; do \
		echo "Run $$i"; \
		./$(SEQ_TARGET) 2>&1 | grep -E "(Loaded|Sorted|Total)"; \
	done
	@for np in 1 2 4 8 16 32 64; do \
		echo "Parallel with $$np processors..."; \
		mpiexec -np $$np ./$(PARALLEL_TARGET); \
	done
	@echo "Benchmark complete! Results in results/benchmark.csv"

# Generate performance graphs
graphs:
	@echo "Generating performance graphs..."
	@python3 generate_graphs.py

# Run with custom number of processors
run-n: $(PARALLEL_TARGET)
	@echo "Usage: make run-n N=<number_of_processors>"
	mpiexec -np $(N) ./$(PARALLEL_TARGET)
