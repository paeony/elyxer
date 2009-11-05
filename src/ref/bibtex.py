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
# Alex 20090905
# eLyXer BibTeX processing

from util.trace import Trace
from util.clone import *
from io.output import *
from io.path import *
from io.bulk import *
from conf.config import *
from parse.position import *
from ref.link import *
from ref.biblio import *


class BibTeX(Container):
  "Show a BibTeX bibliography and all referenced entries"

  def __init__(self):
    self.parser = InsetParser()
    self.output = ContentsOutput()

  def process(self):
    "Read all bibtex files and process them"
    self.entries = []
    bibliography = TranslationConfig.constants['bibliography']
    tag = TaggedText().constant(bibliography, 'h1 class="biblio"')
    self.contents.append(tag)
    files = self.parameters['bibfiles'].split(',')
    for file in files:
      bibfile = BibFile(file)
      bibfile.parse()
      self.entries += bibfile.entries
      Trace.message('Parsed ' + unicode(bibfile))
    self.entries.sort(key = unicode)
    self.applystyle()

  def applystyle(self):
    "Read the style and apply it to all entries"
    style = self.readstyle()
    for entry in self.entries:
      entry.template = style['default']
      if entry.type in style:
        entry.template = style[entry.type]
      entry.process()
      self.contents.append(entry)

  def readstyle(self):
    "Read the style from the bibliography options"
    options = self.parameters['options'].split(',')
    for option in options:
      if hasattr(BibStylesConfig, option):
        return getattr(BibStylesConfig, option)
    return BibStylesConfig.default

class BibFile(object):
  "A BibTeX file"

  def __init__(self, filename):
    "Create the BibTeX file"
    self.filename = filename + '.bib'
    self.added = 0
    self.ignored = 0
    self.entries = []

  def parse(self):
    "Parse the BibTeX file"
    bibpath = InputPath(self.filename)
    bibfile = BulkFile(bibpath.path)
    parsed = list()
    for line in bibfile.readall():
      line = line.strip()
      if not line.startswith('%') and not line == '':
        parsed.append(line)
    self.parseentries('\n'.join(parsed))

  def parseentries(self, text):
    "Extract all the entries in a piece of text"
    pos = Position(text)
    pos.skipspace()
    while not pos.finished():
      self.parseentry(pos)

  def parseentry(self, pos):
    "Parse a single entry"
    for entry in Entry.entries:
      if entry.detect(pos):
        newentry = Cloner.clone(entry)
        newentry.parse(pos)
        if newentry.isreferenced():
          self.entries.append(newentry)
          self.added += 1
        else:
          self.ignored += 1
        return
    # Skip the whole line, and show it as an error
    pos.checkskip('\n')
    toline = pos.globexcluding('\n')
    Trace.error('Unidentified entry: ' + toline)
    pos.checkskip('\n')

  def __unicode__(self):
    "String representation"
    string = self.filename + ': ' + unicode(self.added) + ' entries added, '
    string += unicode(self.ignored) + ' entries ignored'
    return string

class Entry(Container):
  "An entry in a BibTeX file"

  entries = []
  structure = ['{', ',', '=', '"']
  quotes = ['{', '"', '#']

  def __init__(self):
    self.key = None
    self.tags = dict()
    self.output = TaggedOutput().settag('p class="biblio"')

  def parse(self, pos):
    "Parse the entry between {}"
    self.type = self.parsepiece(pos, Entry.structure)
    pos.skipspace()
    if not pos.checkskip('{'):
      self.lineerror(pos, 'Entry should start with {: ')
      return
    pos.pushending('}')
    self.parsetags(pos)
    pos.popending('}')
    pos.skipspace()

  def parsetags(self, pos):
    "Parse all tags in the entry"
    pos.skipspace()
    while not pos.finished():
      if pos.checkskip('{'):
        Trace.error('Unmatched {')
        return
      self.parsetag(pos)
  
  def parsetag(self, pos):
    piece = self.parsepiece(pos, Entry.structure)
    if pos.checkskip(','):
      self.key = piece
      return
    if pos.checkskip('='):
      piece = piece.lower().strip()
      pos.skipspace()
      value = self.parsevalue(pos)
      self.tags[piece] = value
      pos.skipspace()
      if not pos.finished() and not pos.checkskip(','):
        Trace.error('Missing , in BibTeX tag at ' + pos.current())
      return

  def parsevalue(self, pos):
    "Parse the value for a tag"
    pos.skipspace()
    if pos.checkfor(','):
      Trace.error('Unexpected ,')
      return ''
    if pos.checkfor('{'):
      return self.parsebracket(pos)
    elif pos.checkfor('"'):
      return self.parsequoted(pos)
    else:
      return self.parsepiece(pos, Entry.structure)

  def parsebracket(self, pos):
    "Parse a {} bracket"
    if not pos.checkskip('{'):
      Trace.error('Missing opening { in bracket')
      return ''
    pos.pushending('}')
    bracket = self.parserecursive(pos)
    pos.popending('}')
    return bracket

  def parsequoted(self, pos):
    "Parse a piece of quoted text"
    if not pos.checkskip('"'):
      Trace.error('Missing opening " in quote')
      return
    pos.pushending('"')
    quoted = self.parserecursive(pos)
    pos.popending('"')
    pos.skipspace()
    if pos.checkskip('#'):
      pos.skipspace()
      quoted += self.parsequoted(pos)
    return quoted

  def parserecursive(self, pos):
    "Parse brackets or quotes recursively"
    piece = ''
    while not pos.finished():
      piece += self.parsepiece(pos, Entry.quotes)
      if not pos.finished():
        if pos.checkfor('{'):
          piece += self.parsebracket(pos)
        elif pos.checkfor('"'):
          piece += self.parsequoted(pos)
        else:
          Trace.error('Missing opening { or ": ' + pos.current())
          return piece
    return piece

  def parsepiece(self, pos, undesired):
    "Parse a piece not structure"
    return pos.glob(lambda current: not current in undesired)

class SpecialEntry(Entry):
  "A special entry"

  types = ['@STRING', '@PREAMBLE', '@COMMENT']

  def detect(self, pos):
    "Detect the special entry"
    for type in SpecialEntry.types:
      if pos.checkfor(type):
        return True
    return False

  def isreferenced(self):
    "A special entry is never referenced"
    return False

  def __unicode__(self):
    "Return a string representation"
    return self.type

class PubEntry(Entry):
  "A publication entry"

  def detect(self, pos):
    "Detect a publication entry"
    return pos.checkfor('@')

  def isreferenced(self):
    "Check if the entry is referenced"
    if not self.key:
      return False
    return self.key in BiblioCite.entries

  def process(self):
    "Process the entry"
    biblio = BiblioEntry()
    biblio.processcites(self.key)
    self.contents = [biblio]
    self.contents.append(Constant(' '))
    self.contents.append(self.getcontents())

  def getcontents(self):
    "Get the contents as a constant"
    contents = self.template
    while contents.find('$') >= 0:
      tag = self.extracttag(contents)
      value = self.gettag(tag)
      contents = contents.replace('$' + tag, value)
    return Constant(contents)

  def extracttag(self, string):
    "Extract the first tag in the form $tag"
    pos = Position(string)
    pos.globexcluding('$')
    pos.skip('$')
    return pos.globalpha()

  def __unicode__(self):
    "Return a string representation"
    string = ''
    author = self.gettag('author')
    if author:
      string += author + ': '
    title = self.gettag('title')
    if title:
      string += '"' + title + '"'
    return string

  def gettag(self, key):
    "Get a tag with the given key"
    if not key in self.tags:
      return ''
    return self.tags[key]

Entry.entries += [SpecialEntry(), PubEntry()]

