#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
#End Region

Namespace WebApp.APlus.DataAccess.Connections
    Public Class CultureTranslationConnection

#Region " Private Variables"
        Private cnCultureTranslationConnection As New SqlConnection(ConfigurationManager.AppSettings("CultureTranslationConnectionString").ToString.Trim())
#End Region

#Region " Open CultureTranslationConnection"
        Public Function OpenCultureTranslationConnection(ByRef cnMasterConnection As SqlConnection) As SqlConnection
            If cnMasterConnection Is Nothing Then
                If cnCultureTranslationConnection.State = ConnectionState.Closed Then
                    Try
                        cnCultureTranslationConnection.Open()
                    Catch sxc As SqlClient.SqlException
                        'SQL Server Access denied or does not exist
                        If sxc.Number = 17 Then
                            SessionManager.ConnectionError = "Cannot connect to database. Please try again later."
                            HttpContext.Current.Response.Redirect("Login.aspx")
                        End If
                    End Try
                End If
                Return cnCultureTranslationConnection
            Else
                Return cnMasterConnection
            End If
        End Function
#End Region

#Region " Close Connection"
        Public Sub CloseCultureTranslationConnection(ByRef cnMasterConnection As SqlConnection)
            If cnMasterConnection Is Nothing Then
                cnCultureTranslationConnection.Close()
                cnCultureTranslationConnection.Dispose()
            End If
        End Sub
#End Region

    End Class
End Namespace