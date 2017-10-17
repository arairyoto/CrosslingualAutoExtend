# Python Version of WordNetExtractor.java
import os
import sys
#WordNet
import nltk
from nltk.corpus import WordNetCorpusReader
from nltk.corpus import wordnet as wn

import codecs

import util

class WNDExtractor:
    def __init__(self, file_name, folder, wnd_file, wndh_file):
        self.dictS = {}
        self.dictC = {}

        self.hype = {}
        self.hypo = {}

        self.loadWNDFile(wnd_file)
        self.loadWNDHFile(wndh_file)

        self.file_name = file_name
        self.folder = folder
        #initialize
        self.SynsetIndex = {}
        self.CategoryIndex = {}
        self.Shared = util.Shared()

    def main(self):
        print("Loading vector model...")
        self.Shared.loadTxtModel(self.file_name)
        print("    DONE!!")

        self.extractSynsetsAndCategories(self.folder + "synsets.txt",self.folder + "categories.txt",self.folder + "lexemes.txt")
        self.extractCategoryRelations(self.folder + "relation.txt")

        print("DONE")

    def loadWNDFile(self, wnd_file):
        print("loading WNDomains file...")
        f = codecs.open(wnd_file, "r","utf-8-sig")
        lines = f.readlines()
        for line in lines:
            temp = line.strip("\n").split(" ")
            # print(temp)
            pos = temp[0].split("-")[1]
            offset = temp[0].split("-")[0]
            categories = temp[2:]
            try:
                synset = wn._synset_from_pos_and_offset(pos, int(offset)).name()
                self.dictS[synset] = categories
                for category in categories:
                    if category not in self.dictC:
                        self.dictC[category] = []
                    if synset not in self.dictC[category]:
                        self.dictC[category].append(synset)
            except:
                continue
        f.close()
        print("    DONE!!")

    def loadWNDHFile(self, wndh_file):
        print("loading WNDomainsHierarchy file...")
        f = codecs.open(wndh_file, "r","utf-8-sig")
        lines = f.readlines()
        for line in lines:
            temp = line.strip("\n").strip("\r").split(" ")
            up = temp[0]
            downs = temp[1].split(",")
            if up in self.dictC:
                self.hypo[up] = []
                for down in downs:
                    if len(down) is not 0:
                        if down in self.dictC:
                            self.hypo[up].append(down)
            for down in downs:
                if len(down) is not 0:
                    if down not in self.hype:
                        self.hype[down] = []
                    if down in self.dictC:
                        if up in self.dictC:
                            self.hype[down].append(up)
        f.close()
        print("    DONE!!")

    def extractSynsetsAndCategories(self, filenameSynsets, filenameCategories,  filenameLexemes):
        #file
        fSynsets = codecs.open(filenameSynsets, 'w', 'utf-8')
        fCategories = codecs.open(filenameCategories, 'w', 'utf-8')
        fLexemes = codecs.open(filenameLexemes, 'w', 'utf-8')

        synsetCounter = 0
        synsetCounterAll = 0
        categoryCounter = 0
        categoryCounterAll = 0
        lexemCounter = 0
        lexemCounterAll = 0

        for category in self.dictC.keys():
            categoryCounterAll += 1
            categoryId = category
            self.CategoryIndex[categoryId] = categoryCounterAll

            fCategories.write(categoryId+" ")

            synsetInCategory = 0

            for synset in self.dictC[category]:
                lexemCounterAll += 1
                synsetId = synset

                synsetInCategory += 1
                if self.Shared.in_vocab(synsetId):
                    synsetInCategory += 1
                    if synsetId not in self.SynsetIndex:
                        fSynsets.write(synsetId + " " + self.Shared.getVectorAsString(self.Shared.model[synsetId]) + "\n")
                        synsetCounter += 1
                        self.SynsetIndex[synsetId] = synsetCounter

                    lexemCounter += 1
                    #lemma name
                    sensekey = category+':'+synset

                    fCategories.write(sensekey + ",")
                    fLexemes.write(str(self.SynsetIndex[synsetId]) + " " + str(categoryCounterAll) + "\n")

            fCategories.write("\n")
            if synsetInCategory is not 0:
                categoryCounter += 1
            else:
                self.CategoryIndex[categoryId] = -1

        fSynsets.close()
        fCategories.close()
        fLexemes.close()


    def extractCategoryRelations(self, filename):
        f = codecs.open(filename, 'w', 'utf-8')

        for up in self.hypo.keys():
            for down in self.hypo[up]:
                if len(down) is not 0:
                    f.write(str(self.CategoryIndex[up])+" "+str(self.CategoryIndex[down])+"\n")
        f.close()
        print("Extracted done!\n")

if __name__ == '__main__':
    file_name = 'multi_ae\\ae\\synsets.txt'
    #path to output folder
    folder = 'Test\\'
    fwne = WNDExtractor(file_name, folder, "C:\\Users\\Ryoto\\Desktop\\wn-domains-3.2\\for_wn30\\wordnet-domains-3.2-wordnet-3.0.txt", "C:\\Users\\Ryoto\\Desktop\\wn-domains-3.2\\for_wn30\\wn-domains-hierarchy.txt")
    fwne.main()
