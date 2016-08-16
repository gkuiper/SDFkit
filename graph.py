#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Widget to display simulation data of a CSDF graph.

author: Sander Giesselink

"""

import sys
from PyQt5.QtCore import QPoint, QRectF
from node import*
from edge import*
from tokenCluster import*

class Graph():

    def __init__(self, scene, view):
        super().__init__()

        self.scene = scene
        testScene = 1
      
        self.edgeList = []
        self.nodeList = []

        #Add edges with: (QGraphicsScene(), x1, y1, x2, y2)
        #self.addEdge(scene, 0, 0, 100, 100)

        #Add edges between nodes with: (QGraphicsScene(), outputNode, inputNode)
        # self.addEdgeToNodes(scene, 0, 1)

        # Add nodes with: (QGraphicsScene(), xpos, ypos, nodeName)
        # self.addNode(scene, 0, 0, 'Node name')
        
        #---Simple test scene---
        if testScene == 1:
            self.addNode(scene, 0, 0, '1')
            self.addNode(scene, 150, 0, 'n2')
            self.addNode(scene, 300, 200, 'node 3')
            self.addNode(scene, -100, 200, 'Node 4 <-')
            self.addNode(scene, -150, 100, 'Node 5 name')
            self.addNode(scene, -300, 0, 'Node 6 name here')
            self.addNode(scene, -150, -100, 'Node 7 name here')
            self.addNode(scene, 200, -150, 'Node 8 name here')
            self.addNode(scene, 650, -50, 'n9')
            self.addNode(scene, 350, 100, 'node 10')
            self.addNode(scene, 300, 350, 'node 11')
            self.addNode(scene, -300, 200, 'Node 12')
            
            self.addEdgeToNodes(scene, 0, 1, 'right', 'left')
            self.addEdgeToNodes(scene, 6, 6, 'left', 'right')
            self.addEdgeToNodes(scene, 11, 3, 'right', 'right')
            self.addEdgeToNodes(scene, 7, 7, 'right', 'left')
            self.addEdgeToNodes(scene, 7, 7, 'right', 'left')
            self.addEdgeToNodes(scene, 7, 7, 'right', 'left')
            self.addEdgeToNodes(scene, 1, 7, 'right', 'left')
            self.addEdgeToNodes(scene, 1, 8, 'right', 'left')
            self.addEdgeToNodes(scene, 1, 2, 'right', 'left')
            self.addEdgeToNodes(scene, 5, 6, 'right', 'left')
            self.addEdgeToNodes(scene, 6, 0, 'right', 'left')
            self.addEdgeToNodes(scene, 5, 4, 'right', 'left')
            self.addEdgeToNodes(scene, 4, 3, 'right', 'left')
            self.addEdgeToNodes(scene, 3, 1, 'right', 'left')
            self.addEdgeToNodes(scene, 3, 1, 'right', 'left')
            self.addEdgeToNodes(scene, 1, 3, 'left', 'right')
            self.addEdgeToNodes(scene, 3, 1, 'right', 'left')
            self.addEdgeToNodes(scene, 5, 5, 'right', 'left')
            self.addEdgeToNodes(scene, 9, 2, 'left', 'right')
            self.addEdgeToNodes(scene, 2, 10, 'right', 'right')
            self.addEdgeToNodes(scene, 2, 10, 'left', 'left')
            self.addEdgeToNodes(scene, 3, 11, 'left', 'left')




        #---Grid test scene---
        if testScene == 2:
            gridSize = 25
            for i in range(gridSize):
                for j in range(gridSize):
                    name = str(i) + '/' + str(j)
                    #print(name)
                    self.addNode(scene, j*150, i*100, name)

            for i in range(gridSize*gridSize - 1):
                self.addEdgeToNodes(scene, i, i + 1, 'right', 'left')

        #---Simple test scene---
        if testScene == 3:
            self.addNode(scene, 0, 0, 'n1')
            self.addNode(scene, 200, 100, 'n2')
            self.addNode(scene, 200, 300, 'n3')
            self.addNode(scene, -200, 300, 'n4')
            self.addNode(scene, -200, 100, 'n5')

            self.addEdgeToNodes(scene, 0, 1, 'right', 'left')
            self.addEdgeToNodes(scene, 2, 2, 'right', 'left')
            self.addEdgeToNodes(scene, 1, 2, 'right', 'right')
            self.addEdgeToNodes(scene, 2, 3, 'left', 'right')
            self.addEdgeToNodes(scene, 3, 4, 'left', 'left')
            self.addEdgeToNodes(scene, 4, 0, 'right', 'left')

            

    # def paint(self, painter, option, widget):
    #     print('test')
    #     self.scene.drawBackground(painter, QRectF(0, 0, self.getWidth(), self.getHeigth()))

    # def drawBackground(self, painter, rect):
    #     print('test')

    #     super().drawBackground(painter, rect)
    #     self.update()


    def addNode(self, scene, x, y, name):
        newNode = Node(name)
        newNode.setPos(x, y)
        newNode.setZValue(0)
        
        #Add node to the scene and list
        scene.addItem(newNode)
        self.nodeList.append(newNode)


    def addEdge(self, scene, beginPoint, endPoint, beginSide, endSide, edgeSelfLoops):        

        newEdge = Edge(beginPoint, endPoint, beginSide, endSide, edgeSelfLoops)

        #Place edges always behind nodes
        newEdge.setZValue(1)

        #Give edge a cluster of tokens
        tokenCluster = TokenCluster(scene, newEdge, newEdge.getPointOnEdge(0.5))
        
        #Add edge to the scene and list
        scene.addItem(newEdge)
        self.edgeList.append(newEdge)

        return newEdge


    def addEdgeToNodes(self, scene, beginNodeIndex, endNodeIndex, beginSide, endSide):
        beginNode = self.nodeList[beginNodeIndex]
        endNode = self.nodeList[endNodeIndex]

        edgeSelfLoops = False
        if beginNode == endNode:
            edgeSelfLoops = True


        #Get points on the nodes that the edge can connect to
        beginPoint = beginNode.getIOPointForEdge(beginSide, 2)
        endPoint = endNode.getIOPointForEdge(endSide, 1)

        #Set the beginNode as an output
        beginNode.setIOType(beginSide, 2)
        #Set the endNode as an input
        endNode.setIOType(endSide, 1)

        #Add new IO ports to nodes for future edges
        beginNode.addNewIO(beginSide, 0)
        endNode.addNewIO(endSide, 0)
        
        #Create edge between the 2 nodes
        edge = self.addEdge(scene, beginPoint, endPoint, beginSide, endSide, edgeSelfLoops)

        #Give both nodes a reference to the created edge
        beginNode.addEdge(edge, 'begin')
        endNode.addEdge(edge, 'end')