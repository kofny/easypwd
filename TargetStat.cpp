//
// Created by cw on 5/13/20.
//

#include "TargetStat.h"

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
    std::string line;;
    while (getline(tar, line)) {
        line = rm_nl(line);
        if (targetsCount.find(line) == targetsCount.end()) {
            targetsCount.insert(std::make_pair(line, 0));
        }
        targetsCount.at(line)++;
    }
    return 0;
}

int target_stat(std::ifstream &fin, std::ofstream &fout, std::ifstream &tar, std::string &splitter) {
    std::string line;
    TargetsCount targetsCount;
    read_targets(tar, targetsCount);
    int total_targets = 0;
    for (auto &iter : targetsCount) {
        total_targets += iter.second;
    }
    unsigned long long guesses = 0;
    unsigned long long cracked = 0;
    while (getline(fin, line)) {
        guesses += 1;
        line = rm_nl(line);
        if (targetsCount.find(line) != targetsCount.end() && targetsCount.at(line) > 0) {
            int pwd_freq = targetsCount.at(line);
            cracked += pwd_freq;
            targetsCount.at(line) = 0;
            fout << line << splitter << pwd_freq << splitter
                 << guesses << splitter << cracked << splitter
                 << std::setiosflags(std::ios::fixed) << std::setprecision(2)
                 << ((double) cracked / total_targets * 100) << "\n";
        }
    }
    fout << "placeholder" << splitter << 0 << splitter
         << guesses << splitter << cracked << splitter
         << std::setiosflags(std::ios::fixed) << std::setprecision(2)
         << ((double) cracked / total_targets * 100) << "\n";

    return 0;
}


int main(int argc, char *argv[]) {
    std::ifstream fin;
    std::ofstream fout;
    std::ifstream tar;
    std::string splitter("\t");
    auto cli = ((clipp::required("-i", "--input") & clipp::value("input").call([&](const std::string &f) {
        fin.open(f, std::ios::in);
        if (!fin.is_open()) {
            perror("cannot reading input from file...\n");
            std::exit(-1);
        }
    })), (clipp::required("-o", "--output") & clipp::value("output").call([&](const std::string &f) {
        fout.open(f, std::ios::out);
        if (!fout.is_open()) {
            std::cerr << "cannot open output file " << f << std::endl;
            std::exit(-1);
        }
    })), (clipp::required("-t", "--target") & clipp::value("target").call([&](const std::string &f) {
        tar.open(f, std::ios::in);
        if (!tar.is_open()) {
            std::cerr << "Failed to open " << f << std::endl;
            std::exit(-1);
        }
    })), (clipp::option("-s", "--split") & clipp::value("guesses: cracked", splitter)));

    if (clipp::parse(argc, argv, cli)) {
        target_stat(fin, fout, tar, splitter);
        fin.close();
        fout.flush();
        fout.close();
        tar.close();
    } else {
        std::cerr << clipp::usage_lines(cli, "Target Stat") << std::endl;
        return 1;
    }
    return 0;
}