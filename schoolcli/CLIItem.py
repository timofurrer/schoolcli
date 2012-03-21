#!/usr/bin/python3.2

class CLIItem:
  _name       = None
  _function   = None
  _value      = None
  _subitems   = []
  _split_char = " "

  def __init__( self, name, function, value = None, subitems = [], split_char = " " ):
    self._name       = name
    self._function   = function
    self._value      = value
    self._subitems   = subitems
    self._split_char = split_char

  def GetName( self ):
    return self._name

  def GetCompleteName( self ):
    return self._name + self._split_char

  def GetFunction( self ):
    return self._function

  def GetValue( self ):
    return self._value

  def GetSubItems( self ):
    return self._subitems

  def GetSplitChar( self ):
    return self._split_char

  def AppendItem( self, item ):
    self._subitems.append( item )

  def RemoveItem( self, item ):
    self._subitems.remove( item )

  def Complete( self, line ):
    matches = []
    if line.startswith( self._name ):
      cmd, arg = line.split( self._split_char, 1 )
      for s in self._subitems:
        for i in s.Complete( arg ):
          matches.append( i )
    elif self._name.startswith( line ):
      matches.append( self )
    return matches

  def Call( self, line ):
    pass
