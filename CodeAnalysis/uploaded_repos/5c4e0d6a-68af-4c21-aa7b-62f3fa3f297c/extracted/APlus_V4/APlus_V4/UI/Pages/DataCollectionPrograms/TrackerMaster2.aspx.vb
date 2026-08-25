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
    Partial Class TrackerMaster2
        Inherits ApplicationBase

#Region " Private Variables"
        Private Shared ReadOnly FormName As String = "Savings Tracker"
        Private Shared ReadOnly ProgramName As String = "TrackerMaster2"
        Private Shared ReadOnly DBTableName As String = "Trackers"
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
                lblSavingsTracker.Text = GetTranslationString("savingstracker", lblSavingsTracker.Text.Replace(":", "")) & ":"
                lblTrackerOther.Text = GetTranslationString("trackerother", lblTrackerOther.Text.Replace(":", "")) & ":"
                lblTeam.Text = GetTranslationString("team", lblTeam.Text.Replace(":", "")) & ":"
                lblSavingsCategory.Text = GetTranslationString("savingscategory", lblSavingsCategory.Text.Replace(":", "")) & ":"
                lblUOM.Text = GetTranslationString("uom", lblUOM.Text.Replace(":", "")) & ":"
                lblHistoric.Text = GetTranslationString("historic", lblHistoric.Text.Replace(":", "")) & ":"
                lblTarget.Text = GetTranslationString("target", lblTarget.Text.Replace(":", "")) & ":"
                lblStartPeriod.Text = GetTranslationString("startperiod", lblStartPeriod.Text.Replace(":", "")) & ":"
                lblDescription.Text = GetTranslationString("description", lblDescription.Text.Replace(":", "")) & ":"
                lblInterface.Text = GetTranslationString("interface", lblInterface.Text.Replace(":", "")) & ":"
                lblFormula.Text = GetTranslationString("formula", lblFormula.Text.Replace(":", "")) & ":"
                lblScheduleCode.Text = GetTranslationString("schedulecode", lblScheduleCode.Text.Replace(":", "")) & ":"
                lblScheduleTime.Text = GetTranslationString("scheduletime", lblScheduleTime.Text.Replace(":", "")) & ":"
                lblNextExecution.Text = GetTranslationString("nextexecution", lblNextExecution.Text.Replace(":", "")) & ":"
                lblLastExecution.Text = GetTranslationString("lastexecution", lblLastExecution.Text.Replace(":", "")) & ":"
                lblLastExecutionSuccessful.Text = GetTranslationString("lastexecutionsuccessful", lblLastExecutionSuccessful.Text.Replace(":", "")) & ":"
                lblOnDemandExecute.Text = GetTranslationString("ondemandexecute", lblOnDemandExecute.Text.Replace(":", "")) & ":"
                lblActive.Text = GetTranslationString("active", lblActive.Text.Replace(":", "")) & ":"
                btnOK.Text = GetTranslationString("ok", btnOK.Text)
                btnCancel.Text = GetTranslationString("cancel", btnCancel.Text)
                btnExit.Text = GetTranslationString("exit", btnExit.Text)
                btnTrackerTypes.Text = GetTranslationString("trackertypes", btnTrackerTypes.Text)
                btnTrackerTypes2.Text = GetTranslationString("trackertypes", btnTrackerTypes2.Text)
                btnVariables.Text = GetTranslationString("variables", btnVariables.Text)
                btnVariables2.Text = GetTranslationString("variables", btnVariables2.Text)
                lblSavingsTypesHeader.Text = GetTranslationString("trackertypes", lblSavingsTypesHeader.Text)
                lblTrackerVariables.Text = GetTranslationString("trackervariables", lblTrackerVariables.Text)
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

            txtStartDate_CalendarExtender.Format = "yyyy/MM/dd"

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnExit.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
        End Sub
        Private Sub LoadAddEditModeJavaScripts()
            Dim myTabArray() As Object = {txtTracker, _
                                          txtTrackerOther, _
                                          ddlTeam, _
                                          ddlSavingsCategory, _
                                          txtUOM, _
                                          txtHistoric, _
                                          txtTarget, _
                                          txtStartDate, _
                                          txtExpandDescription, _
                                          ckInterface, _
                                          txtExpandFormula, _
                                          txtScheduleCode, _
                                          txtScheduleTime, _
                                          txtOnDemandExecute, _
                                          cbActive}

            Dim TabKeyDownArr() As String = {Tab(txtTrackerOther, cbActive, "No"), _
                                             Tab(ddlTeam, txtTracker, "No"), _
                                             Tab(ddlSavingsCategory, txtTrackerOther, "No"), _
                                             Tab(txtUOM, ddlTeam, "No"), _
                                             Tab(txtHistoric, ddlSavingsCategory, "No"), _
                                             Tab(txtTarget, txtUOM, "Yes"), _
                                             Tab(txtStartDate, txtHistoric, "Yes"), _
                                             Tab(txtExpandDescription, txtTarget, "No"), _
                                             Tab(ckInterface, txtStartDate, "No"), _
                                             Tab(txtExpandFormula, txtExpandDescription, "No"), _
                                             Tab(txtScheduleCode, ckInterface, "No"), _
                                             Tab(txtScheduleTime, txtExpandFormula, "No"), _
                                             Tab(txtOnDemandExecute, txtScheduleCode, "Int"), _
                                             Tab(cbActive, txtScheduleTime, "No"), _
                                             Tab(txtTracker, txtOnDemandExecute, "No")}

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

            Master.HeaderMessage = GetTranslationString(FormName, FormName) & " - " & GetTranslationString(SessionManager.TrackerMode.Replace("Row", ""), SessionManager.TrackerMode.Replace("Row", ""))
            Master.IconImage = Request.ApplicationPath + "/images/boss.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/" & SessionManager.CulturePref & "/DataEntry.js")

            LoadCommonJavaScripts()

            Dim strSessionID As String = Session.SessionID.ToString
            strSessionID = "(S(" + strSessionID + "))"
            imgElements.Attributes.Add("onclick", "window.open('/APlus/" + strSessionID + "/UI/Pages/DataCollectionPrograms/DataElementsListing.aspx','newWin','height=500, width=500, left=500, top=100, resizable=yes, scrollbars=1');")

            If Not Page.IsPostBack Then
                LoadCultureTranslations()

                BindDropDownLists()

                Select Case SessionManager.TrackerMode.ToString()
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                        imgElements.Visible = False
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        pnlOKCancel.Visible = True
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Tracker.');")
                        TransactionHistory1.LockControl = True
                        imgElements.Visible = False
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        pnlMasterControls.Visible = False
                        LoadAddEditModeJavaScripts()
                        If SessionManager.SelectedValueTeamID > 0 Then
                            Dim objItem As ListItem = ddlTeam.Items.FindByValue(SessionManager.SelectedValueTeamID)
                            If objItem IsNot Nothing Then
                                objItem.Selected = True
                                txtTeam.Text = objItem.Text

                                ddlTeam.Visible = False
                                txtTeam.Visible = True
                            End If
                        End If
                        txtTracker.Focus()
                        cbActive.Checked = True
                    Case "EditRow"
                        LoadAddEditModeJavaScripts()
                        LoadSelectedRecord()
                        UnEnableRecords()
                        txtTracker.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TrackerMaster1"), False)
                End Select
            End If
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
            Select Case SessionManager.TrackerMode
                Case "AddRow"
                    blnSuccess = InsertTracker()
                Case "EditRow"
                    blnSuccess = UpdateTracker()
                Case "DeleteRow"
                    blnSuccess = DeleteTracker()
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueTrackerID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TrackerMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TrackerMaster1"), False)
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueTrackerID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TrackerMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TrackerMaster1"), False)
        End Sub
        Protected Sub btnTrackerTypes_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnTrackerTypes.Click, btnTrackerTypes2.Click
            If SessionManager.TrackerMode = "AddRow" Then
                If InsertTracker() Then
                    SessionManager.TrackerMode = "EditRow"
                    SessionManager.MasterControlExitProgram = "TrackerMaster2"
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TrackerCollection1"), False)
                End If
            Else
                If UpdateTracker() Then
                    SessionManager.MasterControlExitProgram = "TrackerMaster2"
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TrackerCollection1"), False)
                End If
            End If
        End Sub
        Protected Sub btnVariables_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnVariables.Click, btnVariables2.Click
            If SessionManager.TrackerMode = "AddRow" Then
                If InsertTracker() Then
                    SessionManager.TrackerMode = "EditRow"
                    SessionManager.MasterControlExitProgram = "TrackerMaster2"
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TrackerVariables1"), False)
                End If
            Else
                If UpdateTracker() Then
                    SessionManager.MasterControlExitProgram = "TrackerMaster2"
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TrackerVariables1"), False)
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
                Teams.FillTeamSelectionList(ddlTeam, SessionManager.UserID, SessionManager.WorkingSiteID, True)
                ddlTeam.Items.Insert(0, "")

                SavingsCategoryMaster.GetSavingsCategoryList(ddlSavingsCategory)
                ddlSavingsCategory.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - SelectTeamList", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
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

            If SessionManager.RecordTransactionCurrentValues IsNot Nothing Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RecordTransactionCurrentValues)
            End If

            Dim objDT As DataTable = Trackers.SelectTracker(SessionManager.SelectedValueTrackerID)
            If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                Dim dtRow As DataRow = objDT.Rows(0)
                Dim objItem As ListItem

                txtTracker.Text = dtRow("Tracker").ToString
                txtTrackerOther.Text = dtRow("TrackerOther").ToString
                objItem = ddlTeam.Items.FindByValue(dtRow("TeamID").ToString)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                    txtTeam.Text = objItem.Text
                End If
                objItem = ddlSavingsCategory.Items.FindByValue(dtRow("SavingsCategoryID").ToString)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                    txtSavingsCategory.Text = objItem.Text
                End If
                txtUOM.Text = dtRow("TrackerValueUOM").ToString
                txtHistoric.Text = dtRow("Historic").ToString
                txtTarget.Text = dtRow("Target").ToString
                If IsDate(dtRow("StartPeriod").ToString) Then
                    txtStartDate.Text = Convert.ToDateTime(dtRow("StartPeriod").ToString).ToString("yyyy/MM/dd")
                Else
                    txtStartDate.Text = dtRow("StartPeriod").ToString
                End If
                txtExpandDescription.Text = dtRow("Description").ToString
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
                cbActive.Checked = Convert.ToBoolean(dtRow("Active").ToString)

                TransactionHistory1.TableName = DBTableName
                TransactionHistory1.RecordID = SessionManager.SelectedValueTrackerID.ToString

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("Tracker", txtTracker.Text.Trim())
                objDic.Add("TrackerOther", txtTrackerOther.Text.Trim())
                objDic.Add("Team", txtTeam.Text.Trim)
                objDic.Add("SavingsCategory", txtSavingsCategory.Text.Trim)
                objDic.Add("TrackerUOM", txtUOM.Text.Trim)
                objDic.Add("Historic", txtHistoric.Text)
                objDic.Add("Target", txtTarget.Text)
                objDic.Add("StartPeriod", RegionalConversion.FormatSQLDate(txtStartDate.Text))
                objDic.Add("Description", txtExpandDescription.Text.Trim)
                objDic.Add("Interface", ckInterface.Checked.ToString)
                objDic.Add("Formula", txtExpandFormula.Text.Trim)
                objDic.Add("ScheduleCode", txtScheduleCode.Text.Trim)
                objDic.Add("ScheduleTime", txtScheduleTime.Text.Trim)
                objDic.Add("OnDemandExecute", txtOnDemandExecute.Text.Trim)
                objDic.Add("Active", cbActive.Checked.ToString)

                SessionManager.RecordTransactionCurrentValues = objDic

                LoadTrackerGrids()
            End If
        End Sub
        Private Sub LoadTrackerGrids()
            mcCollection.StoredProcedureParams.Add("@TrackerID", SessionManager.SelectedValueTrackerID)
            mcCollection.StoredProcedureParams.Add("@UserID", SessionManager.UserID)
            Dim strLanguage As String = New System.Globalization.CultureInfo(SessionManager.CulturePref).TwoLetterISOLanguageName.ToUpper
            mcCollection.StoredProcedureParams.Add("@Language", strLanguage)
            mcCollection.DataBind()

            mcVariables.StoredProcedureParams.Add("@TrackerID", SessionManager.SelectedValueTrackerID)
            mcVariables.DataBind()
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

            Select Case SessionManager.TrackerMode.ToString()
                Case "ViewRow", "DeleteRow"
                    pnlOKCancel.Visible = False
                    txtTracker.ReadOnly = True
                    txtTracker.CssClass = "Textbox_Display"
                    txtTrackerOther.ReadOnly = True
                    txtTrackerOther.CssClass = "Textbox_Display"
                    ddlTeam.Visible = False
                    txtTeam.Visible = True
                    ddlSavingsCategory.Visible = False
                    txtSavingsCategory.Visible = True
                    txtUOM.ReadOnly = True
                    txtUOM.CssClass = "Textbox_Display"
                    txtHistoric.ReadOnly = True
                    txtHistoric.CssClass = "Textbox_Display"
                    txtTarget.ReadOnly = True
                    txtTarget.CssClass = "Textbox_Display"
                    txtStartDate.ReadOnly = True
                    txtStartDate.CssClass = "Textbox_Display"
                    imgStartDate.Visible = False
                    txtStartDate_CalendarExtender.Enabled = False
                    txtExpandDescription.ReadOnly = True
                    txtExpandDescription.CssClass = "Textbox_Display"
                    ckInterface.Enabled = False
                    txtExpandFormula.ReadOnly = True
                    txtExpandFormula.CssClass = "Textbox_Display"
                    txtScheduleCode.ReadOnly = True
                    txtScheduleCode.CssClass = "Textbox_Display"
                    txtScheduleTime.ReadOnly = True
                    txtScheduleTime.CssClass = "Textbox_Display"
                    txtOnDemandExecute.ReadOnly = True
                    txtOnDemandExecute.CssClass = "Textbox_Display"
                    cbActive.Enabled = False
            End Select
        End Sub
        Private Function InsertTracker() As Boolean
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

                If ckInterface.Checked Then
                    If txtExpandFormula.Text.Trim.Length = 0 OrElse (txtScheduleCode.Text.Trim.Length = 0 AndAlso txtOnDemandExecute.Text.Trim.Length = 0) Then
                        Master.DisplayError("Formula is required if this Tracker is set to Interface")
                        Return False
                    End If
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

                SessionManager.SelectedValueTrackerID = Trackers.AddTracker(txtTracker.Text.Trim, txtTrackerOther.Text.Trim, ddlTeam.SelectedItem.Value.ToString.Trim, ddlSavingsCategory.SelectedItem.Value, txtUOM.Text.Trim, RegionalConversion.FormatSQLSingle(txtHistoric.Text), RegionalConversion.FormatSQLSingle(txtTarget.Text), RegionalConversion.FormatSQLDate(txtStartDate.Text), txtExpandDescription.Text.Trim, ckInterface.Checked, txtExpandFormula.Text.Trim, strVariables, txtScheduleCode.Text.Trim, txtScheduleTime.Text.Trim, strNextExecuteTime, strOnDemandExecuteTime, cbActive.Checked)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueTrackerID.ToString, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertTracker", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateTracker() As Boolean
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

                If ckInterface.Checked Then
                    If txtExpandFormula.Text.Trim.Length = 0 OrElse (txtScheduleCode.Text.Trim.Length = 0 AndAlso txtOnDemandExecute.Text.Trim.Length = 0) Then
                        Master.DisplayError("Formula is required if this Tracker is set to Interface")
                        Return False
                    End If
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

                Trackers.UpdateTracker(SessionManager.SelectedValueTrackerID, txtTracker.Text.Trim, txtTrackerOther.Text.Trim, ddlTeam.SelectedItem.Value.ToString.Trim, ddlSavingsCategory.SelectedItem.Value, txtUOM.Text.Trim, RegionalConversion.FormatSQLSingle(txtHistoric.Text), RegionalConversion.FormatSQLSingle(txtTarget.Text), RegionalConversion.FormatSQLDate(txtStartDate.Text), txtExpandDescription.Text.Trim, ckInterface.Checked, txtExpandFormula.Text.Trim, strVariables, txtScheduleCode.Text.Trim, txtScheduleTime.Text.Trim, strNextExecuteTime, strOnDemandExecuteTime, cbActive.Checked)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueTrackerID.ToString, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdatePillars", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function DeleteTracker() As Boolean
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
                Trackers.DeleteTracker(SessionManager.SelectedValueTrackerID)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueTrackerID.ToString, "Savings Tracker Deleted", SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - Delete Tracker", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
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
            objDic.Add("Tracker", txtTracker.Text.Trim())
            objDic.Add("TrackerOther", txtTrackerOther.Text.Trim())
            If ddlTeam.SelectedItem IsNot Nothing AndAlso ddlTeam.SelectedItem.Value.ToString.Trim.Length > 0 Then
                objDic.Add("Team", ddlTeam.SelectedItem.Text.Trim)
            Else
                objDic.Add("Team", "")
            End If
            If ddlSavingsCategory.SelectedItem IsNot Nothing Then
                objDic.Add("SavingsCategory", ddlSavingsCategory.SelectedItem.Text.Trim)
            Else
                objDic.Add("SavingsCategory", "")
            End If
            objDic.Add("TrackerUOM", txtUOM.Text.Trim)
            objDic.Add("Historic", txtHistoric.Text)
            objDic.Add("Target", txtTarget.Text)
            objDic.Add("StartPeriod", RegionalConversion.FormatSQLDate(txtStartDate.Text))
            objDic.Add("Description", txtExpandDescription.Text.Trim)
            objDic.Add("Interface", ckInterface.Checked.ToString)
            objDic.Add("Formula", txtExpandFormula.Text.Trim)
            objDic.Add("ScheduleCode", txtScheduleCode.Text.Trim)
            objDic.Add("ScheduleTime", txtScheduleTime.Text.Trim)
            objDic.Add("OnDemandExecute", txtOnDemandExecute.Text.Trim)
            objDic.Add("Active", cbActive.Checked.ToString)

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

                ' Validate Variables
                strCheckFormula = passFormula.Trim
                If strCheckFormula.Contains("[") Then
                    Do Until Not strCheckFormula.Contains("[")
                        If strCheckFormula.Contains("]") Then
                            strVariableHolder = strCheckFormula.Substring(strCheckFormula.IndexOf("["), strCheckFormula.IndexOf("]") - strCheckFormula.IndexOf("[") + 1)
                            strCheckFormula = strCheckFormula.Replace(strVariableHolder, "")

                            If strVariables.Trim.Length > 0 Then strVariables += ","
                            strVariables += strVariableHolder.Replace("[", "").Replace("]", "")
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
                Return True
            Catch ex As Exception
                Master.DisplayErrors(ProgramName & " - ValidateScheduleInfo", ex, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
            End Try
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
#End Region

    End Class
End Namespace
