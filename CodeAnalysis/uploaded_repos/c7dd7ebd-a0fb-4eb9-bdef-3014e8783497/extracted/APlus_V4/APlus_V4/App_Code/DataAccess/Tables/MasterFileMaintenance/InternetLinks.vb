#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class InternetLinks

#Region " Select, Add, Update & Delete"

#Region " - Select InternetLinks"
        Public Shared Function SelectInternetLinks(Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelInternetLinks", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
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

#Region " - Add InternetLinks"
        Public Shared Sub AddInternetLinks(ByVal passSequence As Integer, _
                                           ByVal passDescription As String, _
                                           ByVal passUrl As String, _
                                           Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSequence, passDescription, passUrl, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsInternetLinks", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                cmAdd.CommandType = CommandType.StoredProcedure
                cmAdd.Parameters.AddWithValue("@Sequence", passSequence)
                cmAdd.Parameters.AddWithValue("@Description", passDescription)
                cmAdd.Parameters.AddWithValue("@Url", passUrl)
                cmAdd.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " - Update InternetLinks"
        Public Shared Sub UpdateInternetLinks(ByVal passSequence As Integer, _
                                              ByVal passDescription As String, _
                                              ByVal passUrl As String, _
                                              Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSequence, passDescription, passUrl, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdInternetLinks", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                cmUpdate.CommandType = CommandType.StoredProcedure
                cmUpdate.Parameters.AddWithValue("@Sequence", passSequence)
                cmUpdate.Parameters.AddWithValue("@Description", passDescription)
                cmUpdate.Parameters.AddWithValue("@Url", passUrl)
                cmUpdate.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " - Delete InternetLinks"
        Public Shared Sub DeleteInternetLinks(ByVal passSequence As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSequence, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelInternetLinks", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                cmDelete.CommandType = CommandType.StoredProcedure
                cmDelete.Parameters.AddWithValue("@Sequence", passSequence)
                cmDelete.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmDelete.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#End Region

    End Class
End Namespace