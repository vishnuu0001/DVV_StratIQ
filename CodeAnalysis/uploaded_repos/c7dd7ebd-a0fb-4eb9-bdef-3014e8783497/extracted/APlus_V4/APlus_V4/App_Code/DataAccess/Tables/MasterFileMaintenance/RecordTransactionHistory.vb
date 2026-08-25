#Region "Imports"
Imports System.Text
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class RecordTransactionHistory

#Region " - Insert Record Transaction History "
        Public Shared Sub InsertRecordTransactionHistory(ByVal passTableName As String, _
                                                         ByVal passRecordID As String, _
                                                         ByVal passChangeLog As String, _
                                                         ByVal passUserID As String, _
                                                         Optional ByRef cnMasterConnection As SqlConnection = Nothing, _
                                                         Optional ByRef trans As SqlTransaction = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTableName, passRecordID, passChangeLog, passUserID, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsRecordTransactionHistory", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmAdd
                    If Not trans Is Nothing Then
                        .Transaction = trans
                    End If
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@TableName", passTableName)
                    .Parameters.AddWithValue("@RecordID", passRecordID)
                    .Parameters.AddWithValue("@RecordInformation", passChangeLog.Trim())
                    .Parameters.AddWithValue("@UserID", passUserID)
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

#Region " - Select Record Transaction History "
        Public Shared Function SelectRecordTransactionHistory(ByVal passTableName As String, ByVal passRecordID As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTableName, passRecordID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelRecordTransactionHistoryByTableNameRecordID", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                With da
                    .SelectCommand.CommandType = CommandType.StoredProcedure
                    .SelectCommand.Parameters.AddWithValue("@TableName", passTableName)
                    .SelectCommand.Parameters.AddWithValue("@RecordID", passRecordID)
                    .Fill(dt)
                End With
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