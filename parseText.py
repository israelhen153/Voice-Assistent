import re, string
from nltk.corpus import stopwords
from collections import Counter
from nltk import wordpunct_tokenize
from nltk.stem.wordnet import WordNetLemmatizer

""" 
    The process of parsing an voice command:
        *   Bring the sentence to it's simplest meaning
        *   try to remove any words that are just noise in the sentence
        *   finally bring the the sentence to a basic structure 
            of: action-on what-additional parts
"""

"""
    This class simply parses the speech text input and formats it to a more easy structure
"""


class Parser:

    @staticmethod
    def __textStemming(userInput):
        ps = WordNetLemmatizer()
        return [ps.lemmatize(word) for word in userInput]

    def __removeNoise(self, userInput):
        stopWordsList = stopwords.words("english")
        stopwordsDict = Counter(stopWordsList)
        loweredInput = wordpunct_tokenize(userInput.lower())
        filteredText = [word for word in loweredInput if word not in stopwordsDict]
        return self.__textStemming(filteredText)

    def __normalizeText(self, userInput):
        userInput = userInput.encode('ascii', 'ignore').decode()
        userInput = userInput.lower().replace("jarvis", "")
        userInput = re.sub('\s{2,}', " ",userInput)
        userInput = re.sub("\'\w+", '', userInput)
        userInput = re.sub('[%s]' % re.escape(string.punctuation), ' ', userInput)

    def __cleanText(self, userInput):
        return " ".join(self.__removeNoise(self.__normalizeText(userInput)))

    def parseText(self, userInput):
        return self.__cleanText(userInput)


if __name__ == '__main__':
    par = Parser().parseText("Hello Mate Please launch brave")
    print(par)
