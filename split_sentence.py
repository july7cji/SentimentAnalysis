# -*- coding: utf-8 -*-
# split sentences

import argparse
import re
import chardet

def process_commands():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
 
    return parser.parse_args()

# 按pattern中的标点符号分隔句子，并且保留分隔的标点
def my_split(s, pattern):
    result = []
    w = ''
    for c in s:
        if c not in pattern:
            w += c
        else:
            w += c
            if w in pattern: # 如果分割开后的仍然是一个符号，例如感叹号，说明有多个感叹号连在一起了，保留
                w = result[-1] + w
                del result[-1]
            if w.strip() != "":
            	result.append(w)
            	#print w
            w = ''
    if w.strip() != '':
        result.append(w)
    return result

if __name__ == '__main__':
    args = process_commands()
    with open(args.input, 'r')as fin, open(args.output, 'w')as fout:
        for sentence in fin:
            sentence = sentence.strip().decode("utf-8")
            #delimiter = re.compile(ur'[，。？！；,?!;\s]') 
            #sents = delimiter.split(sentence)
            sents = my_split(sentence, ur"，。？！；,?!; ")
            sentences = []
            for x in sents:
                if x.strip()!="":
                    sentences.append(x)
            for i in range(len(sentences)):
                #print sentences[i]
                fout.write(sentences[i].encode("utf-8"))
                fout.write("\n")
            fout.write("\n")
