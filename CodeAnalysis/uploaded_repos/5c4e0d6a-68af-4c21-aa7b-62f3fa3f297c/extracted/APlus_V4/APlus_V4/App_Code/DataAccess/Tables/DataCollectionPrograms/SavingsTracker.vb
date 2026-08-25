#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class SavingsTracker

#Region " Select Methods"
        Public Shared Function SelectSavingsTrackerValuesList(ByVal passTrackerID As Integer, ByVal passYear As Integer, _
        Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTrackerID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelSavingsTrackerValuesList", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TrackerID", passTrackerID)
                da.SelectCommand.Parameters.AddWithValue("@Year", passYear)

                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectSavingsTrackerSavingsList(ByVal passTrackerID As Integer, ByVal passYear As Integer, _
        Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTrackerID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelSavingsTrackerSavingsList", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TrackerID", passTrackerID)
                da.SelectCommand.Parameters.AddWithValue("@Year", passYear)

                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectTrackerSavingsByTrackerPlan(ByVal passUserID As String, ByVal passSiteID As Integer, ByVal passYear As Integer, _
                                                                 ByVal TrackerPlanID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, passSiteID, passYear, TrackerPlanID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelMasterPlanSavingsTrackers", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@UserID", passUserID)
                da.SelectCommand.Parameters.AddWithValue("@Year", passYear)
                da.SelectCommand.Parameters.AddWithValue("@SiteID", passSiteID)
                da.SelectCommand.Parameters.AddWithValue("@TrackerPlanID", TrackerPlanID)

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

#Region " Table Updates"
        Public Shared Sub UpdateTrackerValue(ByVal passTrackerID As Integer, ByVal passPeriod As String, ByVal passTrackerValue As String, _
                                             ByVal passHistoric As String, ByVal passTarget As String, _
                                             ByVal passTargetSavings As String, ByVal passPlannedSavings As String, _
                                             Optional ByRef cnMasterConnection As SqlConnection = Nothing, _
                                             Optional ByRef trans As SqlTransaction = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTrackerID, passPeriod, passTrackerValue, passHistoric, passTarget, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spUpdTrackerValues", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                If Not trans Is Nothing Then
                    cmAdd.Transaction = trans
                End If

                cmAdd.CommandType = CommandType.StoredProcedure
                cmAdd.Parameters.AddWithValue("@TrackerID", passTrackerID)
                cmAdd.Parameters.AddWithValue("@TrackerPeriod", passPeriod)
                If passTrackerValue.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@TrackerValue", passTrackerValue)
                End If
                If passHistoric.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@Historic", passHistoric)
                End If
                If passTarget.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@Target", passTarget)
                End If
                If passTargetSavings.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@TargetSavings", passTargetSavings)
                End If
                If passPlannedSavings.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@PlannedSavings", passPlannedSavings)
                End If

                cmAdd.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub UpdateTrackerSavings(ByVal passTrackerCollectionID As Integer, ByVal passPeriod As String, _
                                               ByVal passTrackerSavings As String, ByVal passTrackerFormula As String, _
                                               Optional ByRef cnMasterConnection As SqlConnection = Nothing, _
                                               Optional ByRef trans As SqlTransaction = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTrackerCollectionID, passPeriod, passTrackerSavings, passTrackerFormula, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spUpdTrackerSavings", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                If Not trans Is Nothing Then
                    cmAdd.Transaction = trans
                End If

                cmAdd.CommandType = CommandType.StoredProcedure
                cmAdd.Parameters.AddWithValue("@TrackerCollectionID", passTrackerCollectionID)
                cmAdd.Parameters.AddWithValue("@TrackerPeriod", passPeriod)
                If passTrackerSavings.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@TrackerSavings", passTrackerSavings)
                End If
                If passTrackerFormula.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@TrackerFormula", passTrackerFormula)
                End If

                cmAdd.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub UpdateTrackerSavingsVariableValues(ByVal passTrackerCollectionID As Integer, ByVal passPeriod As String, _
                                                             ByVal passTrackerVariableID As Integer, ByVal passVariableValue As String, _
                                                             Optional ByRef cnMasterConnection As SqlConnection = Nothing, _
                                                             Optional ByRef trans As SqlTransaction = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTrackerCollectionID, passPeriod, passTrackerVariableID, passVariableValue, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spUpdTrackerSavingsVariableValues", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                If Not trans Is Nothing Then
                    cmAdd.Transaction = trans
                End If

                cmAdd.CommandType = CommandType.StoredProcedure
                cmAdd.Parameters.AddWithValue("@TrackerCollectionID", passTrackerCollectionID)
                cmAdd.Parameters.AddWithValue("@TrackerPeriod", passPeriod)
                cmAdd.Parameters.AddWithValue("@TrackerVariableID", passTrackerVariableID)
                If passVariableValue.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@VariableValue", passVariableValue)
                End If

                cmAdd.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

    End Class
End Namespace

