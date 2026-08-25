#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class KPIUserNotifications

#Region " Select Methods"
        Public Shared Function SelectKPIUserNotificationByKey(ByVal passKPIID As Integer, ByVal passUserID As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passKPIID, passUserID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelKPIUserNotificationByKey", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@KPIID", passKPIID)
                da.SelectCommand.Parameters.AddWithValue("@UserID", passUserID)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectKPIUserNotificationDeviation(ByVal passKPIID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passKPIID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelKPIDeviationNotificationByKPIID", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@KPIID", passKPIID)
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
        Public Shared Sub InsertKPIUserNotifications(ByVal passKPIID As Integer, ByVal passUserID As String, ByVal passKPIValueEntry As Boolean, _
                                                     ByVal passKPIValueEntryReminder As Boolean, ByVal passKPITargetEntry As Boolean, ByVal passKPITargetEntryReminder As Boolean, _
                                                     ByVal passKPIDeviation As Boolean, ByVal passAnomalyPending As Boolean, ByVal passAnomalyPendingReminder As Boolean, _
                                                     ByVal passAnomalyActions As Boolean, ByVal passAnomalyActionsReminder As Boolean, _
                                                     Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passKPIID, passUserID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsKPIUserNotifications", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmAdd.CommandType = CommandType.StoredProcedure
                cmAdd.Parameters.AddWithValue("@KPIID", passKPIID)
                cmAdd.Parameters.AddWithValue("@UserID", passUserID)
                cmAdd.Parameters.AddWithValue("@KPIValueEntry", passKPIValueEntry)
                cmAdd.Parameters.AddWithValue("@KPIValueEntryReminder", passKPIValueEntryReminder)
                cmAdd.Parameters.AddWithValue("@KPITargetEntry", passKPITargetEntry)
                cmAdd.Parameters.AddWithValue("@KPITargetEntryReminder", passKPITargetEntryReminder)
                cmAdd.Parameters.AddWithValue("@KPIDeviation", passKPIDeviation)
                cmAdd.Parameters.AddWithValue("@AnomalyPending", passAnomalyPending)
                cmAdd.Parameters.AddWithValue("@AnomalyPendingReminder", passAnomalyPendingReminder)
                cmAdd.Parameters.AddWithValue("@AnomalyActions", passAnomalyActions)
                cmAdd.Parameters.AddWithValue("@AnomalyActionsReminder", passAnomalyActionsReminder)

                cmAdd.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub UpdateKPIUserNotifications(ByVal passKPIID As Integer, ByVal passUserID As String, ByVal passKPIValueEntry As Boolean, _
                                                     ByVal passKPIValueEntryReminder As Boolean, ByVal passKPITargetEntry As Boolean, ByVal passKPITargetEntryReminder As Boolean, _
                                                     ByVal passKPIDeviation As Boolean, ByVal passAnomalyPending As Boolean, ByVal passAnomalyPendingReminder As Boolean, _
                                                     ByVal passAnomalyActions As Boolean, ByVal passAnomalyActionsReminder As Boolean, _
                                                     Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passKPIID, passUserID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spUpdKPIUserNotifications", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmAdd.CommandType = CommandType.StoredProcedure
                cmAdd.Parameters.AddWithValue("@KPIID", passKPIID)
                cmAdd.Parameters.AddWithValue("@UserID", passUserID)
                cmAdd.Parameters.AddWithValue("@KPIValueEntry", passKPIValueEntry)
                cmAdd.Parameters.AddWithValue("@KPIValueEntryReminder", passKPIValueEntryReminder)
                cmAdd.Parameters.AddWithValue("@KPITargetEntry", passKPITargetEntry)
                cmAdd.Parameters.AddWithValue("@KPITargetEntryReminder", passKPITargetEntryReminder)
                cmAdd.Parameters.AddWithValue("@KPIDeviation", passKPIDeviation)
                cmAdd.Parameters.AddWithValue("@AnomalyPending", passAnomalyPending)
                cmAdd.Parameters.AddWithValue("@AnomalyPendingReminder", passAnomalyPendingReminder)
                cmAdd.Parameters.AddWithValue("@AnomalyActions", passAnomalyActions)
                cmAdd.Parameters.AddWithValue("@AnomalyActionsReminder", passAnomalyActionsReminder)

                cmAdd.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub DeleteKPITeamMaster(ByVal passKPIID As Integer, ByVal passUserID As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passKPIID, passUserID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelKPIUserNotifications", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmDelete.CommandType = CommandType.StoredProcedure
                cmDelete.Parameters.AddWithValue("@KPIID", passKPIID)
                cmDelete.Parameters.AddWithValue("@UserID", passUserID)

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

