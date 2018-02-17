#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 16 20:42:40 2018

@author: josharnold
"""

from rdkit import Chem
from rdkit.Chem import Descriptors
from rdkit.Chem import Draw

class molecule:
    
    def __init__(self, smiles):
        
        self.smiles = smiles
        
        mol = Chem.MolFromSmiles(smiles)
        
        # LogP
        self.log_p = Descriptors.MolLogP(mol)
        
        # Topological surce area 
        self.tpsa = Descriptors.TPSA(mol)
        
        # Hydrogrent donors
        self.num_h_donors = Chem.Lipinski.NumHDonors(mol)
        
        # Hydrogrent acceptors
        self.num_h_acceptors = Chem.Lipinski.NumHAcceptors(mol)
        
        # Molecular weight
        self.molecular_weight = Chem.rdMolDescriptors._CalcMolWt(mol)
        
        # Draw molecule
        img = Draw.MolToImage(mol, size=(500, 500), fitImage=True)
        self.molecular_img = img
        
        return