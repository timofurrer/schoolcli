#!/usr/bin/python3.2

import os
import sqlite3

from CLI import *

class SchoolCLI( CLI ):
  _connection = None

  _database   = None

  def __init__( self, prompt = "School:{}> ", database = path.join( os.getenv( "HOME" ), ".schoolcli.db" ) ):
    CLI.__init__( self, "~/.schoolcli_history" )
    CLI.SetWelcomeText( self, "Welcome to schoolcli version 0.00.01" )
    CLI.SetPrompt( self, prompt )

    self.AddDefaultCommands( )
    self.AddSchoolCommands( )

    self._database = database

  def do_BeforStart( self ):
    self.SetupDatabase( )

  def do_Stop( self ):
    self._connection.close( )

  def AddDefaultCommands( self ):
    CLI.AddHelpItem( self )
    CLI.RegisterItem( self, CLIItem( "exit", self.cmd_exit, category = "default" ) )
    CLI.RegisterItem( self, CLIItem( "cd", self.cmd_cd, category = "default" ) )
    CLI.RegisterItem( self, CLIItem( "ls", self.cmd_ls, category = "default" ) )
    CLI.RegisterItem( self, CLIItem( "pwd", self.cmd_pwd, category = "default" ) )

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
    mark.AppendItems( CLIItem( "add", self.cmd_mark_add, category = "mark" ) )
    mark.AppendItems( CLIItem( "remove", self.cmd_mark_remove, category = "mark" ) )
    CLI.RegisterItem( self, mark )

  def SetupDatabase( self ):
    self._connection = sqlite3.connect( self._database )
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

  def cmd_cd( self, item, args, rawline ):
    """[location|..]||change current location. You can go into schools, terms and subjects"""
    pass

  def cmd_ls( self, item, args, rawline ):
    """list the current location content like all schools or subjects"""
    pass

  def cmd_pwd( self, item, args, rawline ):
    """print the working directory ( location )"""
    print( self._location )

  def cmd_school( self, item, args, rawline ):
    """<add|remove>||add or remove a school"""
    sys.stdout.write( "Usage:" )
    CLI.ItemHelpScreen( self, None, "school" )

  def cmd_school_add( self, item, args, rawline ):
    pass

  def cmd_school_remove( self, item, args, rawline ):
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
