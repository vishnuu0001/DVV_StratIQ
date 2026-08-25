#Region "Imports"
Imports System.Text
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class ProgramMaster

#Region " Get Menu List "
        Public Shared Sub GetMenuList(ByRef ddlMenuList As System.Web.UI.WebControls.DropDownList, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, ddlMenuList.ID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmList As New SqlCommand("spSelMenuList", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmList.CommandType = CommandType.StoredProcedure
                drList = cmList.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    ddlMenuList.Items.Add(New ListItem(drList.GetString(0), drList.GetString(0)))
                End While
            Catch Exc As Exception
                Throw
            Finally
                cmList.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " Program Is Menu"
        Public Shared Function ProgramIsMenu(ByVal passProgram As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passProgram, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmProgramMenuYN As New SqlCommand("spSelProgramMasterMenuYN", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim myParm As New SqlParameter

            With cmProgramMenuYN
                .CommandType = CommandType.StoredProcedure
                Try
                    .Parameters.AddWithValue("@Program", passProgram)
                    myParm = .Parameters.AddWithValue("@MenuYN", SqlDbType.Bit)
                    myParm.Direction = ParameterDirection.Output
                    .ExecuteNonQuery()
                    Return CBool(.Parameters("@MenuYN").Value)
                Catch Exc As Exception
                    Return False
                Finally
                    cnSubConnection.CloseConnection(cnMasterConnection)
                    .Dispose()
                End Try
            End With
        End Function
#End Region

#Region " Get Team Board Program List"
        Public Shared Sub GetTeamBoardProgramList(ByRef ddlProgramList As System.Web.UI.WebControls.DropDownList, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, ddlProgramList.ID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmList As New SqlCommand("spSelTeamBoardProgramList", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmList.CommandType = CommandType.StoredProcedure
                drList = cmList.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    ddlProgramList.Items.Add(New ListItem(drList.GetString(1), drList.GetString(2) + "-" + drList.GetString(0)))
                End While
            Catch Exc As Exception
                Throw
            Finally
                cmList.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " Get Program List"
        Public Shared Sub GetProgramList(ByRef ddlProgramList As System.Web.UI.WebControls.DropDownList, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, ddlProgramList.ID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmList As New SqlCommand("spSelProgramList", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmList.CommandType = CommandType.StoredProcedure
                drList = cmList.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    ddlProgramList.Items.Add(New ListItem(drList.GetString(0), drList.GetString(0)))
                End While
            Catch Exc As Exception
                Throw
            Finally
                cmList.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " Get Menu Program List"
        Public Shared Sub GetMenuProgramList(ByRef ddlMenuList As System.Web.UI.WebControls.DropDownList, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, ddlMenuList.ID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmList As New SqlCommand("spSelProgramMenuList", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmList.CommandType = CommandType.StoredProcedure
                drList = cmList.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    ddlMenuList.Items.Add(New ListItem(drList.GetString(0), drList.GetString(0)))
                End While
                ddlMenuList.Items.Insert(0, New ListItem("", ""))
            Catch Exc As Exception
                Throw
            Finally
                cmList.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " Get InitialProgram List "
        Public Shared Sub GetInitialProgramList(ByRef ddlInitialProgramList As System.Web.UI.WebControls.DropDownList, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, ddlInitialProgramList.ID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmList As New SqlCommand("spSelInitialProgram", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmList.CommandType = CommandType.StoredProcedure
                drList = cmList.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    ddlInitialProgramList.Items.Add(New ListItem(drList.GetString(0), drList.GetString(0)))
                End While
            Catch Exc As Exception
                Throw
            Finally
                cmList.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " Get Help File"
        Public Shared Function GetHelpFile(ByVal passProgramURL As String, Optional ByRef cnMasterConnection As SqlClient.SqlConnection = Nothing) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passProgramURL, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelAttachmentsByProgram", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@ProgramURL", passProgramURL)
                da.SelectCommand.Parameters.AddWithValue("@AttachmentTypeID", 2)
                da.Fill(dt)

                If dt.Rows.Count > 0 Then
                    Return dt.Rows(0)("Attachment").ToString.Trim
                Else
                    Return ""
                End If
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " Select Program Master"
        Public Shared Function SelectProgramMaster(ByVal passProgram As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passProgram, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelProgramMaster1", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim ds As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@Program", passProgram)
                da.Fill(ds)
                Return ds
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " Add Program Master"
        Public Shared Sub AddProgramMaster(ByVal passProgram As String, ByVal passProgramURL As String, ByVal passMenuYN As Boolean, _
                                           ByVal passInitialProgramYN As Boolean, ByVal passHelpFile As String, ByVal passTeamSelectionRequired As Boolean, _
                                           ByVal passTeamBoardMenuOptionSelection As Boolean, _
                                           ByVal passTeamBoardMenuOptionMasterDescription As String, ByVal passLinkType As String, _
                                           ByVal passProgramShortcut As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passProgram, _
                                                                                     passProgramURL, _
                                                                                     passMenuYN, _
                                                                                     passInitialProgramYN, _
                                                                                     passHelpFile, _
                                                                                     passTeamSelectionRequired, _
                                                                                     passTeamBoardMenuOptionSelection, _
                                                                                     passTeamBoardMenuOptionMasterDescription, _
                                                                                     passLinkType, _
                                                                                     passProgramShortcut, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmInsert As New SqlCommand("spInsProgramMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmInsert
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@Program", passProgram)
                    .Parameters.AddWithValue("@ProgramURL", passProgramURL)
                    .Parameters.AddWithValue("@MenuYN", passMenuYN)
                    .Parameters.AddWithValue("@InitialProgramYN", passInitialProgramYN)
                    If Not String.IsNullOrEmpty(passHelpFile.Trim()) Then .Parameters.AddWithValue("@HelpFile", passHelpFile)
                    .Parameters.AddWithValue("@TeamSelectionRequired", passTeamSelectionRequired)
                    .Parameters.AddWithValue("@AllowTeamBoardMenuOptionMasterSelection", passTeamBoardMenuOptionSelection)
                    If Not String.IsNullOrEmpty(passTeamBoardMenuOptionMasterDescription.Trim()) Then .Parameters.AddWithValue("@TeamBoardMenuOptionMasterDescription", passTeamBoardMenuOptionMasterDescription)
                    If Not String.IsNullOrEmpty(passLinkType.Trim()) Then .Parameters.AddWithValue("@LinkType", passLinkType)
                    If Not String.IsNullOrEmpty(passProgramShortcut.Trim()) Then .Parameters.AddWithValue("@ProgramShortcut", passProgramShortcut)
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

#Region " Update Program Master"
        Public Shared Sub UpdateProgramMaster(ByVal passProgram As String, ByVal passProgramURL As String, ByVal passMenuYN As Boolean, _
                                              ByVal passInitialProgramYN As Boolean, ByVal passHelpFile As String, ByVal passTeamSelectionRequired As Boolean, _
                                              ByVal passTeamBoardMenuOptionSelection As Boolean, _
                                              ByVal passTeamBoardMenuOptionMasterDescription As String, ByVal passLinkType As String, _
                                              ByVal passProgramShortcut As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passProgram, _
                                                                                     passProgramURL, _
                                                                                     passMenuYN, _
                                                                                     passInitialProgramYN, _
                                                                                     passHelpFile, _
                                                                                     passTeamSelectionRequired, _
                                                                                     passTeamBoardMenuOptionSelection, _
                                                                                     passTeamBoardMenuOptionMasterDescription, _
                                                                                     passLinkType, _
                                                                                     passProgramShortcut, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdProgramMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@Program", passProgram)
                    .Parameters.AddWithValue("@ProgramURL", passProgramURL)
                    .Parameters.AddWithValue("@MenuYN", passMenuYN)
                    .Parameters.AddWithValue("@InitialProgramYN", passInitialProgramYN)
                    If Not String.IsNullOrEmpty(passHelpFile.Trim()) Then .Parameters.AddWithValue("@HelpFile", passHelpFile)
                    .Parameters.AddWithValue("@TeamSelectionRequired", passTeamSelectionRequired)
                    .Parameters.AddWithValue("@AllowTeamBoardMenuOptionMasterSelection", passTeamBoardMenuOptionSelection)
                    If Not String.IsNullOrEmpty(passTeamBoardMenuOptionMasterDescription.Trim()) Then .Parameters.AddWithValue("@TeamBoardMenuOptionMasterDescription", passTeamBoardMenuOptionMasterDescription)
                    If Not String.IsNullOrEmpty(passLinkType.Trim()) Then .Parameters.AddWithValue("@LinkType", passLinkType)
                    If Not String.IsNullOrEmpty(passProgramShortcut.Trim()) Then .Parameters.AddWithValue("@ProgramShortcut", passProgramShortcut)
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

#Region " Delete Program Master"
        Public Shared Sub DeleteProgramMaster(ByVal passProgram As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passProgram, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelProgramMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmDelete.CommandType = CommandType.StoredProcedure
                cmDelete.Parameters.AddWithValue("@Program", passProgram)
                cmDelete.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmDelete.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " Select Program For URL"
        Public Shared Function SelectProgramForURL(ByVal passProgramURL As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passProgramURL, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim myParm As SqlParameter
            Dim cm As New SqlClient.SqlCommand("spSelProgramForURL", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cm
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@ProgramURL", passProgramURL)
                    myParm = .Parameters.Add("@Program", SqlDbType.VarChar, 50)
                    myParm.Direction = ParameterDirection.Output
                    .ExecuteNonQuery()
                    If .Parameters("@Program").Value() Is DBNull.Value Then
                        Return ""
                    Else
                        Return .Parameters("@Program").Value.ToString
                    End If
                End With
            Catch Exc As Exception
                Throw
            Finally
                cm.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " Is Site And Site Group Selection Required For Program"
        Public Shared Function IsSiteAndSiteGroupSelectionRequiredForProgram(ByVal passProgramURL As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passProgramURL, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlClient.SqlCommand("spSelSiteAndSiteGroupSelectionRequiredForProgram", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                With da
                    .SelectCommand.CommandType = CommandType.StoredProcedure
                    .SelectCommand.Parameters.AddWithValue("@ProgramURL", passProgramURL)
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