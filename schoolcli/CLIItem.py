#!/usr/bin/python3.2

class CLIItem:
  _name       = None
  _function   = None
  _value      = None
  _enabled    = True
  _subitems   = []
  _split_char = " "
  _category   = None

  def __init__( self, name, function = None, value = None, enabled = True, subitems = [], split_char = " ", category = None ):
    self._name       = name
    self._function   = function
    self._value      = value
    self._enabled    = enabled
    self._subitems   = subitems
    self._split_char = split_char
    self._category   = category

  def GetName( self ):
    return self._name

  def GetCompleteName( self ):
    return self._name + self._split_char

  def GetFunction( self ):
    return self._function

  def GetValue( self ):
    return self._value

  def IsEnabled( self ):
    return self._enabled

  def GetSubitems( self ):
    return self._subitems

  def GetSplitChar( self ):
    return self._split_char

  def GetCategory( self ):
    return self._category

  def GetUsage( self ):
    if self._function is not None:
      doc = self._function.__doc__
      if doc is not None:
        doc_splitted = doc.split( "||" )
        if len( doc_splitted ) == 2:
          return doc_splitted[0]
        else:
          return ""
      else:
        return ""
    else:
      return ""

  def GetHelpText( self ):
    if self._function is not None:
      doc = self._function.__doc__
      if doc is not None:
        doc_splitted = doc.split( "||" )
        if len( doc_splitted ) == 2:
          return doc_splitted[1]
        else:
          return doc
      else:
        return ""
    else:
      return ""

  def SetFunction( self, function ):
    self._function = function

  def Enabled( self, enabled ):
    self._enabled = enabled

  def AppendItem( self, item ):
    if isinstance( item, CLIItem ):
      self._subitems.append( item )

  def RemoveItem( self, item ):
    self._subitems.remove( item )

  def ClearItems( self ):
    for i in self._subitems:
      self._subitems.remove( i )
    self._subitems = []

  def GetItems( self ):
    return self._subitems

  def GetItemByName( self, name ):
    for i in self._subitems:
      if i.GetName( ) == name:
        return i
    return None

  def Complete( self, line ):
    matches = []
    if self._enabled:
      if line.startswith( self._name + self._split_char ):
        cmd, arg = line.split( self._split_char, 1 )
        for s in self._subitems:
          for i in s.Complete( arg ):
            matches.append( i )
      elif (self._name + self._split_char).startswith( line ):
        matches.append( self )
    return matches

  def GetItemByCLILine( self, line ):
    if line.startswith( self._name + self._split_char ):
      item, args = line.split( self._split_char, 1 )
      if args == "":
        return self, args
      else:
        for i in self._subitems:
          subitem, subargs = i.GetItemByCLILine( args )
          if subitem is not None:
            if subitem.GetFunction( ) is not None:
              return subitem, subargs
            else:
              return self, args
        return self, args
    elif self._name == line:
      return self, ""
    else:
      return None, line
