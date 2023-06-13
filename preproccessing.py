import os

import nltk
from nltk.tokenize import WordPunctTokenizer


class Preprocessing:
    def __init__(self, IN_PATH, OUT_PATH):
        self.IN_PATH = IN_PATH
        self.OUT_PATH = OUT_PATH
    
    def fixPunc(self, text):
        text = text.replace('-'," ")
        text = text.replace('–'," ")
        text = text.replace('—'," ")
        text = text.replace('"',"")
        text = text.replace("“","")
        text = text.replace("”","")
        text = text.replace("'", "'")
        text = text.replace("’","'")
        text = text.replace("‘","'")
        text = text.replace(".",".")
        text = text.replace(","," ,")
        text = text.replace("?","?")
        text = text.replace("!","!")
        return text
    
    def fixAndSaveAll(self):
        for storyname in os.listdir(self.IN_PATH):
            STORY_PATH = os.path.join(self.IN_PATH, storyname)
            storyfile = open(STORY_PATH,'r',encoding="utf8")
            story = storyfile.read()
            storyfile.close()
            story = self.fixPunc(story)
            storyfile = open(os.path.join(self.OUT_PATH, storyname),'w',encoding="utf8")
            storyfile.write(story)
            storyfile.close()

    def getAndFixSentences(self, text):
        sentences = nltk.sent_tokenize(text)
        for i in range(len(sentences)):
            sentences[i] = " " + sentences[i][:-1] + " " + sentences[i][-1] + " "
        return sentences
    
    def afterCorefGetLoweredSentences(self, story):
        sentences = nltk.sent_tokenize(story)
        lowercase_sentences = [sentence.lower() for sentence in sentences]
        return lowercase_sentences