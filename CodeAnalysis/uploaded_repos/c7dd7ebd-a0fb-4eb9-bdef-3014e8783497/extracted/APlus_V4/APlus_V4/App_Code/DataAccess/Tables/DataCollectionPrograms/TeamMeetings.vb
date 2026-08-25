#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class TeamMeetings

#Region " Select Methods"
        Public Shared Function SelectTeamMeeting(ByVal passTeamMeetingID As Integer, _
                                                 Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamMeetingID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTeamMeeting", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim ds As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TeamMeetingID", passTeamMeetingID)

                da.Fill(ds)
                Return ds
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectTeamMeetingsByDateNoDDL(ByVal passTeamID As Integer, ByVal passMeetingDate As String, _
                                                             Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, passMeetingDate, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTeamMeetingsByDate", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim ds As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TeamID", passTeamID)
                da.SelectCommand.Parameters.AddWithValue("@MeetingDate", passMeetingDate)
                da.Fill(ds)
                Return ds
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Sub SelectTeamMeetingList(ByRef ddlList As DropDownList, ByVal passTeamID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, ddlList.ID, passTeamID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelTeamMeetingList", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                ddlList.Items.Clear()
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@TeamID", passTeamID)
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    ddlList.Items.Add(New ListItem(drList.Item(1).ToString & " - " & drList.Item(2).ToString, drList.Item(0).ToString))
                End While
                'If drList.HasRows Then
                '    ddlList.SelectedIndex = ddlList.Items.Count - 1
                'End If
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Function SelectTeamMeetingAudit(ByVal passMeetingDate As String, ByVal passMeetingTime As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passMeetingDate, passMeetingTime, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim myParm As SqlParameter
            Dim cmProgramMode As New SqlCommand("spSelTeamMeetingAudit", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmProgramMode
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@MeetingDate", passMeetingDate.Trim())
                    .Parameters.AddWithValue("@MeetingTime", passMeetingTime)
                    myParm = .Parameters.Add("@Audit", SqlDbType.Bit)
                    myParm.Direction = ParameterDirection.Output
                    .ExecuteNonQuery()
                    .Dispose()
                End With
                Return cmProgramMode.Parameters("@Audit").Value
            Catch Exc As Exception
                Throw
            Finally
                cmProgramMode.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function GetTeamMeetingsCount(ByVal passTeamID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTeamMeetings", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim ds As New DataTable
            Dim iRows As Integer = 0

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TeamID", passTeamID)

                da.Fill(ds)

                If ds IsNot Nothing AndAlso ds.Rows.Count > 0 Then
                    iRows = ds.Rows.Count
                End If
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try

            Return iRows
        End Function
#End Region

#Region " Action Methods"
        Public Shared Function AddTeamMeetings(ByVal passTeamID As Integer, ByVal passMeetingDate As String, ByVal passMeetingTime As String, _
                                               ByVal passMeetingLocation As String, ByVal passAgenda As String, ByVal passHighlights As String, _
                                               ByVal passAgendaNextMeeting As String, ByVal passAudit As Boolean, ByVal passMeetingLength As String, _
                                               ByVal passNextMeetingDate As String, ByVal passMaintenanceUserID As String, _
                                               Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passTeamID, _
                                                                                     passMeetingDate, _
                                                                                     passMeetingTime, _
                                                                                     passMeetingLocation, _
                                                                                     passAgenda, _
                                                                                     passHighlights, _
                                                                                     passAgendaNextMeeting, _
                                                                                     passAudit, _
                                                                                     passMeetingLength, _
                                                                                     passNextMeetingDate, _
                                                                                     passMaintenanceUserID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsTeamMeetings", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmAdd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@TeamID", passTeamID)
                    .Parameters.AddWithValue("@MeetingDate", passMeetingDate)
                    .Parameters.AddWithValue("@MeetingTime", passMeetingTime)
                    .Parameters.AddWithValue("@MeetingLocation", passMeetingLocation)
                    .Parameters.AddWithValue("@Agenda", passAgenda)
                    .Parameters.AddWithValue("@Highlights", passHighlights)
                    .Parameters.AddWithValue("@AgendaNextMeeting", passAgendaNextMeeting)
                    .Parameters.AddWithValue("@Audit", passAudit)
                    If Not String.IsNullOrEmpty(passMeetingLength.Trim()) Then .Parameters.AddWithValue("@MeetingLength", passMeetingLength)
                    If Not String.IsNullOrEmpty(passNextMeetingDate.Trim()) Then .Parameters.AddWithValue("@NextMeetingDate", passNextMeetingDate)
                    .Parameters.AddWithValue("@MaintenanceUserID", passMaintenanceUserID)
                    Return .ExecuteScalar
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Sub UpdateTeamMeetings(ByVal passTeamMeetingID As Integer, _
                                             ByVal passMeetingLocation As String, _
                                             ByVal passAgenda As String, _
                                             ByVal passHighlights As String, _
                                             ByVal passAgendaNextMeeting As String, _
                                             ByVal passAudit As Boolean, _
                                             ByVal passMeetingLength As String, _
                                             ByVal passNextMeetingDate As String, _
                                             ByVal passMaintenanceUserID As String, _
                                             Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passTeamMeetingID, _
                                                                                     passMeetingLocation, _
                                                                                     passAgenda, _
                                                                                     passHighlights, _
                                                                                     passAgendaNextMeeting, _
                                                                                     passAudit, _
                                                                                     passMeetingLength, _
                                                                                     passNextMeetingDate, _
                                                                                     passMaintenanceUserID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdTeamMeetings", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@TeamMeetingID", passTeamMeetingID)
                    .Parameters.AddWithValue("@MeetingLocation", passMeetingLocation)
                    .Parameters.AddWithValue("@Agenda", passAgenda)
                    .Parameters.AddWithValue("@Highlights", passHighlights)
                    .Parameters.AddWithValue("@AgendaNextMeeting", passAgendaNextMeeting)
                    .Parameters.AddWithValue("@Audit", passAudit)
                    If Not String.IsNullOrEmpty(passMeetingLength.Trim()) Then .Parameters.AddWithValue("@MeetingLength", passMeetingLength)
                    If Not String.IsNullOrEmpty(passNextMeetingDate.Trim()) Then .Parameters.AddWithValue("@NextMeetingDate", passNextMeetingDate)
                    .Parameters.AddWithValue("@MaintenanceUserID", passMaintenanceUserID)
                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub RescheduleTeemMeeting(ByVal passTeamMeetingID As Integer, _
                                                     ByVal passMeetingDate As String, _
                                                     ByVal passMeetingTime As String, _
                                                     ByVal passMaintenanceUserID As String, _
                                                     Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passTeamMeetingID, _
                                                                                     passMeetingDate, _
                                                                                     passMeetingTime, _
                                                                                     passMaintenanceUserID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdRescheduleTeamMeeting", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@TeamMeetingID", passTeamMeetingID)
                    .Parameters.AddWithValue("@MeetingDate", passMeetingDate)
                    .Parameters.AddWithValue("@MeetingTime", passMeetingTime)
                    .Parameters.AddWithValue("@MaintenanceUserID", passMaintenanceUserID)
                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub DeleteTeamMeetings(ByVal passTeamMeetingID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamMeetingID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelTeamMeetings", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmDelete
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@TeamMeetingID", passTeamMeetingID)
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
