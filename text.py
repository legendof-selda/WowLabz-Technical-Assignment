import pandas as pd
import numpy as np
import spacy
from textblob import TextBlob
from string import punctuation
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize 
from nltk.tokenize import sent_tokenize
import heapq

summary_n = 5
title_n = 3

def predict_sentiment(string):
    return TextBlob(string).sentiment

def tokenize(string, sw = stopwords.words('english')):
    X_list = word_tokenize(string.lower())
    X_set = {w for w in X_list if not w in sw}
    return X_set

def tokens_union(multiple_tokens):
    return set().union(*multiple_tokens)

def cosine_similarity(X_set, Y_set, debug=False):
    l1 =[]
    l2 =[]
    # form a set containing keywords of both strings
    rvector = X_set.union(Y_set)
    for w in rvector:
        if w in X_set: l1.append(1) # create a vector
        else: l1.append(0)
        if w in Y_set: l2.append(1)
        else: l2.append(0)
    c = 0
    # cosine formula
    for i in range(len(rvector)):
            c+= l1[i]*l2[i]
    cosine = c / float((sum(l1)*sum(l2))**0.5)
    if debug: print("similarity: ", cosine)
    return cosine

def text_semantic_segmentation_top_down(sentence_tokens, k, thresh = 0.10):
    segments = []
    #for i in range(k):
        #segments.append([i])
    segments.append([0])
    i = 1
    max = -1
    s=0
    while(i<k-1):
        print(i,s)
        print(segments)
        sent = sentence_tokens[i]
        next_sents = tokens_union([sentence_tokens[x] for x in segments[s]]) 
        similarity = cosine_similarity(sent, next_sents)
        if(similarity>thresh and similarity>=max):
            segments[s] = segments[s] + [i]
            max = similarity
        else:
            max = -1
            s=s+1
            segments.append([i])
        i = i+1
    return segments

def text_semantic_segmentation_bottom_up(sentence_tokens, k, segments, thresh = 0.10):
    i = len(segments) - 2
    max = -1
    while(i>=0):
        sent = sentence_tokens[segments[i][0]]
        next_sents = tokens_union([sentence_tokens[x] for x in segments[i+1]]) 
        similarity = cosine_similarity(sent, next_sents)
        if(similarity>thresh and similarity>=max):
            segments[i] = segments[i] + segments[i+1]
            del segments[i+1]
            max = similarity
        else:
            max = -1
        i = i-1
    return segments

def word_frequency(sentence_tokens):
    word_freq = {}
    for sent in sentence_tokens:
        for word in sent:
            if word not in word_freq.keys():
                word_freq[word] = 1
            else:
                word_freq[word] += 1
    max_freq = max(word_freq.values())
    for word in word_freq.keys():
        word_freq[word] = word_freq[word]/max_freq
    return word_freq

def sentence_score(sentence_tokens, word_freq):
    sentence_scores = {}
    for i in range(len(sentence_tokens)):
        for word in sentence_tokens[i]:
            if word in word_freq.keys():
                if i not in sentence_scores.keys():
                    sentence_scores[i] = word_freq[word]
                else:
                    sentence_scores[i] += word_freq[word]
    return sentence_scores

def get_top(scores, n=3):
    return heapq.nlargest(n, scores, key=scores.get)

def analyze_text(sample):
    whole_sentiment = predict_sentiment(sample)
    sentences = sent_tokenize(sample)
    sentence_tokens = []
    sw = set(stopwords.words('english') + list(punctuation))
    #sw = stopwords.words('english')
    for s in sentences:
        tokens = tokenize(s, sw)
        sentence_tokens.append(tokens)
    segments = text_semantic_segmentation_top_down(sentence_tokens, len(sentences))
    segments = text_semantic_segmentation_bottom_up(sentence_tokens, len(sentences), segments)

    new_sentences = []
    sentiments = []
    for i in range(len(segments)):
        new_sentences.append("")
        for j in range(len(segments[i])):
            new_sentences[i] = new_sentences[i] + " " + sentences[segments[i][j]]
        sentiments.append(predict_sentiment(new_sentences[i]))

    word_freq = word_frequency(sentence_tokens)
    sentence_scores = sentence_score(sentence_tokens, word_freq)

    summary_sentences = get_top(sentence_scores, summary_n)
    summary = ' '.join([sentences[x] for x in summary_sentences])

    title = get_top(word_freq, title_n)
    title = " ".join(title)

    response = {"title": title, "whole_sentiment": whole_sentiment, "summary": summary, "segments": new_sentences, "sentiments": sentiments} 
    return response

