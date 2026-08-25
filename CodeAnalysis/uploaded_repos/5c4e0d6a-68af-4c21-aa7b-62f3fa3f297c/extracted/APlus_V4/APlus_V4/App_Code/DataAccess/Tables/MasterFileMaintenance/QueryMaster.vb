#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class QueryMaster

#Region " Select Query"
        Public Shared Function SelectQuery(ByVal passQueryID As Long, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataSet
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passQueryID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelQueryMaster", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim ds As New DataSet
            Try
                With da
                    .SelectCommand.Parameters.AddWithValue("@QueryID", passQueryID)
                    .SelectCommand.CommandType = CommandType.StoredProcedure
                    .Fill(ds)
                End With
                Return ds
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " Update Query Master"
        Public Shared Sub UpdateQueryMaster(ByVal passQueryID As Long, _
                                                 ByVal passSiteID As Integer, _
                                                 ByVal passDescription As String, _
                                                 ByVal passQuerySelect As String, _
                                                 ByVal passQueryFrom As String, _
                                                 ByVal passQueryWhere As String, _
                                                 ByVal passQueryGroupBy As String, _
                                                 ByVal passQueryOrderBy As String, _
                                                 ByVal passUserID As String, _
                                                 Optional ByRef cnMasterConnection As SqlConnection = Nothing)

            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passQueryID, _
                                                                                     passSiteID, _
                                                                                     passDescription, _
                                                                                     passQuerySelect, _
                                                                                     passQueryFrom, _
                                                                                     passQueryWhere, _
                                                                                     passQueryGroupBy, _
                                                                                     passQueryOrderBy, _
                                                                                     passUserID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdQueryMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@QueryID", passQueryID)
                    If passSiteID > 0 Then .Parameters.AddWithValue("@SiteID", passSiteID)
                    .Parameters.AddWithValue("@QueryDescription", passDescription.Trim)
                    .Parameters.AddWithValue("@QuerySelect", passQuerySelect.Trim)
                    .Parameters.AddWithValue("@QueryFrom", passQueryFrom.Trim)
                    .Parameters.AddWithValue("@QueryWhere", passQueryWhere.Trim)
                    .Parameters.AddWithValue("@QueryGroupBy", passQueryGroupBy.Trim)
                    .Parameters.AddWithValue("@QueryOrderBy", passQueryOrderBy.Trim)
                    .Parameters.AddWithValue("@MaintenanceUserID", passUserID)
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

#Region " Insert Query Master"
        Public Shared Sub InsertQueryMaster(ByVal passSiteID As Integer, _
                                            ByVal passDescription As String, _
                                            ByVal passQuerySelect As String, _
                                            ByVal passQueryFrom As String, _
                                            ByVal passQueryWhere As String, _
                                            ByVal passQueryGroupBy As String, _
                                            ByVal passQueryOrderBy As String, _
                                            ByVal passUserID As String, _
                                            Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passSiteID, _
                                                                                     passDescription, _
                                                                                     passQuerySelect, _
                                                                                     passQueryFrom, _
                                                                                     passQueryWhere, _
                                                                                     passQueryGroupBy, _
                                                                                     passQueryOrderBy, _
                                                                                     passUserID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try
            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spInsQueryMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    If passSiteID > 0 Then .Parameters.AddWithValue("@SiteID", passSiteID)
                    .Parameters.AddWithValue("@QueryDescription", passDescription.Trim)
                    .Parameters.AddWithValue("@QuerySelect", passQuerySelect.Trim)
                    .Parameters.AddWithValue("@QueryFrom", passQueryFrom.Trim)
                    .Parameters.AddWithValue("@QueryWhere", passQueryWhere.Trim)
                    .Parameters.AddWithValue("@QueryGroupBy", passQueryGroupBy.Trim)
                    .Parameters.AddWithValue("@QueryOrderBy", passQueryOrderBy.Trim)
                    .Parameters.AddWithValue("@CreatedUserID", passUserID)
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

#Region " Delete Query Master"
        Public Shared Sub DeleteQueryMaster(ByVal passQueryID As Long, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passQueryID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelQueryMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmDelete.CommandType = CommandType.StoredProcedure
                cmDelete.Parameters.AddWithValue("@QueryID", passQueryID)
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
