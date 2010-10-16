#! /usr/bin/env python
# -*- coding: utf-8 -*-

#   eLyXer -- convert LyX source files to HTML output.
#
#   Copyright (C) 2009 Alex Fernández
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

# --end--
# Alex 20100705
# eLyXer: key that identifies a given document part (chapter, section...).

from util.trace import Trace
from util.options import *
from util.translate import *
from util.numbering import *
from util.docparams import *
from ref.label import *


class PartKey(object):
  "A key to identify a given document part (chapter, section...)."

  partkey = None
  tocentry = None
  tocsuffix = None
  anchortext = None
  number = None
  filename = None
  header = False

  def __init__(self):
    self.level = 0

  def createindex(self, partkey):
    "Create a part key for an index page."
    self.partkey = partkey
    self.tocentry = partkey
    self.filename = partkey
    return self

  def createfloat(self, partkey, number):
    "Create a part key for a float."
    self.partkey = partkey
    self.number = number
    self.tocentry = partkey
    self.tocsuffix = u':'
    return self

  def createformula(self, number):
    "Create the part key for a formula."
    self.number = number
    self.partkey = 'formula-' + number
    self.tocentry = '(' + number + ')'
    return self

  def createheader(self, headorfooter):
    "Create the part key for a header or footer."
    self.partkey = headorfooter
    self.tocentry = None
    self.header = True
    return self

  def createanchor(self, partkey):
    "Create an anchor for the page."
    self.partkey = partkey
    self.tocentry = partkey
    self.header = True
    return self

  def toclabel(self):
    "Create the label for the TOC."
    labeltext = ''
    if self.anchortext:
      labeltext = self.anchortext
    return Label().create(labeltext, self.partkey, type='toc')

  def __unicode__(self):
    "Return a printable representation."
    return 'Part key for ' + self.partkey

class LayoutPartKey(PartKey):
  "The part key for a layout."

  generator = NumberGenerator.instance

  def create(self, layout):
    "Set the layout for which we are creating the part key."
    self.processtype(layout.type)
    return self

  def processtype(self, type):
    "Process the layout type."
    self.level = self.generator.getlevel(type)
    self.number = self.generator.getnumber(type)
    anchortype = type.replace('*', '-')
    self.partkey = 'toc-' + anchortype + '-' + self.number
    self.tocentry = self.gettocentry(type)
    self.tocsuffix = u': '
    self.filename = self.getfilename(type)
    if self.generator.isnumbered(type):
      self.tocentry += ' ' + self.number
      self.tocsuffix = u':'
      self.anchortext = self.getanchortext(type)

  def gettocentry(self, type):
    "Get the entry for the TOC: Chapter, Section..."
    return Translator.translate(self.generator.deasterisk(type))

  def getanchortext(self, type):
    "Get the text for the anchor given to a layout type."
    if self.generator.isunique(type):
      return self.tocentry + '.'
    return self.number

  def getfilename(self, type):
    "Get the filename to be used if splitpart is active."
    if self.level == Options.splitpart and self.generator.isnumbered(type):
      return self.number
    if self.level <= Options.splitpart:
      self.filename = self.partkey.replace('toc-', '')
    return None

  def needspartkey(self, layout):
    "Find out if a layout needs a part key."
    if self.generator.isunique(layout.type):
      return True
    return self.generator.isinordered(layout.type)

  def __unicode__(self):
    "Get a printable representation."
    return 'Part key for layout ' + self.tocentry

class PartKeyGenerator(object):
  "Number a layout with the relevant attributes."

  partkeyed = []
  layoutpartkey = LayoutPartKey()

  def forlayout(cls, layout):
    "Get the part key for a layout."
    if not cls.layoutpartkey.needspartkey(layout):
      return None
    Label.lastlayout = layout
    cls.partkeyed.append(layout)
    return LayoutPartKey().create(layout)

  def forindex(cls, index):
    "Get the part key for an index or nomenclature."
    cls.partkeyed.append(index)
    return PartKey().createindex(index.name)

  forlayout = classmethod(forlayout)
  forindex = classmethod(forindex)

