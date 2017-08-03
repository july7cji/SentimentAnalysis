#/bin/bash                                   
comment_path=/home/july7/workspace/classifier/Sentiment_analysis/SentimentAnalysis/sentiment_analysis
rnnlm_path=/home/july7/workspace/classifier/Sentiment_analysis/SentimentAnalysis/sentiment_analysis/rnnlm
training_set=/home/july7/workspace/classifier/Sentiment_analysis/SentimentAnalysis/Book_del_4000
cd $comment_path
python split_sentence.py --input test.txt --output /tmp/tmp.txt
python segment_sentences.py --input /tmp/tmp.txt --output /tmp/tmp_out.txt  
#cat /tmp/tmp_out.txt | nl -v0 -s' ' -w1 > $rnnlm_path/test.txt
cat /tmp/tmp.txt | nl -v0 -s' ' -w1 > $rnnlm_path/test.txt
#cat test.txt | nl -v1 -s' ' -w1 > $rnnlm_path/test.txt
cd $rnnlm_path
./rnnlm -rnnlm ./pos.model -test ./test.txt -debug 0 -nbest > ./model_pos_score.txt
./rnnlm -rnnlm ./neg.model -test ./test.txt -debug 0 -nbest > ./model_neg_score.txt
 
paste ./model_pos_score.txt ./model_neg_score.txt | awk '{print $1/$2;}' > ../scores/RNNLM
cd ..

python normalize.py --input scores/RNNLM --output scores/RNNLM --type rnnlm
python sentimentAnalyzer.py --scores scores/RNNLM --result_path result_rnn.txt
 
cd word2vec

cat ${training_set}/pos/pos.txt.train ${training_set}/neg/neg.txt.train ${training_set}/pos/pos.txt.test ${training_set}/neg/neg.txt.test | nl -v0 -s' ' -w1 | sed 's/^/@@SS-/' | shuf > all.txt
# deletes null line
sed '/^$/d' /tmp/tmp_out.txt > /tmp/tmp.txt
sed '/^\s*$/d' /tmp/tmp.txt > /tmp/tmp_out.txt

# add prefix "@@TT" to the corpus tobe classified, in order to pick up these datas easier.
cat /tmp/tmp_out.txt | nl -v0 -s' ' -w1 | sed 's/^/@@TT-/' | shuf >> all.txt
# trains a word2vec model, including words' vector and sentences(each sentence in 'all.txt') vector
time ./word2vec -train all.txt -output vectors.txt -cbow 0 -size 400 -window 10 -negative 5 -hs 1 -sample 1e-3 -threads 24 -binary 0 -iter 20 -min-count 1 -sentence-vectors 1
# finds sentences(including training and testing set)' vector from 'vectors.txt', deletes prefix and sorts the sentences
grep '@@SS-' vectors.txt | sed -e 's/^@@SS-//' | sort -n > sentence_vectors.txt
grep '@@TT-' vectors.txt | sed -e 's/^@@TT-//' | sort -n > dest_vectors.txt
 
# adds id to the datas
python3 ../transform.py --input sentence_vectors.txt --output sentence_features.txt
python3 ../transform.py --input dest_vectors.txt --output dest_features.txt
# splits the datas into training and testing sets, sets label
python ../train.py --features sentence_features.txt --train_pos ${training_set}/pos/pos.txt.train --train_neg ${training_set}/neg/neg.txt.train --test_pos ${training_set}/pos/pos.txt.test --output_train train.txt --output_test test.txt
# removes the line number
cat dest_features.txt |  sed 's/^[0-9]*//g' > dest_features2.txt
# add label -1 (tobe classified)
sed 's/^/-1&/g' dest_features2.txt > dest.txt
# trains a lr model
rm model.logreg
../liblinear/train -s 0 train.txt model.logreg
../liblinear/predict -b 1 test.txt model.logreg out.logreg
../liblinear/predict -b 1 dest.txt model.logreg out2.logreg

sed '1d' out.logreg | cut -d' ' -f3 > ../scores/DOC2VEC
sed '1d' out2.logreg | cut -d' ' -f3 > ../scores/DOC2VEC_DEST
 
cd ..
python normalize.py --input scores/DOC2VEC --output scores/DOC2VEC --type logreg
python normalize.py --input scores/DOC2VEC_DEST --output scores/DOC2VEC_DEST --type logreg
 
python evaluate.py --test_pos ${training_set}/pos/pos.txt.test --scores scores/DOC2VEC
python sentimentAnalyzer.py --scores scores/DOC2VEC_DEST --result_path result_w2v.txt
# -- TF-IDF -- #
cd tfidf
cat ${training_set}/pos/pos.txt.train ${training_set}/neg/neg.txt.train ${training_set}/pos/pos.txt.test ${training_set}/neg/neg.txt.test /tmp/tmp_out.txt  > all.txt
python ../tfidf.py --input all.txt --output features.txt
# gets vectorized datas
python getdest.py --input features.txt --originalInput /tmp/tmp_out.txt --output dest.txt
# removes line num.
cat dest.txt |  sed 's/^x//g' > dest2.txt
# add -1
sed 's/^/-1&/g' dest2.txt > dest.txt
 
python ../train.py --features features.txt --train_pos ${training_set}/pos/pos.txt.train --train_neg ${training_set}/neg/neg.txt.train --test_pos ${training_set}/pos/pos.txt.test --output_train train.txt --output_test test.txt
 
rm model.logreg
../liblinear/train -s 0 train.txt model.logreg
../liblinear/predict -b 1 test.txt model.logreg out.logreg
../liblinear/predict -b 1 dest.txt model.logreg out2.logreg
 
sed '1d' out.logreg | cut -d' ' -f3 > ../scores/TFIDF
sed '1d' out2.logreg | cut -d' ' -f3 > ../scores/TFIDF_DEST
 
cd ..
python normalize.py --input scores/TFIDF --output scores/TFIDF --type logreg
python normalize.py --input scores/TFIDF_DEST --output scores/TFIDF_DEST --type logreg
 
python evaluate.py --test_pos ${training_set}/pos/pos.txt.test --scores scores/TFIDF
python sentimentAnalyzer.py --scores scores/TFIDF_DEST --result_path result_tfidf.txt
 
# -- TOTAL -- #
paste scores/RNNLM scores/DOC2VEC_DEST scores/TFIDF_DEST | awk '{print ($1+$2+$3)/3;}' > scores/TOTAL
python sentimentAnalyzer.py --scores scores/TOTAL --result_path result_total.txt            
