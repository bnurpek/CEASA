import json
import os

import nltk


class Depparse:
    def __init__(self, nlp_wrapper, humanLikeVerbs, stopWords):
        self.wrapper = nlp_wrapper
        self.humanLikeVerbs = humanLikeVerbs
        self.stopWords = stopWords
    
    def corenlp_dparse(self, text):
        annot_doc = self.wrapper.annotate(
            text=text,
            properties={
                'annotators':'depparse',
                'outputFormat':'json',
            }
        )
        return annot_doc
    
    def get_subjects(self, annot_doc):
        nsubjects = []  #özneler
        governorGlosses = []    #fiiller
        dependency = ['amod', 'advmod', 'case', 'nmod:poss', 'compound']     #sıfat ya da aitlik kelimeleri
        annot_doc_sentences = annot_doc['sentences']
        for sentence in annot_doc_sentences:
            words = sentence['basicDependencies']
            for idx, word in enumerate(words):
                if word['dep'] == 'nsubj' and word['dependentGloss'].lower() not in self.stopWords and word['governorGloss'].lower() in self.humanLikeVerbs:
                    subj = [word['dependentGloss']]
                    i = idx - 1
                    while words[i]['dep'] in dependency:
                        subj.append(words[i]['dependentGloss'])
                        i -= 1
                    subj.reverse()
                    subj = " ".join(subj)
                    nsubjects.append(subj)
                    governorGlosses.append(word['governorGloss'])
        subjects = (list(set(nsubjects)))
        return subjects, governorGlosses
