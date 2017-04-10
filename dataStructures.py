import sys, math, calendar
from time import strptime
from scipy import cluster
getn = lambda g,n: g.nodes[nodes.index(n)]
nodes = ['X','Y','month','day','FFMC','DMC','DC','ISI','temp','RH','wind','rain','area']

MAXRANGE = 7

def getCentroids(list):
	minerr = 900000 #is >> from err
	for k in range(2,MAXRANGE):
		#print("K is", k)
		(centroids, err) = cluster.vq.kmeans(list, k)
		#print(k,sorted([int(x) for x in centroids]), err)
		if err < minerr:
			minerr = err
	return sorted([float(format(x,'.2f')) for x in centroids])

class Graph:
	nodes = []

	def __init__(self, nodes, dataDict, priorsDict):
		for name in nodes:
			#print(name)
			self.nodes.append(Node(name))
		self.updateQuantizedValues(self, dataDict)
		self.updatePriors(priorsDict)


	def updateQuantizedDict(self, dataDict, dataDict_Q=[]):
		dataDict_Q = dataDict
		for node in self.nodes:
			nodeValues = [x[nodes.index(node.name)] for x in dataDict_Q]
			closestCentroidToVal = [min(node.centroids, key=lambda x: abs(x - v)) for v in nodeValues]
			#print(node.name, closestCentroidToVal)
			for i in range(0, len(dataDict)):
				dataDict_Q[i][nodes.index(node.name)] = closestCentroidToVal[i]
		return dataDict_Q

	@staticmethod
	def updateQuantizedValues(self, dataDict):
		for node in self.nodes:
			#print(node.name)
			nodeValues = [x[nodes.index(node.name)] for x in dataDict]
			centroids = getCentroids(nodeValues)
			if(node.name == "rain"):
				centroids = (0.01, 3.9)
			node.centroids = centroids
			closestCentroidToVal = [min(centroids, key=lambda x: abs(x - v)) for v in nodeValues]
			node.values = [(c, closestCentroidToVal.count(c), float(format(closestCentroidToVal.count(c) / len(nodeValues), '.3f'))) for c in centroids]
			if len(node.values) < 2:
				print("Not enough values for node", node.name, "exiting...");
				sys.exit()

	def addParentsToNode(self, nodeName, parents):
		if type(parents) == str:
			getn(self, nodeName).addParents([getn(self, parents)])
		else:
			getn(self,nodeName).addParents([getn(self,p) for p in parents])

	def updatePriors(self, priorsDict):
		for node in self.nodes:
			#print(node.name)
			nodePriors = [x[nodes.index(node.name)] for x in priorsDict]
			closestCentroidToVal = [min(node.centroids, key=lambda x: abs(x - v)) for v in nodePriors]
			node.prior = [(c, closestCentroidToVal.count(c), float(format(closestCentroidToVal.count(c) / len(nodePriors), '.3f'))) for c in node.centroids]

	def removeParentsFromNode(self, nodeName, p):
		for i in p:
			getn(self, nodeName).removeParent(getn(self, i))
		#print([p.name for p in getn(self, nodeName).parents])

class Node:
	name = ''
	parents = {}
	values = []
	prior = []
	centroids = []

	def __init__(self, name):
		self.name = name
		self.parents = set([])
		self.values = []
		self.prior = []
		self.centroids = []

	def addParents(self, n):
		#print(self.name)
		#print("parents to add:",  [p.name for p in n])
		for a in n:
			self.parents.add(a)

	def removeParent(self, p):
		#print("remove from", self.name, "parent:", p.name)
		self.parents.remove(p)

	"""def updatePriors(self, prio):
		centroids = [v[0] for v in self.values]
		closestCentroidToVal = [min(centroids, key=lambda x: abs(x - v)) for v in prio]
		#print(self.name, closestCentroidToVal)
		self.prior = [(c, closestCentroidToVal.count(c), float(format(closestCentroidToVal.count(c) / len(prio), '.3f'))) for c in centroids]"""