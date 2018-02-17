#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 16 20:29:55 2018

@author: josharnold
"""

from model.data import preprocessing
from model import nn

# Load data from small data set
X_train, y_train, X_test, y_test = preprocessing.load_small_dataset()

# Create & load model
model = nn(X_train, y_train, X_test, y_test)
model.load()

# Molecules to use as a seed for generating
target_molecules = ['NC=NC1CN1CO', 'CC1=CNCN2CC12']

# Generate a molecule
molecules = model.generate(target=target_molecules)

# Parse molecules to json...?