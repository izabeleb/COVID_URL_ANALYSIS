# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 20:19:06 2021

@author: Izabele
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Mar  7 22:48:09 2021

@author: Izabele
"""

import emoji
import csv
from string import punctuation
import spacy
from datetime import datetime
from os import path
import dateutil.parser
from google.cloud import translate_v2 as translate

class DataProcessor:
    
    """
        This class takes an inputfile consisting of tweet data and extracts a variety
        of features to be used in ML classification
    """
    
    def __init__(self, inputfile, outputfile, translate_text, google_translate_service_acc_json, translation_function):
    
        """
         If translate_text is True, either a google_translate_service_acc_json or a translation_function must be provided
        """
        
        self.extractor = FeatureExtractor(translate_text, google_translate_service_acc_json, translation_function)
        self.inputfile = inputfile
        self.outputfile = outputfile
        
        # features to be extracted
        self.headers = ['LABEL_PERSON','LABEL_GPE','LABEL_NORP','LABEL_ORG','LABEL_EVENT',
                        'POS_ADJ','POS_ADV','POS_INTJ','POS_NOUN','POS_PROPN','POS_VERB','POS_ADP',
                        'POS_AUX','POS_CONJ','POS_DET','POS_NUM','POS_PART','POS_PRON','POS_SCONJ',
                        'EMOTION_anger','EMOTION_anticipation','EMOTION_disgust',
                        'EMOTION_fear','EMOTION_joy','SENTIMENT_negative','SENTIMENT_positive',
                        'EMOTION_sadness','EMOTION_surprise','EMOTION_trust',
                        'ATTRIB_avg_sentence_length','ATTRIB_avg_word_length',
                        'ATTRIB_length_of_tweet','ATTRIB_number_of_capital_letters',
                        'ATTRIB_number_of_emojis','ATTRIB_number_of_exclamation_marks',
                        'ATTRIB_number_of_hashtags','ATTRIB_number_of_periods',
                        'ATTRIB_number_of_question_marks','ATTRIB_number_of_sentences',
                        'ATTRIB_number_of_special_characters','ATTRIB_number_of_uppercase_words',
                        'ATTRIB_number_of_user_mentions','ATTRIB_number_of_words',
                        'TWEET_days_since_tweet_creation','TWEET_retweet_count',
                        'TWEET_favorite_count','TWEET_verified','TWEET_followers_count',
                        'TWEET_friends_count','TWEET_listed_count','TWEET_favourites_count',
                        'TWEET_statuses_count','TWEET_days_since_account_creation',
                        'TWEET_url_length']
        
        if path.exists(self.outputfile):
            self.of = open(self.outputfile, "a+", newline='')
            self.writer = csv.writer(self.of)
        else:
            self.of = open(self.outputfile, "a+", newline='')
            self.writer = csv.writer(self.of) 
            self.writer.writerow(self.headers)
    
    def run(self):
        
        with open(self.inputfile, encoding="utf-8-sig", newline='') as f:
            
            reader = csv.reader(f)   
            header = next(reader)
            
            for row in reader:
    
                try:
                    
                    # text attributes and NLP features extracted from text
                    features_dict = self.extractor.get_features_dict(row[header.index("text")])
                    
                    # days since tweet creation
                    creation_date = dateutil.parser.parse(row[header.index("created_at")])
                    days_since_creation = (datetime.today() - creation_date).days
                    features_dict["TWEET_days_since_tweet_creation"] = days_since_creation                  
                    # retweet count
                    features_dict["TWEET_retweet_count"] = row[header.index("retweet_count")]                
                    # favorite count
                    features_dict["TWEET_favorite_count"] = row[header.index("favorite_count")]                
                    # verified
                    features_dict["TWEET_verified"] = row[header.index("verified")]                
                    # followers count
                    features_dict["TWEET_followers_count"] = row[header.index("followers_count")]                
                    # friend count
                    features_dict["TWEET_friends_count"] = row[header.index("friends_count")]                
                    # listed count
                    features_dict["TWEET_listed_count"] = row[header.index("listed_count")]                
                    # favourites count
                    features_dict["TWEET_favourites_count"] = row[header.index("favourites_count")]                
                    # statuses count
                    features_dict["TWEET_statuses_count"] = row[header.index("statuses_count")]                
                    # days since account creation
                    creation_date = dateutil.parser.parse(row[header.index("user_created_at")])
                    days_since_creation = (datetime.today() - creation_date).days
                    features_dict["TWEET_days_since_account_creation"] = days_since_creation                
                    # url length
                    features_dict["TWEET_url_length"] = len(row[header.index("url")])                
                    
                    self.write_to_outputfile(features_dict)
                    
                except Exception as e:
                    print(e)
        
        self.close_files()            

    def write_to_outputfile(self, features_dict):
        self.writer.writerow([str(value) for value in features_dict.values()])
    
    def close_files(self):
        self.of.close()

class FeatureExtractor:
    
    def __init__(self, translate_text, google_translate_service_acc_json, translation_function):
        
        self.attrib_functions = [func for func in dir(FeatureExtractor) if callable(getattr(FeatureExtractor, func)) and func.startswith("ATTRIB")]
        self.nlp = spacy.load("en_core_web_sm")
        
        self.labels_to_collect = ['PERSON', 'GPE', 'NORP', 'ORG', 'EVENT']
        self.labels_with_info = ["LABEL_" + label for label in self.labels_to_collect]
        self.pos_to_collect = ['ADJ', 'ADV', 'INTJ', 'NOUN', 'PROPN', 'VERB',
                  'ADP', 'AUX', 'CONJ', 'DET', 'NUM', 'PART', 'PRON', 'SCONJ']
        self.pos_with_info = ["POS_" + pos for pos in self.pos_to_collect]
        self.emolex_emotions = ['anger', 'anticipation', 'disgust', 'fear',
                                'joy', 'negative', 'positive', 'sadness', 'surprise', 'trust']
        self.emolex_emotions_with_info = ["SENTIMENT_" + emotion for emotion in self.emolex_emotions]
        
        if google_translate_service_acc_json is not None:
            self.translator_json = google_translate_service_acc_json
        else:
            self.translator_json = None
            
        self.translation_function = translation_function
        self.translate_text = translate_text
    
        self.emolex_file = "‪emolex_wordlevel_92.txt".encode("ascii","ignore")
        
        self.emolex_dict = dict()
        self.SENTIMENT_load_EMOLEX()
        
    def translate(self, text):
        
        if self.translate_text:
            if self.translator_json is None and self.translation_function is not None:
                # custom function first priority if both provided
                return self.translation_function(text)
            elif self.translation_function is None and self.translator_json is not None:
                translator = translate.Client.from_service_account_json(self.translator_json)
                trans_text = translator.translate(text, target_language='en')["translatedText"]
                return trans_text
            raise Exception("No service account key or custom translation function was provided, for translation to occur, at least one must be provided")
            
        else:
            return text
    
    def get_features_dict(self, text):
        
        self.features_dict = dict()
        
        translated_text = self.translate(text)
        cleaned_text = self.UTIL_clean_text(translated_text) # using this for NLP LABELS and POS
        
        # NLP labels and pos
        labels = self.LABEL_get(cleaned_text)
        for k,v in labels.items():
            self.features_dict[str(k)] = v
            
        pos = self.POS_get(cleaned_text)
        for k,v in pos.items():
            self.features_dict[str(k)] = v
        
        # sentiment features
        sentiment_dict = self.SENTIMENT_get(translated_text) # cleaning done here
        for k,v in sentiment_dict.items():
            self.features_dict[str(k)] = v
        
        text = text.replace("'", "")
        text = text.replace('"', "")
        
        print(repr(text))
        
        # attributes
        for function in self.attrib_functions:
            
            func_call = "self." + function + "('" + text + "')"           
            try:
                result = eval(func_call)
                self.features_dict[function] = result
            except:
                result = 0
                self.features_dict[function] = result
                print("ERROR on call - " + func_call)
    
        return self.features_dict
    
    # ----------------------------------
    # PUNCTUATION, SPECIFIC CHARACTERS, AND LENGTH BASED ATTRIBUTES
    # ----------------------------------
                          
    def ATTRIB_number_of_exclamation_marks(self, text):
        try:
            return text.count("!")
        except:
            return 0
    
    def ATTRIB_number_of_periods(self, text):
        try:
            return text.count(".")
        except:
            return 0
    
    def ATTRIB_number_of_question_marks(self, text):
        try:
            return text.count("?")
        except:
            return 0
    
    def ATTRIB_number_of_capital_letters(self, text):
        try:
            return sum(1 for letter in text if letter.isupper())
        except:
            return 0
    
    def ATTRIB_number_of_special_characters(self, text):
        try:
            return sum(1 for letter in text if letter in punctuation)
        except:
            return 0
    
    def ATTRIB_number_of_uppercase_words(self, text):
        try:
            return sum([token.isupper() for token in text.split()])
        except:
            return 0
    
    def ATTRIB_number_of_hashtags(self, text):
        try:
            return text.count("#")
        except:
            return 0
                          
    def ATTRIB_number_of_user_mentions(self, text):
        try:
            return text.count("@")
        except:
            return 0
    
    def ATTRIB_number_of_emojis(self, text):
        try:
            count = 0
            allchars = [str for str in text]
            for char in allchars:
                if char in emoji.UNICODE_EMOJI['en']:
                    count+=1
            return count
        except:
            return 0
    
    def ATTRIB_length_of_tweet(self, text):
        try:
            return len(text)        
        except:
            return 0
        
    def ATTRIB_number_of_words(self, text):
        try:
            return len(text.split())
        except:
            return 0
    
    def ATTRIB_avg_word_length(self, text):
        try:
            num_words = len(text.split())
            num_chars = len(text.replace(" ", ""))
            return num_chars/num_words
        except:
            return 0
    
    def ATTRIB_number_of_sentences(self, text):
        try:
            tokens = text.split()
            new_text = [token for token in tokens if not token.startswith("http")]
            new_text = " ".join(new_text) #removing urls to not impact this
            new_text = new_text.replace("?",".").replace("!",".").split(".")
            new_text = [item for item in new_text if not item == ""]
            return len(new_text)
        except:
            return 0
    
    def ATTRIB_avg_sentence_length(self, text):
        try:
            num_sentences = self.ATTRIB_number_of_sentences(text)
            num_chars = len(text.replace(" ", ""))
            return num_chars/num_sentences
        except:
            return 0

    # ----------------------------------
    # NLP LABEL COUNTERS
    # ----------------------------------    
    
    def UTIL_clean_text(self, text):
        # cleaning for the LABEL and POS functions
        # remove user mentions, hashtags, links, and solitary emojis
        text = [token for token in text.split() if not "@" in token and not "#" in token and not token.startswith("http") and not token in emoji.UNICODE_EMOJI['en']]
        
        # removing inline emojis
        cleaned = []
        for token in text:
            cleaned_token = token
            for char in token:
                if char in emoji.UNICODE_EMOJI['en']:
                    cleaned_token = cleaned_token.replace(char, '')
            cleaned.append(cleaned_token)
            
        cleaned = [token for token in cleaned if token != '']
                    
        text = " ".join(cleaned)
        return text
    
    def LABEL_get(self, text):
           
        labels_list = [0 for label in self.labels_to_collect]
        try:
            doc = self.nlp(text)
            
            for ent in doc.ents:
                if ent.label_ in self.labels_to_collect:
                    labels_list[self.labels_to_collect.index(ent.label_)] += 1
        except:
            pass
        
        return dict(zip(self.labels_with_info, labels_list))
        
    def POS_get(self, text):

        pos_list = [0 for pos in self.pos_to_collect]
        try:
            doc = self.nlp(text)
            
            for token in doc:
                if token.pos_ in self.pos_to_collect:
                    pos_list[self.pos_to_collect.index(token.pos_)] += 1
        except:
            pass
            
        return dict(zip(self.pos_with_info, pos_list))
        
    # ----------------------------------
    # SENTIMENT ANALYSIS
    # ----------------------------------    
    
    def SENTIMENT_load_EMOLEX(self):
        
        print("loading EMOLEX sentiment dictionary, this might take a minute...")
        with open(self.emolex_file, "r") as f:
        
            for i in range(141821):
                
                tokens = f.readline().strip().split("\t")
                if tokens != ['']:
                
                    if tokens[0] in self.emolex_dict:
                        self.emolex_dict[tokens[0]][tokens[1]] = tokens[2]
                    else:
                        self.emolex_dict[tokens[0]] = dict()
                        self.emolex_dict[tokens[0]][tokens[1]] = tokens[2]

    def SENTIMENT_get(self, text):
        
        lemmas = self.SENTIMENT_get_lemmas(text)
        return self.SENTIMENT_get_emotion_counters(lemmas)
        
    def SENTIMENT_get_lemmas(self, text):
        
        try:
            # lowercase
            text = text.lower()
            
            # remove urls and usernames, keep hashtags as they might contain relevant info
            tokens = text.split()
            tokens = [token for token in tokens if not token.startswith("http") and not token.startswith("@")]
            text = " ".join(tokens)
            
            # remove punctuation
            text = "".join([letter for letter in text if letter not in punctuation])
            
            # remove stopwords
            doc = self.nlp(text)
            token_list = []
            for token in doc:
                token_list.append(token.text)
            
            filtered_sentence =[] 
    
            for word in token_list:
                lexeme = self.nlp.vocab[word]
                if lexeme.is_stop == False:
                    filtered_sentence.append(word) 
            
            filtered_sentence = [token for token in filtered_sentence if token != ' ']
            
            # lemmatization
            lemmas = []
            for word in filtered_sentence:
                lemma = " ".join([token.lemma_ for token in self.nlp(word)])
                if not lemma.isdigit():
                    lemmas.append(lemma)
    
            return lemmas
        
        except: 
            return []
    
    def SENTIMENT_get_emotion_counters(self, lemmas):
        
        emotion_counters = [0 for emotion in self.emolex_emotions]
        
        try:
            for lemma in lemmas:
                
                if lemma in self.emolex_dict:
                    
                    word_dict = self.emolex_dict[lemma]
                    
                    for emotion in self.emolex_emotions:
                        emotion_counters[self.emolex_emotions.index(emotion)] += int(word_dict[emotion])
                        
                else:
                    continue
        except:
            pass
        
        return dict(zip(self.emolex_emotions_with_info, emotion_counters))
