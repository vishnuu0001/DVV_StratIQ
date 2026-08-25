#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class Teams

#Region " Select Teams"
        Public Shared Function SelectTeams(ByVal passTeamID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTeam", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TeamID", passTeamID)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectTeamsListing(ByVal passSiteID As Integer, ByVal passUserID As String, ByVal passTeamMember As Boolean, _
                                                  ByVal passPillarMember As Boolean, ByVal passStatus As String, ByVal passPillar As String, _
                                                  ByVal passTeamType As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSiteID, passUserID, _
                                                                                     passTeamMember, passPillarMember, passStatus, passPillar, passTeamType, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTeamsOverview", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@UserID", passUserID)
                da.SelectCommand.Parameters.AddWithValue("@SiteID", passSiteID)
                da.SelectCommand.Parameters.AddWithValue("@TeamMember", passTeamMember)
                da.SelectCommand.Parameters.AddWithValue("@MyPillarTeams", passPillarMember)
                If passStatus.Trim.Length > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@Status", passStatus)
                End If
                If passPillar.Trim.Length > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@PillarAbbrev", passPillar)
                End If
                If IsNumeric(passTeamType) Then
                    da.SelectCommand.Parameters.AddWithValue("@TeamTypeID", passTeamType)
                End If

                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectKPITeamsOverview(ByVal passUserID As String, ByVal passKPIID As Integer, _
                                                  Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passUserID, passKPIID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelKPITeamsOverview", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@UserID", passUserID)
                da.SelectCommand.Parameters.AddWithValue("@KPIID", passKPIID)

                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Sub TeamSelectionList(ByRef ddlList As DropDownList, ByVal passUserID As String, ByVal passSiteID As Integer, ByVal DisplayClosedTeams As Boolean, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", passUserID, passSiteID, DisplayClosedTeams, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelTeamSelectionList", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@UserID", passUserID)
                cmSelect.Parameters.AddWithValue("@WorkingSiteID", passSiteID)
                cmSelect.Parameters.AddWithValue("@DisplayClosedTeams", DisplayClosedTeams)
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    If (New System.Globalization.CultureInfo(SessionManager.CulturePref).TwoLetterISOLanguageName.ToUpper = "EN") Then
                        ddlList.Items.Add(New ListItem(drList.Item("Team").ToString.Trim & " - " & drList.Item("TeamNameOther").ToString.Trim, drList.Item("TeamID").ToString.Trim & "|" & drList.Item("TeamNameOther").ToString.Trim & "|" & drList.Item("Team").ToString.Trim & "|" & Convert.ToBoolean(drList.Item("AllowEdit"))))
                    Else
                        ddlList.Items.Add(New ListItem(drList.Item("Team").ToString.Trim & " - " & drList.Item("TeamName").ToString.Trim, drList.Item("TeamID").ToString.Trim & "|" & drList.Item("TeamName").ToString.Trim & "|" & drList.Item("Team").ToString.Trim & "|" & Convert.ToBoolean(drList.Item("AllowEdit"))))
                    End If
                End While
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub FillTeamSelectionList(ByRef ddlList As DropDownList, ByVal passUserID As String, ByVal passSiteID As Integer, ByVal DisplayClosedTeams As Boolean, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", passUserID, passSiteID, DisplayClosedTeams, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelTeamSelectionList", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@UserID", passUserID)
                cmSelect.Parameters.AddWithValue("@WorkingSiteID", passSiteID)
                cmSelect.Parameters.AddWithValue("@DisplayClosedTeams", DisplayClosedTeams)
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    If (New System.Globalization.CultureInfo(SessionManager.CulturePref).TwoLetterISOLanguageName.ToUpper = "EN") Then
                        ddlList.Items.Add(New ListItem(drList.Item("Team").ToString.Trim & " - " & drList.Item("TeamNameOther").ToString.Trim, drList.Item("TeamID").ToString.Trim))
                    Else
                        ddlList.Items.Add(New ListItem(drList.Item("Team").ToString.Trim & " - " & drList.Item("TeamName").ToString.Trim, drList.Item("TeamID").ToString.Trim))
                    End If
                End While
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub SelectTeamList(ByVal passSiteID As Integer, ByRef ddlList As System.Web.UI.WebControls.DropDownList, Optional ByRef cnMasterConnection As SqlConnection = Nothing, Optional ByVal bAddBlankRow As Boolean = False)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSiteID, "", bAddBlankRow)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelTeamsList", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@SiteID", passSiteID)
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    If (New System.Globalization.CultureInfo(SessionManager.CulturePref).TwoLetterISOLanguageName.ToUpper = "EN") Then
                        ddlList.Items.Add(New ListItem(drList.Item("Team").ToString.Trim & " - " & drList.Item("TeamNameOther").ToString.Trim, drList.Item("TeamID").ToString.Trim))
                    Else
                        ddlList.Items.Add(New ListItem(drList.Item("Team").ToString.Trim & " - " & drList.Item("TeamName").ToString.Trim, drList.Item("TeamID").ToString.Trim))
                    End If
                End While
                If bAddBlankRow = True Then ddlList.Items.Insert(0, New ListItem("", ""))
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub SelectTeamList(ByRef ddlList As System.Web.UI.WebControls.DropDownList, ByVal passUserID As String, ByVal passSiteID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing, Optional ByVal bAddBlankRow As Boolean = False)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", passUserID, passSiteID, "", bAddBlankRow)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelTeamSelectionList", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@UserID", passUserID)
                cmSelect.Parameters.AddWithValue("@WorkingSiteID", passSiteID)
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    ddlList.Items.Add(New ListItem(drList.Item(0).ToString.Trim & " - " & drList.Item(1).ToString.Trim, drList.Item(0).ToString.Trim))
                End While
                If bAddBlankRow = True Then ddlList.Items.Insert(0, New ListItem("", ""))
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub SelectMyTeamList(ByRef ddlList As System.Web.UI.WebControls.DropDownList, ByVal passUserID As String, ByVal passSiteID As Integer, Optional ByVal bShowClosedTeams As Boolean = False, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", passUserID, passSiteID, bShowClosedTeams, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelTeamSelectionList", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@UserID", passUserID)
                cmSelect.Parameters.AddWithValue("@WorkingSiteID", passSiteID)
                cmSelect.Parameters.AddWithValue("@DisplayClosedTeams", bShowClosedTeams)
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    ddlList.Items.Add(New ListItem(drList.Item(0).ToString.Trim & " - " & drList.Item(1).ToString.Trim, drList.Item(0).ToString.Trim))
                End While
                ddlList.Items.Insert(0, New ListItem("", ""))
                ddlList.Items.Insert(1, New ListItem("My Teams", "MYTEAMS"))
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Function SelectMyTeamSecurity(ByVal passUserID As String, ByVal passTeamID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, passTeamID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelMyTeamSecurity", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim ds As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@UserID", passUserID)
                da.SelectCommand.Parameters.AddWithValue("@TeamID", passTeamID)
                da.Fill(ds)
                Return ds
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectTeamListNoDDL(ByVal passUserID As String, ByVal passSite As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, passSite, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTeamSelectionList", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim ds As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@UserID", passUserID)
                da.SelectCommand.Parameters.AddWithValue("@WorkingSite", passSite)
                da.Fill(ds)
                Return ds
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Sub SelectTeamNameList(ByRef ddlList As System.Web.UI.WebControls.DropDownList, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
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
            Dim cmSelect As New SqlCommand("spSelTeamNameList", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    ddlList.Items.Add(New ListItem(drList.GetString(0), drList.GetString(1)))
                End While
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Function GetNextActionNumber(ByVal passTeamID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing, Optional ByRef trans As SqlTransaction = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim myParm As SqlParameter
            Dim cmNextActionNumber As New SqlCommand("spSelNextActionNumber", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmNextActionNumber
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@TeamID", passTeamID)

                    myParm = .Parameters.AddWithValue("@ActionNumberNext", SqlDbType.Int)
                    myParm.Direction = ParameterDirection.Output
                    .ExecuteNonQuery()
                End With
                Return Trim(cmNextActionNumber.Parameters("@ActionNumberNext").Value())
            Catch Exc As Exception
                Throw
            Finally
                cmNextActionNumber.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function GetTeamFolder(ByVal passTeamID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelTeamFolder", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing
            Dim strHolder As String = String.Empty

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@TeamID", passTeamID)
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    strHolder = "" + drList(0).ToString
                End While
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
            Return strHolder
        End Function
        Public Shared Function GetTeamName(ByVal passTeamID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelTeamName", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing
            Dim strHolder As String = String.Empty

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@TeamID", passTeamID)
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    strHolder = "" + drList(0).ToString
                End While
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
            Return strHolder
        End Function
        Public Shared Function GetTeamNameOther(ByVal passTeamID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelTeamNameOther", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing
            Dim strHolder As String = String.Empty

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@TeamID", passTeamID)
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    strHolder = "" + drList(0).ToString
                End While
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
            Return strHolder
        End Function
        Public Shared Function GetTeamRoute(ByVal passTeamID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelTeamRoute", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing
            Dim strHolder As String = String.Empty

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@TeamID", passTeamID)
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    strHolder = "" + drList(0).ToString
                End While
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
            Return strHolder
        End Function
        Public Shared Function UserHasAccessToTeam(ByVal passUserID As String, ByVal passTeamID As Integer, ByVal passSiteID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, passTeamID, passSiteID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.IsAdministrator Then
                Return True
            End If

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelUserCanAccessTeam", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing
            Dim blbRetValue As Boolean = False

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@UserID", passUserID)
                cmSelect.Parameters.AddWithValue("@TeamID", passTeamID)
                cmSelect.Parameters.AddWithValue("@WorkingSiteID", passSiteID)
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    If Convert.ToBoolean(drList(0)) = True Then
                        blbRetValue = True
                    End If
                End While
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
            Return blbRetValue
        End Function
        Public Shared Function GetMasterPlanType(ByVal passTeamID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelTeamMasterPlanType", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing
            Dim strHolder As String = String.Empty

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@TeamID", passTeamID)
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    strHolder = "" + drList(0).ToString
                End While
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
            Return strHolder
        End Function
        Public Shared Function GetTeamStartDate(ByVal passTeamID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Date
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelTeamStartDate", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@TeamID", passTeamID)
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    Return drList(0)
                End While
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
            Return Nothing
        End Function
        Public Shared Function SelectDashboardTeams(ByVal passUserID As String, ByVal passSiteID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, passSiteID.ToString, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelMyDashboardTeams", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim ds As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@UserID", passUserID)
                da.SelectCommand.Parameters.AddWithValue("@SiteID", passSiteID)
                da.Fill(ds)
                Return ds
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectTeamsByBusinessAreaID(ByVal passBusinessAreaID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passBusinessAreaID.ToString, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTeamsByBusinessAreaID", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                If passBusinessAreaID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@BusinessAreaID", passBusinessAreaID)
                End If
                da.Fill(dt)

                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectTeamsByBusinessUnitID(ByVal passBusinessUnitID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passBusinessUnitID.ToString, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTeamsByBusinessUnitID", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                If passBusinessUnitID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@BusinessUnitID", passBusinessUnitID)
                End If
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

#Region " Action Methods"
        Public Shared Function AddTeams(ByVal passTeam As String, ByVal passTeamName As String, ByVal passTeamNameOther As String, _
                                   ByVal passSiteID As Integer, ByVal passBusinessAreaID As String, ByVal passBusinessUnitID As String, _
                                   ByVal passPillarAbbrev As String, ByVal passRouteAbbrev As String, ByVal passDeptNumber As String, _
                                   ByVal passTeamStartDate As String, ByVal passTeamFinishDate As String, ByVal passTeamStatus As String, _
                                   ByVal passTeamFolder As String, ByVal passTeamBoardType As String, ByVal passMasterPlanType As String, _
                                   ByVal passTeamCategory As String, ByVal passNewTeamMembers As Integer, ByVal passAllUsersView As Boolean, _
                                   ByVal passMembersOnly As Boolean, ByVal passMaintenanceUserID As String, ByVal passTeamTypeID As Integer, _
                                   Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer

            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passTeam, _
                                                                                     passTeamName, _
                                                                                     passTeamNameOther, _
                                                                                     passSiteID, _
                                                                                     passBusinessAreaID, _
                                                                                     passBusinessUnitID, _
                                                                                     passPillarAbbrev, _
                                                                                     passRouteAbbrev, _
                                                                                     passDeptNumber, _
                                                                                     passTeamStartDate, _
                                                                                     passTeamFinishDate, _
                                                                                     passTeamStatus, _
                                                                                     passTeamFolder, _
                                                                                     passTeamBoardType, _
                                                                                     passMasterPlanType, _
                                                                                     passTeamCategory, _
                                                                                     passNewTeamMembers, _
                                                                                     passAllUsersView, passMembersOnly, _
                                                                                     passMaintenanceUserID, _
                                                                                     passTeamTypeID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsTeams", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim iTeamID As Integer = 0

            Try
                With cmAdd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@Team", passTeam)
                    .Parameters.AddWithValue("@TeamName", passTeamName)
                    .Parameters.AddWithValue("@TeamNameOther", passTeamNameOther)
                    .Parameters.AddWithValue("@SiteID", passSiteID)
                    If IsNumeric(passBusinessAreaID) AndAlso Convert.ToInt16(passBusinessAreaID) > 0 Then
                        .Parameters.AddWithValue("@BusinessAreaID", passBusinessAreaID)
                    End If
                    If IsNumeric(passBusinessUnitID) AndAlso Convert.ToInt16(passBusinessUnitID) > 0 Then
                        .Parameters.AddWithValue("@BusinessUnitID", passBusinessUnitID)
                    End If
                    .Parameters.AddWithValue("@PillarAbbrev", passPillarAbbrev)
                    .Parameters.AddWithValue("@RouteAbbrev", passRouteAbbrev)
                    If passDeptNumber.Trim.Length > 0 Then
                        .Parameters.AddWithValue("@DeptNumber", passDeptNumber)
                    End If
                    .Parameters.AddWithValue("@TeamStartDate", passTeamStartDate)
                    If IsDate(passTeamFinishDate) Then .Parameters.AddWithValue("@TeamFinishDate", passTeamFinishDate)
                    .Parameters.AddWithValue("@TeamStatus", passTeamStatus)
                    If passTeamFolder.Length > 0 Then .Parameters.AddWithValue("@TeamFolder", passTeamFolder)
                    .Parameters.AddWithValue("@TeamBoardType", passTeamBoardType)
                    .Parameters.AddWithValue("@MasterPlanType", passMasterPlanType)
                    .Parameters.AddWithValue("@TeamCategory", passTeamCategory)
                    If passNewTeamMembers >= 0 Then .Parameters.AddWithValue("@NewTeamMembers", passNewTeamMembers)
                    .Parameters.AddWithValue("@TeamTypeID", passTeamTypeID)
                    .Parameters.AddWithValue("@AllUsersView", passAllUsersView)
                    .Parameters.AddWithValue("@MembersOnly", passMembersOnly)
                    .Parameters.AddWithValue("@MaintenanceUserID", passMaintenanceUserID)

                    iTeamID = .ExecuteScalar
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try

            Return iTeamID
        End Function
        Public Shared Sub UpdateTeams(ByVal passTeamID As Integer, ByVal passTeam As String, ByVal passTeamName As String, _
                                      ByVal passTeamNameOther As String, ByVal passSiteID As Integer, ByVal passBusinessAreaID As String, _
                                      ByVal passBusinessUnitID As String, ByVal passPillarAbbrev As String, ByVal passRouteAbbrev As String, _
                                      ByVal passDeptNumber As String, ByVal passTeamStartDate As String, ByVal passTeamFinishDate As String, _
                                      ByVal passTeamStatus As String, ByVal passTeamFolder As String, ByVal passTeamBoardType As String, _
                                      ByVal passMasterPlanType As String, ByVal passTeamCategory As String, ByVal passNewTeamMembers As Integer, _
                                      ByVal passAllUsersView As Boolean, ByVal passMembersOnly As Boolean, ByVal passMaintenanceUserID As String, _
                                      ByVal passTeamTypeID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()

                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passTeamID, _
                                                                                     passTeam, _
                                                                                     passTeamName, _
                                                                                     passSiteID, _
                                                                                     passBusinessAreaID, _
                                                                                     passBusinessUnitID, _
                                                                                     passPillarAbbrev, _
                                                                                     passRouteAbbrev, _
                                                                                     passDeptNumber, _
                                                                                     passTeamStartDate, _
                                                                                     passTeamFinishDate, _
                                                                                     passTeamStatus, _
                                                                                     passTeamFolder, _
                                                                                     passTeamBoardType, _
                                                                                     passMasterPlanType, _
                                                                                     passTeamCategory, _
                                                                                     passNewTeamMembers, _
                                                                                     passAllUsersView, passMembersOnly, _
                                                                                     passMaintenanceUserID, _
                                                                                     passTeamTypeID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdTeams", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@TeamID", passTeamID)
                    .Parameters.AddWithValue("@Team", passTeam)
                    .Parameters.AddWithValue("@TeamName", passTeamName)
                    .Parameters.AddWithValue("@TeamNameOther", passTeamNameOther)
                    .Parameters.AddWithValue("@SiteID", passSiteID)
                    If passBusinessAreaID.Trim.Length > 0 Then .Parameters.AddWithValue("@BusinessAreaID", passBusinessAreaID)
                    If passBusinessUnitID.Trim.Length > 0 Then .Parameters.AddWithValue("@BusinessUnitID", passBusinessUnitID)
                    .Parameters.AddWithValue("@PillarAbbrev", passPillarAbbrev)
                    .Parameters.AddWithValue("@RouteAbbrev", passRouteAbbrev)
                    If passDeptNumber.Trim.Length > 0 Then
                        .Parameters.AddWithValue("@DeptNumber", passDeptNumber)
                    End If
                    .Parameters.AddWithValue("@TeamStartDate", passTeamStartDate)
                    If IsDate(passTeamFinishDate) Then
                        .Parameters.AddWithValue("@TeamFinishDate", passTeamFinishDate)
                    End If
                    .Parameters.AddWithValue("@TeamStatus", passTeamStatus)
                    If passTeamFolder.Length > 0 Then
                        .Parameters.AddWithValue("@TeamFolder", passTeamFolder)
                    End If
                    .Parameters.AddWithValue("@TeamBoardType", passTeamBoardType)
                    .Parameters.AddWithValue("@MasterPlanType", passMasterPlanType)
                    .Parameters.AddWithValue("@TeamCategory", passTeamCategory)
                    If passNewTeamMembers >= 0 Then
                        .Parameters.AddWithValue("@NewTeamMembers", passNewTeamMembers)
                    End If
                    .Parameters.AddWithValue("@TeamTypeID", passTeamTypeID)
                    .Parameters.AddWithValue("@AllUsersView", passAllUsersView)
                    .Parameters.AddWithValue("@MembersOnly", passMembersOnly)
                    .Parameters.AddWithValue("@MaintenanceUserID", passMaintenanceUserID)
                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub DeleteTeams(ByVal passTeamID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelTeams", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmDelete
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@TeamID", passTeamID)
                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmDelete.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub RenameTeam(ByVal passTeamID As Integer, ByVal passTeam As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, passTeam, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spUpdTeamRename", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmDelete
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@TeamID", passTeamID)
                    .Parameters.AddWithValue("@Team", passTeam)
                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmDelete.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub UpdateTeamBusinessArea(ByVal passTeamID As Integer, ByVal passBusinessAreaID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, passBusinessAreaID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdTeamBusinessArea", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmUpdate.CommandType = CommandType.StoredProcedure
                cmUpdate.Parameters.AddWithValue("@TeamID", passTeamID)
                If passBusinessAreaID > 0 Then
                    cmUpdate.Parameters.AddWithValue("@BusinessAreaID", passBusinessAreaID)
                End If

                cmUpdate.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub UpdateTeamBusinessUnit(ByVal passTeamID As Integer, ByVal passBusinessUnitID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, passBusinessUnitID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdTeamBusinessUnit", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmUpdate.CommandType = CommandType.StoredProcedure
                cmUpdate.Parameters.AddWithValue("@TeamID", passTeamID)
                If passBusinessUnitID > 0 Then
                    cmUpdate.Parameters.AddWithValue("@BusinessUnitID", passBusinessUnitID)
                End If

                cmUpdate.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

    End Class
End Namespace
