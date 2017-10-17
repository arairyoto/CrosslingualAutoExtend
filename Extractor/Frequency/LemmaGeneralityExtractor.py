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

class LemmaGeneralityExtractor:
    def __init__(self, synset_file, word_file, test_synset_file, test_word_file, folder):
        self.S_dict = self.load_dict(synset_file)
        self.W_dict = self.load_dict(word_file)
        self.L_dict = {}

        self.alpha = 0.01

        self.test_synset_file = test_synset_file
        self.test_word_file = test_word_file

        self.folder = folder

    def load_dict(self, file_name):
        f = codecs.open(file_name, 'r', 'utf-8')
        line = f.readline()
        result = {}

        while line:
            temp = line.strip().split(" ")
            result[temp[0]] = float(temp[1])
            line = f.readline()
        f.close()

        return result

    def main(self):
        print("START!!")
        fSynsetTest = codecs.open(self.test_synset_file, 'r', 'utf-8')
        fWordTest = codecs.open(self.test_word_file, 'r', 'utf-8')

        synset_tests = []
        synset_lines = fSynsetTest.readlines()
        for line in synset_lines:
            temp = line.strip("\n").strip(",").split(" ")
            synset = temp[0]
            words = temp[1].split(",")
            synset_tests.append([synset, words])
        print("Synset Test data READY!!")

        word_tests = []
        word_lines = fWordTest.readlines()
        for line in word_lines:
            temp = line.strip("\n").strip(",").split(" ")
            word = temp[0]
            synsets = temp[1].split(",")
            word_tests.append([word, synsets])
        print("Word Test data READY!!")

        for i in range(1000):
            self.train(synset_tests, word_tests)
            if (i%100==0):
                print("%d /1000 DONE!!" % i)
        self.save_model()
        print("DONE")

    def train(self, synset_tests, word_tests):
        # synset test
        for test in synset_tests:
            y = 0
            synset = test[0]
            words = test[1]
            #forward
            for word in words:
                if word in self.W_dict:
                    lemma = synset+":"+word
                    if lemma not in self.L_dict:
                        self.L_dict[lemma] = 0
                    y += self.L_dict[lemma]
            if synset in self.S_dict:
                delta = y-self.S_dict[synset]
            else:
                delta = 0
            #backward
            for word in words:
                if word in self.W_dict:
                    lemma = synset+":"+word
                    if (self.L_dict[lemma] - self.alpha*delta)>0:
                        self.L_dict[lemma] -= self.alpha*delta
                    else:
                        self.L_dict[lemma] = 0
        # word test
        for test in word_tests:
            y = 0
            word = test[0]
            synsets = test[1]
            #forward
            for synset in synsets:
                if synset in self.S_dict:
                    lemma = synset+":"+word
                    if lemma not in self.L_dict:
                        self.L_dict[lemma] = 0
                    y += self.L_dict[lemma]
            if word in self.W_dict:
                delta = y-self.W_dict[word]
            else:
                delta = 0
            #backward
            for synset in synsets:
                if synset in self.S_dict:
                    lemma = synset+":"+word
                    if (self.L_dict[lemma] - self.alpha*delta)>0:
                        self.L_dict[lemma] -= self.alpha*delta
                    else:
                        self.L_dict[lemma] = 0

    def save_model(self):
        f = codecs.open(self.folder+"lemmas.txt", 'w', 'utf-8')

        for lemma, count in self.L_dict.items():
            f.write(lemma+" "+str(count)+"\n")
        f.close()



if __name__ == '__main__':
    synset_file = "/Users/arai9814/Desktop/Test_gen/synsets.txt"
    word_file = "/Users/arai9814/Desktop/Test_gen/Test_fra/words.txt"
    test_synset_file = "/Users/arai9814/Desktop/Test_gen/Test_fra/synset_test.txt"
    test_word_file = "/Users/arai9814/Desktop/Test_gen/Test_fra/word_test.txt"
    folder = "/Users/arai9814/Desktop/Test_gen/Test_fra/"
    lge = LemmaGeneralityExtractor(synset_file, word_file, test_synset_file, test_word_file, folder)
    lge.main()
