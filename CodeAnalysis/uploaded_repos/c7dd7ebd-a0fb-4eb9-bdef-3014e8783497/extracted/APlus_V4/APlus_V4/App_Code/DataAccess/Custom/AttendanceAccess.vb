#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports System.Web.Security
Imports System.DirectoryServices
Imports WebApp.APlus.DataAccess.Connections
Imports WebApp.APlus.DataAccess.Tables

#End Region

Namespace WebApp.APlus.DataAccess.Custom
    Public Class AttendanceAccess

#Region " - Select UserMaster"
        Public Shared Function SelectUserMaster(ByVal passUserID As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New AttendanceConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelUser", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@UserID", passUserID)
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

    End Class
End Namespace