from __future__ import print_function

from pprint import pprint
from time import time
import logging

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.grid_search import GridSearchCV
from sklearn.pipeline import Pipeline

from preprocess import norm_tweets_file_name, read_normalized_tweets

# Display progress logs on stdout
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

# Load data from the training set
labeled_tweets = read_normalized_tweets(norm_tweets_file_name) # list of tuples (label, string_of_normalized_words)
print(type(labeled_tweets), len(labeled_tweets))

data = []
target = []

for item in labeled_tweets:
    label = item[0]
    target.append(int(label))

    tweet = item[1]
    data.append(tweet)

##############################################################################
# define a pipeline combining a text feature extractor with a simple classifier
pipeline = Pipeline([
    ('vect', CountVectorizer()),
    ('tfidf', TfidfTransformer()),
    ('clf', SGDClassifier()),
])

# uncommenting more parameters will give better exploring power but will
# increase processing time in a combinatorial way
parameters = {
    # 'vect__decode_error': ('strict', 'ignore', 'replace'),
    # 'vect__strip_accents': ('ascii', 'unicode', None),
    'vect__analyzer': ('word', 'char', 'char_wb'),
    'vect__ngram_range': ((1, 1), (1, 2), (1, 3)),  # unigrams, bigrams, trigrams
    'vect__stop_words': ('english', None),
    'vect__max_df': (0.5, 0.75, 1.0),
    'vect__max_features': (None, 5000, 10000, 50000),
    # 'vect__binary': (True, False),

    # 'tfidf__decode_error': ('strict', 'ignore', 'replace'),
    # 'tfidf__strip_accents': ('ascii', 'unicode', None),
    # 'tfidf__analyzer': ('word', 'char'),
    # 'tfidf__ngram_range': ((1, 1), (1, 2), (1, 3)),  # unigrams, bigrams, trigrams
    # 'tfidf__stop_words': ('english', None),
    # 'tfidf__lowercase': (True, False),
    # 'tfidf__max_df': (0.5, 0.75, 1.0),
    # 'tfidf__min_df': (0.0, 0.25, 0.5),
    # 'tfidf__max_features': (None, 5000, 10000, 50000, 100000),
    'tfidf__norm': ('l1', 'l2', None),
    'tfidf__use_idf': (True, False),
    # 'tfidf__smooth_idf': (True, False),
    # 'tfidf__sublinear_tf': (True, False),

    # 'clf__loss': ('hinge', 'log', 'modified_huber', 'squared_hinge', 'perceptron'),
    'clf__penalty': ('none', 'l1', 'l2', 'elasticnet'),
    'clf__alpha': (0.01, 0.001, 0.0001, 0.00001, 0.000001),
    # 'clf__l1_ratio': (0, 0.15, 0.3, 0.45, 0.6, 0.75, 0.9, 1.0),
    # 'clf__fit_intercept': (True, False),
    'clf__n_iter': (1, 5, 10, 50, 80),
    # 'clf__shuffle': (True, False),
    # 'clf__verbose': (1, 5, 10),
    # 'clf__warm_start': (True, False),
}

# sample parameters
# parameters = {
#     'vect__max_df': (0.5, 0.75, 1.0),
#     'vect__max_features': (None, 5000, 10000, 50000),
#     'vect__ngram_range': ((1, 1), (1, 2)),  # unigrams or bigrams
#     'tfidf__use_idf': (True, False),
#     'tfidf__norm': ('l1', 'l2'),
#     'clf__alpha': (0.00001, 0.000001),
#     'clf__penalty': ('l2', 'elasticnet'),
#     'clf__n_iter': (10, 50, 80),
# }

if __name__ == "__main__":
    # multiprocessing requires the fork to happen in a __main__ protected
    # block

    # find the best parameters for both the feature extraction and the classifier
    grid_search = GridSearchCV(pipeline, parameters, n_jobs=-1, verbose=1)

    print("Performing grid search...")
    print("pipeline:", [name for name, _ in pipeline.steps])
    print("parameters:")
    pprint(parameters)
    t0 = time()
    grid_search.fit(data, target)
    print("done in %0.3fs" % (time() - t0))
    print()

    print("Best score: %0.3f" % grid_search.best_score_)
    print("Best parameters set:")
    best_parameters = grid_search.best_estimator_.get_params()
    for param_name in sorted(parameters.keys()):
        print("\t%s: %r" % (param_name, best_parameters[param_name]))