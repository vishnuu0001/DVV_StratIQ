#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class ReportMaster

#Region " Select Methods"
        Public Shared Function SelectReportMasterByID(ByVal passReportID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Dim cnSubConnection As New ApplicationConnection
            Try
                Dim da As New SqlDataAdapter(New SqlCommand("spSelReportMasterByID", cnSubConnection.OpenConnection(cnMasterConnection)))
                Dim ds As New DataTable
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@ReportID", passReportID)
                da.Fill(ds)
                da.Dispose()
                Return ds
            Catch Exc As Exception
                Throw
            Finally
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectReportMasterByReportKey(ByVal passReportKey As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Dim cnSubConnection As New ApplicationConnection
            Try
                Dim da As New SqlDataAdapter(New SqlCommand("spSelReportMasterByReportKey", cnSubConnection.OpenConnection(cnMasterConnection)))
                Dim ds As New DataTable
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@ReportKey", passReportKey)
                da.Fill(ds)
                da.Dispose()
                Return ds
            Catch Exc As Exception
                Throw
            Finally
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Sub GetReportMasterList(ByRef ddlList As System.Web.UI.WebControls.DropDownList, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, ddlList.ID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelReportMasterList", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    ddlList.Items.Add(New ListItem(drList.Item("ReportKey").ToString, drList.Item("ReportID").ToString))
                End While
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

    End Class
End Namespace
