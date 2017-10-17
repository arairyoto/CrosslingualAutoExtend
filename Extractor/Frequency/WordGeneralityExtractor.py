# Word2vecからそれぞれの単語の頻度を抽出します
import os
import sys
#WordNet
import nltk
from nltk.corpus import WordNetCorpusReader
from nltk.corpus import wordnet as wn

from gensim.models import word2vec
from gensim.models import KeyedVectors

import codecs

import util

def normalize(lemma):
    return lemma.replace("_", " ").replace("")

class WordGeneralityExtractor:
    def __init__(self, file_name, folder, lang):
        self.file_name = file_name #where word2vec model exists
        self.folder = folder
        if lang in wn.langs():
            self.lang = lang
        else:
            print("language: '%s' is not supported, try another language" % lang)
        #initialize
        self.WordGenerality = {}
        self.pos_list = ['a', 's', 'r', 'n', 'v']
        self.model = word2vec.Word2Vec.load(self.file_name)

    def main(self):
        ver = wn.get_version()
        print("RESOURCE: WN " + str(ver) + "\n")
        print("LANGUAGE: "+self.lang+"\n")
        print("VECTORS: " + self.file_name + "\n")
        print("TARGET: " + self.folder + "\n")
        self.extractWordGenerality(self.folder + "words.txt")
        print("DONE")


    def extractWordGenerality(self, filenameWords):
        #file
        fWords = codecs.open(filenameWords, 'w', 'utf-8')

        f =283715
        CounterAll = 0

        for pos in self.pos_list:
            for word in wn.all_lemma_names(pos=pos, lang=self.lang):
                wordId = word.lower()
                if wordId not in self.WordGenerality:
                    if wordId in self.model.wv.vocab:
                        self.WordGenerality[wordId] = self.model.wv.vocab[wordId].count
                        CounterAll += self.model.wv.vocab[wordId].count
                    else:
                        self.WordGenerality[wordId] = 0

        for word in self.WordGenerality.keys():
            temp = self.WordGenerality[word]
            self.WordGenerality[word] = 1.0*temp*f/CounterAll
            fWords.write(word+" "+str(self.WordGenerality[word])+"\n")

        fWords.close()


if __name__ == '__main__':
    #path to input word embeddings
    file_name = '/Users/arai9814/model/frwiki.gensim'
    #path to output folder
    folder = '/Users/arai9814/Desktop/Test_gen/Test_fra/'
    #language
    lang = 'fra'
    #List of Languages
    #     ['als', 'arb', 'cat', 'cmn', 'dan', 'eng', 'eus', 'fas',
    # 'fin', 'fra', 'fre', 'glg', 'heb', 'ind', 'ita', 'jpn', 'nno',
    # 'nob', 'pol', 'por', 'spa', 'tha', 'zsm']
    wge = WordGeneralityExtractor(file_name, folder, lang)
    wge.main()
