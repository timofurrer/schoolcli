#!/usr/bin/python3.2

import sys
from os import path
import readline

from CLIItem import *

sys.path.insert( 0, "colorful/colorful" ) # Need to add Colorful

from Colorful import * # For colored output in chell

class CLI:
  _started       = False
  _history_file  = None

  _welcome_text  = None

  _location      = "/"        # Current location

  _items         = []         # List with all available CLI items
  _matches       = []         # Current matches if you press tab while typing

  _cf            = None       # Instance of Colorful

  def __init__( self, history_file = None, welcome_text = None ):
    self._cf = Colorful( )
    readline.set_completer( self._Complete )
    readline.parse_and_bind( "tab: complete" )

    if history_file is not None:
      self._history_file = path.expanduser( history_file )
    self._welcome_text = welcome_text

  def Start( self ):
    if self._history_file is not None:
      try:
        readline.read_history_file( self._history_file )
      except IOError: # Occures if the history_file does not exist yet
        pass

    self._started = True
    if self._welcome_text is not None:
      print( self._cf.bold_white( self._welcome_text ) )

    if hasattr( self, "do_BeforStart" ):
      self.do_BeforStart( )

    line_input = ""
    while self._started:
      try:
        line_input = input( self.GetPrompt( ) )
      except EOFError:          # Occures when Ctrl+D is pressed in shell
        self.Stop( )
        print( ) # To break shell prompt to a new line
      except KeyboardInterrupt: # Occures when Ctrl+C is pressed in shell
        self.Stop( )
        print( ) # To break shell prompt to a new line

      if self._started and line_input != "":
        item, args = self.GetItemByCLILine( line_input )
        if item is not None:
          f = item.GetFunction( )
          if f is not None:
            f( item, args, line_input )
          else:
            print( self._cf.bold_red( "Item is not callable" ) )
        else:
          print( self._cf.bold_red( "Command can not be found" ) )

  def Stop( self ):
    if self._history_file is not None:
      readline.write_history_file( self._history_file )

    self._started = False

    if hasattr( self, "do_Stop" ):
      self.do_Stop( )

  def _Complete( self, line, state ):
    if state == 0:
      self._matches = []
      original_line = readline.get_line_buffer( )

      for i in self._items:
        for r in i.Complete( original_line ):
          self._matches.append( r )
    return self._matches[state].GetCompleteName( )

  def SetWelcomeText( self, welcome_text ):
    self._welcome_text = welcome_text

  def SetPrompt( self, prompt ):
    self._prompt = prompt

  def GetPrompt( self, colored = True ):
    if colored:
      return self._prompt.format( self._cf.cyan( self._location ) )
    else:
      return self._prompt.format( self._location )

  def PutPrompt( self, colored = True ):
    if colored:
      sys.stdout.write( "\r{}".format( self.GetPrompt( ) ) )
    else:
      sys.stdout.write( "\r{}".format( self.GetPrompt( False ) ) )
    sys.stdout.write( readline.get_line_buffer( ) )
    sys.stdout.flush( )

  def RegisterItem( self, item ):
    if isinstance( item, CLIItem ):
      self._items.append( item )
      return True
    else:
      return False

  def ClearItems( self ):
    for i in self._items:
      self._items.remove( i )

  def GetItems( self ):
    return self._items

  def GetItemByName( self, name ):
    for i in self._items:
      if i.GetName( ) == name:
        return i
    return None

  def GetItemsByCategory( self, category ):
    return [i for i in self._items if i.GetCategory( ) == category]

  def SetItemsEnabledByCategory( self, enabled = True ):
    for i in self._items:
      i.Enabled( enabled )

  def GetItemByCLILine( self, line ):
    for i in self._items:
      item, args = i.GetItemByCLILine( line )
      if item is not None:
        if item.IsEnabled( ):
          return item, args
    return None, line

  def RemoveItemByName( self, name ):
    for i in self._items:
      if i.GetName( ) == name:
        self._items.remove( i )

  def AddHelpItem( self ):
    item = CLIItem( "help", self.ItemHelpScreen, category = "help" )
    self.RegisterItem( item )

  def ItemHelpScreen( self, item, args = "", line = "" ):
    """[command]||show this help screen"""
    indent           = " " * 4
    space            = " " * 6
    max_len_name     = len( max( [i.GetName( )     for i in self._items], key = len ) )
    max_len_usage    = len( max( [i.GetUsage( )    for i in self._items], key = len ) )
    max_len_helptext = len( max( [i.GetHelpText( ) for i in self._items], key = len ) )

    if args == "":
      for i in sorted( self._items, key = lambda i: i.GetName( ) ):
        f = i.GetFunction( )
        if f is not None:
          sys.stdout.write( indent + self._cf.bold_green( i.GetName( ) ) + " " * ( max_len_name - len( i.GetName( ) ) ) )
          sys.stdout.write( space + i.GetUsage( ) + " " * ( max_len_usage - len( i.GetUsage( ) ) ) )
          sys.stdout.write( space + i.GetHelpText( ) + "\n" )
    else:
      item = self.GetItemByName( args )
      if item is not None:
        f = item.GetFunction( )
        if f is not None:
          print( indent + self._cf.bold_green( item.GetName( ) ) + space + item.GetUsage( ) + space + item.GetHelpText( ) )
        else:
          print( self._cf.bold_red( "Command has no function defined, so no help could be showed" ) )
      else:
        print( self._cf.bold_red( "Command can not be found" ) )
