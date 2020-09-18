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

## 3. gutify.py

### usage

The usage of gutify is to some extent a long story.

**Required**
- -f: Guess number and cracked number stored here
- -s: Save results here
- -t: Testing set will be used to obtain its size

**Optional for -f**
- --gc-split: How to split items of a line in guess number and cracked number file
- --idx-guess: guess number is at idx-guess, start from 0
- --idx-crack: cracked number is at idx-crack, start from 0

**Optional for line style**
- --upper: Max guess number
- --lower: Min guess number
- --color: Color of the line
- --line-style: solid, dash, dot, or dot_dash
- --marker: the marker on the line
- --line-width: the width of the line

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