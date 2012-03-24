#!/usr/bin/python3.2

import sys

sys.path.insert( 0, "schoolcli" )

from SchoolCLI import *

if __name__ == "__main__":
  sc = SchoolCLI( )
  sc.SetPrompt( "School:{}> " )
  sc.Start( )
  sc.Stop( )
