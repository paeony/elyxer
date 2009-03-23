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
# Alex 20090320
# eLyXer general configuration


class FormulaConfig(object):
  "Configuration for formulae"

  unmodified = ['.', '*', u'€', '(', ')', '[', ']', ':', u'·']
  modified = {'\'':u'’', '=':u' = ', ' ':'', '<':u' &lt; ', '-':u' − ', '+':u' + ',
      ',':u', ', '/':u' ⁄ ', '\n':''}
  commands = {
      # spacing
      '\\, ':' ', '& ':u'', '\\\\':'<br/>', '\\,':u' ',
      # typographical
      '\\%':'%', '\\prime':u'′', '\\_':'_',
      '\\left(':u'<span class="bigsymbol">(</span>',
      '\\right)':u'<span class="bigsymbol">)</span>',
      '\\left[':u'<span class="bigsymbol">[</span>',
      '\\right]':u'<span class="bigsymbol">]</span>',
      # regional
      '\\tilde{n}':u'ñ', '\\acute{o}':u'ó', '\\acute{a}':u'á',
      # greek
      '\\alpha':u'α', '\\beta':u'β', '\\gamma':u'γ', '\\delta':u'δ',
      '\\epsilon':u'ε', '\\lambda':u'λ', '\\Delta':u'Δ',
      '\\sigma':u'σ', '\\pi':u'π',
      # mathematical
      '\\times':u' × ', '\\propto':u' ∝ ', '\\cdot':u'⋅', '\\approx':u' ≈ ',
      '\\pm':u'±', '\\sim':u' ~ ', '\\implies':u'  ⇒  ', '\\not':u'¬',
      '\\sum':u'<span class="bigsymbol">∑</span>',
      '\\int':u'<span class="bigsymbol">∫</span>',
      '\\intop':u'<span class="bigsymbol">∫</span>', '\\infty':u'∞',
      # symbols
      '\\rightarrow':u' → ', '\\rightsquigarrow':u' ⇝ ', '\\Rightarrow':u'⇒',
      '\\leftarrow':u' ← ',
      '\\dashrightarrow':u' ⇢ ', '\\blacktriangleright':u'▶', '\\bullet':u'•',
      '\\dagger':u'†', '\\ddagger':u'‡', '\\bigstar':u'★',
      '\\to':u'→', '\\gets':u'←', '\\circ':u'○', '\\diamond':u'◇',
      '\\triangleright':u'▷',
      # common functions
      '\\log':'log', '\\exp':'exp', '\\ln':'ln', '\\lim':'lim', '\\sin':'sin',
      '\\cos':'cos',
      # hyperbolic functions
      '\\tanh':'tanh', '\\sinh':'sinh', '\\cosh':'cosh',
      # LaTeX (ignored)
      '\\nonumber':'', '\\lyxlock':'', '\\end{array}':''
      }
  onefunctions = {
      # typographical
      '\\mathsf':'span class="mathsf"', '\\mathbf':'b', '^':'sup',
      '_':'sub', '\\underline':'u', '\\overline':'span class="overline"',
      '\\dot':'span class="dotted"',
      '\\bar':'span class="bar"', '\\mbox':'span class="mbox"',
      '\\textrm':'span class="mathrm"', '\\mathrm':'span class="mathrm"',
      '\\text':'span class="text"', '\\textipa':'span class="textipa"',
      '\\boldsymbol':'b', '\\mathit':'i', '\\mathtt':'tt',
      '\\mathbb':'span class="blackboard"',
      '\\mathfrak':'span class="fraktur"', '\\mathcal':'span class="script"',
      # combining (start with *)
      '\\check':u'*\u030C', '\\breve':u'*\u0306', '\\vector':u'*\u20D7',
      '\\dot':u'*\u0307',
      # functions
      '\\sqrt':'span class="sqrt"',
      # hard functions
      '\\begin{array}':'span class="arraydef"',
      # LaTeX (ignored)
      '\\label':''
      }
  twofunctions = {
      '\\frac':['span class="fraction"', 'span class="numerator"', 'span class="denominator"'],
      '\\nicefrac':['span class="fraction"', 'span class="numerator"', 'span class="denominator"']
      }

class ContainerConfig(object):
  "Low-level configuration for containers"

  escapes = {'&':'&amp;', '<':'&lt;', '>':'&gt;'}
  replaces = { '`':u'‘', '\'':u'’', '\n':'', '--':u'—' }
  commands = { '\\SpecialChar \\ldots{}':u'…', '\\InsetSpace ~':'&nbsp;',
      '\\InsetSpace \\space{}':'&nbsp;', '\\InsetSpace \\thinspace{}':u' ',
      '\\backslash':'\\', '\\SpecialChar \\@.':'.',
      '\\SpecialChar \\menuseparator':u'&nbsp;▷&nbsp;',
      '\\SpecialChar \\textcompwordmark{}':u'', '\\SpecialChar \\nobreakdash-':'-',
      '\\SpecialChar \\slash{}':'/'}

class BlackBoxConfig(object):
  "Configuration for lines ignored"

  starts = ['\\lyxformat', '\\begin_document', '\\begin_body',
      '\\family default', '\\color inherit',
      '\\shape default', '\\series default', '\\emph off',
      '\\bar no', '\\noun off', '\\emph default', '\\bar default',
      '\\noun default', '\\family roman', '\\series medium',
      '\\shape up', '\\size normal', '\\color none', '#LyX', '\\noindent',
      '\\labelwidthstring', '\\paragraph_spacing', '\\length']

class SpaceConfig(object):
  "Configuration for spaces"

  spaces = {
      '~':'&nbsp;', '\\space{}':'&nbsp;', '\\thinspace{}':u' ',
      '\\hfill{}':u' ', '\\hspace*{\\fill}':u' ', '\\hspace{}':u' ',
      '\\negthinspace{}':u'', '\\enskip{}':u' ', '\\quad{}': u' ',
      '\\qquad{}':u'  '
      }

