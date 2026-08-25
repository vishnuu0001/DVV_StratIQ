#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class MenuMaster

#Region " Select Menu Master By Key"
        Public Shared Function SelectMenuMasterByKey(ByVal passMenu As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passMenu, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelMenuMasterByKey", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@Menu", passMenu)
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

#Region " Update Menu"
        Public Shared Sub UpdateMenu(ByVal passMenu As String, _
                                     ByVal passMenuText As String, _
                                     ByVal passMenuType As String, _
                                     ByVal passShowProgramGroups As Boolean, _
                                     ByVal passAllowProgramShortcuts As Boolean, _
                                     ByVal passShowProgramShortcuts As Boolean, _
                                     ByVal passMaxColumns As Integer, _
                                     ByVal passAllowUserSpecifiedColumns As Boolean, _
                                     ByVal passHideOptionNumbers As Boolean, _
                                     Optional ByRef cnMasterConnection As SqlConnection = Nothing)

            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passMenu, _
                                                                                     passMenuText, _
                                                                                     passMenuType, _
                                                                                     passShowProgramGroups, _
                                                                                     passAllowProgramShortcuts, _
                                                                                     passShowProgramShortcuts, _
                                                                                     passMaxColumns, _
                                                                                     passAllowUserSpecifiedColumns, _
                                                                                     passHideOptionNumbers, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdMenuMaster", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@Menu", passMenu)
                    .Parameters.AddWithValue("@MenuText", passMenuText)
                    .Parameters.AddWithValue("@MenuType", passMenuType)
                    .Parameters.AddWithValue("@ShowProgramGroups", passShowProgramGroups)
                    .Parameters.AddWithValue("@AllowProgramShortcuts", passAllowProgramShortcuts)
                    .Parameters.AddWithValue("@ShowProgramShortcuts", passShowProgramShortcuts)
                    .Parameters.AddWithValue("@HideOptionNumbers", passHideOptionNumbers)
                    .Parameters.AddWithValue("@AllowUserSpecifiedColumns", passAllowUserSpecifiedColumns)
                    .Parameters.AddWithValue("@MaxColumns", passMaxColumns)
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

#Region " Delete Menu"
        Public Shared Sub DeleteMenu(ByVal passMenu As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passMenu, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelMenuMaster", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                cmDelete.CommandType = CommandType.StoredProcedure
                cmDelete.Parameters.AddWithValue("@Menu", passMenu)
                cmDelete.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmDelete.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " Insert Menu"
        Public Shared Sub InsertMenu(ByVal passMenu As String, _
                                     ByVal passMenuText As String, _
                                     ByVal passMenuType As String, _
                                     ByVal passShowProgramGroups As Boolean, _
                                     ByVal passAllowProgramShortcuts As Boolean, _
                                     ByVal passShowProgramShortcuts As Boolean, _
                                     ByVal passMaxColumns As Integer, _
                                     ByVal passAllowUserSpecifiedColumns As Boolean, _
                                     ByVal passHideOptionNumbers As Boolean, _
                                     Optional ByRef cnMasterConnection As SqlConnection = Nothing)

            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passMenu, _
                                                                                     passMenuText, _
                                                                                     passMenuType, _
                                                                                     passShowProgramGroups, _
                                                                                     passAllowProgramShortcuts, _
                                                                                     passShowProgramShortcuts, _
                                                                                     passMaxColumns, _
                                                                                     passAllowUserSpecifiedColumns, _
                                                                                     passHideOptionNumbers, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmInsert As New SqlCommand("spInsMenuMaster", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmInsert
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@Menu", passMenu)
                    .Parameters.AddWithValue("@MenuText", passMenuText)
                    .Parameters.AddWithValue("@MenuType", passMenuType)
                    .Parameters.AddWithValue("@ShowProgramGroups", passShowProgramGroups)
                    .Parameters.AddWithValue("@AllowProgramShortcuts", passAllowProgramShortcuts)
                    .Parameters.AddWithValue("@ShowProgramShortcuts", passShowProgramShortcuts)
                    .Parameters.AddWithValue("@HideOptionNumbers", passHideOptionNumbers)
                    .Parameters.AddWithValue("@AllowUserSpecifiedColumns", passAllowUserSpecifiedColumns)
                    .Parameters.AddWithValue("@MaxColumns", passMaxColumns)
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

    End Class
End Namespace
