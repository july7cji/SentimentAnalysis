# -*- coding: utf-8 -*-
import jieba
import logging
import argparse
import random

#logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
def segment(filepath):
    wholeLine = []
    data = []
    with open(filepath, 'r')as fin:
        for line in fin.readlines():
            line = line.strip("\r\n")
            if line == "1" or line == "2":
                wholeLine = []
                wholeLine.append(str(line))
            elif line:
                tmplist = jieba.lcut(line)
                for each in tmplist:
                    wholeLine.append(each)
                data.append(wholeLine)
    print len(data)
    return data

def writeFile(filepath, data):
    with open(filepath, 'w')as fout:
        for line in data:
            for each in line:
                fout.write(each.encode('utf-8'))
                fout.write(" ")
            fout.write("\r\n")

def processCommands():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_pos', required=True)
    parser.add_argument('--input_neg', required=True)
    parser.add_argument('--train_pos', required=True)
    parser.add_argument('--train_neg', required=True)
    parser.add_argument('--test_pos', required=True)
    parser.add_argument('--test_neg', required=True)
    return parser.parse_args()

def output(filepath, sentence):
    with open(filepath, 'w') as fout:
        fout.writelines(sentence)


if __name__=="__main__":
    SEGMENT = False # true if segmenter is needed
    SETCORPUS = False # true if you want to generate training and testing datas
    negfile = "/home/july7/workspace/classifier/Sentiment_analysis/SentimentAnalysis/Book_del_4000/neg/neg.txt"
    negpro_file = negfile + ".pro"
    posfile = "/home/july7/workspace/classifier/Sentiment_analysis/SentimentAnalysis/Book_del_4000/pos/pos.txt"
    pospro_file = posfile + ".pro"
    if SEGMENT:
        writeFile(negpro_file, segment(negfile))
        writeFile(pospro_file, segment(posfile))
    
    #python pre_process.py --input_pos /root/jichen/SentimentAnalysis/Book_del_4000/pos/pos.txt.pro --input_neg /root/jichen/SentimentAnalysis/Book_del_4000/neg/neg.txt.pro --train_pos /root/jichen/SentimentAnalysis/Book_del_4000/pos/pos.txt.train --train_neg /root/jichen/SentimentAnalysis/Book_del_4000/neg/neg.txt.train --test_pos /root/jichen/SentimentAnalysis/Book_del_4000/pos/pos.txt.test --test_neg /root/jichen/SentimentAnalysis/Book_del_4000/neg/neg.txt.test
    if SETCORPUS:
        args = processCommands()
        pos = []
        neg = []
        with open(args.input_pos, 'r')as fpos:
            for line in fpos.readlines():
                label, sentence = line.split(' ', 1) # once
                if label != '1':
                    raise Exception("error, the input is not positive sentence!")
                pos.append(sentence)
        with open(args.input_neg, 'r')as fneg:
            for line in fneg.readlines():
                label, sentence = line.split(' ', 1)
                if label != '2':
                    raise Exception("error, the input is not negative sentence!")
                neg.append(sentence)

        random.shuffle(pos)
        length = len(pos) // 10 # 10% as testing corpus
        output(args.test_pos, pos[:length])
        output(args.train_pos, pos[length:])
        print "pos corpus finished"

        random.shuffle(neg)
        length = len(neg) // 10
        output(args.test_neg, neg[:length])
        output(args.train_neg, neg[length:])
        print "neg corpus finished"
