#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class MenuProgramGroupMaster

#Region " Select MenuProgramGroups and Return Dropdownlist values"
        Public Shared Sub SelectProgramGroupsListByMenu(ByRef ddlList As System.Web.UI.WebControls.DropDownList, ByVal passMenu As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, ddlList.ID, passMenu, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelMenuProgramGroupMasterByMenu", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                ddlList.Items.Add(New ListItem("", ""))
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@Menu", passMenu)
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    ddlList.Items.Add(New ListItem(drList.GetString(0), drList.GetString(0)))
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

#Region " Select Menu Program Group"
        Public Shared Function SelectMenuProgramGroup(ByVal passMenu As String, ByVal passProgramGroup As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passMenu, passProgramGroup, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelMenuProgramGroup", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                With da
                    .SelectCommand.CommandType = CommandType.StoredProcedure
                    .SelectCommand.Parameters.AddWithValue("@Menu", passMenu)
                    .SelectCommand.Parameters.AddWithValue("@ProgramGroup", passProgramGroup)
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

#Region " Insert Menu Program Group"
        Public Shared Sub InsertMenuProgramGroup(ByVal passMenu As String, _
                                                  ByVal passProgramGroup As String, _
                                                  ByVal passMenuColumn As Integer, _
                                                  ByVal passSortOrder As Integer, _
                                                  Optional ByRef cnMasterConnection As SqlConnection = Nothing)

            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passMenu, _
                                                                                     passProgramGroup, _
                                                                                     passMenuColumn, _
                                                                                     passSortOrder, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmInsert As New SqlCommand("spInsMenuProgramGroupMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmInsert
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@Menu", passMenu)
                    .Parameters.AddWithValue("@ProgramGroup", passProgramGroup)
                    .Parameters.AddWithValue("@MenuColumn", passMenuColumn)
                    .Parameters.AddWithValue("@SortOrder", passSortOrder)
                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmInsert.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " Update Menu Program Group"
        Public Shared Sub UpdateMenuProgramGroup(ByVal passMenu As String, _
                                                 ByVal passProgramGroup As String, _
                                                 ByVal passMenuColumn As Integer, _
                                                 ByVal passSortOrder As Integer, _
                                                 Optional ByRef cnMasterConnection As SqlConnection = Nothing)

            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passMenu, _
                                                                                     passProgramGroup, _
                                                                                     passMenuColumn, _
                                                                                     passSortOrder, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdMenuProgramGroupMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@Menu", passMenu)
                    .Parameters.AddWithValue("@ProgramGroup", passProgramGroup)
                    .Parameters.AddWithValue("@MenuColumn", passMenuColumn)
                    .Parameters.AddWithValue("@SortOrder", passSortOrder)
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

#Region " Delete Menu Program Group"
        Public Shared Sub DeleteMenuProgramGroup(ByVal passMenu As String, _
                                                 ByVal passProgramGroup As String, _
                                                 Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passMenu, passProgramGroup, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelMenuProgramGroup", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmDelete
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@Menu", passMenu)
                    .Parameters.AddWithValue("@ProgramGroup", passProgramGroup)
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
