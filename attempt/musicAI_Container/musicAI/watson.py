import json
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions, CategoriesOptions, ConceptsOptions, EmotionOptions, RelationsOptions, SemanticRolesOptions, SentimentOptions, SyntaxOptions

import config

import statistics
import datetime

from pprint import pprint

'''

NOTE
in order to use properly ... 
  - log in function
  - gather corpus into array ... each item ==  ai_to_Text(message) 
  - run averages on the array ---> averages_calc( text_Models )
  -after you have the averaged array (input works with just one item as well.)... you will recieve a dictionary with all sentiment frequencies.
  -


'''


# Login to NLU service
def login():
  # Login to IBM (30K requests a month.... goes fast if you run each line on its own analysis)
  

  # NOTE COMMENT AND UNCOMMENT  api_key & url combinations for API limit
  api_key = config.watson_api_key
  url = config.watson_url



  authenticator = IAMAuthenticator(api_key)
  natural_language_understanding = NaturalLanguageUnderstandingV1(
      version='2020-08-01',
      authenticator=authenticator)
  natural_language_understanding.set_service_url(url)
  return natural_language_understanding
def analyzeText(client, text):
  # Analyze Text
  response = client.analyze(
      text=text,
      features=Features(
          entities=EntitiesOptions(emotion=True, sentiment=True, limit=2),
          keywords=KeywordsOptions(emotion=True, sentiment=True, limit=2),
          categories=CategoriesOptions(limit=100),
          concepts=ConceptsOptions(limit=100),
          emotion=EmotionOptions(),
          # emotion=EmotionOptions(targets=['apples','oranges'])
          relations=RelationsOptions(),
          semantic_roles=SemanticRolesOptions(keywords=True , entities=True),
          sentiment=SentimentOptions(),
          # sentiment=SentimentOptions(targets=['stocks']),
          syntax=SyntaxOptions(sentences=True),
          )
    ).get_result()
  return json.dumps(response, indent=2)








# CLEAN DATA
def ai_to_Text(message):
  response = analyzeText(nlu_client, message)
  response = json.loads(response)

  # MAKE A DICTIONARY THAT HOLDS THE AVERAGES OF THE OUTPUT
  # after saving the averages, refer to the message_Dictionary to get a total avg of all messages user sent

  emotion = response['emotion']['document']['emotion'] #dict
  entities = response['entities'] #list
  keywords = response['keywords'] #list
  relations = response['relations'] #list
  semantic_roles = response['semantic_roles'] #list
  sentiment = response['sentiment'] #dict
  concepts = response['concepts'] #list
  categories = response['categories'] #list



  # clean data
  clean_relations = []
  for r in relations:
    # print(r['sentence'])
    for a in r['arguments']:
      for e in a['entities']:
        clean_relations.append(  (e['type'] , e['text'])  )

  # # wowowowowoww
  # lolz = [ (e['type'] , e['text']) for r in relations for a in r['arguments'] for e in a['entities'] ]

  model = {
    'overall_emotion' : emotion,
    'relations' : clean_relations,
    'sentiment' :  sentiment['document']['label']  ,
    'entities' : [  (  i['text'] , i['type']  , i['sentiment']['label']  ) for i in entities  ],
    'keywords' : [  (  i['text'] , i['sentiment']['label']   ) for i in keywords  ],
    'subjects' : [  (  i['subject']['text'] , i['action']['verb']['tense'] ) for i in semantic_roles  ],
    'concepts' : [  i['label']  for i in categories  ],
  }


  return model





# calculations of arr with ai outputs *** USING ai_to_Text ***
def averages_calc( text_Models ):
  # NOTE: TEXT MODEL ITEM KEYS
  # dict_keys   ['overall_emotion', 'relations', 'subjects', 'entities', 'keywords', 'concepts']

  

  # initialization of all model points through one loop
  overallEmotion = {
    'anger': [],
    'disgust': [],
    'fear': [],
    'joy': [],
    'sadness': []
  }
  allRelations = []
  allSentiments = []
  allEntities = []
  allKeywords = []
  allConcepts = []
  allSubjects = []
  for i in text_Models:
    # OVERALL EMOTION
    overallEmotion['anger'].append(i['overall_emotion']['anger'])
    overallEmotion['disgust'].append(i['overall_emotion']['disgust'])
    overallEmotion['fear'].append(i['overall_emotion']['fear'])
    overallEmotion['joy'].append(i['overall_emotion']['joy'])
    overallEmotion['sadness'].append(i['overall_emotion']['sadness'])
    # relations
    for r in i['relations']:
      allRelations.append(r)
    # sentiment
    allSentiments.append(i['sentiment'])
    # entities
    for e in i['entities']:
      allEntities.append(e)
    # keywords
    for k in i['keywords']:
      allKeywords.append(k)
    # keywords
    for l in i['concepts']:
      allConcepts.append(l)
    # subject
    for s in i['subjects']:
      allSubjects.append(s)


  # OVER ALL EMOTION AVERAGE
  averageEmotion = {
    'Anger' :  sum(overallEmotion['anger']) / len(overallEmotion['anger'])   ,
    'Disgust': statistics.mean(overallEmotion['disgust']),
    'Fear': statistics.mean(overallEmotion['fear']),
    'Joy': statistics.mean(overallEmotion['joy']),
    'Sadness': statistics.mean(overallEmotion['sadness']),
  }






  # RELATIONS 
  relationsfrequencies = {}
  for item in allRelations:
      if item[0] in relationsfrequencies:
          relationsfrequencies[item[0]].append(item[1])
      else:
          relationsfrequencies[item[0]] = [ item[1] ]



  # sentiment
  sentiment_frequencies = {}
  for item in allSentiments:
      if item in sentiment_frequencies:
          sentiment_frequencies[item] += 1
      else:
          sentiment_frequencies[item] = 1
  




  # NOTE checks if entities and keywords have duplicates
  removes = []
  if len(allEntities) > 0 and len(allKeywords) > 0:
    keywords_Length = len(allKeywords)
    for x in range(len(allEntities)):
      for y in range(keywords_Length):
        if allEntities[x][0] == allKeywords[y][0]:
          removes.append(allKeywords[y])
    # remove the item and handle key error if duplicates of multiples
    if len(removes) > 0:
      for y in removes:
        try:
          allKeywords.remove(y)
        except ValueError:
          pass
        except:
          print('\n\n################## ERROR in calculations ##################\n\n')



  # entities
  entityfrequencies = {}
  for item in allEntities:
      if item[2] in entityfrequencies:
          entityfrequencies[item[2]].append(  ( item[0] , item[1])  )
      else:
          entityfrequencies[item[2]] = [ ( item[0] , item[1])  ] 



  # keywords
  keywordfrequencies = {}
  for item in allKeywords:
      if item[1] in keywordfrequencies:
          keywordfrequencies[item[1]].append(item[0])
      else:
          keywordfrequencies[item[1]] = [item[0]]






  # Concepts
  allConcepts = set(allConcepts) 
  conceptfrequencies = {}
  for x in allConcepts:
    x = x.split("/")[1:]
    if x[0] in conceptfrequencies:
      if len(x[1:]) > 0:
        conceptfrequencies[x[0]].extend( x[1:] )
    else:
      conceptfrequencies[x[0]] = x[1:] 






  # subjects
    #  i['subject']['text'] , i['action']['verb']['tense']
  subjectsfrequencies = {}
  for item in allSubjects:
      if item[1] in subjectsfrequencies:
          subjectsfrequencies[item[1]].append(item[0])
      else:
          subjectsfrequencies[item[1]] = [item[0]]



  # CLEAN AVERAGE DATA MODELS
  # averageEmotion
  # relationsfrequencies
  # sentiment_frequencies
  # entityfrequencies
  # keywordfrequencies
  # conceptfrequencies
  # subjectsfrequencies
  
  sentiment_model = {
    'averageEmotion' : averageEmotion,
    'relationsfrequencies' : relationsfrequencies,
    'sentiment_frequencies' : sentiment_frequencies,
    'entityfrequencies' : entityfrequencies,
    'keywordfrequencies' : keywordfrequencies,
    'conceptfrequencies' : conceptfrequencies,
    'subjectsfrequencies' : subjectsfrequencies
  }


  return sentiment_model


# mood sentiment takes clean data from averages_calc
# averageEmotion
# relationsfrequencies
# sentiment_frequencies
# entityfrequencies
# keywordfrequencies
# conceptfrequencies
# subjectsfrequencies










# runs on import
nlu_client = login()

