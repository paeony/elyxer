#! /usr/bin/env python
# -*- coding: utf-8 -*-

# eLyXer configuration
# autogenerated from config file on 2010-03-15

class GeneralConfig(object):
  "Configuration class from config file"

  version = {
      u'date':u'2010-03-15', u'number':u'0.1', 
      }

class JavaToPyConfig(object):
  "Configuration class from config file"

  declarations = {
      u'$andvalue':u'$value && $value', 
      u'$arithmeticexpression':u'$value + $value', 
      u'$assignment':u'$variablename = $value;', u'$block':u'[$statement]*', 
      u'$class':u'$scope class $classname $inheritance { [$method]* }', 
      u'$classlist':u'[$classname]?[, $classname]*', u'$classname':u'$$', 
      u'$condition':u'$value|$logicalvalue', 
      u'$conditional':u'if ($condition) $block', 
      u'$declaration':u'$simpledeclaration|$declarationassignment', 
      u'$declarationassignment':u'$type $variablename = $value;', 
      u'$file':u'[$class]+', 
      u'$inheritance':u'[extends $classlist]? [implements $classlist]?', 
      u'$logicalvalue':u'$orvalue|$andvalue', 
      u'$method':u'$scope [$qualifier]* $type $methodname ( $paramsdeclaration ) { $block }', 
      u'$methodcall':u'$variablename[.$methodname($params)]+', 
      u'$methodname':u'$$', u'$orvalue':u'$value || $value', 
      u'$paramdeclaration':u'$type $variablename', 
      u'$params':u'[$value]?[,$value]+', 
      u'$paramsdeclaration':u'[$paramdeclaration]?[,$paramdeclaration]*', 
      u'$qualifier':u'static|final', u'$scope':u'public|private|protected', 
      u'$simpledeclaration':u'$type $variablename;', 
      u'$statement':u'$conditional|$declaration|$assignment|$methodcall', 
      u'$type':u'int|String|$classname', 
      u'$value':u'$variablename|$methodcall|$arithmeticexpression', 
      u'$variablename':u'$$', 
      }

  output = {
      u'$class':u'class $classname(object):\\n\\t[$method]*', 
      u'$classname':u'$classname', 
      u'$conditional':u'if $condition:\\n\\t$block', 
      u'$method':u'def $methodname:\\n\\t$block', 
      }

