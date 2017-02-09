import sys
def insertDataIntoMap(row, dict):
	r = row.split('}')[0].split('{')
	name = r[0].split()[1]
	try:
		r[2]
	except:
		return
	domain = r[2].strip().split(',')
	dict.update({name : [i.strip() for i in domain]})


def parseData(rawData):
	dataset = rawData.split('\n')
	dataDict = {}
	for row in dataset:
		insertDataIntoMap(row, dataDict)
	print(dataDict)
	return(dataDict)