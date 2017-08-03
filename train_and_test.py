# -- preprocess -- #                                                                                                                                                  
training_set=/home/july7/workspace/classifier/Sentiment_analysis/SentimentAnalysis/Jingdong_NB_4000
python pre_process.py --input_pos ${training_set}/pos/pos.txt.pro --input_neg ${training_set}/neg/neg.txt.pro --train_pos ${training_set}/pos/pos.txt.train --train_neg ${training_set}/neg/neg.txt.train --test_pos ${training_set}/pos/pos.txt.test --test_neg ${training_set}/neg/neg.txt.test
 
# -- rnnlm -- #
mkdir rnnlm
cd rnnlm
#wget https://f25ea9ccb7d3346ce6891573d543960492b92c30.googledrive.com/host/0ByxdPXuxLPS5RFM5dVNvWVhTd0U/rnnlm-0.4b.tgz
wget http://www.fit.vutbr.cz/~imikolov/rnnlm/rnnlm-0.3e.tgz
tar -xvf rnnlm-0.3e.tgz
g++ -lm -O3 -march=native -Wall -funroll-loops -ffast-math -c rnnlmlib.cpp
g++ -lm -O3 -march=native -Wall -funroll-loops -ffast-math rnnlm.cpp rnnlmlib.o -o rnnlm
 
 
# construct positive language model
rm -rf neg.model
rm -rf pos.model
#sed '1,200d' means deletes line 1 to 200
head -n 200 ${training_set}/pos/pos.txt.train > val.txt
cat ${training_set}/pos/pos.txt.train | sed '1,200d' > train.txt
./rnnlm -rnnlm pos.model -train train.txt -valid val.txt -hidden 50 -direct-order 3 -direct 200 -class 100 -debug 2 -bptt 4 -bptt-block 10 -binary
 
# constructs negative language model
head -n 200 ${training_set}/neg/neg.txt.train > val.txt
cat ${training_set}/neg/neg.txt.train | sed '1,200d' > train.txt
./rnnlm -rnnlm neg.model -train train.txt -valid val.txt -hidden 50 -direct-order 3 -direct 200 -class 100 -debug 2 -bptt 4 -bptt-block 10 -binary
 
#adds id, from 0
cat ${training_set}/pos/pos.txt.test ${training_set}/neg/neg.txt.test | nl -v0 -s' ' -w1 > test.txt
./rnnlm -rnnlm pos.model -test test.txt -debug 0 -nbest > model_pos_score.txt
./rnnlm -rnnlm neg.model -test test.txt -debug 0 -nbest > model_neg_score.txt
 
# predicts the probability of each sentence, by the model of positive and negative, then outputs  result 
mkdir ../scores
paste model_pos_score.txt model_neg_score.txt | awk '{print $1/$2;}' > ../scores/RNNLM

# ajusts the scope of datas, then checks the accuracy
cd ..
python normalize.py --input scores/RNNLM --output scores/RNNLM --type rnnlm
python evaluate.py --test_pos ${training_set}/pos/pos.txt.test --scores scores/RNNLM
 
# -- word2vec - sentence vectors -- #
git clone https://github.com/shaform/word2vec.git
cd word2vec
git checkout doc2vec
make
 
# adds line num, and prefix '@@SS-', shuffles data, trains the word2vec model
cat ${training_set}/pos/pos.txt.train ${training_set}/neg/neg.txt.train ${training_set}/pos/pos.txt.test ${training_set}/neg/neg.txt.test | nl -v0 -s' ' -w1 | sed 's/^/@@SS-/' | shuf > all.txt
time ./word2vec -train all.txt -output vectors.txt -cbow 0 -size 400 -window 10 -negative 5 -hs 1 -sample 1e-3 -threads 24 -binary 0 -iter 20 -min-count 1 -sentence-vectors 1
grep '@@SS-' vectors.txt | sed -e 's/^@@SS-//' | sort -n > sentence_vectors.txt
 
mkdir ../liblinear
cd ../liblinear
wget -O liblinear.zip http://www.csie.ntu.edu.tw/~cjlin/cgi-bin/liblinear.cgi?+http://www.csie.ntu.edu.tw/~cjlin/liblinear+zip
unzip liblinear.zip
cd *
make
cp train predict ..
cd ../../word2vec
 
python3 ../transform.py --input sentence_vectors.txt --output sentence_features.txt
python ../train.py --features sentence_features.txt --train_pos ${training_set}/pos/pos.txt.train --train_neg ${training_set}/neg/neg.txt.train --test_pos ${training_set}/pos/pos.txt.test --output_train train.txt --output_test test.txt
 
rm model.logreg
../liblinear/train -s 0 train.txt model.logreg                     
../liblinear/predict -b 1 test.txt model.logreg out.logreg
 
#deletes first line of out.logreg, splits by space, gets the 3rd col. saves to DOC2VEC
sed '1d' out.logreg | cut -d' ' -f3 > ../scores/DOC2VEC
cd ..
python normalize.py --input scores/DOC2VEC --output scores/DOC2VEC --type logreg
 
python evaluate.py --test_pos ${training_set}/pos/pos.txt.test --scores scores/DOC2VEC
 
# -- TF-IDF -- #
mkdir tfidf
cd tfidf
cat ${training_set}/pos/pos.txt.train ${training_set}/neg/neg.txt.train ${training_set}/pos/pos.txt.test ${training_set}/neg/neg.txt.test > all.txt
python ../tfidf.py --input all.txt --output features.txt
python ../train.py --features features.txt --train_pos ${training_set}/pos/pos.txt.train --train_neg ${training_set}/neg/neg.txt.train --test_pos ${training_set}/pos/pos.txt.test --output_train train.txt --output_test test.txt
 
rm model.logreg
../liblinear/train -s 0 train.txt model.logreg
../liblinear/predict -b 1 test.txt model.logreg out.logreg
 
sed '1d' out.logreg | cut -d' ' -f3 > ../scores/TFIDF
cd ..
python normalize.py --input scores/TFIDF --output scores/TFIDF --type logreg
 
python evaluate.py --test_pos ${training_set}/pos/pos.txt.test --scores scores/TFIDF
 
# -- TOTAL -- #
 
paste scores/RNNLM scores/DOC2VEC scores/TFIDF | awk '{print ($1+$2+$3)/3;}' > scores/TOTAL
python evaluate.py --test_pos ${training_set}/pos/pos.txt.test --scores scores/TOTAL     
