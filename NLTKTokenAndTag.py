#!/usr/bin/python

import sys
import getopt
from datetime import datetime
import re
import string
import csv
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import wordnet

#initialization
lemmatizer = WordNetLemmatizer()
    

def treeBankToWordNet(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return ''

def removeEmoji(text):
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text) # no emoji

def removeNonPrintable(text):
    printable = set(string.printable)
    return "".join([i for i in text if i in printable])

def readTweets(tweetFile):
    with open(tweetFile, newline='', encoding='UTF8') as csvFile:
        print("file found")
        
        #get coloumn names
        header = next(csvFile).split(',')
    
        tweetReader = csv.DictReader(csvFile, header)
        tweets = []
        for row in tweetReader:
            tweets.append((row['user_screen_name'], removeNonPrintable(row['text'])))    
        print("Finished Loading")
    return tweets

def readTweetsTxt(tweetFile):
    with open(tweetFile, newline='', encoding='UTF8') as txtFile:
        print("file found")
        
        tweets = []
        for row in txtFile:
            tweets.append(("none",removeNonPrintable(row)))    
        print("Finished Loading")
    return tweets

def tokenizeAndTagToFile(tweets, taggedConllOut, progressInterval=None, language = 'english'):
    tweetCount = 0
    if progressInterval is None:
        progressInterval = 100
        
    taggedConllFile = open(taggedConllOut, 'w')
    for tweet in tweets:
        #taggedConllFile.write("# newdoc id =\t" + tweet[0] + "\n") #might need to include this for keeping track of tweets
        
        #get sentences                      
        sentences = sent_tokenize(tweet[1]) #the first element in the tweet tuple is the username
        
        for sentence in sentences:
            #get words
            words = word_tokenize(sentence)
            tagged = nltk.pos_tag(words)
            
            #output CONLL
            count = 1   #CONLLX starts at 1
            for word, pos in tagged:
                wordNetPosTag = treeBankToWordNet(pos)
                if wordNetPosTag != '':
                    taggedConllFile.write(str(count) + "\t" + word + "\t" + lemmatizer.lemmatize(word,wordNetPosTag) + "\t" + pos + "\t" + pos + "\t_\n")
                else:
                    taggedConllFile.write(str(count) + "\t" + word + "\t_\t" + pos + "\t" + pos + "\t_\n")
                count += 1
                
            #sentence done, new line
            taggedConllFile.write("\n")
        
        #just to indicate progress
        tweetCount += 1
        if tweetCount % progressInterval == 0:
            print(tweetCount)
    #close file
    taggedConllFile.close()
    
    #done all tweets, print tweetcount
    print("Finished tagging " + str(tweetCount) + " tweets")
        
def outputNameFromInput(inputPath, outputPath):
    name = inputPath.split('/')
    name = name[len(name)-1].split('.')[0] + ".conll"
    
    if outputPath.endswith('/'):
        return outputPath + name
    else:
        return outputPath + '/' + name
    
def readArgs(argv):
    inputFile = ''
    outputFolder = ''
    try:
        opts, args = getopt.getopt(argv,"vhi:o:",["version","ifile=","ofile="])
    except getopt.GetoptError:
        print ('test.py -i <inputfile> -o <outputfile>')
        sys.exit()
    for opt, arg in opts:
        if opt in ("-v", "--version"):
            print("Version:\nRemoved    : All non-printable characters\nTokenizer  : Untrained default NLTK sentence and word tokenizer\nTagger     : Untrained default NLTK english tagger\nLemmatizer : WordNet lemmatizer")
            sys.exit()
        elif opt == '-h':
            print ('NLTKTokenAndTag.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            if not arg.endswith(".csv"):
                print("Input must be a csv file")
                sys.exit()
            inputFile = arg
        elif opt in ("-o", "--ofile"):
            outputFolder = arg
    if (inputFile != '' and outputFolder != ''):
        return inputFile, outputFolder
    
    print ('test.py -i <inputfile> -o <outputfile>')
    sys.exit()

if __name__ == "__main__":
    tweetCSV, outConll = readArgs(sys.argv[1:])

    outConll = outputNameFromInput(tweetCSV, outConll)
    #loadFile
    tweets = readTweets(tweetCSV)
    
    print("Writing to " + outConll)
    tokenizeAndTagToFile(tweets, outConll)