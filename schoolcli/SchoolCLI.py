#''!/usr/bin/python3.2

import os
import sqlite3
import argparse

from CLI import *
from School import *
from Term import *
from Subject import *
from Termsubject import *

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
    subject.AppendItem( CLIItem( "link", self.cmd_subject_link, category = "subject" ) )
    subject.AppendItem( CLIItem( "unlink", self.cmd_subject_unlink, category = "subject" ) )
    CLI.RegisterItem( self, subject )

  def AddMarkCommands( self ):
    mark = CLIItem( "mark", self.cmd_mark, category = "mark", subitems = [] )
    mark.AppendItem( CLIItem( "add", self.cmd_mark_add, category = "mark" ) )
    mark.AppendItem( CLIItem( "remove", self.cmd_mark_remove, category = "mark" ) )
    CLI.RegisterItem( self, mark )

  def _UpdateCDCommand( self ):
    location, value = self.GetSchoolLocation( )
    item            = CLI.GetItemByName( self, "cd" )
    if item is not None:
      item.ClearItems( )
      item.AppendItem( CLIItem( "/", value = "/", category = "default" ) )
      item.AppendItem( CLIItem( "..", value = "..", category = "default" ) )
      if location == "root":
        school_names = [s.Name for s in School.GetSchools( self._connection )]
        for school_name in school_names:
          item.AppendItem( CLIItem( school_name, value = school_name, category = "default" ) )
      if location == "school":
        term_names = [t.Name for t in Term.GetTermsBySchool( self._connection, CLI.GetLocationValue( self ) )]
        for term_name in term_names:
          item.AppendItem( CLIItem( term_name, value = term_name, category = "default" ) )
      if location == "term":
        subject_names = [s.Shortcut for s in Subject.GetSubjectsByTerm( self._connection, CLI.GetLocationValue( self ) )]
        for subject_name in subject_names:
          item.AppendItem( CLIItem( subject_name, value = subject_name, category = "default" ) )

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
    termsubject INTEGER NOT NULL,
    mark DOUBLE NOT NULL,
    points DOUBLE,
    max_points DOUBLE,
    valuation DOUBLE,
    avarage_mark DOUBLE,
    date DATE,
    FOREIGN KEY( termsubject ) REFERENCES Termsubject( id )
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
        return "root", None
    elif len( location ) == 3:
      return "school", location[1]
    elif len( location ) == 4:
      return "term", location[2]
    elif len( location ) == 5:
      return "subject", location[3]
    return None, None

  def PrintSchoolTable( self, schools ):
    indent = " " * 4
    space  = " " * 6
    wall   = "|"
    if len( schools ) > 0:
      max_len_id   = len( max( [str( s.Id ) for s in schools], key = len ) )
      max_len_name = len( max( [s.Name for s in schools],      key = len ) )

      if len( "Id" ) > max_len_id:
        max_len_id = len( "Id" )
      if len( "Name" ) > max_len_name:
        max_len_name = len( "Name" )

      print( indent + self._cf.bold_green( "Id" ) + " " * (max_len_id - 2) + space + wall + " " + self._cf.bold_green( "Name" ) )
      print( " " * 2 + "-" * (2 * len( space ) + max_len_id + max_len_name + 2 ) )

      for school in schools:
        print( indent + str( school.Id ) + " " * (max_len_id - len( str( school.Id ) ) ) + space + wall + " " + school.Name )
    else:
      print( self._cf.bold_green( "There are no schools" ) )

  def PrintTermTable( self, terms ):
    indent = " " * 4
    space  = " " * 6
    wall   = "|"
    if len( terms ) > 0:
      max_len_id          = len( max( [str( t.Id ) for t in terms],   key = len ) )
      max_len_school_name = len( max( [t.School.Name for t in terms], key = len ) )
      max_len_name        = len( max( [t.Name for t in terms],        key = len ) )

      if len( "Id" ) > max_len_id:
        max_len_id = len( "Id ")
      if len( "School" ) > max_len_school_name:
        max_len_school_name = len( "School" )
      if len( "Name" ) > max_len_name:
        max_len_name = len( "Name" )

      print( self._cf.bold_green( indent + "Id" + " " * (max_len_id - 2) + space + wall + " " + "School" + " " * (max_len_school_name - 7) + space + wall + " " + "Name" + " " * (max_len_name - 4) ) )
      print( " " * 2 + "-" * (3 * len( space ) + max_len_id + max_len_school_name + max_len_name + 4 ) )

      for term in terms:
        sys.stdout.write( indent + str( term.Id ) + " " * (max_len_id - len( str( term.Id ) ) ) + space + wall + " " )
        print( term.School.Name + " " * (max_len_school_name - len( term.School.Name ) ) + space + wall + " " + term.Name )
    else:
      print( self._cf.bold_green( "There are no terms" ) )

  def PrintSubjectTable( self, subjects ):
    indent = " " * 4
    space  = " " * 6
    wall   = "|"
    if len( subjects ) > 0:
      max_len_id          = len( max( [str( s.Id ) for s in subjects],   key = len ) )
      max_len_name        = len( max( [s.Name for s in subjects],        key = len ) )
      max_len_shortcut    = len( max( [s.Shortcut for s in subjects],    key = len ) )

      if len( "Id" ) > max_len_id:
        max_len_id = len( "Id ")
      if len( "Name" ) > max_len_name:
        max_len_name = len( "Name" )
      if len( "Shortcut" ) > max_len_shortcut:
        max_len_shortcut = len( "Shortcut" )

      print( self._cf.bold_green( indent + "Id" + " " * (max_len_id - 2) + space + wall + " " + "Name" + " " * (max_len_name - 4) + space + wall + " " + "Shortcut" ) )
      print( " " * 2 + "-" * (3 * len( space ) + max_len_id + max_len_name + max_len_shortcut + 4 ) )

      for subject in subjects:
        sys.stdout.write( indent + str( subject.Id ) + " " * (max_len_id - len( str( subject.Id ) ) ) + space + wall + " " )
        print( subject.Name + " " * (max_len_name - len( subject.Name ) ) + space + wall + " " + subject.Shortcut )
    else:
      print( self._cf.bold_green( "There are no subjects" ) )

  def cmd_cd( self, item, args, rawline ):
    """[location|..]||change current location. You can go into schools, terms and subjects"""
    location, value = self.GetSchoolLocation( )
    args = args.strip( )
    if args == "" or args == "/":
      CLI.SetLocation( self, "/", "root" )
    elif args == "..":
      # FIXME: Go back does not work yet
      location = CLI.ParseLocation( self )
      back_location = location[1:len( location ) - 2]
      #if back_location[len( back_location ) - 1] != "/":
      back_location.append( "/" )
      CLI.SetLocation( self, "/".join( back_location ), "root" )
    elif location == "root":
      schools = School.GetSchools( self._connection )
      school_names = [s.Name for s in schools]
      if args in school_names:
        CLI.SetLocation( self, "/" + args + "/", School.GetSchoolByName( self._connection, args ) )
      else:
        print( self._cf.bold_red( "Could not change location because the school with the name `{}` could not be found".format( args ) ) )
    elif location == "school":
      terms = Term.GetTermsBySchool( self._connection, CLI.GetLocationValue( self ) )
      term_names = [t.Name for t in terms]
      if args in term_names:
        CLI.SetLocation( self, self._location + args + "/", Term.GetTermByName( self._connection, args ) )
      else:
        print( self._cf.bold_red( "Could not change location because the term with the name `{}` could not be found in school `{}`".format( args, CLI.GetLocationValue( self ).Name ) ) )
    elif location == "term":
      subjects = Subject.GetSubjectsByTerm( self._connection, CLI.GetLocationValue( self ) )
      subject_shortcuts = [s.Shortcut for s in subjects]
      if args in subject_shortcuts:
        CLI.SetLocation( self, self._location + args + "/", Termsubject.GetTermsubjectByTermAndSubject( self._connection, CLI.GetLocationValue( self ), Subject.GetSubjectByShortcut( self._connection, args ) ) )
      else:
        print( self._cf.bold_red( "Could not change location because the subject with the shortcut `{}` could not be found in term `{}`".format( args, CLI.GetLocationValue( self ).Name ) ) )

    location, value = self.GetSchoolLocation( )
    CLI.SetItemsEnabled( self, False )
    if location == "root":
      CLI.SetItemsEnabledByCategory( self, "school" )
    elif location == "school":
      CLI.SetItemsEnabledByCategory( self, "term" )
    elif location == "term":
      CLI.SetItemsEnabledByCategory( self, "subject" )
    elif location == "subject":
      CLI.SetItemsEnabledByCategory( self, "mark" )
    self._UpdateCDCommand( )

  def cmd_ls( self, item, args, rawline ):
    """list the current location content like all schools or subjects"""
    location, value = self.GetSchoolLocation( )
    if location == "root":
      self.PrintSchoolTable( School.GetSchools( self._connection ) )
    elif location == "school":
      self.PrintTermTable( Term.GetTermsBySchool( self._connection, CLI.GetLocationValue( self ) ) )
    elif location == "term":
      self.PrintSubjectTable( Subject.GetSubjectsByTerm( self._connection, CLI.GetLocationValue( self ) ) )

  def cmd_pwd( self, item, args, rawline ):
    """print the working directory ( location )"""
    print( self._location )

  def cmd_school( self, item, args, rawline ):
    """<add|remove>||add or remove a school"""
    sys.stdout.write( "Usage:" )
    CLI.HelpScreen( self, None, "school" )

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
          print( self._cf.white( "There is no school to remove" ) )
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
    """<add|remove>||add or remove a term"""
    sys.stdout.write( "Usage:" )
    CLI.HelpScreen( self, None, "term" )

  def cmd_term_add( self, item, args, rawline ):
    """-n <name>|-i||add a new term. Argument -n is to pass a name and -i for interactive mode"""
    parser = argparse.ArgumentParser( prog = "term add", description = self.cmd_term_add.__doc__.split( "||" )[1] )
    parser.add_argument( "-n", "--name", help = "set the name of the new term" )
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
        term = Term( self._connection )
        term.School = CLI.GetLocationValue( self )
        term.Name   = name
        if term.Insert( ):
          print( self._cf.bold_green( "Term with name `{}` has been successfully saved for school `{}`!".format( name, term.School.Name ) ) )
          self._UpdateCDCommand( )
        else:
          print( self._cf.bold_red( "An error occured during the insert action of term with name `{}`".format( name ) ) )
    except SystemExit:       # Do not exit cli if an error occured in parse_args
      pass

  def cmd_term_remove( self, item, args, rawline ):
    """-s <id>|-i||remove a term by id or in interactive mode"""
    parser = argparse.ArgumentParser( prog = "term remove", description = self.cmd_term_remove.__doc__.split( "||" )[1] )
    parser.add_argument( "-s", "--id", help = "set the id of the term to remove" )
    parser.add_argument( "-i", "--interactive", action = "store_true", help = "use the interactive mode" )

    try:
      id = None
      parsed_args = parser.parse_args( args.split( " " ) )
      terms = Term.GetTermsBySchool( self._connection, CLI.GetLocationValue( self ) )
      available_ids = [str( t.Id ) for t in terms]
      if parsed_args.interactive:
        if len( terms ) == 0:
          print( self._cf.white( "There is no term to remove" ) )
        else:
          print( self._cf.bold_green( "Terms you can remove:" ) )
          self.PrintTermTable( terms )
          try:
            id = input( "Enter id of the term to be removed: " )
          except KeyboardInterrupt:
            print( "" ) # To break down prompt to a new line
      elif parsed_args.id is not None and parsed_args.id != "":
        id = parsed_args.id

      if id is not None:
        if id in available_ids:
          term = [t for t in terms if str( t.Id ) == id][0]
          if term.Delete( ):
            print( self._cf.bold_green( "Term with id `{}` has been successfully removed".format( id ) ) )
            self._UpdateCDCommand( )
          else:
            print( self._cf.bold_red( "An error occured during delete action of term with id `{}`".format( id ) ) )
        else:
          print( self._cf.bold_red( "Term with id `{}` does not exist".format( id ) ) )
    except SystemExit:       # Do not exit cli if an error occured in parse_args
      pass

  def cmd_subject( self, item, args, rawline ):
    """<add|remove>|<link>|<unlink>||add, remove, link or unlink a subject"""
    sys.stdout.write( "Usage:" )
    CLI.HelpScreen( self, None, "subject" )

  def cmd_subject_add( self, item, args, rawline ):
    """-n <name> -s <shortcut>|-i||add a new subject. Argument -n is to pass a name and -s to pass a shortcut and -i for interactive mode"""
    parser = argparse.ArgumentParser( prog = "subject add", description = self.cmd_subject_add.__doc__.split( "||" )[1] )
    parser.add_argument( "-n", "--name", help = "set the name of the new subject" )
    parser.add_argument( "-s", "--shortcut", help = "set the shortcut of the new subject" )
    parser.add_argument( "-i", "--interactive", action = "store_true", help = "use the interactive mode" )

    try:
      parsed_args = parser.parse_args( args.split( " " ) )
      name     = ""
      shortcut = ""
      save     = True
      if parsed_args.interactive:
        try:
          while name == "":
            name = input( "Name: " )
          while shortcut == "":
            shortcut = input( "Shortcut: " )
          save = input( "Do you want to save ([y]/n)? " )
          save = (save == "y" or save == "")
        except KeyboardInterrupt:
          save = False
          print( "" ) # To break down prompt to a new line
      elif parsed_args.name is not None and parsed_args.name != "" and parsed_args.shortcut is not None and parsed_args.shortcut != "":
        name     = parsed_args.name
        shortcut = parsed_args.shortcut
      else:
        save = False
      if save:
        subject          = Subject( self._connection )
        subject.Name     = name
        subject.Shortcut = shortcut
        if subject.Insert( ):
          print( self._cf.bold_green( "Subject with name `{} ({})` has been successfully saved!".format( name, shortcut ) ) )
          print( self._cf.white( "If you want to link this subject with the current term you have to execute `subject link`" ) )
          self._UpdateCDCommand( )
        else:
          print( self._cf.bold_red( "An error occured during the insert action of subject with name `{}`".format( name ) ) )
      elif parsed_args.name is None or parsed_args.name == "" or parsed_args.shortcut is None or parsed_args.shortcut == "":
        print( self._cf.bold_red( "You have to pass a name with -n and a shortcut with -s to save a subject else you can choose -i for interactive mode" ) )
    except SystemExit:       # Do not exit cli if an error occured in parse_args
      pass

  def cmd_subject_remove( self, item, args, rawline ):
    """-s <id>|-i||remove a subject by id or in interactive mode"""
    parser = argparse.ArgumentParser( prog = "subject remove", description = self.cmd_subject_remove.__doc__.split( "||" )[1] )
    parser.add_argument( "-s", "--id", help = "set the id of the subject to remove" )
    parser.add_argument( "-i", "--interactive", action = "store_true", help = "use the interactive mode" )

    try:
      id = None
      parsed_args = parser.parse_args( args.split( " " ) )
      subjects = Subject.GetSubjects( self._connection )
      available_ids = [str( s.Id ) for s in subjects]
      if parsed_args.interactive:
        if len( subjects ) == 0:
          print( self._cf.white( "There are no subjects to remove" ) )
        else:
          print( self._cf.bold_green( "Subjects you can remove:" ) )
          self.PrintSubjectTable( subjects )
          try:
            id = input( "Enter id of the subject to be removed: " )
          except KeyboardInterrupt:
            print( "" ) # To break down prompt to a new line
      elif parsed_args.id is not None and parsed_args.id != "":
        id = parsed_args.id

      if id is not None:
        if id in available_ids:
          subject = [s for s in subjects if str( s.Id ) == id][0]
          if subject.Delete( ):
            print( self._cf.bold_green( "Subject with id `{}` has been successfully removed".format( id ) ) )
            self._UpdateCDCommand( )
          else:
            print( self._cf.bold_red( "An error occured during delete action of subject with id `{}`".format( id ) ) )
        else:
          print( self._cf.bold_red( "Subject with id `{}` does not exist".format( id ) ) )
    except SystemExit:       # Do not exit cli if an error occured in parse_args
      pass

  def cmd_subject_link( self, item, args, rawline ):
    """-s <subject>|-i||link an existing subject with the current term. Pass -s for the subject id or -i for interactive mode"""
    parser = argparse.ArgumentParser( prog = "subject add", description = self.cmd_subject_add.__doc__.split( "||" )[1] )
    parser.add_argument( "-s", "--subject", help = "set the subject to link with the current erm" )
    parser.add_argument( "-i", "--interactive", action = "store_true", help = "use the interactive mode" )

    try:
      parsed_args   = parser.parse_args( args.split( " " ) )
      subjects      = Subject.GetSubjects( self._connection )
      available_ids = [str( s.Id ) for s in subjects]
      subjectid     = None
      save          = True
      if parsed_args.interactive:
        try:
          if len( subjects ) == 0:
            print( self._cf.white( "There are no subjects you can link with the current term" ) )
          else:
            print( self._cf.bold_green( "Subjects you can link: ") )
            self.PrintSubjectTable( subjects )
            subjectid = input( "Enter id of the subject to link: " )
            save      = input( "Do you want to save ([y]/n)? " )
            save      = (save == "y" or save == "")
        except KeyboardInterrupt:
          save = False
          print( "" ) # To break down prompt to a new line
      elif parsed_args.subject is not None and parsed_args.subject != "":
        subjectid = parsed_args.subject
      else:
        save = False
      if save:
        if subjectid in available_ids:
          termsubject         = Termsubject( self._connection )
          termsubject.Subject = Subject.GetSubjectById( self._connection, subjectid )
          termsubject.Term    = CLI.GetLocationValue( self )
          if termsubject.Insert( ):
            print( self._cf.bold_green( "Subject with name `{} ({})` has been successfully linked to term `{}`!".format( termsubject.Subject.Name, termsubject.Subject.Shortcut, termsubject.Term.Name ) ) )
            self._UpdateCDCommand( )
          else:
            print( self._cf.bold_red( "An error occured during the linking of subject with id `{}` and the current term".format( subjectid ) ) )
        else:
          print( self._cf.bold_red( "Subject with id `{}` does not exist".format( subjectid ) ) )
    except SystemExit:       # Do not exit cli if an error occured in parse_args
      pass

  def cmd_subject_unlink( self, item, args, rawline ):
    """-s <id>|-i||unlink a subject with the current term by id or in interactive mode"""
    parser = argparse.ArgumentParser( prog = "subject unlink", description = self.cmd_subject_unlink.__doc__.split( "||" )[1] )
    parser.add_argument( "-s", "--id", help = "set the id of the subject to unlink" )
    parser.add_argument( "-i", "--interactive", action = "store_true", help = "use the interactive mode" )

    try:
      id = None
      parsed_args = parser.parse_args( args.split( " " ) )
      subjects = Subject.GetSubjectsByTerm( self._connection, CLI.GetLocationValue( self ) )
      available_ids = [str( s.Id ) for s in subjects]
      if parsed_args.interactive:
        if len( subjects ) == 0:
          print( self._cf.white( "There are no subjects to unlink" ) )
        else:
          print( self._cf.bold_green( "Subjects you can unlink:" ) )
          self.PrintSubjectTable( subjects )
          try:
            id = input( "Enter id of the subject to be unlinked: " )
          except KeyboardInterrupt:
            print( "" ) # To break down prompt to a new line
      elif parsed_args.id is not None and parsed_args.id != "":
        id = parsed_args.id

      if id is not None:
        if id in available_ids:
          subject = [s for s in subjects if str( s.Id ) == id][0]
          term    = CLI.GetLocationValue( self )
          termsubject = Termsubject.GetTermsubjectByTermAndSubject( self._connection, term, subject )
          if termsubject.Delete( ):
            print( self._cf.bold_green( "Subject with id `{}` has been successfully unlinked".format( id ) ) )
            self._UpdateCDCommand( )
          else:
            print( self._cf.bold_red( "An error occured during unlinking of subject with id `{}`".format( id ) ) )
        else:
          print( self._cf.bold_red( "Subject with id `{}` does not exist".format( id ) ) )
    except SystemExit:       # Do not exit cli if an error occured in parse_args
      pass

  def cmd_mark( self, item, args, rawline ):
    pass

  def cmd_mark_add( self, item, args, rawline ):
    pass

  def cmd_mark_remove( self, item, args, rawline ):
    pass

  def cmd_exit( self, item, args, rawline ):
    """exit from the schoolcli"""
    y = input( "Do you really want to exit ([y]/n)? " )
    if y == "y" or y == "":
      CLI.Stop( self )
