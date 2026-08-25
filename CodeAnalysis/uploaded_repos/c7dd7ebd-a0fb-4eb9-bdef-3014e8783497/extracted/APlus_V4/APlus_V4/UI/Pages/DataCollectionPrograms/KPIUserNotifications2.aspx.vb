#Region " Imports"
Imports System.IO
Imports System.Collections.Generic
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class KPIUserNotifications2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "KPI Notifications"
        Private Shared ReadOnly ProgramName As String = "KPIUserNotifications2"
        Private Shared ReadOnly DBTableName As String = "KPIUserNotifications"
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
                lblUser.Text = GetTranslationString("user", lblUser.Text.Replace(":", "")) & ":"
                lblKPIValueEntry.Text = GetTranslationString("kpivalueentry", lblKPIValueEntry.Text.Replace(":", "")) & ":"
                lblKPIValueReminder.Text = GetTranslationString("kpivaluereminder", lblKPIValueReminder.Text.Replace(":", "")) & ":"
                lblKPITargetEntry.Text = GetTranslationString("kpitargetentry", lblKPITargetEntry.Text.Replace(":", "")) & ":"
                lblKPITargetReminder.Text = GetTranslationString("kpitargetreminder", lblKPITargetReminder.Text.Replace(":", "")) & ":"
                lblKPIDeviation.Text = GetTranslationString("kpideviation", lblKPIDeviation.Text.Replace(":", "")) & ":"
                lblAnomalyPending.Text = GetTranslationString("anomalypending", lblAnomalyPending.Text.Replace(":", "")) & ":"
                lblAnomalyPendingReminder.Text = GetTranslationString("anomalypendingreminder", lblAnomalyPendingReminder.Text.Replace(":", "")) & ":"
                lblAnomalyActions.Text = GetTranslationString("anomalyactions", lblAnomalyActions.Text.Replace(":", "")) & ":"
                lblAnomalyActionsReminder.Text = GetTranslationString("anomalyactionsreminder", lblAnomalyActionsReminder.Text.Replace(":", "")) & ":"
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
        Private Sub LoadAddModeJavaScripts()
            Dim myTabArray() As Object = {ddlUser, _
                                          ckKPIValueEntry, _
                                          ckKPIValueReminder, _
                                          ckKPITargetEntry, _
                                          ckKPITargetReminder, _
                                          ckKPIDeviation, _
                                          ckAnomalyPending, _
                                          ckAnomalyPendingReminder, _
                                          ckAnomalyActions, _
                                          ckAnomalyActionsReminder}

            Dim TabKeyDownArr() As String = {Tab(ckKPIValueEntry, ckAnomalyActionsReminder, "No"), _
                                             Tab(ckKPIValueReminder, ddlUser, "No"), _
                                             Tab(ckKPITargetEntry, ckKPIValueEntry, "No"), _
                                             Tab(ckKPITargetReminder, ckKPIValueReminder, "No"), _
                                             Tab(ckKPIDeviation, ckKPITargetEntry, "No"), _
                                             Tab(ckAnomalyPending, ckKPITargetReminder, "No"), _
                                             Tab(ckAnomalyPendingReminder, ckKPIDeviation, "No"), _
                                             Tab(ckAnomalyActions, ckAnomalyPending, "No"), _
                                             Tab(ckAnomalyActionsReminder, ckAnomalyPendingReminder, "No"), _
                                             Tab(ddlUser, ckAnomalyActions, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {ckKPIValueEntry, _
                                          ckKPIValueReminder, _
                                          ckKPITargetEntry, _
                                          ckKPITargetReminder, _
                                          ckKPIDeviation, _
                                          ckAnomalyPending, _
                                          ckAnomalyPendingReminder, _
                                          ckAnomalyActions, _
                                          ckAnomalyActionsReminder}

            Dim TabKeyDownArr() As String = {Tab(ckKPIValueReminder, ckAnomalyActionsReminder, "No"), _
                                             Tab(ckKPITargetEntry, ckKPIValueEntry, "No"), _
                                             Tab(ckKPITargetReminder, ckKPIValueReminder, "No"), _
                                             Tab(ckKPIDeviation, ckKPITargetEntry, "No"), _
                                             Tab(ckAnomalyPending, ckKPITargetReminder, "No"), _
                                             Tab(ckAnomalyPendingReminder, ckKPIDeviation, "No"), _
                                             Tab(ckAnomalyActions, ckAnomalyPending, "No"), _
                                             Tab(ckAnomalyActionsReminder, ckAnomalyPendingReminder, "No"), _
                                             Tab(ckKPIValueEntry, ckAnomalyActions, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
#End Region

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, ProgramName, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Master.IconImage = Request.ApplicationPath + "/images/boss.gif"
            Master.HeaderMessage = GetTranslationString(FormName, FormName)
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                LoadCultureTranslations()

                BindSites()
                BindKPI()
                BindUsers()

                Select Case SessionManager.Mode
                    Case "EditRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        LoadEditModeJavaScripts()
                        ckKPIValueEntry.Focus()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this KPI Notification.');")
                        TransactionHistory1.LockControl = True
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        LoadAddModeJavaScripts()

                        If Not String.IsNullOrEmpty(SessionManager.SelectedValueUser) Then
                            Dim objItem As ListItem = ddlUser.Items.FindByValue(SessionManager.SelectedValueUser)
                            If objItem IsNot Nothing Then
                                objItem.Selected = True
                                txtUser.Text = objItem.Text
                            Else
                                objItem = New ListItem
                                objItem.Value = SessionManager.SelectedValueUser
                                Dim strHolder As String = UserMaster.GetUserFullNameLastNameFirst(SessionManager.SelectedValueUser)
                                If strHolder.Trim.Length > 0 Then
                                    strHolder += " (" & SessionManager.SelectedValueUser & ")"
                                    objItem.Text = strHolder
                                Else
                                    objItem.Text = SessionManager.SelectedValueUser
                                End If
                            End If

                            ddlUser.Visible = False
                            txtUser.Visible = True
                            ddlSite.Visible = False
                        ElseIf SessionManager.SelectedValueKPIID > 0 Then
                            Dim objItem As ListItem = ddlKPI.Items.FindByValue(SessionManager.SelectedValueKPIID)
                            If objItem IsNot Nothing Then
                                objItem.Selected = True
                                txtKPI.Text = objItem.Text

                                ddlKPI.Visible = False
                                txtKPI.Visible = True
                            End If
                        End If

                        ckKPIValueEntry.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPIUserNotifications1"), False)
                End Select
            End If
        End Sub
        Protected Sub ddlSite_SelectedIndexChanged(ByVal sender As Object, ByVal e As System.EventArgs) Handles ddlSite.SelectedIndexChanged
            BindUsers()
        End Sub
        Private Sub btnOK_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim blnSuccess As Boolean
            Select Case SessionManager.Mode
                Case "EditRow"
                    blnSuccess = UpdateKPINotification()
                Case "DeleteRow"
                    blnSuccess = DeleteKPINotification()
                Case "AddRow"
                    blnSuccess = InsertKPINotification()
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue3)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue4)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Mode)
                Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar & (ProgramSecurity.GetProgramURL("KPIUserNotifications1")), False)
            End If
        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click, btnCancel.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue3)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue4)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Mode)
            Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar & (ProgramSecurity.GetProgramURL("KPIUserNotifications1")), False)
        End Sub
#End Region

#Region " Custom methods"
        Private Sub LoadSelectedRecord()
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
                Dim objDT As DataTable = KPIUserNotifications.SelectKPIUserNotificationByKey(SessionManager.SelectedValue3, SessionManager.SelectedValue4)
                If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                    Dim objItem As ListItem
                    Dim dtRow As DataRow = objDT.Rows(0)

                    objItem = ddlKPI.Items.FindByValue(dtRow("KPIID").ToString)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                        txtKPI.Text = objItem.Text
                    End If
                    objItem = ddlUser.Items.FindByValue(dtRow("UserID").ToString)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                        txtUser.Text = objItem.Text
                    Else
                        objItem = New ListItem(UserMaster.GetUserFullName(dtRow("UserID").ToString) & " (" & dtRow("UserID").ToString & ")", dtRow("UserID").ToString)
                        ddlUser.Items.Insert(1, objItem)
                        objItem.Selected = True
                        txtUser.Text = objItem.Text
                    End If

                    ckKPIValueEntry.Checked = Convert.ToBoolean(dtRow("KPIValueEntry"))
                    ckKPIValueReminder.Checked = Convert.ToBoolean(dtRow("KPIValueEntryReminder"))
                    ckKPITargetEntry.Checked = Convert.ToBoolean(dtRow("KPITargetEntry"))
                    ckKPITargetReminder.Checked = Convert.ToBoolean(dtRow("KPITargetEntryReminder"))
                    ckKPIDeviation.Checked = Convert.ToBoolean(dtRow("KPIDeviation"))
                    ckAnomalyPending.Checked = Convert.ToBoolean(dtRow("AnomalyPending"))
                    ckAnomalyPendingReminder.Checked = Convert.ToBoolean(dtRow("AnomalyPendingReminder"))
                    ckAnomalyActions.Checked = Convert.ToBoolean(dtRow("AnomalyActions"))
                    ckAnomalyActionsReminder.Checked = Convert.ToBoolean(dtRow("AnomalyActionsReminder"))
                End If

                If SessionManager.RecordTransactionCurrentValues IsNot Nothing Then
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RecordTransactionCurrentValues)
                End If
                TransactionHistory1.TableName = DBTableName
                TransactionHistory1.RecordID = SessionManager.SelectedValue3 & "," & SessionManager.SelectedValue4

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("KPI", txtKPI.Text.Trim)
                objDic.Add("User", txtUser.Text.Trim)
                objDic.Add("KPIValueEntry", ckKPIValueEntry.Checked.ToString)
                objDic.Add("KPIValueEntryReminder", ckKPIValueReminder.Checked.ToString)
                objDic.Add("KPITargetEntry", ckKPITargetEntry.Checked.ToString)
                objDic.Add("KPITargetEntryReminder", ckKPITargetReminder.Checked.ToString)
                objDic.Add("KPIDeviation", ckKPIDeviation.Checked.ToString)
                objDic.Add("AnomalyPending", ckAnomalyPending.Checked.ToString)
                objDic.Add("AnomalyPendingReminder", ckAnomalyPendingReminder.Checked.ToString)
                objDic.Add("AnomalyActions", ckAnomalyActions.Checked.ToString)
                objDic.Add("AnomalyActionsReminder", ckAnomalyActionsReminder.Checked.ToString)

                SessionManager.RecordTransactionCurrentValues = objDic
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindSites()
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
                Master.DisplayErrors(ProgramName & " - BindSites", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindKPI()
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
                KPIMaster.GetKPISiteList(ddlKPI)
                ddlKPI.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindKPI", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindUsers()
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
                ddlUser.Items.Clear()

                If ddlSite.SelectedItem IsNot Nothing Then
                    UserMaster.SelectUserNameList(ddlSite.SelectedItem.Value, True, ddlUser)
                Else
                    UserMaster.SelectUserNameList(SessionManager.WorkingSiteID, True, ddlUser)
                End If

                ddlUser.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindTeams", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub UnEnableRecords()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Select Case SessionManager.Mode
                Case "EditRow"
                    ddlKPI.Visible = False
                    txtKPI.Visible = True
                    ddlUser.Visible = False
                    txtUser.Visible = True
                    ddlSite.Visible = False
                Case "DeleteRow"
                    ddlKPI.Visible = False
                    txtKPI.Visible = True
                    ddlUser.Visible = False
                    txtUser.Visible = True
                    ddlSite.Visible = False
                    ckKPIValueEntry.Enabled = False
                    ckKPIValueReminder.Enabled = False
                    ckKPITargetEntry.Enabled = False
                    ckKPITargetReminder.Enabled = False
                    ckKPIDeviation.Enabled = False
                    ckAnomalyPending.Enabled = False
                    ckAnomalyPendingReminder.Enabled = False
                    ckAnomalyActions.Enabled = False
                    ckAnomalyActionsReminder.Enabled = False
            End Select
        End Sub
        Private Function InsertKPINotification() As Boolean
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
                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                KPIUserNotifications.InsertKPIUserNotifications(ddlKPI.SelectedItem.Value, ddlUser.SelectedItem.Value.ToString, ckKPIValueEntry.Checked, ckKPIValueReminder.Checked, ckKPITargetEntry.Checked, ckKPITargetReminder.Checked, ckKPIDeviation.Checked, ckAnomalyPending.Checked, ckAnomalyPendingReminder.Checked, ckAnomalyActions.Checked, ckAnomalyActionsReminder.Checked)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, ddlKPI.SelectedItem.Value.ToString & "," & ddlUser.SelectedItem.Value.ToString, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertKPINotification", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateKPINotification() As Boolean
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
                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                KPIUserNotifications.UpdateKPIUserNotifications(SessionManager.SelectedValue3, SessionManager.SelectedValue4, ckKPIValueEntry.Checked, ckKPIValueReminder.Checked, ckKPITargetEntry.Checked, ckKPITargetReminder.Checked, ckKPIDeviation.Checked, ckAnomalyPending.Checked, ckAnomalyPendingReminder.Checked, ckAnomalyActions.Checked, ckAnomalyActionsReminder.Checked)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValue3 & "," & SessionManager.SelectedValue4, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateKPINotification", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function DeleteKPINotification() As Boolean
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
                KPIUserNotifications.DeleteKPITeamMaster(SessionManager.SelectedValue3, SessionManager.SelectedValue4)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValue3 & "," & SessionManager.SelectedValue4, "KPI User Notification Deleted", SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteKPINotification", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
        End Function
        Private Function GetUpdatedValues() As Dictionary(Of String, String)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim objDic As New Dictionary(Of String, String)
            objDic.Add("KPI", ddlKPI.SelectedItem.Text.Trim)
            objDic.Add("User", ddlUser.SelectedItem.Text.Trim)
            objDic.Add("KPIValueEntry", ckKPIValueEntry.Checked.ToString)
            objDic.Add("KPIValueEntryReminder", ckKPIValueReminder.Checked.ToString)
            objDic.Add("KPITargetEntry", ckKPITargetEntry.Checked.ToString)
            objDic.Add("KPITargetEntryReminder", ckKPITargetReminder.Checked.ToString)
            objDic.Add("KPIDeviation", ckKPIDeviation.Checked.ToString)
            objDic.Add("AnomalyPending", ckAnomalyPending.Checked.ToString)
            objDic.Add("AnomalyPendingReminder", ckAnomalyPendingReminder.Checked.ToString)
            objDic.Add("AnomalyActions", ckAnomalyActions.Checked.ToString)
            objDic.Add("AnomalyActionsReminder", ckAnomalyActionsReminder.Checked.ToString)

            Return objDic
        End Function
#End Region

    End Class
End Namespace

