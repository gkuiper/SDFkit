#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Widget to display simulation data of a CSDF graph.

author: Sander Giesselink

"""

import sys
from PyQt5.QtWidgets import QWidget, QGraphicsItem, QPushButton, QVBoxLayout
from PyQt5.QtCore import QRectF, QPointF, QPoint
from PyQt5.QtGui import QColor, QPainter, QBrush, QPainterPath

from testButton import testClass

class Node(QGraphicsItem):

    def __init__(self, nodeName):
        super().__init__()
        
        self.ioWidth = 15
        self.ioHeight = 10
        self.ioHeightDifference = 10
        self.nodeBodyWidth = 100
        self.nodeBodyColor = QColor(200, 200, 200)
        self.nodeBodyColorSelected = QColor(150, 150, 150)
        self.nodeInputColor = QColor(240, 240, 240)
        self.nodeInputColorSelected = QColor(220, 220, 220)
        self.nodeOutputColor = QColor(120, 120, 120)
        self.nodeOutputColorSelected = QColor(100, 100, 100)


        self.nodeText = nodeName

        self.inputList = []
        self.addNewInput()
        #self.addNewInput()

        self.outputList = []
        self.addNewOutput()
        #self.addNewOutput()
        #self.addNewOutput()

        #print(self.inputList)
        #print(self.outputList)

        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        print('node succesfully created: "' + nodeName + '"')



    def boundingRect(self):
        return QRectF(0, 0, self.nodeBodyWidth, self.getNodeBodyHeight())

    
    def shape(self):
    	path = QPainterPath()
    	path.addRect(0, 0, self.nodeBodyWidth, self.getNodeBodyHeight())

    	return path

    
    def paint(self, painter, option, widget):
        self.paintNodeBody(painter)
        self.paintNodeInputs(painter)
        self.paintNodeOutputs(painter)
        self.paintNodeName(painter)


    def paintNodeBody(self, painter):
        color = QColor(0, 0, 0)
        painter.setPen(color)
      
        brush = QBrush(self.nodeBodyColor)
        if QGraphicsItem.isSelected(self):
            brush = QBrush(self.nodeBodyColorSelected)

        painter.setBrush(brush)
        painter.drawRoundedRect(0, 0, self.nodeBodyWidth, self.getNodeBodyHeight(), 10, 10)


    def paintNodeInputs(self, painter):
        color = QColor(0, 0, 0)
        painter.setPen(color)

        #Draw all inputs
        for i in range(0, len(self.inputList)):
            if self.inputList[i][3]:
                brush = QBrush(self.nodeInputColorSelected)  
            else:
                brush = QBrush(self.nodeInputColor) 

            painter.setBrush(brush)
            painter.drawRoundedRect(self.inputList[i][0], self.inputList[i][1], self.ioWidth, 10, 2, 2)
         
         
    def paintNodeOutputs(self, painter):
        color = QColor(0, 0, 0)
        painter.setPen(color)

        #Draw all inputs
        for i in range(0, len(self.outputList)):
            if self.outputList[i][3]:
                brush = QBrush(self.nodeOutputColorSelected)  
            else:
                brush = QBrush(self.nodeOutputColor) 

            painter.setBrush(brush)
            painter.drawRoundedRect(self.outputList[i][0], self.outputList[i][1], self.ioWidth, 10, 2, 2)
      
      
    def paintNodeName(self, painter):
        nodeTextDisplayed = self.nodeText

        maxLength = 10

        if len(self.nodeText) > maxLength:
        	#Cutoff text if the name is too long
            nodeTextDisplayed = self.nodeText[:maxLength]
            nodeTextDisplayed += '..'
            textPoint = QPoint(self.ioWidth + 2, self.ioHeight + 2)
        else:
        	#Calculate xTranslation to center text in node
            xTranslation = ((self.nodeBodyWidth - 2 * self.ioWidth - 2 * 2) / (maxLength * 2 + 2)) * (maxLength - len(self.nodeText))
            textPointX = self.ioWidth + 2 + xTranslation
            textPoint = QPoint(textPointX, self.ioHeight + 2)


        
        painter.drawText(textPoint, nodeTextDisplayed)    



    def mousePressEvent(self, event):
        self.mouseIsOnInput(event.pos())
        self.mouseIsOnOutput(event.pos())

        super().mousePressEvent(event)
        self.update()



    def mouseMoveEvent(self, event):
        #Code for ShiftModifier goes here

        self.update()
        super().mouseMoveEvent(event)


    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.update()


    def getInputPoint(self, inputIndex):
        inputPoint = QPointF(0, inputIndex * (self.ioHeightDifference + self.ioHeight) + self.ioHeight)

        #Returns the point of a specific input
        return inputPoint


    def getOutputPoint(self, outputIndex):
        outputPoint = QPointF(self.nodeBodyWidth - self.ioWidth, outputIndex * (self.ioHeightDifference + self.ioHeight) + self.ioHeight)

        #Returns the point of a specific output
        return outputPoint


    def addNewInput(self):
        i = len(self.inputList)

        #---newInput = (inputPoint.x, inputPoint.y, hasEdge, mouseHover)---
        newInput = (self.getInputPoint(i).x(), self.getInputPoint(i).y(), False, False)
        self.inputList.append(newInput)


    def addNewOutput(self):
        i = len(self.outputList)

        #---newOutput = (outputPoint.x, outputPoint.y, hasEdge, mouseHover)---
        newOutput = (self.getOutputPoint(i).x(), self.getOutputPoint(i).y(), False, False)
        self.outputList.append(newOutput)


    def getNodeBodyHeight(self):
        longestList = len(self.inputList)
        if len(self.outputList) > len(self.inputList):
            longestList = len(self.outputList)

        return (longestList * (self.ioHeightDifference + self.ioHeight) + self.ioHeight)


    def mouseIsOnInput(self, mousePos):
        for i in range(0, len(self.inputList)):
            inputPoint = QPointF(self.inputList[i][0], self.inputList[i][1])

            #If mouse is over input -> set mouseHover to true
            if mousePos.x() > inputPoint.x() and mousePos.x() < inputPoint.x() + self.ioWidth:
                if mousePos.y() > inputPoint.y() and mousePos.y() < inputPoint.y() + self.ioHeight:
                    print('mouse on input: ' + str(i))
                    self.setFlag(QGraphicsItem.ItemIsSelectable, False)
                    self.setFlag(QGraphicsItem.ItemIsMovable, False)
                    return i

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)


    def mouseIsOnOutput(self, mousePos):
        for i in range(0, len(self.outputList)):
            outputPoint = QPointF(self.outputList[i][0], self.outputList[i][1])

            #If mouse is over output -> set mouseHover to true
            if mousePos.x() > outputPoint.x() and mousePos.x() < outputPoint.x() + self.ioWidth:
                if mousePos.y() > outputPoint.y() and mousePos.y() < outputPoint.y() + self.ioHeight:
                    print('mouse on output: ' + str(i))
                    self.setFlag(QGraphicsItem.ItemIsSelectable, False)
                    self.setFlag(QGraphicsItem.ItemIsMovable, False)
                    return i
        
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
