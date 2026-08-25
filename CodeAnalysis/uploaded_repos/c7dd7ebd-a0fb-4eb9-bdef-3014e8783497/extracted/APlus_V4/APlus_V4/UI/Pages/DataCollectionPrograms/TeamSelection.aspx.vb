#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports System.Web.Security
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.UI.CustomControls

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class TeamSelection
        Inherits ApplicationBase

#Region " Constant Variables"
        Private Shared ReadOnly FormName As String = "Team Selection"
        Private Shared ReadOnly ProgramName As String = "TeamSelection"
#End Region

#Region " Load Culture Translations"
        Private Sub LoadCultureTranslations()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                lblTeam.Text = GetTranslationString("team", lblTeam.Text.Replace(":", "")) & ":"
                chkDisplayClosedTeams.Text = GetTranslationString("includeclosedteams", chkDisplayClosedTeams.Text)
                btnOK.Text = GetTranslationString("ok", btnOK.Text)
                btnCancel.Text = GetTranslationString("cancel", btnCancel.Text)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadCultureTranslations", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

#Region " Load JavaScripts"
        Private Sub LoadJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel}
            Dim OverMessageArr() As String = {"OK - Enter", "OK - Enter", "Cancel", "Cancel"}
            Dim OutMessageArr() As String = {"", "", "", ""}
            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)
            btnOK.Attributes.Add("onclick", "return CheckTeam(document.getElementById('" + ddlTeam.UniqueID + "'));")

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event)")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
        End Sub
#End Region

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, ProgramName, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If Not Page.IsPostBack Then
                LoadCultureTranslations()
            End If

            Master.IconImage = Request.ApplicationPath & "/images/usergroup.gif"
            Master.HeaderMessage = GetTranslationString(FormName, FormName)

            LoadJavaScripts()

            If Not Page.IsPostBack Then
                chkDisplayClosedTeams.Checked = SessionManager.DisplayClosedTeams

                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.DisplayClosedTeams)
                BindTeam()
                ddlTeam.Focus()
            End If
        End Sub
        Private Sub btnCancel_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnCancel.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.CallingProgram = "TeamBoardMenu" Then
                SessionManager.CurrentMenuProgram = "MainMenu"
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CallingProgram)
            End If

            RemoveCurrentProgramandGoBack()
        End Sub
        Private Sub btnOK_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                If ddlTeam.SelectedItem.Value.Trim <> "" Then
                    Dim strTarget() As String = ddlTeam.SelectedItem.Value.Split("|")
                    PushTeamOntoStack(SessionManager.SelectedTeamID, SessionManager.SelectedTeam, SessionManager.SelectedOPI, "TeamsListing", SessionManager.CurrentMenuProgram)
                    SessionManager.SelectedTeamID = strTarget(0).Trim
                    SessionManager.SelectedTeam = strTarget(2).Trim()
                    SessionManager.SelectedTeamName = strTarget(1).Trim()
                    SessionManager.SelectedOPI = ""
                    SessionManager.SelectedTeamAllowEdit = Convert.ToBoolean(strTarget(3).Trim())
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedOPI)
                Else
                    Dim objTeamStack As TeamStackItem = CType(SessionManager.TeamStack, Stack).Pop

                    If objTeamStack.TeamName = "" Then
                        SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedTeamID)
                        SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedTeamName)
                        SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedTeam)
                        SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedOPI)
                        SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedTeamAllowEdit)

                        If objTeamStack.LastMenu.Trim.Length > 0 Then
                            SessionManager.CurrentMenuProgram = objTeamStack.LastMenu
                        End If
                        If objTeamStack.ProgramName.ToString.Trim.Length > 0 Then
                            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & DataAccess.Custom.ProgramSecurity.GetProgramURL(objTeamStack.ProgramName), False)
                        End If
                    Else
                        SessionManager.SelectedOPI = objTeamStack.OPIName
                        SessionManager.SelectedTeamID = objTeamStack.TeamID
                        SessionManager.SelectedTeam = objTeamStack.TeamName
                        SessionManager.SelectedTeamName = DataAccess.Tables.Teams.GetTeamName(SessionManager.SelectedTeamID)
                        SessionManager.CurrentMenuProgram = objTeamStack.LastMenu
                        SessionManager.SelectedTeamAllowEdit = UserSiteMaster.SelectTeamAllowEdit(SessionManager.SelectedTeamID, SessionManager.UserID)
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & DataAccess.Custom.ProgramSecurity.GetProgramURL(objTeamStack.ProgramName), False)
                    End If
                End If
            Catch Exc As Exception
                Master.WriteErrors(ProgramName & " - btnOK_Click", Exc, SessionManager.UserID)
            End Try

            If SessionManager.CurrentProgram <> "" Then
                Response.Redirect(SessionManager.CurrentProgram)
            Else
                RemoveCurrentProgramandGoBack()
            End If
        End Sub
        Private Sub chkDisplayClosedTeams_CheckedChanged(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles chkDisplayClosedTeams.CheckedChanged
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.DisplayClosedTeams = chkDisplayClosedTeams.Checked
            Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamSelection"), False)
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub BindTeam()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Teams.TeamSelectionList(ddlTeam, SessionManager.UserID.ToString, SessionManager.WorkingSiteID, chkDisplayClosedTeams.Checked)
                ddlTeam.Items.Insert(0, "")

                If Not SessionManager.SelectedTeam = "" Then
                    ddlTeam.Items.FindByValue(SessionManager.SelectedTeam & "|" & SessionManager.SelectedTeamName).Selected = True
                End If

                If ddlTeam.SelectedIndex = 0 Then
                    If ddlTeam.Items.Count = 2 Then
                        ddlTeam.SelectedIndex = 1
                        btnOK_Click(Nothing, Nothing)
                    End If
                End If
            Catch Txc As System.Threading.ThreadAbortException
            Catch Uxc As System.NullReferenceException
            Catch Exc As Exception
                Master.WriteErrors(ProgramName & " - BindTeam", Exc, SessionManager.UserID)
            End Try
        End Sub
#End Region

    End Class
End Namespace
