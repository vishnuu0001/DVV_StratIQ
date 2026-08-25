#Region " Imports"
Imports System.IO
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class MyActionItems
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "My Action Items"
        Private Shared ReadOnly ProgramName As String = "MyActionItems"
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
                ckTeamMember.Text = GetTranslationString("actionitemsteammember", ckTeamMember.Text)
                ckMyPillarTeams.Text = GetTranslationString("actionitemspillarmember", ckMyPillarTeams.Text)
                ckMyTeams.Text = GetTranslationString("actionitemsmyteams", ckMyTeams.Text)
                ckClosedItems.Text = GetTranslationString("actionitemsclosed", ckClosedItems.Text)
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

            Master.IconImage = Request.ApplicationPath & "/images/TeamAction.gif"
            Master.HeaderMessage = GetTranslationString(FormName, FormName)

            If Not Page.IsPostBack Then
                LoadCultureTranslations()
                'chkDisplayClosedTeamActions.Checked = SessionManager.DisplayClosedTeamActions
            Else
                'SessionManager.DisplayClosedTeamActions = chkDisplayClosedTeamActions.Checked
            End If

            Master.AddBodyAttribute("onkeydown", "TrapEscKey(document.getElementById('" + MasterControl1.ExitButtonID + "'),window.event)")

            Dim objCol As ButtonField
            objCol = New ButtonField
            objCol.ButtonType = ButtonType.Link
            objCol.HeaderText = "Team"
            objCol.DataTextField = "Team"
            objCol.CommandName = "TeamBoard"
            MasterControl1.GridColumns.Insert(1, objCol)

            MasterControl1.GridColumns(7).DataFormatString = "{0:yyyy/MM/dd HH:mm}"
            MasterControl1.GridColumns(10).DataFormatString = "{0:yyyy/MM/dd}"
            MasterControl1.GridColumns(11).DataFormatString = "{0:yyyy/MM/dd}"

            If Not Page.IsPostBack Then
                Master.MasterScriptManager.RegisterPostBackControl(MasterControl1.ExportButton)
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
        End Sub
        Protected Sub btnApplyFilter_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnApplyFilter.Click
            Dim cookie As New HttpCookie("MyActionItemsFilter")
            cookie.Expires = Now.AddDays(Convert.ToInt16(ConfigurationManager.AppSettings("CookieExpirationTime")))

            If ckTeamMember.Checked Then
                cookie.Values("TeamMember") = ckTeamMember.Checked.ToString
            Else
                cookie.Values.Remove("TeamMember")
            End If

            If ckMyPillarTeams.Checked Then
                cookie.Values("MyPillarTeams") = ckMyPillarTeams.Checked.ToString
            Else
                cookie.Values.Remove("MyPillarTeams")
            End If

            If ckMyTeams.Checked Then
                cookie.Values("MyTeams") = ckMyTeams.Checked.ToString
            Else
                cookie.Values.Remove("MyTeams")
            End If

            If ckClosedItems.Checked Then
                cookie.Values("ClosedItems") = ckClosedItems.Checked.ToString
            Else
                cookie.Values.Remove("ClosedItems")
            End If

            If ddlPillar.SelectedItem IsNot Nothing AndAlso ddlPillar.SelectedItem.Value.ToString.Trim.Length > 0 Then
                cookie.Values("PillarAbbrev") = ddlPillar.SelectedItem.Value.ToString.Trim
            Else
                cookie.Values.Remove("PillarAbbrev")
            End If

            Response.Cookies.Add(cookie)

            BindGrid()
        End Sub
        Protected Sub btnClearFilter_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnClearFilter.Click
            Response.Cookies("MyActionItemsFilter").Expires = Now

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("MyActionItems"), False)
        End Sub
        Protected Sub MasterControl1_onRowDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewRowEventArgs) Handles MasterControl1.onRowDataBound
            If e.Row.RowType = DataControlRowType.DataRow Then
                If IsDate(e.Row.Cells(10).Text) Then
                    Dim dtClosedDate As DateTime
                    Dim dtTargetDate As DateTime = Convert.ToDateTime(e.Row.Cells(10).Text)
                    If e.Row.Cells(11).Text <> "&nbsp;" Then
                        dtClosedDate = Convert.ToDateTime(e.Row.Cells(11).Text)
                        If Convert.ToBoolean(MasterControl1.MasterControlGrid.DataKeys(e.Row.RowIndex)("Cancelled").ToString) = True Then
                            e.Row.Cells(11).BackColor = Drawing.Color.Gray
                        ElseIf DateTime.Compare(dtClosedDate, dtTargetDate) <= 0 Then
                            e.Row.Cells(11).BackColor = Drawing.Color.Green
                        Else
                            e.Row.Cells(11).BackColor = Drawing.Color.Orange
                        End If
                    Else
                        If DateTime.Compare(dtTargetDate, Date.Now) >= 0 Then
                            e.Row.Cells(11).BackColor = Drawing.Color.Yellow
                        Else
                            e.Row.Cells(11).BackColor = Drawing.Color.Red
                        End If
                    End If
                End If

                If IsNumeric(MasterControl1.MasterControlGrid.DataKeys(e.Row.RowIndex)("AllowEdit").ToString) AndAlso Convert.ToInt16(MasterControl1.MasterControlGrid.DataKeys(e.Row.RowIndex)("AllowEdit").ToString) <> 1 Then
                    Try
                        CType(e.Row.Cells(15).Controls(0), LinkButton).Enabled = False
                    Catch ex As Exception
                        'do nothing
                    End Try
                End If
            End If
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
                Case "ViewRow", "EditRow", "DeleteRow"
                    PushTeamOntoStack(SessionManager.SelectedTeamID, SessionManager.SelectedTeam, SessionManager.SelectedOPI, "MyActionItems", SessionManager.CurrentMenuProgram)
                    SessionManager.SelectedTeamID = MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("TeamID").ToString
                    SessionManager.SelectedTeam = MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("Team").ToString
                    SessionManager.SelectedTeamName = Teams.GetTeamName(SessionManager.SelectedTeamID)
                    SessionManager.SelectedOPI = ""
                    SessionManager.SelectedTeamAllowEdit = MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("AllowEdit").ToString
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedOPI)

                    SessionManager.SelectedValue = MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("ActionNumber").ToString
                    SessionManager.TeamActionPlanMode = "My" & e.CommandName
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamActionPlanMaintenance2"), False)
                Case "TeamBoard"
                    PushTeamOntoStack(SessionManager.SelectedTeamID, SessionManager.SelectedTeam, SessionManager.SelectedOPI, "MyActionItems", SessionManager.CurrentMenuProgram)
                    SessionManager.SelectedTeamID = MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("TeamID").ToString
                    SessionManager.SelectedTeam = MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("Team").ToString
                    SessionManager.SelectedTeamName = Teams.GetTeamName(SessionManager.SelectedTeamID)
                    SessionManager.SelectedOPI = ""
                    SessionManager.SelectedTeamAllowEdit = MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("AllowEdit").ToString
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedOPI)

                    SessionManager.CurrentMenuProgram = "TeamBoardMenu"
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamBoardMenu"), False)
            End Select
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub ApplyFiltersFromCookie()
            Dim objItem As ListItem

            If Request.Cookies("MyActionItemsFilter") IsNot Nothing Then
                Dim cookie As HttpCookie = Request.Cookies("MyActionItemsFilter")

                If cookie.Values("TeamMember") IsNot Nothing AndAlso cookie.Values("TeamMember").ToString.Trim.Length > 0 Then
                    ckTeamMember.Checked = True
                End If

                If cookie.Values("MyPillarTeams") IsNot Nothing AndAlso cookie.Values("MyPillarTeams").ToString.Trim.Length > 0 Then
                    ckMyPillarTeams.Checked = True
                End If

                If cookie.Values("MyTeams") IsNot Nothing AndAlso cookie.Values("MyTeams").ToString.Trim.Length > 0 Then
                    ckMyTeams.Checked = True
                End If

                If cookie.Values("ClosedItems") IsNot Nothing AndAlso cookie.Values("ClosedItems").ToString.Trim.Length > 0 Then
                    ckClosedItems.Checked = True
                End If

                Pillars.SelectPillarList(ddlPillar)
                ddlPillar.Items.Insert(0, "")

                If cookie.Values("PillarAbbrev") IsNot Nothing AndAlso cookie.Values("PillarAbbrev").ToString.Trim.Length > 0 Then
                    objItem = ddlPillar.Items.FindByValue(cookie.Values("PillarAbbrev"))
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                    End If
                End If

            End If
        End Sub
        Private Sub BindGrid()

            MasterControl1.StoredProcedureParams.Clear()

            MasterControl1.StoredProcedureParams.Add("@UserID", SessionManager.UserID)
            MasterControl1.StoredProcedureParams.Add("@SiteID", SessionManager.WorkingSiteID)

            If ckTeamMember.Checked Then
                MasterControl1.StoredProcedureParams.Add("@TeamMember", 1)
            End If
            If ckMyPillarTeams.Checked Then
                MasterControl1.StoredProcedureParams.Add("@MyPillarTeams", 1)
            End If
            If ckMyTeams.Checked Then
                MasterControl1.StoredProcedureParams.Add("@MyTeams", 1)
            End If
            If ckClosedItems.Checked Then
                MasterControl1.StoredProcedureParams.Add("@ShowCompleted", 1)
            End If
            If ddlPillar.SelectedItem IsNot Nothing AndAlso ddlPillar.SelectedItem.Value.ToString.Trim.Length > 0 Then
                MasterControl1.StoredProcedureParams.Add("@PillarAbbrev", ddlPillar.SelectedItem.Value.ToString.Trim)
            End If

            MasterControl1.DataBind(True)
        End Sub
#End Region

    End Class
End Namespace
