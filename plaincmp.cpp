//
// Created by cw on 5/13/20.
//

#include "plaincmp.h"

void split(const std::string &s, std::vector<std::string> &tokens, char delim = ' ') {
    tokens.clear();
    auto string_find_first_not = [s, delim](size_t pos = 0) -> size_t {
        for (size_t i = pos; i < s.size(); i++) {
            if (s[i] != delim) return i;
        }
        return std::string::npos;
    };
    size_t lastPos = string_find_first_not(0);
    size_t pos = s.find(delim, lastPos);
    while (lastPos != std::string::npos) {
        tokens.emplace_back(s.substr(lastPos, pos - lastPos));
        lastPos = string_find_first_not(pos);
        pos = s.find(delim, lastPos);
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
        std::string &nline = line.replace(idx4r, idx4r + 1, "");
        return nline;
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

int target_stat(std::ifstream &guesses_file, std::ofstream &fout, std::ifstream &tar_pwd_list,
                std::string &splitter, char delim, bool with_prob) {
    std::string line;
    TargetsCount targetsCount;
    read_targets(tar_pwd_list, targetsCount);
    int total_targets = 0;
    for (auto &iter : targetsCount) {
        total_targets += iter.second;
    }
    unsigned long long guesses = 0;
    unsigned long long cracked = 0;
    unsigned long long cur = 0;
    while (getline(guesses_file, line)) {
        if (cur % 1000000 == 0) {
            tqdm::tqdm(cur);
        }
        cur++;
        guesses += 1;
        line = rm_nl(line);
        std::string pwd = line;
        std::string log_prob;
        if (with_prob) {
            auto tokens = std::vector<std::string>();
            split(line, tokens, delim);
            if (tokens.size() != 2) {
                fprintf(stderr, "%s is not the format of (pwd   log_prob)\n", line.c_str());
                std::exit(-1);
            }
            pwd = tokens[0];
            log_prob = tokens[1];
        }
        if (targetsCount.find(pwd) != targetsCount.end() && targetsCount.at(pwd) > 0) {
            int pwd_freq = targetsCount.at(pwd);
            cracked += pwd_freq;
            targetsCount.at(pwd) = 0;
            if (with_prob) {
                fout << pwd << splitter << log_prob << splitter << pwd_freq << splitter
                     << guesses << splitter << cracked << splitter
                     << std::setiosflags(std::ios::fixed) << std::setprecision(2)
                     << ((double) cracked / total_targets * 100) << "\n";
            } else {
                fout << pwd << splitter << pwd_freq << splitter
                     << guesses << splitter << cracked << splitter
                     << std::setiosflags(std::ios::fixed) << std::setprecision(2)
                     << ((double) cracked / total_targets * 100) << "\n";
            }
        }
    }
    std::cerr << "                                                \n";
    return 0;
}


int main(int argc, char *argv[]) {
    std::ifstream guesses_file;
    std::ofstream fout;
    std::ifstream tar_pwd_list;
    std::string splitter("\t");
    char delim = '\t';
    bool with_prob = false;
    auto cli = ((clipp::required("-i", "--guesses") &
                 clipp::value("input, pair of (pwd, log_prob)").call([&](const std::string &f) {
                     guesses_file.open(f, std::ios::in);
                     if (!guesses_file.is_open()) {
                         perror("cannot reading input from file...\n");
                         std::exit(-1);
                     }
                 })),
            (clipp::required("-o", "--output") &
             clipp::value("output").call([&](const std::string &f) {
                 fout.open(f, std::ios::out);
                 if (!fout.is_open()) {
                     std::cerr << "cannot open output file " << f << std::endl;
                     std::exit(-1);
                 }
             })),
            (clipp::required("-t", "--target") & clipp::value("target").call([&](const std::string &f) {
                tar_pwd_list.open(f, std::ios::in);
                if (!tar_pwd_list.is_open()) {
                    std::cerr << "Failed to open " << f << std::endl;
                    std::exit(-1);
                }
            })),
            (clipp::option("-s", "--split4output") & clipp::value("guesses: cracked", splitter)),
            (clipp::option("-d", "--delim4guesses") & clipp::value("guesses log_prob", delim)),
            (clipp::option("-p", "--with-prob").set(with_prob, true))
    );

    if (clipp::parse(argc, argv, cli)) {
        std::string line;
        getline(guesses_file, line);
        guesses_file.seekg(0, std::ios::beg);
        if (with_prob) {
            std::cout << "Mode: pwd & prob\n"
                      << "Delim: \"" << delim << "\"" << std::endl;
            if (line.find(delim) == std::string::npos) {
                std::cerr << "Cannot find \"" << delim
                          << "\", your line should in format of (pwd    prob),"
                             " re-check please!" << std::endl;
                std::exit(-1);
            }
        } else {
            if (line.find(delim) != std::string::npos) {
                std::cerr << "WARNING: guesses file contains \"" << delim
                          << R"(", however, you are in "pwd only" mode)" << std::endl;
            }
            std::cout << "Mode: pwd only\n";
        }
        std::cout << "Splitter: \"" << splitter << "\"" << std::endl;
        target_stat(guesses_file, fout, tar_pwd_list, splitter, delim, with_prob);
        guesses_file.close();
        fout.flush();
        fout.close();
        tar_pwd_list.close();
        std::cout << "Done!" << std::endl;
    } else {
        std::cerr << clipp::usage_lines(cli, "Target Stat") << std::endl;
        return 1;
    }
    return 0;
}