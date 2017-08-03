# -*- coding: utf-8 -*-
# segments sentences
                
import argparse
import re       
import jieba 
                
def process_commands():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
                
    return parser.parse_args()
                
if __name__ == '__main__':
    args = process_commands()
    with open(args.input, 'r')as fin, open(args.output, 'w')as fout:
        for sentence in fin:
            sentence = sentence.strip()
            words = jieba.lcut(sentence)
            for word in words:
                fout.write(word.encode("utf-8") + " ")
            fout.write("\n")                                
