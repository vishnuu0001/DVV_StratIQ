#Region "Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class UserSecurityGroupMaster

#Region " Add UserSecurityGroupMaster"
        Public Shared Sub AddUserSecurityGroupMaster(ByVal passUserID As String, _
                                                     ByVal passSecurityGroupID As Integer, _
                                                     Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, passSecurityGroupID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsUserSecurityGroup", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                cmAdd.CommandType = CommandType.StoredProcedure
                cmAdd.Parameters.AddWithValue("@UserID", passUserID)
                cmAdd.Parameters.AddWithValue("@SecurityGroupId", passSecurityGroupID)
                cmAdd.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " Delete UserSecurityGroupMaster"
        Public Shared Sub DeleteUserSecurityGroupMaster(ByVal passUserID As String, _
                                             ByVal passSecurityGroupID As Integer, _
                                             Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, passSecurityGroupID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelUserSecurityGroupMaster", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                cmDelete.CommandType = CommandType.StoredProcedure
                cmDelete.Parameters.AddWithValue("@UserID", passUserID)
                cmDelete.Parameters.AddWithValue("@SecurityGroupID", passSecurityGroupID)
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