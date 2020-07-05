//
// Created by cw on 7/4/20.
//

#ifndef FSTAT_TQDM_H
#define FSTAT_TQDM_H

#include <fstream>
#include <iostream>
#include <iomanip>

namespace tqdm {

    /**
     * (cur / total) percent of works have been done.
     * cur should be less than 10000 and greater than 0.
     * We'll not do this work for your.
     * @param cur a integer less than 10000
     * @return Unused flag
     */
    int tqdm(unsigned int cur, unsigned int total) {
        std::cerr << std::setw(11) << std::setfill(' ') << cur << '/' << total << "\b\b\b\b\b\b\b\b\b\b";
        return 1;
    }

    int tqdm(unsigned long long cur) {
        std::cerr << std::setw(13) << std::setfill(' ') << cur << "\b\b\b\b\b\b\b\b\b\b\b\b\b";
        return 1;
    }
}
#endif //FSTAT_TQDM_H
