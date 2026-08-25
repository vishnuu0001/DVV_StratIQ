#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports System.DirectoryServices
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class UserMasterAttributes

#Region " Add UserMasterAttributes"
        Public Shared Function AddUserMasterAttributes(ByVal passUserID As String, _
                                                       ByVal passAllTeamView As Boolean, ByVal passAllTeamEdit As Boolean, _
                                                       ByVal passAllKPIView As Boolean, ByVal passAllKPIEdit As Boolean, _
                                                       Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passUserID, passAllTeamView, passAllTeamEdit, passAllKPIView, passAllKPIEdit, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsUserMasterAttributes", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim blnValid As Boolean = False
            Try
                With cmAdd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@UserID", passUserID)
                    .Parameters.AddWithValue("@AllTeamView", passAllTeamView)
                    .Parameters.AddWithValue("@AllTeamEdit", passAllTeamEdit)
                    .Parameters.AddWithValue("@AllKPIView", passAllKPIView)
                    .Parameters.AddWithValue("@AllKPIEdit", passAllKPIEdit)
                    .ExecuteNonQuery()
                End With

                blnValid = True
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
            Return blnValid
        End Function
#End Region

#Region " Update UserMasterAttributes"
        Public Shared Sub UpdateUserMasterAttributes(ByVal passUserID As String, _
                                                     ByVal passAllTeamView As Boolean, ByVal passAllTeamEdit As Boolean, _
                                                     ByVal passAllKPIView As Boolean, ByVal passAllKPIEdit As Boolean, _
                                                     Optional ByRef cnMasterConnection As SqlConnection = Nothing)

            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passUserID, passAllTeamView, passAllTeamEdit, passAllKPIView, passAllKPIEdit, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdUserMasterAttributes", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@UserID", passUserID)
                    .Parameters.AddWithValue("@AllTeamView", passAllTeamView)
                    .Parameters.AddWithValue("@AllTeamEdit", passAllTeamEdit)
                    .Parameters.AddWithValue("@AllKPIView", passAllKPIView)
                    .Parameters.AddWithValue("@AllKPIEdit", passAllKPIEdit)
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

#Region " Delete UserMasterAttributes"
        Public Shared Sub DeleteUserMasterAttributes(ByVal passUserID As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelUserMasterAttributes", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmDelete
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@UserID", passUserID)
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
