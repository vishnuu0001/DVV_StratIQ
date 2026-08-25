#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class RouteStepsKeyActionsTools

#Region " Select RouteStep Key Action Tool"
        Public Shared Function SelectRouteStepsKeyActionsTool(ByVal passToolID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passToolID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Try
                Dim da As New SqlDataAdapter(New SqlCommand("spSelRouteStepsKeyActionsTool", cnSubConnection.OpenConnection(cnMasterConnection)))
                Dim ds As New DataTable
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@ToolID", passToolID)
                da.Fill(ds)
                da.Dispose()
                Return ds
            Catch Exc As Exception
                Throw
            Finally
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " Select Route Steps Key Actions Tools By Key Action"
        Public Shared Function SelectRouteStepsKeyActionsToolsByKeyAction(ByVal passRouteAbbrev As String, _
                                                                          ByVal passStepNumber As Integer, _
                                                                          ByVal passKeyActionNumber As Integer, _
                                                                          Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passRouteAbbrev, passStepNumber, passKeyActionNumber, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Try
                Dim da As New SqlDataAdapter(New SqlCommand("spSelRouteStepsKeyActionsToolsByKeyAction", cnSubConnection.OpenConnection(cnMasterConnection)))
                Dim ds As New DataTable
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@RouteAbbrev", passRouteAbbrev)
                da.SelectCommand.Parameters.AddWithValue("@StepNo", passStepNumber)
                da.SelectCommand.Parameters.AddWithValue("@KeyActionNo", passKeyActionNumber)
                da.Fill(ds)
                da.Dispose()
                Return ds
            Catch Exc As Exception
                Throw
            Finally
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " Add Route Steps Key Actions Tool"
        Public Shared Function AddRouteStepsKeyActionsTool(ByVal passTool As String, _
                                                      ByVal passRoute As String, _
                                                      ByVal passStep As Integer, _
                                                      ByVal passKeyAction As Integer, _
                                                      ByVal passURLLink As String, _
                                                      ByVal passAttachmentID As Integer, _
                                                      Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passTool, _
                                                                                     passRoute, _
                                                                                     passStep, _
                                                                                     passKeyAction, _
                                                                                     passURLLink, _
                                                                                     passAttachmentID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsRouteStepsKeyActionsTool", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmAdd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@Tool", passTool)
                    .Parameters.AddWithValue("@RouteAbbrev", passRoute)
                    .Parameters.AddWithValue("@StepNo", passStep)
                    .Parameters.AddWithValue("@KeyActionNo", passKeyAction)
                    If Not String.IsNullOrEmpty(passURLLink.Trim()) Then .Parameters.AddWithValue("@URLLink", passURLLink)
                    If passAttachmentID > 0 Then .Parameters.AddWithValue("@AttachmentID", passAttachmentID)
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

#Region " Update Route Steps Key Actions Tool"
        Public Shared Sub UpdateRouteStepsKeyActionsTool(ByVal passToolID As Integer, _
                                                         ByVal passTool As String, _
                                                         ByVal passURLLink As String, _
                                                         ByVal passAttachmentID As Integer, _
                                                         Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passToolID, _
                                                                                     passTool, _
                                                                                     passURLLink, _
                                                                                     passAttachmentID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdRouteStepsKeyActionsTool", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@ToolID", passToolID)
                    .Parameters.AddWithValue("@Tool", passTool)
                    If Not String.IsNullOrEmpty(passURLLink.Trim()) Then .Parameters.AddWithValue("@URLLink", passURLLink)
                    If passAttachmentID > 0 Then .Parameters.AddWithValue("@AttachmentID", passAttachmentID)
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

#Region " - DeleteRouteStepsKeyActionsTool"
        Public Shared Sub DeleteRouteStepsKeyActionsTool(ByVal passToolID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passToolID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelRouteStepsKeyActionsTool", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmDelete
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@ToolID", passToolID)
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

#Region " - Select RouteSteps Key Actions Tools By RouteAbbrev"
        Public Shared Function SelectRouteStepsKeyActionsToolsByRouteAbbrev(ByVal passRouteAbbrev As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
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
            Try
                Dim da As New SqlDataAdapter(New SqlCommand("spSelRouteStepsKeyActionsToolsByRouteAbbrev", cnSubConnection.OpenConnection(cnMasterConnection)))
                Dim ds As New DataTable
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@RouteAbbrev", passRouteAbbrev)
                da.Fill(ds)
                da.Dispose()
                Return ds
            Catch Exc As Exception
                Throw
            Finally
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

    End Class
End Namespace
