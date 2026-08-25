#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class RoomReservationsMaster

#Region " Select Room Reservations By Date"
        Public Shared Function SelectRoomReservationsByDate(ByVal passSiteID As Integer, ByVal passDate As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSiteID, passDate, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelRoomReservationsByDate", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@SiteID", passSiteID)
                da.SelectCommand.Parameters.AddWithValue("@ScheduleDate", passDate)
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

#Region " Time Slot Is Open"
        Public Shared Function TimeSlotIsOpen(ByVal passReservationID As Integer, ByVal passRoomID As Integer, ByVal passStartTime As String, ByVal passEndTime As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passReservationID, passRoomID, passStartTime, passEndTime, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim bReturn As Boolean = False
            Dim da As New SqlDataAdapter(New SqlCommand("spSelRoomReservationsByTimeSlot", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@RoomID", passRoomID)
                da.SelectCommand.Parameters.AddWithValue("@StartTime", passStartTime)
                da.SelectCommand.Parameters.AddWithValue("@EndTime", passEndTime)

                da.Fill(dt)
                If dt.Rows.Count > 0 Then
                    If passReservationID > 0 Then
                        bReturn = True
                        For Each dtRow As DataRow In dt.Rows
                            If dtRow("RoomReservationID") <> passReservationID Then
                                bReturn = False
                                Exit For
                            End If
                        Next
                    Else
                        bReturn = False
                    End If
                Else
                    bReturn = True
                End If
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
            Return bReturn
        End Function
#End Region

#Region " Select Room Reservation"
        Public Shared Function SelectRoomReservation(ByVal passReservationID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passReservationID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelRoomReservation", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@RoomReservationID", passReservationID)
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

#Region " Add Room Reservation"
        Public Shared Function AddRoomReservation(ByVal passRoomID As Integer, ByVal passStartTime As String, ByVal passEndTime As String, _
                                                  ByVal passDescription As String, ByVal passNotes As String, ByVal passTeamID As String, _
                                                  ByVal passUserID As String, ByVal passCatering As String, ByVal passVideo As Boolean, _
                                                  Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passRoomID, _
                                                                                     passStartTime, _
                                                                                     passEndTime, _
                                                                                     passDescription, passNotes, _
                                                                                     passTeamID, _
                                                                                     passUserID, _
                                                                                     passCatering, _
                                                                                     passVideo, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsRoomReservation", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmAdd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@RoomID", passRoomID)
                    .Parameters.AddWithValue("@StartTime", passStartTime)
                    .Parameters.AddWithValue("@EndTime", passEndTime)
                    .Parameters.AddWithValue("@Description", passDescription)
                    If Not String.IsNullOrEmpty(passNotes) Then .Parameters.AddWithValue("@Notes", passNotes.Trim)
                    If Not String.IsNullOrEmpty(passCatering.Trim()) Then .Parameters.AddWithValue("@Catering", passCatering)
                    .Parameters.AddWithValue("@VideoConferencing", passVideo)
                    If IsNumeric(passTeamID) AndAlso passTeamID > 0 Then
                        .Parameters.AddWithValue("@TeamID", passTeamID)
                    End If
                    .Parameters.AddWithValue("@UserID", passUserID)
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

#Region " Update Room Reservation"
        Public Shared Sub UpdateRoomReservation(ByVal passRoomReservationID As Integer, ByVal passRoomID As Integer, ByVal passStartTime As String, _
                                                ByVal passEndTime As String, ByVal passDescription As String, ByVal passNotes As String, _
                                                ByVal passTeamID As String, ByVal passUserID As String, ByVal passCatering As String, _
                                                ByVal passVideo As Boolean, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passRoomReservationID, _
                                                                                     passRoomID, _
                                                                                     passStartTime, _
                                                                                     passEndTime, _
                                                                                     passDescription, passNotes, _
                                                                                     passTeamID, _
                                                                                     passUserID, _
                                                                                     passCatering, _
                                                                                     passVideo, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdRoomReservation", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@RoomReservationID", passRoomReservationID)
                    .Parameters.AddWithValue("@RoomID", passRoomID)
                    .Parameters.AddWithValue("@StartTime", passStartTime)
                    .Parameters.AddWithValue("@EndTime", passEndTime)
                    .Parameters.AddWithValue("@Description", passDescription)
                    If Not String.IsNullOrEmpty(passNotes) Then .Parameters.AddWithValue("@Notes", passNotes.Trim)
                    If IsNumeric(passTeamID) AndAlso passTeamID > 0 Then
                        .Parameters.AddWithValue("@TeamID", passTeamID)
                    End If
                    If Not String.IsNullOrEmpty(passCatering.Trim()) Then .Parameters.AddWithValue("@Catering", passCatering)
                    .Parameters.AddWithValue("@VideoConferencing", passVideo)
                    .Parameters.AddWithValue("@UserID", passUserID)
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

#Region " Delete Room Reservation"
        Public Shared Sub DeleteRoomReservation(ByVal passReservationID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passReservationID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelRoomReservation", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmDelete
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@RoomReservationID", passReservationID)
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

    End Class
End Namespace
