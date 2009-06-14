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
# Alex 20090503
# eLyXer formula parsing

import sys
from gen.container import *
from util.trace import Trace
from conf.config import *


class FormulaParser(Parser):
  "Parses a formula"

  def parseheader(self, reader):
    "See if the formula is inlined"
    self.begin = reader.linenumber + 1
    if reader.currentline().find(FormulaConfig.starts['simple']) > 0:
      return ['inline']
    else:
      return ['block']
  
  def parse(self, reader):
    "Parse the formula until the end"
    formula = self.parseformula(reader)
    while not reader.currentline().startswith(self.ending):
      stripped = reader.currentline().strip()
      if len(stripped) > 0:
        Trace.error('Unparsed formula line ' + stripped)
      reader.nextline()
    reader.nextline()
    return [formula]

  def parseformula(self, reader):
    "Parse the formula contents"
    simple = FormulaConfig.starts['simple']
    if simple in reader.currentline():
      rest = reader.currentline().split(simple, 1)[1]
      if simple in rest:
        # formula is $...$
        return self.parsesingleliner(reader, simple, simple)
      # formula is multiline $...$
      return self.parsemultiliner(reader, simple, simple)
    if FormulaConfig.starts['complex'] in reader.currentline():
      # formula of the form \[...\]
      return self.parsemultiliner(reader, FormulaConfig.starts['complex'],
          FormulaConfig.endings['complex'])
    beginbefore = FormulaConfig.starts['beginbefore']
    beginafter = FormulaConfig.starts['beginafter']
    if beginbefore in reader.currentline():
      if reader.currentline().strip().endswith(beginafter):
        current = reader.currentline().strip()
        endsplit = current.split(beginbefore)[1].split(beginafter)
        startpiece = beginbefore + endsplit[0] + beginafter
        endbefore = FormulaConfig.endings['endbefore']
        endafter = FormulaConfig.endings['endafter']
        endpiece = endbefore + endsplit[0] + endafter
        return self.parsemultiliner(reader, startpiece, endpiece)
      Trace.error('Missing ' + beginafter + ' in ' + reader.currentline())
      return ''
    begincommand = FormulaConfig.starts['command']
    beginbracket = FormulaConfig.starts['bracket']
    if begincommand in reader.currentline() and beginbracket in reader.currentline():
      endbracket = FormulaConfig.endings['bracket']
      return self.parsemultiliner(reader, beginbracket, endbracket)
    Trace.error('Formula beginning ' + reader.currentline() + ' is unknown')
    return ''

  def parsesingleliner(self, reader, start, ending):
    "Parse a formula in one line"
    line = reader.currentline().strip()
    if not start in line:
      Trace.error('Line ' + line + ' does not contain formula start ' + start)
      return ''
    if not line.endswith(ending):
      Trace.error('Formula ' + line + ' does not end with ' + ending)
      return ''
    index = line.index(start)
    rest = line[index + len(start):-len(ending)]
    reader.nextline()
    return rest

  def parsemultiliner(self, reader, start, ending):
    "Parse a formula in multiple lines"
    formula = ''
    line = reader.currentline()
    if not start in line:
      Trace.error('Line ' + line.strip() + ' does not contain formula start ' + start)
      return ''
    index = line.index(start)
    formula = line[index + len(start):].strip()
    reader.nextline()
    while not reader.currentline().endswith(ending):
      formula += reader.currentline()
      reader.nextline()
    formula += reader.currentline()[:-len(ending)]
    reader.nextline()
    return formula

class Position(object):
  "A position in a formula to parse"

  def __init__(self, text):
    self.text = text
    self.pos = 0
    self.endinglist = EndingList()

  def skip(self, string):
    "Skip a string"
    self.pos += len(string)

  def remaining(self):
    "Return the text remaining for parsing"
    return self.text[self.pos:]

  def finished(self):
    "Find out if the current formula has finished"
    if self.isout():
      self.endinglist.checkpending()
      return True
    return self.endinglist.checkin(self)

  def isout(self):
    "Find out if we are out of the formula yet"
    return self.pos >= len(self.text)

  def current(self):
    "Return the current character"
    if self.isout():
      Trace.error('Out of the formula')
      return ''
    return self.text[self.pos]

  def checkfor(self, string):
    "Check for a string at the given position"
    if self.pos + len(string) > len(self.text):
      return False
    return self.text[self.pos : self.pos + len(string)] == string

  def pushending(self, ending, optional = False):
    "Push a new ending to the bottom"
    Trace.debug('Adding ' + ending)
    self.endinglist.add(ending, optional)

class EndingList(object):
  "A list of position endings"

  def __init__(self):
    self.endings = []

  def add(self, ending, optional):
    "Add a new ending to the list"
    self.endings.append(PositionEnding(ending, optional))

  def checkin(self, pos):
    "Search for an ending"
    if len(self.endings) == 0:
      return False
    for index, ending in enumerate(reversed(self.endings)):
      if ending.checkin(pos):
        Trace.debug('Found ' + unicode(ending))
        self.remove(index + 1)
        return True
      if not ending.optional:
        return False
    return False

  def remove(self, number):
    "Remove a number of endings"
    for i in range(number):
      self.endings.pop()

  def checkpending(self):
    "Check if there are any pending endings"
    if len(self.endings) != 0:
      Trace.error('Pending endings ' + unicode(self.endings) + ' in ' + self.text)

class PositionEnding(object):
  "An ending for a formula position"

  def __init__(self, ending, optional):
    self.ending = ending
    self.optional = optional

  def checkin(self, pos):
    "Check for the ending"
    return pos.checkfor(self.ending)

  def __unicode__(self):
    "Printable representation"
    string = 'Ending ' + self.ending
    if self.optional:
      string += ' (optional)'
    return string

