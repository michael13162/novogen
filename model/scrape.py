import requests
from bs4 import BeautifulSoup
from search import engine
import pickle

class Molecule:
	def __init__(self, disease, drug_name, molecule_name, smiles):
		self.disease = disease
		self.drug_name = drug_name
		self.smiles = smiles
		self.molecule_name = molecule_name
		return

def molecule_name_to_smiles(molecule_name):
	link = "https://www.ncbi.nlm.nih.gov/pccompound?term=" + molecule_name.replace(' ', '%20')
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
				return smiles 
	return ""			

def extract_content(soup):
	links = soup.find_all('a', attrs={'class': 'ToggleDrugCategory'})
	divs = soup.find_all('div', attrs={'class': 'CategoryListSection'})    
	results = []

	for i in range(0, len(links)):
		disease_title = links[i].text		
		for j in divs[i].select("a"):
			if "/drug/" in j["href"]:				
				drug_name = j.text
				molecule_name = drug_name[drug_name.find("(")+1:drug_name.find(")")]		
				smiles = molecule_name_to_smiles(molecule_name)
				if smiles != "":
					mol = Molecule(disease=disease_title, drug_name=drug_name, molecule_name=molecule_name, smiles=smiles)	
					results.append(mol)									
					print("Created Molecule")										
	return results					

def scrape_letter(letter):
	link = 'https://www.centerwatch.com/drug-information/fda-approved-drugs/medical-conditions/' + letter
	r = requests.get(link)
	content = r.text
	soup = BeautifulSoup(content, "html5lib")
	results = extract_content(soup)
	return results

'''
res = []
for letter in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
	print("Searching section", letter)
	result = scrape_letter(letter)
	for i in result:
		res.append(i)

with open("RESULT.pkl", 'wb') as output:   
	print "Saving..."
	pickle.dump(res, output)	
print("script done!")		
'''
