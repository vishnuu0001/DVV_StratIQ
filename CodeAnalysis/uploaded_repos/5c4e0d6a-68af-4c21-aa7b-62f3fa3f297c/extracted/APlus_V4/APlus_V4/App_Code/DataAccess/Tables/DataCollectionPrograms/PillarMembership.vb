#Region "Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class PillarMembership

#Region " Select Pillar Membership By Key"
        Public Shared Function SelectPillarMembershipByKey(ByVal passUserID As String, _
                                                           ByVal passPillarAbbrev As String, _
                                                           ByVal passSiteID As Integer, _
                                                           Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, passPillarAbbrev, passSiteID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelPillarMembershipByKey", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@UserId", passUserID)
                da.SelectCommand.Parameters.AddWithValue("@PillarAbbrev", passPillarAbbrev)
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
#End Region

#Region " Add Pillar Membership"
        Public Shared Sub AddPillarMembership(ByVal passUserID As String, _
                                              ByVal passPillarAbbrev As String, _
                                              ByVal passSiteID As Integer, _
                                              ByVal passRole As String, _
                                              ByVal passDateJoined As String, _
                                              ByVal passMaintenanceUserID As String, _
                                              Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passUserID, _
                                                                                     passPillarAbbrev, _
                                                                                     passSiteID, _
                                                                                     passRole, _
                                                                                     passDateJoined, _
                                                                                     passMaintenanceUserID, _
                                                                                     "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsPillarMembership", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmAdd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@UserId", passUserID)
                    .Parameters.AddWithValue("@PillarAbbrev", passPillarAbbrev)
                    .Parameters.AddWithValue("@SiteID", passSiteID)
                    If Not String.IsNullOrEmpty(passRole.Trim()) Then .Parameters.AddWithValue("@Role", passRole)
                    .Parameters.AddWithValue("@DateJoined", passDateJoined)
                    .Parameters.AddWithValue("@MaintenanceUserId", passMaintenanceUserID)
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

#Region " Update Pillar Membership"
        Public Shared Sub UpdatePillarMembership(ByVal passUserID As String, _
                                                 ByVal passPillarAbbrev As String, _
                                                 ByVal passSiteID As Integer, _
                                                 ByVal passRole As String, _
                                                 ByVal passDateJoined As String, _
                                                 ByVal passMaintenanceUserID As String, _
                                                 Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passUserID, _
                                                                                     passPillarAbbrev, _
                                                                                     passSiteID, _
                                                                                     passRole, _
                                                                                     passDateJoined, _
                                                                                     passMaintenanceUserID, _
                                                                                     "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdPillarMembership", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@UserId", passUserID)
                    .Parameters.AddWithValue("@PillarAbbrev", passPillarAbbrev)
                    .Parameters.AddWithValue("@SiteID", passSiteID)
                    If Not String.IsNullOrEmpty(passRole.Trim()) Then .Parameters.AddWithValue("@Role", passRole)
                    .Parameters.AddWithValue("@DateJoined", passDateJoined)
                    .Parameters.AddWithValue("@MaintenanceUserId", passMaintenanceUserID)
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

#Region " Delete Pillar Membership"
        Public Shared Sub DeletePillarMembership(ByVal passUserID As String, _
                                                 ByVal passPillarAbbrev As String, _
                                                 ByVal passSiteID As Integer, _
                                                 Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passUserID, _
                                                                                     passPillarAbbrev, _
                                                                                     passSiteID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelPillarMembership", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmDelete
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@UserId", passUserID)
                    .Parameters.AddWithValue("@PillarAbbrev", passPillarAbbrev)
                    .Parameters.AddWithValue("@SiteID", passSiteID)
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
