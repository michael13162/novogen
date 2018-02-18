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
        scale = 3
        img = Draw.MolToImage(mol, size=(155*scale, 68*scale), fitImage=True)
        
        # Make img transparent background
        img = img.convert("RGBA")
        datas = img.getdata()        
        newData = []
        for item in datas:
            if item[0] == 255 and item[1] == 255 and item[2] == 255:
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)        
        img.putdata(newData)
        
        self.molecular_img = img
        
        return