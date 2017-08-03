from __future__ import division
import argparse
import os       
                
POSITIVE = 1 
NEGATIVE = -1
ZERO = 0        
                
def process_commands():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scores', required=True)
    parser.add_argument('--result_path', required=True)
                
    return parser.parse_args()
                
                
if __name__ == '__main__':
    args = process_commands()
                
    result = []
    with open(args.scores, 'r') as s:
        for v in s:
            if float(v) < 0:
                result.append(POSITIVE)
            elif float(v) > 0:
                result.append(NEGATIVE)
            else:
                result.append(ZERO)
                
    with open(args.result_path, 'w') as fout:
        for item in result:
            fout.write(str(item) + "\n")              
