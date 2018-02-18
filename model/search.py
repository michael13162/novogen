#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 07:41:23 2018

@author: josharnold
"""

import requests
from bs4 import BeautifulSoup

class engine:
    
    def search(self, query):   
        if len(query) > 6:
            query = query[:-4]
        first_letter = query[0]
        link = 'https://www.centerwatch.com/drug-information/fda-approved-drugs/medical-conditions/' + first_letter        
        r = requests.get(link)
        content = r.text        
        drug_names, descriptions = self.find_drugs_in_content(query, content)                
        names_output, smiles_output = self.drug_names_to_smiles(drug_names)        
        return names_output, smiles_output, descriptions
    
    def find_drugs_in_content(self, query, content):        
        soup = BeautifulSoup(content, 'html.parser')
        links = soup.find_all('a', attrs={'class': 'ToggleDrugCategory'})
        des = soup.find_all('div', attrs={'class': 'CategoryListSection'})        
        main_des = None        
        for i in range(0, len(links)):
            link = links[i]
            if ((link.text in query) or (query in link.text)):
                main_des = des[i]
                break                        
        names = []
        descriptions = []            
        for i in main_des.select("a"):
            s = i.text
            s = s[s.find("(")+1:s.find(")")]
            names.append(s)
        for i in main_des.select("p"):
            des = i.text
            des = des.replace('                        ', '') # Looks sketch but trust me lol
            descriptions.append(des)                
        return names, descriptions
    
    def drug_names_to_smiles(self, names):    
        names_output = []
        smiles_output = []
        for name in names:
            link = "https://www.ncbi.nlm.nih.gov/pccompound?term=" + name.replace(' ', '%20')
            r = requests.get(link).content
            soup = BeautifulSoup(r, 'html.parser')
            link = soup.find('p', attrs={'class': 'title'})
            if link != None:
                for i in link:
                    soup = BeautifulSoup(str(i))
                    for a in soup.find_all('a', href=True):
                        link = a['href'] + "end"                                                
                        s = link                  
                        start = 'compound/'
                        end = 'end'                       
                        s = s[s.find(start)+len(start):s.rfind(end)]
                        link = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/" + s + "/property/CanonicalSMILES/txt"
                        smiles = requests.get(link).text
                        smiles = smiles.replace('.','')
                        if len(smiles) < 51:
                            names_output.append(name)
                            smiles_output.append(smiles)                                                        
        return names_output, smiles_output
    

names_output, smiles_output, descriptions = engine().search("Alzheim")
#names_output, smiles_output, descriptions = engine.search("Cancer")    
#print(names_output, smiles_output, descriptions)
print(smiles_output)
