import json
import os

import nltk
from nltk.tokenize import WordPunctTokenizer
from preproccessing import Preprocessing
from pycorenlp import StanfordCoreNLP


class Coreference:
    def __init__(self, nlp_wrapper, stopWords):
        self.wrapper = nlp_wrapper
        self.stopWords = stopWords
    
    def corenlp_coref(self, text):
        annot_doc = self.wrapper.annotate(
            text=text,
            properties={
                'annotators':'coref',
                'coref.algorithm':'statistical',
                'outputFormat':'json',
            }
        )
        if type(annot_doc) == str.__class__:
            annot_doc = dict(annot_doc)
            #annot_doc = json.load(annot_doc)
        return annot_doc
    
    def replaceCorefs(self, corefs, sentences, nltkChar, depparseChar):
        for id in corefs:
            name = ""
            for i in range(len(corefs[id])):
                if corefs[id][i]['text'] in nltkChar+depparseChar:
                    name = corefs[id][i]['text']
                    name = name.replace('the ','').replace('The ', '').replace('a ', '').replace('A ', '')
                    break
            if name != "":
                for syn in corefs[id]:
                    print(f"\n{syn['text']} -> {name}")
                    sentence = sentences[syn['sentNum'] - 1]
                    print(f"Orijinal sentence: {sentence}")
                    new_sentence = sentence.replace(" " + syn['text'] + " ", " " + name + " ")
                    print(f"After coref: {new_sentence}")
                    sentences[syn['sentNum'] - 1] = new_sentence
        new_text = " ".join(sentences)
        return new_text