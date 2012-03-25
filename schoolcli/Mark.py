#!/usr/bin/python3.2

class Mark:
  _connection  = None
  _id          = None
  _termsubject = None
  _mark        = None
  _points      = None
  _max_points  = None
  _valuation   = None
  _avarage     = None
  _date        = None

  def __init__( self, connection, id = None, termsubject = None, mark = None, points = None, max_points = None, valuation = None, avarage = None, date = None ):
    self._connection  = connection
    self._id          = id
    self._termsubject = termsubject
    self._mark        = mark
    self._points      = points
    self._max_points  = max_points
    self._valuation   = valuation
    self._avarage     = avarage
    self._date        = date

  @property
  def Id( self ):
    return self._id

  @Id.setter
  def Id( self, id ):
    self._id = id

  @property
  def Termsubject( self ):
    return self._termsubject

  @Termsubject.setter
  def Termsubject( self, termsubject ):
    self._termsubject = termsubject

  @property
  def Mark( self ):
    return self._mark

  @Mark.setter
  def Mark( self, mark ):
    self._mark = mark

  @property
  def Points( self ):
    return self._points

  @Points.setter
  def Points( self, points ):
    self._points = points

  @property
  def MaxPoints( self ):
    return self._max_points

  @MaxPoints.setter
  def MaxPoints( self, max_points ):
    self._max_points = max_points

  @property
  def Valuation( self ):
    return self._valuation

  @Valuation.setter
  def Valuation( self, valuation ):
    self._valuation = valuation

  @property
  def Avarage( self ):
    return self._avarage

  @Avarage.setter
  def Avarage( self, avarage ):
    self._avarage = avarage

  @property
  def Date( self ):
    return self._date

  @Date.setter
  def Date( self, date ):
    self._date = date

  def Insert( self ):
    if self._connection is not None:
      #try:
      c = self._connection.cursor( )
      insert = """
        INSERT INTO Mark
          VALUES( ?, ?, ?, ?, ?, ?, ?, ? )
      """
      c.execute( insert, (c.lastrowid, self._termsubject.Id, self._mark, self._points, self._max_points, self._valuation, self._avarage, self._date ) )
      self._connection.commit( )
      c.close( )
      return True
      #except:
        #return False
    else:
      return False

  def Delete( self ):
    if self._connection is not None:
      try:
        c = self._connection.cursor( )
        delete = """
          DELETE FROM Mark
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
  def GetMarksByTermsubject( connection, termsubject ):
    if connection is not None:
      try:
        marks = []
        c = connection.cursor( )
        select = """
          SELECT *
            FROM Mark
            WHERE termsubject = ?
        """
        c.execute( select, [termsubject.Id] )
        rows = c.fetchall( )

        for row in rows:
          marks.append( Mark( connection, row["id"], termsubject, row["mark"], row["points"], row["max_points"], row["valuation"], row["avarage_mark"], row["date"] ) )
        c.close( )
        return marks
      except:
        return []
    return []

  @staticmethod
  def GetMarksByTerm( connection, term ):
    if connection is not None:
      try:
        marks = []
        c = connection.cursor( )
        select = """
          SELECT Mark.id AS id, Mark.mark AS mark, Mark.points AS points, Mark.max_points AS max_points, Mark.valuation AS valuation, Mark.avarage_mark AS avarage_mark, Mark.date AS date
            FROM Mark
            INNER JOIN Termsubject
              ON Termsubject.id = Mark.termsubject
            WHERE Termsubject.term = ?
        """
        c.execute( select, [termsubject.Id] )
        rows = c.fetchall( )

        for row in rows:
          marks.append( Mark( connection, row["id"], termsubject, row["mark"], row["points"], row["max_points"], row["valuation"], row["avarage_mark"], row["date"] ) )
        c.close( )
        return marks
      except:
        return []
    return []
