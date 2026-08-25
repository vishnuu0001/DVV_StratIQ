#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class QueryParametersMaster

#Region " Select Query Parameters Master"
        Public Shared Function SelectQueryParametersMaster(ByVal passQueryID As Long, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passQueryID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelQueryParametersMaster", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim ds As New DataTable

            Try
                With da
                    .SelectCommand.Parameters.AddWithValue("@QueryID", passQueryID)
                    .SelectCommand.CommandType = CommandType.StoredProcedure
                    .Fill(ds)
                End With
                Return ds
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " Select Query Parameter"
        Public Shared Function SelectQueryParameter(ByVal passQueryID As Long, ByVal passParameter As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passQueryID, passParameter, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelQueryParameter", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim ds As New DataTable

            Try
                With da
                    .SelectCommand.Parameters.AddWithValue("@QueryID", passQueryID)
                    .SelectCommand.Parameters.AddWithValue("@QueryParameter", passParameter)
                    .SelectCommand.CommandType = CommandType.StoredProcedure
                    .Fill(ds)
                End With

                Return ds
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " Update Query Parameters Master"
        Public Shared Sub UpdateQueryParametersMaster(ByVal passQueryID As Long, _
                                                      ByVal passParameter As String, _
                                                      ByVal passParameterPrompt As String, _
                                                      ByVal passParameterType As String, _
                                                      ByVal passParameterDefaultValue As String, _
                                                      ByVal passShowInputPrompt As Boolean, _
                                                      Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passQueryID, _
                                                                                     passParameter, _
                                                                                     passParameterPrompt, _
                                                                                     passParameterType, _
                                                                                     passParameterDefaultValue, _
                                                                                     passShowInputPrompt, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdQueryParametersMaster", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@QueryID", passQueryID)
                    .Parameters.AddWithValue("@QueryParameter", passParameter.Trim)
                    .Parameters.AddWithValue("@ParameterPrompt", passParameterPrompt.Trim)
                    .Parameters.AddWithValue("@ParameterType", passParameterType.Trim)
                    If passParameterDefaultValue.Trim.Length > 0 Then
                        .Parameters.AddWithValue("@ParameterDefaultValue", passParameterDefaultValue.Trim)
                    End If
                    .Parameters.AddWithValue("@ShowInputPrompt", passShowInputPrompt)
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

#Region " Insert Query Parameters Master"
        Public Shared Sub InsertQueryParametersMaster(ByVal passQueryID As Long, _
                                                      ByVal passParameter As String, _
                                                      ByVal passParameterPrompt As String, _
                                                      ByVal passParameterType As String, _
                                                      ByVal passParameterDefaultValue As String, _
                                                      ByVal passShowInputPrompt As Boolean, _
                                                      Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passQueryID, _
                                                                                     passParameter, _
                                                                                     passParameterPrompt, _
                                                                                     passParameterType, _
                                                                                     passParameterDefaultValue, _
                                                                                     passShowInputPrompt, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spInsQueryParametersMaster", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@QueryID", passQueryID)
                    .Parameters.AddWithValue("@QueryParameter", passParameter.Trim)
                    .Parameters.AddWithValue("@ParameterPrompt", passParameterPrompt.Trim)
                    .Parameters.AddWithValue("@ParameterType", passParameterType.Trim)
                    If passParameterDefaultValue.Trim.Length > 0 Then
                        .Parameters.AddWithValue("@ParameterDefaultValue", passParameterDefaultValue.Trim)
                    End If
                    .Parameters.AddWithValue("@ShowInputPrompt", passShowInputPrompt)
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

#Region " Delete Query Parameters Master"
        Public Shared Sub DeleteQueryParametersMaster(ByVal passQueryID As Long, ByVal passParameter As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passQueryID, passParameter, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelQueryParametersMaster", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmDelete
                    cmDelete.CommandType = CommandType.StoredProcedure
                    cmDelete.Parameters.AddWithValue("@QueryID", passQueryID)
                    cmDelete.Parameters.AddWithValue("@QueryParameter", passParameter.Trim)
                    cmDelete.ExecuteNonQuery()
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
