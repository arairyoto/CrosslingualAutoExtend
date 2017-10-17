# WordNetのlemma.count()を用いて各word,synset,lemmaの頻度を算出してtextファイル化
import os
import sys
#WordNet
import nltk
from nltk.corpus import WordNetCorpusReader
from nltk.corpus import wordnet as wn

import codecs

import util

class ForwardWNGeneralityExtractor:
    def __init__(self, folder, lang):
        self.folder = folder
        if lang in wn.langs():
            self.lang = lang
        else:
            print("language: '%s' is not supported, try another language" % lang)
        #initialize
        self.WordCounter = {}
        self.SynsetCounter = {}
        self.pos_list = ['a', 's', 'r', 'n', 'v']

    def main(self):

        ver = wn.get_version()
        print("RESOURCE: WN " + str(ver) + "\n")
        print("LANGUAGE: "+self.lang+"\n")
        print("TARGET: " + self.folder + "\n")

        self.extractWordsAndSynsetsGenerality(self.folder + "words.txt",self.folder + "synsets.txt",self.folder + "lemmas.txt")
        print("DONE")

    def extractWordsAndSynsetsGenerality(self, filenameWords, filenameSynsets,  filenameLemmas):
        #file
        fWords = codecs.open(filenameWords, 'w', 'utf-8')
        fSynsets = codecs.open(filenameSynsets, 'w', 'utf-8')
        fLemmas = codecs.open(filenameLemmas, 'w', 'utf-8')

        frequencyAllTold = 0

        for pos in self.pos_list:
            for synset in wn.all_synsets(pos=pos):
                synsetId = synset.name()
                self.SynsetCounter[synsetId] = 0

                fSynsets.write(synsetId+" ")

                for lemma in synset.lemmas():
                    frequencyAllTold += lemma.count()

                    wordId = lemma.name().lower()
                    fLemmas.write(synsetId+":"+wordId+" "+str(lemma.count())+"\n")

                    if wordId not in self.WordCounter:
                        self.WordCounter[wordId] = 0

                    self.SynsetCounter[synsetId] += lemma.count()
                    self.WordCounter[wordId] += lemma.count()

                fSynsets.write(str(self.SynsetCounter[synsetId])+"\n")

        for word, count in self.WordCounter.items():
            fWords.write(word+" "+str(count)+"\n")

        fWords.close()
        fSynsets.close()
        fLemmas.close()

        print("  Frequency all told: %d\n" % frequencyAllTold)
        print("  Words: %d\n" % len(self.wordCounter))
        print("  Synsets: %d\n" % len(self.synsetCounter))

if __name__ == '__main__':
    #path to output folder
    folder = '/Users/arai9814/Desktop/generality/'
    #language
    lang = 'eng'
    fwnge = ForwardWNGeneralityExtractor(folder, lang)
    fwnge.main()
