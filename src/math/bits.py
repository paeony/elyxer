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
# Alex 20090614
# eLyXer formula bits

import sys
from util.trace import Trace
from conf.config import *
from math.formula import *


class RawText(FormulaBit):
  "A bit of text inside a formula"

  def detect(self, pos):
    "Detect a bit of raw text"
    return pos.current().isalpha()

  def parse(self, pos):
    "Parse alphabetic text"
    alpha = self.glob(pos, lambda(p): p.current().isalpha())
    self.addconstant(alpha, pos)
    self.type = 'alpha'

class FormulaSymbol(FormulaBit):
  "A symbol inside a formula"

  modified = FormulaConfig.modified
  unmodified = FormulaConfig.unmodified['characters']

  def detect(self, pos):
    "Detect a symbol"
    if pos.current() in FormulaSymbol.unmodified:
      return True
    if pos.current() in FormulaSymbol.modified:
      return True
    return False

  def parse(self, pos):
    "Parse the symbol"
    if pos.current() in FormulaSymbol.unmodified:
      self.addconstant(pos.current(), pos)
      return
    if pos.current() in FormulaSymbol.modified:
      symbol = FormulaSymbol.modified[pos.current()]
      self.addoriginal(pos.current(), pos)
      self.contents.append(FormulaConstant(symbol))
      return
    Trace.error('Symbol ' + pos.current() + ' not found')

class Number(FormulaBit):
  "A string of digits in a formula"

  def detect(self, pos):
    "Detect a digit"
    return pos.current().isdigit()

  def parse(self, pos):
    "Parse a bunch of digits"
    digits = self.glob(pos, lambda(p): p.current().isdigit())
    self.addconstant(digits, pos)
    self.type = 'number'

class Bracket(FormulaBit):
  "A {} bracket inside a formula"

  start = FormulaConfig.starts['bracket']
  ending = FormulaConfig.endings['bracket']

  def __init__(self):
    "Create a (possibly literal) new bracket"
    FormulaBit.__init__(self)
    self.inner = None

  def detect(self, pos):
    "Detect the start of a bracket"
    return pos.checkfor(self.start)

  def parse(self, pos):
    "Parse the bracket"
    self.parsecomplete(pos, self.innerformula)

  def parseliteral(self, pos):
    "Parse a literal bracket"
    self.parsecomplete(pos, self.innerliteral)
    return self

  def parsecomplete(self, pos, innerparser):
    "Parse the start and end marks"
    if not pos.checkfor(self.start):
      Trace.error('Bracket should start with ' + self.start)
      return
    self.addoriginal(self.start, pos)
    pos.pushending(self.ending)
    innerparser(pos)
    if pos.isout():
      Trace.error('Bracket ' + self.original + ' should end with ' +
          self.ending)
      return
    if not pos.checkfor(self.ending):
      Trace.error('Missing ' + self.ending + ' in ' + pos.remaining())
      return
    self.addoriginal(self.ending, pos)

  def innerformula(self, pos):
    "Parse a whole formula inside the bracket"
    self.inner = WholeFormula()
    if self.inner.detect(pos):
      self.inner.parse(pos)
      self.add(self.inner)
      return
    if pos.finished():
      Trace.error('Unexpected end of bracket')
      return
    if pos.current() != self.ending:
      Trace.error('No formula in bracket at ' + pos.remaining())
    return

  def innerliteral(self, pos):
    "Parse a literal inside the bracket, which cannot generate html"
    literal = self.glob(pos, lambda(p): p.current() != self.ending)
    self.addoriginal(literal, pos)
    self.contents = literal

  def process(self):
    "Process the bracket"
    if self.inner:
      self.inner.process()

class SquareBracket(Bracket):
  "A [] bracket inside a formula"

  start = FormulaConfig.starts['squarebracket']
  ending = FormulaConfig.endings['squarebracket']

FormulaFactory.bits += [ FormulaSymbol(), RawText(), Number(), Bracket() ]

