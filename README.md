# plainpwdcmp
Compare plaintext passwords with specified targets

## usage
- -i: guesses file, one password per line, or (password, probability) per line
- -t: passwords to be cracked in plaintext, one password per line
- -o: results will be saved in this file
- -p: guesses file in format of (password, probability), bool
- -s: splitter in results file, "\t" by default
- -d: delim in guesses file, "\t" by default

## outputs
output are organized as follows:
pwd prob(optional)  appearance  guess_number    cracked_num cracked_ratio