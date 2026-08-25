#Region "Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class UserSiteMaster

#Region " Select Methods"
        Public Shared Function SelectUserSiteMaster(ByVal passUserID As String, ByVal passSiteID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSiteID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelUserSiteMasterByKey", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@UserID", passUserID)
                da.SelectCommand.Parameters.AddWithValue("@SiteID", passSiteID)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectTeamAllowEdit(ByVal passTeamID As Integer, ByVal passUserID As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, passUserID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTeamAllowEdit", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim ds As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TeamID", passTeamID)
                da.SelectCommand.Parameters.AddWithValue("@UserID", passUserID)
                da.Fill(ds)
                If ds.Rows.Count > 0 Then
                    Return Convert.ToBoolean(ds.Rows(0).Item("AllowEdit"))
                Else
                    Return False
                End If
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " Table Methods"
        Public Shared Sub AddUserSiteMaster(ByVal passUserID As String, ByVal passSiteID As String, _
                                            ByVal passAllowTeamView As Boolean, ByVal passAllowTeamEdit As Boolean, _
                                            ByVal passAllowKPIView As Boolean, ByVal passAllowKPIEdit As Boolean, _
                                            Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, passSiteID, passAllowTeamView, passAllowTeamEdit, passAllowKPIView, passAllowKPIEdit, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsUserSiteMaster", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                cmAdd.CommandType = CommandType.StoredProcedure
                cmAdd.Parameters.AddWithValue("@UserID", passUserID)
                cmAdd.Parameters.AddWithValue("@SiteID", passSiteID)
                cmAdd.Parameters.AddWithValue("@AllowTeamView", passAllowTeamView)
                cmAdd.Parameters.AddWithValue("@AllowTeamEdit", passAllowTeamEdit)
                cmAdd.Parameters.AddWithValue("@AllowKPIView", passAllowKPIView)
                cmAdd.Parameters.AddWithValue("@AllowKPIEdit", passAllowKPIEdit)
                cmAdd.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub UpdateUserSiteMaster(ByVal passUserID As String, ByVal passSiteID As String, _
                                            ByVal passAllowTeamView As Boolean, ByVal passAllowTeamEdit As Boolean, _
                                            ByVal passAllowKPIView As Boolean, ByVal passAllowKPIEdit As Boolean, _
                                            Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, passSiteID, passAllowTeamView, passAllowTeamEdit, passAllowKPIView, passAllowKPIEdit, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spUpdUserSiteMaster", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                cmAdd.CommandType = CommandType.StoredProcedure
                cmAdd.Parameters.AddWithValue("@UserID", passUserID)
                cmAdd.Parameters.AddWithValue("@SiteID", passSiteID)
                cmAdd.Parameters.AddWithValue("@AllowTeamView", passAllowTeamView)
                cmAdd.Parameters.AddWithValue("@AllowTeamEdit", passAllowTeamEdit)
                cmAdd.Parameters.AddWithValue("@AllowKPIView", passAllowKPIView)
                cmAdd.Parameters.AddWithValue("@AllowKPIEdit", passAllowKPIEdit)
                cmAdd.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub DeleteUserSiteMaster(ByVal passUserID As String, ByVal passSiteID As String, _
                                               Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, passSiteID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelUserSiteMaster", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                cmDelete.CommandType = CommandType.StoredProcedure
                cmDelete.Parameters.AddWithValue("@UserID", passUserID)
                cmDelete.Parameters.AddWithValue("@SiteID", passSiteID)
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