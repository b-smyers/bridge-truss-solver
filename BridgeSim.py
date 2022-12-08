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
        pass
        #plotMember(member)

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
        matrixAngleX = math.cos(angleToHorizontal)
        matrixAngleY = math.sin(angleToHorizontal)
        #add to angles matrix
        trussAngleMatrix[(node1-1)*2, member["memberNum"]-1] = matrixAngleX #1 to 2 cos()
        trussAngleMatrix[(node1-1)*2+1, member["memberNum"]-1] = matrixAngleY #1 to 2 sin()
        trussAngleMatrix[(node2-1)*2, member["memberNum"]-1] = -matrixAngleX #2 to 1 cos()
        trussAngleMatrix[(node2-1)*2+1, member["memberNum"]-1] = -matrixAngleY #2 to 1 sin()

    #Adding reaction force angles to angle matrix, all reaction force angles will be completely vertical or horizontal
    ##The last three columns for the matrix will always be ordered {Reaction2y, Reaction1x, Reaction1y}
    for node in constrainedNodes:
        if nodeInfo(node).isFixed:
            trussAngleMatrix[(nodeInfo(node).nodeNum-1)*2, trussAngleMatrix.shape[1]-1] = 1
            trussAngleMatrix[(nodeInfo(node).nodeNum-1)*2+1, trussAngleMatrix.shape[1]-2] = 1
        elif nodeInfo(node).isRolling:
            trussAngleMatrix[(nodeInfo(node).nodeNum-1)*2+1, trussAngleMatrix.shape[1]-3] = 1
    print(trussAngleMatrix)

    inverseTrussAngleMatrix = np.linalg.inv(trussAngleMatrix)

    print(inverseTrussAngleMatrix) ## I Suspect their is an issue with these values

    coeffecientMatrix = np.zeros(len(data["Nodes"])*2)
    for load in data["Loads"]:
        coeffecientMatrix[(load["loadNode"]-1)*2+1] = load["loadForce"]

    trussForceMatrix = inverseTrussAngleMatrix.dot(coeffecientMatrix.T)

    print(trussForceMatrix)
    plotTrussForces(trussForceMatrix)

class Node(object):
    def __init__(self, nodeNum):
        self.nodeNum = nodeNum
        self.position = data["Nodes"][nodeNum-1]["cords"]
        self.x = self.position[0]
        self.y = self.position[1]
        self.adjMembers = data["Nodes"][nodeNum-1]["adjMembers"]
        self.isFixed = data["Nodes"][nodeNum-1]["fixedNode?"]
        self.isRolling = data["Nodes"][nodeNum-1]["rollingNode?"]

def nodeInfo(nodeNum: int):
    nodeInfo = Node(nodeNum)
    return nodeInfo

constrainedNodes = []

def plotNode(node):
    if nodeInfo(node).isFixed or nodeInfo(node).isRolling:
        plt.plot(nodeInfo(node).x, nodeInfo(node).y, "ko")
        constrainedNodes.append(node)
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
    loadX = nodeInfo(load["loadNode"]).x
    loadY = nodeInfo(load["loadNode"]).y
    plt.arrow(x=loadX, y=loadY,
                dx=0,    dy=-load["loadNode"]/25,
                width=0.03, color="r")
    plt.annotate(load["loadNumber"], (loadX, (loadY+load["loadNode"]/25)/2), color="c")

def plotTrussForces(forces):
    i = 0
    for member in data["Members"]:
        nodeXs = nodeInfo(member["nodes"][0]).x, nodeInfo(member["nodes"][1]).x
        nodeYs = nodeInfo(member["nodes"][0]).y, nodeInfo(member["nodes"][1]).y
        plt.plot(nodeXs, nodeYs, "g") #matplotlib wants a (x, x, ...), (y, y, ...) list for some dumb reason

        centerx, centery = sum(nodeXs)/2, sum(nodeYs)/2 #Midpoint formula
        plt.annotate(round(forces[i], 2), (centerx, centery), color="k")
        i += 1

if __name__=="__main__":
    print("Starting...")
    main()
    plt.show()