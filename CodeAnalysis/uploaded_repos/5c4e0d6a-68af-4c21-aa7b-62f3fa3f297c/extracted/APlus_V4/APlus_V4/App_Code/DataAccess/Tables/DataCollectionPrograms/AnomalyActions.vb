#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class AnomalyActions

#Region " Select Methods"
        Public Shared Function SelectAnomalyActionByID(ByVal passAnomalyActionID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passAnomalyActionID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelAnomalyActionByID", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@AnomalyActionID", passAnomalyActionID)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectOpenAnomalyActions(ByVal passAnomalyID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passAnomalyID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelAnomalyActionsOpen", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@AnomalyID", passAnomalyID)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectAnomalyActionAuthority(ByVal passAnomalyActionID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passAnomalyActionID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelAnomalyActionAuthority", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@AnomalyActionID", passAnomalyActionID)
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

#Region " Table Methods"
        Public Shared Function AddAnomalyAction(ByVal passAnomalyID As Integer, ByVal passAnomalyCauseID As Integer, ByVal passActionWhat As String, _
                                                ByVal passActionWhere As String, ByVal passActionWhy As String, ByVal passTargetDate As String, _
                                                ByVal passActionHow As String, ByVal passResponsibleUserID As String, ByVal passActions As String, _
                                                ByVal passClosedDate As String, ByVal passCancelled As Boolean, ByVal passContentionAction As Boolean, _
                                                Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passAnomalyID, passAnomalyCauseID, passActionWhat, passActionWhere, _
                                                                                     passActionWhy, passTargetDate, passResponsibleUserID, passActionHow, passActions, passClosedDate, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsAnomalyAction", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmAdd.CommandType = CommandType.StoredProcedure
                cmAdd.Parameters.AddWithValue("@AnomalyID", passAnomalyID)
                If passAnomalyCauseID > 0 Then
                    cmAdd.Parameters.AddWithValue("@AnomalyCauseID", passAnomalyCauseID)
                End If
                If passActionWhat.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@ActionWhat", passActionWhat)
                End If
                If passActionWhere.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@ActionWhere", passActionWhere)
                End If
                If passActionWhy.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@ActionWhy", passActionWhy)
                End If
                cmAdd.Parameters.AddWithValue("@ContentionAction", passContentionAction)
                cmAdd.Parameters.AddWithValue("@TargetDate", passTargetDate)
                cmAdd.Parameters.AddWithValue("@ResponsibleUserID", passResponsibleUserID)
                If passActionHow.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@ActionHow", passActionHow)
                End If
                If passActions.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@Actions", passActions.Trim)
                End If
                If passClosedDate.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@ClosedDate", passClosedDate)
                End If
                cmAdd.Parameters.AddWithValue("@Cancelled", passCancelled)

                Return cmAdd.ExecuteScalar
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Sub UpdateAnomalyAction(ByVal passAnomalyActionID As Integer, ByVal passAnomalyCauseID As Integer, ByVal passActionWhat As String, _
                                              ByVal passActionWhere As String, ByVal passActionWhy As String, ByVal passTargetDate As String, ByVal passActionHow As String, _
                                              ByVal passResponsibleUserID As String, ByVal passActions As String, ByVal passClosedDate As String, ByVal passCancelled As Boolean, _
                                              ByVal passContentionAction As Boolean, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passAnomalyActionID, passActionWhat, passActionWhere, passActionWhy, _
                                                                                     passTargetDate, passResponsibleUserID, passActionHow, passActions, passClosedDate, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdAnomalyAction", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmUpdate.CommandType = CommandType.StoredProcedure
                cmUpdate.Parameters.AddWithValue("@AnomalyActionID", passAnomalyActionID)
                If passAnomalyCauseID > 0 Then
                    cmUpdate.Parameters.AddWithValue("@AnomalyCauseID", passAnomalyCauseID)
                End If
                If passActionWhat.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@ActionWhat", passActionWhat)
                End If
                If passActionWhere.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@ActionWhere", passActionWhere)
                End If
                If passActionWhy.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@ActionWhy", passActionWhy)
                End If
                cmUpdate.Parameters.AddWithValue("@ContentionAction", passContentionAction)
                cmUpdate.Parameters.AddWithValue("@TargetDate", passTargetDate)
                cmUpdate.Parameters.AddWithValue("@ResponsibleUserID", passResponsibleUserID)
                If passActionHow.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@ActionHow", passActionHow)
                End If
                If passActions.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@Actions", passActions.Trim)
                End If
                If passClosedDate.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@ClosedDate", passClosedDate)
                End If
                cmUpdate.Parameters.AddWithValue("@Cancelled", passCancelled)

                cmUpdate.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub DeleteAnomalyAction(ByVal passAnomalyActionID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passAnomalyActionID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelAnomalyAction", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmDelete.CommandType = CommandType.StoredProcedure
                cmDelete.Parameters.AddWithValue("@AnomalyActionID", passAnomalyActionID)
                cmDelete.ExecuteNonQuery()
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

