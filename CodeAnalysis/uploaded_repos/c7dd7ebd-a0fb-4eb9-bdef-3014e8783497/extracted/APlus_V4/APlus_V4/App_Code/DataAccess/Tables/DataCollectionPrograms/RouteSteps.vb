#Region "Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class RouteSteps

#Region " Select Route Steps "
        Public Shared Function SelectRouteSteps(Optional ByVal passRouteAbbrev As String = "", Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataSet
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passRouteAbbrev, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelRouteSteps", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim ds As New DataSet
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                If passRouteAbbrev.Trim.Length > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@RouteAbbrev", passRouteAbbrev)
                End If
                da.Fill(ds)
                Return ds
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " Select Route Steps By Key"
        Public Shared Function SelectRouteStepsByKey(ByVal passRouteAbbrev As String, _
                                                     ByVal passStepNo As Integer, _
                                                     Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passRouteAbbrev, passStepNo, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelRoutesByRouteAbbrevStepNo", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@RouteAbbrev", passRouteAbbrev)
                da.SelectCommand.Parameters.AddWithValue("@StepNo", passStepNo)
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

#Region " Add Route Steps"
        Public Shared Sub AddRouteSteps(ByVal passRouteAbbrev As String, _
                                        ByVal passStepNo As Integer, _
                                        ByVal passStepShortDesc As String, _
                                        ByVal passStepDefinition As String, _
                                        ByVal passStartDateOffset As Integer, _
                                        ByVal passPlannedDuration As Integer, _
                                        Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passRouteAbbrev, _
                                                                                     passStepNo, _
                                                                                     passStepShortDesc, _
                                                                                     passStepDefinition, _
                                                                                     passStartDateOffset, _
                                                                                     passPlannedDuration, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsRouteSteps", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmAdd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@RouteAbbrev", passRouteAbbrev)
                    .Parameters.AddWithValue("@StepNo", passStepNo)
                    .Parameters.AddWithValue("@Step", passStepShortDesc)
                    .Parameters.AddWithValue("@StepDefinition", passStepDefinition)
                    .Parameters.AddWithValue("@StartDateOffset", passStartDateOffset)
                    .Parameters.AddWithValue("@PlannedDuration", passPlannedDuration)
                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " Update Route Steps"
        Public Shared Sub UpdateRouteSteps(ByVal passRouteAbbrev As String, _
                                           ByVal passStepNo As Integer, _
                                           ByVal passStepShortDesc As String, _
                                           ByVal passStepDefinition As String, _
                                           ByVal passStartDateOffset As Integer, _
                                           ByVal passPlannedDuration As Integer, _
                                           Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passRouteAbbrev, _
                                                                                     passStepNo, _
                                                                                     passStepShortDesc, _
                                                                                     passStepDefinition, _
                                                                                     passStartDateOffset, _
                                                                                     passPlannedDuration, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try


            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdRouteSteps", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@RouteAbbrev", passRouteAbbrev)
                    .Parameters.AddWithValue("@StepNo", passStepNo)
                    .Parameters.AddWithValue("@Step", passStepShortDesc)
                    .Parameters.AddWithValue("@StepDefinition", passStepDefinition)
                    .Parameters.AddWithValue("@StartDateOffset", passStartDateOffset)
                    .Parameters.AddWithValue("@PlannedDuration", passPlannedDuration)
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

#Region " Delete Route Steps"
        Public Shared Sub DeleteRouteSteps(ByVal passRouteAbbrev As String, ByVal passStepNo As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passRouteAbbrev, passStepNo, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelRouteSteps", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmDelete
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@RouteAbbrev", passRouteAbbrev)
                    .Parameters.AddWithValue("@StepNo", passStepNo)
                    .ExecuteNonQuery()
                    .Dispose()
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
