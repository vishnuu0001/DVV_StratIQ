#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class OEEReports

#Region " Select OEE Reports"
        Public Shared Function SelectOEEReports(ByVal passSiteID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSiteID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelOEEReports", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
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

#Region " AddOEEREPORTS"
        Public Shared Sub AddOEEREPORTS(ByVal passSiteID As Integer, _
                                             ByVal passWorkcenter As String, _
                                             ByVal passReport As String, _
                                             ByVal passURL As String, _
                                             Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passSiteID, _
                                                                                     passWorkcenter, _
                                                                                     passReport, _
                                                                                     passURL, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsOEEReports", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmAdd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@SiteID", passSiteID)
                    .Parameters.AddWithValue("@Workcenter", passWorkcenter)
                    .Parameters.AddWithValue("@Report", passReport)
                    .Parameters.AddWithValue("@URL", passURL)
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

#Region " Update OEE REPORTS"
        Public Shared Sub UpdateOEEREPORTS(ByVal passSiteID As Integer, _
                                                ByVal passWorkcenter As String, _
                                                ByVal passReport As String, _
                                                ByVal passURL As String, _
                                                Optional ByRef cnMasterConnection As SqlConnection = Nothing)

            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passSiteID, _
                                                                                     passWorkcenter, _
                                                                                     passReport, _
                                                                                     passURL, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdOEEReports", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@SiteID", passSiteID)
                    .Parameters.AddWithValue("@Workcenter", passWorkcenter)
                    .Parameters.AddWithValue("@Report", passReport)
                    .Parameters.AddWithValue("@URL", passURL)
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

#Region " Delete OEE REPORTS"
        Public Shared Sub DeleteOEEREPORTS(ByVal passSiteID As Integer, _
                                                ByVal passWorkcenter As String, _
                                                ByVal passReport As String, _
                                                Optional ByRef cnMasterConnection As SqlConnection = Nothing)

            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passSiteID, _
                                                                                     passWorkcenter, _
                                                                                     passReport, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelOEEReports", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmDelete
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@Site", passSiteID)
                    .Parameters.AddWithValue("@Workcenter", passWorkcenter)
                    .Parameters.AddWithValue("@Report", passReport)
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
