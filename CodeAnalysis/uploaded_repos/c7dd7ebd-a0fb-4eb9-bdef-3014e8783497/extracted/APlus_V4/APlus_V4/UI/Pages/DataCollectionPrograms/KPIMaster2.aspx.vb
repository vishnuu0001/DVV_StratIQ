#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports System.Collections.Generic

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class KPIMaster2
        Inherits ApplicationBase

#Region " Private Variables"
        Private Shared ReadOnly FormName As String = "KPI Maintenance"
        Private Shared ReadOnly ProgramName As String = "KPIMaster2"
        Private Shared ReadOnly DBTableName As String = "KPIMaster"
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
                lblKPI.Text = GetTranslationString("kpi", lblKPI.Text.Replace(":", "")) & ":"
                lblKPIEnglish.Text = GetTranslationString("kpienglish", lblKPIEnglish.Text.Replace(":", "")) & ":"
                lblDescription.Text = GetTranslationString("description", lblDescription.Text.Replace(":", "")) & ":"
                lblUOM.Text = GetTranslationString("uom", lblUOM.Text.Replace(":", "")) & ":"
                lblTargetUp.Text = GetTranslationString("targetup", lblTargetUp.Text.Replace(":", "")) & ":"
                lblSite.Text = GetTranslationString("site", lblSite.Text.Replace(":", "")) & ":"
                lblCategory.Text = GetTranslationString("category", lblCategory.Text.Replace(":", "")) & ":"
                lblSortSequence.Text = GetTranslationString("sortsequence", lblSortSequence.Text.Replace(":", "")) & ":"
                lblPillar.Text = GetTranslationString("pillar", lblPillar.Text.Replace(":", "")) & ":"
                lblBusinessArea.Text = GetTranslationString("businessarea", lblBusinessArea.Text)
                lblBusinessUnit.Text = GetTranslationString("businessunit", lblBusinessUnit.Text)
                lblReportingLevel.Text = GetTranslationString("reportinglevel", lblReportingLevel.Text)
                lblSummaryType.Text = GetTranslationString("summaryype", lblSummaryType.Text.Replace(":", "")) & ":"
                lblResponsibleUser.Text = GetTranslationString("responsibleuser", lblResponsibleUser.Text.Replace(":", "")) & ":"
                lblArea.Text = GetTranslationString("area", lblArea.Text.Replace(":", "")) & ":"
                lblInterface.Text = GetTranslationString("interface", lblInterface.Text.Replace(":", "")) & ":"
                lblFormula.Text = GetTranslationString("formula", lblFormula.Text.Replace(":", "")) & ":"
                lblNoNotification.Text = GetTranslationString("nonotifications", lblNoNotification.Text.Replace(":", "")) & ":"
                lblScheduleCode.Text = GetTranslationString("schedulecode", lblScheduleCode.Text.Replace(":", "")) & ":"
                lblScheduleTime.Text = GetTranslationString("scheduletime", lblScheduleTime.Text.Replace(":", "")) & ":"
                lblNextExecution.Text = GetTranslationString("nextexecution", lblNextExecution.Text.Replace(":", "")) & ":"
                lblLastExecution.Text = GetTranslationString("lastexecution", lblLastExecution.Text.Replace(":", "")) & ":"
                lblLastExecutionSuccessful.Text = GetTranslationString("lastexecutionsuccessful", lblLastExecutionSuccessful.Text.Replace(":", "")) & ":"
                lblOnDemandExecute.Text = GetTranslationString("ondemandexecute", lblOnDemandExecute.Text.Replace(":", "")) & ":"
                lblActive.Text = GetTranslationString("active", lblActive.Text.Replace(":", "")) & ":"
                lblPrimaryKPI.Text = GetTranslationString("primarykpi", lblPrimaryKPI.Text.Replace(":", "")) & ":"
                lblAutoMonth.Text = GetTranslationString("automonthanomaly", lblAutoMonth.Text.Replace(":", "")) & ":"
                lblAutoYTD.Text = GetTranslationString("autoytdanomaly", lblAutoYTD.Text.Replace(":", "")) & ":"
                lblAnomalyResponsibleUser.Text = GetTranslationString("anomalyresponsibleuser", lblAnomalyResponsibleUser.Text.Replace(":", "")) & ":"
                lblDailyKPI.Text = GetTranslationString("dailykpi", lblDailyKPI.Text.Replace(":", "")) & ":"
                lblDailyInterface.Text = GetTranslationString("dailyinterface", lblDailyInterface.Text.Replace(":", "")) & ":"
                lblDailyCompare.Text = GetTranslationString("dailycompare", lblDailyCompare.Text.Replace(":", "")) & ":"
                lblKPITeamsHeader.Text = GetTranslationString("kpiteams", lblKPITeamsHeader.Text)
                lblKPINotification.Text = GetTranslationString("kpinotification", lblKPINotification.Text)
                lblKPIDataElements.Text = GetTranslationString("kpidataelements", lblKPIDataElements.Text)
                lblElement.Text = GetTranslationString("element", lblElement.Text)
                btnOK.Text = GetTranslationString("ok", btnOK.Text)
                btnCancel.Text = GetTranslationString("cancel", btnCancel.Text)
                btnExit.Text = GetTranslationString("exit", btnExit.Text)
                btnTeamKPI.Text = GetTranslationString("kpiteams", btnTeamKPI.Text)
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
            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnExit.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
        End Sub
        Private Sub LoadAddEditModeJavaScripts()
            Dim myTabArray() As Object = {txtKPI, _
                                          txtKPIOther, _
                                          txtExpandDescription, _
                                          txtUOM, _
                                          ckTargetUp, _
                                          ddlSite, _
                                          ddlCategory, _
                                          txtSortSequence, _
                                          ddlPillar, _
                                          ddlBusinessArea, _
                                          ddlBusinessUnit, _
                                          ddlReportingLevel, _
                                          txtSummaryType, _
                                          ddlResponsibleUser, _
                                          ddlArea, _
                                          ckInterface, _
                                          txtExpandFormula, _
                                          txtScheduleCode, _
                                          txtScheduleTime, _
                                          txtOnDemandExecute, _
                                          ckNoNotifications, _
                                          ckActive, _
                                          ddlPrimaryKPI, _
                                          ckAutoMonth, _
                                          ckAutoYTD, _
                                          ddlAnomalyResponsibleUser,
                                          ckDailyKPI,
                                          ckDailyInterface, _
                                          ckDailyCompare}

            Dim TabKeyDownArr() As String = {Tab(txtKPIOther, ckDailyCompare, "No"), _
                                             Tab(txtExpandDescription, txtKPI, "No"), _
                                             Tab(txtUOM, txtKPIOther, "No"), _
                                             Tab(ckTargetUp, txtExpandDescription, "No"), _
                                             Tab(ddlSite, txtUOM, "No"), _
                                             Tab(ddlCategory, ckTargetUp, "No"), _
                                             Tab(txtSortSequence, ddlSite, "No"), _
                                             Tab(ddlPillar, ddlCategory, "Int"), _
                                             Tab(ddlBusinessArea, txtSortSequence, "No"), _
                                             Tab(ddlBusinessUnit, ddlPillar, "No"), _
                                             Tab(ddlReportingLevel, ddlBusinessArea, "No"), _
                                             Tab(txtSummaryType, ddlBusinessUnit, "No"), _
                                             Tab(ddlResponsibleUser, ddlReportingLevel, "No"), _
                                             Tab(ddlArea, txtSummaryType, "No"), _
                                             Tab(ckInterface, ddlResponsibleUser, "No"), _
                                             Tab(txtExpandFormula, ddlArea, "No"), _
                                             Tab(txtScheduleCode, ckInterface, "No"), _
                                             Tab(txtScheduleTime, txtExpandFormula, "No"), _
                                             Tab(txtOnDemandExecute, txtScheduleCode, "Int"), _
                                             Tab(ckNoNotifications, txtScheduleTime, "No"), _
                                             Tab(ckActive, txtOnDemandExecute, "No"), _
                                             Tab(ddlPrimaryKPI, ckNoNotifications, "No"), _
                                             Tab(ckAutoMonth, ckActive, "No"), _
                                             Tab(ckAutoYTD, ddlPrimaryKPI, "No"), _
                                             Tab(ddlAnomalyResponsibleUser, ckAutoMonth, "No"), _
                                             Tab(ckDailyKPI, ckAutoYTD, "No"), _
                                             Tab(ckDailyInterface, ddlAnomalyResponsibleUser, "No"), _
                                             Tab(ckDailyCompare, ckDailyKPI, "No"), _
                                             Tab(txtKPI, ckDailyInterface, "No")}

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

            Master.HeaderMessage = GetTranslationString(FormName, FormName) & " - " & GetTranslationString(SessionManager.KPIMasterMode.Replace("Row", ""), SessionManager.KPIMasterMode.Replace("Row", ""))
            Master.IconImage = Request.ApplicationPath + "/images/boss.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/" & SessionManager.CulturePref & "/DataEntry.js")
            LoadCommonJavaScripts()

            mcKPITeams.StoredProcedureParams.Add("@KPIID", SessionManager.SelectedValueKPIID)
            mcKPINotifications.StoredProcedureParams.Add("@KPIID", SessionManager.SelectedValueKPIID)
            mcKPIDataElements.StoredProcedureParams.Add("@KPIID", SessionManager.SelectedValueKPIID)

            Dim strSessionID As String = Session.SessionID.ToString
            strSessionID = "(S(" + strSessionID + "))"
            imgElements.Attributes.Add("onclick", "window.open('/APlus/" + strSessionID + "/UI/Pages/DataCollectionPrograms/DataElementsListing.aspx','newWin','height=500, width=500, left=500, top=100, resizable=yes, scrollbars=1');")

            If Not Page.IsPostBack Then
                LoadCultureTranslations()

                LoadDropDowns()

                Select Case SessionManager.KPIMasterMode.ToString()
                    Case "ViewRow"
                        pnlExit.Visible = True
                        pnlOKCancel.Visible = False
                        LoadSelectedRecord()
                        UnEnableRecords()
                        imgElements.Visible = False
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this KPI.');")
                        TransactionHistory1.LockControl = True
                        imgElements.Visible = False
                    Case "AddRow"
                        pnlGrids.Visible = False
                        btnTeamKPI.Visible = False
                        btnKPINotifications.Visible = False
                        TransactionHistory1.Visible = False
                        LoadAddEditModeJavaScripts()

                        If SessionManager.WorkingSiteID > 0 Then
                            Dim objItem As ListItem = ddlSite.Items.FindByValue(SessionManager.WorkingSiteID)
                            If objItem IsNot Nothing Then
                                objItem.Selected = True
                                txtSite.Text = objItem.Text

                                LoadPrimaryKPIDDL()
                                LoadAreaMasterDDL()
                            Else
                                Dim dtSite As DataTable = SiteMaster.GetSiteMasterBySite(SessionManager.WorkingSiteID)
                                If dtSite IsNot Nothing AndAlso dtSite.Rows.Count = 1 Then
                                    Dim drSite As DataRow = dtSite.Rows(0)
                                    objItem = New ListItem(drSite("SiteAbbrev").ToString & " - " & drSite("Site").ToString, drSite("SiteID").ToString)
                                    ddlSite.Items.Add(objItem)
                                    objItem.Selected = True
                                    txtSite.Text = objItem.Text

                                    LoadPrimaryKPIDDL()
                                    LoadAreaMasterDDL()
                                End If
                            End If
                        End If

                        UnEnableRecords()
                        ckActive.Checked = True
                        txtKPI.Focus()
                    Case "EditRow"
                        LoadAddEditModeJavaScripts()
                        LoadSelectedRecord()
                        UnEnableRecords()
                        txtKPI.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPIMaster1"), False)
                End Select
            End If
        End Sub
        Protected Sub ddlUserSite_SelectedIndexChanged(ByVal sender As Object, ByVal e As System.EventArgs) Handles ddlUserSite.SelectedIndexChanged
            LoadResponsibleUserDDL()
        End Sub
        Protected Sub ddlAnomalyUserSite_SelectedIndexChanged(ByVal sender As Object, ByVal e As System.EventArgs) Handles ddlAnomalyUserSite.SelectedIndexChanged
            LoadAnomalyResponsibleUserDDL()
        End Sub
        Protected Sub ddlPrimaryKPISite_SelectedIndexChanged(ByVal sender As Object, ByVal e As System.EventArgs) Handles ddlPrimaryKPISite.SelectedIndexChanged
            LoadPrimaryKPIDDL()
        End Sub
        Private Sub btnOK_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim blnSuccess As Boolean
            Select Case SessionManager.KPIMasterMode.ToString()
                Case "AddRow"
                    blnSuccess = InsertKPIMaster()
                Case "EditRow"
                    blnSuccess = UpdateKPIMaster()
                Case "DeleteRow"
                    blnSuccess = DeleteKPIMaster()
            End Select

            If blnSuccess Then
                Dim strProgram As String = "KPIMaster1"
                If Not String.IsNullOrEmpty(SessionManager.CallingProgram2) Then
                    strProgram = SessionManager.CallingProgram2
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CallingProgram2)
                ElseIf SessionManager.CallingProgram.Trim.Length > 0 Then
                    strProgram = SessionManager.CallingProgram
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CallingProgram)
                Else
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueKPIID)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.KPIMasterMode)
                End If

                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strProgram), False)
            End If
        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click, btnCancel.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim strProgram As String = "KPIMaster1"
            If Not String.IsNullOrEmpty(SessionManager.CallingProgram2) Then
                strProgram = SessionManager.CallingProgram2
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CallingProgram2)
            ElseIf SessionManager.CallingProgram.Trim.Length > 0 Then
                strProgram = SessionManager.CallingProgram
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CallingProgram)
            Else
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueKPIID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.KPIMasterMode)
            End If
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strProgram), False)
        End Sub
        Protected Sub btnTeamKPI_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnTeamKPI.Click
            Select Case SessionManager.KPIMasterMode
                Case "EditRow"
                    If UpdateKPIMaster() Then
                        SessionManager.MasterControlExitProgram = ProgramName
                        Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPITeamMaster1"), False)
                    End If
                Case "DeleteRow"
                    SessionManager.MasterControlExitProgram = ProgramName
                    Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPITeamMaster1"), False)
            End Select
        End Sub
        Protected Sub btnKPINotifications_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnKPINotifications.Click
            Select Case SessionManager.KPIMasterMode
                Case "EditRow"
                    If UpdateKPIMaster() Then
                        SessionManager.MasterControlExitProgram = ProgramName
                        Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPIUserNotifications1"), False)
                    End If
                Case "DeleteRow"
                    SessionManager.MasterControlExitProgram = ProgramName
                    Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPIUserNotifications1"), False)
            End Select
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadDropDowns()
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
                SiteMaster.SelectSiteMasterAbbrevList(ddlSite)
                ddlSite.Items.Insert(0, "")

                Pillars.SelectPillarList(ddlPillar)
                ddlPillar.Items.Insert(0, "")

                BusinessAreaMaster.GetBusinessAreaMasterAbbrevList(ddlBusinessArea)
                ddlBusinessArea.Items.Insert(0, "")

                BusinessUnitMaster.SelectBusinessUnitMasterAbbrevList(ddlBusinessUnit)
                ddlBusinessUnit.Items.Insert(0, "")

                TeamCategoryMaster.GetTeamCategoryList(ddlCategory)
                ddlCategory.Items.Insert(0, "")

                ReportingLevelMaster.GetReportingLevelList(ddlReportingLevel)
                ddlReportingLevel.Items.Insert(0, "")

                BindUserSites()

                LoadResponsibleUserDDL()

                LoadAnomalyResponsibleUserDDL()

                AreaMaster.GetAreaMasterList(ddlArea, SessionManager.WorkingSiteID)
                ddlArea.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - Error Loading DropDowns", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindUserSites()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim objItem As ListItem = Nothing
                Dim iUserSiteID As Integer = UserMaster.GetUserSite(SessionManager.UserID)

                SiteMaster.SelectSiteMasterList(ddlUserSite)
                If SessionManager.WorkingSiteID > 0 Then
                    objItem = ddlUserSite.Items.FindByValue(SessionManager.WorkingSiteID)
                Else
                    objItem = ddlUserSite.Items.FindByValue(iUserSiteID)
                End If
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                Else
                    If ddlUserSite.Items.Count > 0 Then
                        ddlUserSite.Items(0).Selected = True
                    End If
                End If

                SiteMaster.SelectSiteMasterList(ddlAnomalyUserSite)
                If SessionManager.WorkingSiteID > 0 Then
                    objItem = ddlAnomalyUserSite.Items.FindByValue(SessionManager.WorkingSiteID)
                Else
                    objItem = ddlAnomalyUserSite.Items.FindByValue(iUserSiteID)
                End If
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                Else
                    If ddlAnomalyUserSite.Items.Count > 0 Then
                        ddlAnomalyUserSite.Items(0).Selected = True
                    End If
                End If

                SiteMaster.SelectSiteMasterList(ddlPrimaryKPISite)
                If SessionManager.WorkingSiteID > 0 Then
                    objItem = ddlPrimaryKPISite.Items.FindByValue(SessionManager.WorkingSiteID)
                Else
                    objItem = ddlPrimaryKPISite.Items.FindByValue(iUserSiteID)
                End If
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                Else
                    If ddlPrimaryKPISite.Items.Count > 0 Then
                        ddlPrimaryKPISite.Items(0).Selected = True
                    End If
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindUserSites", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub LoadResponsibleUserDDL()
            Try
                ddlResponsibleUser.Items.Clear()

                If ddlUserSite.SelectedItem IsNot Nothing Then
                    UserMaster.SelectUserNameList(ddlUserSite.SelectedItem.Value, True, ddlResponsibleUser)
                Else
                    UserMaster.SelectUserNameList(SessionManager.WorkingSiteID, True, ddlResponsibleUser)
                End If

                ddlResponsibleUser.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadResponsibleUserDDL", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub LoadAnomalyResponsibleUserDDL()
            Try
                ddlAnomalyResponsibleUser.Items.Clear()

                If ddlAnomalyUserSite.SelectedItem IsNot Nothing Then
                    UserMaster.SelectUserNameList(ddlAnomalyUserSite.SelectedItem.Value, True, ddlAnomalyResponsibleUser)
                Else
                    UserMaster.SelectUserNameList(SessionManager.WorkingSiteID, True, ddlAnomalyResponsibleUser)
                End If

                ddlAnomalyResponsibleUser.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadResponsibleUserDDL", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub LoadPrimaryKPIDDL()
            ddlPrimaryKPI.Items.Clear()

            If ddlPrimaryKPISite.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlPrimaryKPISite.SelectedItem.Value) Then
                KPIMaster.GetPrimaryKPISelectionList(ddlPrimaryKPI, SessionManager.UserID, ddlPrimaryKPISite.SelectedItem.Value)
                ddlPrimaryKPI.Items.Insert(0, "")
            End If
        End Sub
        Private Sub LoadAreaMasterDDL()
            ddlArea.Items.Clear()

            If ddlSite.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlSite.SelectedItem.Value) Then
                AreaMaster.GetAreaMasterList(ddlArea, ddlSite.SelectedItem.Value)
                ddlArea.Items.Insert(0, "")
            End If
        End Sub
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

            If SessionManager.RecordTransactionCurrentValues IsNot Nothing Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RecordTransactionCurrentValues)
            End If

            Dim objDT As DataTable = KPIMaster.SelectKPIMasterByID(SessionManager.SelectedValueKPIID)
            If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                Dim dtRow As DataRow = objDT.Rows(0)
                Dim objItem As ListItem

                txtKPI.Text = dtRow("KPI").ToString
                txtKPIOther.Text = dtRow("KPIOther").ToString
                txtExpandDescription.Text = dtRow("Description").ToString
                txtSortSequence.Text = dtRow("SortSequence").ToString
                objItem = ddlSite.Items.FindByValue(dtRow("SiteID").ToString)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                    txtSite.Text = objItem.Text
                Else
                    Dim dtSite As DataTable = SiteMaster.GetSiteMasterBySite(dtRow("SiteID").ToString)
                    If dtSite IsNot Nothing AndAlso dtSite.Rows.Count = 1 Then
                        Dim drSite As DataRow = dtSite.Rows(0)
                        objItem = New ListItem(drSite("SiteAbbrev").ToString & " - " & drSite("Site").ToString, drSite("SiteID").ToString)
                        ddlSite.Items.Add(objItem)
                        objItem.Selected = True
                        txtSite.Text = objItem.Text
                    End If
                End If
                If ddlSite.SelectedItem IsNot Nothing Then
                    LoadPrimaryKPIDDL()
                    LoadAreaMasterDDL()
                End If

                objItem = ddlPillar.Items.FindByValue(dtRow("PillarAbbrev").ToString)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                    txtPillar.Text = objItem.Text
                End If

                objItem = ddlBusinessArea.Items.FindByValue(dtRow("BusinessAreaID").ToString)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                    txtBusinessArea.Text = objItem.Text
                End If
                objItem = ddlBusinessUnit.Items.FindByValue(dtRow("BusinessUnitID").ToString)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                    txtBusinessUnit.Text = objItem.Text
                End If

                objItem = ddlCategory.Items.FindByValue(dtRow("TeamCategoryID").ToString)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                    txtCategory.Text = objItem.Text
                End If

                objItem = ddlReportingLevel.Items.FindByValue(dtRow("ReportingLevelID").ToString)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                    txtReportingLevel.Text = objItem.Text
                End If

                txtUOM.Text = dtRow("UOM").ToString

                objItem = ddlArea.Items.FindByValue(dtRow("AreaID").ToString)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                    txtArea.Text = objItem.Text
                End If

                txtSummaryType.Text = dtRow("SummaryType").ToString
                objItem = ddlResponsibleUser.Items.FindByValue(dtRow("ResponsibleUserID").ToString)
                If objItem Is Nothing AndAlso dtRow("ResponsibleUserID").ToString.Trim.Length > 0 Then
                    objItem = New ListItem
                    objItem.Value = dtRow("ResponsibleUserID").ToString
                    Dim strHolder As String = UserMaster.GetUserFullNameLastNameFirst(dtRow("ResponsibleUserID").ToString)
                    If strHolder.Trim.Length > 0 Then
                        strHolder += " (" & dtRow("ResponsibleUserID").ToString & ")"
                        objItem.Text = strHolder
                    Else
                        objItem.Text = dtRow("ResponsibleUserID").ToString
                    End If
                    objItem.Selected = True
                    txtResponsibleUser.Text = objItem.Text
                    ddlResponsibleUser.Items.Insert(0, objItem)
                ElseIf objItem IsNot Nothing Then
                    objItem.Selected = True
                    txtResponsibleUser.Text = objItem.Text
                End If
                ckTargetUp.Checked = Convert.ToBoolean(dtRow("TargetUp"))
                ckInterface.Checked = Convert.ToBoolean(dtRow("Interface"))
                txtExpandFormula.Text = dtRow("InterfaceFormula").ToString.Trim
                txtScheduleCode.Text = dtRow("ScheduleCode").ToString.Trim
                txtScheduleTime.Text = dtRow("ScheduleTime").ToString.Trim
                If IsDate(dtRow("NextExecution").ToString) Then
                    txtNextExecution.Text = Convert.ToDateTime(dtRow("NextExecution").ToString).ToString("yyyy/MM/dd HH:mm:ss")
                Else
                    txtNextExecution.Text = dtRow("NextExecution").ToString.Trim
                End If
                If IsDate(dtRow("LastExecution").ToString) Then
                    txtLastExecution.Text = Convert.ToDateTime(dtRow("LastExecution").ToString.Trim).ToString("yyyy/MM/dd HH:mm:ss")
                Else
                    txtLastExecution.Text = dtRow("LastExecution").ToString.Trim
                End If
                ckLastSuccessful.Checked = dtRow("LastExecutionSuccessful")
                If IsDate(dtRow("OnDemandExecute").ToString) Then
                    txtOnDemandExecute.Text = Convert.ToDateTime(dtRow("OnDemandExecute").ToString.Trim).ToString("yyyy/MM/dd HH:mm:ss")
                Else
                    txtOnDemandExecute.Text = dtRow("OnDemandExecute").ToString
                End If
                ckNoNotifications.Checked = Convert.ToBoolean(dtRow("SupressEmailNotification"))
                ckActive.Checked = Convert.ToBoolean(dtRow("Active"))

                objItem = ddlPrimaryKPI.Items.FindByValue(dtRow("PrimaryKPIID").ToString)
                If objItem Is Nothing AndAlso IsNothing(dtRow("PrimaryKPIID").ToString) Then
                    Dim dtKPI As DataTable = KPIMaster.SelectKPIMasterByID(dtRow("PrimaryKPIID").ToString)
                    If dtKPI IsNot Nothing AndAlso dtKPI.Rows.Count = 1 Then
                        objItem = New ListItem
                        objItem.Value = dtRow("PrimaryKPIID").ToString
                        objItem.Text = dtRow("KPI").ToString
                        objItem.Selected = True
                        txtPrimaryKPI.Text = objItem.Text
                    End If
                ElseIf objItem IsNot Nothing Then
                    objItem.Selected = True
                    txtPrimaryKPI.Text = objItem.Text
                End If
                ckAutoMonth.Checked = Convert.ToBoolean(dtRow("AutoGenerateAnomalyMonth").ToString)
                ckAutoYTD.Checked = Convert.ToBoolean(dtRow("AutoGenerateAnomalyYTD").ToString)
                objItem = ddlAnomalyResponsibleUser.Items.FindByValue(dtRow("AnomalyResponsibleUserID").ToString)
                If objItem Is Nothing AndAlso dtRow("AnomalyResponsibleUserID").ToString.Trim.Length > 0 Then
                    objItem = New ListItem
                    objItem.Value = dtRow("AnomalyResponsibleUserID").ToString
                    Dim strHolder As String = UserMaster.GetUserFullNameLastNameFirst(dtRow("AnomalyResponsibleUserID").ToString)
                    If strHolder.Trim.Length > 0 Then
                        strHolder += " (" & dtRow("AnomalyResponsibleUserID").ToString & ")"
                        objItem.Text = strHolder
                    Else
                        objItem.Text = dtRow("AnomalyResponsibleUserID").ToString
                    End If
                    objItem.Selected = True
                    ddlAnomalyResponsibleUser.Items.Insert(0, objItem)
                    txtAnomalyResponsibleUser.Text = objItem.Text
                ElseIf objItem IsNot Nothing Then
                    objItem.Selected = True
                    txtAnomalyResponsibleUser.Text = objItem.Text
                End If
                ckDailyKPI.Checked = Convert.ToBoolean(dtRow("DailyKPI"))
                ckDailyInterface.Checked = Convert.ToBoolean(dtRow("DailyInterface"))
                ckDailyCompare.Checked = Convert.ToBoolean(dtRow("DailyKPICompare"))
                txtElement.Text = "[KPI" & SessionManager.SelectedValueKPIID.ToString("00000") & "]"

                TransactionHistory1.TableName = DBTableName
                TransactionHistory1.RecordID = SessionManager.SelectedValueKPIID.ToString

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("KPI", txtKPI.Text.Trim())
                objDic.Add("KPIEnglish", txtKPIOther.Text.Trim)
                objDic.Add("Description", txtExpandDescription.Text.Trim)
                objDic.Add("UOM", txtUOM.Text.Trim())
                objDic.Add("TargetUp", ckTargetUp.Checked.ToString)
                objDic.Add("Site", ddlSite.SelectedItem.Text.Trim())
                objDic.Add("TeamCategory", txtCategory.Text.Trim())
                objDic.Add("SortSequence", txtSortSequence.Text.Trim())
                objDic.Add("Pillar", txtPillar.Text.Trim())
                objDic.Add("BusinessArea", txtBusinessArea.Text.Trim())
                objDic.Add("BusinessUnit", txtBusinessUnit.Text.Trim())
                objDic.Add("ReportingLevel", txtReportingLevel.Text.Trim)
                objDic.Add("SummaryType", txtSummaryType.Text.Trim())
                objDic.Add("ResponsibleUserID", txtResponsibleUser.Text.Trim())
                objDic.Add("Area", txtArea.Text.Trim())
                objDic.Add("Interface", ckInterface.Checked.ToString)
                objDic.Add("Formula", txtExpandFormula.Text.Trim)
                objDic.Add("ScheduleCode", txtScheduleCode.Text.Trim)
                objDic.Add("ScheduleTime", txtScheduleTime.Text.Trim)
                objDic.Add("OnDemandExecute", txtOnDemandExecute.Text.Trim)
                objDic.Add("NoNotifications", ckNoNotifications.Checked.ToString)
                objDic.Add("Active", ckActive.Checked.ToString)
                objDic.Add("PrimaryKPI", txtPrimaryKPI.Text.Trim)
                objDic.Add("AutoAnomalyMonth", ckAutoMonth.Checked.ToString)
                objDic.Add("AutoAnomalyYTD", ckAutoYTD.Checked.ToString)
                objDic.Add("AnomalyResponsibleUser", txtAnomalyResponsibleUser.Text.Trim)
                objDic.Add("DailyKPI", ckDailyKPI.Checked.ToString)
                objDic.Add("DailyInterface", ckDailyInterface.Checked.ToString)
                objDic.Add("CompareDaily", ckDailyCompare.Checked.ToString)

                SessionManager.RecordTransactionCurrentValues = objDic

                mcKPITeams.DataBind(True)
                mcKPINotifications.DataBind(True)
                mcKPIDataElements.DataBind(True)
            End If
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

            Select Case SessionManager.KPIMasterMode.ToString()
                Case "ViewRow", "DeleteRow"
                    txtKPI.ReadOnly = True
                    txtKPI.CssClass = "Textbox_Display"
                    txtKPIOther.ReadOnly = True
                    txtKPIOther.CssClass = "Textbox_Display"
                    txtExpandDescription.ReadOnly = True
                    txtExpandDescription.CssClass = "Textbox_Display"
                    txtSortSequence.ReadOnly = True
                    txtSortSequence.CssClass = "Textbox_Display"
                    ddlSite.Visible = False
                    txtSite.Visible = True
                    ddlPillar.Visible = False
                    txtPillar.Visible = True
                    ddlBusinessArea.Visible = False
                    txtBusinessArea.Visible = True
                    ddlBusinessUnit.Visible = False
                    txtBusinessUnit.Visible = True
                    ddlCategory.Visible = False
                    txtCategory.Visible = True
                    ddlReportingLevel.Visible = False
                    txtReportingLevel.Visible = True
                    txtUOM.ReadOnly = True
                    txtUOM.CssClass = "Textbox_Display"
                    ddlArea.Visible = False
                    txtArea.Visible = True
                    txtSummaryType.ReadOnly = True
                    txtSummaryType.CssClass = "Textbox_Display"
                    ddlResponsibleUser.Visible = False
                    txtResponsibleUser.Visible = True
                    ddlUserSite.Visible = False
                    ckTargetUp.Enabled = False
                    ckInterface.Enabled = False
                    ckNoNotifications.Enabled = False
                    txtExpandFormula.ReadOnly = True
                    txtExpandFormula.CssClass = "Textbox_Display"
                    txtScheduleCode.ReadOnly = True
                    txtScheduleCode.CssClass = "Textbox_Display"
                    txtScheduleTime.ReadOnly = True
                    txtScheduleTime.CssClass = "Textbox_Display"
                    txtOnDemandExecute.ReadOnly = True
                    txtOnDemandExecute.CssClass = "Textbox_Display"
                    ckActive.Enabled = False
                    ddlPrimaryKPI.Visible = False
                    txtPrimaryKPI.Visible = True
                    ddlPrimaryKPISite.Visible = False
                    ckAutoMonth.Enabled = False
                    ckAutoYTD.Enabled = False
                    ddlAnomalyResponsibleUser.Visible = False
                    txtAnomalyResponsibleUser.Visible = True
                    ddlAnomalyUserSite.Visible = False
                    ckDailyKPI.Enabled = False
                    ckDailyInterface.Enabled = False
                    ckDailyCompare.Enabled = False
                Case "AddRow", "EditRow"
                    ddlSite.Visible = False
                    txtSite.Visible = True
            End Select
        End Sub
        Private Function InsertKPIMaster() As Boolean
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
                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                Dim iBusinessAreaID As Integer = 0
                Dim iBusinessUnitID As Integer = 0
                Dim iPrimaryKPIID As Integer = 0
                Dim strAnomolyResponsibleUserID As String = ""
                If ddlBusinessArea.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlBusinessArea.SelectedItem.Value) Then
                    iBusinessAreaID = ddlBusinessArea.SelectedItem.Value
                End If
                If ddlBusinessUnit.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlBusinessUnit.SelectedItem.Value) Then
                    iBusinessUnitID = ddlBusinessUnit.SelectedItem.Value
                End If
                If ddlPrimaryKPI.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlPrimaryKPI.SelectedItem.Value) Then
                    iPrimaryKPIID = ddlPrimaryKPI.SelectedItem.Value

                    If ckActive.Checked AndAlso Not IsPrimaryKPIActive(iPrimaryKPIID) Then
                        Master.DisplayError("Primary KPI is InActive, unable to set current KPI to Active")
                        Return False
                    End If
                End If
                If ddlAnomalyResponsibleUser.SelectedItem IsNot Nothing AndAlso ddlAnomalyResponsibleUser.SelectedItem.Value.ToString.Trim.Length > 0 Then
                    strAnomolyResponsibleUserID = ddlAnomalyResponsibleUser.SelectedItem.Value.ToString.Trim
                End If

                If ckInterface.Checked Or ckDailyInterface.Checked Then
                    If txtExpandFormula.Text.Trim.Length = 0 OrElse (txtScheduleCode.Text.Trim.Length = 0 AndAlso txtOnDemandExecute.Text.Trim.Length = 0) Then
                        Master.DisplayError("Formula and Schedule are required if KPI is set to Interface or Daily Interface")
                        Return False
                    End If
                End If

                If ckDailyInterface.Checked OrElse ckDailyCompare.Checked Then
                    ckDailyKPI.Checked = True
                End If

                Dim strVariables As String = ""
                If Not ValidateFormula(txtExpandFormula.Text.Trim, strVariables) Then
                    Return False
                End If

                If Not ValidateScheduleInfo() Then
                    Return False
                End If
                CalculateNextExecution()
                Dim strNextExecuteTime As String = RegionalConversion.FormatSQLDate(txtNextExecution.Text.Trim, True)
                Dim strOnDemandExecuteTime As String = RegionalConversion.FormatSQLDate(txtOnDemandExecute.Text.Trim, True)

                Dim iRecordID As Integer = KPIMaster.AddKPIMaster(txtKPI.Text.Trim, txtKPIOther.Text.Trim, txtExpandDescription.Text.Trim, CInt(txtSortSequence.Text), ddlSite.SelectedItem.Value, ddlPillar.SelectedItem.Value, iBusinessAreaID, iBusinessUnitID, CInt(ddlCategory.SelectedItem.Value), txtUOM.Text.Trim, CInt(ddlArea.SelectedItem.Value), txtSummaryType.Text.Trim.ToUpper, Convert.ToInt16(ddlReportingLevel.SelectedItem.Value), ddlResponsibleUser.SelectedItem.Value, ckTargetUp.Checked, ckInterface.Checked, txtExpandFormula.Text.Trim, strVariables, txtScheduleCode.Text, txtScheduleTime.Text, strNextExecuteTime, strOnDemandExecuteTime, ckNoNotifications.Checked, ckActive.Checked, iPrimaryKPIID, ckAutoMonth.Checked, ckAutoYTD.Checked, strAnomolyResponsibleUserID.Trim, ckDailyKPI.Checked, ckDailyInterface.Checked, ckDailyCompare.Checked)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, iRecordID.ToString, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertKPIMaster", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateKPIMaster() As Boolean
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
                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.CompareDictionaryValues(SessionManager.RecordTransactionCurrentValues, objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                If IsKPIPrimary() Then
                    If ddlPrimaryKPI.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlPrimaryKPI.SelectedItem.Value) Then
                        Master.DisplayError("Current KPI has supporting KPIs, unable to set the Primary KPI")
                        Return False
                    End If

                    If Not ckActive.Checked AndAlso CheckSupportingKPIs() Then
                        Master.DisplayError("All Supporting KPIs must be set to InActive before you can set this Primary KPI to Inactive")
                        Return False
                    End If
                End If

                Dim iBusinessAreaID As Integer = 0
                Dim iBusinessUnitID As Integer = 0
                Dim iPrimaryKPIID As Integer = 0
                Dim strAnomolyResponsibleUserID As String = ""
                If ddlBusinessArea.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlBusinessArea.SelectedItem.Value) Then
                    iBusinessAreaID = ddlBusinessArea.SelectedItem.Value
                End If
                If ddlBusinessUnit.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlBusinessUnit.SelectedItem.Value) Then
                    iBusinessUnitID = ddlBusinessUnit.SelectedItem.Value
                End If
                If ddlPrimaryKPI.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlPrimaryKPI.SelectedItem.Value) Then
                    iPrimaryKPIID = ddlPrimaryKPI.SelectedItem.Value

                    If iPrimaryKPIID = SessionManager.SelectedValueKPIID Then
                        Master.DisplayError("Primary KPI can not be set to the current KPI")
                        Return False
                    ElseIf ckActive.Checked AndAlso Not IsPrimaryKPIActive(iPrimaryKPIID) Then
                        Master.DisplayError("Primary KPI is InActive, unable to set current KPI to Active")
                        Return False
                    End If
                End If

                If ddlAnomalyResponsibleUser.SelectedItem IsNot Nothing AndAlso ddlAnomalyResponsibleUser.SelectedItem.Value.ToString.Trim.Length > 0 Then
                    strAnomolyResponsibleUserID = ddlAnomalyResponsibleUser.SelectedItem.Value.ToString.Trim
                End If

                If ckInterface.Checked Or ckDailyInterface.Checked Then
                    If txtExpandFormula.Text.Trim.Length = 0 OrElse (txtScheduleCode.Text.Trim.Length = 0 AndAlso txtOnDemandExecute.Text.Trim.Length = 0) Then
                        Master.DisplayError("Formula and Schedule are required if KPI is set to Interface or Daily Interface")
                        Return False
                    End If
                End If

                If ckDailyInterface.Checked OrElse ckDailyCompare.Checked Then
                    ckDailyKPI.Checked = True
                End If

                Dim strVariables As String = ""
                If Not ValidateFormula(txtExpandFormula.Text.Trim, strVariables) Then
                    Return False
                End If

                If Not ValidateScheduleInfo() Then
                    Return False
                End If
                CalculateNextExecution()
                Dim strNextExecuteTime As String = RegionalConversion.FormatSQLDate(txtNextExecution.Text.Trim, True)
                Dim strOnDemandExecuteTime As String = RegionalConversion.FormatSQLDate(txtOnDemandExecute.Text.Trim, True)

                KPIMaster.UpdateKPIMaster(SessionManager.SelectedValueKPIID, txtKPI.Text.Trim, txtKPIOther.Text.Trim, txtExpandDescription.Text.Trim, CInt(txtSortSequence.Text), ddlSite.SelectedItem.Value, ddlPillar.SelectedItem.Value, iBusinessAreaID, iBusinessUnitID, CInt(ddlCategory.SelectedItem.Value), txtUOM.Text.Trim, CInt(ddlArea.SelectedItem.Value), txtSummaryType.Text.Trim.ToUpper, Convert.ToInt16(ddlReportingLevel.SelectedItem.Value), ddlResponsibleUser.SelectedItem.Value, ckTargetUp.Checked, ckInterface.Checked, txtExpandFormula.Text.Trim, strVariables, txtScheduleCode.Text.Trim, txtScheduleTime.Text.Trim, strNextExecuteTime, strOnDemandExecuteTime, ckNoNotifications.Checked, ckActive.Checked, iPrimaryKPIID, ckAutoMonth.Checked, ckAutoYTD.Checked, strAnomolyResponsibleUserID, ckDailyKPI.Checked, ckDailyInterface.Checked, ckDailyCompare.Checked)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueKPIID.ToString, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateKPIMaster", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function DeleteKPIMaster() As Boolean
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
                KPIMaster.DeleteKPIMaster(SessionManager.SelectedValueKPIID)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueKPIID.ToString, "KPI Deleted", SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteKPIMaster", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
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
            objDic.Add("KPI", txtKPI.Text.Trim())
            objDic.Add("KPIEnglish", txtKPIOther.Text.Trim)
            objDic.Add("Description", txtExpandDescription.Text.Trim)
            objDic.Add("UOM", txtUOM.Text.Trim())
            objDic.Add("TargetUp", ckTargetUp.Checked)
            objDic.Add("Site", ddlSite.SelectedItem.Text.Trim())
            If ddlCategory.SelectedItem IsNot Nothing AndAlso ddlCategory.SelectedItem.Text.Trim.Length > 0 Then
                objDic.Add("TeamCategory", ddlCategory.SelectedItem.Text.Trim())
            Else
                objDic.Add("TeamCategory", "")
            End If
            objDic.Add("SortSequence", txtSortSequence.Text.Trim())
            If ddlPillar.SelectedItem IsNot Nothing AndAlso ddlPillar.SelectedItem.Text.Trim.Length > 0 Then
                objDic.Add("Pillar", ddlPillar.SelectedItem.Text.Trim())
            Else
                objDic.Add("Pillar", "")
            End If
            If ddlBusinessArea.SelectedItem IsNot Nothing AndAlso ddlBusinessArea.SelectedItem.Text.Trim.Length > 0 Then
                objDic.Add("BusinessArea", ddlBusinessArea.SelectedItem.Text.Trim())
            Else
                objDic.Add("BusinessArea", "")
            End If
            If ddlBusinessUnit.SelectedItem IsNot Nothing AndAlso ddlBusinessUnit.SelectedItem.Text.Trim.Length > 0 Then
                objDic.Add("BusinessUnit", ddlBusinessUnit.SelectedItem.Text.Trim())
            Else
                objDic.Add("BusinessUnit", "")
            End If
            If ddlReportingLevel.SelectedItem IsNot Nothing AndAlso ddlReportingLevel.SelectedItem.Text.Trim.Length > 0 Then
                objDic.Add("ReportingLevel", ddlReportingLevel.SelectedItem.Text.Trim())
            Else
                objDic.Add("ReportingLevel", "")
            End If
            objDic.Add("SummaryType", txtSummaryType.Text.Trim())
            If ddlResponsibleUser.SelectedItem IsNot Nothing AndAlso ddlResponsibleUser.SelectedItem.Text.Trim.Length > 0 Then
                objDic.Add("ResponsibleUserID", ddlResponsibleUser.SelectedItem.Text.Trim())
            Else
                objDic.Add("ResponsibleUserID", "")
            End If
            If ddlArea.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlArea.SelectedItem.Value) Then
                objDic.Add("Area", ddlArea.SelectedItem.Text.Trim)
            Else
                objDic.Add("Area", "")
            End If
            objDic.Add("Interface", ckInterface.Checked.ToString)
            objDic.Add("Formula", txtExpandFormula.Text.Trim)
            objDic.Add("ScheduleCode", txtScheduleCode.Text.Trim)
            objDic.Add("ScheduleTime", txtScheduleTime.Text.Trim)
            objDic.Add("OnDemandExecute", txtOnDemandExecute.Text.Trim)
            objDic.Add("NoNotifications", ckNoNotifications.Checked.ToString)
            objDic.Add("Active", ckActive.Checked.ToString)
            If ddlPrimaryKPI.SelectedItem IsNot Nothing AndAlso ddlPrimaryKPI.SelectedItem.Text.Trim.Length > 0 Then
                objDic.Add("PrimaryKPI", ddlPrimaryKPI.SelectedItem.Text.Trim)
            Else
                objDic.Add("PrimaryKPI", "")
            End If
            objDic.Add("AutoAnomalyMonth", ckAutoMonth.Checked.ToString)
            objDic.Add("AutoAnomalyYTD", ckAutoYTD.Checked.ToString)
            If ddlAnomalyResponsibleUser.SelectedItem IsNot Nothing AndAlso ddlAnomalyResponsibleUser.SelectedItem.Text.Trim.Length > 0 Then
                objDic.Add("AnomalyResponsibleUser", ddlAnomalyResponsibleUser.SelectedItem.Text.Trim)
            Else
                objDic.Add("AnomalyResponsibleUser", "")
            End If
            objDic.Add("DailyKPI", ckDailyKPI.Checked.ToString)
            objDic.Add("DailyInterface", ckDailyInterface.Checked.ToString)
            objDic.Add("CompareDaily", ckDailyCompare.Checked.ToString)

            Return objDic
        End Function
        Private Function ValidateFormula(ByVal passFormula As String, ByRef passVariables As String) As Boolean
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
                Dim strCheckFormula As String = ""
                Dim strVariables As String = ""
                Dim strVariableHolder As String = ""
                Dim iElementCount As Integer = 1

                ' Validate Variables
                strCheckFormula = passFormula.Trim

                ' If we have a KPI element, verify that Daily KPI is not checked
                If strCheckFormula.Contains("[KPI") AndAlso (ckDailyInterface.Checked) Then
                    Master.DisplayError("KPI Data Elements not allowed for Daily Interface KPI")
                    Return False
                End If

                ' If we have a Tracker element, verify that Daily KPI is not checked
                If strCheckFormula.Contains("[TRACKER") AndAlso (ckDailyInterface.Checked) Then
                    Master.DisplayError("Savings Tracker Data Elements not allowed for Daily Interface KPI")
                    Return False
                End If

                ' If we have an FX element, verify that Daily KPI is not checked
                If strCheckFormula.Contains("[FX_") AndAlso (ckDailyInterface.Checked) Then
                    Master.DisplayError("Currenty Exchange Data Elements not allowed for Daily Interface KPI")
                    Return False
                End If

                If strCheckFormula.Contains("[") Then
                    Do Until Not strCheckFormula.Contains("[")
                        If strCheckFormula.Contains("]") Then
                            strVariableHolder = strCheckFormula.Substring(strCheckFormula.IndexOf("["), strCheckFormula.IndexOf("]") - strCheckFormula.IndexOf("[") + 1)

                            iElementCount = StringCount(strCheckFormula, strVariableHolder)
                            For i As Integer = 1 To iElementCount
                                If strVariables.Trim.Length > 0 Then strVariables += ","
                                strVariables += strVariableHolder.Replace("[", "").Replace("]", "")
                            Next

                            strCheckFormula = strCheckFormula.Replace(strVariableHolder, "")
                        Else
                            Master.DisplayError("Mismatched brackets detected []")
                            Return False
                        End If
                    Loop

                    If strVariables.Trim.Length > 0 Then
                        Dim iVariables As Integer = strVariables.Split(",").Length
                        Dim iValidVariables As Integer = 0
                        Dim objDT As DataTable = InterfaceDataElements.SelectValidateDataElements(strVariables)

                        If objDT IsNot Nothing Then
                            iValidVariables = objDT.Rows.Count

                            If ckDailyInterface.Checked Then
                                For Each dtRow As DataRow In objDT.Rows
                                    If Not Convert.ToBoolean(dtRow("DailyValid")) Then
                                        Master.DisplayError("Only Daily Data Elements are allowed for Daily Interface KPI")
                                        Return False
                                    End If
                                Next
                            End If
                        End If

                        If iVariables <> iValidVariables Then
                            Master.DisplayError("Invalid Data Elements used in formula")
                            Return False
                        End If
                    End If
                End If

                ' Validate formula logic
                strCheckFormula = passFormula.Trim
                If strCheckFormula.Contains("[") Then
                    Do Until Not strCheckFormula.Contains("[")
                        If strCheckFormula.Contains("]") Then
                            strVariableHolder = strCheckFormula.Substring(strCheckFormula.IndexOf("["), strCheckFormula.IndexOf("]") - strCheckFormula.IndexOf("[") + 1)
                            strCheckFormula = strCheckFormula.Replace(strVariableHolder, "1")
                        End If
                    Loop
                End If

                If strCheckFormula.Contains("{") Then
                    Do Until Not strCheckFormula.Contains("{")
                        If strCheckFormula.Contains("}") Then
                            strVariableHolder = strCheckFormula.Substring(strCheckFormula.IndexOf("{"), strCheckFormula.IndexOf("}") - strCheckFormula.IndexOf("{") + 1)
                            strCheckFormula = strCheckFormula.Replace(strVariableHolder, "1")
                        End If
                    Loop
                End If

                Dim dValue As Double = 0

                If strCheckFormula.Trim.Length > 0 Then
                    Try
                        dValue = WebApp.APlus.UI.CustomControls.Evaluator.EvaluateToDouble(strCheckFormula)
                    Catch ex As Exception
                        Master.DisplayError("Formula does not evaluate to a number:<br />" & strCheckFormula)
                        Return False
                    End Try
                End If

                passVariables = strVariables
                Return True
            Catch ex As Exception
                Return False
            End Try
        End Function
        Private Function StringCount(ByVal sInputStr As String, ByVal sSrchString As String) As Integer
            Dim iStrPos As Integer, iStrCount As Integer
            Do
                iStrPos = sInputStr.IndexOf(sSrchString, iStrPos)
                If iStrPos <> -1 Then
                    iStrCount += 1
                    iStrPos += sSrchString.Length
                End If
            Loop Until iStrPos = -1
            Return iStrCount
        End Function
        Private Function ValidateScheduleInfo() As Boolean
            Try
                If txtScheduleCode.Text.Trim.Length = 0 Then
                    Return True
                End If

                Dim strScheduleCode As String = txtScheduleCode.Text.Trim

                If Not RegularExpressions.Regex.IsMatch(strScheduleCode, TaskScheduler.GetScheduleRegularExpression, RegexOptions.IgnoreCase) Then
                    Master.DisplayError("Invalid Schedule Code")
                    txtScheduleCode.Focus()
                    Return False
                End If

                If txtScheduleTime.Text.Trim.Length > 0 Then
                    If txtScheduleTime.Text.Replace(":", "").Trim.Length <> 4 OrElse Not IsNumeric(txtScheduleTime.Text.Replace(":", "")) OrElse _
                    CInt(txtScheduleTime.Text.Replace(":", "")) < 0 OrElse CInt(txtScheduleTime.Text.Replace(":", "")) > 2400 Then
                        Master.DisplayError("Invalid Schedule Time")
                        txtScheduleTime.Focus()
                        Return False
                    End If
                End If

                If txtOnDemandExecute.Text.Trim.Length > 0 Then
                    If Not IsDate(txtOnDemandExecute.Text.Trim) OrElse txtOnDemandExecute.Text.Trim.Length < 16 Then
                        Master.DisplayError("Invalid OnDemand Date/Time")
                        txtScheduleTime.Focus()
                        Return False
                    End If
                End If
            Catch ex As Exception
                Master.DisplayErrors(ProgramName & " - ValidateScheduleInfo", ex, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
            End Try

            Return True
        End Function
        Private Sub CalculateNextExecution()
            Try
                If txtScheduleCode.Text.Trim.Length = 0 Then
                    txtNextExecution.Text = ""
                Else
                    txtNextExecution.Text = TaskScheduler.CalculateNextExecution(txtScheduleCode.Text.Trim, txtScheduleTime.Text.Replace(":", "").Trim)
                End If
            Catch ex As Exception
                Master.DisplayErrors(ProgramName & " - CalculateNextExecution", ex, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
            End Try
        End Sub
        Private Function IsKPIPrimary() As Boolean
            ' Returns TRUE if there are ANY supporting KPIs
            Dim bReturn As Boolean = False

            Try
                Dim objDT As DataTable = KPIMaster.SelectSupportingKPIsByKPIID(SessionManager.SelectedValueKPIID)
                If objDT IsNot Nothing AndAlso objDT.Rows.Count > 0 Then
                    bReturn = True
                End If
            Catch ex As Exception
                Master.DisplayErrors(ProgramName & " - CheckSupportingKPIs", ex, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
            End Try

            Return bReturn
        End Function
        Private Function CheckSupportingKPIs() As Boolean
            ' Returns TRUE if there are ANY supporting KPIs that have the Active flag set to true
            Dim bReturn As Boolean = False

            Try
                Dim objDT As DataTable = KPIMaster.SelectSupportingKPIsByKPIID(SessionManager.SelectedValueKPIID)
                If objDT IsNot Nothing AndAlso objDT.Rows.Count > 0 Then
                    For Each dtRow As DataRow In objDT.Rows
                        If Convert.ToBoolean(dtRow("Active")) Then
                            bReturn = True
                            Exit For
                        End If
                    Next
                End If
            Catch ex As Exception
                Master.DisplayErrors(ProgramName & " - CheckSupportingKPIs", ex, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
            End Try

            Return bReturn
        End Function
        Private Function IsPrimaryKPIActive(ByVal passPrimaryKPIID As Integer) As Boolean
            Dim bReturn As Boolean = False

            Try
                Dim objDT As DataTable = KPIMaster.SelectKPIMasterByID(passPrimaryKPIID)
                If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                    If Convert.ToBoolean(objDT.Rows(0)("Active")) Then
                        bReturn = True
                    End If
                End If
            Catch ex As Exception
                Master.DisplayErrors(ProgramName & " - IsPrimaryKPIActive", ex, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
            End Try

            Return bReturn
        End Function
#End Region

    End Class
End Namespace
