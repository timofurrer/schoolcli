#!/usr/bin/python3.2

from SchoolCLI import *

if __name__ == "__main__":
  sc = SchoolCLI( )
  sc.SetPrompt( "School:{}> " )
  sc.Start( )
  sc.Stop( )
