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
# Alex 20090324
# eLyXer postprocessor code

from gen.container import *
from util.trace import Trace
from gen.structure import *
from ref.label import *
from gen.layout import *
from gen.inset import *
from util.numbering import *
from ref.link import *


class Group(Container):
  "A silly group of containers"

  def __init__(self):
    self.output = ContentsOutput()

  def contents(self, contents):
    self.contents = contents
    return self

  def __unicode__(self):
    return 'Group: ' + unicode(self.contents)

class PostLayout(object):
  "Numerate an indexed layout"

  processedclass = Layout

  def postprocess(self, layout, last):
    "Generate a number and place it before the text"
    if self.containsappendix(layout):
      self.activateappendix()
    layout.unordered = False
    if NumberGenerator.instance.isunique(layout):
      layout.number = NumberGenerator.instance.generateunique(layout.type)
      layout.entry = TranslationConfig.constants[layout.type] + ' ' + layout.number
      text = layout.entry + '.'
    elif NumberGenerator.instance.isordered(layout):
      layout.number = NumberGenerator.instance.generateordered(layout.type)
      text = layout.number
      layout.entry = TranslationConfig.constants[layout.type] + ' ' + layout.number
      self.modifylayout(layout, layout.type)
    elif NumberGenerator.instance.isunordered(layout):
      layout.unordered = True
      layout.number = NumberGenerator.instance.generateunique('unordered')
      text = ''
      type = NumberGenerator.instance.deasterisk(layout.type)
      layout.entry = TranslationConfig.constants[type]
      self.modifylayout(layout, type)
    else:
      return layout
    key = 'toc-' + layout.type + '-' + layout.number
    label = Label().create(text, key, type='toc')
    layout.contents.insert(0, label)
    if not layout.unordered:
      layout.contents.insert(1, Constant(u' '))
    return layout

  def modifylayout(self, layout, type):
    "Modify a layout according to the given type."
    layout.level = NumberGenerator.instance.getlevel(type)
    layout.output.tag = layout.output.tag.replace('?', unicode(layout.level))

  def containsappendix(self, layout):
    "Find out if there is an appendix somewhere in the layout"
    for element in layout.contents:
      if isinstance(element, Appendix):
        return True
    return False

  def activateappendix(self):
    "Change first number to letter, and chapter to appendix"
    NumberGenerator.instance.number = ['-']

class PostStandard(object):
  "Convert any standard spans in root to divs"

  processedclass = StandardLayout

  def postprocess(self, standard, last):
    "Switch to div"
    standard.output = TaggedOutput().settag('div class="Standard"', True)
    return standard

class Postprocessor(object):
  "Postprocess a container keeping some context"

  stages = [PostLayout, PostStandard]

  def __init__(self):
    self.stages = StageDict(Postprocessor.stages, self)
    self.hooks = []
    self.last = None

  def postprocess(self, container):
    "Postprocess the root container and its contents"
    self.postrecursive(container)
    result = self.postcurrent(container)
    result = self.posthooks(container, result)
    self.last = container
    return result

  def postrecursive(self, container):
    "Postprocess the container contents recursively"
    if not hasattr(container, 'contents'):
      return
    contents = container.contents
    if len(contents) == 0:
      return
    postprocessor = Postprocessor()
    for index, element in enumerate(contents):
      if isinstance(element, Container):
        contents[index] = postprocessor.postprocess(element)
    postlast = postprocessor.postprocess(None)
    if postlast:
      contents.append(postlast)

  def postcurrent(self, element):
    "Postprocess the current element taking into account the last one"
    stage = self.stages.getstage(element)
    if not stage:
      return element
    return stage.postprocess(element, self.last)

  def addhook(self, hook):
    "Add a postprocessing hook; only one of each type allowed."
    for element in self.hooks:
      if isinstance(element, hook.__class__):
        return
    self.hooks.append(hook)
    hook.postprocessor = self

  def posthooks(self, element, result):
    "Postprocess the current element using the hooks."
    "The element is used to see if the hook applies, but the previous"
    "result is actually used in postprocessing."
    for hook in self.hooks:
      if hook.applies(element, self.last):
        result = hook.postprocess(result, self.last)
    return result

class StageDict(object):
  "A dictionary of stages corresponding to classes"

  def __init__(self, classes, postprocessor):
    "Instantiate an element from each class and store as a dictionary"
    instances = self.instantiate(classes, postprocessor)
    self.stagedict = dict([(x.processedclass, x) for x in instances])

  def instantiate(self, classes, postprocessor):
    "Instantiate an element from each class"
    stages = [x.__new__(x) for x in classes]
    for element in stages:
      element.__init__()
      element.postprocessor = postprocessor
    return stages

  def getstage(self, element):
    "Get the stage for a given element, if the type is in the dict"
    if not element.__class__ in self.stagedict:
      return None
    return self.stagedict[element.__class__]

class PostHook(object):
  "A postprocessing hook inserted by another postprocessing stage."
  "It can only add an element, not modify an existing one."
  "Only a hook of a given class is allowed."

  def applies(self, element, last):
    "Decide if the hook applies or not"
    Trace.error("applies() in PostHook")

  def postprocess(self, element, last):
    "Get the result of postprocessing"
    Trace.error("getresult() in PostHook")

