#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class TeamMeetingAttendance

#Region " Select Methods"
        Public Shared Function SelectTeamMeetingAttendance(ByVal passTeamMeetingID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
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
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTeamMeetingAttendance", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TeamMeetingID", passTeamMeetingID)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectTeamMeetingAttendanceUser(ByVal passTeamMeetingID As Integer, _
                                                               ByVal passUserName As String, _
                                                               Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passTeamMeetingID, _
                                                                                     passUserName, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTeamMeetingAttendanceUser", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TeamMeetingID", passTeamMeetingID)
                da.SelectCommand.Parameters.AddWithValue("@UserName", passUserName)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectTeamMeetingAttendanceAdd(ByVal passTeamID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
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
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTeamMeetingAttendanceAdd", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TeamID", passTeamID)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Sub SelectTeamMeetingAttendanceList(ByVal passTeamMeetingID As Integer, _
                                                          ByRef passddlList As System.Web.UI.WebControls.DropDownList, _
                                                          Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passTeamMeetingID, _
                                                                                     passddlList.ID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelTeamMeetingAttendanceList", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@TeamMeetingID", passTeamMeetingID)
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    passddlList.Items.Add(New ListItem(drList.GetString(2) + ", " + drList.GetString(1) + " (" + drList.GetString(0) + ")", drList.GetString(0).Trim))
                End While
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Function SelectTeamMeetingAttendanceByTeam(ByVal passTeamID As Integer, ByVal passAll As Boolean, ByVal passLimiteMeetings As Boolean, _
                                                                 Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, passAll, passLimiteMeetings, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTeamMeetingAttendanceCrossTabReport", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TeamID", passTeamID)
                da.SelectCommand.Parameters.AddWithValue("@ShowAll", passAll)
                da.SelectCommand.Parameters.AddWithValue("@LimitMeetings", passLimiteMeetings)
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

#Region " Action Methods"
        Public Shared Function AddTeamMeetingAttendance(ByVal passTeamID As Integer, ByVal passTeamMeetingID As Integer, _
                                                        ByVal passUserID As String, ByVal passUserName As String, ByVal passInvited As Boolean, _
                                                        ByVal passAttended As Boolean, ByVal passMaintenanceUserID As String, _
                                                        Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passTeamID, _
                                                                                     passTeamMeetingID, _
                                                                                     passUserID, _
                                                                                     passUserName, _
                                                                                     passInvited, _
                                                                                     passAttended, _
                                                                                     passMaintenanceUserID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsTeamMeetingAttendance", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmAdd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@TeamID", passTeamID)
                    .Parameters.AddWithValue("@TeamMeetingID", passTeamMeetingID)
                    .Parameters.AddWithValue("@UserID", passUserID)
                    .Parameters.AddWithValue("@UserName", passUserName)
                    .Parameters.AddWithValue("@Invited", passInvited)
                    .Parameters.AddWithValue("@Attended", passAttended)
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
        Public Shared Sub UpdateTeamMeetingAttendance(ByVal passTeamID As Integer, ByVal passTeamMeetingID As Integer, ByVal passUserID As String, _
                                                      ByVal passUserName As String, ByVal passInvited As Boolean, ByVal passAttended As Boolean, _
                                                      ByVal passMaintenanceUserID As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passTeamID, _
                                                                                     passTeamMeetingID, _
                                                                                     passUserID, _
                                                                                     passUserName, _
                                                                                     passInvited, _
                                                                                     passAttended, _
                                                                                     passMaintenanceUserID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdTeamMeetingAttendance", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@TeamID", passTeamID)
                    .Parameters.AddWithValue("@TeamMeetingID", passTeamMeetingID)
                    .Parameters.AddWithValue("@UserID", passUserID)
                    .Parameters.AddWithValue("@UserName", passUserName)
                    .Parameters.AddWithValue("@Invited", passInvited)
                    .Parameters.AddWithValue("@Attended", passAttended)
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
        Public Shared Sub DeleteTeamMeetingAttended(ByVal passTeamMeetingID As Integer, ByVal passUserName As String, _
                                                    Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passTeamMeetingID, _
                                                                                     passUserName, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelTeamMeetingAttendance", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmDelete
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@TeamMeetingID", passTeamMeetingID)
                    .Parameters.AddWithValue("@UserName", passUserName)
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
