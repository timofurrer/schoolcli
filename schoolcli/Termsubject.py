#!/usr/bin/python3.2

class Termsubject:
  _connection = None
  _id         = None
  _term       = None
  _subject    = None

  def __init__( self, connection, id = None, term = None, subject = None ):
    self._connection = connection
    self._id         = id
    self._term       = term
    self._subject    = subject

  @property
  def Id( self ):
    return self._id

  @Id.setter
  def Id( self, id ):
    self._id = id

  @property
  def Term( self ):
    return self._term

  @Term.setter
  def Term( self, term ):
    self._term = term

  @property
  def Subject( self ):
    return self._subject

  @Subject.setter
  def Subject( self, subject ):
    self._subject = subject

  def Insert( self ):
    if self._connection is not None:
      try:
        c = self._connection.cursor( )
        insert = """
          INSERT INTO Termsubject
            VALUES( ?, ?, ? )
        """
        c.execute( insert, (c.lastrowid, self._term.Id, self._subject.Id))
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
          DELETE FROM Termsubject
            WHERE id = ?
        """
        c.execute( delete, str( self._id ))
        self._connection.commit( )
        c.close( )
        return True
      except:
        return False
    else:
      return False

  @staticmethod
  def GetTermsubjectByTermAndSubject( connection, term, subject ):
    if connection is not None:
      try:
        c = connection.cursor( )
        c.execute( "SELECT * FROM Termsubject WHERE term = ? and subject = ?", [term.Id, subject.Id] )
        row = c.fetchall( )[0]
        termsubject = Termsubject( connection, row["id"], term, subject )
        c.close( )
        return termsubject
      except:
        return []
    return []
