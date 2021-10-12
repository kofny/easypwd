//
// Created by cw on 5/13/20.
//

#include "plaincmp.h"

/**
 * find substring split by delimiter
 *
 * @param s  string to be split
 * @param tokens substring split from the string {@code s}
 * @param delimiter the bound of the substrings
 */
void split(const std::string &s, std::vector<std::string> &tokens, char delimiter = ' ') {
    tokens.clear();
    auto string_find_first_not = [s, delimiter](size_t pos = 0) -> size_t {
        for (size_t i = pos; i < s.size(); i++) {
            if (s[i] != delimiter) return i;
        }
        return std::string::npos;
    };
    size_t lastPos = string_find_first_not(0);
    size_t pos = s.find(delimiter, lastPos);
    while (lastPos != std::string::npos) {
        tokens.emplace_back(s.substr(lastPos, pos - lastPos));
        lastPos = string_find_first_not(pos);
        pos = s.find(delimiter, lastPos);
    }
}

/**
 *
 * @param line line to remove \r
 * @return line removed \r
 */
inline std::string &rm_nl(std::string &line) {
    auto idx4r = line.find('\r');
    if (idx4r != std::string::npos) {
        std::string &n_line = line.replace(idx4r, idx4r + 1, "");
        return n_line;
    } else {
        return line;
    }
}

int read_targets(std::ifstream &tar, TargetsCount &targetsCount) {
    std::string line;
    while (getline(tar, line)) {
        line = rm_nl(line);
        if (targetsCount.find(line) == targetsCount.end()) {
            targetsCount.insert(std::make_pair(line, 0));
        }
        targetsCount.at(line)++;
    }
    return 0;
}

int plain_cmp(std::istream &fd, std::ofstream &f_out, std::ifstream &tar_pwd_list,
              std::string &splitter, char delimiter, bool with_prob, bool forget) {
    std::string line;
    TargetsCount targetsCount;
    read_targets(tar_pwd_list, targetsCount);
    int total_targets = 0;
    for (auto &iter: targetsCount) {
        total_targets += iter.second;
    }
    unsigned long long guesses = 0;
    unsigned long long cracked = 0;
    unsigned long long cur = 0;
    while (getline(fd, line)) {
        if (cur % 1000000 == 0) {
            tqdm::tqdm(cur);
        }
        cur++;
        line = rm_nl(line);
        std::string pwd = line;
        std::string log_prob;
        auto tokens = std::vector<std::string>();
        if (with_prob) {
            split(line, tokens, delimiter);
            if (tokens.size() != 2) {
                fprintf(stderr, "%s is not the format of (pwd   log_prob)\n", line.c_str());
                return -8;
            }
            pwd = tokens.at(0);
            log_prob = tokens.at(1);
        }
        guesses++;
        if (targetsCount.find(pwd) == targetsCount.end()) { continue; }
        if (targetsCount.at(pwd) <= 0) {
            if (forget) guesses--;
            continue;
        }
        int pwd_freq = targetsCount.at(pwd);
        cracked += pwd_freq;
        targetsCount.at(pwd) = 0;
        if (with_prob) {
            f_out << pwd << splitter << log_prob << splitter << pwd_freq << splitter
                  << guesses << splitter << cracked << splitter
                  << std::setiosflags(std::ios::fixed) << std::setprecision(2)
                  << ((double) cracked / total_targets * 100) << "\n";
        } else {
            f_out << pwd << splitter << pwd_freq << splitter
                  << guesses << splitter << cracked << splitter
                  << std::setiosflags(std::ios::fixed) << std::setprecision(2)
                  << ((double) cracked / total_targets * 100) << "\n";
        }
    }
    std::cerr << "                                                \n";
    return 0;
}


int main(int argc, char *argv[]) {
    std::ifstream guesses_file;
    std::ofstream f_out;
    std::ifstream tar_pwd_list;
    std::string splitter("\t");
    char delimiter = '\t';
    bool with_prob = false;
    bool forget = false;
    auto cli = ((clipp::required("-i", "--guesses") &
                 clipp::value("input, pair of (pwd, log_prob)").call([&](const std::string &f) {
                     if (f == "stdin") return;
                     guesses_file.open(f, std::ios::in);
                     if (!guesses_file.is_open()) {
                         perror("cannot reading input from file...\n");
                         std::exit(-6);
                     }
                 })),
            (clipp::required("-o", "--output") &
             clipp::value("output").call([&](const std::string &f) {
                 f_out.open(f, std::ios::out);
                 if (!f_out.is_open()) {
                     std::cerr << "cannot open output file " << f << std::endl;
                     std::exit(-5);
                 }
             })),
            (clipp::required("-t", "--target") & clipp::value("target").call([&](const std::string &f) {
                tar_pwd_list.open(f, std::ios::in);
                if (!tar_pwd_list.is_open()) {
                    std::cerr << "Failed to open " << f << std::endl;
                    std::exit(-4);
                }
            })),
            (clipp::option("-s", "--split4output") & clipp::value("guesses: cracked", splitter)),
            (clipp::option("-d", "--delimiter4guesses") & clipp::value("guesses log_prob", delimiter)),
            (clipp::option("-p", "--with-prob").set(with_prob, true)),
            (clipp::option("--forget").set(forget, true).label(
                    "The same guess in the guesses file will be ignored and has no impact on guess number"))
    );
    if (forget) {
        std::cerr << "Caution!\n"
                  << "Make sure that you know the meaning of the flag \"--forget\"!"
                  << std::endl;
    }
    if (clipp::parse(argc, argv, cli)) {
        std::istream &fd = guesses_file.is_open() ? guesses_file : std::cin;
        if (with_prob) {
            std::cerr << "Mode: pwd & prob\n" << "Delimiter: \"" << delimiter << "\"" << std::endl;
        } else {
            std::cerr << "Mode: pwd only\n";
        }
        std::cerr << "Splitter: \"" << splitter << "\"" << std::endl;
        int ret_code = plain_cmp(fd, f_out, tar_pwd_list, splitter, delimiter, with_prob, forget);
        if (ret_code != 0) {
            std::cerr << std::endl;
            return ret_code;
        }
        guesses_file.close();
        f_out.flush();
        f_out.close();
        tar_pwd_list.close();
        std::cerr << "Done!" << std::endl;
    } else {
        std::cerr << clipp::usage_lines(cli, "Target Stat") << std::endl;
        std::cerr << "Using `-i stdin` to read input from stdin" << std::endl;
        return 1;
    }
    return 0;
}