import json
import math
import numpy as np
import matplotlib.pyplot as plt

plt.grid(linestyle='--', linewidth=0.5)
plt.gca().set_aspect('equal', adjustable='box')

#Load Bridge Data
try:
    f = open('TestBridgeData.json')
except:
    print("No bridge data file could be found.")
    exit
else:
    data = json.load(f)
    f.close()

def main():

    #plot nodes
    for node in range(1, len(data["Nodes"])+1):
        plotNode(node)

    #plot members
    for member in data["Members"]:
        plotMember(member)

    #Add and label loads
    for load in data["Loads"]:
        plotLoad(load)
    
    trussAngleMatrix = np.zeros((len(data["Nodes"])*2, len(data["Members"])+3))
    for member in data["Members"]:
        node1 = member["nodes"][0]
        node2 = member["nodes"][1]
        #get position of both nodes
        #find inverse tan of (y2-y1)/(x2-x1)
        angleToHorizontal = math.atan((nodeInfo(node2).y-nodeInfo(node1).y)/
                          (nodeInfo(node2).x-nodeInfo(node1).x))
        #get cos and sin of angle
        matrixAngleX =  math.cos(angleToHorizontal)
        matrixAngleY =  math.sin(angleToHorizontal)
        #add to angles matrix
        trussAngleMatrix[member["memberNum"]-1, member["memberNum"]-1]

    print(trussAngleMatrix)

class Node(object):
    def __init__(self, nodeNum):
        self.nodeex = nodeNum
        self.position = data["Nodes"][nodeNum-1]["cords"]
        self.x = self.position[0]
        self.y = self.position[1]
        self.adjMembers = data["Nodes"][nodeNum-1]["adjMembers"]
        self.isFixed = data["Nodes"][nodeNum-1]["fixed"]

def nodeInfo(nodeNum: int):
    nodeInfo = Node(nodeNum)
    return nodeInfo

fixedPoints = []

def plotNode(node):
    if nodeInfo(node).isFixed:
        plt.plot(nodeInfo(node).x, nodeInfo(node).y, "ko")
        fixedPoints.append(node)
    else:
        plt.plot(nodeInfo(node).x, nodeInfo(node).y, "bo")

        plt.annotate(node, (nodeInfo(node).x, nodeInfo(node).y), color="m")

def plotMember(member):
    nodeXs = nodeInfo(member["nodes"][0]).x, nodeInfo(member["nodes"][1]).x
    nodeYs = nodeInfo(member["nodes"][0]).y, nodeInfo(member["nodes"][1]).y
    plt.plot(nodeXs, nodeYs, "g") #matplotlib wants a (x, x, ...), (y, y, ...) list for some dumb reason

    centerx, centery = sum(nodeXs)/2, sum(nodeYs)/2 #Midpoint formula
    plt.annotate(member["memberNum"], (centerx, centery), color="c")

def plotLoad(load):
    loadX = nodeInfo(load["loadVertex"]).x
    loadY = nodeInfo(load["loadVertex"]).y
    plt.arrow(x=loadX, y=loadY,
                dx=0,    dy=-load["loadForce"]/50,
                width=0.03, color="r")
    plt.annotate(load["loadNumber"], (loadX, (loadY+load["loadForce"]/50)/2), color="c")

if __name__=="__main__":
    print("Starting...")
    main()
    plt.show()