#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Widget to display simulation data of a CSDF graph.

author: Sander Giesselink

"""

import sys
from PyQt5.QtWidgets import QWidget, QGraphicsItem
from PyQt5.QtCore import QPoint, QRectF, QEvent
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush, QPainterPath

class Edge(QGraphicsItem):

    def __init__(self, scene, startPoint, endPoint):
        super().__init__()

        self.scene = scene
        self.startPoint = startPoint
        self.endPoint = endPoint
        self.midPoint = self.calculateMidPoint(startPoint, endPoint)
        # print('startPoint: ' + str(self.startPoint))
        # print('midPoint: ' + str(self.midPoint))
        # print('endPoint: ' + str(self.endPoint))

        self.edgeColor = QColor(200, 200, 200)
        self.edgeColorSelected = QColor(120, 120, 120)
        self.edgeColorHover = QColor(160, 160, 160)

        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        self.setAcceptHoverEvents(True)
        self.hover = False


    def boundingRect(self):
        #Used for collision detection
        rect = QRectF(self.startPoint, self.endPoint)
        rect = rect.normalized()

        return rect

    
    def shape(self):
        #Determines the paint area
        path = QPainterPath()

        rect = QRectF(self.startPoint, self.endPoint)
        rect = rect.normalized()

        path.addRect(rect)

        return path


    def paint(self, painter, option, widget):
        pen = QPen(self.edgeColor)
        pen.setWidth(3)

        if self.hover:
        	pen.setColor(self.edgeColorHover)

        if QGraphicsItem.isSelected(self):
        	pen.setColor(self.edgeColorSelected)

        painter.setPen(pen)

        painter.drawLine(self.startPoint, self.midPoint)
        painter.drawLine(self.midPoint, self.endPoint)


    def calculateMidPoint(self, startPoint, endPoint):
        x = (startPoint.x() + endPoint.x()) / 2
        y = (startPoint.y() + endPoint.y()) / 2
        return QPoint(x, y)


    def hoverEnterEvent(self, event):
        self.hover = True

        super().hoverEnterEvent(event)
        self.update()


    def hoverLeaveEvent(self, event):
        self.hover = False

        super().hoverLeaveEvent(event)
        self.update()


    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.update()
