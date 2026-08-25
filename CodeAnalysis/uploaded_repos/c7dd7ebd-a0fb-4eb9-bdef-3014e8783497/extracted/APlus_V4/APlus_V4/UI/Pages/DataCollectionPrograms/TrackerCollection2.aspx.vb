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
    Partial Class TrackerCollection2
        Inherits ApplicationBase

#Region " Private Variables"
        Private Shared ReadOnly FormName As String = "Savings Types"
        Private Shared ReadOnly ProgramName As String = "TrackerCollection2"
        Private Shared ReadOnly DBTableName As String = "TrackerCollection"
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
                lblSavingsType.Text = GetTranslationString("savingstype", lblSavingsType.Text.Replace(":", "")) & ":"
                lblSavingsTerm.Text = GetTranslationString("savingsterm", lblSavingsTerm.Text.Replace(":", "")) & ":"
                lblManualEntered.Text = GetTranslationString("manualentered", lblManualEntered.Text.Replace(":", "")) & ":"
                lblFormula.Text = GetTranslationString("formula", lblFormula.Text.Replace(":", "")) & ":"
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
            If ddlTracker.Visible Then
                Dim myTabArray() As Object = {ddlTracker, _
                                              ddlTrackerType, _
                                              ddlSavingsType, _
                                              cbNoFormula, _
                                              txtExpandFormula}

                Dim TabKeyDownArr() As String = {Tab(ddlTrackerType, txtExpandFormula, "No"), _
                                                 Tab(ddlSavingsType, ddlTracker, "No"), _
                                                 Tab(cbNoFormula, ddlTrackerType, "No"), _
                                                 Tab(txtExpandFormula, ddlSavingsType, "No"), _
                                                 Tab(ddlTracker, cbNoFormula, "No")}

                AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
            Else
                Dim myTabArray() As Object = {ddlTrackerType, _
                                              ddlSavingsType, _
                                              cbNoFormula, _
                                              txtExpandFormula}

                Dim TabKeyDownArr() As String = {Tab(ddlSavingsType, txtExpandFormula, "No"), _
                                                 Tab(cbNoFormula, ddlTrackerType, "No"), _
                                                 Tab(txtExpandFormula, ddlSavingsType, "No"), _
                                                 Tab(ddlTrackerType, cbNoFormula, "No")}

                AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
            End If
        End Sub
        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {cbNoFormula, txtExpandFormula}

            Dim TabKeyDownArr() As String = {Tab(txtExpandFormula, txtExpandFormula, "No"), _
                                             Tab(cbNoFormula, cbNoFormula, "No")}

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

            Master.HeaderMessage = GetTranslationString(FormName, FormName) & " - " & GetTranslationString(SessionManager.TrackerCollectionMode.Replace("Row", ""), SessionManager.TrackerCollectionMode.Replace("Row", ""))
            Master.IconImage = Request.ApplicationPath + "/images/boss.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            Dim strSessionID As String = Session.SessionID.ToString
            strSessionID = "(S(" + strSessionID + "))"
            imgElements.Attributes.Add("onclick", "window.open('/APlus/" + strSessionID + "/UI/Pages/DataCollectionPrograms/TrackerVariablesListing.aspx','newWin','height=500, width=500, left=500, top=100, resizable=yes, scrollbars=1');")

            If Not Page.IsPostBack Then
                LoadCultureTranslations()
                BindDropDownLists()

                Select Case SessionManager.TrackerCollectionMode.ToString()
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
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Savings Type.');")
                        TransactionHistory1.LockControl = True
                        imgElements.Visible = False
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        Dim objItem As ListItem = ddlTracker.Items.FindByValue(SessionManager.SelectedValueTrackerID)
                        If objItem IsNot Nothing Then
                            objItem.Selected = True
                            txtTracker.Text = objItem.Text
                            ddlTracker.Visible = False
                            txtTracker.Visible = True
                            ddlTrackerType.Focus()
                        Else
                            ddlTracker.Focus()
                        End If
                        LoadAddModeJavaScripts()
                    Case "EditRow"
                        LoadEditModeJavaScripts()
                        LoadSelectedRecord()
                        UnEnableRecords()
                        txtExpandFormula.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TrackerCollection1"), False)
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
            Select Case SessionManager.TrackerCollectionMode.ToString()
                Case "AddRow"
                    blnSuccess = InsertTrackerCollection()
                Case "EditRow"
                    blnSuccess = UpdateTrackerCollection()
                Case "DeleteRow"
                    blnSuccess = DeleteTrackerCollection()
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueTrackerCollectionID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TrackerCollectionMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TrackerCollection1"), False)
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueTrackerCollectionID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TrackerCollectionMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TrackerCollection1"), False)
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
                Trackers.GetTrackerList(ddlTracker)
                ddlTracker.Items.Insert(0, "")

                TrackerTypes.GetTrackerTypesList(ddlTrackerType)
                ddlTrackerType.Items.Insert(0, "")

                SavingsTypeMaster.GetSavingsTypeList(ddlSavingsType)
                ddlSavingsType.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindDropDownLists", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
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

            Dim objDT As DataTable = TrackerCollection.SelectTrackerCollection(SessionManager.SelectedValueTrackerCollectionID)
            If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                Dim dtRow As DataRow = objDT.Rows(0)
                Dim objItem As ListItem

                objItem = ddlTracker.Items.FindByValue(dtRow("TrackerID").ToString)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                    txtTracker.Text = objItem.Text
                End If
                objItem = ddlTrackerType.Items.FindByValue(dtRow("TrackerTypeID").ToString)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                    txtTrackerType.Text = objItem.Text
                End If
                objItem = ddlSavingsType.Items.FindByValue(dtRow("SavingsTypeID").ToString)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                    txtSavingsType.Text = objItem.Text
                Else
                    Dim dtSavings As DataTable = SavingsTypeMaster.SelectSavingsTypeByID(dtRow("SavingsTypeID").ToString)
                    If dtSavings IsNot Nothing AndAlso dtSavings.Rows.Count = 1 Then
                        objItem = New ListItem(dtSavings.Rows(0)("SavingsType").ToString, dtRow("SavingsTypeID").ToString)
                        objItem.Selected = True
                        ddlSavingsType.Items.Add(objItem)
                        txtSavingsType.Text = objItem.Text
                    End If
                End If
                If dtRow("Formula").ToString.Trim.Length = 0 Then
                    cbNoFormula.Checked = True
                    txtExpandFormula.Text = ""
                Else
                    cbNoFormula.Checked = False
                    txtExpandFormula.Text = dtRow("Formula").ToString
                End If

                TransactionHistory1.TableName = DBTableName
                TransactionHistory1.RecordID = SessionManager.SelectedValueTrackerCollectionID.ToString

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("Tracker", txtTracker.Text.Trim())
                objDic.Add("TrackerType", txtTrackerType.Text.Trim())
                objDic.Add("SavingsType", txtSavingsType.Text.Trim())
                objDic.Add("Formula", txtExpandFormula.Text.Trim())

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

            Select Case SessionManager.TrackerCollectionMode.ToString()
                Case "ViewRow", "DeleteRow"
                    pnlOKCancel.Visible = False
                    ddlTracker.Visible = False
                    txtTracker.Visible = True
                    ddlTrackerType.Visible = False
                    txtTrackerType.Visible = True
                    ddlSavingsType.Visible = False
                    txtSavingsType.Visible = True
                    cbNoFormula.Enabled = False
                    txtExpandFormula.ReadOnly = True
                    txtExpandFormula.CssClass = "Textbox_Display"
                Case "EditRow"
                    ddlTracker.Visible = False
                    txtTracker.Visible = True
                    ddlTrackerType.Visible = False
                    txtTrackerType.Visible = True
                    ddlSavingsType.Visible = False
                    txtSavingsType.Visible = True
            End Select
        End Sub
        Private Function InsertTrackerCollection() As Boolean
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

                Dim strVariables As String = ""
                If Not ValidateFormula(txtExpandFormula.Text.Trim, strVariables) Then
                    Return False
                End If

                SessionManager.SelectedValueTrackerCollectionID = TrackerCollection.AddTrackerCollection(ddlTracker.SelectedItem.Value, ddlTrackerType.SelectedItem.Value, ddlSavingsType.SelectedItem.Value, txtExpandFormula.Text.Trim, strVariables)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueTrackerCollectionID, strChangeLog, SessionManager.UserID)
                RecordTransactionHistory.InsertRecordTransactionHistory("Trackers", ddlTracker.SelectedItem.Value.ToString, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertTrackerCollection", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateTrackerCollection() As Boolean
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

                Dim strVariables As String = ""
                If Not ValidateFormula(txtExpandFormula.Text.Trim, strVariables) Then
                    Return False
                End If

                TrackerCollection.UpdateTrackerCollection(SessionManager.SelectedValueTrackerCollectionID, txtExpandFormula.Text.Trim, strVariables)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueTrackerCollectionID, strChangeLog, SessionManager.UserID)
                RecordTransactionHistory.InsertRecordTransactionHistory("Trackers", SessionManager.SelectedValueTrackerID.ToString, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateTrackerCollection", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function DeleteTrackerCollection() As Boolean
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
                TrackerCollection.DeleteTrackerCollection(SessionManager.SelectedValueTrackerCollectionID)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueTrackerCollectionID.ToString, "Savings Type Deleted", SessionManager.UserID)
                RecordTransactionHistory.InsertRecordTransactionHistory("Trackers", SessionManager.SelectedValueTrackerID.ToString, txtTrackerType.Text.Trim & " Deleted", SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteTrackerCollection", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
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
            If ddlTracker.SelectedItem IsNot Nothing AndAlso ddlTracker.SelectedItem.Value.ToString.Trim.Length > 0 Then
                objDic.Add("Tracker", ddlTracker.SelectedItem.Text.Trim)
            Else
                objDic.Add("Tracker", "")
            End If
            If ddlTrackerType.SelectedItem IsNot Nothing AndAlso ddlTrackerType.SelectedItem.Value.ToString.Trim.Length > 0 Then
                objDic.Add("TrackerType", ddlTrackerType.SelectedItem.Text.Trim)
            Else
                objDic.Add("TrackerType", "")
            End If
            If ddlSavingsType.SelectedItem IsNot Nothing AndAlso ddlSavingsType.SelectedItem.Value.ToString.Trim.Length > 0 Then
                objDic.Add("SavingsType", ddlSavingsType.SelectedItem.Text.Trim)
            Else
                objDic.Add("SavingsType", "")
            End If
            objDic.Add("Formula", txtExpandFormula.Text.Trim())

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
                If cbNoFormula.Checked AndAlso txtExpandFormula.Text.Trim.Length > 0 Then
                    Master.DisplayError("Formula is not valid when Savings are to be manually entered")
                    Return False
                ElseIf Not cbNoFormula.Checked AndAlso txtExpandFormula.Text.Trim.Length = 0 Then
                    Master.DisplayError("Formula is required if Savings are not manually entered")
                    Return False
                End If

                Dim strCheckFormula As String = ""
                Dim strVariables As String = ""
                Dim strVariableHolder As String = ""

                ' Validate Variables
                strCheckFormula = txtExpandFormula.Text.Trim.Replace("[Value]", "").Replace("[Target]", "").Replace("[Historic]", "")
                If strCheckFormula.Contains("[") Then
                    Do Until Not strCheckFormula.Contains("[")
                        If strCheckFormula.Contains("]") Then
                            strVariableHolder = strCheckFormula.Substring(strCheckFormula.IndexOf("["), strCheckFormula.IndexOf("]") - strCheckFormula.IndexOf("[") + 1)
                            strCheckFormula = strCheckFormula.Replace(strVariableHolder, "")

                            If strVariables.Trim.Length > 0 Then strVariables += ","
                            strVariables += strVariableHolder
                        Else
                            Master.DisplayError("Syntax error in formula: missing right bracker ']'")
                            Return False
                        End If
                    Loop

                    If strVariables.Trim.Length > 0 Then
                        Dim iVariables As Integer = strVariables.Split(",").Length
                        Dim iValidVariables As Integer = TrackerVariables.SelectValidateTrackerVariables(strVariables)

                        If iVariables <> iValidVariables Then
                            Master.DisplayError("Invalid variables used in formula")
                            Return False
                        End If
                    End If
                End If

                ' Validate formula logic
                strCheckFormula = txtExpandFormula.Text.Trim.Replace("[Value]", "1").Replace("[Target]", "1").Replace("[Historic]", "1")
                If strCheckFormula.Contains("[") Then
                    Do Until Not strCheckFormula.Contains("[")
                        If strCheckFormula.Contains("]") Then
                            strVariableHolder = strCheckFormula.Substring(strCheckFormula.IndexOf("["), strCheckFormula.IndexOf("]") - strCheckFormula.IndexOf("[") + 1)
                            strCheckFormula = strCheckFormula.Replace(strVariableHolder, "1")
                        Else
                            Master.DisplayError("Syntax error in formula: missing right bracker ']'")
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
#End Region

    End Class
End Namespace
