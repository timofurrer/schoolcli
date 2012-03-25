#!/usr/bin/python3.2

class Subject:
  _connection = None
  _id         = None
  _name       = None
  _schortcut  = None

  def __init__( self, connection = None, id = None, name = None, shortcut = None ):
    self._connection = connection
    self._id         = id
    self._name       = name
    self._shortcut   = shortcut

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
  def Shortcut( self ):
    return self._shortcut

  @Shortcut.setter
  def Shortcut( self, shortcut ):
    self._shortcut = shortcut

  def Insert( self ):
    if self._connection is not None:
      try:
        c = self._connection.cursor( )
        insert = """
          INSERT INTO Subject
            VALUES( ?, ?, ? )
        """
        c.execute( insert, (c.lastrowid, self._name, self._shortcut) )
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
          DELETE FROM Subject
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
  def GetSubjects( connection ):
    if connection is not None:
      try:
        subjects = []
        c = connection.cursor( )
        c.execute( "SELECT * FROM Subject" )
        rows = c.fetchall( )

        for row in rows:
          subjects.append( Subject( connection, row["id"], row["name"], row["shortcut"] ) )
        c.close( )
        return subjects
      except:
        return []
    return []

  @staticmethod
  def GetSubjectsByTerm( connection, term ):
    if connection is not None:
      try:
        subjects = []
        c = connection.cursor( )
        select = """
          SELECT Subject.Id AS id, Subject.Name AS name, Subject.shortcut AS shortcut
            FROM Termsubject
              INNER JOIN Subject
                ON Termsubject.subject = Subject.Id
            WHERE Termsubject.term = ?
        """
        c.execute( select, [term.Id] )
        rows = c.fetchall( )

        for row in rows:
          subjects.append( Subject( connection, row["id"], row["name"], row["shortcut"] ) )
        c.close( )
        return subjects
      except:
        return []
    return []

  @staticmethod
  def GetSubjectByName( connection, name ):
    if connection is not None:
      try:
        c = connection.cursor( )
        c.execute( "SELECT * FROM Subject WHERE name = ?", [name] )
        row = c.fetchall( )[0]
        subject = Subject( connection, row["id"], row["name"], row["shortcut"] )
        c.close( )
        return subject
      except:
        return None
    return None

  @staticmethod
  def GetSubjectByShortcut( connection, shortcut ):
    if connection is not None:
      try:
        c = connection.cursor( )
        c.execute( "SELECT * FROM Subject WHERE shortcut = ?", [shortcut] )
        row = c.fetchall( )[0]
        subject = Subject( connection, row["id"], row["name"], row["shortcut"] )
        c.close( )
        return subject
      except:
        return None
    return None

  @staticmethod
  def GetSubjectById( connection, id ):
    if connection is not None:
      try:
        c = connection.cursor( )
        c.execute( "SELECT * FROM Subject WHERE id = ?", [id] )
        row = c.fetchall( )[0]
        subject = Subject( connection, row["id"], row["name"], row["shortcut"] )
        c.close( )
        return subject
      except:
        return None
    return None
