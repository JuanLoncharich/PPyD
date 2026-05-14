#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <algorithm>
#include <random>
#include <chrono>
#include <cstring>
#include <mpi.h>

using Clock = std::chrono::high_resolution_clock;
using Ms    = std::chrono::duration<double, std::milli>;

// ── Data ─────────────────────────────────────────────────────────────────────

struct Player {
    std::string name;
    std::string title;
    int         standard_rating;
    int         rapid_rating;
    int         blitz_rating;
    double      mean;

    // For MPI serialization
    void serialize(std::vector<char> &buffer) const {
        size_t name_len = name.size();
        size_t title_len = title.size();
        size_t total_size = sizeof(size_t) + name_len +
                            sizeof(size_t) + title_len +
                            sizeof(int) * 3 + sizeof(double);

        size_t offset = buffer.size();
        buffer.resize(offset + total_size);

        char *ptr = buffer.data() + offset;

        // Name
        memcpy(ptr, &name_len, sizeof(size_t));
        ptr += sizeof(size_t);
        memcpy(ptr, name.c_str(), name_len);
        ptr += name_len;

        // Title
        memcpy(ptr, &title_len, sizeof(size_t));
        ptr += sizeof(size_t);
        memcpy(ptr, title.c_str(), title_len);
        ptr += title_len;

        // Ratings
        memcpy(ptr, &standard_rating, sizeof(int));
        ptr += sizeof(int);
        memcpy(ptr, &rapid_rating, sizeof(int));
        ptr += sizeof(int);
        memcpy(ptr, &blitz_rating, sizeof(int));
        ptr += sizeof(int);

        // Mean
        memcpy(ptr, &mean, sizeof(double));
    }

    static Player deserialize(const char *ptr, size_t &offset) {
        Player p;

        // Name
        size_t name_len;
        memcpy(&name_len, ptr + offset, sizeof(size_t));
        offset += sizeof(size_t);
        p.name = std::string(ptr + offset, name_len);
        offset += name_len;

        // Title
        size_t title_len;
        memcpy(&title_len, ptr + offset, sizeof(size_t));
        offset += sizeof(size_t);
        p.title = std::string(ptr + offset, title_len);
        offset += title_len;

        // Ratings
        memcpy(&p.standard_rating, ptr + offset, sizeof(int));
        offset += sizeof(int);
        memcpy(&p.rapid_rating, ptr + offset, sizeof(int));
        offset += sizeof(int);
        memcpy(&p.blitz_rating, ptr + offset, sizeof(int));
        offset += sizeof(int);

        // Mean
        memcpy(&p.mean, ptr + offset, sizeof(double));
        offset += sizeof(double);

        return p;
    }
};

// Mean of only the non-zero ratings
double calc_mean(int s, int r, int b) {
    int sum = 0, count = 0;
    if (s > 0) { sum += s; count++; }
    if (r > 0) { sum += r; count++; }
    if (b > 0) { sum += b; count++; }
    return count > 0 ? static_cast<double>(sum) / count : 0.0;
}

// ── CSV parsing ───────────────────────────────────────────────────────────────

std::vector<std::string> parse_csv_line(const std::string &line) {
    std::vector<std::string> fields;
    std::string field;
    bool in_quotes = false;

    for (size_t i = 0; i < line.size(); i++) {
        char c = line[i];
        if (c == '"') {
            in_quotes = !in_quotes;
        } else if (c == ',' && !in_quotes) {
            fields.push_back(field);
            field.clear();
        } else {
            field += c;
        }
    }
    fields.push_back(field);
    return fields;
}

int safe_int(const std::string &s) {
    if (s.empty()) return 0;
    try { return std::stoi(s); } catch (...) { return 0; }
}

// ── Sequential Quicksort (for local sorting) ──────────────────────────────────

void quicksort(std::vector<Player> &data, int left, int right) {
    if (left >= right) return;

    // Median-of-three pivot selection
    int mid = left + (right - left) / 2;
    double pivot_val;

    if (data[left].mean >= data[mid].mean && data[left].mean <= data[right].mean) {
        pivot_val = data[left].mean;
        std::swap(data[left], data[right]);
    } else if (data[mid].mean >= data[left].mean && data[mid].mean <= data[right].mean) {
        pivot_val = data[mid].mean;
        std::swap(data[mid], data[right]);
    } else {
        pivot_val = data[right].mean;
    }

    int i = left, j = right - 1;
    while (i <= j) {
        while (i <= j && data[i].mean >= pivot_val) i++;
        while (i <= j && data[j].mean < pivot_val) j--;
        if (i <= j) {
            std::swap(data[i], data[j]);
            i++;
            j--;
        }
    }
    std::swap(data[i], data[right]);

    quicksort(data, left, i - 1);
    quicksort(data, i + 1, right);
}

// ── MPI Communication ─────────────────────────────────────────────────────────

void send_players(const std::vector<Player> &players, int dest, int tag, MPI_Comm comm) {
    std::vector<char> buffer;
    for (const auto &p : players) {
        p.serialize(buffer);
    }

    int size = buffer.size();
    MPI_Send(&size, 1, MPI_INT, dest, tag, comm);
    if (size > 0) {
        MPI_Send(buffer.data(), size, MPI_BYTE, dest, tag + 1, comm);
    }
}

std::vector<Player> recv_players(int src, int tag, MPI_Comm comm) {
    int size;
    MPI_Status status;
    MPI_Recv(&size, 1, MPI_INT, src, tag, comm, &status);

    std::vector<Player> players;
    if (size > 0) {
        std::vector<char> buffer(size);
        MPI_Recv(buffer.data(), size, MPI_BYTE, src, tag + 1, comm, &status);

        size_t offset = 0;
        while (offset < static_cast<size_t>(size)) {
            players.push_back(Player::deserialize(buffer.data(), offset));
        }
    }
    return players;
}

// ── Hyperquicksort ─────────────────────────────────────────────────────────────

void hyperquicksort(std::vector<Player> &local_data, int rank, int size, MPI_Comm comm) {
    int p = size;
    int d = 0;

    // Calculate dimension of hypercube
    while ((1 << d) < p) d++;

    // Step 1: Locally sort data in descending order
    if (!local_data.empty()) {
        quicksort(local_data, 0, local_data.size() - 1);
    }

    // Step 2: Hypercube communication phases
    for (int dim = 0; dim < d; dim++) {
        // Partner is rank with bit dim flipped
        int partner = rank ^ (1 << dim);

        if (partner >= p) continue;

        // Median of current processor serves as pivot
        double local_pivot = local_data.empty() ? 0.0 :
                            local_data[local_data.size() / 2].mean;

        double pivot;
        MPI_Allreduce(&local_pivot, &pivot, 1, MPI_DOUBLE, MPI_SUM, comm);
        pivot /= 2.0;

        // Partition data around pivot
        std::vector<Player> keep, send;

        if (rank < partner) {
            for (const auto &player : local_data) {
                if (player.mean >= pivot) {
                    keep.push_back(player);
                } else {
                    send.push_back(player);
                }
            }
        } else {
            for (const auto &player : local_data) {
                if (player.mean < pivot) {
                    keep.push_back(player);
                } else {
                    send.push_back(player);
                }
            }
        }

        // Exchange data
        std::vector<Player> received = recv_players(partner, dim * 2, comm);
        send_players(send, partner, dim * 2, comm);

        // Merge kept and received data
        local_data = keep;
        local_data.insert(local_data.end(), received.begin(), received.end());

        // Re-sort locally
        if (!local_data.empty()) {
            quicksort(local_data, 0, local_data.size() - 1);
        }
    }
}

// ── Main ───────────────────────────────────────────────────────────────────────

int main(int argc, char **argv) {
    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    const std::string csv_file = "top_chess_players_aug_2020.csv";

    std::vector<Player> local_data;
    int total_loaded = 0;

    auto t0 = Clock::now();

    // Rank 0 reads and distributes data
    if (rank == 0) {
        std::ifstream file(csv_file);
        if (!file.is_open()) {
            std::cerr << "Error: could not open " << csv_file << "\n";
            MPI_Abort(MPI_COMM_WORLD, 1);
        }

        std::vector<Player> all_players;
        std::string line;
        std::getline(file, line); // skip header

        while (std::getline(file, line)) {
            auto f = parse_csv_line(line);
            if (f.size() < 9) continue;

            Player p;
            p.name             = f[1];
            p.title            = f[5];
            p.standard_rating  = safe_int(f[6]);
            p.rapid_rating     = safe_int(f[7]);
            p.blitz_rating     = safe_int(f[8]);
            p.mean             = calc_mean(p.standard_rating, p.rapid_rating, p.blitz_rating);

            if (p.mean == 0.0) continue;
            all_players.push_back(p);
        }

        // Shuffle for fair comparison with sequential
        std::mt19937 rng(std::random_device{}());
        std::shuffle(all_players.begin(), all_players.end(), rng);

        total_loaded = all_players.size();

        // Distribute round-robin
        std::vector<std::vector<Player>> processor_data(size);
        for (size_t i = 0; i < all_players.size(); i++) {
            processor_data[i % size].push_back(all_players[i]);
        }

        // Send data to all processors
        for (int i = 1; i < size; i++) {
            send_players(processor_data[i], i, 0, MPI_COMM_WORLD);
        }
        local_data = processor_data[0];
    } else {
        // Receive data from rank 0
        local_data = recv_players(0, 0, MPI_COMM_WORLD);
    }

    MPI_Barrier(MPI_COMM_WORLD);
    auto t1 = Clock::now();

    if (rank == 0) {
        std::cout << "Loaded " << total_loaded << " players across "
                  << size << " processors\n";
        std::cout << "Distribution time: " << Ms(t1 - t0).count() << " ms\n";
        std::cout << "Sorting with Hyperquicksort...\n";
    }

    // Perform parallel sort
    auto t2 = Clock::now();
    hyperquicksort(local_data, rank, size, MPI_COMM_WORLD);
    MPI_Barrier(MPI_COMM_WORLD);
    auto t3 = Clock::now();

    // Gather results on rank 0
    std::vector<Player> sorted_data;
    std::vector<int> local_sizes(size);

    int local_size = local_data.size();
    MPI_Gather(&local_size, 1, MPI_INT, local_sizes.data(), 1, MPI_INT, 0, MPI_COMM_WORLD);

    if (rank == 0) {
        double dist_time = Ms(t1 - t0).count();
        double sort_time = Ms(t3 - t2).count();
        double total_time = Ms(t3 - t0).count();

        std::cout << "Sort time: " << sort_time << " ms\n";
        std::cout << "Total time: " << total_time << " ms\n";

        // Prepare receive buffer
        std::vector<int> recv_displs(size);
        std::vector<char> recv_buffer;
        std::vector<int> send_sizes(size);
        send_sizes[0] = 0;

        // First gather the sizes of serialized data
        for (const auto &p : local_data) {
            std::vector<char> tmp;
            p.serialize(tmp);
            send_sizes[0] += tmp.size();
        }

        MPI_Gather(send_sizes.data(), 1, MPI_INT, send_sizes.data(), 1, MPI_INT, 0, MPI_COMM_WORLD);

        for (int i = 0; i < size; i++) {
            recv_displs[i] = recv_buffer.size();
            recv_buffer.resize(recv_buffer.size() + send_sizes[i]);
        }

        // Serialize local data
        std::vector<char> send_buffer;
        for (const auto &p : local_data) {
            p.serialize(send_buffer);
        }

        MPI_Gatherv(send_buffer.data(), send_buffer.size(), MPI_BYTE,
                    recv_buffer.data(), send_sizes.data(), recv_displs.data(), MPI_BYTE,
                    0, MPI_COMM_WORLD);

        // Deserialize all data
        for (int i = 0; i < size; i++) {
            size_t offset = recv_displs[i];
            while (offset < static_cast<size_t>(recv_displs[i] + send_sizes[i])) {
                sorted_data.push_back(Player::deserialize(recv_buffer.data(), offset));
            }
        }

        // Print top 20
        std::cout << "\nRank  | Title | Name                            | Std  | Rapid | Blitz | Mean\n";
        std::cout << std::string(80, '-') << "\n";
        for (int i = 0; i < std::min(20, static_cast<int>(sorted_data.size())); i++) {
            const Player &p = sorted_data[i];
            std::string title = p.title.empty() ? "-" : p.title;
            printf("%-5d | %-5s | %-31s | %-4d | %-5d | %-5d | %.1f\n",
                   i + 1, title.c_str(), p.name.c_str(),
                   p.standard_rating, p.rapid_rating, p.blitz_rating, p.mean);
        }

        // Save to CSV with processor count in filename
        std::string out_file = "results/sorted_players_p" + std::to_string(size) + ".csv";
        std::ofstream out(out_file);
        out << "Rank,Name,Title,Standard_Rating,Rapid_Rating,Blitz_Rating,Mean\n";
        for (size_t i = 0; i < sorted_data.size(); i++) {
            const Player &p = sorted_data[i];
            out << (i + 1) << ","
                << "\"" << p.name << "\","
                << p.title << ","
                << p.standard_rating << ","
                << p.rapid_rating << ","
                << p.blitz_rating << ","
                << p.mean << "\n";
        }
        std::cout << "\nFull results saved to " << out_file << "\n";

        // Append timing to benchmark CSV
        std::ofstream bench("results/benchmark.csv", std::ios::app);
        if (bench.tellp() == 0) {
            bench << "processors,distribution_time_ms,sort_time_ms,total_time_ms\n";
        }
        bench << size << "," << dist_time << "," << sort_time << "," << total_time << "\n";
    } else {
        // Send local data size to rank 0
        std::vector<char> send_buffer;
        for (const auto &p : local_data) {
            p.serialize(send_buffer);
        }

        int send_size = send_buffer.size();
        MPI_Gather(&send_size, 1, MPI_INT, nullptr, 0, MPI_INT, 0, MPI_COMM_WORLD);

        MPI_Gatherv(send_buffer.data(), send_buffer.size(), MPI_BYTE,
                    nullptr, nullptr, nullptr, MPI_BYTE,
                    0, MPI_COMM_WORLD);
    }

    MPI_Finalize();
    return 0;
}
