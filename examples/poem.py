from pychuck import *
import gensim.downloader as api
from numpy import interp

print("Loading Word2Vec model...")
wv = api.load('glove-wiki-gigaword-50')

s = SinOsc()
s >> dac

while True:
    word = input('word: ')
    for similar_word, _ in wv.most_similar(word, topn=10):
        print(similar_word)
        s.freq = interp(wv.key_to_index[similar_word], [0, 400000], [100, 1000])
        Dur(200, "ms") >> now
