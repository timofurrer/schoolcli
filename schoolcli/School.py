#!/usr/bin/python3.2

class School:
  _id         = None
  _name       = None
  _connection = None

  def __init__( self, connection = None, id = None, name = None ):
    self._connection = connection
    self._id         = id
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

  def Insert( self ):
    if self._connection is not None:
      try:
        c = self._connection.cursor( )
        insert = """
          INSERT INTO School
            VALUES( ?, ? )
        """
        c.execute( insert, (c.lastrowid, self._name))
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
          DELETE FROM School
            WHERE id = ?
        """
        c.execute( delete, [self._id] )
        self._connection.commit( )
        c.close( )
        return True
      except:
        return False
    else:
      return False

  @staticmethod
  def GetSchools( connection ):
    if connection is not None:
      try:
        schools = []
        c = connection.cursor( )
        c.execute( "SELECT * FROM School" )
        rows = c.fetchall( )

        for row in rows:
          schools.append( School( connection, row["id"], row["name"] ))
        c.close( )
        return schools
      except:
        return []
    return []

  @staticmethod
  def GetSchoolById( connection, id ):
    if connection is not None:
      try:
        school = None
        c = connection.cursor( )
        c.execute( "SELECT * FROM School WHERE id = ?", [id] )
        row = c.fetchall( )[0]
        school = School( connection, row["id"], row["name"] )
        c.close( )
        return school
      except:
        return None
    return None

  @staticmethod
  def GetSchoolByName( connection, name ):
    if connection is not None:
      try:
        school = None
        c = connection.cursor( )
        c.execute( "SELECT * FROM School WHERE name = ?", [name] )
        row = c.fetchall( )[0]
        school = School( connection, row["id"], row["name"] )
        c.close( )
        return school
      except:
        return None
    return None
