#Region " Imports"
Imports System.IO
Imports System.Collections.Generic
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class AreaGroupUserMaster2
        Inherits ApplicationBase

#Region " Private Constant Variables"
        Private Shared ReadOnly FormName As String = "Area User Master"
        Private Shared ReadOnly ProgramName As String = "AreaGroupUserMaster2"
        Private Shared ReadOnly DBTableName As String = "AreaGroupUserMaster"
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
                lblArea.Text = GetTranslationString("area", lblArea.Text.Replace(":", "")) & ":"
                lblUser.Text = GetTranslationString("username", lblUser.Text.Replace(":", "")) & ":"
                lblEvaluate.Text = GetTranslationString("allowevaluate", lblEvaluate.Text.Replace(":", "")) & ":"
                lblEdit.Text = GetTranslationString("allowedit", lblEdit.Text.Replace(":", "")) & ":"
                lblKPIView.Text = GetTranslationString("allowkpiview", lblKPIView.Text.Replace(":", "")) & ":"
                lblKPIEdit.Text = GetTranslationString("allowkpiedit", lblKPIEdit.Text.Replace(":", "")) & ":"
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
        Private Sub LoadAddEditModeJavaScript()
            Dim myTabArray() As Object = {ddlArea, ddlUserID, ckAllowAnomalyEvaluate, ckAllowAnomalyEdit, ckAllowKPIView, ckAllowKPIEdit}

            Dim TabKeyDownArr() As String = {Tab(ddlUserID, ckAllowKPIEdit, "No"), _
                                             Tab(ckAllowAnomalyEvaluate, ddlArea, "No"), _
                                             Tab(ckAllowAnomalyEdit, ddlUserID, "No"), _
                                             Tab(ckAllowKPIView, ckAllowAnomalyEvaluate, "No"), _
                                             Tab(ckAllowKPIEdit, ckAllowAnomalyEdit, "No"), _
                                             Tab(ddlArea, ckAllowKPIView, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
#End Region

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, CType(sender, Page).Title.Trim(), "Page_Load")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Master.IconImage = Request.ApplicationPath + "/images/Padlock-User-Control.gif"
            Master.HeaderMessage = FormName & " - " & SessionManager.Mode.Replace("Row", "")
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                LoadCultureTranslations()
                BindLists()

                Select Case SessionManager.Mode
                    Case "EditRow"
                        LoadSelectedRecord()
                        LoadAddEditModeJavaScript()
                        UnEnableRecords()
                        ckAllowAnomalyEvaluate.Focus()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Area User Record.');")
                        TransactionHistory1.LockControl = True
                    Case "AddRow"
                        TransactionHistory1.Visible = False

                        If Not String.IsNullOrEmpty(SessionManager.SelectedValueUser) Then
                            Dim objItem As ListItem = ddlUserID.Items.FindByValue(SessionManager.SelectedValueUser)
                            If objItem IsNot Nothing Then
                                objItem.Selected = True
                                txtUserID.Text = objItem.Text
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

                            ddlUserID.Visible = False
                            txtUserID.Visible = True
                        End If

                        If SessionManager.SelectedValueAreaGroupID > 0 Then
                            Dim objItem As ListItem = ddlArea.Items.FindByValue(SessionManager.SelectedValueAreaGroupID)
                            If objItem IsNot Nothing Then
                                objItem.Selected = True
                                txtArea.Text = objItem.Text
                            End If

                            ddlArea.Visible = False
                            txtArea.Visible = True

                            ddlUserID.Focus()
                        Else
                            ddlArea.Focus()
                        End If

                        LoadAddEditModeJavaScript()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AreaGroupUserMaster1"), False)
                End Select
            End If
        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, CType(sender, Button).ID, "btnExit_Click")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueAreaGroupID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Mode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AreaGroupUserMaster1"), False)
        End Sub
        Private Sub btnOK_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, CType(sender, Button).ID, "btnOK_Click")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim blnSuccess As Boolean
            Select Case SessionManager.Mode
                Case "EditRow"
                    blnSuccess = UpdateAreaGroupUserMaster()
                Case "DeleteRow"
                    blnSuccess = DeleteAreaGroupUserMaster()
                Case "AddRow"
                    blnSuccess = InsertAreaGroupUserMaster()
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueAreaGroupID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Mode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AreaGroupUserMaster1"), False)
            End If
        End Sub
        Private Sub btnCancel_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnCancel.Click, btnExit.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueAreaGroupID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Mode)

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AreaGroupUserMaster1"), False)
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub BindLists()
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
                AreaGroupMaster.GetAreaGroupMasterList(ddlArea, SessionManager.WorkingSiteID)
                ddlArea.Items.Insert(0, "")

                UserMaster.SelectUserNameList(SessionManager.WorkingSiteID, ddlUserID)
                ddlUserID.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindLists", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
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

            If SessionManager.RecordTransactionCurrentValues IsNot Nothing Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RecordTransactionCurrentValues)
            End If

            Try
                Dim objDT As DataTable = AreaGroupUserMaster.SelectAreaGroupUserMasterByID(SessionManager.SelectedValueAreaGroupID, SessionManager.SelectedValue1)

                If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                    Dim dtRow As DataRow = objDT.Rows(0)
                    Dim objItem As ListItem

                    objItem = ddlArea.Items.FindByValue(SessionManager.SelectedValueAreaGroupID)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                        txtArea.Text = objItem.Text
                    End If
                    objItem = ddlUserID.Items.FindByValue(SessionManager.SelectedValue1)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                        txtUserID.Text = objItem.Text
                    End If
                    ckAllowAnomalyEvaluate.Checked = dtRow("AllowAnomalyEvaluate")
                    ckAllowAnomalyEdit.Checked = dtRow("AllowAnomalyEdit")
                    ckAllowKPIView.Checked = dtRow("AllowKPIView")
                    ckAllowKPIEdit.Checked = dtRow("AllowKPIEdit")

                    TransactionHistory1.TableName = DBTableName
                    TransactionHistory1.RecordID = SessionManager.SelectedValueAreaGroupID.ToString & "," & SessionManager.SelectedValue1

                    Dim objDic As New Dictionary(Of String, String)
                    objDic.Add("Area", txtArea.Text.Trim)
                    objDic.Add("User", txtUserID.Text.Trim)
                    objDic.Add("EvaluateAnomaly", ckAllowAnomalyEvaluate.Checked.ToString)
                    objDic.Add("EditAnomaly", ckAllowAnomalyEdit.Checked.ToString)
                    objDic.Add("ViewKPI", ckAllowKPIView.Checked.ToString)
                    objDic.Add("EditKPI", ckAllowKPIEdit.Checked.ToString)

                    SessionManager.RecordTransactionCurrentValues = objDic
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
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
                Case "ViewRow", "DeleteRow"
                    ddlArea.Visible = False
                    txtArea.Visible = True
                    ddlUserID.Visible = False
                    txtUserID.Visible = True
                    ckAllowAnomalyEvaluate.Enabled = False
                    ckAllowAnomalyEdit.Enabled = False
                    ckAllowKPIView.Enabled = False
                    ckAllowKPIEdit.Enabled = False
                Case "EditRow"
                    ddlArea.Visible = False
                    txtArea.Visible = True
                    ddlUserID.Visible = False
                    txtUserID.Visible = True
            End Select
        End Sub
        Private Function InsertAreaGroupUserMaster() As Boolean
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

                If ckAllowKPIEdit.Checked AndAlso Not ckAllowKPIView.Checked Then
                    Master.DisplayError("Allow KPI View must be checked when Allow Edit is checked.")
                    Return False
                End If

                AreaGroupUserMaster.AddAreaGroupUserMaster(ddlArea.SelectedItem.Value, ddlUserID.SelectedItem.Value, ckAllowAnomalyEvaluate.Checked, ckAllowAnomalyEdit.Checked, ckAllowKPIView.Checked, ckAllowKPIEdit.Checked)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, ddlArea.SelectedItem.Value.ToString & "," & ddlUserID.SelectedItem.Value, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertAreaGroupUserMaster", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateAreaGroupUserMaster() As Boolean
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

                If ckAllowKPIEdit.Checked AndAlso Not ckAllowKPIView.Checked Then
                    Master.DisplayError("Allow KPI View must be checked when Allow Edit is checked.")
                    Return False
                End If

                AreaGroupUserMaster.UpdateAreaGroupUserMaster(SessionManager.SelectedValueAreaGroupID, SessionManager.SelectedValue1, ckAllowAnomalyEvaluate.Checked, ckAllowAnomalyEdit.Checked, ckAllowKPIView.Checked, ckAllowKPIEdit.Checked)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueAreaGroupID & "," & SessionManager.SelectedValue1, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateAreaGroupUserMaster", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function DeleteAreaGroupUserMaster() As Boolean
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
                AreaGroupUserMaster.DeleteAreaGroupUserMaster(SessionManager.SelectedValueAreaGroupID, SessionManager.SelectedValue1)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValue & "," & SessionManager.SelectedValue1, "Area User Master Deleted", SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteAreaGroupUserMaster", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
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
            If ddlArea.SelectedItem IsNot Nothing Then
                objDic.Add("Area", ddlArea.SelectedItem.Text.Trim())
            End If
            If ddlUserID.SelectedItem IsNot Nothing Then
                objDic.Add("User", ddlUserID.SelectedItem.Text.Trim())
            End If
            objDic.Add("EvaluateAnomaly", ckAllowAnomalyEvaluate.Checked.ToString)
            objDic.Add("EditAnomaly", ckAllowAnomalyEdit.Checked.ToString)
            objDic.Add("ViewKPI", ckAllowKPIView.Checked.ToString)
            objDic.Add("EditKPI", ckAllowKPIEdit.Checked.ToString)

            Return objDic
        End Function
#End Region

    End Class
End Namespace