# easypwd
Some password utils.

Codes implemented in Python will not use external packages if possible.

## 1. plainpwdcmp

Compare plaintext passwords with specified targets

### usage
- -i: guesses file, one password per line, or (password, probability) per line
- -t: passwords to be cracked in plaintext, one password per line
- -o: results will be saved in this file
- -p: guesses file in format of (password, probability), bool
- -s: splitter in results file, "\t" by default
- -d: delim in guesses file, "\t" by default

### outputs
outputs are organized as follows:

pwd | prob(optional) | appearance | guess_number | cracked_num | cracked_ratio

## 2. Split2TrainTest.py

### usage
- -c: corpus to be parsed
- -s: training set path to be saved
- -t: testing set path to be saved
- -a: training set takes a / (a + b) percent
- -b: testing set takes b / (a + b) percent
- -l: passwords whose length being less than this will be ignored
- -u: passwords whose length being greater than this will be ignored.

### outputs
Removed invalid passwords (unprintable ASCII, too short length, etc.) will be saved if any.

## 3. gcutify.py

### usage

The usage of gcutify is to some extent a long story, so you'd better
 type in "./gcutify.py -h" in shell and see help info.

### outputs

A json file contains following items:
- label
- total number of passwords in test set, to calc the crack ratio
- color of this curve
- marker of points of curve
- line_width
_ line_style, solid or other
- guesses_list
_ cracked_list

## curver.py

### usage
See help info please. 

This is a relatively easy utils to draw curves.

If you want some additional functions, rewrite it.

### outputs
A picture