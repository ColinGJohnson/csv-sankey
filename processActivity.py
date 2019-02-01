import csv
import re

# define a node class for use in organizing purchase data 
class Node(object):
	def __init__(self, name, value = 0):
		self.name = name
		self.value = value
		self.children = []

	def __str__(self):
		return "Node Name: {0}, Value: {1}, Number of children: {2}".format(self.name, round(self.value, 2), len(self.children))

	# adds an element to this tree or its children
	def addNode(self, node):
		self.children.append(node)
		return

	# adds a purchase somewhere on this tree
	def addPurchase(self, path, value):

		# add the value of the purchase to this node
		self.value += value

		# check if the end of the path has been reached, if so we are done
		if(len(path) == 0):
			return

		# if the first node on the path exists as a child of this node, follow it
		for child in self.children:
			if(child.name == path[0]):
				child.addPurchase(path[1:], value)
				return

		# otherwise create the missing child node and follow it
		newNode = Node(path[0], 0)
		self.addNode(newNode)
		newNode.addPurchase(path[1:], value)
		return

	# returns a string containing this node and it's children in sankeyMatic format (http://sankeymatic.com)
	def getSankeyMatic(self):
		s = ""

		for child in self.children:
			s += self.name + " [" + str(round(child.value, 2)) + "] " + child.name + "\n"
			
			if(child.name != self.name):
				s += child.getSankeyMatic()

		return s

# open the account activity .csv file and extract data from it
purchases = []
incomeTotal = 0.0
expensesTotal = 0.0
with open('accountactivity.csv', newline='') as csvfile:
	reader = csv.reader(csvfile, delimiter=',', quotechar='|')
	for row in reader:
		if row[2] != "":
			expensesTotal += float(row[2])
			purchases.append([row[1], row[2]])
		else:
			incomeTotal += float(row[3])

# create initial nodes
origin = Node("Income", incomeTotal)
expenses = Node("Expenses", 0)
savings = Node("Savings", incomeTotal - expensesTotal)
origin.addNode(expenses)
origin.addNode(savings)

# get list of paths and patterns
patterns = []
with open('config.cfg') as configFile:
	line = configFile.readline()
	while line:

		# skip config lines that are blank or marked as comments
		line = line.strip()
		if line == "" or line[0] == "#":
			line = configFile.readline()
			continue

		# add valid lines to patterns list as ["Pattern", [path]]
		patterns.append([line.split(",")[0], line.split(",")[1].split("-")])
		line = configFile.readline()

# add nodes from purchases according to patterns
for purchase in purchases:

	# try to find a pattern that matches the current purchase
	match = False
	for pattern in patterns:
		if re.search(pattern[0], purchase[0]):
			match = True

			# skip ignored transactions
			if(pattern[-1][0] != "IGNORE"):
				origin.children[0].addPurchase(pattern[-1], float(purchase[1]))

	# warn about unfiltered purchases
	if(match == False):
		print(purchase, " did not match any given pattern.\n")

# convert node tree  to sankeymatic format
output = origin.getSankeyMatic()

# order sankeymatic string
SplitRanked = []
for item in output.split("\n"): 
	if(len(item) > 0):
		valueString = item[item.find("[")+1:item.find("]")]
		value = float(valueString) 
		SplitRanked.append([value, item])

# run inbuild python sorting algorithm
def firstElement(L):
	return L[0]
SplitRanked.sort(key=firstElement, reverse=True)

# clear output string and readd each item in order
output = "";
for item in SplitRanked:
	output += item[1] + "\n"

# write ordered sankeymatic format to output file 
with open("output.txt", "w") as outputFile:
	outputFile.write(output)