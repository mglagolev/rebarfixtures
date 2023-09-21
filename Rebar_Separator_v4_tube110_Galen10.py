#!/usr/bin/env python3


import FreeCAD as App, FreeCADGui as Gui, Draft
from FreeCAD import Base, Part, Vector
import math
from math import sin, cos, asin, acos, atan, pi
from pivy import coin
import sys

myDocument = App.newDocument("Separator")
App.setActiveDocument("Separator")
App.ActiveDocument = App.getDocument("Separator")
Gui.ActiveDocument = Gui.getDocument("Separator")

def makeCylinder(radius, height, translate = App.Vector(0,0,0), rotate = App.Rotation(0, 0, 0), name = ""):
    """ Replacement for the old Part API function """
    doc = App.activeDocument()
    cylinder = doc.addObject("Part::Cylinder", name)
    cylinder.Radius = radius
    cylinder.Height = height
    cylinder.Placement = App.Placement(translate, rotate)
    doc.recompute()
    return cylinder
    
def makeCone(radius1, radius2, height, translate = App.Vector(0,0,0), rotate = App.Rotation(0,0,0)):
    doc = App.activeDocument()
    cone = doc.addObject("Part::Cone", "Name")
    cone.Radius1 = radius1
    cone.Radius2 = radius2
    cone.Height = height
    cone.Angle = 360
    cone.Placement = App.Placement(translate, rotate)
    doc.recompute()
    return cone

def cut(obj1, obj2):
    """ Simplification of the cut function """
    result = App.activeDocument().addObject("Part::Cut", "Name")
    App.ActiveDocument.ActiveObject.Base=obj1
    App.ActiveDocument.ActiveObject.Tool=obj2
    App.ActiveDocument.recompute()
    return result
    
def fuse(obj1, obj2):
    """ Simplification of the fuse function """
    result = App.activeDocument().addObject("Part::Fuse", "Name")
    App.ActiveDocument.ActiveObject.Base=obj1
    App.ActiveDocument.ActiveObject.Tool=obj2
    App.ActiveDocument.recompute()
    return result

def common(obj1, obj2):
    """ Simplification of the common function """
    result = App.activeDocument().addObject("Part::Common", "Name")
    App.ActiveDocument.ActiveObject.Base=obj1
    App.ActiveDocument.ActiveObject.Tool=obj2
    App.ActiveDocument.recompute()
    return result

#Independent values

tubeDiameter = 102
positionerDiameter = 6.0
positionerConeHeight = 2.5
height = 6.0
mainInnerDiam = 70
mainThickness = 5.0
holderInnerDiam = 10.7
holderThickness = 5
holderCenterDiameter = 73 
holderCutoffDiameter = 80
nHolders = 4

#Derivative values

mainOuterDiam = mainInnerDiam + mainThickness * 2.
holderOuterDiam = holderInnerDiam + holderThickness * 2.
holderCenter = holderCenterDiameter / 2.
positionerLength = ( tubeDiameter / 2.
                 - mainInnerDiam / 2.
                 - mainThickness / 2.
                 - positionerConeHeight)

#Making the parts

cutoffCylinder = makeCylinder(holderCutoffDiameter / 2., height)

outMain = makeCylinder(mainOuterDiam / 2. , height)
inMain = makeCylinder(mainInnerDiam / 2. , height)
ring = cut(outMain, inMain)

positioners = []
for i in range(1, nHolders + 1):
    oH = makeCylinder(holderOuterDiam / 2., height)
    iH = makeCylinder(holderInnerDiam / 2. , height)
    mTranslate = App.Matrix()
    mTranslate.move(App.Vector(holderCenter, 0, 0))
    mTranslate.rotateZ(2 * math.pi * i / nHolders)
    oH.Placement = App.Placement(mTranslate)
    iH.Placement = oH.Placement
    ring = fuse(ring, oH)
    ring = cut(ring, iH)
    p = makeCylinder(positionerDiameter / 2.,
                     positionerLength,
                     translate = App.Vector(0, 0, height / 2.),
                     rotate = App.Rotation(0, 90, 0))
    mTranslate = App.Matrix()
    mTranslate.rotateY( math.pi / 2 )
    mTranslate.move(App.Vector(mainInnerDiam / 2. + mainThickness / 2., 0, height / 2.))
    mTranslate.rotateZ(2 * math.pi * (i + 0.5) / nHolders)
    p.Placement = App.Placement(mTranslate)
    positioners.append(p)
    c = makeCone(positionerDiameter / 2.,
                 positionerDiameter / 2. - positionerConeHeight,
                 positionerConeHeight,
                 translate = App.Vector(0, 0, height / 2.),
                 rotate = App.Rotation(0, 90, 0))
    mTranslate = App.Matrix()
    mTranslate.rotateY( math.pi / 2 )
    mTranslate.move(App.Vector(mainInnerDiam / 2. + mainThickness / 2. + positionerLength, 0, height / 2.))
    mTranslate.rotateZ(2 * math.pi * (i + 0.5) / nHolders)
    c.Placement = App.Placement(mTranslate)
    positioners.append(c)
shape = common(ring, cutoffCylinder)
for positioner in positioners:
    shape = fuse(shape, positioner)


#COLORING AND SHOWING THE ACTUAL STRUCTURES
edgeObj = App.ActiveDocument.addObject("Part::Feature","shape")
Gui.ActiveDocument.getObject("shape").ShapeColor = (0.80,0.,0.)
edgeObj.Shape = shape

Gui.ActiveDocument.shape.Visibility = True
Gui.ActiveDocument.ActiveView.setNavigationType("Gui::InventorNavigationStyle")
Gui.ActiveDocument.ActiveView.fitAll()
