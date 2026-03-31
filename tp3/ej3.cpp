/*
 * Alumnos:
 * Julian Ignacio Fernandez
 * Juan Andres Loncharich
*/


#include <cstdlib>
#include <iostream>
#include <sys/wait.h>
#include <unistd.h>

const int NUM_USERS = 10;

void close_fd(int fd) {
	if (close(fd) == -1) {
		perror("close");
		_exit(1);
	}
}

void user_process(int user_id, int slot_pipe_read, int queue_pipe_write) {
	char token;
	if (read(slot_pipe_read, &token, 1) != 1) {
		perror("read slot token");
		_exit(1);
	}

	if (write(queue_pipe_write, &user_id, sizeof(user_id)) != sizeof(user_id)) {
		perror("write queue");
		_exit(1);
	}

	std::cout << "Usuario " << user_id << " agregó archivo a la cola de impresión" << std::endl;
}

void printer_process(int queue_pipe_read, int slot_pipe_write) {
	for (int printed = 0; printed < NUM_USERS; ++printed) {
		int user_id;
		if (read(queue_pipe_read, &user_id, sizeof(user_id)) != sizeof(user_id)) {
			perror("read queue");
			_exit(1);
		}

		std::cout << "Imprimiendo archivo de usuario " << user_id << std::endl;

		char token = 'T';
		if (write(slot_pipe_write, &token, 1) != 1) {
			perror("write slot token");
			_exit(1);
		}
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

	char initial_token = 'T';
	if (write(slot_pipe[1], &initial_token, 1) != 1) {
		perror("init slot token");
		return 1;
	}

	pid_t printer_pid = fork();
	if (printer_pid == -1) {
		perror("fork printer");
		return 1;
	}

	if (printer_pid == 0) {
		close_fd(queue_pipe[1]);
		close_fd(slot_pipe[0]);
		printer_process(queue_pipe[0], slot_pipe[1]);
		close_fd(queue_pipe[0]);
		close_fd(slot_pipe[1]);
		_exit(0);
	}

	for (int i = 0; i < NUM_USERS; ++i) {
		pid_t user_pid = fork();
		if (user_pid == -1) {
			perror("fork user");
			return 1;
		}

		if (user_pid == 0) {
			close_fd(queue_pipe[0]);
			close_fd(slot_pipe[1]);
			user_process(i + 1, slot_pipe[0], queue_pipe[1]);
			close_fd(slot_pipe[0]);
			close_fd(queue_pipe[1]);
			_exit(0);
		}
	}

	close_fd(queue_pipe[0]);
	close_fd(queue_pipe[1]);
	close_fd(slot_pipe[0]);
	close_fd(slot_pipe[1]);

	for (int i = 0; i < NUM_USERS + 1; ++i) {
		wait(nullptr);
	}

	return 0;
}
