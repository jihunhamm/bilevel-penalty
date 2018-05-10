# -*- coding: utf-8 -*-
"""
Created on Wed May 09 08:39:33 2018

@author: Akshay
"""
## test_cw_mnist.py
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


import sys
#sys.path.append('/home/hammj/Dropbox/Research/AdversarialLearning/codes/lib/cleverhans-master')

import numpy as np
from six.moves import xrange
import tensorflow as tf
from tensorflow.python.platform import flags

import logging
import os
from cleverhans.utils import pair_visual, grid_visual, AccuracyReport
from cleverhans.utils import set_log_level
from cleverhans.utils_mnist import data_mnist
from cleverhans.utils_tf import model_train, model_eval, tf_model_load, batch_eval, model_argmax
from cleverhans_tutorials.tutorial_models import make_basic_cnn
import time
from cleverhans.utils_tf import model_loss

# Load the training, test and validation set
X_train = np.load("X_train.npy")
Y_train = np.load("Y_train.npy")
X_val = np.load("X_val.npy")
Y_val = np.load("Y_val.npy")
X_test = np.load("X_test.npy")
Y_test = np.load("Y_test.npy")


# We know that SVHN images have 32 pixels in each dimension
img_rows = X_train.shape[1]
img_cols = X_train.shape[2]
# Greyscale images only have 1 color channel
channels = X_train.shape[-1]

# Number of classes, one class for each of 10 digits
num_classes = Y_train.shape[1]
        
print('Training set', X_train.shape, Y_train.shape)
print('Validation set', X_val.shape, Y_val.shape)
print('Test set', X_test.shape, Y_test.shape)

# Object used to keep track of (and return) key accuracies
report = AccuracyReport()
# Set TF random seed to improve reproducibility
tf.set_random_seed(1234)

# Create TF session
sess = tf.Session()
print("Created TensorFlow session.")

set_log_level(logging.DEBUG)
# Define input TF placeholder
x_tf = tf.placeholder(tf.float32, shape=(None, img_rows, img_cols, channels))
y_tf = tf.placeholder(tf.float32, shape=(None, 10))

# Define TF model graph
scope_model = 'mnist_classifier'
with tf.variable_scope(scope_model):    
    model = make_basic_cnn()
preds = model(x_tf)
    
var_model = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES,scope=scope_model)        
saver_model = tf.train.Saver(var_model,max_to_keep=None)
print("Defined TensorFlow model graph.")

###########################################################################
# Training the model using TensorFlow
###########################################################################

# Train an MNIST model
train_params = {
    'nb_epochs': 100,
    'batch_size': 128,
    'learning_rate': 1E-3,
}

rng = np.random.RandomState([2017, 8, 30])

batch_size = min(128, len(X_val))


for pct in [0, 1]: # percentile from top
    
    if pct == 0:
        importance = np.load("importance.npy")
        ind = np.argsort(importance)
        for it in range(1, 6):
            till = int(500 * it)
            print(importance[ind[-till:]])
            X = X_train[ind[-till:]]
            print(len(X))
            Y = Y_train[ind[-till:]]
            print(len(Y)) 
            sess.run(tf.global_variables_initializer())
            model_train(sess, x_tf, y_tf, preds, X, Y, args=train_params, save=os.path.exists("models"), rng=rng)
            eval_params = {'batch_size': 128}
            accuracy = model_eval(sess, x_tf, y_tf, preds, X_test, Y_test, args=eval_params)
            print('Test accuracy of the MT: {0}'.format(accuracy))
            accuracy = model_eval(sess, x_tf, y_tf, preds, X_val, Y_val, args=eval_params)
            print('Test accuracy of the MT: {0}'.format(accuracy))
            
    elif pct == 1:
        importance = np.random.randn(X_train.shape[0])
        ind = np.argsort(importance)
        for it in range(1, 6):
            till = int(500 * it)
            print(importance[ind[-till:]])
            X = X_train[ind[-till:]]
            print(len(X))
            Y = Y_train[ind[-till:]]
            print(len(Y)) 
            sess.run(tf.global_variables_initializer())
            model_train(sess, x_tf, y_tf, preds, X, Y, args=train_params, rng=rng)
            eval_params = {'batch_size': 128}
            accuracy = model_eval(sess, x_tf, y_tf, preds, X_test, Y_test, args=eval_params)
            print('Test accuracy of the random: {0}'.format(accuracy))
            accuracy = model_eval(sess, x_tf, y_tf, preds, X_val, Y_val, args=eval_params)
            print('Test accuracy of the MT: {0}'.format(accuracy))
   
    elif pct == 2:
        
        importance = np.load("importance.npy")
        ind = np.argwhere(importance > np.median(importance)).flatten()
        print(ind)
        X = X_train[ind]
        print(len(X))
        Y = Y_train[ind]
        print(len(Y)) 
        sess.run(tf.global_variables_initializer())
        model_train(sess, x_tf, y_tf, preds, X, Y, args=train_params, rng=rng)
        eval_params = {'batch_size': 128}
        accuracy = model_eval(sess, x_tf, y_tf, preds, X_test, Y_test, args=eval_params)
        print('Test accuracy of the MT: {0}'.format(accuracy))
    
    elif pct == 3:
        
        importance = np.load("importance.npy")
        ind = np.argwhere(importance > np.median(importance))
        p = len(ind)
        print(p)
        
        importance = np.random.randn(X_train.shape[0])
        ind = np.argsort(importance)
        X = X_train[ind[:p]]
        print(len(X))
        Y = Y_train[ind[:p]]
        print(len(Y)) 
        sess.run(tf.global_variables_initializer())
        model_train(sess, x_tf, y_tf, preds, X, Y, args=train_params, rng=rng)
        eval_params = {'batch_size': 128}
        accuracy = model_eval(sess, x_tf, y_tf, preds, X_test, Y_test, args=eval_params)
        print('Test accuracy of the MT: {0}'.format(accuracy))