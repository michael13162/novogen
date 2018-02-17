#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 16:46:05 2018

@author: josharnold
"""

from data import preprocessing
from model import nn

# Load data
X_train, y_train, X_test, y_test = preprocessing.load_data(load_char_set=False, pad=25)

# Define model
model = nn(X_train, y_train, X_test, y_test)

# Create model
model.create_model()

# Set num epochs
model.num_epochs = 125

# Train
model.train(show_loss=True)

# Save
model.save(force_overwrite=True)

# Predict
model.predict(7)