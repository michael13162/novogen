#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 16 20:29:55 2018

@author: josharnold
"""

from data import preprocessing
from model import nn

def gen(target_molecules):   
    for i in range(0, len(target_molecules)):
        mol = target_molecules[i]
        while(len(mol) > 50):
            mol = mol[:-1] 
            target_molecules[i] = mol
            
    # Create preprocessing instance
    pp = preprocessing()    

    # Load data from small data set
    X_train, y_train, X_test, y_test = pp.load_data()     
    
    # Remove non characters
    for i in range(0, len(target_molecules)):
        mol = target_molecules[i]
        for char in mol:
            if char in pp.charset:
                print("We good.")
            else:
                mol = mol.replace(char, '')
                target_molecules[i] = mol
                print("Oopps. Removing bad char:", char)   
                         
    # Create & load model
    model = nn(X_train, y_train, X_test, y_test)
    model.load(pp)
      
    # Generate a molecule
    molecules = model.generate(target=target_molecules, preprocessing_instance=pp, hit_rate=20)
    return molecules
