#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 16 20:23:06 2018

@author: josharnold
"""

import pandas as pd
import numpy as np
import os, pickle
from sklearn.cross_validation import train_test_split

class utils:    
    def extract_smiles(data, index=1):
        smiles = []
        minLen = 10000
        maxLen = 0
        for d in data[0]:
            molecule = d.split()[index]
            smiles.append(molecule)
            if len(molecule) > maxLen:
                maxLen = len(molecule)
            elif len(molecule) < minLen:
                minLen = len(molecule)                                        
        return np.array(smiles)
    
    def vectorize(self, smiles, preprocessing_instance):
        one_hot =  np.zeros((smiles.shape[0], preprocessing_instance.embed , len(preprocessing_instance.charset)),dtype=np.int8)
        for i,smile in enumerate(smiles):
            one_hot[i,0,preprocessing_instance.char_to_int["!"]] = 1
            for j,c in enumerate(smile):
                one_hot[i,j+1,preprocessing_instance.char_to_int[c]] = 1
            one_hot[i,len(smile)+1:,preprocessing_instance.char_to_int["E"]] = 1
        return one_hot[:,0:-1,:], one_hot[:,1:,:]

class preprocessing:    
    charset = None
    char_to_int = None
    int_to_char = None
    embed = None
           
    def load_data(self, file_name = "model/gdb11_size08.smi", load_char_set=True, pad=30):
        data = pd.read_csv(file_name, delimiter = "\t", names = ["smiles","No","Int"])
        smiles_train, smiles_test = train_test_split(data["smiles"], random_state=42)  
        
        self.charset = set("".join(list(data.smiles))+"!E")   
        
        self.char_to_int = dict((c,i) for i,c in enumerate(self.charset))
        self.int_to_char = dict((i,c) for i,c in enumerate(self.charset))
        
        if (load_char_set==True):
            self.load_charset()
        
        self.embed = max([len(smile) for smile in data.smiles]) + pad
        
        X_train, y_train = utils().vectorize(smiles_train.values, self)
        X_test,y_test = utils().vectorize(smiles_test.values, self)
        return X_train, y_train, X_test, y_test

    def load_charset(self):
        if (os.path.exists("model/char_to_int.pkl") and os.path.exists("model/int_to_char.pkl")):
            with open('model/char_to_int.pkl', 'rb') as path:
                self.char_to_int = pickle.load(path)            
            with open('model/int_to_char.pkl', 'rb') as path:
                self.int_to_char = pickle.load(path)
        return
    
    def process_smiles(self, smiles):  
        smiles = np.array(smiles)
        X_train, y_train = utils().vectorize(smiles, self)
        return X_train
