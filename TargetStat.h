//
// Created by cw on 5/13/20.
//

#ifndef FSTAT_TARGETSTAT_H
#define FSTAT_TARGETSTAT_H

#include <fstream>
#include <iostream>
#include <unordered_map>
#include <set>
#include <iomanip>
#include <regex>
#include "include/clipp.h"

typedef std::unordered_map<std::string, int> TargetsCount;
typedef std::unordered_map<std::string, std::set<std::string>> Reduce2Origin;
#endif //FSTAT_TARGETSTAT_H
