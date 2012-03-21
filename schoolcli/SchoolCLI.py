#!/usr/bin/python3.2

from CLI import *

class SchoolCLI( CLI ):
  def __init__( self ):
    CLI.__init__( self, "~/.schoolcli_history" )
    CLI.RegisterItem( self, CLIItem( "bla", self.cmd_bla, subitems = [CLIItem( "on", self.cmd_bla ), CLIItem( "off", self.cmd_lol )] ) )
    CLI.RegisterItem( self, CLIItem( "lol", self.cmd_lol ) )

  def cmd_bla( self, args, rawline ):
    print( "bla" )

  def cmd_lol( self, args, rawline ):
    print( "lol" )


if __name__ == "__main__":
  sc = SchoolCLI( )
  sc.SetPrompt( "School:/> " )
  sc.Start( )
