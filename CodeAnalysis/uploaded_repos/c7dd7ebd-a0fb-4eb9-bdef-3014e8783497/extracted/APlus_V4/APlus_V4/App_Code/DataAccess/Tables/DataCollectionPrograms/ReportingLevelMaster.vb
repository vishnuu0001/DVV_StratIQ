#Region "Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class ReportingLevelMaster

#Region " Select Methods"
        Public Shared Sub GetReportingLevelList(ByRef ddlList As System.Web.UI.WebControls.DropDownList, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, ddlList.ID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelReportingLevelMaster", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    ddlList.Items.Add(New ListItem(drList(1), drList(0)))
                End While
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Function SelectReportingLevelMaster(ByVal passReportingLevelID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passReportingLevelID.ToString, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelReportingLevelMasterByID", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@ReportingLevelID", passReportingLevelID)
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
        Public Shared Function AddReportingLevelMaster(ByVal passReportingLevelDescription As String, ByVal passReportingLevelAbbrev As String, _
                                                       ByVal passReportingLevel As Integer, _
                                                       Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passReportingLevelDescription, passReportingLevelAbbrev, passReportingLevel.ToString, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsReportingLevelMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmAdd.CommandType = CommandType.StoredProcedure
                cmAdd.Parameters.AddWithValue("@ReportingLevelDescription", passReportingLevelDescription)
                cmAdd.Parameters.AddWithValue("@ReportingLevelAbbrev", passReportingLevelAbbrev)
                cmAdd.Parameters.AddWithValue("@ReportingLevel", passReportingLevel)

                Return cmAdd.ExecuteScalar
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Sub UpdateReportingLevelMaster(ByVal passReportingLevelID As Integer, ByVal passReportingLevelAbbrev As String, _
                                                     ByVal passReportingLevelDescription As String, ByVal passReportingLevel As Integer, _
                                                     Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passReportingLevelID.ToString, passReportingLevelDescription, passReportingLevelAbbrev, passReportingLevel.ToString, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdReportingLevelMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmUpdate.CommandType = CommandType.StoredProcedure
                cmUpdate.Parameters.AddWithValue("@ReportingLevelID", passReportingLevelID)
                cmUpdate.Parameters.AddWithValue("@ReportingLevelDescription", passReportingLevelDescription)
                cmUpdate.Parameters.AddWithValue("@ReportingLevelAbbrev", passReportingLevelAbbrev)
                cmUpdate.Parameters.AddWithValue("@ReportingLevel", passReportingLevel)

                cmUpdate.ExecuteNonQuery()
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub DeleteReportingLevelMaster(ByVal passReportingLevelID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passReportingLevelID.ToString, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelReportingLevelMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmDelete.CommandType = CommandType.StoredProcedure
                cmDelete.Parameters.AddWithValue("@ReportingLevelID", passReportingLevelID)
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
