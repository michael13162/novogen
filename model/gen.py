#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 16 20:29:55 2018

@author: josharnold
"""

from model.data import preprocessing
from model.model import nn


def gen(target_molecules):
    # Load data from small data set
    X_train, y_train, X_test, y_test = preprocessing.load_small_dataset()

    # Create & load model
    model = nn(X_train, y_train, X_test, y_test)
    model.load()

    # Generate a molecule
    molecules = model.generate(target=target_molecules)

    return molecules
