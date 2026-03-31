#include <cerrno>
#include <chrono>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <string>
#include <sys/wait.h>
#include <thread>
#include <unistd.h>

const int NUM_USERS = 10;
const int NUM_PRINTERS = 2;
const int QUEUE_CAPACITY = 4;
const int END_SIGNAL = -1;

void fail(const char* message) {
	perror(message);
	_exit(1);
}

void close_fd(int fd) {
	if (close(fd) == -1) {
		fail("close");
	}
}

void write_exact(int fd, const void* buffer, size_t count, const char* error_context) {
	const char* ptr = static_cast<const char*>(buffer);
	size_t total_written = 0;
	while (total_written < count) {
		ssize_t n = write(fd, ptr + total_written, count - total_written);
		if (n == -1) {
			if (errno == EINTR) {
				continue;
			}
			fail(error_context);
		}
		total_written += static_cast<size_t>(n);
	}
}

bool read_exact(int fd, void* buffer, size_t count, const char* error_context) {
	char* ptr = static_cast<char*>(buffer);
	size_t total_read = 0;
	while (total_read < count) {
		ssize_t n = read(fd, ptr + total_read, count - total_read);
		if (n == 0) {
			return false;
		}
		if (n == -1) {
			if (errno == EINTR) {
				continue;
			}
			fail(error_context);
		}
		total_read += static_cast<size_t>(n);
	}
	return true;
}

void print_line(const std::string& message) {
	std::string line = message + "\n";
	write_exact(STDOUT_FILENO, line.c_str(), line.size(), "write stdout");
}

void user_process(int user_id, int slot_pipe_read, int queue_pipe_write) {
	char token;
	if (!read_exact(slot_pipe_read, &token, 1, "read slot token")) {
		fail("read slot token");
	}

	write_exact(queue_pipe_write, &user_id, sizeof(user_id), "write queue");
	print_line("Usuario " + std::to_string(user_id) + " agregó archivo a la cola de impresión");
}

void printer_process(int printer_id, int queue_pipe_read, int slot_pipe_write) {
	while (true) {
		int user_id;
		if (!read_exact(queue_pipe_read, &user_id, sizeof(user_id), "read queue")) {
			break;
		}

		if (user_id == END_SIGNAL) {
			break;
		}

		print_line("Impresora " + std::to_string(printer_id) + ": Imprimiendo archivo");
		std::this_thread::sleep_for(std::chrono::milliseconds(500));

		char token = 'T';
		write_exact(slot_pipe_write, &token, 1, "write slot token");
	}
}

int main() {
	int queue_pipe[2];
	int slot_pipe[2];

	if (pipe(queue_pipe) == -1) {
		perror("pipe queue");
		return 1;
	}

	if (pipe(slot_pipe) == -1) {
		perror("pipe slot");
		return 1;
	}

	char token = 'T';
	for (int i = 0; i < QUEUE_CAPACITY; ++i) {
		write_exact(slot_pipe[1], &token, 1, "init slot token");
	}

	pid_t printer_pids[NUM_PRINTERS];
	for (int i = 0; i < NUM_PRINTERS; ++i) {
		pid_t pid = fork();
		if (pid == -1) {
			perror("fork printer");
			return 1;
		}
		if (pid == 0) {
			close_fd(queue_pipe[1]);
			close_fd(slot_pipe[0]);
			printer_process(i + 1, queue_pipe[0], slot_pipe[1]);
			close_fd(queue_pipe[0]);
			close_fd(slot_pipe[1]);
			_exit(0);
		}
		printer_pids[i] = pid;
	}

	pid_t user_pids[NUM_USERS];
	for (int i = 0; i < NUM_USERS; ++i) {
		pid_t pid = fork();
		if (pid == -1) {
			perror("fork user");
			return 1;
		}
		if (pid == 0) {
			close_fd(queue_pipe[0]);
			close_fd(slot_pipe[1]);
			user_process(i + 1, slot_pipe[0], queue_pipe[1]);
			close_fd(slot_pipe[0]);
			close_fd(queue_pipe[1]);
			_exit(0);
		}
		user_pids[i] = pid;
	}

	close_fd(queue_pipe[0]);
	close_fd(slot_pipe[1]);

	for (int i = 0; i < NUM_USERS; ++i) {
		waitpid(user_pids[i], nullptr, 0);
	}

	for (int i = 0; i < NUM_PRINTERS; ++i) {
		write_exact(queue_pipe[1], &END_SIGNAL, sizeof(END_SIGNAL), "write end signal");
	}
	close_fd(queue_pipe[1]);

	for (int i = 0; i < NUM_PRINTERS; ++i) {
		waitpid(printer_pids[i], nullptr, 0);
	}

	close_fd(slot_pipe[0]);

	return 0;
}
