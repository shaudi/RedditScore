import os

import numpy as np
import pandas as pd
import pytest
from sklearn.model_selection import GridSearchCV

from redditscore.models import fasttext, sklearn
from redditscore.tokenizer import CrazyTokenizer

df = pd.read_csv(os.path.join(os.path.dirname(__file__), '..',
                              'redditscore', 'data', 'reddit_small_sample.csv'))

tokenizer = CrazyTokenizer(urls='domain')
df['tokens'] = df['body'].apply(tokenizer.tokenize)

political_subs = ['AskTrumpSupporters', 'EnoughTrumpSpam', 'AskThe_Donald',
                  'conservatives', 'The_Donald', 'politics',
                  'PoliticalDiscussion', 'hillaryclinton', 'Conservative',
                  'SandersForPresident', 'Libertarian', 'esist', 'Fuckthealtright',
                  'democrats', 'HillaryForPrison', 'NeutralPolitics',
                  'Republican', 'uspolitics', 'Liberal', 'conspiracy']
alt_subs = ['CoonTown', 'uncensorednews', 'sjwhate', 'PussyPass',
            'whiteknighting', 'CringeAnarchy', 'KotakuInAction', 'DebateAltRight',
            'SocialJusticeInAction', 'WhiteRights', 'AntiPOZi',
            'TumblrInAction', 'altright', '4chan', 'dankmemes',
            'MGTOW', 'TheRedPill']

X = df['tokens']
y = df['subreddit']


def test_model_init():
    multi_model = sklearn.SklearnModel(
        model_type='multinomial', alpha=0.1, random_state=24, tfidf=False, ngrams=1)
    bernoulli_model = sklearn.SklearnModel(
        model_type='bernoulli', alpha=0.1, random_state=24, tfidf=False, ngrams=1)
    svm_model = sklearn.SklearnModel(model_type='svm', C=0.1,
                                     random_state=24, tfidf=False, ngrams=1)
    fasttext_model = fasttext.FastTextModel(minCount=5)


def test_multimodel():
    multi_model = sklearn.SklearnModel(model_type='multinomial')
    multi_model.tune_params(X, y, cv=0.2, scoring='neg_log_loss',
                            param_grid={'tfidf': [False, True]})
    multi_model.tune_params(X, y, cv=5, scoring='accuracy',
                            param_grid={'tfidf': [False, True],
                                        'alpha': [0.1, 1.0]}, refit=True)
    multi_model.predict(X)
    multi_model.predict_proba(X)


def test_bernoulli():
    bernoulli_model = sklearn.SklearnModel(model_type='bernoulli')
    bernoulli_model.tune_params(X, y, cv=0.2, scoring='neg_log_loss',
                                param_grid={'tfidf': [False, True]})
    bernoulli_model.tune_params(X[0:10], y[0:10], cv=0.2)
    bernoulli_model.tune_params(X, y, cv=5, scoring='accuracy',
                                param_grid={'tfidf': [False, True],
                                            'alpha': [0.1, 1.0]}, refit=True)
    bernoulli_model.predict(X)
    bernoulli_model.predict_proba(X)


def test_fasttext_train():
    fasttext_model = fasttext.FastTextModel(minCount=5)
    fasttext_model.fit(X, y)
    fasttext_model.predict(X)
    fasttext_model.predict_proba(X)
    fasttext_model.tune_params(X, y, cv=0.2, param_grid={
                               'step0': {'epoch': [1, 2]},
                               'step1': {'minCount': [1, 5]}})


def test_step_exception():
    fasttext_model = fasttext.FastTextModel(minCount=5)
    with pytest.raises(KeyError) as e_info:
        fasttext_model.tune_params(X, y, cv=0.2, param_grid={
                                   'step0': {'epoch': [1, 2]},
                                   'step2': {'minCount': [1, 5]}})
