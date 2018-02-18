import requests
from bs4 import BeautifulSoup
from search import engine
import pickle

print("Starting scrape...")

def extract_content(soup):

	links = soup.find_all('a', attrs={'class': 'ToggleDrugCategory'})
	divs = soup.find_all('div', attrs={'class': 'CategoryListSection'})    

	if (len(links) != len(divs)):
		print("Uh oh. Unable to parse links and divs.")
		return

	results = []

	for i in range(0, len(links)):
		disease = links[i].text		
		drug_names = []	
		for j in divs[i].select("a"):
			if "/drug/" in j["href"]:
				drug_name = j.text + " " + disease
				s = j.text
				drug_names.append(drug_name)
		names_output, smiles_output = engine().drug_names_to_smiles(s[s.find("(")+1:s.find(")")])
		print smiles_output
		outcome = (names_output, smiles_output)
		results.append(outcome)
	return results

def scrape_letter(letter):
	link = 'https://www.centerwatch.com/drug-information/fda-approved-drugs/medical-conditions/' + letter
	r = requests.get(link)
	content = r.text
	soup = BeautifulSoup(content, "html5lib")
	results = extract_content(soup)
	return results

for letter in ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
	print letter, "almost there D:"
	result = scrape_letter(letter)
	s = letter + ".pkl"
	with open(s, 'wb') as output:   
		pickle.dump(result, output)		
print("script done!")		