"""
Utilities for handling WinoDict-generated new-words.
"""

from typing import Dict, List, Optional, Sequence, Set

def read_new_words_file(file_path:str) -> Dict:
    with open(file_path, 'r', encoding='utf-8') as new_words_file:
        new_words_raw = new_words_file.read().split("\n")
    new_words_dict = dict()
    for new_word_line in new_words_raw[:-1]:
        # print(new_word_line)
        tab_split_line = new_word_line.split("\t")
        # print(tab_split_line)

        pos_dict = dict()
        pos_split_1 = tab_split_line[2].split(",")
        # print(pos_split_1)
        for pos_split in pos_split_1:
            pos_split_2 = pos_split.split(":")
            pos_dict[pos_split_2[0]] = pos_split_2[1]

        new_words_dict[tab_split_line[0]] = {'wino_dict_value': tab_split_line[1], 'pos': pos_dict}
        # print(new_words_dict)
        # break
    return new_words_dict


if __name__ == "__main__":
    new_words = read_new_words_file("new_words.tsv")
    print(new_words)