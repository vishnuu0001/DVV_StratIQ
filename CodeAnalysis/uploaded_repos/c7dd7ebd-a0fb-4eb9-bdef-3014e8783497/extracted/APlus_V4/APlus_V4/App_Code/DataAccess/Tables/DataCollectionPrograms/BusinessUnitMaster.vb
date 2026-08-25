#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class BusinessUnitMaster

#Region " Select Methods"
        Public Shared Sub SelectBusinessUnitMasterList(ByRef ddlList As System.Web.UI.WebControls.DropDownList, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelBusinessUnitMasterList", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    ddlList.Items.Add(New ListItem(drList.GetString(1), drList.GetInt32(0)))
                End While
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub SelectBusinessUnitMasterAbbrevList(ByRef ddlList As System.Web.UI.WebControls.DropDownList, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelBusinessUnitMasterList", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    ddlList.Items.Add(New ListItem(drList.GetString(2) & " - " & drList.GetString(1), drList.GetInt32(0)))
                End While
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Function SelectBusinessUnitByID(ByVal passBusinessUnitID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelBusinessUnitByID", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@BusinessUnitID", passBusinessUnitID)
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
        Public Shared Function InsertBusinessUnit(ByVal passBusinessUnit As String, ByVal passBusinessUnitAbbrev As String, _
        ByVal passBusinessAreaID As Integer, ByVal passActive As Boolean, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsBusinessUnitMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmAdd.CommandType = CommandType.StoredProcedure

                cmAdd.Parameters.AddWithValue("@BusinessUnit", passBusinessUnit)
                cmAdd.Parameters.AddWithValue("@BusinessUnitAbbrev", passBusinessUnitAbbrev)
                If passBusinessAreaID > 0 Then
                    cmAdd.Parameters.AddWithValue("@BusinessAreaID", passBusinessAreaID)
                End If
                cmAdd.Parameters.AddWithValue("@Active", passActive)

                Return cmAdd.ExecuteScalar
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Sub UpdateBusinessUnit(ByVal passBusinessUnitID As Integer, ByVal passBusinessUnit As String, ByVal passBusinessUnitAbbrev As String, _
        ByVal passBusinessAreaID As Integer, ByVal passActive As Boolean, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdBusinessUnitMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmUpdate.CommandType = CommandType.StoredProcedure

                cmUpdate.Parameters.AddWithValue("@BusinessUnitID", passBusinessUnitID)
                cmUpdate.Parameters.AddWithValue("@BusinessUnit", passBusinessUnit)
                cmUpdate.Parameters.AddWithValue("@BusinessUnitAbbrev", passBusinessUnitAbbrev)
                If passBusinessAreaID > 0 Then
                    cmUpdate.Parameters.AddWithValue("@BusinessAreaID", passBusinessAreaID)
                End If
                cmUpdate.Parameters.AddWithValue("@Active", passActive)

                cmUpdate.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub DeleteBusinessUnit(ByVal passBusinessUnitID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelBusinessUnitMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmDelete.CommandType = CommandType.StoredProcedure
                cmDelete.Parameters.AddWithValue("@BusinessUnitID", passBusinessUnitID)
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