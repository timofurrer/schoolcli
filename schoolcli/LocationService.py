#!/usr/bin/python3.2

class LocationService:
  _location      = []  # Location dictonary
  _splitter      = "/"

  @property
  def Splitter( self ):
    return self._splitter

  def SetLocation( self, location ):
    self._location = location

  def AppendLocation( self, location, value ):
    self._location.append( (location, value))

  def GoToRoot( self ):
    self._location = []

  def GoOneBack( self ):
    if len( self._location ) >= 1:
      self._location.pop( )

  def GetLocationAsText( self ):
    text = self._splitter
    for location, value in self._location:
      text += location + self._splitter
    return text

  def GetHierarchyIndex( self ):
    return len( self._location )

  def GetCurrentLocation( self ):
    if len( self._location ) >= 1:
      return self._location[len( self._location ) - 1]
    else:
      return ( None, None )

  def GetCurrentLocationText( self ):
    if len( self._location ) >= 1:
      return self._location[len( self._location ) -1][0]
    else:
      return None

  def GetCurrentLocationValue( self ):
    if len( self._location ) >= 1:
      return self._location[len( self._location ) -1][1]
    else:
      return None

  def GetLocation( self ):
    return self._location

  def GetLocationAt( self, at ):
    return self._location[at]

  def GetLocationValueAt( self, at ):
    return self._location[at][1]
