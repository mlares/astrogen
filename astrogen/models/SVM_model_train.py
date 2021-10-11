import matplotlib.pyplot as plt

from sklearn.svm import LinearSVC
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn import svm

from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler

from sklearn import metrics
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score, precision_score, f1_score
from sklearn.metrics import classification_report,plot_confusion_matrix,plot_roc_curve

import numpy as np
import pandas as pd
from time import time
import pickle

np.random.seed(0)

import warnings
warnings.filterwarnings("ignore")

D = pd.read_csv('papers_learn.csv', header=None)
X = D.drop(columns=[6,7,8,9,10,11,12,13])

# Scale
scaler = StandardScaler()
scaler.fit(X)
X = scaler.transform(X)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3) #, random_state=20)

#Create a svm Classifier
clf = svm.SVC(kernel='linear', probability=True)

#Train the model using the training sets
clf.fit(X_train, y_train)

#Predict the response for test dataset
y_pred = clf.predict_proba(X_test)

d = y_test - y_pred[:,1]

y_predL = y_pred[:,0]*[0]
y_predL[y_pred[:,1]>0.5] = 1

y_predL = y_predL.astype(int)

   
from joblib import dump, load

dump([clf, scaler], 'SVM_model.joblib')

