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
    Partial Class TrackerVariables2
        Inherits ApplicationBase

#Region " Private Variables"
        Private Shared ReadOnly FormName As String = "Tracker Variables"
        Private Shared ReadOnly ProgramName As String = "TrackerVariables2"
        Private Shared ReadOnly DBTableName As String = "TrackerVariables"
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
                lblVariableID.Text = GetTranslationString("trackervariableid", lblVariableID.Text.Replace(":", "")) & ":"
                lblTrackerVariable.Text = GetTranslationString("trackervariable", lblTrackerVariable.Text.Replace(":", "")) & ":"
                lblValue.Text = GetTranslationString("variablevalue", lblValue.Text.Replace(":", "")) & ":"
                lblSite.Text = GetTranslationString("site", lblSite.Text.Replace(":", "")) & ":"
                lblInterface.Text = GetTranslationString("interface", lblInterface.Text.Replace(":", "")) & ":"
                lblFormula.Text = GetTranslationString("formula", lblFormula.Text.Replace(":", "")) & ":"
                lblScheduleCode.Text = GetTranslationString("schedulecode", lblScheduleCode.Text.Replace(":", "")) & ":"
                lblScheduleTime.Text = GetTranslationString("scheduletime", lblScheduleTime.Text.Replace(":", "")) & ":"
                lblNextExecution.Text = GetTranslationString("nextexecution", lblNextExecution.Text.Replace(":", "")) & ":"
                lblLastExecution.Text = GetTranslationString("lastexecution", lblLastExecution.Text.Replace(":", "")) & ":"
                lblLastExecutionSuccessful.Text = GetTranslationString("lastexecutionsuccessful", lblLastExecutionSuccessful.Text.Replace(":", "")) & ":"
                lblOnDemandExecute.Text = GetTranslationString("ondemandexecute", lblOnDemandExecute.Text.Replace(":", "")) & ":"
                btnOK.Text = GetTranslationString("ok", btnOK.Text)
                btnCancel.Text = GetTranslationString("cancel", btnCancel.Text)
                btnExit.Text = GetTranslationString("exit", btnExit.Text)
                lblSavingsTypesHeader.Text = GetTranslationString("savingstrackers", lblSavingsTypesHeader.Text)
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
            Dim myTabArray() As Object = {txtTrackerVariable, _
                                          txtVariableValue, _
                                          ddlSite, _
                                          ckInterface, _
                                          txtExpandFormula, _
                                          txtScheduleCode, _
                                          txtScheduleTime, _
                                          txtOnDemandExecute}

            Dim TabKeyDownArr() As String = {Tab(txtVariableValue, txtOnDemandExecute, "No"), _
                                             Tab(ddlSite, txtTrackerVariable, "Yes"), _
                                             Tab(ckInterface, txtVariableValue, "No"), _
                                             Tab(txtExpandFormula, ddlSite, "No"), _
                                             Tab(txtScheduleCode, ckInterface, "No"), _
                                             Tab(txtScheduleTime, txtExpandFormula, "No"), _
                                             Tab(txtOnDemandExecute, txtScheduleCode, "Int"), _
                                             Tab(txtTrackerVariable, txtScheduleTime, "No")}

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

            Master.HeaderMessage = GetTranslationString(FormName, FormName) & " - " & GetTranslationString(SessionManager.TrackerVariableMode.Replace("Row", ""), SessionManager.TrackerVariableMode.Replace("Row", ""))
            Master.IconImage = Request.ApplicationPath + "/images/boss.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/" & SessionManager.CulturePref & "/DataEntry.js")

            LoadCommonJavaScripts()

            LoadDropDownLists()

            Dim strSessionID As String = Session.SessionID.ToString
            strSessionID = "(S(" + strSessionID + "))"
            imgElements.Attributes.Add("onclick", "window.open('/APlus/" + strSessionID + "/UI/Pages/DataCollectionPrograms/DataElementsListing.aspx','newWin','height=500, width=500, left=500, top=100, resizable=yes, scrollbars=1');")

            If Not Page.IsPostBack Then
                LoadCultureTranslations()

                Select Case SessionManager.TrackerVariableMode.ToString()
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
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Tracker Variable.');")
                        TransactionHistory1.LockControl = True
                        imgElements.Visible = False
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        txtTrackerVariableID.Text = "New"
                        LoadAddEditModeJavaScripts()
                        pnlMasterControls.Visible = False
                        If SessionManager.WorkingSiteID > 0 Then
                            Dim objitem As ListItem = ddlSite.Items.FindByValue(SessionManager.WorkingSiteID)
                            If objitem IsNot Nothing Then
                                objitem.Selected = True
                                txtSite.Text = objitem.Text
                                ddlSite.Visible = False
                                txtSite.Visible = True
                            Else
                                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TrackerVariables1"), False)
                                Return
                            End If
                        Else
                            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TrackerVariables1"), False)
                            Return
                        End If
                        txtTrackerVariable.Focus()
                    Case "EditRow"
                        LoadAddEditModeJavaScripts()
                        LoadSelectedRecord()
                        UnEnableRecords()
                        txtTrackerVariable.Focus()

                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TrackerVariables1"), False)
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
            Select Case SessionManager.TrackerVariableMode.ToString()
                Case "AddRow"
                    blnSuccess = InsertTrackerVariable()
                Case "EditRow"
                    blnSuccess = UpdateTrackerVariable()
                Case "DeleteRow"
                    blnSuccess = DeleteTrackerVariable()
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TrackerVariableMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TrackerVariables1"), False)
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TrackerVariableMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TrackerVariables1"), False)
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadDropDownLists()
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
                Master.DisplayErrors(ProgramName & " - LoadDropDownLists", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
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

            Dim objDT As DataTable = TrackerVariables.SelectTrackerVariable(Convert.ToInt16(SessionManager.SelectedValue))
            If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                Dim dtRow As DataRow = objDT.Rows(0)
                Dim objItem As ListItem

                txtTrackerVariableID.Text = SessionManager.SelectedValue
                txtTrackerVariable.Text = dtRow("TrackerVariable").ToString
                txtVariableValue.Text = dtRow("VariableValue").ToString

                objItem = ddlSite.Items.FindByValue(dtRow("SiteID").ToString)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                    txtSite.Text = objItem.Text
                ElseIf IsNumeric(dtRow("SiteID").ToString) Then
                    Dim dtSite As DataTable = SiteMaster.GetSiteMasterBySite(dtRow("SiteID").ToString)
                    If dtSite IsNot Nothing AndAlso dtSite.Rows.Count = 1 Then
                        objItem = New ListItem(dtSite.Rows(0)("Site").ToString, dtSite.Rows(0)("SiteID").ToString)
                        objItem.Selected = True
                        txtSite.Text = objItem.Text
                    End If
                End If

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

                TransactionHistory1.TableName = DBTableName
                TransactionHistory1.RecordID = SessionManager.SelectedValue.Trim()

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("TrackerVariable", txtTrackerVariable.Text.Trim())
                objDic.Add("VariableValue", txtVariableValue.Text.Trim())
                objDic.Add("Site", txtSite.Text.Trim)
                objDic.Add("Interface", ckInterface.Checked.ToString)
                objDic.Add("Formula", txtExpandFormula.Text.Trim)
                objDic.Add("ScheduleCode", txtScheduleCode.Text.Trim)
                objDic.Add("ScheduleTime", txtScheduleTime.Text.Trim)
                objDic.Add("OnDemandExecute", txtOnDemandExecute.Text.Trim)

                SessionManager.RecordTransactionCurrentValues = objDic

                LoadTrackerGrids()
            End If
        End Sub
        Private Sub LoadTrackerGrids()
            mcCollection.StoredProcedureParams.Add("@TrackerVariableID", SessionManager.SelectedValue)
            mcCollection.DataBind()
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

            Select Case SessionManager.TrackerVariableMode.ToString()
                Case "ViewRow", "DeleteRow"
                    pnlOKCancel.Visible = False
                    txtTrackerVariable.ReadOnly = True
                    txtTrackerVariable.CssClass = "Textbox_Display"
                    txtVariableValue.ReadOnly = True
                    txtVariableValue.CssClass = "Textbox_Display"
                    ddlSite.Visible = False
                    txtSite.Visible = True
                    ckInterface.Enabled = False
                    txtExpandFormula.ReadOnly = True
                    txtExpandFormula.CssClass = "Textbox_Display"
                    txtScheduleCode.ReadOnly = True
                    txtScheduleCode.CssClass = "Textbox_Display"
                    txtScheduleTime.ReadOnly = True
                    txtScheduleTime.CssClass = "Textbox_Display"
                    txtOnDemandExecute.ReadOnly = True
                    txtOnDemandExecute.CssClass = "Textbox_Display"
            End Select
        End Sub
        Private Function InsertTrackerVariable() As Boolean
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
                If Not txtTrackerVariable.Text.StartsWith("[") OrElse Not txtTrackerVariable.Text.EndsWith("]") OrElse txtTrackerVariable.Text.Trim.Length < 3 Then
                    Master.DisplayError("Tracker Variable must be enclosed in brackets - [ ] ")
                    Return False
                End If
                If txtTrackerVariable.Text.IndexOfAny(" @#$%^&*(){}<>") > 0 Then
                    Master.DisplayError("Tracker Variable cannot contain any space or special characters")
                    Return False
                End If
                If txtTrackerVariable.Text.Trim.ToUpper = "[VALUE]" OrElse _
                txtTrackerVariable.Text.Trim.ToUpper = "[TARGET]" OrElse _
                txtTrackerVariable.Text.Trim.ToUpper = "[HISTORIC]" Then
                    Master.DisplayError("Value, Target and Historic are reserved keywords and cannot be used as variable names")
                    Return False
                End If
                If ckInterface.Checked AndAlso txtExpandFormula.Text.Trim.Length = 0 Then
                    Master.DisplayError("Formula is required if this variable is set to Interface")
                    Return False
                End If

                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                Dim strVariable As String = RegionalConversion.FormatSQLSingle(txtVariableValue.Text)
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

                SessionManager.SelectedValue = TrackerVariables.AddTrackerVariable(txtTrackerVariable.Text.Trim, strVariable, ddlSite.SelectedItem.Value, ckInterface.Checked, txtExpandFormula.Text.Trim, strVariables.Trim, txtScheduleCode.Text.Trim, txtScheduleTime.Text.Trim, strNextExecuteTime, strOnDemandExecuteTime)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValue, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertTrackerVariable", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateTrackerVariable() As Boolean
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
                If Not txtTrackerVariable.Text.StartsWith("[") OrElse Not txtTrackerVariable.Text.EndsWith("]") OrElse txtTrackerVariable.Text.Trim.Length < 3 Then
                    Master.DisplayError("Tracker Variable must be enclosed in brackets - [ ] ")
                    Return False
                End If
                If txtTrackerVariable.Text.IndexOfAny(" @#$%^&*(){}<>") > 0 Then
                    Master.DisplayError("Tracker Variable cannot contain any space or special characters")
                    Return False
                End If
                If txtTrackerVariable.Text.Trim.ToUpper = "[VALUE]" OrElse _
                txtTrackerVariable.Text.Trim.ToUpper = "[TARGET]" OrElse _
                txtTrackerVariable.Text.Trim.ToUpper = "[HISTORIC]" Then
                    Master.DisplayError("Value, Target and Historic are reserved keywords and cannot be used as variable names")
                    Return False
                End If
                If ckInterface.Checked AndAlso txtExpandFormula.Text.Trim.Length = 0 Then
                    Master.DisplayError("Formula is required if this variable is set to Interface")
                    Return False
                End If

                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.CompareDictionaryValues(SessionManager.RecordTransactionCurrentValues, objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                Dim strVariable As String = RegionalConversion.FormatSQLSingle(txtVariableValue.Text)
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

                TrackerVariables.UpdateTrackerVariable(SessionManager.SelectedValue, txtTrackerVariable.Text.Trim, strVariable, ddlSite.SelectedItem.Value, ckInterface.Checked, txtExpandFormula.Text.Trim, strVariables.Trim, txtScheduleCode.Text.Trim, txtScheduleTime.Text.Trim, strNextExecuteTime, strOnDemandExecuteTime)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValue.Trim(), strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateTrackerVariable", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function DeleteTrackerVariable() As Boolean
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
                TrackerVariables.DeleteTrackerVariable(SessionManager.SelectedValue)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValue.Trim(), "Tracker Variable Deleted", SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteTrackerVariable", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
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
            objDic.Add("TrackerVariable", txtTrackerVariable.Text.Trim())
            objDic.Add("VariableValue", txtVariableValue.Text.Trim())
            If ddlSite.Visible Then
                objDic.Add("Site", ddlSite.SelectedItem.Text)
            End If
            objDic.Add("Interface", ckInterface.Checked.ToString)
            objDic.Add("Formula", txtExpandFormula.Text.Trim)
            objDic.Add("ScheduleCode", txtScheduleCode.Text.Trim)
            objDic.Add("ScheduleTime", txtScheduleTime.Text.Trim)
            objDic.Add("OnDemandExecute", txtOnDemandExecute.Text.Trim)

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
                        Else
                            Master.DisplayError("Mismatched brackets detected []")
                            Return False
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
