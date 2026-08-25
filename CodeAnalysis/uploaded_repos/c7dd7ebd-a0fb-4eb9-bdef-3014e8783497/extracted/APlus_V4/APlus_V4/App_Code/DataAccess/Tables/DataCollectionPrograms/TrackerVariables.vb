#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class TrackerVariables

#Region " Select Methods"
        Public Shared Function SelectTrackerVariable(ByVal passTrackerVariableID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTrackerVariableID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTrackerVariable", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TrackerVariableID", passTrackerVariableID)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectFormulaTrackerVariables(ByVal passTrackerVariables As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTrackerVariables, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelFormulaTrackerVariables", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TrackerVariables", passTrackerVariables)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectValidateTrackerVariables(ByVal passTrackerVariables As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTrackerVariables, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelValidateTrackerVariables", cnSubConnection.OpenConnection(cnMasterConnection)))
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TrackerVariables", passTrackerVariables)

                Return Convert.ToInt16(da.SelectCommand.ExecuteScalar)
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectSavingsTrackerVariables(ByVal passTrackerVariables As String, ByVal passTrackerCollectionID As Integer, _
                                                             ByVal passTrackerPeriod As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTrackerVariables, passTrackerCollectionID, passTrackerPeriod, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelSavingsTrackerVariables", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TrackerVariables", passTrackerVariables)
                da.SelectCommand.Parameters.AddWithValue("@TrackerCollectionID", passTrackerCollectionID)
                da.SelectCommand.Parameters.AddWithValue("@TrackerPeriod", passTrackerPeriod)
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
        Public Shared Function AddTrackerVariable(ByVal passTrackerVariable As String, ByVal passVariableValue As String, _
                                                  ByVal passSiteID As Integer, ByVal passInterface As Boolean, _
                                                  ByVal passInterfaceFormula As String, ByVal passDataElements As String, _
                                                  ByVal passScheduleCode As String, ByVal passScheduleTime As String, _
                                                  ByVal passNextExecute As String, ByVal passOnDemandExecute As String, _
                                                  Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTrackerVariable, passVariableValue, passSiteID, passInterface, passInterfaceFormula, passDataElements, _
                                                                                     passScheduleCode, passScheduleTime, passNextExecute, passOnDemandExecute, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsTrackerVariable", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmAdd.CommandType = CommandType.StoredProcedure
                cmAdd.Parameters.AddWithValue("@TrackerVariable", passTrackerVariable)
                cmAdd.Parameters.AddWithValue("@VariableValue", passVariableValue)
                cmAdd.Parameters.AddWithValue("@SiteID", passSiteID)
                cmAdd.Parameters.AddWithValue("@Interface", passInterface)
                If passInterfaceFormula.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@InterfaceFormula", passInterfaceFormula.Trim)
                End If
                If passDataElements.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@DataElements", passDataElements.Trim)
                End If
                If passScheduleCode.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@ScheduleCode", passScheduleCode)
                End If
                If passScheduleTime.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@ScheduleTime", passScheduleTime)
                End If
                If passNextExecute.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@NextExecution", passNextExecute)
                End If
                If passOnDemandExecute.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@OnDemandExecute", passOnDemandExecute)
                End If

                Return cmAdd.ExecuteScalar
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Sub UpdateTrackerVariable(ByVal passTrackerVariableID As Integer, _
                                                ByVal passTrackerVariable As String, ByVal passVariableValue As String, _
                                                ByVal passSiteID As Integer, ByVal passInterface As Boolean, _
                                                ByVal passInterfaceFormula As String, ByVal passDataElements As String, _
                                                ByVal passScheduleCode As String, ByVal passScheduleTime As String, _
                                                ByVal passNextExecute As String, ByVal passOnDemandExecute As String, _
                                                Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTrackerVariableID, passTrackerVariable, passVariableValue, passSiteID, passInterface, passInterfaceFormula, passDataElements, _
                                                                                     passScheduleCode, passScheduleTime, passNextExecute, passOnDemandExecute, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdTrackerVariable", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmUpdate.CommandType = CommandType.StoredProcedure
                cmUpdate.Parameters.AddWithValue("@TrackerVariableID", passTrackerVariableID)
                cmUpdate.Parameters.AddWithValue("@TrackerVariable", passTrackerVariable)
                cmUpdate.Parameters.AddWithValue("@VariableValue", passVariableValue)
                cmUpdate.Parameters.AddWithValue("@SiteID", passSiteID)
                cmUpdate.Parameters.AddWithValue("@Interface", passInterface)
                If passInterfaceFormula.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@InterfaceFormula", passInterfaceFormula.Trim)
                End If
                If passDataElements.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@DataElements", passDataElements.Trim)
                End If
                If passScheduleCode.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@ScheduleCode", passScheduleCode)
                End If
                If passScheduleTime.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@ScheduleTime", passScheduleTime)
                End If
                If passNextExecute.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@NextExecution", passNextExecute)
                End If
                If passOnDemandExecute.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@OnDemandExecute", passOnDemandExecute)
                End If

                cmUpdate.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub DeleteTrackerVariable(ByVal passTrackerVariableID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTrackerVariableID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelTrackerVariable", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmDelete.CommandType = CommandType.StoredProcedure
                cmDelete.Parameters.AddWithValue("@TrackerVariableID", passTrackerVariableID)
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

