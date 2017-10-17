# それぞれの言語についてAutoExtendで計算する際に必要なデータを作成します
import os
import sys
#WordNet
import nltk
from nltk.corpus import WordNetCorpusReader
from nltk.corpus import wordnet as wn

import codecs

import util

def normalize(lemma):
    return lemma.replace("_", " ").replace("")

class BackwardWNGeneralityExtractor:
    def __init__(self, file_name, folder, lang):
        self.file_name = file_name
        self.folder = folder
        if lang in wn.langs():
            self.lang = lang
        else:
            print("language: '%s' is not supported, try another language" % lang)
        #initialize
        self.WordIndex = {}
        self.SynsetIndex = {}
        self.pos_list = ['a', 's', 'r', 'n', 'v']
        self.Shared = util.Shared()

    def main(self):
        # if self.file_name.split(".")[-1] is "bin":
        #     self.Shared.loadGoogleModel(self.file_name)
        # elif self.file_name.split(".")[-1] is "txt":
        #     self.Shared.loadTxtModel(self.file_name)
        # else:
        #     self.Shared.loadModel(self.file_name)
        self.Shared.loadTxtModel(self.file_name)
        ver = wn.get_version()
        print("RESOURCE: WN " + str(ver) + "\n")
        print("LANGUAGE: "+self.lang+"\n")
        print("VECTORS: " + self.folder + "\n")
        print("TARGET: " + self.folder + "\n")
        self.extractWordsAndSynsets(self.folder + "words.txt",self.folder + "synsets.txt",self.folder + "lemmas.txt")

        print("DONE")


    def extractWordsAndSynsets(self, filenameWords, filenameSynsets,  filenameLemmas):
        #file
        fWords = codecs.open(filenameWords, 'w', 'utf-8')
        fSynsets = codecs.open(filenameSynsets, 'w',  'utf-8')
        fLemmas = codecs.open(filenameLemmas, 'w',  'utf-8')

        wordCounter = 0
        wordCounterAll = 0
        synsetCounter = 0
        synsetCounterAll = 0
        lemmaCounter = 0
        lemmaCounterAll = 0

        ovv = []

        for pos in self.pos_list:
            for word in wn.all_lemma_names(pos=pos, lang=self.lang):
                wordCounterAll += 1
                self.WordIndex[word.lower()] = wordCounterAll
                fWords.write(word+" ")
                synsetInWord = 0
                for synset in wn.synsets(word, lang=self.lang):
                    lemmaCounterAll += 1
                    synsetId = synset.name()

                    if self.Shared.in_vocab(synsetId):
                        synsetInWord += 1
                        if synsetId not in self.SynsetIndex:
                            fSynsets.write(synsetId + " " + self.Shared.getVectorAsString(self.Shared.model[synsetId]) + "\n")
                            synsetCounter += 1
                            self.SynsetIndex[synsetId] = synsetCounter

                        lemmaCounter += 1
                        sensekey = synset.name()+':'+word

                        fWords.write(sensekey + ",")
                        fLemmas.write(str(self.SynsetIndex[synsetId]) + " " + str(wordCounterAll) + "\n")

                        #try:
                            #lemma name
                            #sensekey = wn.lemma(synset.name()+'.'+word, lang=self.lang).key()

                            #fWords.write(sensekey + ",")
                            #fLexemes.write(str(self.SynsetIndex[synsetId]) + " " + str(wordCounterAll) + "\n")
                        #except:
                            # print(synset.name()+'.'+word)
                    else:
                        if synsetId not in oov:
                            ovv.append(synsetId)


                fWords.write("\n")
                if synsetInWord is not 0:
                    wordCounter += 1
                else:
                    self.WordIndex[word] = -1

        fWords.close()
        fSynsets.close()
        fLemmas.close()
        print("   Words: %d / %d\n" % (wordCounter, wordCounterAll))
        print("  Synset: %d / %d\n" % (synsetCounter, synsetCounter + len(ovv)))
        print("  Lemmas: %d / %d\n" % (lemmaCounter, lemmaCounterAll))


if __name__ == '__main__':
    #path to input word embeddings
    file_name = '/Users/arai9814/Desktop/generality/synsets.txt'
    #path to output folder
    folder = '/Users/arai9814/Desktop/generality/Test_fra/'
    #language
    lang = 'fra'
    #List of Languages
    #     ['als', 'arb', 'cat', 'cmn', 'dan', 'eng', 'eus', 'fas',
    # 'fin', 'fra', 'fre', 'glg', 'heb', 'ind', 'ita', 'jpn', 'nno',
    # 'nob', 'pol', 'por', 'spa', 'tha', 'zsm']
    bwnge = BackwardWNGeneralityExtractor(file_name, folder, lang)
    bwnge.main()
