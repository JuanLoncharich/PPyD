/*
 * Alumnos:
 * Julian Ignacio Fernandez
 * Juan Andres Loncharich
*/

#include <iostream>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <atomic>
#include <chrono>

std::mutex m;
std::condition_variable cv_queue;
std::condition_variable cv_printer;
bool queue_has_document = false;
int queued_user_id = -1;
std::atomic<int> processed(0);
const int NUM_USERS = 10;

void user_thread(int user_id) {
    std::unique_lock<std::mutex> lock(m);
    while (queue_has_document) {
        cv_queue.wait(lock);
    }
    queued_user_id = user_id;
    queue_has_document = true;
    std::cout << "Usuario " << user_id << " agregó archivo a la cola de impresión" << std::endl;
    cv_printer.notify_one();
}

void printer_thread() {
    while (processed < NUM_USERS) {
        std::unique_lock<std::mutex> lock(m);
        while (!queue_has_document) {
            cv_printer.wait(lock);
        }
        int user_id = queued_user_id;
        queue_has_document = false;
        cv_queue.notify_one();
        lock.unlock();

        std::cout << "Imprimiendo archivo de usuario " << user_id << std::endl;
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
        processed++;
    }
}

int main() {
    std::thread printer(printer_thread);
    std::thread users[NUM_USERS];
    for (int i = 0; i < NUM_USERS; ++i) {
        users[i] = std::thread(user_thread, i + 1);
    }
    for (auto& t : users) {
        t.join();
    }
    printer.join();
    return 0;
}
