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
    Partial Class AnomalyActions2
        Inherits ApplicationBase

#Region " Private Variables"
        Private Shared ReadOnly FormName As String = "Anomaly Action"
        Private Shared ReadOnly ProgramName As String = "AnomalyActions2"
        Private Shared ReadOnly DBTableName As String = "AnomalyActions"
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
                lblAnomalyActionID.Text = GetTranslationString("anomalyactionid", lblAnomalyActionID.Text.Replace(":", "")) & ":"
                lblAnomalyCause.Text = GetTranslationString("anomalycause", lblAnomalyCause.Text.Replace(":", "")) & ":"
                lblActionWhat.Text = GetTranslationString("actionwhat", lblActionWhat.Text.Replace(":", "")) & ":"
                lblActionWhere.Text = GetTranslationString("actionwhere", lblActionWhere.Text.Replace(":", "")) & ":"
                lblActionWhy.Text = GetTranslationString("actionwhy", lblActionWhy.Text.Replace(":", "")) & ":"
                lblTargetDate.Text = GetTranslationString("targetdate", lblTargetDate.Text.Replace(":", "")) & ":"
                lblResponsibleUser.Text = GetTranslationString("responsibleuser", lblResponsibleUser.Text.Replace(":", "")) & ":"
                lblActionHow.Text = GetTranslationString("actionhow", lblActionHow.Text.Replace(":", "")) & ":"
                lblContention.Text = GetTranslationString("contentionaction", lblContention.Text.Replace(":", "")) & ":"
                lblActions.Text = GetTranslationString("actions", lblActions.Text.Replace(":", "")) & ":"
                lblClosed.Text = GetTranslationString("closeddate", lblClosed.Text.Replace(":", "")) & ":"
                btnOK.Text = GetTranslationString("ok", btnOK.Text)
                btnCancel.Text = GetTranslationString("cancel", btnCancel.Text)
                btnExit.Text = GetTranslationString("exit", btnExit.Text)
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
        Private Sub LoadEditModeJavaScripts()
            If pnlSGI.Visible Then
                Dim myTabArray() As Object = {ddlAnomalyCause, _
                                              txtExpandActionWhat, _
                                              txtActionWhere, _
                                              txtExpandActionWhy, _
                                              txtTargetDate, _
                                              txtExpandActionHow, _
                                              ckContention, _
                                              ddlResponsibleUser, _
                                              txtExpandActions, _
                                              txtClosedDate}

                Dim TabKeyDownArr() As String = {Tab(txtExpandActionWhat, txtClosedDate, "No"), _
                                                 Tab(txtActionWhere, ddlAnomalyCause, "No"), _
                                                 Tab(txtExpandActionWhy, txtExpandActionWhat, "No"), _
                                                 Tab(txtTargetDate, txtActionWhere, "No"), _
                                                 Tab(txtExpandActionHow, txtExpandActionWhy, "No"), _
                                                 Tab(ckContention, txtTargetDate, "No"), _
                                                 Tab(ddlResponsibleUser, txtExpandActionHow, "No"), _
                                                 Tab(txtExpandActions, ckContention, "No"), _
                                                 Tab(txtClosedDate, ddlResponsibleUser, "No"), _
                                                 Tab(ddlAnomalyCause, txtExpandActions, "No")}

                AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
            Else
                Dim myTabArray() As Object = {ddlAnomalyCause, _
                                              txtExpandActionWhat, _
                                              txtActionWhere, _
                                              txtExpandActionWhy, _
                                              txtTargetDate, _
                                              txtExpandActionHow, _
                                              ddlResponsibleUser, _
                                              txtExpandActions, _
                                              txtClosedDate}

                Dim TabKeyDownArr() As String = {Tab(txtExpandActionWhat, txtClosedDate, "No"), _
                                                 Tab(txtActionWhere, ddlAnomalyCause, "No"), _
                                                 Tab(txtExpandActionWhy, txtExpandActionWhat, "No"), _
                                                 Tab(txtTargetDate, txtActionWhere, "No"), _
                                                 Tab(txtExpandActionHow, txtExpandActionWhy, "No"), _
                                                 Tab(ddlResponsibleUser, txtTargetDate, "No"), _
                                                 Tab(txtExpandActions, txtExpandActionHow, "No"), _
                                                 Tab(txtClosedDate, ddlResponsibleUser, "No"), _
                                                 Tab(ddlAnomalyCause, txtExpandActions, "No")}

                AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
            End If
        End Sub
        Private Sub LoadAddModeJavaScripts()
            If pnlSGI.Visible Then
                Dim myTabArray() As Object = {ddlAnomalyCause, _
                                              txtExpandActionWhat, _
                                              txtActionWhere, _
                                              txtExpandActionWhy, _
                                              txtTargetDate, _
                                              txtExpandActionHow, _
                                              ckContention, _
                                              ddlResponsibleUser}

                Dim TabKeyDownArr() As String = {Tab(txtExpandActionWhat, ddlResponsibleUser, "No"), _
                                                 Tab(txtActionWhere, ddlAnomalyCause, "No"), _
                                                 Tab(txtExpandActionWhy, txtExpandActionWhat, "No"), _
                                                 Tab(txtTargetDate, txtActionWhere, "No"), _
                                                 Tab(txtExpandActionHow, txtExpandActionWhy, "No"), _
                                                 Tab(ckContention, txtTargetDate, "No"), _
                                                 Tab(ddlResponsibleUser, txtExpandActionHow, "No"), _
                                                 Tab(ddlAnomalyCause, ckContention, "No")}

                AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
            Else
                Dim myTabArray() As Object = {ddlAnomalyCause, _
                                              txtExpandActionWhat, _
                                              txtActionWhere, _
                                              txtExpandActionWhy, _
                                              txtTargetDate, _
                                              txtExpandActionHow, _
                                              ddlResponsibleUser}

                Dim TabKeyDownArr() As String = {Tab(txtExpandActionWhat, ddlResponsibleUser, "No"), _
                                                 Tab(txtActionWhere, ddlAnomalyCause, "No"), _
                                                 Tab(txtExpandActionWhy, txtExpandActionWhat, "No"), _
                                                 Tab(txtTargetDate, txtActionWhere, "No"), _
                                                 Tab(txtExpandActionHow, txtExpandActionWhy, "No"), _
                                                 Tab(ddlResponsibleUser, txtTargetDate, "No"), _
                                                 Tab(ddlAnomalyCause, txtExpandActionHow, "No")}

                AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
            End If
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

            Master.HeaderMessage = GetTranslationString(FormName, FormName) & " - " & GetTranslationString(SessionManager.AnomalyActionMode.Replace("Row", ""), SessionManager.AnomalyActionMode.Replace("Row", ""))
            Master.IconImage = Request.ApplicationPath + "/images/data_information.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            mcAnomaly.StoredProcedureParams.Add("@AnomalyID", SessionManager.SelectedValueAnomalyID)
            mcAnomaly.StoredProcedureParams.Add("@UserID", SessionManager.UserID)
            mcAnomaly.GridColumns(5).DataFormatString = "{0:yyyy/MM/dd}"
            mcAnomaly.GridColumns(8).DataFormatString = "{0:yyyy/MM/dd}"

            If Not Page.IsPostBack Then
                Dim objDT As DataTable = SiteMaster.GetSiteMasterAttributesBySite(SessionManager.WorkingSiteID)
                If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                    If objDT.Rows(0)("ShowAnomalySGI") IsNot DBNull.Value AndAlso Convert.ToBoolean(objDT.Rows(0)("ShowAnomalySGI")) Then
                        pnlSGI.Visible = True
                    End If
                End If

                mcAnomaly.DataBind(True)

                LoadCultureTranslations()
                BindDropDownLists()

                If Not AnomalyMaster.AnomalyActionRequiresCause(SessionManager.SelectedValueAnomalyID) Then
                    reqAnomalyCause.Enabled = False
                End If

                Select Case SessionManager.AnomalyActionMode
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        pnlOKCancel.Visible = True
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Anomaly Action.');")
                        TransactionHistory1.LockControl = True
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        txtAnomalyActionID.Text = "New"
                        LoadAddModeJavaScripts()
                        UnEnableRecords()
                        ddlAnomalyCause.Focus()
                    Case "EditRow"
                        LoadEditModeJavaScripts()
                        LoadSelectedRecord()
                        UnEnableRecords()
                        txtExpandActions.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyActions1"), False)
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
            Select Case SessionManager.AnomalyActionMode
                Case "AddRow"
                    blnSuccess = InsertAnomalyAction()
                Case "EditRow"
                    blnSuccess = UpdateAnomalyAction()
                Case "DeleteRow"
                    blnSuccess = DeleteAnomalyAction()
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueAnomalyActionID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.AnomalyActionMode)
                Dim strProgram As String = "AnomalyActions1"
                If SessionManager.CallingProgram.Trim.Length > 0 AndAlso String.IsNullOrEmpty(SessionManager.MasterControlExitProgram) Then
                    strProgram = SessionManager.CallingProgram
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CallingProgram)
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueAnomalyActionID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.AnomalyActionMode)
            Dim strProgram As String = "AnomalyActions1"
            If SessionManager.CallingProgram.Trim.Length > 0 AndAlso String.IsNullOrEmpty(SessionManager.MasterControlExitProgram) Then
                strProgram = SessionManager.CallingProgram
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CallingProgram)
            End If
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strProgram), False)
        End Sub
        Protected Sub ddlUserSite_SelectedIndexChanged(ByVal sender As Object, ByVal e As System.EventArgs) Handles ddlUserSite.SelectedIndexChanged
            LoadResponsibleUserDDL()
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
                AnomalyCauses.GetAnomalyCausesByAnomalyID(ddlAnomalyCause, SessionManager.SelectedValueAnomalyID)
                ddlAnomalyCause.Items.Insert(0, "")

                BindUserSites()

                LoadResponsibleUserDDL()
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindDropDownLists", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                Return
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

                SiteMaster.SelectSiteMasterList(ddlUserSite)
                If SessionManager.WorkingSiteID > 0 Then
                    objItem = ddlUserSite.Items.FindByValue(SessionManager.WorkingSiteID)
                Else
                    objItem = ddlUserSite.Items.FindByValue(UserMaster.GetUserSite(SessionManager.UserID))
                End If
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                Else
                    If ddlUserSite.Items.Count > 0 Then
                        ddlUserSite.Items(0).Selected = True
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

            Dim objDT As DataTable = AnomalyActions.SelectAnomalyActionByID(SessionManager.SelectedValueAnomalyActionID)
            If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                Dim dtRow As DataRow = objDT.Rows(0)
                Dim objItem As ListItem = Nothing

                txtAnomalyActionID.Text = SessionManager.SelectedValueAnomalyActionID.ToString
                objItem = ddlAnomalyCause.Items.FindByValue(dtRow("AnomalyCauseID").ToString)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                    txtAnomalyCause.Text = objItem.Text
                End If
                txtExpandActionWhat.Text = dtRow("ActionWhat").ToString
                txtActionWhere.Text = dtRow("ActionWhere").ToString
                txtExpandActionWhy.Text = dtRow("ActionWhy").ToString
                If IsDate(dtRow("TargetDate").ToString) Then
                    txtTargetDate.Text = Convert.ToDateTime(dtRow("TargetDate")).ToString(SessionManager.DateFormat)
                Else
                    txtTargetDate.Text = dtRow("TargetDate").ToString
                End If
                txtExpandActionHow.Text = dtRow("ActionHow").ToString
                If dtRow("ContentionAction") IsNot DBNull.Value Then
                    ckContention.Checked = Convert.ToBoolean(dtRow("ContentionAction"))
                End If
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
                txtExpandActions.Text = dtRow("Actions").ToString
                If IsDate(dtRow("ClosedDate").ToString) Then
                    txtClosedDate.Text = Convert.ToDateTime(dtRow("ClosedDate")).ToString(SessionManager.DateFormat)
                Else
                    txtClosedDate.Text = dtRow("ClosedDate").ToString
                End If
                If txtClosedDate.Text.Trim.Length > 0 Then
                    If Convert.ToBoolean(dtRow("Cancelled")) Then
                        rblCancelled.SelectedValue = 1
                    Else
                        rblCancelled.SelectedValue = 0
                    End If
                End If

                TransactionHistory1.TableName = DBTableName
                TransactionHistory1.RecordID = SessionManager.SelectedValueAnomalyActionID.ToString

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("AnomalyCause", txtAnomalyCause.Text.Trim())
                objDic.Add("ActionWhat", txtExpandActionWhat.Text.Trim)
                objDic.Add("ActionWhere", txtActionWhere.Text.Trim)
                objDic.Add("ActionWhy", txtExpandActionWhy.Text.Trim)
                objDic.Add("TargetDate", txtTargetDate.Text.Trim)
                objDic.Add("ActionHow", txtExpandActionHow.Text.Trim)
                objDic.Add("ContentionAction", ckContention.Checked.ToString)
                objDic.Add("ResponsibleUser", txtResponsibleUser.Text.Trim)
                objDic.Add("Actions", txtExpandActions.Text.Trim)
                objDic.Add("ClosedDate", txtClosedDate.Text.Trim)

                SessionManager.RecordTransactionCurrentValues = objDic
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

            Select Case SessionManager.AnomalyActionMode
                Case "ViewRow", "DeleteRow"
                    pnlOKCancel.Visible = False
                    ddlAnomalyCause.Visible = False
                    txtAnomalyCause.Visible = True
                    txtExpandActionWhat.ReadOnly = True
                    txtExpandActionWhat.CssClass = "Textbox_Display"
                    txtActionWhere.ReadOnly = True
                    txtActionWhere.CssClass = "Textbox_Display"
                    txtExpandActionWhy.ReadOnly = True
                    txtExpandActionWhy.CssClass = "Textbox_Display"
                    txtTargetDate.ReadOnly = True
                    txtTargetDate.CssClass = "Textbox_Display"
                    imgTargetDate.Visible = False
                    txtTargetDate_CalendarExtender.Enabled = False
                    txtExpandActionHow.ReadOnly = True
                    txtExpandActionHow.CssClass = "Textbox_Display"
                    ckContention.Enabled = False
                    ddlResponsibleUser.Visible = False
                    txtResponsibleUser.Visible = True
                    ddlUserSite.Visible = False
                    txtExpandActions.ReadOnly = True
                    txtExpandActions.CssClass = "Textbox_Display"
                    txtClosedDate.ReadOnly = True
                    txtClosedDate.CssClass = "Textbox_Display"
                    imgClosedDate.Visible = False
                    txtClosedDate_CalendarExtender.Enabled = False
                    rblCancelled.Enabled = False
                Case "EditRow"
                    Dim objDT As DataTable = AnomalyActions.SelectAnomalyActionAuthority(SessionManager.SelectedValueAnomalyActionID)
                    If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                        Dim dtRow As DataRow = objDT.Rows(0)

                        If dtRow("CreatedUserID").ToString = SessionManager.UserID OrElse dtRow("ResponsibleUserID").ToString = SessionManager.UserID Then
                            'User can edit all fields
                            Return
                        End If
                    End If

                    ddlAnomalyCause.Visible = False
                    txtAnomalyCause.Visible = True
                    txtExpandActionWhat.ReadOnly = True
                    txtExpandActionWhat.CssClass = "Textbox_Display"
                    txtActionWhere.ReadOnly = True
                    txtActionWhere.CssClass = "Textbox_Display"
                    txtExpandActionWhy.ReadOnly = True
                    txtExpandActionWhy.CssClass = "Textbox_Display"
                    txtTargetDate.ReadOnly = True
                    txtTargetDate.CssClass = "Textbox_Display"
                    imgTargetDate.Visible = False
                    txtTargetDate_CalendarExtender.Enabled = False
                    txtExpandActionHow.ReadOnly = True
                    txtExpandActionHow.CssClass = "Textbox_Display"
                    ckContention.Enabled = False
                    ddlResponsibleUser.Visible = False
                    txtResponsibleUser.Visible = True
                    ddlUserSite.Visible = False
                Case "AddRow"
                    lblActions.Visible = False
                    txtExpandActions.Visible = False
                    lblClosed.Visible = False
                    txtClosedDate.Visible = False
                    imgClosedDate.Visible = False
                    txtClosedDate_CalendarExtender.Enabled = False
                    rblCancelled.Visible = False
            End Select
        End Sub
        Private Function InsertAnomalyAction() As Boolean
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

                Dim iCauseID = -1
                Dim strTargetDate As String = RegionalConversion.FormatSQLDate(txtTargetDate.Text)
                Dim strResponsibleUserID As String = ""
                Dim strClosedDate As String = RegionalConversion.FormatSQLDate(txtClosedDate.Text)
                Dim bCancelled As Boolean = False
                If ddlAnomalyCause.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlAnomalyCause.SelectedItem.Value) Then
                    iCauseID = ddlAnomalyCause.SelectedItem.Value
                End If
                If ddlResponsibleUser.SelectedItem IsNot Nothing AndAlso ddlResponsibleUser.SelectedItem.Value.ToString.Trim.Length > 0 Then
                    strResponsibleUserID = ddlResponsibleUser.SelectedItem.Value
                End If

                If strClosedDate.Trim.Length > 0 Then
                    If txtExpandActions.Text.Trim.Length = 0 Then
                        Master.DisplayError("You must enter Actions text to Close an Action")
                        Return False
                    ElseIf rblCancelled.SelectedItem Is Nothing Then
                        Master.DisplayError("You must select a status to Close an Action")
                        Return False
                    End If

                    bCancelled = rblCancelled.SelectedValue
                End If

                Dim iAnomalyActionID As Integer = AnomalyActions.AddAnomalyAction(SessionManager.SelectedValueAnomalyID, iCauseID, txtExpandActionWhat.Text.Trim, txtActionWhere.Text.Trim, txtExpandActionWhy.Text.Trim, strTargetDate, txtExpandActionHow.Text.Trim, strResponsibleUserID, txtExpandActions.Text.Trim, strClosedDate, bCancelled, ckContention.Checked)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, iAnomalyActionID.ToString, strChangeLog, SessionManager.UserID)

                If (Not String.IsNullOrEmpty(strResponsibleUserID)) AndAlso strResponsibleUserID <> SessionManager.UserID Then
                    Dim strEmail As String = UserMaster.GetUserEmail(strResponsibleUserID)
                    If Not String.IsNullOrEmpty(strEmail) Then
                        Dim strSubject As String = GetTranslationString("Anomaly Action created for Anomaly") & ": "
                        strSubject += mcAnomaly.MasterControlGrid.DataKeys(0)("Anomaly").ToString

                        Dim strBody As String = strSubject & "<br /><br />"
                        strBody += GetTranslationString("Action") + " - <br />"
                        strBody += GetTranslationString("What") + " - "
                        strBody += " " + txtExpandActionWhat.Text.Trim + "<br />"
                        strBody += GetTranslationString("Where") + " - "
                        strBody += " " + txtActionWhere.Text.Trim + "<br />"
                        strBody += GetTranslationString("When") + " - "
                        strBody += " " + txtTargetDate.Text.Trim + "<br />"

                        Dim strURL As String = "http://" & ConfigurationManager.AppSettings("ApplicationServerDNS").ToString & "/aplus/login.aspx"
                        strURL += "?auto=y&anomalyaction=" + iAnomalyActionID.ToString()
                        strURL += "&anomaly=" + SessionManager.SelectedValueAnomalyID.ToString()
                        strBody += "<a href='" + strURL + "'>" + GetTranslationString("Click Here to Process Anomaly Action")
                        strBody += "<br /><br />"
                        strURL = "http://" & ConfigurationManager.AppSettings("ApplicationServerDNS").ToString & "/aplus/login.aspx?auto=y"
                        strBody += "<a href='" + strURL + "'>" + GetTranslationString("Click Here to login to APlus App")

                        SendEmail(strEmail, ConfigurationManager.AppSettings("SendEmailFrom").ToString, strSubject, strBody)
                    End If
                End If

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertAnomalyAction", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateAnomalyAction() As Boolean
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

                Dim iCauseID = -1
                Dim strTargetDate As String = RegionalConversion.FormatSQLDate(txtTargetDate.Text)
                Dim strResponsibleUserID As String = ""
                Dim strClosedDate As String = RegionalConversion.FormatSQLDate(txtClosedDate.Text)
                Dim bCancelled As Boolean = False
                If ddlAnomalyCause.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlAnomalyCause.SelectedItem.Value) Then
                    iCauseID = ddlAnomalyCause.SelectedItem.Value
                End If
                If ddlResponsibleUser.SelectedItem IsNot Nothing AndAlso ddlResponsibleUser.SelectedItem.Value.ToString.Trim.Length > 0 Then
                    strResponsibleUserID = ddlResponsibleUser.SelectedItem.Value
                End If

                If strClosedDate.Trim.Length > 0 Then
                    If txtExpandActions.Text.Trim.Length = 0 Then
                        Master.DisplayError("You must enter Actions text to Close an Action")
                        Return False
                    ElseIf rblCancelled.SelectedItem Is Nothing Then
                        Master.DisplayError("You must select a status to Close an Action")
                        Return False
                    End If

                    bCancelled = rblCancelled.SelectedValue
                End If

                AnomalyActions.UpdateAnomalyAction(SessionManager.SelectedValueAnomalyActionID, iCauseID, txtExpandActionWhat.Text.Trim, txtActionWhere.Text.Trim, txtExpandActionWhy.Text.Trim, strTargetDate, txtExpandActionHow.Text.Trim, strResponsibleUserID, txtExpandActions.Text.Trim, strClosedDate, bCancelled, ckContention.Checked)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueAnomalyActionID.ToString, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateAnomalyAction", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function DeleteAnomalyAction() As Boolean
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
                AnomalyActions.DeleteAnomalyAction(SessionManager.SelectedValueAnomalyActionID)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueAnomalyActionID.ToString, "Anomaly Action Deleted", SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteAnomalyAction", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
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
            If ddlAnomalyCause.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlAnomalyCause.SelectedItem.Value) Then
                objDic.Add("AnomalyCause", ddlAnomalyCause.SelectedItem.Text)
            Else
                objDic.Add("AnomalyCause", "")
            End If
            objDic.Add("ActionWhat", txtExpandActionWhat.Text.Trim)
            objDic.Add("ActionWhere", txtActionWhere.Text.Trim)
            objDic.Add("ActionWhy", txtExpandActionWhy.Text.Trim)
            objDic.Add("TargetDate", txtTargetDate.Text.Trim)
            objDic.Add("ActionHow", txtExpandActionHow.Text.Trim)
            objDic.Add("ContentionAction", ckContention.Checked.ToString)
            If ddlResponsibleUser.SelectedItem IsNot Nothing AndAlso ddlResponsibleUser.SelectedItem.Value.ToString.Trim.Length > 0 Then
                objDic.Add("ResponsibleUser", ddlResponsibleUser.SelectedItem.Text)
            Else
                objDic.Add("ResponsibleUser", "")
            End If
            objDic.Add("Actions", txtExpandActions.Text.Trim)
            objDic.Add("ClosedDate", txtClosedDate.Text.Trim)

            Return objDic
        End Function
#End Region

    End Class
End Namespace
