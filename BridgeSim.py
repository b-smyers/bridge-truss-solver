import json
import math
import matplotlib.pyplot as plt

plt.grid(linestyle='--', linewidth=0.5)
plt.gca().set_aspect('equal', adjustable='box')


def main():
    print("Starting...")

    #Load Bridge Data
    try:
        f = open('Bridge.json')
    except:
        print("No bridge data file could be found.")
        exit
    else:
        data = json.load(f)
        f.close()

    class Vertex(object):
        def __init__(self, vertNum):
            self.vertex = vertNum
            self.position = data["Vertices"][vertNum-1]["cords"]
            self.x = self.position[0]
            self.y = self.position[1]
            self.adjEdges = data["Vertices"][vertNum-1]["adjEdges"]
            self.isFixed = data["Vertices"][vertNum-1]["fixed"]

    def vertInfo(vertNum: int):
        vertInfo = Vertex(vertNum)
        return vertInfo

    fixedPoints = []
    #plot verts
    for vert in range(1, len(data["Vertices"])+1):
        if vertInfo(vert).isFixed:
            plt.plot(vertInfo(vert).x, vertInfo(vert).y, "ko")
            fixedPoints.append(vert)
        else:
            plt.plot(vertInfo(vert).x, vertInfo(vert).y, "bo")

        plt.annotate(vert, (vertInfo(vert).x, vertInfo(vert).y), color="m")

    #plot edges
    for edge in data["Edges"]:
        vertXs = vertInfo(edge["vertices"][0]).x, vertInfo(edge["vertices"][1]).x
        vertYs = vertInfo(edge["vertices"][0]).y, vertInfo(edge["vertices"][1]).y
        plt.plot(vertXs, vertYs, "g") #matplotlib wants a (x, x, ...), (y, y, ...) list for some dumb reason

        centerx, centery = sum(vertXs)/2, sum(vertYs)/2 #Midpoint formula
        plt.annotate(edge["edge"], (centerx, centery), color="c")

    #Add and label loads
    for load in data["Loads"]:
        loadX = vertInfo(load["loadVertex"]).x
        loadY = vertInfo(load["loadVertex"]).y
        plt.arrow(x=loadX, y=loadY+(load["loadForce"]/100),
                  dx=0,    dy=-(load["loadForce"]/100)+.1,
                  width=0.03, color="r")

    #Get fixed points and find distance between them
    dist = vertInfo(fixedPoints[1]).x - vertInfo(fixedPoints[0]).x
    #Get the reaction force of the 2nd fixed point
    forceOfLoads = 0
    sumOfLoads = 0
    for load in data["Loads"]:
        forceOfLoads += load["loadForce"] * vertInfo(load["loadVertex"]).x
        sumOfLoads += load["loadForce"]
    reactionForceTwo = forceOfLoads / dist
    #Subsequently calculate the 1st reaction force
    reactionForceOne = sumOfLoads - reactionForceTwo

    print(reactionForceOne, reactionForceTwo)
    

    #For each load
    for load in data["Loads"]:
        #Find vertex and force
        loadVertex = load["loadVertex"]
        Force = load["loadForce"]
        #Find all edges connected to vertex
        adjacentEdges = vertInfo(loadVertex).adjEdges
        #For each edge find the start and end points
        for edge in adjacentEdges:
            start = vertInfo(data["Edges"][edge-1]["vertices"][0]).position
            end = vertInfo(data["Edges"][edge-1]["vertices"][1]).position
            b = start[0] - end[0] # delta X
            a = start[1] - end[1] # delta Y
            c = math.sqrt(pow(b,2)+pow(a,2)) #PYTHAGORAS BABY!

            #Find all angles of edges to the horizontal
            radToHorizontal = math.acos((pow(b,2)+pow(c,2)-pow(a,2)) / abs(2*b*c))
            degreesToHorizontal = math.degrees(radToHorizontal)

            #Calculate the forces on each adjacent edge
            
            forceOnEdge = Force*math.sin(radToHorizontal)
        #Store forces on each edge
        
    

if __name__=="__main__":
    main()
    plt.show()