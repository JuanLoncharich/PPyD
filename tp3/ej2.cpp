/*
 * Alumnos:
 * Julian Ignacio Fernandez
 * Juan Andres Loncharich
*/


#include <chrono>
#include <condition_variable>
#include <deque>
#include <iostream>
#include <mutex>
#include <thread>

std::mutex m;
std::mutex io_m;
std::condition_variable cv_not_full;
std::condition_variable cv_not_empty;

std::deque<int> print_queue;

const int NUM_USERS = 10;
const int NUM_PRINTERS = 2;
const int QUEUE_CAPACITY = 4;

int completed_prints = 0;

void user_thread(int user_id) {
	std::unique_lock<std::mutex> lock(m);
	while (print_queue.size() == QUEUE_CAPACITY) {
		cv_not_full.wait(lock);
	}

	print_queue.push_back(user_id);
	{
		std::lock_guard<std::mutex> io_lock(io_m);
		std::cout << "Usuario " << user_id << " agregó archivo a la cola de impresión" << std::endl;
	}
	cv_not_empty.notify_one();
}

void printer_thread(int printer_id) {
	while (true) {
		int user_id = -1;

		{
			std::unique_lock<std::mutex> lock(m);
			while (print_queue.empty() && completed_prints < NUM_USERS) {
				cv_not_empty.wait(lock);
			}

			if (print_queue.empty() && completed_prints == NUM_USERS) {
				return;
			}

			user_id = print_queue.front();
			print_queue.pop_front();
			cv_not_full.notify_one();
		}

		(void)user_id;
		{
			std::lock_guard<std::mutex> io_lock(io_m);
			std::cout << "Impresora " << printer_id << ": Imprimiendo archivo" << std::endl;
		}
		std::this_thread::sleep_for(std::chrono::milliseconds(500));

		{
			std::lock_guard<std::mutex> lock(m);
			completed_prints++;
			if (completed_prints == NUM_USERS) {
				cv_not_empty.notify_all();
			}
		}
	}
}

int main() {
	std::thread printers[NUM_PRINTERS];
	for (int i = 0; i < NUM_PRINTERS; ++i) {
		printers[i] = std::thread(printer_thread, i + 1);
	}

	std::thread users[NUM_USERS];
	for (int i = 0; i < NUM_USERS; ++i) {
		users[i] = std::thread(user_thread, i + 1);
	}

	for (auto& user : users) {
		user.join();
	}

	for (auto& printer : printers) {
		printer.join();
	}

	return 0;
}
