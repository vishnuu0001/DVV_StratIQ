#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class SecurityGroupProgramMaster

#Region " Select Security Group Program Master"
        Public Shared Function SelectSecurityGroupProgramMaster(ByVal passSecurityGroupID As Integer, _
                                                                ByVal passProgram As String, _
                                                                Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSecurityGroupID, passProgram, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelSecurityGroupProgramMasterByKey", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@SecurityGroupID", passSecurityGroupID)
                da.SelectCommand.Parameters.AddWithValue("@Program", passProgram)
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

#Region " Add Security Group Program Master"
        Public Shared Sub AddSecurityGroupProgramMaster(ByVal passSecurityGroupID As Integer, _
                                                        ByVal passProgram As String, _
                                                        ByVal passAllowAdd As Boolean, _
                                                        ByVal passAllowEdit As Boolean, _
                                                        ByVal passAllowDelete As Boolean, _
                                                        Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passSecurityGroupID, _
                                                                                     passProgram, _
                                                                                     passAllowAdd, _
                                                                                     passAllowEdit, _
                                                                                     passAllowDelete, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsSecurityGroupProgramMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmAdd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@SecurityGroupID", passSecurityGroupID)
                    .Parameters.AddWithValue("@Program", passProgram)
                    .Parameters.AddWithValue("@AllowAdd", passAllowAdd)
                    .Parameters.AddWithValue("@AllowEdit", passAllowEdit)
                    .Parameters.AddWithValue("@AllowDelete", passAllowDelete)
                    .ExecuteNonQuery()
                    .Dispose()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " Update Security Group Program Master"
        Public Shared Sub UpdateSecurityGroupProgramMaster(ByVal passSecurityGroupID As Integer, _
                                                           ByVal passProgram As String, _
                                                           ByVal passAllowAdd As Boolean, _
                                                           ByVal passAllowEdit As Boolean, _
                                                           ByVal passAllowDelete As Boolean, _
                                                           Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passSecurityGroupID, _
                                                                                     passProgram, _
                                                                                     passAllowAdd, _
                                                                                     passAllowEdit, _
                                                                                     passAllowDelete, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdSecurityGroupProgramMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@SecurityGroupID", passSecurityGroupID)
                    .Parameters.AddWithValue("@Program", passProgram)
                    .Parameters.AddWithValue("@AllowAdd", passAllowAdd)
                    .Parameters.AddWithValue("@AllowEdit", passAllowEdit)
                    .Parameters.AddWithValue("@AllowDelete", passAllowDelete)
                    .ExecuteNonQuery()
                    .Dispose()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " Delete Security Group Program Master"
        Public Shared Sub DeleteSecurityGroupProgramMaster(ByVal passSecurityGroupID As Integer, _
                                                           ByVal passProgram As String, _
                                                           Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSecurityGroupID, passProgram, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelSecurityGroupProgramMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmDelete
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@SecurityGroupID", passSecurityGroupID)
                    .Parameters.AddWithValue("@Program", passProgram)
                    .ExecuteNonQuery()
                    .Dispose()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try

        End Sub
#End Region

    End Class
End Namespace