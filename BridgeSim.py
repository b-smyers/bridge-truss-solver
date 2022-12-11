import json
import math
import numpy as np
import matplotlib.pyplot as plt

plt.grid(linestyle='--', linewidth=0.5)
plt.gca().set_aspect('equal', adjustable='box')


useMaterial = True
showCompressionTension = False
showStressColoredMemers = True #Will only work while using a material

#Material Density g/cm^3 (Gram per cubic centimeter)
#Material compressive and tensile strength MPa (Mega Pascal)
#Load Material Data
try:
    f = open('Materials/Balsa.json')
except:
    raise Exception("No material data file could be found.")
else:
    materialData = json.load(f)
    f.close()

#Load Bridge Data
try:
    f = open('Bridges/TestBridgeData2.json')
except:
    raise Exception("No bridge data file could be found.")
else:
    bridgeData = json.load(f)
    f.close()

def preRunBridgeChecker():
    print("Running Pre-run Bridge Checks...")
    numOfNodes = len(bridgeData["Nodes"])
    numOfMembers = len(bridgeData["Members"])
    numOfLoads = len(bridgeData["Loads"])
    numOfFixedNodes = 0
    numOfRollingNodes = 0

    for node in bridgeData["Nodes"]:
        if node["fixedNode?"] and node["rollingNode?"]:
            raise Exception('Nodes cannot be fixed and rolling, make sure your anchored nodes are fixed OR rolling.')
        elif node["fixedNode?"]:
            numOfFixedNodes += 1
        elif node["rollingNode?"]:
            numOfRollingNodes += 1

    #Fixed and rolling node error catching
    if numOfFixedNodes > 1:
        raise Exception('This simulation does not support more than one fixed node at a time.')
    elif numOfFixedNodes < 1:
        raise Exception('This simulation requires at least one fixed node.')
    if numOfRollingNodes > 1:
        raise Exception('This simulation does not support more than one rolling node at a time.')
    elif numOfRollingNodes < 1:
        raise Exception('This simulation requires at least one rolling node.')

    #Member error catching
    if numOfNodes*2 > numOfMembers+3:
        raise Exception(f'There are too little members, try adding {(numOfNodes*2)-(numOfMembers+3)} more.')
    elif numOfNodes*2 < numOfMembers+3:
        raise Exception(f'There are too many members, try removing {(numOfMembers+3)-(numOfNodes*2)} more.')
    
    #Load error catching
    loadNodes = []
    for load in bridgeData["Loads"]:
        loadNodes.append(load["loadNode"])
    if sorted(loadNodes) != sorted(list(set(loadNodes))):
        raise Exception('There can only be a maximum of one load per node, make sure there isn\'t more than one load per node')
    if numOfLoads <= 0:
        raise Exception('There are no loads on the bridge, try adding some.')

    #Material error catching
    if useMaterial:
        if "CrossSectionalDimensions" not in materialData:
            raise Exception("Material is missing 'CrossSectionalDimensions' attribute (unit meter)")
        if "Density" not in materialData:
            raise Exception("Material is missing 'Density' attribute (unit g/cm^3).")
        if "CompressionStrength" not in materialData:
            raise Exception("Material is missing 'CompressionStrength' attribute (unit MPa).")
        if "TensileStrength" not in materialData:
            raise Exception("Material is missing 'TensionStrength' attribute (unit MPa).")
    
def main():

    constrainedNodes = []
    #Store the constrained nodes
    for node in bridgeData["Nodes"]:
        nodeNumber = node["nodeNum"]
        if nodeInfo(nodeNumber).isFixed or nodeInfo(nodeNumber).isRolling:
            constrainedNodes.append(nodeNumber)

    trussAngleMatrix = np.zeros((len(bridgeData["Nodes"])*2, len(bridgeData["Members"])+3))
    # This matrix will be as follows
    # Nodes M01 M12 M02      Each column represents a member
    # 0 x  |___|___|___|     and each row represents a nodes
    #   y  |___|___|___|     reaction force angle to its member.
    # 1 x  |___|___|___|     Reaction force angles for nodes on oppisite
    #   y  |___|___|___|     ends of a member are equal and oppisite
    for member in bridgeData["Members"]:
        node1 = member["nodes"][0]
        node2 = member["nodes"][1]
        #get position of both nodes
        #find inverse tan of (y2-y1)/(x2-x1)
        angleToHorizontal = math.pi/2
        if nodeInfo(node2).x-nodeInfo(node1).x != 0:
            angleToHorizontal = math.atan((nodeInfo(node2).y-nodeInfo(node1).y)/
                                          (nodeInfo(node2).x-nodeInfo(node1).x))
            
        #get cos and sin of angle
        matrixAngleX = round(abs(math.cos(angleToHorizontal)),2)
        matrixAngleY = round(abs(math.sin(angleToHorizontal)),2)
        #Determine positive or negative by the direction of member
        if nodeInfo(node2).x < nodeInfo(node1).x:
            matrixAngleX = -matrixAngleX
        if nodeInfo(node2).y < nodeInfo(node1).y:
            matrixAngleY = -matrixAngleY

        #add reaction angles to matrix
        trussAngleMatrix[node1*2, member["memberNum"]] = matrixAngleX #1 to 2 cos()
        trussAngleMatrix[node1*2+1, member["memberNum"]] = matrixAngleY #1 to 2 sin()
        trussAngleMatrix[node2*2, member["memberNum"]] = -matrixAngleX #2 to 1 cos()
        trussAngleMatrix[node2*2+1, member["memberNum"]] = -matrixAngleY #2 to 1 sin()

    #Adding reaction force angles to angle matrix, all fixed reaction forces angles will be completely vertical or horizontal
    for node in constrainedNodes:
        if nodeInfo(node).isFixed:
            trussAngleMatrix[(nodeInfo(node).nodeNum)*2, trussAngleMatrix.shape[1]-1] = 1
            trussAngleMatrix[(nodeInfo(node).nodeNum)*2+1, trussAngleMatrix.shape[1]-2] = 1
        elif nodeInfo(node).isRolling:
            trussAngleMatrix[(nodeInfo(node).nodeNum)*2+1, trussAngleMatrix.shape[1]-3] = 1

    #Inverse the angle matrix (AngleMatrix^-1 * Coeffecients = Forces)
    inverseTrussAngleMatrix = np.linalg.inv(trussAngleMatrix)

    #Make empty list, add load to list, Transpose.
    coeffecientMatrix = np.zeros(len(bridgeData["Nodes"])*2)
    for load in bridgeData["Loads"]:
        coeffecientMatrix[load["loadNode"]*2+1] = load["loadForce"]

    trussForceMatrix = inverseTrussAngleMatrix.dot(coeffecientMatrix.T)

    #Plot and label nodes
    for node in bridgeData["Nodes"]:
        plotNode(node["nodeNum"])

    #Plot and label members
    for i in range(len(bridgeData["Members"])):
        plotMember(bridgeData["Members"][i], trussForceMatrix[i])

    #Plot and label loads
    for load in bridgeData["Loads"]:
        plotLoad(load)


class Node(object):
    def __init__(self, nodeNum):
        self.nodeNum = nodeNum
        self.position = bridgeData["Nodes"][nodeNum]["cords"]
        self.x = self.position[0]
        self.y = self.position[1]
        self.isFixed = bridgeData["Nodes"][nodeNum]["fixedNode?"]
        self.isRolling = bridgeData["Nodes"][nodeNum]["rollingNode?"]

def nodeInfo(nodeNum: int):
    nodeInfo = Node(nodeNum)
    return nodeInfo

def plotNode(node):
    if nodeInfo(node).isFixed or nodeInfo(node).isRolling:
        plt.plot(nodeInfo(node).x, nodeInfo(node).y, "ko")
    else:
        plt.plot(nodeInfo(node).x, nodeInfo(node).y, "bo")

    plt.annotate(node, (nodeInfo(node).x, nodeInfo(node).y), color="m")

def plotLoad(load):
    loadX = nodeInfo(load["loadNode"]).x
    loadY = nodeInfo(load["loadNode"]).y
    plt.arrow(x=loadX, y=loadY,
                dx=0,    dy=-load["loadForce"]/200,
                width=0.03, color="r")
    plt.annotate(load["loadNumber"], (loadX, (loadY-load["loadForce"]/200)/2), color="c")

def plotMember(member, force):
    tressColor = "g" #Forces between half load and zero load are green

    if useMaterial:
        #Breaking forces are in Newtons
        maxCompressionForce = ((materialData["CompressionStrength"] * 1000000) * 
                                    (materialData["CrossSectionalDimensions"][0] * materialData["CrossSectionalDimensions"][1]))
        maxTensileForce = ((materialData["TensileStrength"] * 1000000) * 
                                (materialData["CrossSectionalDimensions"][0] * materialData["CrossSectionalDimensions"][1]))

        if showStressColoredMemers:
            if force > maxTensileForce or -force > maxCompressionForce:
                tressColor = "r" #Members that will break are red
            elif (force < maxTensileForce and force > maxTensileForce*.5) or (-force < maxCompressionForce and -force > maxCompressionForce*.5):
                tressColor = "y" #Forces between breaking load and half of breaking load are yellow

    nodeXs = nodeInfo(member["nodes"][0]).x, nodeInfo(member["nodes"][1]).x
    nodeYs = nodeInfo(member["nodes"][0]).y, nodeInfo(member["nodes"][1]).y

    if showCompressionTension:
        if force < 0:
            plt.plot(nodeXs, nodeYs, color="r", lw=3) #negative forces are compressive and are colored red
        else:
            plt.plot(nodeXs, nodeYs, color="b", lw=3) #positive forces are tensile and are colored blue

    plt.plot(nodeXs, nodeYs, color=tressColor) #matplotlib wants a (x, x, ...), (y, y, ...) list for some dumb reason

    centerx, centery = sum(nodeXs)/2, sum(nodeYs)/2 #Midpoint formula
    plt.annotate(member["memberNum"], (centerx, centery), color="c")

    angle = 90
    if nodeXs[1]-nodeXs[0] != 0:
        angle = math.degrees(math.atan((nodeYs[1]-nodeYs[0])/
                            (nodeXs[1]-nodeXs[0])))

    plt.annotate(round(force, 2), (centerx, centery), rotation=angle, 
                    color="k", ha='center', va='center',
                    bbox=dict(facecolor='white', edgecolor='green', boxstyle='square'))

if __name__=="__main__":
    print("Starting...")
    preRunBridgeChecker()
    main()
    plt.show()