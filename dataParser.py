import sys, math
import csv
from time import strptime
from dataStructures import Graph
from decimal import Decimal
nodes = ['X','Y','month','day','FFMC','DMC','DC','ISI','temp','RH','wind','rain','area']
days = {'mon':1, 'tue':2, 'wed':3, 'thu':4, 'fri':5, 'sat':6, 'sun':7}

m = Decimal(1) #Decimal(10.0012**131)

dataDict = []
dataDict_Q = []
priorsDict = []
priors_Q =[]

gamma = lambda x: math.factorial(x-1)
antilog = lambda x: Decimal(10)**x

def createSimpleGraph(G):
	with open(sys.argv[3], 'r') as f:
		parentsToNode = list(csv.reader(f))
	for ptn in parentsToNode:
		ptn = [v.strip() for v in ptn]
		print(ptn)
		G.addParentsToNode(ptn.pop(0), ptn)

noParents = lambda n: len(n.parents) == 0

def calculateNoParentNodeScore(node, score):
	sig_n = sum([x[1] for x in node.values])
	sig_a = sum([x[1] for x in node.priors])
	#print("calculateNoParentNodeScore:sigma n =", sig_n, "sigma a =" ,sig_a)
	#print("calculateNoParentNodeScore:gamma", sig_a, "gamma", (sig_a + sig_n))
	score += (Decimal(gamma(sig_a)) / Decimal(gamma(sig_a + sig_n))).log10()
	for i in range(0, len(node.priors)):
		a = node.priors[i][1]
		n = node.values[i][1]
		#print("a =",a,"n = ",n)
		a = 1 if a == 0 else a
		#print("calculateNoParentNodeScore a+n: gamma",(a + n), "a:gamma",a)
		score += (Decimal(gamma(a + n)) / Decimal(gamma(a))).log10()
		#print("calculateNoParentNodeScore:score after", i ,"values:", score)
	return score

def calculateNodeScore(node, parent, score): #for one parent
	#print(node.name, parent.name)
	n_i = nodes.index(node.name)
	p_i = nodes.index(parent.name)
	for j in parent.priors:
		#print("calculateNodeScore:value = ", j[0], "in", parent.name)
		sig_n = len([x[n_i] for x in dataDict_Q if x[p_i]==j[0]])
		sig_a = len([x[n_i] for x in priors_Q if x[p_i]==j[0]])
		#print("calculateNodeScore: gamma",(sig_a), "gamma", (sig_a + sig_n))
		score += (Decimal(gamma(sig_a)) / Decimal(gamma(sig_a + sig_n))).log10()
		for k in node.priors:
			#print("calculateNodeScore:value of node", node.name, "is ", k[0], ", value of parent", parent.name, "is", j[0])
			n = len([x[n_i] for x in dataDict_Q if x[n_i]==k[0] and x[p_i]==j[0]])
			a = len([x[n_i] for x in priors_Q if x[n_i]==k[0] and x[p_i]==j[0]])
			#print([x for x in dataDict_Q if x[n_i]==k[0] and x[p_i]==j[0]])
			#print([x for x in priors_Q if x[n_i]==k[0] and x[p_i]==j[0]])
			#print("calculateNodeScore:for k in node.values: n =", n,"a =", a)
			a = 1 if a == 0 else a
			#print("value = " ,(Decimal(gamma(a + n)) / Decimal(gamma(a))).log10())
			#print("calculateNodeScore a+n: gamma", (a + n), "a:gamma", a)
			score += (Decimal(gamma(a + n)) / Decimal(gamma(a))).log10()
	return score

def getGraphScore(G, currentScore=0):
	#print("getGraphScore")
	for node in G.nodes:
		if noParents(node):
			currentScore += calculateNoParentNodeScore(node, currentScore)
		else:
			for parent in node.parents: #for every parent
				currentScore += calculateNodeScore(node, parent, currentScore)
	return currentScore

def parseAux(rawData, dict):
	for row in rawData:
		r = row.split(',')
		r[2] = (strptime(r[2], '%b').tm_mon)
		r[3] = (days[r[3]])  # replace months and days to ints
		dict.append([float(x) for x in r])

def parseData(priors, data):
	rawPriors = priors.split('\n')
	nodes = rawPriors.pop(0).split(',')
	rawData = data.split('\n')
	rawData.pop(0)
	parseAux(rawPriors, priorsDict)
	parseAux(rawData, dataDict)
	return (dataDict, priorsDict)

def changeGraph(G):
	with open(sys.argv[4], 'r') as f:
		changes = list(csv.reader(f))
	for change in changes:
		line = [c.strip() for c in change]
		firstW = line.pop(0)
		node = line.pop(0)
		if firstW == 'add':
			G.addParentsToNode(node,line)
		elif firstW == 'remove':
			G.removeParentsFromNode(node, line)
		elif firstW == 'switch':
			G.removeParentsFromNode(node, line) #only one arg
			for l in line:
				G.addParentsToNode(l, node)

def printGraphsAux(G):
	for node in G.nodes:
		print(node.name, "parents:", [n.name for n in node.parents])

	print('\nGraph Score = 10^{}'.format(float(format(getGraphScore(G), '.3f'))))

def printGraphs(G):
	print("\nBEFORE CHANGES:\n")
	printGraphsAux(G)
	changeGraph(G)
	print("\nAFTER CHANGES:\n")
	printGraphsAux(G)


if __name__ == '__main__':
	if len(sys.argv) < 5:
		print("usage: program.py priors.csv data.csv  parents.csv changes.csv")
		sys.exit()
	priors = open(sys.argv[1], "r").read()
	data = open(sys.argv[2], "r").read()
	changes = open(sys.argv[4], "r").read()
	(dataDict, priorsDict) = parseData(priors, data)
	#print("dataDict:", dataDict)
	G = Graph(nodes, dataDict, priorsDict)
	dataDict_Q = G.updateQuantizedDict(dataDict)
	priors_Q = G.updateQuantizedDict(priorsDict)
	createSimpleGraph(G)
	"""for node in G.nodes:
		print(node.name, "priors:", node.priors, "data:", node.values)"""
	printGraphs(G)
	#newScore = getGraphScore(G)
