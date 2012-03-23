#!/usr/bin/python3.2

from CLI import *

class SchoolCLI( CLI ):
  def __init__( self, prompt = "School:/> " ):
    CLI.__init__( self, "~/.schoolcli_history" )
    CLI.SetWelcomeText( self, "Welcome to schoolcli version 0.00.01" )
    CLI.SetPrompt( self, prompt )
    CLI.RegisterItem( self, CLIItem( "exit", self.cmd_exit ) )
    CLI.RegisterItem( self, CLIItem( "bla", self.cmd_bla, subitems = [CLIItem( "on", self.cmd_bla ), CLIItem( "off", self.cmd_lol ), CLIItem( "val", value = "value" )] ) )
    CLI.RegisterItem( self, CLIItem( "lol", self.cmd_lol ) )

  def cmd_bla( self, item, args, rawline ):
    print( "bla" )

  def cmd_lol( self, item, args, rawline ):
    print( "lol" )

  def cmd_exit( self, item, args, rawline ):
    """exit from the schoolcli"""
    CLI.Stop( self )
