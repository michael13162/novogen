import openbabel
import pybel

def convert(smiles_array):
	cmlMols = []
	for smile in smiles_array:
		obConversion = openbabel.OBConversion()
		obConversion.SetInAndOutFormats("smi", "cml")
		obmol = openbabel.OBMol()
		obConversion.ReadString(obmol, "CC12CC3CC(C1)(CC(C3)(C2)N)C")
		cmlMol = obConversion.WriteString(obmol)
		cmlMols.append(cmlMol)
	return cmlMols


