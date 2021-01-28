### Import Packages

import re
import csv
import os
import os.path
from os import listdir
from os.path import isfile, join

import time

import docx2txt

import pandas as pd
import numpy as np

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('stopwords')
nltk.download('punkt')

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyser = SentimentIntensityAnalyzer()

from textblob import TextBlob

import json
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, CategoriesOptions, KeywordsOptions, SentimentOptions

### Watson Credentials

authenticator = IAMAuthenticator('Sign Up Login Here')

natural_language_understanding = NaturalLanguageUnderstandingV1(
    version='2020-08-01',
    authenticator=authenticator
)
natural_language_understanding.set_service_url('URL Watson Here')

### Test Response from Watson

print("Getting test response from Watson")
response = natural_language_understanding.analyze(
    url='www.ibm.com',
    features=Features(categories=CategoriesOptions(limit=3))).get_result()

print(json.dumps(response, indent=2))


#Define the Watson call

def WatsonSentiment_score(input_text): 
    # Input text can be sentence, paragraph or document
    try:
        time.sleep(2)
        response = natural_language_understanding.analyze(text = input_text,language='en',features=Features(
                                                      keywords=KeywordsOptions(emotion=True,
                                                                               sentiment=True,limit=1))).get_result()
    except:
        response = "NA"
        

            
    
    return response

#Define the Vader Lexicon Update


def vaderUpdate(data):
    updateLexicon = pd.read_csv(data)
    print("*---------------*")
    print("These are the first five lexicon updates")
    print(updateLexicon.head())
    print("*---------------*")

    existingLexicon = list(analyser.lexicon.keys())

    for pos,word in updateLexicon['Term'].items():
        updatedWords = {word:updateLexicon['Score'].loc[pos]}
        print("this word {} will be added with score of {} ".format(word, updateLexicon['Score'].loc[pos]))
        analyser.lexicon.update(updatedWords)
        print("")

## Update the Lexicon for Vader

vaderFile = "VADER_Update_201029.csv"
vaderUpdate(vaderFile)


### Transcript Location and Parameters

titles = ['mr','mrs','dr','your','honour','her']
transcriptLocation = "Location of Transcripts Here"
os.chdir(transcriptLocation)
onlyfiles = [f for f in listdir() if isfile(join(f))]


### Define Data Encoding and Decoding from Word and WordX

def dataCoverterDocx(data):
    
    folderName = data.replace(" ", "_")
    folderName = folderName.replace(".", "")
    folderName = folderName.replace("docx", "")
    
    if not os.path.exists(folderName):
        os.makedirs(folderName)
    
    #os.chdir(folderName)
    
    MY_TEXT = docx2txt.process(data)
    MY_TEXT = re.sub(r'[^\x00-\x7F]+',' ', MY_TEXT)
    MY_TEXT = MY_TEXT.lower()
    
    filename = data.replace(" ", "_")
    filename = filename.replace(".", "")
    filename = filename.replace("docx", "")
    filename = folderName+"/"+filename+".txt"
    
    
    
    with open(filename, "w") as text_file:
        print(MY_TEXT, file=text_file)
    
    print("")
    print("------------------------")
    print("Converted Docx {} file to {}".format(i,filename))
    print("")
    print("------------------------")
    
    return folderName, filename

def dataCoverterDoc(data):
    
    
    
    folderName = data.replace(" ", "_")
    folderName = folderName.replace(".", "")
    folderName = folderName.replace("doc", "")
    
    if not os.path.exists(folderName):
        os.makedirs(folderName)
    
    #os.chdir(folderName)
    
    filename = data.replace(" ", "_")
    filename = filename.replace(".", "")
    filename = filename.replace("doc", "")
    filename = filename+".txt"
    filename = folderName+"/"+filename+".txt"
    
    file = open(filename,"w+")
    
    with open(data, 'r', encoding="latin-1") as f:
        for line in f:
            line = re.sub(r'[^\x00-\x7F]+',' ', line)
            file.write(line)
    file.close()        
    
    print("")
    print("------------------------")
    print("Converted Doc {} file to {}".format(i,filename))
    print("")
    print("------------------------")
    
    return folderName, filename
    
### Define Sentiment Analysis Operations

def sentiment_analyzer_scores(sentence):
    score = analyser.polarity_scores(sentence)
    final_score = score
    return final_score

def TextBlober(dataFrame):
    for pos, text in dataFrame['Speech_Text'].items():
        textblobscore = TextBlob(text).sentiment
        scorePolarity = float(textblobscore.polarity)
        scoreSubjectivity = float(textblobscore.subjectivity)
        dataFrame.loc[pos,'Text_Blob_Sentiment'] = scorePolarity
        dataFrame.loc[pos,'Text_Blob_Subjectivity'] = scoreSubjectivity
        
    return dataFrame   

def Watson(dataFrame):
    for pos, text in dataFrame['Speech_Text'].items():
        time.sleep(2)
        print("---------------")
        print("")
        print("Doing line now")
        
        response = WatsonSentiment_score(text)
        if response != "NA":
            try:
                anger = response.get('keywords')[0].get('emotion').get('anger')
            except:
                anger = "NA"

            try:
                disgust = response.get('keywords')[0].get('emotion').get('disgust')
            except:
                disgust = "NA"
            
            try:    
                fear = response.get('keywords')[0].get('emotion').get('fear')
            except:
                fear = "NA"
            
            try:
                joy = response.get('keywords')[0].get('emotion').get('joy')
            except:
                joy = "NA"
                
            try:
                sadness = response.get('keywords')[0].get('emotion').get('sadness')
            except:
                sadness = "NA"
                
            try:
                sentimentLabel = response.get('keywords')[0].get('sentiment').get('label')
            except:
                sentimentLabel = "NA"
            
            try:
                sentimentScore = response.get('keywords')[0].get('sentiment').get('score')
            except:
                sentimentScore = "NA"

            dataFrame.loc[pos,'Watson_Sentiment_Score'] = sentimentScore
            dataFrame.loc[pos,'Watson_Sentiment_Label'] = sentimentLabel
            dataFrame.loc[pos,'Watson_Anger_Score'] = anger
            dataFrame.loc[pos,'Watson_Disgust_Score'] = disgust
            dataFrame.loc[pos,'Watson_Joy_Score'] = joy
            dataFrame.loc[pos,'Watson_Sadness_Score'] = sadness
            dataFrame.loc[pos,'Watson_Fear_Score'] = fear
            print("Finished line successfully")
            print("")
            print("---------------")
        else:
            dataFrame.loc[pos,'Watson_Sentiment_Score'] = 0
            dataFrame.loc[pos,'Watson_Sentiment_Label'] = 0
            dataFrame.loc[pos,'Watson_Anger_Score'] = 0
            dataFrame.loc[pos,'Watson_Disgust_Score'] = 0
            dataFrame.loc[pos,'Watson_Joy_Score'] = 0
            dataFrame.loc[pos,'Watson_Sadness_Score'] = 0
            dataFrame.loc[pos,'Watson_Fear_Score'] = 0
            print("Could not finish line")
            print("")
            print("---------------")
        
    return dataFrame  

def VaderAnalysis(dataFrame):
    for pos, text in dataFrame['Speech_Text'].items():
        SentenceScore = sentiment_analyzer_scores(text)
        dataFrame.loc[pos,'Negative_Score'] = SentenceScore.get('neg')
        dataFrame.loc[pos,'Positive_Score'] = SentenceScore.get('pos')
        dataFrame.loc[pos,'Neutral_Score'] = SentenceScore.get('neu')
        dataFrame.loc[pos,'Compound_Score'] = SentenceScore.get('compound')
    
    return dataFrame
	
### Define the Sentiment Analysis Loop Operation and Dataframe Build

def doSentiment(filename, folderName):
    
    titles = ['mr','mrs','her','honour']
    
    counters = []
    sentence = []
    names = []

    current_name = "NA"
    name= "NO_NAME"
    
    with open(filename) as f:
        for num,line in enumerate(f,1):
            line = re.sub("\n|\x1e\xa0\x1e\xa0\x1e|\xa0","",line)
            line = line.strip()
            
            if line == "":
                pass
            
            elif re.match("matter adjourned",line[0:30].lower()) !=None:
                break
        
        ### add some more cleaning
            else:
                if current_name != "NA":

                    name = line.split(':')[0]
                    name = name.strip()
                    titleMatch = name[0:5]
                    
                    resultMatch = 0
                    for title in titles:
                        if re.match(title, titleMatch.lower()) != None:
                            resultMatch += 1
                        else:
                            pass
                        
                    if resultMatch >0:
                        name = name
                    else:
                        name = current_name
        


                    if name == current_name:
                            names.append(current_name)

                    else:
                        current_name = name
                        names.append(name)


                else:
                    current_name = line.split(':')[0]
                    current_name = name.strip()
                    
                    if len(current_name) > 5:
                        current_name = "NO_NAME"
                        names.append(current_name)
                    else:
                        names.append(current_name)
                
                counter = num
                        #print(line)
                        ###update dictionary or specific name
                counters.append(counter)
                #sentence.append(line.partition(key)[2].lstrip())
                if ":" in line:
                    line = line.split(':')[1]
                else:
                    line = line
                line = line.replace(":", "")
                line = line.strip()
                sentence.append(line.lstrip())
    
    
    
    print("")
    print("-----------------------------------------")
    print("Starting new frame")
    print("-----------------------------------------")
        
   
    dataframe_name = filename.replace(" ", "_")
    dataframe_name = dataframe_name.replace(".", "")
    i = dataframe_name
    frameName = filename+"_results"
    frameName = "Results"     
    print("The dataframe name is {}".format(i))
        
        

    try:
        exec('{} = pd.DataFrame(np.column_stack([counters,sentence]),columns=["Speech_Number", "Speech_Text"])'.format(frameName))
        exec('{}{} = {}'.format(frameName,['Name'],names))
        exec('{}{} = 0'.format(frameName,['Negative_Score']))
        exec('{}{} = 0'.format(frameName,['Neutral_Score']))
        exec('{}{} = 0'.format(frameName,['Positive_Score']))
        exec('{}{} = 0'.format(frameName,['Compound_Score']))
        
        exec('{}{} = 0'.format(frameName,['Text_Blob_Sentiment']))
        exec('{}{} = 0'.format(frameName,['Text_Blob_Subjectivity']))
        
        exec('{}{} = 0'.format(frameName,['Watson_Sentiment_Score']))
        exec('{}{} = 0'.format(frameName,['Watson_Sentiment_Label']))
        exec('{}{} = 0'.format(frameName,['Watson_Anger_Score']))
        exec('{}{} = 0'.format(frameName,['Watson_Disgust_Score']))
        exec('{}{} = 0'.format(frameName,['Watson_Joy_Score']))
        exec('{}{} = 0'.format(frameName,['Watson_Sadness_Score']))
        exec('{}{} = 0'.format(frameName,['Watson_Fear_Score']))
        


        print("Dataframe created for {}".format(i))
        print("")
        #print("Length of dataframe is {}".format(len(i)))

        print("")
        print("The dataframe sample is")
        exec('print({}.head())'.format(frameName))
        
    except:
        
        print("Could not create dataframe for {}".format(i))

           
    print("Doing Vader Analysis for {}".format(i))
        
    try:
        print("")
        exec('{} = VaderAnalysis({})'.format(frameName,frameName))
        print("Success for vader analysis of {}".format(i))
        print("")
    except:
        print("Could not do vader analysis for {}".format(i))

        #for i in dataframeNames:
        
    print("Doing TextBlob Analysis for {}".format(i))
        
    try:
        print("")
        exec('{} = TextBlober({})'.format(frameName,frameName))
        print("Success for TextBlob analysis of {}".format(i))
        print("")
    except:
        print("Could not do TextBlob analysis for {}".format(i))

    print("Doing Watson Analysis for {}".format(i))
    
    time.sleep(2)
    try:
        print("")
        exec('{} = Watson({})'.format(frameName,frameName))
        print("Success for Watson analysis of {}".format(i))
        print("")
    except:
        print("Could not do Watson analysis for {}".format(i))    
        
    

    print("Now trying to create CSV file for {}".format(i))
    print("")
    print("The folder it will be saved into is {}".format(folderName))

    try:
        name = folderName+"/"+frameName+".csv"
        print(name)
        exec('{}.to_csv(name, quoting=csv.QUOTE_NONNUMERIC)'.format(frameName))
        print("")
        print("Success for creating CSV of {}".format(i))
    except:
        print("Cannot create CSV for {}".format(i))

### Loop through files in directory and do sentiment analysis for labelling

for i in onlyfiles:
    if ".docx" in i:
        folderName, filename = dataCoverterDocx(i)
        doSentiment(filename,folderName)
    else:
        folderName, filename = dataCoverterDoc(i)
        doSentiment(filename,folderName)
