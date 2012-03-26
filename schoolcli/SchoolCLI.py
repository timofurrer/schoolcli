#''!/usr/bin/python3.2

import os
import sqlite3
import argparse
import time

from CLI         import *
from School      import *
from Term        import *
from Subject     import *
from Termsubject import *
from Mark        import *

class SchoolCLI( CLI ):
  _connection = None

  _database   = None

  def __init__( self, prompt = "School:{}> ", database = path.join( os.getenv( "HOME" ), ".schoolcli.db" )):
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
    CLI.RegisterItem( self, CLIItem( "exit", self.cmd_exit, category = "default", subitems = [] ))
    CLI.RegisterItem( self, CLIItem( "cd", self.cmd_cd, category = "default", subitems = [] ))
    CLI.RegisterItem( self, CLIItem( "ls", self.cmd_ls, category = "default", subitems = [] ))
    CLI.RegisterItem( self, CLIItem( "pwd", self.cmd_pwd, category = "default", subitems = [] ))
    CLI.RegisterItem( self, CLIItem( "avg", self.cmd_avg, category = "default", subitems = [] ))
    self._UpdateCDCommand( )

  def AddSchoolCommands( self ):
    school = CLIItem( "school", self.cmd_school, category = "school", subitems = [] )
    school.AppendItem( CLIItem( "add", self.cmd_school_add, category = "school" ))
    school.AppendItem( CLIItem( "remove", self.cmd_school_remove, category = "school" ))
    CLI.RegisterItem( self, school )

  def AddTermCommands( self ):
    term = CLIItem( "term", self.cmd_term, category = "term", subitems = [] )
    term.AppendItem( CLIItem( "add", self.cmd_term_add, category = "term" ))
    term.AppendItem( CLIItem( "remove", self.cmd_term_remove, category = "term" ))
    CLI.RegisterItem( self, term )

  def AddSubjectCommands( self ):
    subject = CLIItem( "subject", self.cmd_subject, category = "subject", subitems = [] )
    subject.AppendItem( CLIItem( "add", self.cmd_subject_add, category = "subject" ))
    subject.AppendItem( CLIItem( "remove", self.cmd_subject_remove, category = "subject" ))
    subject.AppendItem( CLIItem( "link", self.cmd_subject_link, category = "subject" ))
    subject.AppendItem( CLIItem( "unlink", self.cmd_subject_unlink, category = "subject" ))
    CLI.RegisterItem( self, subject )

  def AddMarkCommands( self ):
    mark = CLIItem( "mark", self.cmd_mark, category = "mark", subitems = [] )
    mark.AppendItem( CLIItem( "add", self.cmd_mark_add, category = "mark" ))
    mark.AppendItem( CLIItem( "remove", self.cmd_mark_remove, category = "mark" ))
    CLI.RegisterItem( self, mark )

  def _UpdateCDCommand( self ):
    item            = CLI.GetItemByName( self, "cd" )
    if item is not None:
      index = self._ls.GetHierarchyIndex( )
      item.ClearItems( )
      item.AppendItem( CLIItem( "/", value = "/", category = "default" ))
      item.AppendItem( CLIItem( "..", value = "..", category = "default" ))

      cds = []
      schools = [s for s in School.GetSchools( self._connection )]
      for school in schools:
        schoolitem = CLIItem( school.Name, value = school.Name, split_char = "/", category = "default", subitems = [] )
        terms = [t for t in Term.GetTermsBySchool( self._connection, school )]
        for term in terms:
          termitem = CLIItem( term.Name, value = term.Name, split_char = "/", category = "default", subitems = [] )
          subjects = [s for s in Subject.GetSubjectsByTerm( self._connection, term )]
          for subject in subjects:
            subjectitem = CLIItem( subject.Shortcut, value = subject.Shortcut, split_char = "/", category = "default" )
            termitem.AppendItem( subjectitem )
          schoolitem.AppendItem( termitem )
        cds.append( schoolitem )

      if index == 0:
        for cd in cds:
          item.AppendItem( cd )
      elif index == 1:
        for cd in [i for i in cds if i.GetName( ) == self._ls.GetCurrentLocationValue( ).Name]:
          for subcd in cd.GetSubitems( ):
            item.AppendItem( subcd )
      elif index == 2:
        for cd in [i for i in cds if i.GetName( ) == self._ls.GetLocationValueAt( 0 ).Name]:
          for subcd in [i for i in cd.GetSubitems( ) if i.GetName( ) == self._ls.GetLocationValueAt( 1 ).Name]:
            for subsubcd in subcd.GetSubitems( ):
              item.AppendItem( subsubcd )

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

    print( Colorful.bold_green( "Connected to valid database at path `{}`".format( self._database )))

  def PrintSchoolTable( self, schools ):
    indent = " " * 4
    space  = " " * 6
    wall   = "|"
    if len( schools ) > 0:
      max_len_id   = len( max( [str( s.Id ) for s in schools], key = len ))
      max_len_name = len( max( [s.Name for s in schools],      key = len ))

      if len( "Id" ) > max_len_id:     max_len_id = len( "Id" )
      if len( "Name" ) > max_len_name: max_len_name = len( "Name" )

      print( indent + Colorful.bold_green( "Id" ) + " " * (max_len_id - 2) + space + wall + " " + Colorful.bold_green( "Name" ))
      print( " " * 2 + "-" * (2 * len( space ) + max_len_id + max_len_name + 2 ))

      for school in schools:
        print( indent + str( school.Id ) + " " * (max_len_id - len( str( school.Id ))) + space + wall + " " + school.Name )
    else:
      print( Colorful.bold_green( "There are no schools" ))

  def PrintTermTable( self, terms ):
    indent = " " * 4
    space  = " " * 6
    wall   = "|"
    if len( terms ) > 0:
      max_len_id          = len( max( [str( t.Id ) for t in terms],   key = len ))
      max_len_school_name = len( max( [t.School.Name for t in terms], key = len ))
      max_len_name        = len( max( [t.Name for t in terms],        key = len ))

      if len( "Id" ) > max_len_id:              max_len_id = len( "Id")
      if len( "School" ) > max_len_school_name: max_len_school_name = len( "School" )
      if len( "Name" ) > max_len_name:          max_len_name = len( "Name" )

      print( Colorful.bold_green( indent + "Id" + " " * (max_len_id - 2) + space + wall + " " + "School" + " " * (max_len_school_name - 7) + space + wall + " " + "Name" + " " * (max_len_name - 4)))
      print( " " * 2 + "-" * (3 * len( space ) + max_len_id + max_len_school_name + max_len_name + 4 ))

      for term in terms:
        sys.stdout.write( indent + str( term.Id ) + " " * (max_len_id - len( str( term.Id ))) + space + wall + " " )
        print( term.School.Name + " " * (max_len_school_name - len( term.School.Name )) + space + wall + " " + term.Name )
    else:
      print( Colorful.bold_green( "There are no terms" ))

  def PrintSubjectTable( self, subjects ):
    indent = " " * 4
    space  = " " * 6
    wall   = "|"
    if len( subjects ) > 0:
      max_len_id          = len( max( [str( s.Id ) for s in subjects],   key = len ))
      max_len_name        = len( max( [s.Name for s in subjects],        key = len ))
      max_len_shortcut    = len( max( [s.Shortcut for s in subjects],    key = len ))

      if len( "Id" ) > max_len_id:             max_len_id = len( "Id")
      if len( "Name" ) > max_len_name:         max_len_name = len( "Name" )
      if len( "Shortcut" ) > max_len_shortcut: max_len_shortcut = len( "Shortcut" )

      print( Colorful.bold_green( indent + "Id" + " " * (max_len_id - 2) + space + wall + " " + "Name" + " " * (max_len_name - 4) + space + wall + " " + "Shortcut" ))
      print( " " * 2 + "-" * (3 * len( space ) + max_len_id + max_len_name + max_len_shortcut + 4 ))

      for subject in subjects:
        sys.stdout.write( indent + str( subject.Id ) + " " * (max_len_id - len( str( subject.Id ))) + space + wall + " " )
        print( subject.Name + " " * (max_len_name - len( subject.Name )) + space + wall + " " + subject.Shortcut )
    else:
      print( Colorful.bold_green( "There are no subjects" ))

  def PrintMarkTable( self, marks ):
    indent = " " * 4
    space  = " " * 6
    wall   = "|"
    if len( marks ) > 0:
      max_len_id          = len( max( [str( m.Id ) for m in marks],        key = len ))
      max_len_mark        = len( max( [str( m.Mark ) for m in marks],      key = len ))
      max_len_points      = len( max( [str( m.Points ) for m in marks],    key = len ))
      max_len_max_points  = len( max( [str( m.MaxPoints ) for m in marks], key = len ))
      max_len_valuation   = len( max( [str( m.Valuation ) for m in marks], key = len ))
      max_len_avarage     = len( max( [str( m.Avarage ) for m in marks],   key = len ))
      max_len_date        = len( max( [str( m.Date ) for m in marks],      key = len ))

      if len( "Id" ) > max_len_id:                 max_len_id = len( "Id")
      if len( "Mark" ) > max_len_mark:             max_len_mark = len( "Mark")
      if len( "Points" ) > max_len_points:         max_len_points = len( "Points")
      if len( "Max Points" ) > max_len_max_points: max_len_max_points = len( "Max Points")
      if len( "Valuation" ) > max_len_valuation:   max_len_valuation = len( "Valuation")
      if len( "Avarage" ) > max_len_avarage:       max_len_avarage = len( "Avarage")
      if len( "Date" ) > max_len_date:             max_len_date = len( "Date")

      sys.stdout.write( Colorful.bold_green( indent + "Id" + " " * (max_len_id - 2) + space + wall + " " + "Mark" + " " * (max_len_mark - 4) + space + wall + " " ))
      sys.stdout.write( Colorful.bold_green( "Points" + " " * (max_len_points - 6) + space + wall + " " + "Max Points" + " " * (max_len_max_points - 10) + space + wall + " " ))
      print( Colorful.bold_green( "Valuation" + " " * (max_len_valuation - 9) + space + wall + " " + "Avarage" + " " * (max_len_avarage - 7) + space + wall + " " + "Date" ))
      print( " " * 2 + "-" * (6 * len( space ) + max_len_id + max_len_mark + max_len_points + max_len_max_points + max_len_valuation + max_len_avarage + max_len_date + 6 * len( wall ) + 12 * len( " " )))

      for mark in marks:
        if mark.Mark >= 5.5:
          mark_output = Colorful.bold_green( str( mark.Mark )) #FIXME: Can Colorful "underline_and_bold_green ?!
        elif mark.Mark >= 5:
          mark_output = Colorful.bold_green( str( mark.Mark ))
        elif mark.Mark >= 4:
          mark_output = Colorful.green( str( mark.Mark ))
        elif mark.Mark >= 3:
          mark_output = Colorful.red( str( mark.Mark ))
        else:
          mark_output = Colorful.bold_red( str( mark.Mark ))

        points_output     = str( mark.Points ) if mark.Points             != "" else Colorful.white( "---" )
        points_len        = len( str( mark.Points )) if mark.Points       != "" else 3
        max_points_output = str( mark.MaxPoints ) if mark.MaxPoints       != "" else Colorful.white( "---" )
        max_points_len    = len( str( mark.MaxPoints )) if mark.MaxPoints != "" else 3
        valuation_output  = str( mark.Valuation ) if mark.Valuation       != "" else Colorful.white( "---" )
        valuation_len     = len( str( mark.Valuation )) if mark.Valuation != "" else 3
        avarage_output    = str( mark.Avarage ) if mark.Avarage           != "" else Colorful.white( "---" )
        avarage_len       = len( str( mark.Avarage )) if mark.Avarage     != "" else 3
        date_output       = str( mark.Date ) if mark.Date                 != "" else Colorful.white( "---" )
        date_len          = len( str( mark.Date )) if mark.Date           != "" else 3

        sys.stdout.write( indent + str( mark.Id ) + " " * (max_len_id - len( str( mark.Id ))) + space + wall + " " )
        sys.stdout.write( mark_output + " " * (max_len_mark - len( str( mark.Mark))) + space + wall + " " )
        sys.stdout.write( points_output + " " * (max_len_points - points_len) + space + wall + " " )
        sys.stdout.write( max_points_output + " " * (max_len_max_points - max_points_len) + space + wall + " " )
        sys.stdout.write( valuation_output + " " * (max_len_valuation - valuation_len) + space + wall + " " )
        sys.stdout.write( avarage_output + " " * (max_len_avarage - avarage_len) + space + wall + " " )
        print( date_output + " " * (max_len_date - date_len))
    else:
      print( Colorful.bold_green( "There are no marks" ))

  def cmd_cd( self, item, args, rawline ):
    """[location|..]||change current location. You can go into schools, terms and subjects"""
    index = self._ls.GetHierarchyIndex( )
    args = args.strip( )
    if args == "" or args == "/":
      self._ls.GoToRoot( )
    elif args == "..":
      self._ls.GoOneBack( )
    else:
      if args.split( self._ls.Splitter )[0] == "/":
        self._ls.GoToRoot( )
      stations = [s for s in args.split( self._ls.Splitter ) if s != ""]
      for station in stations:
        if station == "..":
          self._ls.GoOneBack( )
        elif station == ".":
          pass
        else:
          index = self._ls.GetHierarchyIndex( )
          if index == 0:
            school = School.GetSchoolByName( self._connection, station )
            if school is not None:
              self._ls.AppendLocation( station, school )
            else:
              print( Colorful.bold_red( "Could not change location because the school with the name `{}` could not be found".format( station )))
          elif index == 1:
            term = Term.GetTermByName( self._connection, station )
            if term is not None:
              self._ls.AppendLocation( station, term )
            else:
              print( Colorful.bold_red( "Could not change location because the term with the name `{}` could not be found".format( args )))
          elif index == 2:
            termsubject = Termsubject.GetTermsubjectByTermAndSubject( self._connection, self._ls.GetCurrentLocationValue( ), Subject.GetSubjectByShortcut( self._connection, station ))
            if termsubject is not None:
              self._ls.AppendLocation( station, termsubject )
            else:
              print( Colorful.bold_red( "Could not change location because the subject with the shortcut `{}` could not be found".format( args )))

    index = self._ls.GetHierarchyIndex( )
    CLI.SetItemsEnabled( self, False )
    if index == 0:
      CLI.SetItemsEnabledByCategory( self, "school" )
    elif index == 1:
      CLI.SetItemsEnabledByCategory( self, "term" )
    elif index == 2:
      CLI.SetItemsEnabledByCategory( self, "subject" )
    elif index == 3:
      CLI.SetItemsEnabledByCategory( self, "mark" )
    self._UpdateCDCommand( )

  def cmd_ls( self, item, args, rawline ):
    """list the current location content like all schools or subjects"""
    index = self._ls.GetHierarchyIndex( )
    if index == 0:
      self.PrintSchoolTable( School.GetSchools( self._connection ))
    elif index == 1:
      self.PrintTermTable( Term.GetTermsBySchool( self._connection, self._ls.GetCurrentLocationValue( )))
    elif index == 2:
      self.PrintSubjectTable( Subject.GetSubjectsByTerm( self._connection, self._ls.GetCurrentLocationValue( )))
    elif index == 3:
      self.PrintMarkTable( Mark.GetMarksByTermsubject( self._connection, self._ls.GetCurrentLocationValue( )))

  def cmd_pwd( self, item, args, rawline ):
    """print the working directory ( location )"""
    print( self._ls.GetLocationAsText( ))

  def cmd_avg( self, item, args, rawline ):
    """calculate the avarage of the current location"""
    index = self._ls.GetHierarchyIndex( )
    indent = " " * 4
    space  = " " * 6
    wall   = "|"

    rows  = []

    if index == 0:
      rows.append( { "key" : "Schools", "value" : "Avarage" } )
      for school in School.GetSchools( self._connection ):
        avarage     = 0.0
        valuation   = 0.0
        for term in Term.GetTermsBySchool( self._connection, school ):
          for mark in Mark.GetMarksByTerm( self._connection, term ):
            mark_tmp      = float( mark.Mark )
            if mark.Valuation is not None and mark.Valuation != "":
              valuation_tmp = mark.Valuation
            else:
              valuation_tmp = 100.0

            avarage   += mark_tmp * valuation_tmp
            valuation += valuation_tmp
        elem = {}
        elem["key"] = school.Name
        if valuation == 0:
          elem["value"] = 0
        else:
          elem["value"] = avarage / valuation
        rows.append( elem )

    max_len_first_col  = len( max( [d["key"] for d in rows],          key = len ))
    max_len_second_col = len( max( [str( d["value"] ) for d in rows], key = len ))

    print( indent + Colorful.bold_green( rows[0]["key"] ) + " " * (max_len_first_col - len( rows[0]["key"] )) + space + wall + " " + Colorful.bold_green( rows[0]["value"] ))
    print( " " * 2 + "-" * (max_len_first_col + max_len_second_col + len( space ) + len( wall ) + 1 + 4 ))

    for row in rows[1:]:
      print( indent + row["key"] + " " * (max_len_first_col - len( row["key"] )) + space + wall + " " + str( row["value"] ) + " " * (max_len_second_col - len( str( row["value"] ))))

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
      parsed_args = parser.parse_args( args.split( " " ))
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
          print( Colorful.bold_green( "School with name `{}` has been successfully saved!".format( name )))
          self._UpdateCDCommand( )
        else:
          print( Colorful.bold_red( "An error occured during the insert action of school with name `{}`".format( name )))
    except SystemExit:       # Do not exit cli if an error occured in parse_args
      pass

  def cmd_school_remove( self, item, args, rawline ):
    """-s <id>|-i||remove a school by id or in interactive mode"""
    parser = argparse.ArgumentParser( prog = "school remove", description = self.cmd_school_remove.__doc__.split( "||" )[1] )
    parser.add_argument( "-s", "--id", help = "set the id of the school to remove" )
    parser.add_argument( "-i", "--interactive", action = "store_true", help = "use the interactive mode" )

    try:
      id = None
      parsed_args = parser.parse_args( args.split( " " ))
      schools = School.GetSchools( self._connection )
      available_ids = [str( s.Id ) for s in schools]
      if parsed_args.interactive:
        if len( schools ) == 0:
          print( Colorful.white( "There is no school to remove" ))
        else:
          print( Colorful.bold_green( "Schools you can remove:" ))
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
            print( Colorful.bold_green( "School with id `{}` has been successfully removed".format( id )))
            self._UpdateCDCommand( )
          else:
            print( Colorful.bold_red( "An error occured during delete action of school with id `{}`".format( id )))
        else:
          print( Colorful.bold_red( "School with id `{}` does not exist".format( id )))
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
      parsed_args = parser.parse_args( args.split( " " ))
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
        term.School = self._ls.GetCurrentLocationValue( )
        term.Name   = name
        if term.Insert( ):
          print( Colorful.bold_green( "Term with name `{}` has been successfully saved for school `{}`!".format( name, term.School.Name )))
          self._UpdateCDCommand( )
        else:
          print( Colorful.bold_red( "An error occured during the insert action of term with name `{}`".format( name )))
    except SystemExit:       # Do not exit cli if an error occured in parse_args
      pass

  def cmd_term_remove( self, item, args, rawline ):
    """-s <id>|-i||remove a term by id or in interactive mode"""
    parser = argparse.ArgumentParser( prog = "term remove", description = self.cmd_term_remove.__doc__.split( "||" )[1] )
    parser.add_argument( "-s", "--id", help = "set the id of the term to remove" )
    parser.add_argument( "-i", "--interactive", action = "store_true", help = "use the interactive mode" )

    try:
      id = None
      parsed_args = parser.parse_args( args.split( " " ))
      terms = Term.GetTermsBySchool( self._connection, self._ls.GetCurrentLocationValue( ))
      available_ids = [str( t.Id ) for t in terms]
      if parsed_args.interactive:
        if len( terms ) == 0:
          print( Colorful.white( "There is no term to remove" ))
        else:
          print( Colorful.bold_green( "Terms you can remove:" ))
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
            print( Colorful.bold_green( "Term with id `{}` has been successfully removed".format( id )))
            self._UpdateCDCommand( )
          else:
            print( Colorful.bold_red( "An error occured during delete action of term with id `{}`".format( id )))
        else:
          print( Colorful.bold_red( "Term with id `{}` does not exist".format( id )))
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
      parsed_args = parser.parse_args( args.split( " " ))
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
          print( Colorful.bold_green( "Subject with name `{} ({})` has been successfully saved!".format( name, shortcut )))
          print( Colorful.white( "If you want to link this subject with the current term you have to execute `subject link`" ))
          self._UpdateCDCommand( )
        else:
          print( Colorful.bold_red( "An error occured during the insert action of subject with name `{}`".format( name )))
      elif parsed_args.name is None or parsed_args.name == "" or parsed_args.shortcut is None or parsed_args.shortcut == "":
        print( Colorful.bold_red( "You have to pass a name with -n and a shortcut with -s to save a subject else you can choose -i for interactive mode" ))
    except SystemExit:       # Do not exit cli if an error occured in parse_args
      pass

  def cmd_subject_remove( self, item, args, rawline ):
    """-s <id>|-i||remove a subject by id or in interactive mode"""
    parser = argparse.ArgumentParser( prog = "subject remove", description = self.cmd_subject_remove.__doc__.split( "||" )[1] )
    parser.add_argument( "-s", "--id", help = "set the id of the subject to remove" )
    parser.add_argument( "-i", "--interactive", action = "store_true", help = "use the interactive mode" )

    try:
      id = None
      parsed_args = parser.parse_args( args.split( " " ))
      subjects = Subject.GetSubjects( self._connection )
      available_ids = [str( s.Id ) for s in subjects]
      if parsed_args.interactive:
        if len( subjects ) == 0:
          print( Colorful.white( "There are no subjects to remove" ))
        else:
          print( Colorful.bold_green( "Subjects you can remove:" ))
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
            print( Colorful.bold_green( "Subject with id `{}` has been successfully removed".format( id )))
            self._UpdateCDCommand( )
          else:
            print( Colorful.bold_red( "An error occured during delete action of subject with id `{}`".format( id )))
        else:
          print( Colorful.bold_red( "Subject with id `{}` does not exist".format( id )))
    except SystemExit:       # Do not exit cli if an error occured in parse_args
      pass

  def cmd_subject_link( self, item, args, rawline ):
    """-s <subject>|-i||link an existing subject with the current term. Pass -s for the subject id or -i for interactive mode"""
    parser = argparse.ArgumentParser( prog = "subject add", description = self.cmd_subject_add.__doc__.split( "||" )[1] )
    parser.add_argument( "-s", "--subject", help = "set the subject to link with the current erm" )
    parser.add_argument( "-i", "--interactive", action = "store_true", help = "use the interactive mode" )

    try:
      parsed_args   = parser.parse_args( args.split( " " ))
      subjects      = Subject.GetSubjects( self._connection )
      available_ids = [str( s.Id ) for s in subjects]
      subjectid     = None
      save          = True
      if parsed_args.interactive:
        try:
          if len( subjects ) == 0:
            print( Colorful.white( "There are no subjects you can link with the current term" ))
          else:
            print( Colorful.bold_green( "Subjects you can link: "))
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
          termsubject.Term    = self._ls.GetCurrentLocationValue( )
          if termsubject.Insert( ):
            print( Colorful.bold_green( "Subject with name `{} ({})` has been successfully linked to term `{}`!".format( termsubject.Subject.Name, termsubject.Subject.Shortcut, termsubject.Term.Name )))
            self._UpdateCDCommand( )
          else:
            print( Colorful.bold_red( "An error occured during the linking of subject with id `{}` and the current term".format( subjectid )))
        else:
          print( Colorful.bold_red( "Subject with id `{}` does not exist".format( subjectid )))
    except SystemExit:       # Do not exit cli if an error occured in parse_args
      pass

  def cmd_subject_unlink( self, item, args, rawline ):
    """-s <id>|-i||unlink a subject with the current term by id or in interactive mode"""
    parser = argparse.ArgumentParser( prog = "subject unlink", description = self.cmd_subject_unlink.__doc__.split( "||" )[1] )
    parser.add_argument( "-s", "--id", help = "set the id of the subject to unlink" )
    parser.add_argument( "-i", "--interactive", action = "store_true", help = "use the interactive mode" )

    try:
      id = None
      parsed_args = parser.parse_args( args.split( " " ))
      subjects = Subject.GetSubjectsByTerm( self._connection, self._ls.GetCurrentLocationValue( ))
      available_ids = [str( s.Id ) for s in subjects]
      if parsed_args.interactive:
        if len( subjects ) == 0:
          print( Colorful.white( "There are no subjects to unlink" ))
        else:
          print( Colorful.bold_green( "Subjects you can unlink:" ))
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
          term    = self._ls.GetCurrentLocationValue( )
          termsubject = Termsubject.GetTermsubjectByTermAndSubject( self._connection, term, subject )
          if termsubject.Delete( ):
            print( Colorful.bold_green( "Subject with id `{}` has been successfully unlinked".format( id )))
            self._UpdateCDCommand( )
          else:
            print( Colorful.bold_red( "An error occured during unlinking of subject with id `{}`".format( id )))
        else:
          print( Colorful.bold_red( "Subject with id `{}` does not exist".format( id )))
    except SystemExit:       # Do not exit cli if an error occured in parse_args
      pass

  def cmd_mark( self, item, args, rawline ):
    """<add|remove>||add or remove a mark"""
    sys.stdout.write( "Usage:" )
    CLI.HelpScreen( self, None, "mark" )

  def cmd_mark_add( self, item, args, rawline ):
    """add a new mark - Everytime in interactive mode"""

    mark_input = ""
    points     = None
    max_points = None
    valuation  = -1
    avarage    = None
    date       = None
    save = True
    try:
      while mark_input == "":
        mark_input = input( "Mark: " )
      points       = input( "Points []: " )
      max_points   = input( "Max Points []: " )
      while valuation < 0 or valuation > 100:
        valuation    = input( "Valuation (In %) [100]: " )
        if valuation == "":
          valuation == 100
          break
        try:
          valuation = float( valuation )
        except ValueError:
          valuation = -1
          continue

      avarage      = input( "Avarage []: " )
      while date is None:
        date       = input( "Date []: " )
        if date == "":
          date = None
          break
        try:
          test = time.strptime( date, "%d.%m.%Y" )
          break
        except ValueError:
          date = None
          continue

      save         = input( "Do you want to save ([y]/n)? " )
      save         = (save == "y" or save == "")
    except KeyboardInterrupt:
      save = False
      print( "" ) # To break down prompt to a new line
    if save:
      mark             = Mark( self._connection )
      mark.Termsubject = self._ls.GetCurrentLocationValue( )
      mark.Mark        = mark_input
      mark.Points      = points
      mark.MaxPoints   = max_points
      mark.Valuation   = valuation
      mark.Avarage     = avarage
      mark.Date        = date
      if mark.Insert( ):
        print( Colorful.bold_green( "This mark has been successfully saved!" ))
        self._UpdateCDCommand( )
      else:
        print( Colorful.bold_red( "An error occured during the insert action of the mark" ))

  def cmd_mark_remove( self, item, args, rawline ):
    """-s <id>|-i||remove a mark by id or in interactive mode"""
    parser = argparse.ArgumentParser( prog = "mark remove", description = self.cmd_mark_remove.__doc__.split( "||" )[1] )
    parser.add_argument( "-s", "--id", help = "set the id of the mark to remove" )
    parser.add_argument( "-i", "--interactive", action = "store_true", help = "use the interactive mode" )

    try:
      id = None
      parsed_args = parser.parse_args( args.split( " " ))
      marks = Mark.GetMarksByTermsubject( self._connection, self._ls.GetCurrentLocationValue( ))
      available_ids = [str( m.Id ) for m in marks]
      if parsed_args.interactive:
        if len( marks ) == 0:
          print( Colorful.white( "There are no marks to remove" ))
        else:
          print( Colorful.bold_green( "Marks you can remove:" ))
          self.PrintMarkTable( marks )
          try:
            id = input( "Enter id of the mark to be removed: " )
          except KeyboardInterrupt:
            print( "" ) # To break down prompt to a new line
      elif parsed_args.id is not None and parsed_args.id != "":
        id = parsed_args.id

      if id is not None:
        if id in available_ids:
          mark = [m for m in marks if str( m.Id ) == id][0]
          if mark.Delete( ):
            print( Colorful.bold_green( "Mark with id `{}` has been successfully removed".format( id )))
            self._UpdateCDCommand( )
          else:
            print( Colorful.bold_red( "An error occured during delete action of mark with id `{}`".format( id )))
        else:
          print( Colorful.bold_red( "Mark with id `{}` does not exist".format( id )))
    except SystemExit:       # Do not exit cli if an error occured in parse_args
      pass

  def cmd_exit( self, item, args, rawline ):
    """exit from the schoolcli"""
    y = input( "Do you really want to exit ([y]/n)? " )
    if y == "y" or y == "":
      CLI.Stop( self )
