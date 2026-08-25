#Region "Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class RouteStepKeyActions

#Region " Select RouteStep Key Action"
        Public Shared Function SelectRouteStepKeyAction(ByVal passRouteAbbrev As String, _
                                                        ByVal passRouteStepNo As Integer, _
                                                        ByVal passKeyActionNo As Integer, _
                                                        Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passRouteAbbrev, passRouteStepNo, passKeyActionNo, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelRouteStepsKeyAction", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@RouteAbbrev", passRouteAbbrev)
                da.SelectCommand.Parameters.AddWithValue("@RouteStepNo", passRouteStepNo)
                da.SelectCommand.Parameters.AddWithValue("@KeyActionNo", passKeyActionNo)
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

#Region " Select Route Step Key Actions By Route Step"
        Public Shared Function SelectRouteStepKeyActionsByRouteStep(ByVal passRouteAbbrev As String, _
                                                                    ByVal passRouteStepNo As Integer, _
                                                                    Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passRouteAbbrev, passRouteStepNo, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelRouteStepsKeyActionsByRouteStep", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@RouteAbbrev", passRouteAbbrev)
                da.SelectCommand.Parameters.AddWithValue("@RouteStepNo", passRouteStepNo)
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

#Region " Add Route Steps KeyAction"
        Public Shared Sub AddRouteStepsKeyAction(ByVal passRouteAbbrev As String, _
                                                 ByVal passStepNo As Integer, _
                                                 ByVal passKeyActionNo As Integer, _
                                                 ByVal passKeyAction As String, _
                                                 Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passRouteAbbrev, _
                                                                                     passStepNo, _
                                                                                     passKeyActionNo, _
                                                                                     passKeyAction, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsRouteStepsKeyAction", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmAdd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@RouteAbbrev", passRouteAbbrev)
                    .Parameters.AddWithValue("@StepNo", passStepNo)
                    .Parameters.AddWithValue("@KeyActionNo", passKeyActionNo)
                    .Parameters.AddWithValue("@KeyAction", passKeyAction)
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

#Region " Update Route Steps Key Action"
        Public Shared Sub UpdateRouteStepsKeyAction(ByVal passRouteAbbrev As String, _
                                                    ByVal passStepNo As Integer, _
                                                    ByVal passKeyActionNo As Integer, _
                                                    ByVal passKeyAction As String, _
                                                    Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passRouteAbbrev, _
                                                                                     passStepNo, _
                                                                                     passKeyActionNo, _
                                                                                     passKeyAction, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdRouteStepsKeyAction", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@RouteAbbrev", passRouteAbbrev)
                    .Parameters.AddWithValue("@StepNo", passStepNo)
                    .Parameters.AddWithValue("@KeyActionNo", passKeyActionNo)
                    .Parameters.AddWithValue("@KeyAction", passKeyAction)
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

#Region " Delete Route Steps Key Action"
        Public Shared Sub DeleteRouteStepsKeyAction(ByVal passRouteAbbrev As String, _
                                                    ByVal passStepNo As Integer, _
                                                    ByVal passKeyActionNo As Integer, _
                                                    Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passRouteAbbrev, _
                                                                                     passStepNo, _
                                                                                     passKeyActionNo, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelRouteStepsKeyAction", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmDelete
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@RouteAbbrev", passRouteAbbrev)
                    .Parameters.AddWithValue("@RouteStepNo", passStepNo)
                    .Parameters.AddWithValue("@KeyActionNo", passKeyActionNo)
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