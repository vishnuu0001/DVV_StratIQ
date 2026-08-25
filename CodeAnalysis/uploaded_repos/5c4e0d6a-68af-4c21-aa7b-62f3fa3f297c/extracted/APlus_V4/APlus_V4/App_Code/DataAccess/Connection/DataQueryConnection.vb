#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
#End Region

Namespace WebApp.APlus.DataAccess.Connections
    Public Class DataQueryConnection

#Region " Private Variables"
        Private cnSubConnection As New SqlConnection(ConfigurationManager.AppSettings("DataQueryConnectionString").ToString.Trim())
#End Region

#Region " Open Connection"
        Public Function OpenConnection(ByRef cnMasterConnection As SqlConnection) As SqlConnection
            If cnMasterConnection Is Nothing Then
                If cnSubConnection.State = ConnectionState.Closed Then
                    Try
                        cnSubConnection.Open()
                    Catch sxc As SqlClient.SqlException
                        'SQL Server Access denied or does not exist
                        If sxc.Number = 17 Then
                            SessionManager.ConnectionError = "Cannot connect to database. Please try again later."
                            HttpContext.Current.Response.Redirect("Login.aspx")
                        End If
                    End Try
                End If
                Return cnSubConnection
            Else
                Return cnMasterConnection
            End If
        End Function
        Public Shared Function OpenMasterConnection() As SqlConnection
            Dim cnMasterConnection As New SqlConnection(ConfigurationManager.AppSettings("DataQueryConnectionString").ToString)
            cnMasterConnection.Open()
            Return cnMasterConnection
        End Function
#End Region

#Region " Close Connection"
        Public Sub CloseConnection(ByRef cnMasterConnection As SqlConnection)
            If cnMasterConnection Is Nothing Then
                cnSubConnection.Close()
                cnSubConnection.Dispose()
            End If
        End Sub
#End Region

    End Class
End Namespace