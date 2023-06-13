import os
from collections import Counter

import nltk
import pandas as pd
from coreference import Coreference
from nltk.tokenize import WordPunctTokenizer
from preproccessing import Preprocessing
from pycorenlp import StanfordCoreNLP
from relationAnalyzer import Analyzer
from saveFirestore import Database

from depparse import Depparse

STORIES_PATH = './stories'
FIXED_STORIES_PATH = './fixedStories'
os.makedirs('depparse', exist_ok=True)
os.makedirs('fixedStories', exist_ok=True)
os.makedirs('nltkPosTag', exist_ok=True)
os.makedirs('storyAfterCoref', exist_ok=True)
os.makedirs('Characters', exist_ok=True)
os.makedirs('figures', exist_ok=True)
os.makedirs('Relation Scores', exist_ok=True)

preprocessing = Preprocessing(STORIES_PATH, FIXED_STORIES_PATH)
preprocessing.fixAndSaveAll()
print("Stories fixed and saved.")

nlp_wrapper = StanfordCoreNLP('http://localhost:9000')

humanlikeverbs = open("humanLikeVerbs.txt").read().split(" ")
stopWords = open("stopwords.txt").read().split(", ")

depparse = Depparse(nlp_wrapper, humanlikeverbs, stopWords)
coref = Coreference(nlp_wrapper, stopWords)
database = Database()
analyzer = Analyzer()

for storyname in os.listdir(FIXED_STORIES_PATH):
    STORY_PATH = os.path.join(FIXED_STORIES_PATH, storyname)
    storyfile = open(STORY_PATH,'r',encoding="utf8")
    story = storyfile.read()
    storyfile.close()
    
    print("------------------------------------------------------------")
    print(f"Story name: {storyname}")

    annot_doc = depparse.corenlp_dparse(story)
    depparseChar, verbs = depparse.get_subjects(annot_doc)
    print(f'Depparse Result Subjects: {depparseChar}\n')

    depparsefile = open("./depparse/" + storyname, "w")
    depparsefile.write("\n".join(depparseChar))
    depparsefile.close()

    words = WordPunctTokenizer().tokenize(story)
    pos_tags = nltk.pos_tag(words)
    chunks = nltk.ne_chunk(pos_tags, binary=False) #either NE or not NE

    nltkChar =[]
    labels =[]
    for chunk in chunks:
        if hasattr(chunk,'label') and chunk.label() == 'PERSON':
            nltkChar.append(' '.join(c[0] for c in chunk))
    nltkChar = list(set(nltkChar))
    print(f"NLTK NER Result Entities labeled as PERSON: {nltkChar}")

    file = open("./nltkPosTag/" + storyname, "w")
    file.write("\n".join(nltkChar))
    file.close()

    print("------------------------------------------------------------")

    sentences = preprocessing.getAndFixSentences(story)
    print(f"Number of sentences: {len(sentences)}")

    annot_doc = coref.corenlp_coref(story)
    corefs = annot_doc['corefs']
    
    storyAfterCoref = coref.replaceCorefs(corefs, sentences, nltkChar, depparseChar)
    
    """
    # We canceled use of Animates results because it was observed that they decreased the success rate.
    """
    storyfile = open("./storyAfterCoref/" + storyname, "w", encoding="utf8")
    storyfile.write(storyAfterCoref)
    storyfile.close()

    lowerSentences = preprocessing.afterCorefGetLoweredSentences(storyAfterCoref)

    chars = database.saveCharacters(" ".join(lowerSentences), storyname, depparseChar, nltkChar, stopWords)

    pairsAndScores, pairsAndNumbers = analyzer.matchChars(chars)

    analyzer.analyzeForPairs(lowerSentences, pairsAndNumbers, pairsAndScores, storyname[:-4], database)