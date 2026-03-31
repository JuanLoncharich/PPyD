#include <iostream>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <atomic>
#include <chrono>

std::mutex m;
std::condition_variable cv_queue;  // for PCs to wait when queue is full
std::condition_variable cv_printer;  // for printer to wait when queue is empty
bool queue_has_document = false;
int queued_pc_id = -1;
std::atomic<int> processed(0);
const int NUM_PCS = 10;

void pc_thread(int pc_id) {
    std::unique_lock<std::mutex> lock(m);
    // Wait if queue is full
    while (queue_has_document) {
        cv_queue.wait(lock);
    }
    // Submit document
    queued_pc_id = pc_id;
    queue_has_document = true;
    std::cout << "PC " << pc_id << " submitted document" << std::endl;
    // Notify printer
    cv_printer.notify_one();
}

void printer_thread() {
    while (processed < NUM_PCS) {
        std::unique_lock<std::mutex> lock(m);
        // Wait if no document in queue
        while (!queue_has_document) {
            cv_printer.wait(lock);
        }
        // Take document from queue
        int pc = queued_pc_id;
        queue_has_document = false;
        // Notify PCs that queue is free
        cv_queue.notify_one();
        lock.unlock();
        // Simulate printing
        std::cout << "Printing document from PC " << pc << std::endl;
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
        std::cout << "Finished printing document from PC " << pc << std::endl;
        processed++;
    }
}

int main() {
    std::thread pcs[NUM_PCS];
    for (int i = 0; i < NUM_PCS; ++i) {
        pcs[i] = std::thread(pc_thread, i);
    }
    std::thread printer(printer_thread);
    for (auto& t : pcs) {
        t.join();
    }
    printer.join();
    return 0;
}
