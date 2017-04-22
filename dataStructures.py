import sys,copy
from scipy import cluster
from math import floor
getn = lambda g,n: g.nodes[nodes.index(n)]
nodes = ['X','Y','month','day','FFMC','DMC','DC','ISI','temp','RH','wind','rain','area']

MAXRANGE = 7

def getCentroids(list):
	minerr = 900000 #is >> from err
	"""for k in range(2,MAXRANGE):
		#print("K is", k)
		(centroids, err) = cluster.vq.kmeans(list, k)
		#print(k,sorted([int(x) for x in centroids]), err)
		if err < minerr:
			minerr = err"""
	(centroids, err) = cluster.vq.kmeans(list, 12)
	print(sorted([floor(float(format(x,'.2f'))) for x in centroids]))
	return sorted([floor(float(format(x,'.2f'))) for x in centroids])

class Graph:
	nodes = []
	def __init__(self, nodes, dataDict, priorsDict):
		for name in nodes:
			#print(name)
			self.nodes.append(Node(name))
		self.updatePriors(self, priorsDict)
		"""for node in self.nodes:
			print("INIT:", node.name, "priors:", node.priors, "data:", node.values)"""
		self.updateQuantizedValues(self, dataDict)

	def __deepcopy__(self, memo):
		cls = self.__class__
		result = cls.__new__(cls)
		result.nodes = []
		memo[id(self)] = result
		for node in self.nodes:
			result.nodes.append(copy.deepcopy(node))
		return result

	def checkCircle(self): #simple DFS
		visited = set()
		path = []
		path_set = set(path)
		stack = [iter(self.nodes)]
		while stack:
			#print("visited:", [n.name for n in visited], ",path:", [n.name for n in path], ",stack:", stack)
			for v in stack[-1]:
				#print("v:", v.name)
				if v in path_set:
					return True
				elif v not in visited:
					visited.add(v)
					path.append(v)
					path_set.add(v)
					stack.append(iter(v.parents))
					break
			else:
				if len(path)==0:
					return False
				path_set.remove(path.pop())
				stack.pop()
		return False


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
	def updatePriors(self, dataDict):
		for node in self.nodes:
			#print(node.name)
			nodePriors = [x[nodes.index(node.name)] for x in dataDict]
			centroids = getCentroids(nodePriors)
			if(node.name == "rain"):
				centroids = (0.01, 3.9)
			elif(node.name == 'area'):
				centroids = (0.00, 4.0)
			node.centroids = centroids
			closestCentroidToVal = [min(centroids, key=lambda x: abs(x - v)) for v in nodePriors]
			node.priors = [(c, closestCentroidToVal.count(c), float(format(closestCentroidToVal.count(c) / len(nodePriors), '.3f'))) for c in centroids]
			if len(node.priors) < 2:
				print("Not enough values for node", node.name, "exiting...");
				sys.exit()

	def addParentsToNode(self, nodeName, parents):
		node = getn(self, nodeName)
		if type(parents) == str:
			node.addParents([getn(self, parents)])
			if self.checkCircle() == True:
				#print("\nCircle inserted into graph after", parents, "was inserted!!!\n")
				self.removeParentsFromNode(nodeName, [parents])
		else:
			parentNames = [getn(self,p) for p in parents]
			node.addParents(parentNames)
			if self.checkCircle() == True:
				#print("Circle inserted into graph after", parents, "was inserted!!!\n")
				self.removeParentsFromNode(nodeName, parents)

	@staticmethod
	def updateQuantizedValues(self, dataDict):
		for node in self.nodes:
			#print(node.name)
			nodeValues = [x[nodes.index(node.name)] for x in dataDict]
			closestCentroidToVal = [min(node.centroids, key=lambda x: abs(x - v)) for v in nodeValues]
			node.values = [(c, closestCentroidToVal.count(c), float(format(closestCentroidToVal.count(c) / len(nodeValues), '.3f'))) for c in node.centroids]
			#print("updateQuantizedValues:", node.name, "priors:", node.priors, "data:", node.values)

	def removeParentsFromNode(self, nodeName, p):
		for i in p:
			#print("in removeParentsFromNode. node: ,i:", nodeName, i)
			getn(self, nodeName).removeParent(getn(self, i))
		#print([p.name for p in getn(self, nodeName).parents])

class Node:
	name = ''
	parents = []
	values = []
	priors = []
	centroids = []

	def __init__(self, name):
		self.name = name
		self.parents = set([])
		self.values = []
		self.priors = []
		self.centroids = []

	def __deepcopy__(self, memo):
		cls = self.__class__
		result = cls.__new__(cls)
		memo[id(self)] = result
		for k, v in self.__dict__.items():
			setattr(result, k, copy.deepcopy(v, memo))
		return result

	def addParents(self, n):
		#print(self.name)
		#print("parents to add:",  [p.name for p in n])
		for a in n:
			self.parents.add(a)

	def removeParent(self, p):
		#print("remove from", self.name, "parent:", p.name, "current parents are:", [x.name for x in self.parents], "\n")
		self.parents.remove(p)

	"""def updatePriors(self, prio):
		centroids = [v[0] for v in self.values]
		closestCentroidToVal = [min(centroids, key=lambda x: abs(x - v)) for v in prio]
		#print(self.name, closestCentroidToVal)
		self.prior = [(c, closestCentroidToVal.count(c), float(format(closestCentroidToVal.count(c) / len(prio), '.3f'))) for c in centroids]"""