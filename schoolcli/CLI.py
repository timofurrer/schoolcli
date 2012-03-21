#!/usr/bin/python3.2

import sys
from os import path
import readline

from CLIItem import *

class CLI:
  _started       = False
  _history_file  = None

  _items         = []         # List with all available CLI items
  _matches       = []         # Current matches if you press tab while typing

  def __init__( self, history_file = None ):
    if history_file is not None:
      self._history_file = path.expanduser( history_file )
    readline.set_completer( self._Complete )
    readline.parse_and_bind( "tab: complete" )

  def Start( self ):
    if self._history_file is not None:
      try:
        readline.read_history_file( self._history_file )
      except IOError:
        pass

    self._started = True
    line_input = ""
    while self._started:
      try:
        line_input = input( self._prompt )
      except EOFError:
        self.Stop( )
      except KeyboardInterrupt:
        self.Stop( )

      if self._started and line_input != "":
        print( line_input )

  def Stop( self ):
    if self._history_file is not None:
      readline.write_history_file( self._history_file )
    self._started = False
    print( ) # To break shell prompt to a new line

  def _Complete( self, line, state ):
    if state == 0:
      self._matches = []
      original_line = readline.get_line_buffer( )

      for i in self._items:
        for r in i.Complete( original_line ):
          self._matches.append( r )
    return self._matches[state].GetCompleteName( )

  def SetPrompt( self, prompt ):
    self._prompt = prompt

  def GetPrompt( self ):
    return self._prompt

  def PutPrompt( self ):
    sys.stdout.write( "\r{}".format( self._prompt ) )
    sys.stdout.write( readline.get_line_buffer( ) )
    sys.stdout.flush( )

  def RegisterItem( self, item ):
    if isinstance( item, CLIItem ):
      self._items.append( item )
