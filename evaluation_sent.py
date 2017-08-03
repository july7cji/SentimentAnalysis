#-*- coding: utf-8 -*-                                                                                                                                                
import argparse
# computes accuracy for test datas
def process_commands():
    parser = argparse.ArgumentParser()
    parser.add_argument('--result', required=True)
    parser.add_argument('--label', required=True)
         
    return parser.parse_args()
         
if __name__=="__main__":
    args = process_commands()
    with open(args.result,'r')as f1, open(args.label, 'r')as f2:
        right = 0
        allsum =0
        result = []
        labels = []
        for line in f1:
            line = line.strip()
            res = int(line)
            result.append(res)
        for line in f2:
            line = line.strip()
            label = int(line)
            labels.append(label)
        if len(result) != len(labels):
            print "error"
            exit()
        else:
            for i in range(len(result)):
                if labels[i] != 0:
                    allsum += 1
                    if labels[i] == result[i]:
                        right += 1
        print ("accuracy: " + str(float(right) / float(allsum)))
