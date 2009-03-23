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
# Alex 20090207
# eLyXer formula processing

import sys
from container import *
from trace import Trace
from general import *


class Formula(Container):
  "A Latex formula"

  start = '\\begin_inset Formula'
  ending = '\\end_inset'

  def __init__(self):
    self.parser = FormulaParser()
    self.output = TagOutput()

  def process(self):
    "Convert the formula to HTML"
    text = self.contents[0]
    original, result = self.convert(text, 0)
    #Trace.debug('Formula ' + original + ' -> ' + result)
    self.contents = result
    self.restyle(TaggedText, self.restyletagged)
    if self.header[0] == 'inline':
      self.tag = 'span class="formula"'
      self.breaklines = False
    else:
      self.tag = 'div class="formula"'
      self.breaklines = True
  
  def convert(self, text, pos):
    "Convert a bit of text to HTML"
    processed = ''
    result = list()
    while pos < len(text) and text[pos] != '}':
      original, converted = self.convertchars(text, pos)
      #Trace.debug('converted: ' + unicode(converted))
      processed += original
      pos += len(original)
      result += converted
    return processed, result

  def convertchars(self, text, pos):
    "Convert one or more characters, return the conversion"
    #Trace.debug('Formula ' + text + ' @' + str(pos))
    for reader in Formula.readers:
      bit, result = reader(self, text, pos)
      if bit:
        return bit, result
    Trace.error('Unrecognized function at ' + str(self.parser.begin) + ' in ' +
        unicode(text[pos:]))
    return '\\', [Constant('\\')]

  def readalpha(self, text, pos):
    "Read alphabetic sequence"
    alpha = str()
    while pos < len(text) and text[pos].isalpha():
      alpha += text[pos]
      pos += 1
    return alpha, [TaggedText().constant(alpha, 'i')]

  def readsymbols(self, text, pos):
    "Read a string of symbols"
    symbols = unicode()
    result = unicode()
    while pos + len(symbols) < len(text):
      char = text[pos + len(symbols)]
      if char.isdigit() or char in FormulaConfig.unmodified:
        symbols += char
        result += char
      elif char in FormulaConfig.modified:
        symbols += char
        result += FormulaConfig.modified[char]
      else:
        break
    if len(symbols) == 0:
      return None, None
    return symbols, [Constant(result)]

  def command(self, text, pos):
    "read a command"
    command, translated = self.find(text, pos, FormulaConfig.commands)
    if not command:
      return None, None
    return command, [Constant(translated)]

  def readone(self, text, pos):
    "read a one-parameter function"
    function, value = self.find(text, pos, FormulaConfig.onefunctions)
    if not function:
      return None, None
    pos += len(function)
    bracket, result = self.readbracket(text, pos)
    if len(value) == 0:
      return function + bracket, []
    if value.startswith('*') and len(result) == 1:
      # combining
      first = result[0].searchfor(StringContainer)
      if first:
        first.contents[0] = value.replace('*','') + first.contents[0]
        return function + bracket, result
    return function + bracket, [TaggedText().complete(result, value)]

  def readtwo(self, text, pos):
    "read a two-parameter function"
    function, tags = self.find(text, pos, FormulaConfig.twofunctions)
    if not function:
      return None, None
    pos += len(function)
    bracket1, result1 = self.readbracket(text, pos)
    pos += len(bracket1)
    bracket2, result2 = self.readbracket(text, pos)
    original =  function + bracket1 + bracket2
    tagged1 = TaggedText().complete(result1, tags[1])
    tagged2 = TaggedText().complete(result2, tags[2])
    tagged0 = TaggedText().complete([tagged1, tagged2], tags[0])
    return original, [tagged0]

  def readbracket(self, text, pos):
    "Read a bracket as {result}"
    if text[pos] != u'{':
      Trace.error(u'Missing { in ' + text + '@' + str(pos))
      return '', [Constant('')]
    original, converted = self.convert(text, pos + 1)
    if text[pos + 1 + len(original)] != u'}':
      Trace.error(u'Missing } in ' + text + '@' + str(pos))
    return '{' + original + '}', converted

  def find(self, text, pos, map):
    "Read TeX command or function"
    bit = text[pos:]
    for element in map:
      if bit.startswith(element):
        return element, map[element]
    return None, []

  readers = [readalpha, readsymbols, command, readone, readtwo]

  def restyletagged(self, container, index):
    "Restyle tagged text"
    tagged = container.contents[index]
    if tagged.tag == 'span class="mathsf"' or tagged.tag == 'span class="text"':
      tagged.restyle(TaggedText, self.removeitalics)
      first = tagged.contents[0]
      if self.mustspaceunits(container.contents, index):
        first.contents[0] = u' ' + first.contents[0]
    elif tagged.tag == 'span class="sqrt"':
      tagged.tag = 'span class="root"'
      radical = TaggedText().constant(u'√', 'span class="radical"')
      container.contents.insert(index, radical)
    elif tagged.tag == 'i':
      group = TaggedText().complete([], 'i')
      self.group(index, group, self.isalpha)
      group.restyle(TaggedText, self.removeitalics)

  def removeitalics(self, container, index):
    "Remove italics tag"
    if container.contents[index].tag == 'i':
      container.remove(index)

  def isalpha(self, element):
    "Check if the element is all text"
    if isinstance(element, StringContainer):
      return element.contents[0].isalpha()
    for item in element.contents:
      if not self.isalpha(item):
        return False
    return True

  def mustspaceunits(self, contents, index):
    "Check if units must be spaced"
    if index == 0:
      return False
    first = contents[index].contents[0]
    if not isinstance(first, Constant):
      return False
    last = contents[index - 1]
    if isinstance(last, Constant):
      string = last.contents[-1]
      if len(string) == 0:
        return False
      if string[-1].isdigit():
        return True
    return False

class FormulaParser(Parser):
  "Parses a formula"

  def parseheader(self, reader):
    "See if the formula is inlined"
    self.begin = reader.linenumber + 1
    if reader.currentline().find('$') > 0:
      return ['inline']
    else:
      return ['block']
  
  def parse(self, reader):
    "Parse the formula"
    if '$' in reader.currentline():
      rest = reader.currentline().split('$', 1)[1]
      if '$' in rest:
        # formula is $...$
        formula = reader.currentline().split('$')[1]
        reader.nextline()
      else:
        # formula is multiline $...$
        formula = self.parsemultiliner(reader, '$')
    elif '\\[' in reader.currentline():
      # formula of the form \[...\]
      formula = self.parsemultiliner(reader, '\\]')
    elif '\\begin{' in reader.currentline() and reader.currentline().endswith('}\n'):
      current = reader.currentline().strip()
      endsplit = current.split('\\begin{')[1].split('}')
      endpiece = '\\end{' + endsplit[0] + '}'
      formula = self.parsemultiliner(reader, endpiece)
    else:
      Trace.error('Formula beginning ' + reader.currentline().strip +
          ' is unknown')
    while not reader.currentline().startswith(self.ending):
      stripped = reader.currentline().strip()
      if len(stripped) > 0:
        Trace.error('Unparsed formula line ' + stripped)
      reader.nextline()
    reader.nextline()
    return [formula]

  def parsemultiliner(self, reader, ending):
    "Parse a formula in multiple lines"
    reader.nextline()
    formula = ''
    while not reader.currentline().endswith(ending + '\n'):
      formula += reader.currentline()
      reader.nextline()
    formula += reader.currentline()[:-len(ending) - 1]
    reader.nextline()
    return formula

ContainerFactory.types.append(Formula)

