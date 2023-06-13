from saveFirestore import Database
from transformers import pipeline


class Analyzer():
    def __init__(self):
        self.classifier = pipeline('sentiment-analysis',model="finiteautomata/bertweet-base-sentiment-analysis")
    
    def matchChars(self, chars):
        pairsAndScores = {}
        pairsAndNumbers = {}
        for i in range(len(chars)-1):
            for j in range(i+1, len(chars)):
                key = (chars[i], chars[j])
                if key[::-1] not in pairsAndScores:  # Aynı ikili sırası farklı olarak tekrar bulunmasın
                    pairsAndScores[key] = 0
                    pairsAndNumbers[key] = 0
        return pairsAndScores, pairsAndNumbers
    
    def calculateSentiment(self, sentence, classifier):
        result = classifier(sentence)
        label = result[0]['label']
        score = result[0]['score']
    
        if label == 'NEU':
            score = 0
        elif label == 'NEG':
            score = -score
        else:
            score = score
    
        return score
    
    def calculateAvarage(self, numbers, pairsAndScores, setZero):
        scores = {}
        for pair in pairsAndScores:
            count = numbers.get(pair, 0)
            if count != 0:
                scores[pair] = pairsAndScores[pair] / count
                if setZero:
                    pairsAndScores[pair] = 0
                    numbers[pair] = 0
        return scores

    def analyzeForPairs(self, storySentences, pairsAndNumbers, pairsAndScores, storyname, database):
        length = len(storySentences)
        entryEnd = int(length / 3)

        for idx in range(length):
            for key in pairsAndNumbers:
                word1, word2 = key
                if word1 in storySentences[idx] and word2 in storySentences[idx]:
                    pairsAndNumbers[key] += 1
                    score = self.calculateSentiment(storySentences[idx], self.classifier)
                    pairsAndScores[key] += score
        scores = self.calculateAvarage(pairsAndNumbers, pairsAndScores, False)
        pairsAndLabels = self.convert_scores_to_labels(scores)
        storyfile = open("Relation Scores/"+storyname+".txt",'w',encoding="utf8")
        storyfile.write(str(scores))
        storyfile.close()
        database.saveGraph(pairsAndLabels,storyname+".png")

        for idx in range(entryEnd):
            for key in pairsAndNumbers:
                word1, word2 = key
                if word1 in storySentences[idx] and word2 in storySentences[idx]:
                    pairsAndNumbers[key] += 1
                    score = self.calculateSentiment(storySentences[idx], self.classifier)
                    pairsAndScores[key] += score
        scores = self.calculateAvarage(pairsAndNumbers, pairsAndScores, True)
        pairsAndLabels = self.convert_scores_to_labels(scores)
        storyfile = open("Relation Scores/"+storyname+" Entry.txt",'w',encoding="utf8")
        storyfile.write(str(scores))
        storyfile.close()
        database.saveGraph(pairsAndLabels, storyname+" Entry.png")

        progressEnd = entryEnd*2
        for idx in range(entryEnd+1, progressEnd):
            for key in pairsAndNumbers:
                word1, word2 = key
                if word1 in storySentences[idx] and word2 in storySentences[idx]:
                    pairsAndNumbers[key] += 1
                    score = self.calculateSentiment(storySentences[idx], self.classifier)
                    pairsAndScores[key] += score
        scores = self.calculateAvarage(pairsAndNumbers, pairsAndScores, True)
        pairsAndLabels = self.convert_scores_to_labels(scores)
        storyfile = open("Relation Scores/"+storyname+" Progress.txt",'w',encoding="utf8")
        storyfile.write(str(scores))
        storyfile.close()
        database.saveGraph(pairsAndLabels, storyname+" Progress.png")

        for idx in range(progressEnd+1, length):
            for key in pairsAndNumbers:
                word1, word2 = key
                if word1 in storySentences[idx] and word2 in storySentences[idx]:
                    pairsAndNumbers[key] += 1
                    score = self.calculateSentiment(storySentences[idx], self.classifier)
                    pairsAndScores[key] += score
        scores = self.calculateAvarage(pairsAndNumbers, pairsAndScores, True)
        pairsAndLabels = self.convert_scores_to_labels(scores)
        storyfile = open("Relation Scores/"+storyname+" Result.txt",'w',encoding="utf8")
        storyfile.write(str(scores))
        storyfile.close()
        database.saveGraph(pairsAndLabels, storyname+" Result.png")
        
    def convert_scores_to_labels(self, pairsAndScores):
        labelDict = {}
        for key, value in pairsAndScores.items():
            if value < 0:
                label = 'NEG'
            elif value == 0:
                label = 'NEU'
            else:
                label = 'POS'
    
            labelDict[key] = label
    
        return labelDict
    
    