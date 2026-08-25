#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class TeamsSummary
        Inherits ApplicationBase

#Region " Constants"
        Private Shared ReadOnly FormName As String = "TeamsSummary"
        Private Shared ReadOnly ProgramName As String = "TeamsSummary"
        Private bEnglish As Boolean = True
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
                lblStatus.Text = GetTranslationString("status", lblStatus.Text.Replace(":", "")) & ":"
                lblPillar.Text = GetTranslationString("pillar", lblPillar.Text.Replace(":", "")) & ":"
                lblTeamType.Text = GetTranslationString("teamtype", lblTeamType.Text.Replace(":", "")) & ":"
                btnApplyFilter.Text = GetTranslationString("applyfilter", btnApplyFilter.Text)
                btnClearFilter.Text = GetTranslationString("clearfilter", btnClearFilter.Text)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadCultureTranslations", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
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

            Master.IconImage = Request.ApplicationPath & "/images/usergroup.gif"
            Master.HeaderMessage = GetTranslationString(FormName, FormName)
            Master.ProgramName = ProgramName
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + MasterControl1.ExitButtonID + "'),window.event)")

            Dim objCol As ButtonField
            objCol = New ButtonField
            objCol.ButtonType = ButtonType.Link
            objCol.HeaderText = "Team"
            objCol.DataTextField = "Team"
            objCol.SortExpression = "Team"
            objCol.CommandName = "TeamBoard"
            MasterControl1.GridColumns.Insert(1, objCol)

            If Not Page.IsPostBack Then
                LoadDropDownListBoxes()
                LoadCultureTranslations()
                ApplyFiltersFromCookie()
            End If
        End Sub
        Protected Sub Timer1_Tick(ByVal sender As Object, ByVal e As System.EventArgs) Handles Timer1.Tick
            Timer1.Enabled = False
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            BindGrid()
            Master.MasterScriptManager.RegisterPostBackControl(MasterControl1.ExportButton)
        End Sub
        Protected Sub btnApplyFilter_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnApplyFilter.Click
            Dim cookie As New HttpCookie("MyTeamsFilter")
            cookie.Expires = Now.AddDays(Convert.ToInt16(ConfigurationManager.AppSettings("CookieExpirationTime")))

            If ddlStatus.SelectedItem IsNot Nothing Then
                cookie.Values("TeamStatus") = ddlStatus.SelectedItem.Value
            Else
                cookie.Values.Remove("TeamStatus")
            End If

            If ddlPillar.SelectedItem IsNot Nothing AndAlso ddlPillar.SelectedItem.Value.ToString.Trim.Length > 0 Then
                cookie.Values("Pillar") = ddlPillar.SelectedItem.Value
            Else
                cookie.Values.Remove("Pillar")
            End If

            If ddlTeamType.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlTeamType.SelectedItem.Value) Then
                cookie.Values("TeamType") = ddlTeamType.SelectedItem.Value
            Else
                cookie.Values.Remove("TeamType")
            End If

            Response.Cookies.Add(cookie)

            BindGrid()
        End Sub
        Protected Sub btnClearFilter_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnClearFilter.Click
            Response.Cookies("MyTeamsFilter").Expires = Now

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamsSummary"), False)
        End Sub
        Protected Sub MasterControl1_onRowCommand(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewCommandEventArgs) Handles MasterControl1.onRowCommand
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", e.CommandName)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Select Case e.CommandName
                Case "TeamBoard"
                    PushTeamOntoStack(SessionManager.SelectedTeamID, SessionManager.SelectedTeam, SessionManager.SelectedOPI, "TeamsSummary", SessionManager.CurrentMenuProgram)
                    SessionManager.SelectedTeamID = MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("TeamID").ToString
                    SessionManager.SelectedTeam = MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("Team").ToString
                    SessionManager.SelectedTeamName = Teams.GetTeamName(SessionManager.SelectedTeamID)
                    SessionManager.SelectedOPI = ""
                    SessionManager.SelectedTeamAllowEdit = UserSiteMaster.SelectTeamAllowEdit(SessionManager.SelectedTeamID, SessionManager.UserID)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedOPI)

                    SessionManager.CurrentMenuProgram = "TeamBoardMenu"
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamBoardMenu"), False)
            End Select
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadDropDownListBoxes()
            Pillars.SelectPillarList(ddlPillar)
            ddlPillar.Items.Insert(0, "")

            TeamTypes.SelectTeamTypesMasterList(ddlTeamType)
        End Sub
        Private Sub ApplyFiltersFromCookie()
            If Request.Cookies("MyTeamsFilter") IsNot Nothing Then
                Dim cookie As HttpCookie = Request.Cookies("MyTeamsFilter")
                Dim objItem As ListItem = Nothing

                If cookie.Values("TeamStatus") IsNot Nothing AndAlso cookie.Values("TeamStatus").ToString.Trim.Length > 0 Then
                    objItem = ddlStatus.Items.FindByValue(cookie.Values("TeamStatus").ToString)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                    End If
                Else
                    ddlStatus.Items(1).Selected = True
                End If

                If cookie.Values("Pillar") IsNot Nothing AndAlso cookie.Values("Pillar").ToString.Trim.Length > 0 Then
                    objItem = ddlPillar.Items.FindByValue(cookie.Values("Pillar").ToString)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                    End If
                End If

                If cookie.Values("TeamType") IsNot Nothing AndAlso cookie.Values("TeamType").ToString.Trim.Length > 0 Then
                    objItem = ddlTeamType.Items.FindByValue(cookie.Values("TeamType").ToString)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                    End If
                End If
            Else
                ddlStatus.Items(1).Selected = True
            End If
        End Sub
        Private Sub BindGrid()
            Try
                If ddlStatus.SelectedItem IsNot Nothing AndAlso ddlStatus.SelectedItem.Value.ToString.Trim.Length > 0 Then
                    MasterControl1.StoredProcedureParams.Add("@Status", ddlStatus.SelectedItem.Value.ToString)
                End If
                If ddlPillar.SelectedItem IsNot Nothing AndAlso ddlPillar.SelectedItem.Value.ToString.Trim.Length > 0 Then
                    MasterControl1.StoredProcedureParams.Add("@PillarAbbrev", ddlPillar.SelectedItem.Value.ToString)
                End If
                If ddlTeamType.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlTeamType.SelectedItem.Value) Then
                    MasterControl1.StoredProcedureParams.Add("@TeamTypeID", ddlTeamType.SelectedItem.Value.ToString)
                End If
                MasterControl1.StoredProcedureParams.Add("@UserID", SessionManager.UserID)
                MasterControl1.StoredProcedureParams.Add("@SiteID", SessionManager.WorkingSiteID)

                MasterControl1.DataBind(True)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindGrid", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
            End Try
        End Sub
#End Region

    End Class
End Namespace
