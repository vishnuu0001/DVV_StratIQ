#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class AnomalyAttachments

#Region " Select Methods"
        Public Shared Function SelectAnomalyAttachments(ByVal passAnomalyID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelAnomalyAttachments", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@AnomalyID", passAnomalyID)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectAnomalyAttachmentByID(ByVal passAttachmentID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelAnomalyAttachmentByID", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@AttachmentID", passAttachmentID)
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

#Region " Table Methods"
        Public Shared Function InsertAttachment(ByVal passAnomalyID As Integer, ByVal passFileName As String, ByVal passFileAttachment As Byte(), _
                                                Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Boolean
            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsAnomalyAttachment", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmAdd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@AnomalyID", passAnomalyID)
                    .Parameters.AddWithValue("@FileName", passFileName)
                    .Parameters.AddWithValue("@FileAttachment", passFileAttachment)
                    .ExecuteNonQuery()
                End With

                Return True
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try

            Return False
        End Function
        Public Shared Function DeleteAttachment(ByVal passAttachmentID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Boolean
            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spDelAnomalyAttachmentByID", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmAdd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@AttachmentID", passAttachmentID)
                    .ExecuteNonQuery()
                End With

                Return True
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try

            Return False
        End Function
#End Region

    End Class
End Namespace
