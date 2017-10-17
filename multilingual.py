import os
import sys
import math
#WordNet
import nltk
from nltk.corpus import WordNetCorpusReader
from nltk.corpus import wordnet as wn

import matplotlib as mpl
import matplotlib.pyplot as plt

#dealing with japanese
mpl.rcParams['font.family'] = 'AppleGothic'

import numpy as np
import codecs
import csv

import util

class WSLObject:
    def __init__(self, name, attribute, lang = None):
        self.name = name
        self.attribute = attribute
        self.lang = lang


class MultilingualWordVector:
    def __init__(self, folder, langs):
        self.folder = folder
        self.langs = langs
        self.map = ['word', 'lemma']

        self.get = {}

        self.get[('synset', None)] = util.Shared()
        self.get[('synset', None)].loadTxtModel(self.folder+"/synsets.txt")

        self.get[('domain', None)] = util.Shared()
        self.get[('domain', None)].loadTxtModel(self.folder+"/domains.txt")

        for lang in langs:
            self.get[('word', lang)] = util.Shared()
            self.get[('word', lang)].loadTxtModel(self.folder+"/"+lang+"/words.txt")
            self.get[('lemma', lang)] = util.Shared()
            self.get[('lemma', lang)].loadTxtModel(self.folder+"/"+lang+"/lexemes.txt")
        print("MultilingualWordVector READY!")

    #e = [lang, attr(word or synset or lexeme), id]
    def relatedness(self, e1, e2):
        try:
            v1 = np.array(self.get[(e1.attribute, e1.lang)].model[e1.name])
            v2 = np.array(self.get[(e2.attribute, e2.lang)].model[e2.name])
            if (sum(v1*v1) is not 0) and (sum(v2*v2) is not 0):
                return sum(v1*v2)/np.sqrt(sum(v1*v1)*sum(v2*v2))
            else:
                return 0
        except:
            return -1
    def is_longer(self, e1, e2):
        try:
            v1 = np.array(self.get[(e1.attribute, e1.lang)].model[e1.name])
            v2 = np.array(self.get[(e2.attribute, e2.lang)].model[e2.name])
            if sum(v1*v1) > sum(v2*v2):
                return True
            else:
                return False
        except:
            return False

    def plot2D(self, file_name, descriptors):
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        for d in descriptors:
            try:
                v = self.get[(d.attribute, d.lang)].model[d.name]
                #ベクトルの1,2次元に射影
                x = v[0]
                y = v[1]
                w = d.name+'@'+d.lang
                ax.plot(x,y, ".")
                ax.annotate(w, xy=(x, y), size=10)
            except:
                continue
        plt.savefig(file_name+'.png' )
        plt.show()

    def plot2Dcsv(self, file_name, descriptors):
        f = codecs.open(file_name+'.txt','w','utf-8')
        for d in descriptors:
            try:
                v = self.get[(d.attribute, d.lang)].model[d.name]
                x = v[0]
                y = v[1]
                w = d.name+'@'+d.lang
                f.write(w+','+str(x)+','+str(y)+'\n')
            except:
                continue
        f.close()

    def plotCSV(self, file_name, descriptors):
        f = codecs.open(file_name+'.txt','w','utf-8')
        for d in descriptors:
            try:
                v = self.get[(d.attribute, d.lang)].model[d.name]
                w = d.name+'@'+d.lang
                f.write(w)
                for i in range(300):
                    f.write(","+str(v[i]))
                f.write('\n')
            except:
                continue
        f.close()

    def output_relatedness_matrix(self, file_name, descriptors):
        f = codecs.open(file_name+'.csv', 'w', 'utf-8')
        f.write(",")
        for d in descriptors:
            f.write(d.name+"::"+d.lang+"::"+d.attribute+",")
        f.write("\n")
        for d1 in descriptors:
            f.write(d1.name+"::"+d1.lang+"::"+d1.attribute+",")
            for d2 in descriptors:
                    f.write(str(self.relatedness(d1,d2)))
                    f.write(",")
            f.write("\n")
        f.close()
        print("OUTPUT FILE DONE!")

    def most_similar(self, target, target_attributes=['word', 'lemma', 'synset','domain'], target_pos=['n','v','s','a','r'],target_langs = None):
        result = {}
        if target_langs is None:
            langs = self.langs
        else:
            langs = set(target_langs)&set(self.langs)

        if 'synset' in target_attributes:
            for e in self.get[('synset', None)].model.keys():
                pos = e.split(".")[1]
                o = WSLObject(e, 'synset')
                temp = self.relatedness(o,target)
                if not math.isnan(temp):
                    if pos in target_pos:
                        result[e] = temp

        if 'domain' in target_attributes:
            for e in self.get[('domain', None)].model.keys():
                o = WSLObject(e, 'domain')
                temp = self.relatedness(o,target)
                if not math.isnan(temp):
                    result[e] = temp

        if 'lemma' in target_attributes:
            for lang in langs:
                for e in self.get[('lemma', lang)].model.keys():
                    pos = e.split(".")[1]
                    o = WSLObject(e, 'lemma', lang = lang)
                    temp = self.relatedness(o,target)
                    if not math.isnan(temp):
                        if pos in target_pos:
                            result[e+':'+lang] = temp

        if 'word' in target_attributes:
            for lang in langs:
                for e in self.get[('word', lang)].model.keys():
                    o = WSLObject(e, 'word', lang = lang)
                    temp = self.relatedness(o,target)

                    synsets = wn.synsets(e, lang=lang)
                    pos_set = set([synset.pos() for synset in synsets])
                    if not math.isnan(temp):
                        if len(set(target_pos) & pos_set) != 0:
                            result[e+':'+lang] = temp
        #ソート
        result = sorted(result.items() , key=lambda x: x[1], reverse=True)
        return result


def load_csv(file_name):
    result = []
    with codecs.open(file_name, 'r', 'utf-8') as f:
        reader = csv.reader(f)
        header = next(reader) #skip header

        for row in reader:
            name = row[0]
            attribute = row[1]
            lang = row[2]
            obj = WSLObject(name, attribute, lang)
            result.append(obj)
    print("LOADING CSV DONE!!")
    return result

#****************************************************Test****************************************************

#folder for 'ae'
folder = '/Users/arai9814/Desktop/ae'
# folder = 'ae'
langs = ['eng', 'jpn', 'fra']

#descriptor file_name
# file_name = 'descriptors_utf8.csv'

mwv = MultilingualWordVector(folder, langs)

# target = []
# target.append(WSLObject('sensitivity.n.01:感性','lemma','jpn'))
# target.append(WSLObject('sensibility.n.02:感性','lemma','jpn'))
# target.append(WSLObject('sensitivity.n.04:感性','lemma','jpn'))
# target.append(WSLObject('sense.n.05:感性','lemma','jpn'))
# target.append(WSLObject('sensitivity.n.05:感性','lemma','jpn'))

# target = [WSLObject('food','domain'),WSLObject('chocolate','word','eng')]
target = [WSLObject('food','domain')]

for t in target:
    f = open(t.name+"_a.txt","w")
    result = mwv.most_similar(t, target_attributes=['word','lemma'], target_pos=['a'])
    for v in result:
        f.write(v[0]+","+str(v[1])+"\n")
    f.close()
# descriptors = load_csv(file_name)

#generating relatedness matrix
# mwv.output_relatedness_matrix('geneva_positive_list', descriptors)
#generating 2d plot
# mwv.plotCSV('geneva_positive_list_all_dimention', descriptors)
