import os
import pandas as pd
import time

from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline

from sklearn import model_selection as ms
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import BaggingClassifier
from sklearn.svm import SVC

import build_train_test

data_path = '/home/tlappas/data_science/Yelp-Ratings/data/processed/processed_alice'

classifiers = [
    KNeighborsClassifier(),
    SVC(),
    RandomForestClassifier(max_depth=5), # Random Forest documentation recommends setting a default max_depth so trees don't become enormous.
    AdaBoostClassifier(),
    GaussianNB(),
    MultinomialNB(),
    BaggingClassifier()
]

# Import Data
print('Loading data.')
data = build_train_test.load_batch_data(1, data_path)
print('Convert word lists into strings.')
data['processed_text'] = data['processed_text'].apply(' '.join)
# Get Labels
data = build_train_test.join_labels(data, 'yelp', 'tlappas', '/var/run/postgresql/', 'SYK&kI#4')
# Set Class labels
# data.apply(data.loc[:,'stars'], build_train_test.remap_labels([1,2,3,4,5], [1,2,3,4,5]))
# Split into training and testing
print('Split data into train and test sets.')
[x_train, x_test, y_train, y_test] = build_train_test.split(data.loc[:,'processed_text'], data.loc[:,'stars'], save_data=False)

# Transform
print('Transform the datasets into tf-idf sparse arrays.')
x_train = TfidfVectorizer(ngram_range=(1,2)).fit_transform(x_train)
x_test = TfidfVectorizer(ngram_range=(1,2)).fit_transform(x_test)

# Print data info
print('Number of Instances: {}'.format(data.shape[0]))
print('\tTraining instances: {}'.format(x_train.shape[0]))
print('\tTesting instances: {}\n'.format(x_test.shape[0]))

strat_kfold = ms.StratifiedKFold(n_splits=5, shuffle=True)
print('Cross-validation: {} folds\n'.format(strat_kfold.get_n_splits))

for estimator in classifiers:

    print('{} fitting - '.format(estimator.__class__.__name__), end='')
    # Fit model
    time_start = time.time()
    estimator.fit(x_train, y_train)
    time_stop = time.time()
    elapsed = time_stop - time_start
    print('{} minutes {} seconds'.format(elapsed // 60, elapsed % 60))

    # Predict on the training dataset
    print('{} predict training - '.format(estimator.__class__.__name__), end='')
    time_start = time.time()
    train_predictions = estimator.predict(x_train)
    time_stop = time.time()
    elapsed = time_stop - time_start
    print('{} minutes {} seconds'.format(elapsed // 60, elapsed % 60))
    print('\tTraining Accuracy Score: {}'.format(accuracy_score(train_predictions, y_train)))
    print('\tTraining F1 Score: {}\n'.format(f1_score(train_predictions, y_train)))

    # Predict on test dataset
    print('{} predict testing - '.format(estimator.__class__.__name__), end='')
    time_start = time.time()
    test_predictions = estimator.predict(x_test)
    time_stop = time.time()
    elapsed = time_stop - time_start
    print('{} minutes {} seconds'.format(elapsed // 60, elapsed % 60))
    print('\tTesting Accuracy Score: {}'.format(accuracy_score(test_predictions, y_test)))
    print('\tTesting F1 Score: {}'.format(f1_score(test_predictions, y_test)))
    print('\n')
