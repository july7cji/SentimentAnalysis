# -*- coding: utf-8 -*-
##################################################
#
#      Filename: preprocess.py
#
#        Author: Chen
#   Description: ---
#        Create: 2017-08-05 19:35:07
# Last Modified: 2017-08-05 19:35:07
##################################################

import xml.dom.minidom as xmlparser
import jieba

def decodeXML(url):
    dom = xmlparser.parse(url)
    root = dom.documentElement

    pos = []
    neg = []

    sentencelists = root.getElementsByTagName("sentences")
    for sentencelist in sentencelists:
        sentences = sentencelist.getElementsByTagName("sentence")
        for sentence in sentences:
            text = sentence.getElementsByTagName("text")[0].childNodes[0].data
            options = sentence.getElementsByTagName("Opinions")
            if options:
                option = options[0].getElementsByTagName("Opinion")
                if option[0].hasAttribute("polarity"):
                    polarity = option[0].getAttribute("polarity")
                    if polarity == "positive":
                        label = 1
                    elif polarity == "negative":
                        label = 2
                    else:
                        print "polarity error occured"
                        continue
                    line = str(label) + " " + text
                    #print line
                    if label == 1:
                        pos.append(line)
                    else:
                        neg.append(line)
    return pos, neg

def writeFile(pos, neg, basedir):
    with open(basedir + "pos.txt", 'a')as p:
        for line in pos:
            p.write(line.encode("utf-8") + "\n")
    with open(basedir + "neg.txt", 'a')as n:
        for line in neg:
            n.write(line.encode("utf-8") + "\n")

def segmenter(input_, output_, stopwordsPath=""):
    stopwords = []
    if stopwordsPath != "":
        with open(stopwordsPath, 'r')as fin:
            for word in fin:
                word = word.strip()
                stopwords.append(word)
    with open(input_, 'r')as fin, open(output_, 'w')as fout:
        for line in fin:
            line = line.strip()
            line = line.split(' ', 1)
            label = line[0]
            sentence = line[1]
            words = jieba.lcut(sentence)
            if stopwords: # performance problem
                words_ = [x for x in words if x not in stopwords]
                words = words_
            fout.write(label + " ")
            for w in words:
                if w.strip() != "":
                    fout.write(w.encode("utf-8") + " ")
            fout.write("\n")

if __name__=="__main__":
    pos,neg = decodeXML("/home/bruce/dataset/sentimentAnalysis_corpus/phone/Chinese_phones_training.xml")
    writeFile(pos, neg, "/home/bruce/dataset/sentimentAnalysis_corpus/")
    pos,neg = decodeXML("/home/bruce/dataset/sentimentAnalysis_corpus/camera/camera_corpus/camera_training.xml")
    writeFile(pos, neg, "/home/bruce/dataset/sentimentAnalysis_corpus/")
    pos,neg = decodeXML("/home/bruce/dataset/sentimentAnalysis_corpus/phone/CH_PHNS_SB1_TESTGold_.xml")
    writeFile(pos, neg, "/home/bruce/dataset/sentimentAnalysis_corpus/test.")
    pos,neg = decodeXML("/home/bruce/dataset/sentimentAnalysis_corpus/camera/CH_CAME_SB1_TESTGold.xml")
    writeFile(pos, neg, "/home/bruce/dataset/sentimentAnalysis_corpus/test.")
    segmenter("/home/bruce/dataset/sentimentAnalysis_corpus/pos.txt", "/home/bruce/dataset/sentimentAnalysis_corpus/pos.txt.train")
    segmenter("/home/bruce/dataset/sentimentAnalysis_corpus/neg.txt", "/home/bruce/dataset/sentimentAnalysis_corpus/neg.txt.train")
    segmenter("/home/bruce/dataset/sentimentAnalysis_corpus/test.pos.txt", "/home/bruce/dataset/sentimentAnalysis_corpus/pos.txt.test")
    segmenter("/home/bruce/dataset/sentimentAnalysis_corpus/test.neg.txt", "/home/bruce/dataset/sentimentAnalysis_corpus/neg.txt.test")
