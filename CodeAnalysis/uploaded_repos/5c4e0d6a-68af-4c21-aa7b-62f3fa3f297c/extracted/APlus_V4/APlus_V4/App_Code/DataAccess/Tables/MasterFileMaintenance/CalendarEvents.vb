#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class CalendarEvents

#Region " Select Calendar Events"
        Public Shared Function SelectCalendarEvents(ByVal passUserID As String, ByVal passStartDate As String, _
                                                    ByVal passEndDate As String, ByVal passWorkingSiteID As Integer, _
                                                    ByVal passShowMyTeams As Boolean, ByVal passShowAllTeams As Boolean, _
                                                    ByVal passSelectedTeam As String, ByVal passReservations As Integer, _
                                                    ByVal passRoomGroupID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, passStartDate, passEndDate, passWorkingSiteID, passShowMyTeams, passShowAllTeams, passSelectedTeam, passReservations, passRoomGroupID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelAllCalendarEvents", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure

                da.SelectCommand.Parameters.AddWithValue("@UserID", passUserID)
                da.SelectCommand.Parameters.AddWithValue("@StartDate", passStartDate)
                da.SelectCommand.Parameters.AddWithValue("@EndDate", passEndDate)
                da.SelectCommand.Parameters.AddWithValue("@SiteID", passWorkingSiteID)
                da.SelectCommand.Parameters.AddWithValue("@MyTeams", passShowMyTeams)
                da.SelectCommand.Parameters.AddWithValue("@AllTeams", passShowAllTeams)
                If passSelectedTeam.Trim.Length > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@SelectedTeam", passSelectedTeam)
                End If
                da.SelectCommand.Parameters.AddWithValue("@RoomReservations", passReservations)
                If passRoomGroupID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@RoomGroupID", passRoomGroupID)
                End If

                da.Fill(dt)

                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " Select Calendar Event By ID"
        Public Shared Function SelectCalendarEventByID(ByVal passCalendarEventID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passCalendarEventID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelCalendarEventByKey", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@CalendarEventID", passCalendarEventID)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " Select Calendar Event"
        Public Shared Function SelectCalendarEvent(ByVal passSiteID As Integer, ByVal passEventType As String, ByVal passEvent As String, ByVal passEventDate As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSiteID, passEventType, passEvent, passEventDate, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelCalendarEvent", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                If passSiteID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@SiteID", passSiteID)
                End If
                da.SelectCommand.Parameters.AddWithValue("@EventType", passEventType)
                da.SelectCommand.Parameters.AddWithValue("@Event", passEvent)
                da.SelectCommand.Parameters.AddWithValue("@EventDate", passEventDate)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " Delete Calendar Event"
        Public Shared Sub DeleteCalendarEvent(ByVal passCalendarEventID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passCalendarEventID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelCalendarEvent", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmDelete
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@CalendarEventID", passCalendarEventID)
                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmDelete.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " Add Calendar Event"
        Public Shared Function AddCalendarEvent(ByVal passSiteID As Integer, _
                                           ByVal passEventTypeID As Integer, _
                                           ByVal passEvent As String, _
                                           ByVal passEventDate As String, _
                                           ByVal passEventTime As String, _
                                           ByVal passDescription As String, _
                                           Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passSiteID, _
                                                                                     passEventTypeID, _
                                                                                     passEvent, _
                                                                                     passEventDate, _
                                                                                     passEventTime, _
                                                                                     passDescription, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsCalendarEvent", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmAdd
                    .CommandType = CommandType.StoredProcedure
                    If passSiteID > 0 Then
                        .Parameters.AddWithValue("@SiteID", passSiteID)
                    End If
                    .Parameters.AddWithValue("@EventTypeID", passEventTypeID)
                    .Parameters.AddWithValue("@Event", passEvent)
                    .Parameters.AddWithValue("@EventDate", passEventDate)
                    If passEventTime.Trim.Length > 0 Then .Parameters.AddWithValue("@EventTime", passEventTime)
                    If Not String.IsNullOrEmpty(passDescription.Trim()) Then .Parameters.AddWithValue("@EventDescription", passDescription)
                    Return .ExecuteScalar
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " Update Calendar Event"
        Public Shared Sub UpdateCalendarEvent(ByVal passCalendarEventID As Integer, _
                                              ByVal passEventDescription As String, _
                                              Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passCalendarEventID, passEventDescription, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdCalendarEvent", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@CalendarEventID", passCalendarEventID)
                    If Not String.IsNullOrEmpty(passEventDescription.Trim()) Then .Parameters.AddWithValue("@EventDescription", passEventDescription)
                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

    End Class
End Namespace
