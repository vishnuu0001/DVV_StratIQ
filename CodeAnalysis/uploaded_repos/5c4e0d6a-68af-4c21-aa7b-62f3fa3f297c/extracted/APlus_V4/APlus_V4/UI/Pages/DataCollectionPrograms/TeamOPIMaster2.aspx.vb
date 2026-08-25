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
    Partial Class TeamOPIMaster2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Team OPIs"
        Private Shared ReadOnly ProgramName As String = "TeamOPIMaintenance2"
        Private Shared ReadOnly DBTableName As String = "TeamOPIMaster"
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel, btnExit}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel", "Exit"}
            Dim OutMessageArr() As String = {"", "", ""}
            Dim strDateFormat As String = SessionManager.DateFormat

            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)

            txtStartDate_CalendarExtender.Format = strDateFormat
            txtEndDate_CalendarExtender.Format = strDateFormat
            txtReportStart_CalendarExtender.Format = strDateFormat
            txtReportEnd_CalendarExtender.Format = strDateFormat

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnExit.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
        End Sub
        Private Sub LoadAddModeJavaScripts()
            Dim myTabArray() As Object = {ddlTeam, txtOPI, txtOPIShortName, txtExpandOPIDescription, ddlOPICategoryMaster, _
                                          ddlOPIUOMMaster, cbTimeEntryRequired, cbCalculateValue, txtExpandOPIFormula, _
                                          txtExpandBenefitFormula, ddlEntryType, txtOPISize, cbNegativeEntryAllowed, txtSummaryType, _
                                          txtExpandCollectionEvent, ddlCollectionInterval, _
                                          txtAttribute1, ddlAttribute1EntryType, txtAttribute1Size, ckAttribute1Default, _
                                          txtAttribute2, ddlAttribute2EntryType, txtAttribute2Size, ckAttribute2Default, _
                                          txtAttribute3, ddlAttribute3EntryType, txtAttribute3Size, ckAttribute3Default, _
                                          txtAttribute4, ddlAttribute4EntryType, txtAttribute4Size, ckAttribute4Default, _
                                          txtAttribute5, ddlAttribute5EntryType, txtAttribute5Size, ckAttribute5Default, _
                                          txtAttribute6, ddlAttribute6EntryType, txtAttribute6Size, ckAttribute6Default, _
                                          cbPrimaryOPI, cbDataCollectionOnline, ddlResponsiblePerson, txtHistoric, _
                                          txtTarget, txtStartDate, txtEndDate, txtProjectedBenefit, txtExpectedBenefit, _
                                          txtUOM, txtReportStart, txtReportingPeriods, txtReportEnd, _
                                          ddlReportingInterval, chkCustomYValues, txtChartYMin, txtChartYMax, txtChartYLines}

            Dim TabKeyDownArr() As String = {Tab(txtOPI, txtChartYLines, "No"), _
                                             Tab(txtOPIShortName, ddlTeam, "No"), _
                                             Tab(txtExpandOPIDescription, txtOPI, "No"), _
                                             Tab(ddlOPICategoryMaster, txtOPIShortName, "No"), _
                                             Tab(ddlOPIUOMMaster, txtExpandOPIDescription, "No"), _
                                             Tab(cbTimeEntryRequired, ddlOPICategoryMaster, "No"), _
                                             Tab(cbCalculateValue, ddlOPIUOMMaster, "No"), _
                                             Tab(txtExpandOPIFormula, cbTimeEntryRequired, "No"), _
                                             Tab(txtExpandBenefitFormula, cbCalculateValue, "No"), _
                                             Tab(ddlEntryType, txtExpandOPIFormula, "No"), _
                                             Tab(txtOPISize, txtExpandBenefitFormula, "No"), _
                                             Tab(cbNegativeEntryAllowed, ddlEntryType, "Yes"), _
                                             Tab(txtSummaryType, txtOPISize, "No"), _
                                             Tab(txtExpandCollectionEvent, cbNegativeEntryAllowed, "No"), _
                                             Tab(ddlCollectionInterval, txtSummaryType, "No"), _
                                             Tab(txtAttribute1, txtExpandCollectionEvent, "No"), _
                                             Tab(ddlAttribute1EntryType, ddlCollectionInterval, "No"), _
                                             Tab(txtAttribute1Size, txtAttribute1, "No"), _
                                             Tab(ckAttribute1Default, ddlAttribute1EntryType, "No"), _
                                             Tab(txtAttribute2, txtAttribute1Size, "No"), _
                                             Tab(ddlAttribute2EntryType, ckAttribute1Default, "No"), _
                                             Tab(txtAttribute2Size, txtAttribute2, "No"), _
                                             Tab(ckAttribute2Default, ddlAttribute2EntryType, "No"), _
                                             Tab(txtAttribute3, txtAttribute2Size, "No"), _
                                             Tab(ddlAttribute3EntryType, ckAttribute2Default, "No"), _
                                             Tab(txtAttribute3Size, txtAttribute3, "No"), _
                                             Tab(ckAttribute3Default, ddlAttribute3EntryType, "No"), _
                                             Tab(txtAttribute4, txtAttribute3Size, "No"), _
                                             Tab(ddlAttribute4EntryType, ckAttribute3Default, "No"), _
                                             Tab(txtAttribute4Size, txtAttribute4, "No"), _
                                             Tab(ckAttribute4Default, ddlAttribute4EntryType, "No"), _
                                             Tab(txtAttribute5, txtAttribute4Size, "No"), _
                                             Tab(ddlAttribute5EntryType, ckAttribute4Default, "No"), _
                                             Tab(txtAttribute5Size, txtAttribute5, "No"), _
                                             Tab(ckAttribute5Default, ddlAttribute5EntryType, "No"), _
                                             Tab(txtAttribute6, txtAttribute5Size, "No"), _
                                             Tab(ddlAttribute6EntryType, ckAttribute5Default, "No"), _
                                             Tab(txtAttribute6Size, txtAttribute6, "No"), _
                                             Tab(ckAttribute6Default, ddlAttribute6EntryType, "No"), _
                                             Tab(cbPrimaryOPI, txtAttribute6Size, "No"), _
                                             Tab(cbDataCollectionOnline, ckAttribute6Default, "No"), _
                                             Tab(ddlResponsiblePerson, cbPrimaryOPI, "No"), _
                                             Tab(txtHistoric, cbDataCollectionOnline, "No"), _
                                             Tab(txtTarget, ddlResponsiblePerson, "Neg"), _
                                             Tab(txtStartDate, txtHistoric, "Neg"), _
                                             Tab(txtEndDate, txtTarget, "No"), _
                                             Tab(txtProjectedBenefit, txtStartDate, "No"), _
                                             Tab(txtExpectedBenefit, txtEndDate, "Yes"), _
                                             Tab(txtUOM, txtProjectedBenefit, "Yes"), _
                                             Tab(txtReportStart, txtExpectedBenefit, "No"), _
                                             Tab(txtReportingPeriods, txtUOM, "No"), _
                                             Tab(txtReportEnd, txtReportStart, "Int"), _
                                             Tab(ddlReportingInterval, txtReportingPeriods, "No"), _
                                             Tab(chkCustomYValues, txtReportEnd, "No"), _
                                             Tab(txtChartYMin, ddlReportingInterval, "No"), _
                                             Tab(txtChartYMax, chkCustomYValues, "Neg"), _
                                             Tab(txtChartYLines, txtChartYMin, "Neg"), _
                                             Tab(ddlTeam, txtChartYMax, "Yes")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {txtOPIShortName, txtExpandOPIDescription, ddlOPICategoryMaster, _
                                          ddlOPIUOMMaster, cbTimeEntryRequired, cbCalculateValue, txtExpandOPIFormula, _
                                          txtExpandBenefitFormula, ddlEntryType, txtOPISize, cbNegativeEntryAllowed, _
                                          txtSummaryType, txtExpandCollectionEvent, ddlCollectionInterval, _
                                          txtAttribute1, ddlAttribute1EntryType, txtAttribute1Size, ckAttribute1Default, _
                                          txtAttribute2, ddlAttribute2EntryType, txtAttribute2Size, ckAttribute2Default, _
                                          txtAttribute3, ddlAttribute3EntryType, txtAttribute3Size, ckAttribute3Default, _
                                          txtAttribute4, ddlAttribute4EntryType, txtAttribute4Size, ckAttribute4Default, _
                                          txtAttribute5, ddlAttribute5EntryType, txtAttribute5Size, ckAttribute5Default, _
                                          txtAttribute6, ddlAttribute6EntryType, txtAttribute6Size, ckAttribute6Default, _
                                          cbPrimaryOPI, cbDataCollectionOnline, ddlResponsiblePerson, _
                                          txtHistoric, txtTarget, txtStartDate, txtEndDate, txtProjectedBenefit, _
                                          txtExpectedBenefit, txtUOM, txtReportStart, txtReportingPeriods, _
                                          txtReportEnd, ddlReportingInterval, chkCustomYValues, txtChartYMin, _
                                          txtChartYMax, txtChartYLines}

            Dim TabKeyDownArr() As String = {Tab(txtExpandOPIDescription, txtChartYLines, "No"), _
                                             Tab(ddlOPICategoryMaster, txtOPIShortName, "No"), _
                                             Tab(ddlOPIUOMMaster, txtExpandOPIDescription, "No"), _
                                             Tab(cbTimeEntryRequired, ddlOPICategoryMaster, "No"), _
                                             Tab(cbCalculateValue, ddlOPIUOMMaster, "No"), _
                                             Tab(txtExpandOPIFormula, cbTimeEntryRequired, "No"), _
                                             Tab(txtExpandBenefitFormula, cbCalculateValue, "No"), _
                                             Tab(ddlEntryType, txtExpandOPIFormula, "No"), _
                                             Tab(txtOPISize, txtExpandBenefitFormula, "No"), _
                                             Tab(cbNegativeEntryAllowed, ddlEntryType, "Yes"), _
                                             Tab(txtSummaryType, txtOPISize, "No"), _
                                             Tab(txtExpandCollectionEvent, cbNegativeEntryAllowed, "No"), _
                                             Tab(ddlCollectionInterval, txtSummaryType, "No"), _
                                             Tab(txtAttribute1, txtExpandCollectionEvent, "No"), _
                                             Tab(ddlAttribute1EntryType, ddlCollectionInterval, "No"), _
                                             Tab(txtAttribute1Size, txtAttribute1, "No"), _
                                             Tab(ckAttribute1Default, ddlAttribute1EntryType, "No"), _
                                             Tab(txtAttribute2, txtAttribute1Size, "No"), _
                                             Tab(ddlAttribute2EntryType, ckAttribute1Default, "No"), _
                                             Tab(txtAttribute2Size, txtAttribute2, "No"), _
                                             Tab(ckAttribute2Default, ddlAttribute2EntryType, "No"), _
                                             Tab(txtAttribute3, txtAttribute2Size, "No"), _
                                             Tab(ddlAttribute3EntryType, ckAttribute2Default, "No"), _
                                             Tab(txtAttribute3Size, txtAttribute3, "No"), _
                                             Tab(ckAttribute3Default, ddlAttribute3EntryType, "No"), _
                                             Tab(txtAttribute4, txtAttribute3Size, "No"), _
                                             Tab(ddlAttribute4EntryType, ckAttribute3Default, "No"), _
                                             Tab(txtAttribute4Size, txtAttribute4, "No"), _
                                             Tab(ckAttribute4Default, ddlAttribute4EntryType, "No"), _
                                             Tab(txtAttribute5, txtAttribute4Size, "No"), _
                                             Tab(ddlAttribute5EntryType, ckAttribute4Default, "No"), _
                                             Tab(txtAttribute5Size, txtAttribute5, "No"), _
                                             Tab(ckAttribute5Default, ddlAttribute5EntryType, "No"), _
                                             Tab(txtAttribute6, txtAttribute5Size, "No"), _
                                             Tab(ddlAttribute6EntryType, ckAttribute5Default, "No"), _
                                             Tab(txtAttribute6Size, txtAttribute6, "No"), _
                                             Tab(ckAttribute6Default, ddlAttribute6EntryType, "No"), _
                                             Tab(cbPrimaryOPI, txtAttribute6Size, "Yes"), _
                                             Tab(cbDataCollectionOnline, ckAttribute6Default, "No"), _
                                             Tab(ddlResponsiblePerson, cbPrimaryOPI, "No"), _
                                             Tab(txtHistoric, cbDataCollectionOnline, "No"), _
                                             Tab(txtTarget, ddlResponsiblePerson, "Neg"), _
                                             Tab(txtStartDate, txtHistoric, "Neg"), _
                                             Tab(txtEndDate, txtTarget, "No"), _
                                             Tab(txtProjectedBenefit, txtStartDate, "No"), _
                                             Tab(txtExpectedBenefit, txtEndDate, "Yes"), _
                                             Tab(txtUOM, txtProjectedBenefit, "Yes"), _
                                             Tab(txtReportStart, txtExpectedBenefit, "No"), _
                                             Tab(txtReportingPeriods, txtUOM, "No"), _
                                             Tab(txtReportEnd, txtReportStart, "Int"), _
                                             Tab(ddlReportingInterval, txtReportingPeriods, "No"), _
                                             Tab(chkCustomYValues, txtReportEnd, "No"), _
                                             Tab(txtChartYMin, ddlReportingInterval, "No"), _
                                             Tab(txtChartYMax, chkCustomYValues, "Neg"), _
                                             Tab(txtChartYLines, txtChartYMin, "Neg"), _
                                             Tab(txtOPIShortName, txtChartYMax, "Yes")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
        Private Sub LoadEditOPIModeJavaScripts()
            Dim myTabArray() As Object = {txtHistoric, _
                                          txtTarget, _
                                          txtStartDate, _
                                          txtEndDate, _
                                          txtProjectedBenefit, _
                                          txtExpectedBenefit, _
                                          txtUOM, _
                                          txtReportStart, _
                                          txtReportingPeriods, _
                                          txtReportEnd, _
                                          ddlReportingInterval, _
                                          chkCustomYValues, _
                                          txtChartYMin, _
                                          txtChartYMax, _
                                          txtChartYLines}
            Dim TabKeyDownArr() As String = {Tab(txtTarget, txtChartYLines, "Neg"), _
                                             Tab(txtStartDate, txtHistoric, "Neg"), _
                                             Tab(txtEndDate, txtTarget, "No"), _
                                             Tab(txtProjectedBenefit, txtStartDate, "No"), _
                                             Tab(txtExpectedBenefit, txtEndDate, "Yes"), _
                                             Tab(txtUOM, txtProjectedBenefit, "Yes"), _
                                             Tab(txtReportStart, txtExpectedBenefit, "No"), _
                                             Tab(txtReportingPeriods, txtUOM, "No"), _
                                             Tab(txtReportEnd, txtReportStart, "Int"), _
                                             Tab(ddlReportingInterval, txtReportingPeriods, "No"), _
                                             Tab(chkCustomYValues, txtReportEnd, "No"), _
                                             Tab(txtChartYMin, ddlReportingInterval, "No"), _
                                             Tab(txtChartYMax, chkCustomYValues, "Neg"), _
                                             Tab(txtChartYLines, txtChartYMin, "Neg"), _
                                             Tab(txtHistoric, txtChartYMax, "Yes")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
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
                lblRouteAbbrev.Text = GetTranslationString("team", lblRouteAbbrev.Text.Replace(":", "")) & ":"
                cbNegativeEntryAllowed.Text = GetTranslationString("negativeentryallowed", cbNegativeEntryAllowed.Text)
                lblRouteDefinition.Text = GetTranslationString("routedefinition", lblRouteDefinition.Text.Replace(":", "")) & ":"
                lblDataCollectionOnline.Text = GetTranslationString("datacollectiononline", lblDataCollectionOnline.Text.Replace(":", "")) & ":"
                lblResponsiblePerson.Text = GetTranslationString("responsibleperson", lblResponsiblePerson.Text.Replace(":", "")) & ":"
                lblHistoricValue.Text = GetTranslationString("historicvalue", lblHistoricValue.Text.Replace(":", "")) & ":"
                lblTargetValue.Text = GetTranslationString("targetvalue", lblTargetValue.Text.Replace(":", "")) & ":"
                lblHistoricStartDate.Text = GetTranslationString("historicstartdate", lblHistoricStartDate.Text.Replace(":", "")) & ":"
                lblHistoricEndDate.Text = GetTranslationString("historicenddate", lblHistoricEndDate.Text.Replace(":", "")) & ":"
                lblProjectedBenefit.Text = GetTranslationString("projectedbenefit", lblProjectedBenefit.Text.Replace(":", "")) & ":"
                lblExpectedBenefit.Text = GetTranslationString("expectedbenefit", lblExpectedBenefit.Text.Replace(":", "")) & ":"
                lblExpectedBenefitUOM.Text = GetTranslationString("expectedbenefituom", lblExpectedBenefitUOM.Text.Replace(":", "")) & ":"
                lblStartingPeriod.Text = GetTranslationString("startingperiod", lblStartingPeriod.Text.Replace(":", "")) & ":"
                lblOR.Text = GetTranslationString("or", lblOR.Text)
                lblReportingPeriods.Text = GetTranslationString("reportingperiods", lblReportingPeriods.Text.Replace(":", "")) & ":"
                lblEndingPeriod.Text = GetTranslationString("endingperiod", lblEndingPeriod.Text.Replace(":", "")) & ":"
                lblReportingInterval.Text = GetTranslationString("reportinginterval", lblReportingInterval.Text.Replace(":", "")) & ":"
                chkCustomYValues.Text = GetTranslationString("customyvalues", chkCustomYValues.Text.Replace(":", "")) & ":"
                lblChartYMin.Text = GetTranslationString("chartymin", lblChartYMin.Text.Replace(":", "")) & ":"
                lblChartYMax.Text = GetTranslationString("chartymax", lblChartYMax.Text.Replace(":", "")) & ":"
                lblChartYLines.Text = GetTranslationString("chartylines", lblChartYLines.Text.Replace(":", "")) & ":"
                btnOK.Text = GetTranslationString("ok", btnOK.Text)
                btnCancel.Text = GetTranslationString("cancel", btnCancel.Text)
                btnExit.Text = GetTranslationString("exit", btnExit.Text)
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

            If Not Page.IsPostBack Then
                LoadCultureTranslations()
            End If

            Master.HeaderMessage = GetTranslationString(FormName, FormName) & " - " & GetTranslationString(SessionManager.OPIMode.Replace("Row", ""), SessionManager.OPIMode.Replace("Row", ""))
            Master.IconImage = Request.ApplicationPath + "/images/TeamOPI.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/" & SessionManager.CulturePref & "/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                BindDropDownLists()
                BindUserDropDown()
                BindIntervalDropDown()

                Select Case SessionManager.OPIMode
                    Case "ViewRow", "View-OPI Entry"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        pnlOKCancel.Visible = True
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Team OPI.');")
                        TransactionHistory1.LockControl = True
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        LoadAddModeJavaScripts()

                        Dim objItem As ListItem = ddlTeam.Items.FindByValue(SessionManager.SelectedTeamID)
                        If objItem IsNot Nothing Then
                            objItem.Selected = True
                            txtTeam.Text = objItem.Text
                        End If
                        ddlTeam.Visible = False
                        txtTeam.Visible = True

                        txtOPI.Focus()
                    Case "EditRow"
                        LoadEditModeJavaScripts()
                        LoadSelectedRecord()
                        UnEnableRecords()
                        txtOPIShortName.Focus()
                    Case "Edit-OPI Entry"
                        LoadEditOPIModeJavaScripts()
                        LoadSelectedRecord()
                        UnEnableRecords()
                        txtReportStart.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamOPIMaintenance"), False)
                End Select
            End If
        End Sub
        Protected Sub ddlSite_SelectedIndexChanged(ByVal sender As Object, ByVal e As System.EventArgs) Handles ddlSite.SelectedIndexChanged
            BindUserDropDown()
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

            Select Case SessionManager.OPIMode
                Case "EditRow", "ViewRow", "DeleteRow", "AddRow"
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.OPIMode)
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamOPIMaintenance"), False)
                Case Else
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.OPIMode)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.OPIEntrySelectedValue)
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamOPIReports2"), False)
            End Select
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

            If SessionManager.OPIMode = "Edit-OPI Entry" Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.OPIMode)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.OPIEntrySelectedValue)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamOPIReports2"), False)
            Else
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.OPIMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamOPIMaintenance"), False)
            End If
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

            Dim blnSuccess As Boolean

            Select Case SessionManager.OPIMode
                Case "DeleteRow"
                    blnSuccess = DeleteTEAMOPI()
                Case "AddRow"
                    blnSuccess = InsertTEAMOPI()
                Case "EditRow", "Edit-OPI Entry"
                    blnSuccess = UpdateTEAMOPI()
            End Select

            If blnSuccess Then
                If SessionManager.OPIMode = "Edit-OPI Entry" Then
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.OPIMode)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.OPIEntrySelectedValue)
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamOPIReports2"), False)
                Else
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.OPIMode)
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamOPIMaintenance"), False)
                End If
            End If
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub BindDropDownLists()
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
                Teams.FillTeamSelectionList(ddlTeam, SessionManager.UserID, 0, 1)

                OPICategoryMaster.SelectOPICategoryMasterList(ddlOPICategoryMaster)
                OPIUOMMaster.SelectOPIUOMMasterList(ddlOPIUOMMaster)

                ddlCollectionInterval.Items.Add("Hour")
                ddlCollectionInterval.Items.Add("Day")
                ddlCollectionInterval.Items.Add("Week")
                ddlCollectionInterval.Items.Add("Month")
                ddlCollectionInterval.Items.Add("Per Instance")

                Dim objItem As ListItem = Nothing

                SiteMaster.SelectSiteMasterActiveList(ddlSite)
                If SessionManager.WorkingSiteID > 0 Then
                    objItem = ddlSite.Items.FindByValue(SessionManager.WorkingSiteID)
                Else
                    objItem = ddlSite.Items.FindByValue(UserMaster.GetUserSite(SessionManager.UserID))
                End If
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                Else
                    If ddlSite.Items.Count > 0 Then
                        ddlSite.Items(0).Selected = True
                    End If
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - SelectTeamList", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                Return
            End Try
        End Sub
        Private Sub BindIntervalDropDown()
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
                ddlReportingInterval.Items.Add("Day")
                ddlReportingInterval.Items.Add("Week")
                ddlReportingInterval.Items.Add("Month")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindIntervalDropDown", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                Return
            End Try
        End Sub
        Private Sub BindUserDropDown()
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
                ddlResponsiblePerson.Items.Clear()

                If ddlSite.SelectedItem IsNot Nothing Then
                    UserMaster.SelectUserNameList(ddlSite.SelectedItem.Value, True, ddlResponsiblePerson)
                Else
                    UserMaster.SelectUserNameList(SessionManager.WorkingSiteID, True, ddlResponsiblePerson)
                End If

                ddlResponsiblePerson.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - SelectUserMasterList", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                Return
            End Try
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

            Try
                Dim iTeamID As Integer = 0
                Dim strOPI As String = ""

                If SessionManager.OPIEntrySelectedValue.Trim.Length > 0 Then
                    iTeamID = SessionManager.OPIEntrySelectedValue
                    strOPI = SessionManager.OPIEntrySelectedValue1
                Else
                    iTeamID = SessionManager.SelectedValue
                    strOPI = SessionManager.SelectedValue1
                End If

                Dim objDT As DataTable = TeamOPI.SelectTeamOPI(iTeamID, strOPI)
                If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                    Dim dtRow As DataRow = objDT.Rows(0)
                    Dim objItem As ListItem
                    Dim bHidePanels As Boolean = False
                    Dim bAttributes As Boolean = False

                    If SessionManager.OPIMode = "ViewRow" OrElse SessionManager.OPIMode = "DeleteRow" OrElse SessionManager.OPIMode = "View-OPI Entry" Then
                        bHidePanels = True
                    End If

                    objItem = ddlTeam.Items.FindByValue(dtRow("TeamID").ToString)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                        txtTeam.Text = objItem.Text
                    End If
                    txtOPI.Text = dtRow("OPI").ToString
                    txtOPIShortName.Text = dtRow("OPIShortName").ToString
                    txtExpandOPIDescription.Text = dtRow("OPIDescription").ToString
                    objItem = ddlOPICategoryMaster.Items.FindByValue(dtRow("OPICategory").ToString)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                        txtOPICategoryMaster.Text = objItem.Text
                    End If
                    objItem = ddlOPIUOMMaster.Items.FindByValue(dtRow("OPIUOM").ToString)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                        txtOPIUOMMaster.Text = objItem.Text
                    End If
                    cbTimeEntryRequired.Checked = Convert.ToBoolean(dtRow("TimeEntryRequired").ToString)
                    cbCalculateValue.Checked = Convert.ToBoolean(dtRow("CalculateValue").ToString)
                    txtExpandOPIFormula.Text = dtRow("OPIFormula").ToString
                    txtExpandBenefitFormula.Text = dtRow("BenefitFormula").ToString
                    objItem = ddlEntryType.Items.FindByValue(dtRow("OPIEntryType").ToString)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                        txtOPIEntryType.Text = objItem.Text
                    End If
                    txtOPISize.Text = dtRow("OPISize").ToString
                    cbNegativeEntryAllowed.Checked = Convert.ToBoolean(dtRow("NegativeEntryAllowed").ToString)
                    txtSummaryType.Text = dtRow("SummaryType").ToString
                    txtExpandCollectionEvent.Text = dtRow("CollectionEvent").ToString
                    objItem = ddlCollectionInterval.Items.FindByValue(dtRow("CollectionInterval").ToString)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                        txtCollectionInterval.Text = objItem.Text
                    End If

                    ' Attributes
                    If dtRow("Attribute1") Is DBNull.Value Then
                        If bHidePanels = True Then
                            pnlAttribute1.Visible = False
                        End If
                    Else
                        txtAttribute1.Text = dtRow("Attribute1").ToString
                        objItem = ddlAttribute1EntryType.Items.FindByValue(dtRow("Attribute1EntryType").ToString)
                        If objItem IsNot Nothing Then
                            objItem.Selected = True
                            txtAttribute1EntryType.Text = objItem.Text
                        End If
                        txtAttribute1Size.Text = dtRow("Attribute1Size")
                        If dtRow("Attribute1Default") IsNot DBNull.Value Then
                            ckAttribute1Default.Checked = Convert.ToBoolean(dtRow("Attribute1Default"))
                        End If
                        bAttributes = True
                    End If
                    If dtRow("Attribute2") Is DBNull.Value Then
                        If bHidePanels = True Then
                            pnlAttribute2.Visible = False
                        End If
                    Else
                        txtAttribute2.Text = dtRow("Attribute2").ToString
                        objItem = ddlAttribute2EntryType.Items.FindByValue(dtRow("Attribute2EntryType").ToString)
                        If objItem IsNot Nothing Then
                            objItem.Selected = True
                            txtAttribute2EntryType.Text = objItem.Text
                        End If
                        txtAttribute2Size.Text = dtRow("Attribute2Size")
                        If dtRow("Attribute2Default") IsNot DBNull.Value Then
                            ckAttribute2Default.Checked = Convert.ToBoolean(dtRow("Attribute2Default"))
                        End If
                        bAttributes = True
                    End If
                    If dtRow("Attribute3") Is DBNull.Value Then
                        If bHidePanels = True Then
                            pnlAttribute3.Visible = False
                        End If
                    Else
                        txtAttribute3.Text = dtRow("Attribute3").ToString
                        objItem = ddlAttribute3EntryType.Items.FindByValue(dtRow("Attribute3EntryType").ToString)
                        If objItem IsNot Nothing Then
                            objItem.Selected = True
                            txtAttribute3EntryType.Text = objItem.Text
                        End If
                        txtAttribute3Size.Text = dtRow("Attribute3Size")
                        If dtRow("Attribute3Default") IsNot DBNull.Value Then
                            ckAttribute3Default.Checked = Convert.ToBoolean(dtRow("Attribute3Default"))
                        End If
                        bAttributes = True
                    End If
                    If dtRow("Attribute4") Is DBNull.Value Then
                        If bHidePanels = True Then
                            pnlAttribute4.Visible = False
                        End If
                    Else
                        txtAttribute4.Text = dtRow("Attribute4").ToString
                        objItem = ddlAttribute4EntryType.Items.FindByValue(dtRow("Attribute4EntryType").ToString)
                        If objItem IsNot Nothing Then
                            objItem.Selected = True
                            txtAttribute4EntryType.Text = objItem.Text
                        End If
                        txtAttribute4Size.Text = dtRow("Attribute4Size")
                        If dtRow("Attribute4Default") IsNot DBNull.Value Then
                            ckAttribute4Default.Checked = Convert.ToBoolean(dtRow("Attribute4Default"))
                        End If
                        bAttributes = True
                    End If
                    If dtRow("Attribute5") Is DBNull.Value Then
                        If bHidePanels = True Then
                            pnlAttribute5.Visible = False
                        End If
                    Else
                        txtAttribute5.Text = dtRow("Attribute5").ToString
                        objItem = ddlAttribute5EntryType.Items.FindByValue(dtRow("Attribute5EntryType").ToString)
                        If objItem IsNot Nothing Then
                            objItem.Selected = True
                            txtAttribute5EntryType.Text = objItem.Text
                        End If
                        txtAttribute5Size.Text = dtRow("Attribute5Size")
                        If dtRow("Attribute5Default") IsNot DBNull.Value Then
                            ckAttribute5Default.Checked = Convert.ToBoolean(dtRow("Attribute5Default"))
                        End If
                        bAttributes = True
                    End If
                    If dtRow("Attribute6") Is DBNull.Value Then
                        If bHidePanels = True Then
                            pnlAttribute6.Visible = False
                        End If
                    Else
                        txtAttribute6.Text = dtRow("Attribute6").ToString
                        objItem = ddlAttribute6EntryType.Items.FindByValue(dtRow("Attribute6EntryType").ToString)
                        If objItem IsNot Nothing Then
                            objItem.Selected = True
                            txtAttribute6EntryType.Text = objItem.Text
                        End If
                        txtAttribute6Size.Text = dtRow("Attribute6Size")
                        If dtRow("Attribute6Default") IsNot DBNull.Value Then
                            ckAttribute6Default.Checked = Convert.ToBoolean(dtRow("Attribute6Default"))
                        End If
                        bAttributes = True
                    End If

                    ' Team OPI
                    cbPrimaryOPI.Checked = Convert.ToBoolean(dtRow("PrimaryOPI").ToString())
                    cbDataCollectionOnline.Checked = Convert.ToBoolean(dtRow("DataCollectionOnline").ToString())
                    objItem = ddlResponsiblePerson.Items.FindByValue(dtRow("ResponsibleUser").ToString())
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                        txtResponsiblePerson.Text = objItem.Text
                    Else
                        objItem = New ListItem(UserMaster.GetUserFullName(dtRow("ResponsibleUser").ToString) & " (" & dtRow("ResponsibleUser").ToString & ")", dtRow("ResponsibleUser").ToString)
                        ddlResponsiblePerson.Items.Insert(1, objItem)
                        objItem.Selected = True
                        txtResponsiblePerson.Text = objItem.Text
                    End If
                    txtHistoric.Text = dtRow("Historic").ToString
                    txtTarget.Text = dtRow("Target").ToString
                    If IsDate(dtRow("HistoricStartDate").ToString) Then
                        txtStartDate.Text = Convert.ToDateTime(dtRow("HistoricStartDate")).ToString("yyyy/MM/dd")
                    Else
                        txtStartDate.Text = ""
                    End If
                    If IsDate(dtRow("HistoricEndDate").ToString) Then
                        txtEndDate.Text = Convert.ToDateTime(dtRow("HistoricEndDate")).ToString("yyyy/MM/dd")
                    Else
                        txtEndDate.Text = ""
                    End If
                    txtProjectedBenefit.Text = dtRow("ProjectedBenefit").ToString
                    txtExpectedBenefit.Text = dtRow("ExpectedBenefit").ToString
                    txtUOM.Text = dtRow("ExpectedBenefitUOM").ToString
                    If IsDate(dtRow("ReportStartDate")) Then
                        txtReportStart.Text = Convert.ToDateTime(dtRow("ReportStartDate")).ToString("yyyy/MM/dd")
                    Else
                        txtReportStart.Text = ""
                    End If
                    txtReportingPeriods.Text = dtRow("ReportingPeriods").ToString
                    If IsDate(dtRow("ReportEndDate")) Then
                        txtReportEnd.Text = Convert.ToDateTime(dtRow("ReportEndDate")).ToString("yyyy/MM/dd")
                    Else
                        txtReportEnd.Text = ""
                    End If
                    objItem = ddlReportingInterval.Items.FindByValue(dtRow("ReportingInterval").ToString)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                        txtReportingInterval.Text = objItem.Text
                    End If

                    If dtRow("CustomYAxisValues") IsNot DBNull.Value Then
                        chkCustomYValues.Checked = Convert.ToBoolean(dtRow("CustomYAxisValues").ToString)
                    End If
                    txtChartYMin.Text = dtRow("ChartYMin").ToString
                    txtChartYMax.Text = dtRow("ChartYMax").ToString
                    txtChartYLines.Text = dtRow("ChartYLines").ToString

                    'if the attribute bool is still false then hide the whole attributes panel
                    If bAttributes = False Then
                        If bHidePanels = True Then
                            pnlAttributes.Visible = False
                        End If
                    End If

                    TransactionHistory1.TableName = DBTableName
                    TransactionHistory1.RecordID = iTeamID.ToString & "," & strOPI

                    If SessionManager.OPIMode = "EditRow" OrElse SessionManager.OPIMode = "Edit-OPI Entry" Then
                        Dim objDic As New Dictionary(Of String, String)
                        objDic.Add("OPIShortName", txtOPIShortName.Text.Trim())
                        objDic.Add("OPIDescription", txtExpandOPIDescription.Text.Trim())
                        objDic.Add("OPICategory", ddlOPICategoryMaster.SelectedItem.Text.Trim())
                        objDic.Add("OPIUOM", ddlOPIUOMMaster.SelectedItem.Text.Trim())
                        objDic.Add("TimeEntryRequired", cbTimeEntryRequired.Checked)
                        objDic.Add("CalculateValue", cbCalculateValue.Checked)
                        objDic.Add("OPIFormula", txtExpandOPIFormula.Text.Trim())
                        objDic.Add("BenefitFormula", txtExpandBenefitFormula.Text.Trim())
                        objDic.Add("OPIEntryType", ddlEntryType.SelectedItem.Text.Trim())
                        objDic.Add("OPISize", txtOPISize.Text.Trim())
                        objDic.Add("NegativeEntryAllowed", cbNegativeEntryAllowed.Checked)
                        objDic.Add("SummaryType", txtSummaryType.Text.Trim())
                        objDic.Add("CollectionEvent", txtExpandCollectionEvent.Text.Trim())
                        objDic.Add("CollectionInterval", ddlCollectionInterval.SelectedItem.Text.Trim())
                        If pnlAttribute1.Visible Then
                            objDic.Add("Attribute1", txtAttribute1.Text.Trim())
                            objDic.Add("Attribute1EntryType", ddlAttribute1EntryType.SelectedItem.Text())
                            objDic.Add("Attribute1Size", txtAttribute1Size.Text.Trim())
                            objDic.Add("Attribute1Default", ckAttribute1Default.Checked)
                        End If
                        If pnlAttribute2.Visible Then
                            objDic.Add("Attribute2", txtAttribute2.Text.Trim())
                            objDic.Add("Attribute2EntryType", ddlAttribute2EntryType.SelectedItem.Text())
                            objDic.Add("Attribute2Size", txtAttribute2Size.Text.Trim())
                            objDic.Add("Attribute2Default", ckAttribute2Default.Checked)
                        End If
                        If pnlAttribute3.Visible Then
                            objDic.Add("Attribute3", txtAttribute3.Text.Trim())
                            objDic.Add("Attribute3EntryType", ddlAttribute3EntryType.SelectedItem.Text())
                            objDic.Add("Attribute3Size", txtAttribute3Size.Text.Trim())
                            objDic.Add("Attribute3Default", ckAttribute3Default.Checked)
                        End If
                        If pnlAttribute4.Visible Then
                            objDic.Add("Attribute4", txtAttribute4.Text.Trim())
                            objDic.Add("Attribute4EntryType", ddlAttribute4EntryType.SelectedItem.Text())
                            objDic.Add("Attribute4Size", txtAttribute4Size.Text.Trim())
                            objDic.Add("Attribute4Default", ckAttribute4Default.Checked)
                        End If
                        If pnlAttribute5.Visible Then
                            objDic.Add("Attribute5", txtAttribute5.Text.Trim())
                            objDic.Add("Attribute5EntryType", ddlAttribute5EntryType.SelectedItem.Text())
                            objDic.Add("Attribute5Size", txtAttribute5Size.Text.Trim())
                            objDic.Add("Attribute5Default", ckAttribute5Default.Checked)
                        End If
                        If pnlAttribute6.Visible Then
                            objDic.Add("Attribute6", txtAttribute6.Text.Trim())
                            objDic.Add("Attribute6EntryType", ddlAttribute6EntryType.SelectedItem.Text())
                            objDic.Add("Attribute6Size", txtAttribute6Size.Text.Trim())
                            objDic.Add("Attribute6Default", ckAttribute6Default.Checked)
                        End If
                        objDic.Add("PrimaryOPI", cbPrimaryOPI.Checked)
                        objDic.Add("DataCollectionOnline", cbDataCollectionOnline.Checked)
                        objDic.Add("ResponsibleUser", ddlResponsiblePerson.SelectedItem.Text())
                        objDic.Add("Historic", txtHistoric.Text.Trim())
                        objDic.Add("Target", txtTarget.Text.Trim())
                        objDic.Add("HistoricStartDate", txtStartDate.Text.Trim())
                        objDic.Add("HistoricEndDate", txtEndDate.Text.Trim())
                        objDic.Add("ProjectedBenefit", txtProjectedBenefit.Text.Trim())
                        objDic.Add("ExpectedBenefit", txtExpectedBenefit.Text.Trim())
                        objDic.Add("ExpectedBenefitUOM", txtUOM.Text.Trim())
                        objDic.Add("ReportingPeriods", txtReportingPeriods.Text.Trim())
                        objDic.Add("ReportStartDate", txtReportStart.Text.Trim())
                        objDic.Add("ReportEndDate", txtReportEnd.Text.Trim())
                        objDic.Add("ReportingInterval", ddlReportingInterval.SelectedItem.Text.Trim())
                        objDic.Add("CustomYAxisValues", chkCustomYValues.Checked)
                        objDic.Add("ChartYMin", txtChartYMin.Text.Trim())
                        objDic.Add("ChartYMax", txtChartYMax.Text.Trim())
                        objDic.Add("ChartYLines", txtChartYLines.Text.Trim())

                        SessionManager.RecordTransactionCurrentValues = objDic
                    End If
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
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

            Select Case SessionManager.OPIMode
                Case "ViewRow", "DeleteRow", "View-OPI Entry"
                    If SessionManager.OPIMode = "ViewRow" OrElse SessionManager.OPIMode = "View-OPI Entry" Then
                        pnlOKCancel.Visible = False
                    End If

                    ddlTeam.Visible = False
                    txtTeam.Visible = True
                    txtOPI.ReadOnly = True
                    txtOPI.CssClass = "Textbox_Display"
                    txtOPIShortName.ReadOnly = True
                    txtOPIShortName.CssClass = "Textbox_Display"
                    txtExpandOPIDescription.ReadOnly = True
                    txtExpandOPIDescription.CssClass = "Textbox_Display"
                    ddlOPICategoryMaster.Visible = False
                    txtOPICategoryMaster.Visible = True
                    ddlOPIUOMMaster.Visible = False
                    txtOPIUOMMaster.Visible = True
                    cbTimeEntryRequired.Enabled = False
                    cbCalculateValue.Enabled = False
                    txtExpandOPIFormula.ReadOnly = True
                    txtExpandOPIFormula.CssClass = "Textbox_Display"
                    txtExpandBenefitFormula.ReadOnly = True
                    txtExpandBenefitFormula.CssClass = "Textbox_Display"
                    ddlEntryType.Visible = False
                    txtOPIEntryType.Visible = True
                    txtOPISize.ReadOnly = True
                    txtOPISize.CssClass = "Textbox_Display"
                    cbNegativeEntryAllowed.Enabled = False
                    txtSummaryType.ReadOnly = True
                    txtSummaryType.CssClass = "Textbox_Display"
                    txtExpandCollectionEvent.ReadOnly = True
                    txtExpandCollectionEvent.CssClass = "Textbox_Display"
                    ddlCollectionInterval.Visible = False
                    txtCollectionInterval.Visible = True

                    txtAttribute1.ReadOnly = True
                    txtAttribute1.CssClass = "Textbox_Display"
                    ddlAttribute1EntryType.Visible = False
                    txtAttribute1EntryType.Visible = True
                    txtAttribute1Size.ReadOnly = True
                    txtAttribute1Size.CssClass = "Textbox_Display"
                    ckAttribute1Default.Enabled = False

                    txtAttribute2.ReadOnly = True
                    txtAttribute2.CssClass = "Textbox_Display"
                    ddlAttribute2EntryType.Visible = False
                    txtAttribute2EntryType.Visible = True
                    txtAttribute2Size.ReadOnly = True
                    txtAttribute2Size.CssClass = "Textbox_Display"
                    ckAttribute2Default.Enabled = False

                    txtAttribute3.ReadOnly = True
                    txtAttribute3.CssClass = "Textbox_Display"
                    ddlAttribute3EntryType.Visible = False
                    txtAttribute3EntryType.Visible = True
                    txtAttribute3Size.ReadOnly = True
                    txtAttribute3Size.CssClass = "Textbox_Display"
                    ckAttribute3Default.Enabled = False

                    txtAttribute4.ReadOnly = True
                    txtAttribute4.CssClass = "Textbox_Display"
                    ddlAttribute4EntryType.Visible = False
                    txtAttribute4EntryType.Visible = True
                    txtAttribute4Size.ReadOnly = True
                    txtAttribute4Size.CssClass = "Textbox_Display"
                    ckAttribute4Default.Enabled = False

                    txtAttribute5.ReadOnly = True
                    txtAttribute5.CssClass = "Textbox_Display"
                    ddlAttribute5EntryType.Visible = False
                    txtAttribute5EntryType.Visible = True
                    txtAttribute5Size.ReadOnly = True
                    txtAttribute5Size.CssClass = "Textbox_Display"
                    ckAttribute5Default.Enabled = False

                    txtAttribute6.ReadOnly = True
                    txtAttribute6.CssClass = "Textbox_Display"
                    ddlAttribute6EntryType.Visible = False
                    txtAttribute6EntryType.Visible = True
                    txtAttribute6Size.ReadOnly = True
                    txtAttribute6Size.CssClass = "Textbox_Display"
                    ckAttribute6Default.Enabled = False

                    cbPrimaryOPI.Enabled = False
                    txtTarget.ReadOnly = True
                    txtTarget.CssClass = "Textbox_Display"
                    txtHistoric.ReadOnly = True
                    txtHistoric.CssClass = "Textbox_Display"
                    txtStartDate.ReadOnly = True
                    txtStartDate.CssClass = "Textbox_Display"
                    txtStartDate_CalendarExtender.Enabled = False
                    txtEndDate.ReadOnly = True
                    txtEndDate.CssClass = "Textbox_Display"
                    txtEndDate_CalendarExtender.Enabled = False
                    imgStartDate.Visible = False
                    txtStartDate_CalendarExtender.Enabled = False
                    imgEndDate.Visible = False
                    txtEndDate_CalendarExtender.Enabled = False
                    txtProjectedBenefit.ReadOnly = True
                    txtProjectedBenefit.CssClass = "Textbox_Display"
                    txtExpectedBenefit.ReadOnly = True
                    txtExpectedBenefit.CssClass = "Textbox_Display"
                    txtReportingPeriods.ReadOnly = True
                    txtReportingPeriods.CssClass = "Textbox_Display"
                    txtUOM.ReadOnly = True
                    txtUOM.CssClass = "Textbox_Display"
                    imgReportStart.Visible = False
                    txtReportStart_CalendarExtender.Enabled = False
                    txtReportStart.ReadOnly = True
                    txtReportStart.CssClass = "Textbox_Display"
                    txtReportStart_CalendarExtender.Enabled = False
                    imgReportEnd.Visible = False
                    txtReportEnd_CalendarExtender.Enabled = False
                    txtReportEnd.ReadOnly = True
                    txtReportEnd.CssClass = "Textbox_Display"
                    txtReportEnd_CalendarExtender.Enabled = False
                    chkCustomYValues.Enabled = False
                    txtChartYMin.ReadOnly = True
                    txtChartYMin.CssClass = "Textbox_Display"
                    txtChartYMax.ReadOnly = True
                    txtChartYMax.CssClass = "Textbox_Display"
                    txtChartYLines.ReadOnly = True
                    txtChartYLines.CssClass = "Textbox_Display"
                    ddlReportingInterval.Visible = False
                    txtReportingInterval.Visible = True
                    ddlResponsiblePerson.Visible = False
                    txtResponsiblePerson.Visible = True
                    ddlSite.Visible = False
                    cbDataCollectionOnline.Enabled = False
                Case "EditRow"
                    ddlTeam.Visible = False
                    txtTeam.Visible = True
                    txtOPI.ReadOnly = True
                    txtOPI.CssClass = "Textbox_Display"
                    cbPrimaryOPI.Focus()
                Case "Edit-OPI Entry"
                    ddlTeam.Visible = False
                    txtTeam.Visible = True
                    txtOPI.ReadOnly = True
                    txtOPI.CssClass = "Textbox_Display"
                    cbPrimaryOPI.Enabled = False
                    ddlSite.Visible = False
                    cbDataCollectionOnline.Enabled = False
            End Select
        End Sub
        Private Function InsertTEAMOPI() As Boolean
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
                Dim passReportingPeriods As Integer = -1
                If txtReportingPeriods.Text.Trim.Length > 0 Then passReportingPeriods = Convert.ToInt32(txtReportingPeriods.Text.Trim)
                Dim passReportStart As String = RegionalConversion.FormatSQLDate(txtReportStart.Text)
                Dim passReportEnd As String = RegionalConversion.FormatSQLDate(txtReportEnd.Text)
                Dim passReportInterval As String = ddlReportingInterval.SelectedItem.Value

                'we MUST have a report periods or report start
                If passReportingPeriods <= 0 AndAlso passReportStart.Trim.Length = 0 Then
                    Master.DisplayError("You must enter a valid Report Start Date or number of Reporting Periods")
                    Return False
                End If

                If chkCustomYValues.Checked Then
                    If txtChartYMin.Text.Trim.Length = 0 OrElse txtChartYMax.Text.Trim.Length = 0 OrElse txtChartYLines.Text.Trim.Length = 0 Then
                        Master.DisplayError("All Chart Y Axis values must be entered to use Custom Values.")
                        Return False
                    ElseIf CDbl(txtChartYMax.Text) <= CDbl(txtChartYMin.Text) Then
                        Master.DisplayError("Y Axis Max Value must be greate than Y Asix Min Value")
                        Return False
                    End If
                End If

                If Not IsNumeric(txtOPISize.Text) Then
                    Master.DisplayError("OPI Size must be numeric")
                    Return False
                ElseIf ddlEntryType.SelectedItem IsNot Nothing AndAlso ddlEntryType.SelectedItem.Value = "N" AndAlso Convert.ToInt16(txtOPISize.Text) = 0 Then
                    Master.DisplayError("OPI Size must be > 0 for integer type")
                    Return False
                End If

                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                Dim sHistoric As String = RegionalConversion.FormatSQLSingle(txtHistoric.Text)
                Dim sTarget As String = RegionalConversion.FormatSQLSingle(txtTarget.Text)
                Dim sProjectedBenefit As String = RegionalConversion.FormatSQLSingle(txtProjectedBenefit.Text)
                Dim sExptectedBenefit As String = RegionalConversion.FormatSQLSingle(txtExpectedBenefit.Text)
                Dim sChartYMin As String = RegionalConversion.FormatSQLSingle(txtChartYMin.Text)
                Dim sChartYMax As String = RegionalConversion.FormatSQLSingle(txtChartYMax.Text)

                TeamOPI.AddTeamOPI(ddlTeam.SelectedValue.Trim, txtOPI.Text.Trim, txtOPIShortName.Text.Trim(), txtExpandOPIDescription.Text.Trim(), ddlOPICategoryMaster.SelectedItem.Text.Trim(), ddlOPIUOMMaster.SelectedItem.Text.Trim(), ddlEntryType.SelectedItem.Value.ToString.ToUpper.Trim(), _
                                      Convert.ToInt32("0" + txtOPISize.Text), txtSummaryType.Text.ToUpper.Trim(), txtExpandCollectionEvent.Text.Trim(), ddlCollectionInterval.SelectedItem.Text.Trim(), cbTimeEntryRequired.Checked, cbNegativeEntryAllowed.Checked, cbCalculateValue.Checked, _
                                      txtExpandOPIFormula.Text.Trim(), txtExpandBenefitFormula.Text.Trim(), txtAttribute1.Text.Trim(), ddlAttribute1EntryType.SelectedItem.Value.ToString.ToUpper, Convert.ToInt32("0" + txtAttribute1Size.Text), ckAttribute1Default.Checked, _
                                      txtAttribute2.Text.Trim(), ddlAttribute2EntryType.SelectedItem.Value.ToString.ToUpper.Trim(), Convert.ToInt32("0" + txtAttribute2Size.Text), ckAttribute2Default.Checked, txtAttribute3.Text.Trim(), ddlAttribute3EntryType.SelectedItem.Value.ToString.ToUpper, _
                                      Convert.ToInt32("0" + txtAttribute3Size.Text), ckAttribute3Default.Checked, txtAttribute4.Text.Trim(), ddlAttribute4EntryType.SelectedItem.Value.ToString.ToUpper.Trim(), Convert.ToInt32("0" + txtAttribute4Size.Text), ckAttribute4Default.Checked, txtAttribute5.Text, _
                                      ddlAttribute5EntryType.SelectedItem.Value.ToString.ToUpper, Convert.ToInt32("0" + txtAttribute5Size.Text), ckAttribute5Default.Checked, txtAttribute6.Text.Trim(), ddlAttribute6EntryType.SelectedItem.Value.ToString.ToUpper.Trim(), Convert.ToInt32("0" + txtAttribute6Size.Text), _
                                      ckAttribute6Default.Checked, cbPrimaryOPI.Checked, ddlResponsiblePerson.SelectedItem.Value.ToString.Trim(), cbDataCollectionOnline.Checked, sTarget, sHistoric, RegionalConversion.FormatSQLDate(txtStartDate.Text), RegionalConversion.FormatSQLDate(txtEndDate.Text), sProjectedBenefit, _
                                      sExptectedBenefit, txtUOM.Text, passReportInterval, passReportingPeriods, passReportStart, passReportEnd, chkCustomYValues.Checked, sChartYMin, sChartYMax, txtChartYLines.Text.Trim)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, ddlTeam.SelectedValue.ToString.Trim & "," & txtOPI.Text.Trim, "OPI Created", SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertTEAMOPI ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateTEAMOPI() As Boolean
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
                Dim passReportingPeriods As Integer = -1
                If txtReportingPeriods.Text.Trim.Length > 0 Then passReportingPeriods = Convert.ToInt32(txtReportingPeriods.Text.Trim)
                Dim passReportStart As String = RegionalConversion.FormatSQLDate(txtReportStart.Text)
                Dim passReportEnd As String = RegionalConversion.FormatSQLDate(txtReportEnd.Text)
                Dim passReportInterval As String = ddlReportingInterval.SelectedItem.Value

                If passReportingPeriods <= 0 AndAlso passReportStart.Trim.Length = 0 Then
                    Master.DisplayError("You must enter a valid Report Start Date or number of Reporting Periods")
                    Return False
                End If

                If chkCustomYValues.Checked Then
                    If txtChartYMin.Text.Trim.Length = 0 OrElse txtChartYMax.Text.Trim.Length = 0 OrElse txtChartYLines.Text.Trim.Length = 0 Then
                        Master.DisplayError("All Chart Y Axis values must be entered to use Custom Values.")
                        Return False
                    ElseIf CDbl(txtChartYMax.Text) <= CDbl(txtChartYMin.Text) Then
                        Master.DisplayError("Y Axis Max Value must be greate than Y Asix Min Value")
                        Return False
                    End If
                End If

                If Not IsNumeric(txtOPISize.Text) Then
                    Master.DisplayError("OPI Size must be numeric")
                    Return False
                ElseIf ddlEntryType.SelectedItem IsNot Nothing AndAlso ddlEntryType.SelectedItem.Value = "N" AndAlso Convert.ToInt16(txtOPISize.Text) = 0 Then
                    Master.DisplayError("OPI Size must be > 0 for integer type")
                    Return False
                End If

                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.CompareDictionaryValues(SessionManager.RecordTransactionCurrentValues, objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                Dim iTeamID As Integer = 0
                Dim strOPI As String = ""
                If SessionManager.OPIEntrySelectedValue.Trim.Length > 0 Then
                    iTeamID = SessionManager.OPIEntrySelectedValue
                    strOPI = SessionManager.OPIEntrySelectedValue1
                Else
                    iTeamID = SessionManager.SelectedValue
                    strOPI = SessionManager.SelectedValue1
                End If
                Dim sHistoric As String = RegionalConversion.FormatSQLSingle(txtHistoric.Text)
                Dim sTarget As String = RegionalConversion.FormatSQLSingle(txtTarget.Text)
                Dim sProjectedBenefit As String = RegionalConversion.FormatSQLSingle(txtProjectedBenefit.Text)
                Dim sExptectedBenefit As String = RegionalConversion.FormatSQLSingle(txtExpectedBenefit.Text)
                Dim sChartYMin As String = RegionalConversion.FormatSQLSingle(txtChartYMin.Text)
                Dim sChartYMax As String = RegionalConversion.FormatSQLSingle(txtChartYMax.Text)

                TeamOPI.UpdateTeamOPI(iTeamID, strOPI, txtOPIShortName.Text.Trim(), txtExpandOPIDescription.Text.Trim(), ddlOPICategoryMaster.SelectedItem.Text.Trim(), ddlOPIUOMMaster.SelectedItem.Text.Trim(), ddlEntryType.SelectedItem.Value.ToString.ToUpper.Trim(), _
                                      Convert.ToInt32("0" + txtOPISize.Text), txtSummaryType.Text.ToUpper.Trim(), txtExpandCollectionEvent.Text.Trim(), ddlCollectionInterval.SelectedItem.Text.Trim(), cbTimeEntryRequired.Checked, cbNegativeEntryAllowed.Checked, cbCalculateValue.Checked, _
                                      txtExpandOPIFormula.Text.Trim(), txtExpandBenefitFormula.Text.Trim(), txtAttribute1.Text.Trim(), ddlAttribute1EntryType.SelectedItem.Value.ToString.ToUpper, Convert.ToInt32("0" + txtAttribute1Size.Text), ckAttribute1Default.Checked, _
                                      txtAttribute2.Text.Trim(), ddlAttribute2EntryType.SelectedItem.Value.ToString.ToUpper.Trim(), Convert.ToInt32("0" + txtAttribute2Size.Text), ckAttribute2Default.Checked, txtAttribute3.Text.Trim(), ddlAttribute3EntryType.SelectedItem.Value.ToString.ToUpper, _
                                      Convert.ToInt32("0" + txtAttribute3Size.Text), ckAttribute3Default.Checked, txtAttribute4.Text.Trim(), ddlAttribute4EntryType.SelectedItem.Value.ToString.ToUpper.Trim(), Convert.ToInt32("0" + txtAttribute4Size.Text), ckAttribute4Default.Checked, txtAttribute5.Text, _
                                      ddlAttribute5EntryType.SelectedItem.Value.ToString.ToUpper, Convert.ToInt32("0" + txtAttribute5Size.Text), ckAttribute5Default.Checked, txtAttribute6.Text.Trim(), ddlAttribute6EntryType.SelectedItem.Value.ToString.ToUpper.Trim(), Convert.ToInt32("0" + txtAttribute6Size.Text), _
                                      ckAttribute6Default.Checked, cbPrimaryOPI.Checked, ddlResponsiblePerson.SelectedItem.Value.ToString.Trim(), cbDataCollectionOnline.Checked, sTarget, sHistoric, RegionalConversion.FormatSQLDate(txtStartDate.Text), RegionalConversion.FormatSQLDate(txtEndDate.Text), sProjectedBenefit, _
                                      sExptectedBenefit, txtUOM.Text, passReportInterval, passReportingPeriods, passReportStart, passReportEnd, chkCustomYValues.Checked, sChartYMin, sChartYMax, txtChartYLines.Text.Trim)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, iTeamID.ToString & "," & strOPI, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateTEAMOPI ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function DeleteTEAMOPI() As Boolean
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
                TeamOPI.DeleteTeamOPI(SessionManager.SelectedTeamID, txtOPI.Text.Trim)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, txtTeam.Text.Trim & "," & txtOPI.Text.Trim, "Team OPI Deleted", SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteTEAMOPI ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
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

            objDic.Add("OPIShortName", txtOPIShortName.Text.Trim())
            objDic.Add("OPIDescription", txtExpandOPIDescription.Text.Trim())
            objDic.Add("OPICategory", ddlOPICategoryMaster.SelectedItem.Text.Trim())
            objDic.Add("OPIUOM", ddlOPIUOMMaster.SelectedItem.Text.Trim())
            objDic.Add("TimeEntryRequired", cbTimeEntryRequired.Checked)
            objDic.Add("CalculateValue", cbCalculateValue.Checked)
            objDic.Add("OPIFormula", txtExpandOPIFormula.Text.Trim())
            objDic.Add("BenefitFormula", txtExpandBenefitFormula.Text.Trim())
            objDic.Add("OPIEntryType", ddlEntryType.SelectedItem.Text.Trim())
            objDic.Add("OPISize", txtOPISize.Text.Trim())
            objDic.Add("NegativeEntryAllowed", cbNegativeEntryAllowed.Checked)
            objDic.Add("SummaryType", txtSummaryType.Text.Trim())
            objDic.Add("CollectionEvent", txtExpandCollectionEvent.Text.Trim())
            objDic.Add("CollectionInterval", ddlCollectionInterval.SelectedItem.Text.Trim())
            If pnlAttribute1.Visible Then
                objDic.Add("Attribute1", txtAttribute1.Text.Trim())
                objDic.Add("Attribute1EntryType", ddlAttribute1EntryType.SelectedItem.Text())
                objDic.Add("Attribute1Size", txtAttribute1Size.Text.Trim())
                objDic.Add("Attribute1Default", ckAttribute1Default.Checked)
            End If
            If pnlAttribute2.Visible Then
                objDic.Add("Attribute2", txtAttribute2.Text.Trim())
                objDic.Add("Attribute2EntryType", ddlAttribute2EntryType.SelectedItem.Text())
                objDic.Add("Attribute2Size", txtAttribute2Size.Text.Trim())
                objDic.Add("Attribute2Default", ckAttribute2Default.Checked)
            End If
            If pnlAttribute3.Visible Then
                objDic.Add("Attribute3", txtAttribute3.Text.Trim())
                objDic.Add("Attribute3EntryType", ddlAttribute3EntryType.SelectedItem.Text())
                objDic.Add("Attribute3Size", txtAttribute3Size.Text.Trim())
                objDic.Add("Attribute3Default", ckAttribute3Default.Checked)
            End If
            If pnlAttribute4.Visible Then
                objDic.Add("Attribute4", txtAttribute4.Text.Trim())
                objDic.Add("Attribute4EntryType", ddlAttribute4EntryType.SelectedItem.Text())
                objDic.Add("Attribute4Size", txtAttribute4Size.Text.Trim())
                objDic.Add("Attribute4Default", ckAttribute4Default.Checked)
            End If
            If pnlAttribute5.Visible Then
                objDic.Add("Attribute5", txtAttribute5.Text.Trim())
                objDic.Add("Attribute5EntryType", ddlAttribute5EntryType.SelectedItem.Text())
                objDic.Add("Attribute5Size", txtAttribute5Size.Text.Trim())
                objDic.Add("Attribute5Default", ckAttribute5Default.Checked)
            End If
            If pnlAttribute6.Visible Then
                objDic.Add("Attribute6", txtAttribute6.Text.Trim())
                objDic.Add("Attribute6EntryType", ddlAttribute6EntryType.SelectedItem.Text())
                objDic.Add("Attribute6Size", txtAttribute6Size.Text.Trim())
                objDic.Add("Attribute6Default", ckAttribute6Default.Checked)
            End If

            objDic.Add("PrimaryOPI", cbPrimaryOPI.Checked)
            objDic.Add("DataCollectionOnline", cbDataCollectionOnline.Checked)
            If ddlResponsiblePerson.SelectedItem IsNot Nothing Then
                objDic.Add("ResponsibleUser", ddlResponsiblePerson.SelectedItem.Text())
            Else
                objDic.Add("ResponsibleUser", txtResponsiblePerson.Text.Trim)
            End If
            objDic.Add("Historic", txtHistoric.Text.Trim())
            objDic.Add("Target", txtTarget.Text.Trim())
            objDic.Add("HistoricStartDate", txtStartDate.Text.Trim())
            objDic.Add("HistoricEndDate", txtEndDate.Text.Trim())
            objDic.Add("ProjectedBenefit", txtProjectedBenefit.Text.Trim())
            objDic.Add("ExpectedBenefit", txtExpectedBenefit.Text.Trim())
            objDic.Add("ExpectedBenefitUOM", txtUOM.Text.Trim())
            objDic.Add("ReportingPeriods", txtReportingPeriods.Text.Trim())
            objDic.Add("ReportStartDate", txtReportStart.Text.Trim())
            objDic.Add("ReportEndDate", txtReportEnd.Text.Trim())
            If ddlReportingInterval.SelectedItem IsNot Nothing Then
                objDic.Add("ReportingInterval", ddlReportingInterval.SelectedItem.Text.Trim())
            Else
                objDic.Add("ReportingInterval", txtReportingInterval.Text.Trim)
            End If
            objDic.Add("CustomYAxisValues", chkCustomYValues.Checked.ToString)
            objDic.Add("ChartYMin", txtChartYMin.Text.Trim())
            objDic.Add("ChartYMax", txtChartYMax.Text.Trim())
            objDic.Add("ChartYLines", txtChartYLines.Text.Trim())
            Return objDic
        End Function
#End Region

    End Class
End Namespace