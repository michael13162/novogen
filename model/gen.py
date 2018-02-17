#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 16 20:29:55 2018

@author: josharnold
"""

from data import preprocessing
from model import nn

# Load data from small data set
X_train, y_train, X_test, y_test = preprocessing.load_data(file_name = "gdb11_size08.smi", load_char_set=True, pad=30)

# Create & load model
model = nn(X_train, y_train, X_test, y_test)
model.load()

# Molecules to use as a seed for generating
#target_molecules = ['NC=NC1CN1CO', 'CC1=CNCN2CC12', 'FC1CCC1(F)C=C', 'CC1=COnnnn1']

# Target Asprin, Cocaine, Dopamine & THC
#target_molecules = ['CC(=O)OC1=CC=CC=C1C(=O)O', 'CN1C2CCC1C(C(C2)OC(=O)C3=CC=CC=C3)C(=O)OC','C1=CC(=C(C=C1CCN)O)O', 'CCCCCC1=CC2=C(C3C=C(CCC3C(O2)(C)C)C)C(=C1)O']

target_molecules = ["CCN(C)C(=O)OC1=CC=CC(=C1)C(C)N(C)C", 
                    "CC12CC3CC(C1)(CC(C3)(C2)N)C", "CN1CCC23C=CC(CC2OC4=C(C=CC(=C34)C1)OC)O"]

# Generate a molecule
molecules = model.generate(target=target_molecules)

for mol in molecules:
    mol.molecular_img.show()

# Parse molecules to json...?