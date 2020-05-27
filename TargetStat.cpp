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

int read_targets(std::ifstream &tar, TargetsCount &targetsCount, Reduce2Origin &reduce2Origin) {
    std::string line;;
    std::regex tab_re("\\t|\\s+");
    while (getline(tar, line)) {
        line = rm_nl(line);
        std::vector<std::string> v(std::sregex_token_iterator(line.begin(), line.end(), tab_re, -1),
                                   std::sregex_token_iterator());
        if (v.size() != 2) {
            perror("Invalid format of input file, \"origin_pwd\treduce_pwd\" please!");
            std::exit(-1);
        }
        std::string origin_pwd = v[0];
        std::string reduce_pwd = v[1];
        if (targetsCount.find(origin_pwd) == targetsCount.end()) {
            targetsCount.insert(std::make_pair(origin_pwd, 0));
        }
        targetsCount.at(origin_pwd)++;
        if (reduce2Origin.find(reduce_pwd) == reduce2Origin.end()) {
            std::set<std::string> origins;
            origins.insert(origin_pwd);
            reduce2Origin.insert(std::make_pair(reduce_pwd, origins));
        } else {
            reduce2Origin.at(reduce_pwd).insert(origin_pwd);
        }
        if (reduce2Origin.find(origin_pwd) == reduce2Origin.end()) {
            std::set<std::string> origins;
            origins.insert(origin_pwd);
            reduce2Origin.insert(std::make_pair(origin_pwd, origins));
        } else {
            reduce2Origin.at(origin_pwd).insert(origin_pwd);
        }
    }
    return 0;
}

int target_stat(std::ifstream &fin, std::ofstream &fout, std::ifstream &tar, std::string &splitter) {
    std::string line;
    TargetsCount targetsCount;
    Reduce2Origin reduce2Origin;
    read_targets(tar, targetsCount, reduce2Origin);
    int total_targets = 0;
    for (auto &iter : targetsCount) {
        total_targets += iter.second;
    }
    unsigned long long guesses = 0;
    unsigned long long cracked = 0;
    while (getline(fin, line)) {
        line = rm_nl(line);
        if (reduce2Origin.find(line) == reduce2Origin.end()) {
            guesses += 1;
            continue;
        }
        auto origins = reduce2Origin.at(line);
        for (auto &origin_pwd : origins) {
            guesses += 1;
            if (targetsCount.at(origin_pwd) > 0) {
                int pwd_freq = targetsCount.at(origin_pwd);
                cracked += pwd_freq;
                targetsCount.at(origin_pwd) = 0;
                fout << line << splitter << origin_pwd << splitter << pwd_freq << splitter
                     << guesses << splitter << cracked << splitter
                     << std::setiosflags(std::ios::fixed) << std::setprecision(2)
                     << ((double) cracked / total_targets * 100) << "\n";
            }
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