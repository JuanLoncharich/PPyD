#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <chrono>

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
};

// Mean of only the non-zero ratings
double calc_mean(int s, int r, int b) {
    int sum = 0, count = 0;
    if (s > 0) { sum += s; count++; }
    if (r > 0) { sum += r; count++; }
    if (b > 0) { sum += b; count++; }
    return count > 0 ? static_cast<double>(sum) / count : 0.0;
}

// ── Linked list ───────────────────────────────────────────────────────────────

struct Node {
    Player data;
    Node  *next;
    Node(const Player &p) : data(p), next(nullptr) {}
};

class LinkedList {
public:
    Node *head = nullptr;
    int   size  = 0;

    void push_back(const Player &p) {
        Node *node = new Node(p);
        if (!head) { head = node; }
        else       { tail->next = node; }
        tail = node;
        size++;
    }

    // Sort descending by mean rating
    void sort() {
        if (!head || !head->next) return;
        head = quicksort(head, last(head));
    }

    void print_top(int n) const {
        Node *cur = head;
        int   rank = 1;
        std::cout << "Rank  | Title | Name                            | Std  | Rapid | Blitz | Mean\n";
        std::cout << std::string(80, '-') << "\n";
        while (cur && rank <= n) {
            const Player &p = cur->data;
            std::string title = p.title.empty() ? "-" : p.title;
            printf("%-5d | %-5s | %-31s | %-4d | %-5d | %-5d | %.1f\n",
                   rank, title.c_str(), p.name.c_str(),
                   p.standard_rating, p.rapid_rating, p.blitz_rating, p.mean);
            cur = cur->next;
            rank++;
        }
    }

    void save_csv(const std::string &filename) const {
        std::ofstream out(filename);
        out << "Rank,Name,Title,Standard_Rating,Rapid_Rating,Blitz_Rating,Mean\n";
        Node *cur = head;
        int   rank = 1;
        while (cur) {
            const Player &p = cur->data;
            out << rank++ << ","
                << "\"" << p.name << "\","
                << p.title << ","
                << p.standard_rating << ","
                << p.rapid_rating << ","
                << p.blitz_rating << ","
                << p.mean << "\n";
            cur = cur->next;
        }
    }

    ~LinkedList() {
        while (head) { Node *tmp = head; head = head->next; delete tmp; }
    }

private:
    Node *tail = nullptr;

    Node *last(Node *node) {
        while (node && node->next) node = node->next;
        return node;
    }

    // Median-of-three: avoids O(n²) on already-sorted input
    Node *median_of_three(Node *a, Node *b, Node *c) {
        double va = a->data.mean, vb = b->data.mean, vc = c->data.mean;
        if ((va >= vb && va <= vc) || (va >= vc && va <= vb)) return a;
        if ((vb >= va && vb <= vc) || (vb >= vc && vb <= va)) return b;
        return c;
    }

    Node *middle(Node *head, Node *end) {
        Node *slow = head, *fast = head;
        while (fast != end && fast->next != end) {
            slow = slow->next;
            fast = fast->next->next;
        }
        return slow;
    }

    void move_to_end(Node *&head, Node *&tail, Node *node, Node *prev) {
        if (prev) prev->next = node->next;
        else      head = node->next;
        node->next = nullptr;
        tail->next = node;
        tail = node;
    }

    // Partition around pivot (descending order)
    Node *partition(Node *head, Node *end, Node **new_head, Node **new_end) {
        // Pick median-of-three pivot and swap its data with end
        Node *mid  = middle(head, end);
        Node *pivotNode = median_of_three(head, mid, end);
        std::swap(pivotNode->data, end->data);

        Node *pivot = end;
        Node *prev  = nullptr;
        Node *cur   = head;
        Node *gtail = pivot; // tail of the > pivot group

        while (cur != pivot) {
            if (cur->data.mean >= pivot->data.mean) {
                // belongs on the left (larger values first)
                if (!*new_head) *new_head = cur;
                prev = cur;
                cur  = cur->next;
            } else {
                if (prev) prev->next = cur->next;
                Node *tmp  = cur->next;
                cur->next  = nullptr;
                gtail->next = cur;
                gtail = cur;
                cur   = tmp;
            }
        }

        if (!*new_head) *new_head = pivot;
        *new_end = gtail;
        return pivot;
    }

    Node *quicksort(Node *head, Node *end) {
        if (!head || head == end) return head;

        Node *new_head = nullptr, *new_end = nullptr;
        Node *pivot = partition(head, end, &new_head, &new_end);

        // Sort left side (values >= pivot)
        if (new_head != pivot) {
            Node *tmp = new_head;
            while (tmp->next != pivot) tmp = tmp->next;
            tmp->next = nullptr;

            new_head = quicksort(new_head, tmp);
            last(new_head)->next = pivot;
        }

        // Sort right side (values < pivot)
        pivot->next = quicksort(pivot->next, new_end);
        return new_head;
    }
};

// ── CSV parsing ───────────────────────────────────────────────────────────────

// Handles quoted fields like "Carlsen, Magnus"
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

int main() {
    const std::string csv_file = "top_chess_players_aug_2020.csv";
    std::ifstream file(csv_file);

    if (!file.is_open()) {
        std::cerr << "Error: could not open " << csv_file << "\n";
        return 1;
    }

    LinkedList list;
    std::string line;
    std::getline(file, line); // skip header

    auto t0 = Clock::now();

    int loaded = 0;
    while (std::getline(file, line)) {
        auto f = parse_csv_line(line);
        if (f.size() < 9) continue;

        Player p;
        // f[0]=fide_id, f[1]=name, f[2]=federation, f[3]=gender,
        // f[4]=year, f[5]=title, f[6]=standard, f[7]=rapid, f[8]=blitz
        p.name             = f[1];
        p.title            = f[5];
        p.standard_rating  = safe_int(f[6]);
        p.rapid_rating     = safe_int(f[7]);
        p.blitz_rating     = safe_int(f[8]);
        p.mean             = calc_mean(p.standard_rating, p.rapid_rating, p.blitz_rating);

        // Skip players with no ratings at all
        if (p.mean == 0.0) continue;

        list.push_back(p);
        loaded++;
    }

    auto t1 = Clock::now();
    std::cout << "Loaded " << loaded << " players in "
              << Ms(t1 - t0).count() << " ms\n";

    std::cout << "Sorting...\n";
    auto t2 = Clock::now();
    list.sort();
    auto t3 = Clock::now();
    std::cout << "Sorted in " << Ms(t3 - t2).count() << " ms\n";
    std::cout << "Total: " << Ms(t3 - t0).count() << " ms\n\n";

    list.print_top(20);

    const std::string out_file = "sorted_players.csv";
    list.save_csv(out_file);
    std::cout << "\nFull results saved to " << out_file << "\n";

    return 0;
}
