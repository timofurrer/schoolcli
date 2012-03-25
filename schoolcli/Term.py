#!/usr/bin/python3.2

from School import *

class Term:
  _connection = None
  _id         = None
  _school     = None
  _name       = None

  def __init__( self, connection = None, id = None, school = None, name = None ):
    self._connection = connection
    self._id         = id
    self._school     = school
    self._name       = name

  @property
  def Id( self ):
    return self._id

  @Id.setter
  def Id( self, id ):
    self._id = id

  @property
  def Name( self ):
    return self._name

  @Name.setter
  def Name( self, name ):
    self._name = name

  @property
  def School( self ):
    return self._school

  @School.setter
  def School( self, school ):
    self._school = school

  def Insert( self ):
    if self._connection is not None:
      try:
        c = self._connection.cursor( )
        insert = """
          INSERT INTO Term
            VALUES( ?, ?, ? )
        """
        c.execute( insert, (c.lastrowid, self._school.Id, self._name) )
        self._connection.commit( )
        c.close( )
        return True
      except:
        return False
    else:
      return False

  def Delete( self ):
    if self._connection is not None:
      try:
        c = self._connection.cursor( )
        delete = """
          DELETE FROM Term
            WHERE id = ?
        """
        c.execute( delete, str( self._id ) )
        self._connection.commit( )
        c.close( )
        return True
      except:
        return False
    else:
      return False

  @staticmethod
  def GetTerms( connection ):
    if connection is not None:
      try:
        terms = []
        c = connection.cursor( )
        c.execute( "SELECT * FROM Term" )
        rows = c.fetchall( )

        for row in rows:
          school = School.GetSchoolById( connection, row["id"] )
          if school is not None:
            terms.append( Term( connection, row["id"], school, row["name"] ) )
        c.close( )
        return terms
      except:
        return []
    return []

  @staticmethod
  def GetTermsBySchool( connection, school ):
    if connection is not None:
      try:
        terms = []
        c = connection.cursor( )
        c.execute( "SELECT * FROM Term WHERE school = ?", [school.Id] )
        rows = c.fetchall( )

        for row in rows:
          terms.append( Term( connection, row["id"], school, row["name"] ) )
        c.close( )
        return terms
      except:
        return []
    return []

  @staticmethod
  def GetTermByName( connection, name ):
    if connection is not None:
      try:
        school = None
        c = connection.cursor( )
        c.execute( "SELECT * FROM Term WHERE name = ?", [name] )
        row = c.fetchall( )[0]
        school = School.GetSchoolById( connection, row["school"] )
        term = Term( connection, row["id"], school, row["name"] )
        c.close( )
        return term
      except:
        return None
    return None
