#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.UI.CustomControls
Imports System.Collections.Generic

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class Teams2
        Inherits ApplicationBase

#Region " Private/Constant Variables"
        Private Shared ReadOnly FormName As String = "Teams"
        Private Shared ReadOnly ProgramName As String = "Teams2"
        Private Shared ReadOnly DBTableName As String = "Teams"
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
                lblTeamID.Text = GetTranslationString("teamid", lblTeamID.Text.Replace(":", "")) & ":"
                lblTeam.Text = GetTranslationString("team", lblTeam.Text.Replace(":", "")) & ":"
                lblTeamName.Text = GetTranslationString("team name", lblTeamName.Text.Replace(":", "")) & ":"
                lblTeamNameOther.Text = GetTranslationString("teamnameother", lblTeamNameOther.Text.Replace(":", "")) & ":"
                lblSite.Text = GetTranslationString("site", lblSite.Text.Replace(":", "")) & ":"
                lblBusinessArea.Text = GetTranslationString("businessarea", lblBusinessArea.Text.Replace(":", "")) & ":"
                lblBusinessUnit.Text = GetTranslationString("businessunit", lblBusinessUnit.Text.Replace(":", "")) & ":"
                lblPillar.Text = GetTranslationString("pillar", lblPillar.Text.Replace(":", "")) & ":"
                lblRoute.Text = GetTranslationString("route", lblRoute.Text.Replace(":", "")) & ":"
                lblRouteChange.Text = GetTranslationString("routechange1", lblRouteChange.Text)
                lblRouteChange2.Text = GetTranslationString("routechange2", lblRouteChange2.Text)
                lblRouteChangeJob.Text = GetTranslationString("routechange3", lblRouteChangeJob.Text)
                lblDeptNumber.Text = GetTranslationString("department", lblDeptNumber.Text.Replace(":", "")) & ":"
                lblTeamFolder.Text = GetTranslationString("teamfolder", lblTeamFolder.Text.Replace(":", "")) & ":"
                lblStartDate.Text = GetTranslationString("start date", lblStartDate.Text.Replace(":", "")) & ":"
                lblFinishDate.Text = GetTranslationString("finishdate", lblFinishDate.Text.Replace(":", "")) & ":"
                lblTeamBoardType.Text = GetTranslationString("teamboardtype", lblTeamBoardType.Text.Replace(":", "")) & ":"
                lblMasterPlanType.Text = GetTranslationString("masterplantype", lblMasterPlanType.Text.Replace(":", "")) & ":"
                lblStatus.Text = GetTranslationString("status", lblStatus.Text.Replace(":", "")) & ":"
                lblTeamType.Text = GetTranslationString("teamtype", lblTeamType.Text.Replace(":", "")) & ":"
                lblTeamCategory.Text = GetTranslationString("teamcategory", lblTeamCategory.Text.Replace(":", "")) & ":"
                lblAllUsersView.Text = GetTranslationString("allusersview", lblAllUsersView.Text.Replace(":", "")) & ":"
                lblMembersOnly.Text = GetTranslationString("membersonly", lblMembersOnly.Text.Replace(":", "")) & ":"
                lblMaintenanceUserID.Text = GetTranslationString("maintuserid", lblMaintenanceUserID.Text.Replace(":", "")) & ":"
                lblMaintenanceDate.Text = GetTranslationString("maintdate", lblMaintenanceDate.Text.Replace(":", "")) & ":"
                lblTeamActionItems.Text = GetTranslationString("teamactionitems", lblTeamActionItems.Text.Replace(":", "")) & ":"
                lblTeamMembership.Text = GetTranslationString("teammembership", lblTeamMembership.Text.Replace(":", "")) & ":"
                lblTeamTrackers.Text = GetTranslationString("teamtrackers", lblTeamTrackers.Text.Replace(":", "")) & ":"
                lblTeamKPI.Text = GetTranslationString("teamkpi", lblTeamKPI.Text.Replace(":", "")) & ":"
                btnOK.Text = GetTranslationString("ok", btnOK.Text)
                btnCancel.Text = GetTranslationString("cancel", btnCancel.Text)
                btnTeamMembership.Text = GetTranslationString("team membership", btnTeamMembership.Text)
                btnTeamUsers.Text = GetTranslationString("team users", btnTeamUsers.Text)
                btnExit.Text = GetTranslationString("exit", btnExit.Text)
                btnTeamMembership2.Text = GetTranslationString("team membership", btnTeamMembership2.Text)
                btnTeamUsers2.Text = GetTranslationString("team users", btnTeamUsers2.Text)
                btnTeamKPI.Text = GetTranslationString("team kpi", btnTeamKPI.Text)
                btnTeamKPI2.Text = GetTranslationString("team kpi", btnTeamKPI2.Text)
                lblTeamPhoto.Text = GetTranslationString("teamphotoerror", lblTeamPhoto.Text)
                btnEditTeam.Text = GetTranslationString("editteam", btnEditTeam.Text)
                For i As Integer = 0 To gvTeamMembership.Columns.Count - 1
                    gvTeamMembership.Columns(i).HeaderText = GetTranslationString(gvTeamMembership.Columns(i).HeaderText, gvTeamMembership.Columns(i).HeaderText)
                Next
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadCultureTranslations", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel, btnExit}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel", "Exit"}
            Dim OutMessageArr() As String = {"", "", ""}
            Dim strDateFormat As String = Session("DateFormat")

            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)
            txtStartDate_CalendarExtender.Format = strDateFormat
            txtFinishDate_CalendarExtender.Format = strDateFormat

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnExit.UniqueID + "'))")
        End Sub
        Private Sub LoadAddModeJavaScripts()
            Dim myTabArray() As Object = {txtTeam, _
                                          txtTeamName, _
                                          txtTeamNameOther, _
                                          ddlSite, _
                                          ddlBusinessArea, _
                                          ddlBusinessUnit, _
                                          ddlPillar, _
                                          ddlRoute, _
                                          txtDeptNumber, _
                                          txtTeamFolder, _
                                          txtStartDate, _
                                          txtFinishDate, _
                                          ddlTeamBoardType, _
                                          ddlMasterPlanType, _
                                          ddlStatus, _
                                          ddlTeamType, _
                                          ddlTeamCategory, _
                                          ckAllUsersView, _
                                          ckMembersOnly}

            Dim TabKeyDownArr() As String = {Tab(txtTeamName, ckMembersOnly, "No"), _
                                             Tab(txtTeamNameOther, txtTeam, "No"), _
                                             Tab(ddlSite, txtTeamName, "No"), _
                                             Tab(ddlBusinessArea, txtTeamNameOther, "No"), _
                                             Tab(ddlBusinessUnit, ddlSite, "No"), _
                                             Tab(ddlPillar, ddlBusinessArea, "No"), _
                                             Tab(ddlRoute, ddlBusinessUnit, "No"), _
                                             Tab(txtDeptNumber, ddlPillar, "No"), _
                                             Tab(txtTeamFolder, ddlRoute, "No"), _
                                             Tab(txtStartDate, txtDeptNumber, "No"), _
                                             Tab(txtFinishDate, txtTeamFolder, "No"), _
                                             Tab(ddlTeamBoardType, txtStartDate, "No"), _
                                             Tab(ddlMasterPlanType, txtFinishDate, "No"), _
                                             Tab(ddlStatus, ddlTeamBoardType, "Yes"), _
                                             Tab(ddlTeamType, ddlMasterPlanType, "No"), _
                                             Tab(ddlTeamCategory, ddlStatus, "No"), _
                                             Tab(ckAllUsersView, ddlTeamType, "No"), _
                                             Tab(ckMembersOnly, ddlTeamCategory, "No"), _
                                             Tab(txtTeam, ckAllUsersView, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {txtTeamName, _
                                          txtTeamNameOther, _
                                          ddlSite, _
                                          ddlBusinessArea, _
                                          ddlBusinessUnit, _
                                          ddlPillar, _
                                          ddlRoute, _
                                          txtDeptNumber, _
                                          txtTeamFolder, _
                                          txtStartDate, _
                                          txtFinishDate, _
                                          ddlTeamBoardType, _
                                          ddlMasterPlanType, _
                                          ddlStatus, _
                                          ddlTeamType, _
                                          ddlTeamCategory, _
                                          ckAllUsersView, _
                                          ckMembersOnly}

            Dim TabKeyDownArr() As String = {Tab(txtTeamNameOther, ckMembersOnly, "No"), _
                                             Tab(ddlSite, txtTeamName, "No"), _
                                             Tab(ddlBusinessArea, txtTeamNameOther, "No"), _
                                             Tab(ddlBusinessUnit, ddlSite, "No"), _
                                             Tab(ddlPillar, ddlBusinessArea, "No"), _
                                             Tab(ddlRoute, ddlBusinessUnit, "No"), _
                                             Tab(txtDeptNumber, ddlPillar, "No"), _
                                             Tab(txtTeamFolder, ddlRoute, "No"), _
                                             Tab(txtStartDate, txtDeptNumber, "No"), _
                                             Tab(txtFinishDate, txtTeamFolder, "No"), _
                                             Tab(ddlTeamBoardType, txtStartDate, "No"), _
                                             Tab(ddlMasterPlanType, txtFinishDate, "No"), _
                                             Tab(ddlStatus, ddlTeamBoardType, "Yes"), _
                                             Tab(ddlTeamType, ddlMasterPlanType, "Yes"), _
                                             Tab(ddlTeamCategory, ddlStatus, "Yes"), _
                                             Tab(ckAllUsersView, ddlTeamType, "No"), _
                                             Tab(ckMembersOnly, ddlTeamCategory, "No"), _
                                             Tab(txtTeamName, ckAllUsersView, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
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

            Master.HeaderMessage = GetTranslationString(FormName, FormName) & " - " & GetTranslationString(SessionManager.TeamsMode.Replace("Row", ""), SessionManager.TeamsMode.Replace("Row", ""))
            Master.IconImage = Request.ApplicationPath + "/images/usergroup.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            Try
                If Not Page.IsPostBack Then
                    LoadDropdownLists()

                    If Not ProgramSecurity.CanUserAccessProgram(SessionManager.UserID, "TrackerMaster1") Then
                        btnTeamTrackers.Visible = False
                        btnTeamTrackers2.Visible = False
                    End If

                    If Not ProgramSecurity.CanUserAccessProgram(SessionManager.UserID, "KPITeamMaster1") Then
                        btnTeamKPI.Visible = False
                        btnTeamKPI2.Visible = False
                    End If

                    Select Case SessionManager.TeamsMode
                        Case "EditRow"
                            LoadEditModeJavaScripts()
                            LoadSelectedRecord()
                            BindTeamActionItems()
                            BindTeamMembership()
                            BindTeamTrackers()
                            BindTeamKPIs()
                            BindTeamAttachments()
                            UnEnableRecords()
                            CheckMembersOnlySecurity()
                        Case "ViewRow"
                            LoadSelectedRecord()
                            BindTeamActionItems()
                            BindTeamMembership()
                            BindTeamTrackers()
                            BindTeamKPIs()
                            BindTeamAttachments()
                            UnEnableRecords()

                            If SessionManager.CallingProgram = "TeamStatus" Then
                                If SessionManager.IsAdministrator Then
                                    btnEditTeam.Visible = True
                                ElseIf SessionManager.SelectedTeamAllowEdit Then
                                    Dim dtMode As DataTable = ProgramSecurity.ProgramModeFromProgram(SessionManager.UserID, "TeamsMaintenance")
                                    If dtMode.Rows.Count > 0 Then
                                        If CType(dtMode.Rows(0).Item("AllowEdit"), Boolean) = True Then
                                            btnEditTeam.Visible = True
                                        End If
                                    End If
                                End If
                            End If
                        Case "DeleteRow"
                            LoadSelectedRecord()
                            BindTeamActionItems()
                            BindTeamMembership()
                            BindTeamTrackers()
                            BindTeamKPIs()
                            BindTeamAttachments()
                            UnEnableRecords()
                            btnOK.CausesValidation = False
                            btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Team.');")
                            TransactionHistory1.LockControl = True
                        Case "AddRow"
                            TransactionHistory1.Visible = False
                            ucTeamAttachments.Visible = False

                            If SessionManager.WorkingSiteID > 0 Then
                                Dim objitem As ListItem = ddlSite.Items.FindByValue(SessionManager.WorkingSiteID)
                                If objitem IsNot Nothing Then
                                    objitem.Selected = True
                                    txtSite.Text = objitem.Text
                                Else
                                    Dim dtSite As DataTable = SiteMaster.GetSiteMasterBySite(SessionManager.WorkingSiteID)
                                    If dtSite IsNot Nothing AndAlso dtSite.Rows.Count = 1 Then
                                        Dim drSite As DataRow = dtSite.Rows(0)
                                        objitem = New ListItem(drSite("Site").ToString, drSite("SiteID").ToString)
                                        ddlSite.Items.Add(objitem)
                                        objitem.Selected = True
                                        txtSite.Text = objitem.Text
                                    End If
                                End If
                            End If

                            txtTeamID.Text = "New"
                            LoadAddModeJavaScripts()
                            UnEnableRecords()
                        Case Else
                            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamsMaintenance"), False)
                    End Select
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - Page_Load", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
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

            Dim bResetTeamBoard As Boolean = False
            If Save(bResetTeamBoard) Then
                If (SessionManager.CallingProgram = "TeamStatus" AndAlso SessionManager.TeamsMode = "EditRow") OrElse (SessionManager.TeamsMode = "AddRow" OrElse SessionManager.TeamsMode = "EditRow") Then
                    SessionManager.TeamsMode = "ViewRow"

                    If bResetTeamBoard Then
                        SessionManager.MasterControlExitProgram2 = "TeamsMaintenance2"
                        Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar + (ProgramSecurity.GetProgramURL("TeamBoardMenuOptionMaster3")), False)

                        Return
                    Else
                        Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar + (ProgramSecurity.GetProgramURL("TeamsMaintenance2")), False)

                        Return
                    End If
                End If

                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueTeamID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamsMode)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.AttachmentsMode)

                RedirectToPriorProgram()
            End If
        End Sub
        Private Sub btnCancel_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnCancel.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.CallingProgram = "TeamStatus" AndAlso SessionManager.TeamsMode = "EditRow" Then
                SessionManager.TeamsMode = "ViewRow"
                Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar + (ProgramSecurity.GetProgramURL("TeamsMaintenance2")), False)
                Return
            End If

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueTeamID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamsMode)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.AttachmentsMode)
            RedirectToPriorProgram()
        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.TeamsMode = "EditRow" Or SessionManager.TeamsMode = "ViewRow" Or SessionManager.TeamsMode = "DeleteRow" Or SessionManager.TeamsMode = "AddRow" Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueTeamID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamsMode)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.AttachmentsMode)
            End If

            RedirectToPriorProgram()
        End Sub
        Private Sub btnTeamMembership_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnTeamMembership.Click, btnTeamMembership2.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.TeamsMode = "ViewRow" Or SessionManager.TeamsMode = "DeleteRow" Then
                SessionManager.MasterControlExitProgram = "TeamsMaintenance2"
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamMembershipMasterMaintenance"), False)
            Else
                Dim bResetTeamBoard As Boolean = False
                If Save(bResetTeamBoard) Then
                    If SessionManager.TeamsMode = "AddRow" Then
                        SessionManager.TeamsMode = "EditRow"
                    End If

                    If bResetTeamBoard Then
                        SessionManager.MasterControlExitProgram = "TeamsMaintenance2"
                        SessionManager.RedirectProgram = "TeamMembershipMasterMaintenance"

                        Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar + (ProgramSecurity.GetProgramURL("TeamBoardMenuOptionMaster3")), False)

                        Return
                    Else
                        SessionManager.MasterControlExitProgram = "TeamsMaintenance2"
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamMembershipMasterMaintenance"), False)
                    End If
                End If
            End If
        End Sub
        Protected Sub btnTeamTrackers_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnTeamTrackers.Click, btnTeamTrackers2.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.TeamsMode = "ViewRow" Or SessionManager.TeamsMode = "DeleteRow" Then
                SessionManager.MasterControlExitProgram = "TeamsMaintenance2"
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TrackerMaster1"), False)
            Else
                Dim bResetTeamBoard As Boolean = False
                If Save(bResetTeamBoard) Then
                    If SessionManager.TeamsMode = "AddRow" Then
                        SessionManager.TeamsMode = "EditRow"
                    End If

                    If bResetTeamBoard Then
                        SessionManager.MasterControlExitProgram = "TeamsMaintenance2"
                        SessionManager.RedirectProgram = "TrackerMaster1"

                        Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar + (ProgramSecurity.GetProgramURL("TeamBoardMenuOptionMaster3")), False)

                        Return
                    Else
                        SessionManager.MasterControlExitProgram = "TeamsMaintenance2"
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TrackerMaster1"), False)
                    End If
                End If
            End If
        End Sub
        Private Sub btnTeamUsers_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnTeamUsers.Click, btnTeamUsers2.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.TeamsMode = "ViewRow" Or SessionManager.TeamsMode = "DeleteRow" Then
                SessionManager.MasterControlExitProgram = "TeamsMaintenance2"
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamUsers1"), False)
            Else
                Dim bResetTeamBoard As Boolean = False
                If Save(bResetTeamBoard) Then
                    If SessionManager.TeamsMode = "AddRow" Then
                        SessionManager.TeamsMode = "EditRow"
                    End If

                    If bResetTeamBoard Then
                        SessionManager.MasterControlExitProgram = "TeamsMaintenance2"
                        SessionManager.RedirectProgram = "TeamUsers1"

                        Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar + (ProgramSecurity.GetProgramURL("TeamBoardMenuOptionMaster3")), False)

                        Return
                    Else
                        SessionManager.MasterControlExitProgram = "TeamsMaintenance2"
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamUsers1"), False)
                    End If
                End If
            End If
        End Sub
        Protected Sub btnTeamKPI_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnTeamKPI.Click, btnTeamKPI2.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.TeamsMode = "ViewRow" Or SessionManager.TeamsMode = "DeleteRow" Then
                SessionManager.MasterControlExitProgram = "TeamsMaintenance2"
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPITeamMaster1"), False)
            Else
                Dim bResetTeamBoard As Boolean = False
                If Save(bResetTeamBoard) Then
                    If SessionManager.TeamsMode = "AddRow" Then
                        SessionManager.TeamsMode = "EditRow"
                    End If

                    If bResetTeamBoard Then
                        SessionManager.MasterControlExitProgram = "TeamsMaintenance2"
                        SessionManager.RedirectProgram = "KPITeamMaster1"

                        Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar + (ProgramSecurity.GetProgramURL("TeamBoardMenuOptionMaster3")), False)

                        Return
                    Else
                        SessionManager.MasterControlExitProgram = "TeamsMaintenance2"
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPITeamMaster1"), False)
                    End If
                End If
            End If
        End Sub
        Protected Sub btnEditTeam_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnEditTeam.Click
            SessionManager.TeamsMode = "EditRow"
            Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar + (ProgramSecurity.GetProgramURL("TeamsMaintenance2")), False)
        End Sub
        Private Sub ucTeamAttachments_AttachClick() Handles ucTeamAttachments.AttachClick
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
                TeamAttachments.AddTeamAttachments(SessionManager.SelectedValueTeamID, Path.GetFileName(ucTeamAttachments.PostedFile.FileName), SessionManager.UserID)
                ucTeamAttachments.Attach(ConfigurationManager.AppSettings("TeamAttachmentsRootDirectory") & txtTeam.Text)
                BindTeamAttachments()
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertTeamAttachments", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
            End Try
        End Sub
        Private Sub ucTeamAttachments_AttachError(ByVal strErrorMessage As String) Handles ucTeamAttachments.AttachError
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, strErrorMessage)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Master.DisplayError(strErrorMessage)
        End Sub
        Protected Sub ucTeamAttachments_DeleteAttachment(ByVal strFileName As String) Handles ucTeamAttachments.DeleteAttachment
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, strFileName)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                TeamAttachments.DeleteTeamAttachments(SessionManager.SelectedValueTeamID, strFileName)
                ucTeamAttachments.Detach(ConfigurationManager.AppSettings("TeamAttachmentsRootDirectory") + Session("SelectedValueTeam"), strFileName)
                BindTeamAttachments()
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteTeamAttachments", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
            End Try
        End Sub
        Private Sub ddlRoute_SelectedIndexChanged(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles ddlRoute.SelectedIndexChanged
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.TeamsMode = "EditRow" Then
                pnlChange.Visible = True
                lblRouteChange.Visible = True
                lblRouteChange2.Visible = True
                If UserSkillRatings.UserSkillsExistByTeamJob(SessionManager.SelectedValueTeamID) = False Then
                    lblRouteChangeJob.Visible = True
                End If
            End If
        End Sub
#End Region

#Region " Custom Methods"
        Public Function Save(ByRef passResetTeamBoard As Boolean) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim blnSuccess As Boolean = False
            If SessionManager.TeamsMode = "EditRow" Then
                If Not ValidateFinishDate() Then
                    Return False
                End If

                blnSuccess = UpdateTeams()

                If lblRouteChange.Visible Then
                    passResetTeamBoard = True
                End If

                If lblRouteChangeJob.Visible Then
                    If ddlRoute.SelectedItem.Value.ToString.Trim.Length > 0 Then
                        JobMaster.DeleteTeamJobByTeam(SessionManager.SelectedValueTeamID)
                        Dim iJobID As Integer = JobMaster.InsertTeamJob(SessionManager.SelectedValueTeamID, txtTeam.Text, SessionManager.WorkingSiteID, ddlRoute.SelectedItem.Value)
                        If iJobID > 0 Then
                            UserJobMaster.AddAllTeamMembersToJob(iJobID, SessionManager.SelectedValueTeamID)
                        End If
                    End If
                End If
            ElseIf SessionManager.TeamsMode = "DeleteRow" Then
                blnSuccess = DeleteTeams()
            ElseIf SessionManager.TeamsMode = "AddRow" Then
                If Not ValidateFinishDate() Then
                    Return False
                End If

                blnSuccess = InsertTeams()
                If blnSuccess Then
                    passResetTeamBoard = True

                    If ddlRoute.SelectedItem.Value.ToString.Trim.Length > 0 Then
                        Dim iJobID As Integer = JobMaster.InsertTeamJob(SessionManager.SelectedValueTeamID, txtTeam.Text, SessionManager.WorkingSiteID, ddlRoute.SelectedItem.Value)
                        If iJobID > 0 Then
                            UserJobMaster.AddAllTeamMembersToJob(iJobID, SessionManager.SelectedValueTeamID)
                        End If
                    End If
                End If
            End If

            Return blnSuccess
        End Function
        Public Function BuildDataTable() As DataTable
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
                Dim ds1 As New DataTable
                ds1 = TeamAttachments.SelectTeamAttachments(SessionManager.SelectedValueTeamID)

                Dim dt As New DataTable
                dt.Columns.Add(New DataColumn("AttachmentsText"))
                dt.Columns.Add(New DataColumn("AttachmentsURL"))
                For Each row As DataRow In ds1.Rows
                    Dim dr As DataRow = dt.NewRow()
                    dr = dt.NewRow
                    dr("AttachmentsText") = GetLinkText(row("Attachment"))
                    dr("AttachmentsURL") = GetNavigateURL(row("Attachment"))
                    dt.Rows.Add(dr)
                Next
                Return dt
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BuildDataset", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                Return Nothing
            End Try
        End Function
        Public Function GetLinkText(ByVal passAttachment As String) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passAttachment)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try
            Select Case SessionManager.TeamsMode.ToString()
                Case "ViewRow", "EditRow", "DeleteRow"
                    Return Path.GetFileName(ConfigurationManager.AppSettings("TeamAttachmentsRootDirectory") & SessionManager.SelectedValueTeam & "\" & passAttachment)
                Case Else
                    Return Path.GetFileName(ConfigurationManager.AppSettings("TeamAttachmentsRootDirectory") & txtTeam.Text & "\" & passAttachment)
            End Select
        End Function
        Public Function GetNavigateURL(ByVal passAttachment As String) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passAttachment)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try
            Select Case SessionManager.TeamsMode.ToString()
                Case "ViewRow", "EditRow", "DeleteRow"
                    Return "http://" & ConfigurationManager.AppSettings("ApplicationServerDNS").ToString & ConfigurationManager.AppSettings("TeamAttachmentsVirtualRootDirectory") & SessionManager.SelectedValueTeam & "/" & passAttachment
                Case Else
                    Return "http://" & ConfigurationManager.AppSettings("ApplicationServerDNS").ToString & ConfigurationManager.AppSettings("TeamAttachmentsVirtualRootDirectory") & txtTeam.Text & "/" & passAttachment
            End Select
        End Function
        Public Function GetRouteDefinition(ByVal passRouteAbbrev As String) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passRouteAbbrev)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim dt As DataTable = Routes.SelectRoutesByKey(passRouteAbbrev)
                Return dt.Rows(0).Item("RouteDefinition")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - GetRouteDefinition", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                Return ""
            End Try
        End Function
        Private Sub LoadSelectedRecord()
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
                Dim dt As DataTable = Teams.SelectTeams(SessionManager.SelectedValueTeamID)
                If dt.Rows.Count <> 0 Then
                    Dim dr As DataRow = dt.Rows(0)
                    Dim objItem As ListItem

                    txtTeamID.Text = SessionManager.SelectedValueTeamID.ToString
                    txtTeam.Text = dr.Item("Team").ToString.Trim()
                    txtTeamName.Text = dr.Item("TeamName").ToString.Trim()
                    txtTeamNameOther.Text = dr("TeamNameOther").ToString.Trim
                    txtDeptNumber.Text = dr.Item("DeptNumber").ToString.Trim()
                    txtTeamFolder.Text = dr("TeamFolder").ToString.Trim
                    If IsDate(dr("TeamStartDate")) Then
                        txtStartDate.Text = Convert.ToDateTime("" + dr("TeamStartDate")).ToShortDateString
                    Else
                        txtStartDate.Text = String.Empty
                    End If
                    If IsDate(dr("TeamFinishDate")) Then
                        txtFinishDate.Text = Convert.ToDateTime("" + dr("TeamFinishDate")).ToShortDateString
                    Else
                        txtFinishDate.Text = String.Empty
                    End If

                    objItem = ddlTeamBoardType.Items.FindByValue(dr("TeamBoardType").ToString)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                        txtTeamBoardType.Text = objItem.Text
                    End If

                    objItem = ddlPillar.Items.FindByValue(dr.Item("PillarAbbrev").ToString.Trim())
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                        txtPillar.Text = objItem.Text
                    End If

                    objItem = ddlBusinessArea.Items.FindByValue(dr("BusinessAreaID").ToString)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                        txtBusinessArea.Text = objItem.Text
                    End If

                    objItem = ddlBusinessUnit.Items.FindByValue(dr.Item("BusinessUnitID").ToString.Trim())
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                        txtBusinessUnit.Text = objItem.Text
                    End If

                    objItem = ddlSite.Items.FindByValue(dr("SiteID").ToString.Trim())
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                        txtSite.Text = objItem.Text
                    ElseIf IsNumeric(dr("SiteID").ToString) Then
                        Dim dtSite As DataTable = SiteMaster.GetSiteMasterBySite(dr("SiteID").ToString)
                        If dtSite IsNot Nothing AndAlso dtSite.Rows.Count = 1 Then
                            objItem = New ListItem(dtSite.Rows(0)("Site").ToString, dtSite.Rows(0)("SiteID").ToString)
                            objItem.Selected = True
                            txtSite.Text = objItem.Text
                        End If
                    End If

                    objItem = ddlRoute.Items.FindByValue(dr.Item("RouteAbbrev").ToString.Trim())
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                        txtRoute.Text = objItem.Text
                    End If

                    objItem = ddlMasterPlanType.Items.FindByValue(dr("MasterPlanType").ToString)
                    If Not IsNothing(objItem) Then
                        objItem.Selected = True
                        txtMasterPlanType.Text = objItem.Text
                    End If

                    objItem = ddlStatus.Items.FindByValue(dr("TeamStatus").ToString)
                    If Not IsNothing(objItem) Then
                        objItem.Selected = True
                        txtTeamStatus.Text = objItem.Text
                    End If

                    objItem = ddlTeamCategory.Items.FindByText(dr("TeamCategory").ToString)
                    If Not objItem Is Nothing Then
                        objItem.Selected = True
                        txtTeamCategory.Text = objItem.Text
                    End If

                    objItem = ddlTeamType.Items.FindByValue(dr("TeamTypeID").ToString)
                    If Not objItem Is Nothing Then
                        objItem.Selected = True
                        txtTeamType.Text = objItem.Text
                    End If

                    ckAllUsersView.Checked = Convert.ToBoolean(dr("AllUsersView"))
                    ckMembersOnly.Checked = Convert.ToBoolean(dr("MembersOnly"))

                    txtMaintenanceUserID.Text = dr.Item("MaintenanceUserID")
                    txtMaintenanceDate.Text = Convert.ToDateTime("" + dr.Item("MaintenanceDate")).ToString(Session("DateTimeFormat"))

                    TransactionHistory1.TableName = DBTableName
                    TransactionHistory1.RecordID = SessionManager.SelectedValueTeamID

                    Dim objDic As New Dictionary(Of String, String)
                    objDic.Add("TeamName", txtTeamName.Text.Trim())
                    objDic.Add("TeamNameOther", txtTeamNameOther.Text.Trim())
                    objDic.Add("Site", ddlSite.SelectedItem.Text.Trim())
                    objDic.Add("BusinessArea", ddlBusinessArea.SelectedItem.Text.Trim())
                    objDic.Add("BusinessUnit", ddlBusinessUnit.SelectedItem.Text.Trim())
                    objDic.Add("PillarAbbrev", ddlPillar.SelectedItem.Text.Trim())
                    objDic.Add("RouteAbbrev", ddlRoute.SelectedItem.Text.Trim())
                    objDic.Add("DeptNumber", txtDeptNumber.Text.Trim())
                    objDic.Add("TeamFolder", txtTeamFolder.Text.Trim())
                    objDic.Add("TeamStartDate", txtStartDate.Text.Trim())
                    objDic.Add("TeamFinishDate", txtFinishDate.Text.Trim())
                    objDic.Add("TeamBoardType", ddlTeamBoardType.SelectedItem.Text.Trim())
                    objDic.Add("MasterPlanType", ddlMasterPlanType.SelectedItem.Text.Trim())
                    objDic.Add("TeamStatus", ddlStatus.SelectedItem.Text.Trim())
                    objDic.Add("TeamType", ddlTeamType.SelectedItem.Text.Trim())
                    objDic.Add("TeamCategory", ddlTeamCategory.SelectedItem.Text.Trim())
                    objDic.Add("AllUsersView", ckAllUsersView.Checked.ToString())
                    objDic.Add("MembersOnly", ckMembersOnly.Checked.ToString())
                    SessionManager.RecordTransactionCurrentValues = objDic
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub LoadDropdownLists()
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
                BindSiteMaster()
                BindBusinessAreaMaster()
                BindBusinessUnitMaster()
                BindTeamCategory()
                BindPillars()
                BindTeamBoardType()
                BindRoutes()
                BindTeamTypes()
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadDropdownLists", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindSiteMaster()
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
                SiteMaster.SelectSiteMasterActiveList(ddlSite)
                ddlSite.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindSiteMaster", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindBusinessAreaMaster()
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
                BusinessAreaMaster.GetBusinessAreaMasterList(ddlBusinessArea)
                ddlBusinessArea.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindBusinessUnit", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindBusinessUnitMaster()
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
                BusinessUnitMaster.SelectBusinessUnitMasterList(ddlBusinessUnit)
                ddlBusinessUnit.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindBusinessUnit", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindTeamCategory()
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
                TeamCategoryMaster.SelectTeamCategoryMasterList(ddlTeamCategory)
                ddlTeamCategory.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindTeamCategory", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindPillars()
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
                Pillars.SelectPillarList(ddlPillar)
                ddlPillar.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindPillar", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindTeamBoardType()
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
                ddlTeamBoardType.Items.Insert(0, "Step")
                ddlTeamBoardType.Items.Insert(1, "Pillar")
                ddlTeamBoardType.Items.Insert(2, "Generic")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindTeamBoardType", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindRoutes()
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
                Routes.SelectRoutesList(ddlRoute)
                ddlRoute.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindRoute", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindTeamTypes()
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
                ddlTeamType.Items.Clear()
                TeamTypes.SelectTeamTypesMasterList(ddlTeamType)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindTeamTypes", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindTeamAttachments()
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
                SessionManager.AttachmentsMode = SessionManager.TeamsMode
                ucTeamAttachments.Visible = True
                ucTeamAttachments.DataSource = BuildDataTable()
                ucTeamAttachments.DataBind()

                Select Case SessionManager.TeamsMode.ToString()
                    Case "ViewRow", "DeleteRow"
                        ucTeamAttachments.AllowEdit = False
                    Case Else
                        ucTeamAttachments.AllowEdit = True
                End Select
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindTeamAttachments", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindTeamActionItems()
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
                Dim objDT As DataTable = TeamActionPlan.SelectTeamActionPlansByTeam(SessionManager.SelectedValueTeamID, 0)
                gvTeamActionItems.DataSource = objDT
                gvTeamActionItems.DataBind()
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindTeamActionItems", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindTeamMembership()
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
                Dim dt As DataTable = TeamMembership.SelectTeamMembershipDisplayByTeam(SessionManager.SelectedValueTeamID)
                If dt.Rows.Count > 0 Then
                    gvTeamMembership.DataSource = dt
                    gvTeamMembership.DataBind()
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindTeamMembership", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindTeamTrackers()
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
                Dim dt As DataTable = Trackers.SelectTeamTrackers(SessionManager.SelectedValueTeamID)
                gvTeamTrackers.DataSource = dt
                gvTeamTrackers.DataBind()
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindTeamTrackers", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindTeamKPIs()
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
                Dim dt As DataTable = KPITeamMaster.SelectKPITeamByTeam(SessionManager.SelectedValueTeamID)
                gvTeamKPIs.DataSource = dt
                gvTeamKPIs.DataBind()
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindTeamKPIs", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub UnEnableRecords()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Select Case SessionManager.TeamsMode.ToString()
                Case "ViewRow", "DeleteRow"
                    If SessionManager.TeamsMode = "ViewRow" Then
                        pnlExit.Visible = True
                        pnlOKCancel.Visible = False
                    End If
                    imgStartDate.Visible = False
                    txtStartDate_CalendarExtender.Enabled = False
                    imgFinishDate.Visible = False
                    txtFinishDate_CalendarExtender.Enabled = False
                    txtTeam.ReadOnly = True
                    txtTeam.CssClass = "Textbox_Display"
                    txtTeamName.ReadOnly = True
                    txtTeamName.CssClass = "Textbox_Display"
                    txtTeamNameOther.ReadOnly = True
                    txtTeamNameOther.CssClass = "Textbox_Display"
                    ddlSite.Visible = False
                    txtSite.Visible = True
                    ddlBusinessArea.Visible = False
                    txtBusinessArea.Visible = True
                    ddlBusinessUnit.Visible = False
                    txtBusinessUnit.Visible = True
                    ddlPillar.Visible = False
                    txtPillar.Visible = True
                    ddlRoute.Visible = False
                    txtRoute.Visible = True
                    txtDeptNumber.ReadOnly = True
                    txtDeptNumber.CssClass = "Textbox_Display"
                    txtTeamFolder.ReadOnly = True
                    txtTeamFolder.CssClass = "Textbox_Display"
                    fiTeamFolder.Visible = False
                    lblTeamFolderMessage.Visible = False
                    txtStartDate.ReadOnly = True
                    txtStartDate.CssClass = "Textbox_Display"
                    If txtStartDate.Text = "YYYY/MM/DD" Then
                        txtStartDate.Text = "0"
                    End If
                    txtFinishDate.ReadOnly = True
                    txtFinishDate.CssClass = "Textbox_Display"
                    If txtFinishDate.Text = "YYYY/MM/DD" Then
                        txtFinishDate.Text = "0"
                    End If
                    ddlTeamBoardType.Visible = False
                    txtTeamBoardType.Visible = True
                    ddlMasterPlanType.Visible = False
                    txtMasterPlanType.Visible = True
                    ddlStatus.Visible = False
                    txtTeamStatus.Visible = True
                    ddlTeamType.Visible = False
                    txtTeamType.Visible = True
                    ddlTeamCategory.Visible = False
                    txtTeamCategory.Visible = True
                    ckAllUsersView.Enabled = False
                    ckMembersOnly.Enabled = False
                    txtMaintenanceDate.Visible = True
                    lblMaintenanceDate.Visible = True
                    txtMaintenanceUserID.Visible = True
                    lblMaintenanceUserID.Visible = True
                Case "EditRow"
                    'If TeamRouteSteps.RouteLockedForTeam(SessionManager.SelectedValueTeamID) = True OrElse Not CheckIfTeamBoardMenuOptionMasterByTeamExist(SessionManager.SelectedValueTeamID) Then
                    If TeamRouteSteps.RouteLockedForTeam(SessionManager.SelectedValueTeamID) = True Then
                        txtRoute.Visible = True
                        ddlRoute.Visible = False
                    End If
                    lblTeamPhoto.Visible = True
                    imgStartDate.Visible = True
                    imgFinishDate.Visible = True
                    txtTeam.ReadOnly = True
                    txtTeam.CssClass = "Textbox_Display"
                    txtMaintenanceDate.Visible = True
                    lblMaintenanceDate.Visible = True
                    txtMaintenanceUserID.Visible = True
                    lblMaintenanceUserID.Visible = True
                    fiTeamFolder.Visible = True
                    lblTeamFolderMessage.Visible = True
                    txtTeamName.Focus()
                Case "AddRow"
                    imgStartDate.Visible = True
                    imgFinishDate.Visible = True
                    txtMaintenanceDate.Visible = False
                    lblMaintenanceDate.Visible = False
                    txtMaintenanceUserID.Visible = False
                    lblMaintenanceUserID.Visible = False
                    lblTeamActionItems.Visible = False
                    lblTeamMembership.Visible = False
                    lblTeamTrackers.Visible = False
                    lblTeamKPI.Visible = False
                    fiTeamFolder.Visible = True
                    lblTeamFolderMessage.Visible = True
                    If String.IsNullOrEmpty(txtTeamStatus.Text.Trim()) Then
                        txtTeamStatus.Text = "O"
                    End If
                    txtTeam.Focus()
            End Select
        End Sub
        Private Sub CheckMembersOnlySecurity()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            ' Only care about this when Edit mode
            If SessionManager.TeamsMode = "EditRow" Then
                Try
                    'If the team has at least one meeting then only members can modify the 'Members Only' checkbox
                    Dim objDT As DataTable = Teams.SelectMyTeamSecurity(SessionManager.UserID, SessionManager.SelectedValueTeamID)
                    If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                        If Convert.ToInt32(objDT.Rows(0)("TeamMeetings")) > 0 Then
                            If Not Convert.ToBoolean(objDT.Rows(0)("TeamMember")) Then
                                ckMembersOnly.ToolTip = "You do not have the authority to modify this value"
                                ckMembersOnly.Enabled = False
                            End If
                        End If
                    End If
                Catch ex As Exception

                End Try
            End If
        End Sub
        Private Sub RedirectToPriorProgram()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.CallingProgram > "" Then
                Dim strCallingProgram As String = SessionManager.CallingProgram
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CallingProgram)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamMeetingsMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strCallingProgram), False)
            Else
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamsMaintenance"), False)
            End If
        End Sub
        Private Function InsertTeams() As Boolean
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
                If Not String.IsNullOrEmpty(txtStartDate.Text.Trim()) Then
                    If Not IsDate(txtStartDate.Text) Then
                        Master.DisplayError("Invalid Start Date")
                        txtStartDate.Focus()
                        Return False
                    End If
                End If
                If Not String.IsNullOrEmpty(txtFinishDate.Text.Trim()) Then
                    If Not IsDate(txtFinishDate.Text) Then
                        Master.DisplayError("Invalid Finish Date")
                        txtFinishDate.Focus()
                        Return False
                    End If
                End If

                If ddlStatus.SelectedItem Is Nothing OrElse ddlStatus.SelectedItem.Value.Trim.Length = 0 Then
                    Master.DisplayError("Invalid Team Status")
                    ddlStatus.Focus()
                    Return False
                End If

                If ckAllUsersView.Checked AndAlso ckMembersOnly.Checked Then
                    Master.DisplayError("Select either 'All Users View' OR 'Members Only'")
                    Return False
                End If

                Dim strStartDate As String = RegionalConversion.FormatSQLDate(txtStartDate.Text)
                Dim strFinishDate As String = RegionalConversion.FormatSQLDate(txtFinishDate.Text)
                Dim strPillar As String = ddlPillar.SelectedItem.Value
                Dim strRoute As String = ddlRoute.SelectedItem.Value
                Dim strTeamCategory As String = ddlTeamCategory.SelectedValue.ToString()
                Dim iNewTeamMembers As Integer = -1

                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                SessionManager.SelectedValueTeamID = Teams.AddTeams(txtTeam.Text.Trim, txtTeamName.Text.Trim, txtTeamNameOther.Text.Trim, CInt(ddlSite.SelectedItem.Value), ddlBusinessArea.SelectedItem.Value, ddlBusinessUnit.SelectedItem.Value, strPillar, strRoute, txtDeptNumber.Text.Trim(), strStartDate, strFinishDate, ddlStatus.SelectedItem.Value.ToString.ToUpper(), txtTeamFolder.Text.Trim, ddlTeamBoardType.SelectedValue.ToString.Trim(), ddlMasterPlanType.SelectedValue.ToString.Trim, strTeamCategory, iNewTeamMembers, ckAllUsersView.Checked, ckMembersOnly.Checked, SessionManager.UserID, Convert.ToInt32(ddlTeamType.SelectedItem.Value.ToString))
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueTeamID, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertTeams", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateTeams() As Boolean
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
                If Not String.IsNullOrEmpty(txtStartDate.Text.Trim()) Then
                    If Not IsDate(txtStartDate.Text) Then
                        Master.DisplayError("Invalid Start Date")
                        txtStartDate.Focus()
                        Return False
                    End If
                End If
                If Not String.IsNullOrEmpty(txtFinishDate.Text.Trim()) Then
                    If Not IsDate(txtFinishDate.Text) Then
                        Master.DisplayError("Invalid Finish Date")
                        txtFinishDate.Focus()
                        Return False
                    End If
                End If

                If IsNothing(ddlStatus.SelectedItem) Or ddlStatus.SelectedItem.Value.Trim.Length = 0 Then
                    Master.DisplayError("Invalid Team Status")
                    ddlStatus.Focus()
                    Return False
                End If

                If ckAllUsersView.Checked AndAlso ckMembersOnly.Checked Then
                    Master.DisplayError("Select either 'All Users View' OR 'Members Only'")
                    Return False
                End If

                Dim strStartDate As String = RegionalConversion.FormatSQLDate(txtStartDate.Text)
                Dim strFinishDate As String = RegionalConversion.FormatSQLDate(txtFinishDate.Text)
                Dim strTeamCategory As String = ddlTeamCategory.SelectedValue.ToString()
                Dim iNewTeamMembers As Integer = -1

                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.CompareDictionaryValues(SessionManager.RecordTransactionCurrentValues, objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                Teams.UpdateTeams(SessionManager.SelectedValueTeamID, txtTeam.Text.Trim, txtTeamName.Text.Trim(), txtTeamNameOther.Text.Trim, CInt(ddlSite.SelectedItem.Value), ddlBusinessArea.SelectedItem.Value, ddlBusinessUnit.SelectedItem.Value, ddlPillar.SelectedValue.ToString.Trim(), ddlRoute.SelectedValue.ToString.Trim(), txtDeptNumber.Text.Trim(), strStartDate, strFinishDate, ddlStatus.SelectedItem.Value.ToString.ToUpper(), txtTeamFolder.Text.Trim, ddlTeamBoardType.SelectedValue.ToString.Trim(), ddlMasterPlanType.SelectedValue.ToString.Trim, strTeamCategory, iNewTeamMembers, ckAllUsersView.Checked, ckMembersOnly.Checked, Session("UserID"), Convert.ToInt32(ddlTeamType.SelectedItem.Value))
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueTeamID, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateTeams", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function DeleteTeams() As Boolean
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

                If TeamRouteSteps.RouteLockedForTeam(SessionManager.SelectedValueTeamID) Then
                    Master.DisplayError("Clear all Team Route Step dates to delete this team.")
                    Return False
                End If

                Teams.DeleteTeams(SessionManager.SelectedValueTeamID)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueTeamID, "Team Deleted", SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteTeams", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
        End Function
        Private Function ValidateFinishDate() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If Not String.IsNullOrEmpty(txtFinishDate.Text.Trim()) Then
                If Not IsDate(txtFinishDate.Text) Then
                    Master.DisplayError("Invalid Date")
                    txtFinishDate.Focus()
                    Return False
                End If
            End If
            Return True
        End Function
        Private Function CheckIfTeamBoardMenuOptionMasterByTeamExist(ByVal passTeamID As Integer) As Boolean
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
                Return TeamBoardMenuOptionMaster.TeamBoardMenuOptionMasterByTeamExist(passTeamID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - CheckIfTeamBoardMenuOptionMasterByTeamExist", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Function
        Private Function GetUpdatedValues() As Dictionary(Of String, String)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim objDic As New Dictionary(Of String, String)
            objDic.Add("TeamName", txtTeamName.Text.Trim())
            objDic.Add("TeamNameOther", txtTeamNameOther.Text.Trim())
            objDic.Add("Site", ddlSite.SelectedItem.Text.Trim())
            objDic.Add("BusinessUnit", ddlBusinessUnit.SelectedItem.Text.Trim())
            objDic.Add("PillarAbbrev", ddlPillar.SelectedItem.Text.Trim())
            objDic.Add("RouteAbbrev", ddlRoute.SelectedItem.Text.Trim())
            objDic.Add("DeptNumber", txtDeptNumber.Text.Trim())
            objDic.Add("TeamFolder", txtTeamFolder.Text.Trim())
            objDic.Add("TeamStartDate", txtStartDate.Text.Trim())
            objDic.Add("TeamFinishDate", txtFinishDate.Text.Trim())
            objDic.Add("TeamBoardType", ddlTeamBoardType.SelectedItem.Text.Trim())
            objDic.Add("MasterPlanType", ddlMasterPlanType.SelectedItem.Text.Trim())
            objDic.Add("TeamStatus", ddlStatus.SelectedItem.Text.Trim())
            objDic.Add("TeamType", ddlTeamType.SelectedItem.Text.Trim())
            objDic.Add("TeamCategory", ddlTeamCategory.SelectedItem.Text.Trim())
            objDic.Add("AllUsersView", ckAllUsersView.Checked.ToString())
            objDic.Add("MembersOnly", ckMembersOnly.Checked.ToString())

            Return objDic
        End Function
#End Region

    End Class
End Namespace
