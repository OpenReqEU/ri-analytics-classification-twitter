import uuid

import numpy as np

from feature_extractor.extractor_facade import FeatureExtractor
from model_factory import CFG_PBR, ModelFactory

KEY_TWEET_CLASS = 'tweet_class'
KEY_TWEET_CLASS_PROBA = 'classifier_certainty'

TWEET_CLASS_PBR = 'problem_report'
TWEET_CLASS_INQ = 'inquiry'
TWEET_CLASS_IRR = 'irrelevant'

def process_tweets(tweets, lang):
    model = ModelFactory.create(lang)
    classified_tweets = classify(model, tweets)
    return classified_tweets

def classify(model, tweets):
    unique_id = uuid.uuid4()
    # print('{}, start classification of {} tweets'.format(unique_id, len(tweets)))

    ###################
    # prepare tweets
    ###################
    encoded_tweets = []
    for t in tweets:
        tweet = dict(t)
        tweet['text'] = t['text'].encode('ascii', errors='ignore').decode("utf-8")
        encoded_tweets.append(tweet)

    ###################
    # extract ml features and classify tweets
    ###################
    classified_tweets = []
    for tweet in encoded_tweets:
        universal_feature_vector = None
        if model.are_feature_vectors_identical:
            universal_feature_vector = FeatureExtractor(model.cfg_irr, model.lang, tweet)

        is_irrelevant, proba = get_classification_result(TWEET_CLASS_IRR, model, tweet, universal_feature_vector)
        if is_irrelevant:
            tweet[KEY_TWEET_CLASS] = TWEET_CLASS_IRR
            tweet[KEY_TWEET_CLASS_PROBA] = proba
            classified_tweets.append(tweet)
            continue
        is_inquiry, proba = get_classification_result(TWEET_CLASS_INQ, model, tweet, universal_feature_vector)
        if is_inquiry:
            tweet[KEY_TWEET_CLASS] = TWEET_CLASS_INQ
            tweet[KEY_TWEET_CLASS_PROBA] = proba
            classified_tweets.append(tweet)
            continue

        is_problem_report, proba = get_classification_result(TWEET_CLASS_PBR, model, tweet, universal_feature_vector)
        if is_problem_report:
            tweet[KEY_TWEET_CLASS] = TWEET_CLASS_PBR
            tweet[KEY_TWEET_CLASS_PROBA] = proba
            classified_tweets.append(tweet)
            continue

        # if no class was identified mark the tweet as irrelevant
        tweet[KEY_TWEET_CLASS] = TWEET_CLASS_IRR
        tweet[KEY_TWEET_CLASS_PROBA] = -1
        classified_tweets.append(tweet)

    return classified_tweets

def get_classification_result(target, model, tweet, universal_feature_vector):
    is_target = False
    proba = None

    if target == TWEET_CLASS_IRR:
        model_irr = universal_feature_vector if universal_feature_vector else FeatureExtractor(model.cfg_irr, model.lang, tweet)
        is_target = int(model.clf_irr.predict(model_irr.data_vector)[0]) == 1
        try:
            proba = model.clf_irr.predict_proba(model_irr.data_vector)[0][1]
            proba = int(proba*100)
        except:
            proba = -1

    elif target == TWEET_CLASS_INQ:
        model_inq =  universal_feature_vector if universal_feature_vector else FeatureExtractor(model.cfg_inq, model.lang, tweet)
        is_target = int(model.clf_inq.predict(model_inq.data_vector)[0]) == 1
        try:
            proba = model.clf_inq.predict_proba(model_inq.data_vector)[0][1]
            proba = int(proba*100)
        except:
            proba = -1

    elif target == TWEET_CLASS_PBR:
        model_pbr =  universal_feature_vector if universal_feature_vector else FeatureExtractor(model.cfg_pbr, model.lang, tweet)
        is_target = int(model.clf_pbr.predict(model_pbr.data_vector)[0]) == 1
        try:
            proba = model.clf_pbr.predict_proba(model_pbr.data_vector)[0][1]
            proba = int(proba*100)
        except:
            proba = -1
    
    return is_target, proba
