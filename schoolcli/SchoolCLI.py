#''!/usr/bin/python3.2

import os
import sqlite3
import argparse

from CLI import *
from School import *

class SchoolCLI( CLI ):
  _connection = None

  _database   = None

  def __init__( self, prompt = "School:{}> ", database = path.join( os.getenv( "HOME" ), ".schoolcli.db" ) ):
    CLI.__init__( self, "~/.schoolcli_history" )
    CLI.SetWelcomeText( self, "Welcome to schoolcli version 0.00.01" )
    CLI.SetPrompt( self, prompt )

    self.AddDefaultCommands( )
    self.AddSchoolCommands( )
    self.AddTermCommands( )
    self.AddSubjectCommands( )
    self.AddMarkCommands( )

    CLI.SetItemsEnabled( self, False )
    CLI.SetItemsEnabledByCategory( self, "school" )

    self._database = database

  def do_BeforStart( self ):
    self.SetupDatabase( )
    self._UpdateCDCommand( )

  def do_Stop( self ):
    self._connection.close( )

  def AddDefaultCommands( self ):
    CLI.AddHelpItem( self )
    CLI.RegisterItem( self, CLIItem( "exit", self.cmd_exit, category = "default", subitems = [] ) )
    CLI.RegisterItem( self, CLIItem( "cd", self.cmd_cd, category = "default", subitems = [] ) )
    CLI.RegisterItem( self, CLIItem( "ls", self.cmd_ls, category = "default", subitems = [] ) )
    CLI.RegisterItem( self, CLIItem( "pwd", self.cmd_pwd, category = "default", subitems = [] ) )
    self._UpdateCDCommand( )

  def AddSchoolCommands( self ):
    school = CLIItem( "school", self.cmd_school, category = "school", subitems = [] )
    school.AppendItem( CLIItem( "add", self.cmd_school_add, category = "school" ) )
    school.AppendItem( CLIItem( "remove", self.cmd_school_remove, category = "school" ) )
    CLI.RegisterItem( self, school )

  def AddTermCommands( self ):
    term = CLIItem( "term", self.cmd_term, category = "term", subitems = [] )
    term.AppendItem( CLIItem( "add", self.cmd_term_add, category = "term" ) )
    term.AppendItem( CLIItem( "remove", self.cmd_term_remove, category = "term" ) )
    CLI.RegisterItem( self, term )

  def AddSubjectCommands( self ):
    subject = CLIItem( "subject", self.cmd_subject, category = "subject", subitems = [] )
    subject.AppendItem( CLIItem( "add", self.cmd_subject_add, category = "subject" ) )
    subject.AppendItem( CLIItem( "remove", self.cmd_subject_remove, category = "subject" ) )
    CLI.RegisterItem( self, subject )

  def AddMarkCommands( self ):
    mark = CLIItem( "mark", self.cmd_mark, category = "mark", subitems = [] )
    mark.AppendItem( CLIItem( "add", self.cmd_mark_add, category = "mark" ) )
    mark.AppendItem( CLIItem( "remove", self.cmd_mark_remove, category = "mark" ) )
    CLI.RegisterItem( self, mark )

  def _UpdateCDCommand( self ):
    location = self.GetSchoolLocation( )
    item     = CLI.GetItemByName( self, "cd" )
    if item is not None:
      item.ClearItems( )
      item.AppendItem( CLIItem( "/", value = "/", category = "default" ) )
      item.AppendItem( CLIItem( "..", value = "..", category = "default" ) )
      if location == "root":
        school_names = [s.Name for s in School.GetSchools( self._connection )]
        for school_name in school_names:
          item.AppendItem( CLIItem( school_name, value = school_name, category = "default" ) )

  def SetupDatabase( self ):
    self._connection = sqlite3.connect( self._database )
    self._connection.row_factory = sqlite3.Row
    c = self._connection.cursor( )

    create_school_table = """
    CREATE TABLE IF NOT EXISTS School (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR NOT NULL
    );
    """
    create_term_table = """
    CREATE TABLE IF NOT EXISTS Term (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    school INTEGER NOT NULL,
    name VARCHAR NOT NULL,
    FOREIGN KEY( school ) REFERENCES School( id )
    );
    """
    create_termsubject_table = """
    CREATE TABLE IF NOT EXISTS Termsubject (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term INTEGER NOT NULL,
    subject INTEGER NOT NULL,
    FOREIGN KEY( term ) REFERENCES Term( id ),
    FOREIGN KEY( subject ) REFERENCES Subject( id )
    );
    """
    create_subject_table = """
    CREATE TABLE IF NOT EXISTS Subject (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR NOT NULL,
    shortcut VARCHAR
    );
    """
    create_mark_table = """
    CREATE TABLE IF NOT EXISTS Mark (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject INTEGER NOT NULL,
    mark DOUBLE NOT NULL,
    points DOUBLE,
    max_points DOUBLE,
    valuation DOUBLE,
    avarage_mark DOUBLE,
    date DATE,
    FOREIGN KEY( subject ) REFERENCES Subject( id )
    );
    """
    c.execute( create_school_table )
    c.execute( create_term_table )
    c.execute( create_subject_table )
    c.execute( create_termsubject_table )
    c.execute( create_mark_table )

    self._connection.commit( )
    c.close( )

    print( self._cf.bold_green( "Connected to valid database at path `{}`".format( self._database ) ) )

  def GetSchoolLocation( self ):
    location = CLI.ParseLocation( self )
    if len( location ) == 2:
      if location[0] == "" and location[1] == "":
        return "root"
      else:
        return None
    elif len( location ) == 3:
      return "school", location[1]
    else:
      return None

  def PrintSchoolTable( self, schools ):
    indent = " " * 4
    space  = " " * 6
    wall = "|"
    max_len_id = len( max( [str( s.Id ) for s in schools], key = len ) )
    max_len_name = len( max( [s.Name for s in schools], key = len ) )

    print( self._cf.bold_green( indent + "Id" + " " * (max_len_id - 2) + space + wall + " Name" + " " * (max_len_name - 4) ) )
    print( " " * 2 + "-" * (2 * len( space ) + max_len_id + max_len_name + 2 ) )

    for school in schools:
      print( indent + str( school.Id ) + " " * (max_len_id - len( str( school.Id ) ) ) + space + " " + wall + " " + school.Name )

  def cmd_cd( self, item, args, rawline ):
    """[location|..]||change current location. You can go into schools, terms and subjects"""
    location = self.GetSchoolLocation( )
    args = args.strip( )
    if args == "" or args == "/":
      CLI.SetLocation( self, "/" )
    elif args == "..":
      location = CLI.ParseLocation( self )
      back_location = location[1:len( location ) - 2]
      back_location.append( "/" )
      CLI.SetLocation( self, "/".join( back_location ) )
    elif location == "root":
      schools = School.GetSchools( self._connection )
      school_names = [s.Name for s in schools]
      if args in school_names:
        CLI.SetLocation( self, "/" + args + "/" )
      else:
        print( self._cf.bold_red( "Could not change location because school with name `{}` could not be found".format( args ) ) )

    location = self.GetSchoolLocation( )
    CLI.SetItemsEnabled( self, False )
    if location == "root":
      CLI.SetItemsEnabledByCategory( self, "school" )
    elif location[0] == "school":
      CLI.SetItemsEnabledByCategory( self, "term" )
    self._UpdateCDCommand( )

  def cmd_ls( self, item, args, rawline ):
    """list the current location content like all schools or subjects"""
    location = self.GetSchoolLocation( )
    if location == "root":
      self.PrintSchoolTable( School.GetSchools( self._connection ) )

  def cmd_pwd( self, item, args, rawline ):
    """print the working directory ( location )"""
    print( self._location )

  def cmd_school( self, item, args, rawline ):
    """<add|remove>||add or remove a school"""
    sys.stdout.write( "Usage:" )
    CLI.ItemHelpScreen( self, None, "school" )

  def cmd_school_add( self, item, args, rawline ):
    """-n <name>|-i||add a new school. Argument -n is to pass a name and -i for interactive mode"""
    parser = argparse.ArgumentParser( prog = "school add", description = self.cmd_school_add.__doc__.split( "||" )[1] )
    parser.add_argument( "-n", "--name", help = "set the name of the new school" )
    parser.add_argument( "-i", "--interactive", action = "store_true", help = "use the interactive mode" )

    try:
      parsed_args = parser.parse_args( args.split( " " ) )
      name = ""
      save = True
      if parsed_args.interactive:
        try:
          while name == "":
            name = input( "Name: " )
          save = input( "Do you want to save ([y]/n)? " )
          save = (save == "y" or save == "")
        except KeyboardInterrupt:
          save = False
          print( "" ) # To break down prompt to a new line
      elif parsed_args.name != "" and parsed_args.name is not None:
        name = parsed_args.name
      else:
        save = False
      if save:
        school = School( self._connection )
        school.Name = name
        if school.Insert( ):
          print( self._cf.bold_green( "School with name `{}` has been successfully saved!".format( name ) ) )
          self._UpdateCDCommand( )
        else:
          print( self._cf.bold_red( "An error occured during the insert action of school with name `{}`".format( name ) ) )
    except SystemExit:       # Do not exit cli if an error occured in parse_args
      pass

  def cmd_school_remove( self, item, args, rawline ):
    """-s <id>|-i||remove a school by id or in interactive mode"""
    parser = argparse.ArgumentParser( prog = "school remove", description = self.cmd_school_remove.__doc__.split( "||" )[1] )
    parser.add_argument( "-s", "--id", help = "set the id of the school to remove" )
    parser.add_argument( "-i", "--interactive", action = "store_true", help = "use the interactive mode" )

    try:
      id = None
      parsed_args = parser.parse_args( args.split( " " ) )
      schools = School.GetSchools( self._connection )
      available_ids = [str( s.Id ) for s in schools]
      if parsed_args.interactive:
        if len( schools ) == 0:
          print( self._cf.white( "There is no school to be removed" ) )
        else:
          print( self._cf.bold_green( "Schools you can remove:" ) )
          self.PrintSchoolTable( schools )
          try:
            id = input( "Enter id of the school to be removed: " )
          except KeyboardInterrupt:
            print( "" ) # To break down prompt to a new line
      elif parsed_args.id is not None and parsed_args.id != "":
        id = parsed_args.id

      if id is not None:
        if id in available_ids:
          school = [s for s in schools if str( s.Id ) == id][0]
          if school.Delete( ):
            print( self._cf.bold_green( "School with id `{}` has been successfully removed".format( id ) ) )
            self._UpdateCDCommand( )
          else:
            print( self._cf.bold_red( "An error occured during delete action of school with id `{}`".format( id ) ) )
        else:
          print( self._cf.bold_red( "School with id `{}` does not exist".format( id ) ) )
    except SystemExit:       # Do not exit cli if an error occured in parse_args
      pass

  def cmd_term( self, item, args, rawline ):
    pass

  def cmd_term_add( self, item, args, rawline ):
    pass

  def cmd_term_remove( self, item, args, rawline ):
    pass

  def cmd_subject( self, item, args, rawline ):
    pass

  def cmd_subject_add( self, item, args, rawline ):
    pass

  def cmd_subject_remove( self, item, args, rawline ):
    pass

  def cmd_mark( self, item, args, rawline ):
    pass

  def cmd_mark_add( self, item, args, rawline ):
    pass

  def cmd_mark_remove( self, item, args, rawline ):
    pass

  def cmd_exit( self, item, args, rawline ):
    """exit from the schoolcli"""
    CLI.Stop( self )
