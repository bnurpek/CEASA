import os

import firebase_admin
import matplotlib.pyplot as plt
import networkx as nx
from firebase_admin import credentials, firestore, storage
from nltk.tokenize import WordPunctTokenizer


class Database:
    def __init__(self):
        self
        # Firestore bağlantı olmadan çalıştırmak için inaktif
    #    self.cred = credentials.Certificate('key-for-firestore')
    #    firebase_admin.initialize_app(self.cred, {
    #        'storageBucket': 'ceasa-6b001.appspot.com'
    #    })
    #    self.character_ref = firestore.client().collection("characters")
    #    self.storage_bucket = storage.bucket()

    def saveCharacters(self, story, storyname, depparse, nltkNER, stopWords):
        depparse = ", ".join(depparse).lower().split(", ")
        nltkNER = ", ".join(nltkNER).lower().split(", ")
        mergedResultForCharacters = list(set(depparse + nltkNER) - set(stopWords)) #Tekrarları silmek için
    
        frequencyOfCharacters = {}
        for character in mergedResultForCharacters:
            frequencyOfCharacters[character] = story.count(character)
        frequencyOfCharacters = dict(sorted(frequencyOfCharacters.items(), key=lambda x:x[1], reverse=True))
        
        print("--------------------------------------------------")
        print(f'Frequency of characters: {frequencyOfCharacters}')

        keepedChars = {}
        for idx, charname in enumerate(frequencyOfCharacters):
            if 1 < frequencyOfCharacters[charname] < 100 and idx < 6: 
                keepedChars[f'karakter_{idx}'] = charname
        
        print(f'Keeped characters: {keepedChars}\n'),
        storyfile = open("Characters/"+storyname,'w',encoding="utf8")
        storyfile.write("\n".join(keepedChars))
        storyfile.close()

        # Firestore inaktif
    #    self.character_ref.document(storyname).set(keepedChars)

        return list(keepedChars.values())
    
    def saveGraph(self, pairsAndLabels, fileName):
        G = nx.Graph()
        colorDict = {'NEG':'red', 'POS':'green', 'NEU':'yellow'}

        uniqueChars = set()
        for pair in pairsAndLabels:
            uniqueChars.update(pair)

        for character in uniqueChars:
            G.add_node(character)
    
        for pair, label in pairsAndLabels.items():
            node1, node2 = pair
            color = colorDict[label]
            G.add_edge(node1, node2, color=color)

        plt.subplots(figsize=(11, 11))

        pos = nx.spring_layout(G)
        colors = [G[u][v]['color'] for u, v in G.edges()]

        nx.draw(G, pos, with_labels=True, node_color='lightgray', node_size=2500, font_size=15, 
            edge_color=colors, width=2.5, edge_cmap=plt.cm.Blues)
        
        plt.savefig("figures/"+fileName)

        #Firestore inaktif
    #    blob = self.storage_bucket.blob(fileName)
    #    blob.upload_from_filename("figures/"+fileName)
    #    os.remove("figures/"+fileName)