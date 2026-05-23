/*
 * Внешняя сортировка на C++
 * Сортирует большие файлы, разбивая на чанки
 */

#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <algorithm>
#include <sstream>
#include <chrono>
#include <filesystem>
#include <queue>
#include <iomanip>

using namespace std;
namespace fs = std::filesystem;

// Структура одного сотрудника
struct Employee {
    int id;
    string full_name;
    string department;
    string position;
    int salary;
    bool is_fired;
    string fire_date;
    string hire_date;
    string original_line;  // сохраняем строку как есть для записи

    Employee(const string& line) : original_line(line) {
        parseFromLine(line);
    }

    // Разбираем строку CSV на поля
    void parseFromLine(const string& line) {
        stringstream ss(line);
        string token;

        getline(ss, token, ',');
        id = stoi(token);

        getline(ss, full_name, ',');
        getline(ss, department, ',');
        getline(ss, position, ',');

        getline(ss, token, ',');
        salary = stoi(token);

        getline(ss, token, ',');
        is_fired = (token == "True");

        getline(ss, fire_date, ',');
        getline(ss, hire_date, ',');
    }

    string toLine() const {
        return original_line;
    }
};

// Сравнители для разных ключей
struct CompareById {
    bool operator()(const Employee& a, const Employee& b) const {
        return a.id < b.id;
    }
};

struct CompareByName {
    bool operator()(const Employee& a, const Employee& b) const {
        return a.full_name < b.full_name;
    }
};

struct CompareByDepartment {
    bool operator()(const Employee& a, const Employee& b) const {
        return a.department < b.department;
    }
};

struct CompareByPosition {
    bool operator()(const Employee& a, const Employee& b) const {
        return a.position < b.position;
    }
};

struct CompareBySalary {
    bool operator()(const Employee& a, const Employee& b) const {
        return a.salary < b.salary;
    }
};

struct CompareByFired {
    bool operator()(const Employee& a, const Employee& b) const {
        return a.is_fired < b.is_fired;
    }
};

struct CompareByFireDate {
    bool operator()(const Employee& a, const Employee& b) const {
        return a.fire_date < b.fire_date;
    }
};

// Класс внешней сортировки
class ExternalSortCPP {
private:
    string input_file;
    string output_file;
    string temp_dir;
    size_t memory_limit;
    int sort_key;
    vector<string> temp_files;

    // Размер файла
    size_t getFileSize(const string& filename) {
        return fs::file_size(filename);
    }

    // Имя для временного файла
    string getTempFilename() {
        static int counter = 0;
        return temp_dir + "/temp_" + to_string(++counter) + ".csv";
    }

    // Сортировка чанка по выбранному ключу
    void sortChunkByKey(vector<Employee>& employees, int key) {
        switch(key) {
            case 0: sort(employees.begin(), employees.end(), CompareById()); break;
            case 1: sort(employees.begin(), employees.end(), CompareByName()); break;
            case 2: sort(employees.begin(), employees.end(), CompareByDepartment()); break;
            case 3: sort(employees.begin(), employees.end(), CompareByPosition()); break;
            case 4: sort(employees.begin(), employees.end(), CompareBySalary()); break;
            case 5: sort(employees.begin(), employees.end(), CompareByFired()); break;
            case 6: sort(employees.begin(), employees.end(), CompareByFireDate()); break;
            default: sort(employees.begin(), employees.end(), CompareById());
        }
    }

    // Запись отсортированного чанка в файл
    void writeChunk(const vector<Employee>& employees, const string& filename, const string& header) {
        ofstream out(filename);
        out << header << "\n";
        for (const auto& emp : employees) {
            out << emp.toLine() << "\n";
        }
        out.close();
    }

public:
    ExternalSortCPP(const string& input, const string& output, int key = 0)
        : input_file(input), output_file(output), sort_key(key) {

        // Создаем временную папку
        string temp_dir_name = "temp_sort_cpp_" + to_string(
            chrono::system_clock::now().time_since_epoch().count());
        temp_dir = temp_dir_name;
        fs::create_directory(temp_dir);

        // Лимит памяти - 10% от файла
        size_t file_size = getFileSize(input_file);
        memory_limit = file_size / 10;

        cout << "\n============================================================" << endl;
        cout << "ВНЕШНЯЯ СОРТИРОВКА (C++)" << endl;
        cout << "============================================================" << endl;
        cout << "Входной файл: " << input_file << endl;
        cout << "Выходной файл: " << output_file << endl;

        const char* key_names[] = {"id", "full_name", "department", "position",
                                   "salary", "is_fired", "fire_date"};
        cout << "Ключ сортировки: " << key_names[key] << endl;
        cout << "Размер файла: " << file_size / (1024*1024) << " МБ" << endl;
        cout << "Лимит памяти (10%): " << memory_limit / (1024*1024) << " МБ" << endl;
        cout << "============================================================\n" << endl;
    }

    ~ExternalSortCPP() {
        cleanup();
    }

    // Удаляем временные файлы
    void cleanup() {
        for (const auto& f : temp_files) {
            if (fs::exists(f)) {
                fs::remove(f);
            }
        }
        if (fs::exists(temp_dir)) {
            fs::remove_all(temp_dir);
        }
    }

    // Фаза разбиения
    pair<size_t, double> splitPhase() {
        cout << "ФАЗА 1: РАЗБИЕНИЕ" << endl;
        cout << "----------------------------------------" << endl;

        auto start = chrono::high_resolution_clock::now();

        ifstream in(input_file);
        if (!in.is_open()) {
            throw runtime_error("Не удалось открыть файл: " + input_file);
        }

        string header;
        getline(in, header);

        vector<Employee> buffer;
        size_t current_memory = 0;
        size_t chunk_count = 0;
        size_t total_records = 0;

        string line;
        while (getline(in, line)) {
            current_memory += line.size();
            buffer.emplace_back(line);
            total_records++;

            // Если набрали лимит памяти
            if (current_memory >= memory_limit) {
                sortChunkByKey(buffer, sort_key);
                string temp_file = getTempFilename();
                writeChunk(buffer, temp_file, header);
                temp_files.push_back(temp_file);

                buffer.clear();
                current_memory = 0;
                chunk_count++;

                if (chunk_count % 10 == 0) {
                    cout << "  Создано чанков: " << chunk_count << endl;
                }
            }
        }

        // Последний чанк
        if (!buffer.empty()) {
            sortChunkByKey(buffer, sort_key);
            string temp_file = getTempFilename();
            writeChunk(buffer, temp_file, header);
            temp_files.push_back(temp_file);
            chunk_count++;
        }

        in.close();

        auto end = chrono::high_resolution_clock::now();
        double elapsed = chrono::duration<double>(end - start).count();

        cout << "  Создано " << chunk_count << " чанков" << endl;
        cout << "  Всего записей: " << total_records << endl;
        cout << "  Время разбиения: " << fixed << setprecision(2) << elapsed << " сек\n" << endl;

        return {total_records, elapsed};
    }

    // Фаза слияния
    double mergePhase() {
        cout << "ФАЗА 2: СЛИЯНИЕ" << endl;
        cout << "----------------------------------------" << endl;

        auto start = chrono::high_resolution_clock::now();

        if (temp_files.empty()) {
            throw runtime_error("Нет временных файлов для слияния");
        }

        // Компаратор для кучи (сравнивает записи по выбранному ключу)
        auto cmp = [this](const pair<string, int>& a, const pair<string, int>& b) {
            Employee ea(a.first), eb(b.first);

            switch(sort_key) {
                case 0: return ea.id > eb.id;
                case 1: return ea.full_name > eb.full_name;
                case 2: return ea.department > eb.department;
                case 3: return ea.position > eb.position;
                case 4: return ea.salary > eb.salary;
                case 5: return ea.is_fired > eb.is_fired;
                case 6: return ea.fire_date > eb.fire_date;
                default: return ea.id > eb.id;
            }
        };

        priority_queue<pair<string, int>, vector<pair<string, int>>, decltype(cmp)> pq(cmp);

        vector<ifstream> file_streams;
        string header;

        // Открываем все временные файлы
        for (size_t i = 0; i < temp_files.size(); i++) {
            file_streams.emplace_back(temp_files[i]);
            if (i == 0) {
                getline(file_streams.back(), header);
            } else {
                string dummy;
                getline(file_streams.back(), dummy);
            }

            string line;
            if (getline(file_streams.back(), line)) {
                pq.push({line, i});
            }
        }

        // Сливаем в выходной файл
        ofstream out(output_file);
        out << header << "\n";

        size_t output_count = 0;
        while (!pq.empty()) {
            auto top = pq.top();
            pq.pop();

            out << top.first << "\n";
            output_count++;

            if (output_count % 50000 == 0) {
                cout << "  Записано записей: " << output_count << endl;
            }

            string next_line;
            if (getline(file_streams[top.second], next_line)) {
                pq.push({next_line, top.second});
            }
        }

        out.close();
        for (auto& fs : file_streams) {
            fs.close();
        }

        auto end = chrono::high_resolution_clock::now();
        double elapsed = chrono::duration<double>(end - start).count();

        cout << "  Записано " << output_count << " записей" << endl;
        cout << "  Время слияния: " << fixed << setprecision(2) << elapsed << " сек\n" << endl;

        return elapsed;
    }

    // Запуск сортировки
    void run() {
        auto total_start = chrono::high_resolution_clock::now();

        size_t total_records = 0;
        double split_time = 0, merge_time = 0;

        try {
            auto split_result = splitPhase();
            total_records = split_result.first;
            split_time = split_result.second;

            if (temp_files.empty()) {
                throw runtime_error("Нет данных для сортировки");
            }

            merge_time = mergePhase();

        } catch (const exception& e) {
            cerr << "Ошибка: " << e.what() << endl;
            throw;
        }

        auto total_end = chrono::high_resolution_clock::now();
        double total_time = chrono::duration<double>(total_end - total_start).count();

        // Итоговая статистика
        cout << "\n============================================================" << endl;
        cout << "ИТОГОВАЯ СТАТИСТИКА" << endl;
        cout << "============================================================" << endl;
        cout << "Всего записей: " << total_records << endl;
        cout << "Количество чанков: " << temp_files.size() << endl;
        cout << "Время разбиения: " << fixed << setprecision(2) << split_time << " сек" << endl;
        cout << "Время слияния: " << fixed << setprecision(2) << merge_time << " сек" << endl;
        cout << "Общее время: " << fixed << setprecision(2) << total_time << " сек" << endl;

        if (total_time < 600) {
            cout << "\nВремя сортировки в пределах нормы (менее 10 минут)" << endl;
        } else {
            cout << "\nВремя сортировки превышает 10 минут!" << endl;
        }
        cout << "============================================================\n" << endl;
    }
};

int main(int argc, char* argv[]) {
    string input_file = "data.csv";
    string output_file = "sorted.txt";
    int sort_key = 0;

    if (argc > 1) input_file = argv[1];
    if (argc > 2) output_file = argv[2];
    if (argc > 3) sort_key = atoi(argv[3]);

    try {
        ExternalSortCPP sorter(input_file, output_file, sort_key);
        sorter.run();
    } catch (const exception& e) {
        cerr << "Ошибка: " << e.what() << endl;
        return 1;
    }

    return 0;
}