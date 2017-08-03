# -*- coding: utf -8 -*-                                                                                                                                              
# get vetorized version of corpus to be classified from "features.txt" 

import argparse
 
 
def process_commands():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--originalInput', required=True)
    parser.add_argument('--output', required=True)
 
    return parser.parse_args()
 
if __name__ == '__main__':
    args = process_commands()
    cnt = 0 
    with open(args.originalInput, 'r')as fin:
        for line in fin:
            cnt += 1
 
    features = []
    with open(args.input, 'r')as fin:
        for line in fin:
            features.append(line)
    
    with open(args.output, 'w')as fout:
        for i in range(-cnt, 0): 
            fout.write(features[i])
