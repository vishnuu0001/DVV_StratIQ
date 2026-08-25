#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class TeamActionPlan

#Region " Select Methods"
        Public Shared Function SelectTeamActionPlan(ByVal passTeamID As Integer, ByVal passActionNumber As String, _
                                                    Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, passActionNumber, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTeamActionPlan", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TeamID", passTeamID)
                da.SelectCommand.Parameters.AddWithValue("@ActionNumber", passActionNumber)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectTeamActionPlansByTeam(ByVal passTeamID As Integer, ByVal passDisplayClosedActions As Boolean, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, passDisplayClosedActions, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTeamActionPlansByTeam", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TeamID", passTeamID)
                da.SelectCommand.Parameters.AddWithValue("@DisplayClosedTeamActions", passDisplayClosedActions)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function TeamActionPlansByMeetingDate(ByVal passTeamMeetingID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
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
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTeamActionPlansByMeetingDate", cnSubConnection.OpenConnection(cnMasterConnection)))
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
        Public Shared Function SelectMyActionItems(ByVal passUserID As String, ByVal passSiteID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, passSiteID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelMyActionItems", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@UserID", passUserID)
                da.SelectCommand.Parameters.AddWithValue("@SiteID", passSiteID)
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
        Public Shared Function AddTeamActionPlan(ByVal passTeamID As Integer, ByVal passTeamMeetingID As Integer, ByVal passActionItem As String, _
                                                 ByVal passActionItemDefinition As String, ByVal passAssignedTo As String, ByVal passAssignedToOther As String, _
                                                 ByVal passTargetDate As String, ByVal passClosedDate As String, ByVal passStepNo As String, _
                                                 ByVal passActions As String, ByVal passCancelled As Boolean, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passTeamID, _
                                                                                     passTeamMeetingID, _
                                                                                     passActionItem, _
                                                                                     passActionItemDefinition, _
                                                                                     passAssignedTo, _
                                                                                     passAssignedToOther, _
                                                                                     passTargetDate, _
                                                                                     passClosedDate, _
                                                                                     passStepNo, _
                                                                                     passActions, passCancelled, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsTeamActionPlan", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmAdd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@TeamID", passTeamID)
                    If passTeamMeetingID > 0 Then
                        .Parameters.AddWithValue("@TeamMeetingID", passTeamMeetingID)
                    End If
                    .Parameters.AddWithValue("@ActionItem", passActionItem)
                    .Parameters.AddWithValue("@ActionItemDefinition", passActionItemDefinition)
                    .Parameters.AddWithValue("@AssignedTo", passAssignedTo)
                    .Parameters.AddWithValue("@AssignedToOther", passAssignedToOther)
                    .Parameters.AddWithValue("@TargetDate", passTargetDate)
                    If Not String.IsNullOrEmpty(passStepNo.Trim()) Then
                        .Parameters.AddWithValue("@StepNo", passStepNo)
                    End If
                    If Not String.IsNullOrEmpty(passActions.Trim) Then
                        .Parameters.AddWithValue("@Actions", passActions.Trim)
                    End If
                    If IsDate(passClosedDate) Then
                        .Parameters.AddWithValue("@ClosedDate", passClosedDate)
                    End If
                    .Parameters.AddWithValue("@Cancelled", passCancelled)

                    Return .ExecuteScalar
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Sub UpdateTeamActionPlan(ByVal passTeamID As Integer, ByVal passActionNumber As Integer, ByVal passTeamMeetingID As Integer, _
                                               ByVal passActionItem As String, ByVal passActionItemDefinition As String, ByVal passAssignedTo As String, _
                                               ByVal passAssignedToOther As String, ByVal passTargetDate As String, ByVal passClosedDate As String, _
                                               ByVal passStepNo As String, ByVal passActions As String, ByVal passCancelled As Boolean, _
                                               Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passTeamID, _
                                                                                     passActionNumber, _
                                                                                     passTeamMeetingID, _
                                                                                     passActionItem, _
                                                                                     passActionItemDefinition, _
                                                                                     passAssignedTo, _
                                                                                     passAssignedToOther, _
                                                                                     passTargetDate, _
                                                                                     passClosedDate, _
                                                                                     passStepNo, _
                                                                                     passActions, passCancelled, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdTeamActionPlan", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@TeamID", passTeamID)
                    .Parameters.AddWithValue("@ActionNumber", passActionNumber)
                    If passTeamMeetingID > 0 Then
                        .Parameters.AddWithValue("@TeamMeetingID", passTeamMeetingID)
                    End If
                    .Parameters.AddWithValue("@ActionItem", passActionItem)
                    .Parameters.AddWithValue("@ActionItemDefinition", passActionItemDefinition)
                    .Parameters.AddWithValue("@AssignedTo", passAssignedTo)
                    .Parameters.AddWithValue("@AssignedToOther", passAssignedToOther)
                    .Parameters.AddWithValue("@TargetDate", passTargetDate)
                    If Not String.IsNullOrEmpty(passStepNo.Trim()) Then
                        .Parameters.AddWithValue("@StepNo", passStepNo)
                    End If
                    If Not String.IsNullOrEmpty(passActions.Trim) Then
                        .Parameters.AddWithValue("@Actions", passActions.Trim)
                    End If
                    If IsDate(passClosedDate) Then
                        .Parameters.AddWithValue("@ClosedDate", passClosedDate)
                    End If
                    .Parameters.AddWithValue("@Cancelled", passCancelled)

                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub DeleteTeamActionPlan(ByVal passTeamID As Integer, ByVal passActionNumber As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, passActionNumber, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelTeamActionPlan", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmDelete
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@TeamID", passTeamID)
                    .Parameters.AddWithValue("@ActionNumber", passActionNumber)
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
