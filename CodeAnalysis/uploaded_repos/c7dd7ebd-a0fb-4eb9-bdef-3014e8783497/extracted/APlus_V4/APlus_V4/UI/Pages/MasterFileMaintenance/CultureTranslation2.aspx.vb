#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports System.Collections.Generic

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class CultureTranslation2
        Inherits ApplicationBase

#Region " Constants"
        Private Shared ReadOnly FormName As String = "Culture Translation Master"
        Private Shared ReadOnly ProgramName As String = "CultureTranslationMaster2"
        Private Shared ReadOnly DBTableName As String = "CultureTranslationMaster"
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel, btnExit}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel", "Exit"}
            Dim OutMessageArr() As String = {"", "", ""}

            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnExit.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
            If SessionManager.CultureTranslationMode = "DeleteRow" Then
                btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Culture Translation record.');")
                TransactionHistory.LockControl = True
            End If
        End Sub
        Private Sub LoadAddModeJavaScripts()
            Dim myTabArray() As Object = {ddlCulture, txtExpandResourceKey, txtExpandDefaultValue, txtExpandTranslationText}

            Dim TabKeyDownArr() As String = {Tab(txtExpandResourceKey, txtExpandTranslationText, "No"), _
                                             Tab(txtExpandDefaultValue, ddlCulture, "No"), _
                                             Tab(txtExpandTranslationText, txtExpandDefaultValue, "No"), _
                                             Tab(ddlCulture, txtExpandDefaultValue, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {txtExpandTranslationText}
            Dim TabKeyDownArr() As String = {Tab(txtExpandTranslationText, txtExpandTranslationText, "No")}

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
                lblCulture.Text = GetTranslationString("culture", lblCulture.Text.Replace(":", "")) & ":"
                lblKey.Text = GetTranslationString("key", lblKey.Text.Replace(":", "")) & ":"
                lblCultureValue.Text = GetTranslationString("defaultvalue", lblCultureValue.Text.Replace(":", "")) & ":"
                lblTranslationText.Text = GetTranslationString("translation", lblTranslationText.Text.Replace(":", "")) & ":"
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
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
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

            Master.HeaderMessage = GetTranslationString(FormName, FormName) & " - " & GetTranslationString(SessionManager.CultureTranslationMode.Replace("Row", ""), SessionManager.CultureTranslationMode.Replace("Row", "")) & " " & GetTranslationString("culturetranslation", "Culture Translation")
            Master.IconImage = Request.ApplicationPath + "/images/earth_location.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                Select Case SessionManager.CultureTranslationMode.ToString()
                    Case "EditRow"
                        BindCulture()
                        LoadSelectedRecord()
                        UnEnableRecords()
                        LoadEditModeJavaScripts()
                        txtExpandTranslationText.Focus()
                    Case "DeleteRow"
                        BindCulture()
                        LoadSelectedRecord()
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this CultureTranslation record.');")
                        UnEnableRecords()
                        TransactionHistory.LockControl = True
                    Case "AddRow"
                        TransactionHistory.Visible = False
                        BindCulture()
                        LoadAddModeJavaScripts()
                        ddlCulture.Focus()
                        txtCulture.Visible = False
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("CultureMaster1"), False)
                End Select
            End If
        End Sub
        Private Sub btnOK_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnOK.Click
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
            Select Case SessionManager.CultureTranslationMode.ToString()
                Case "AddRow"
                    blnSuccess = InsertCultureTranslation()
                Case "DeleteRow"
                    blnSuccess = DeleteCultureTranslation()
                Case "EditRow"
                    blnSuccess = UpdateCultureTranslation()
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CultureTranslationMode)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedCultureCode)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedCultureValue)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("CultureTranslation1"), False)
            End If
        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CultureTranslationMode)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedCultureCode)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedCultureValue)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("CultureTranslation1"), False)
        End Sub
        Private Sub btnCancel_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnCancel.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CultureTranslationMode)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedCultureCode)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedCultureValue)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("CultureTranslation1"), False)
        End Sub
#End Region

#Region " Custom Methods"
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
            TransactionHistory.TableName = DBTableName
            TransactionHistory.RecordID = ConfigurationManager.AppSettings("ApplicationNameRef") & "," & SessionManager.SelectedCultureCode.Trim() & "," & SessionManager.SelectedCultureValue.Trim()

            Try
                Dim ds As DataTable = CultureTranslation.SelectCultureTranslationByKey(SessionManager.SelectedCultureCode, SessionManager.SelectedCultureValue)
                If ds.Rows.Count <> 0 Then
                    Dim dr As DataRow = ds.Rows(0)
                    txtCulture.Text = dr("CultureCode").ToString
                    Dim objItem As ListItem = ddlCulture.Items.FindByText(dr("CultureCode").ToString)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                    End If
                    txtExpandResourceKey.Text = dr("ResourceKey").ToString
                    txtExpandDefaultValue.Text = dr("DefaultValue").ToString
                    txtExpandTranslationText.Text = dr("ResourceValue").ToString

                    Dim objDic As New Dictionary(Of String, String)
                    objDic.Add("Culture", ddlCulture.SelectedItem.Text.Trim())
                    objDic.Add("ResourceKey", txtExpandResourceKey.Text.Trim())
                    objDic.Add("DefaultValue", txtExpandDefaultValue.Text.Trim())
                    objDic.Add("Translation", txtExpandTranslationText.Text.Trim())
                    SessionManager.RecordTransactionCurrentValues = objDic
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
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

            If SessionManager.CultureTranslationMode = "DeleteRow" Then
                ddlCulture.Visible = False
                txtCulture.Visible = True
                pnlOKCancel.Visible = True
                txtExpandResourceKey.ReadOnly = True
                txtExpandResourceKey.CssClass = "Textbox_Display"
                txtExpandDefaultValue.ReadOnly = True
                txtExpandDefaultValue.CssClass = "Textbox_Display"
                txtExpandTranslationText.ReadOnly = True
                txtExpandTranslationText.CssClass = "Textbox_Display"
            ElseIf SessionManager.CultureTranslationMode = "EditRow" Then
                ddlCulture.Visible = False
                txtCulture.Visible = True
                txtExpandResourceKey.ReadOnly = True
                txtExpandResourceKey.CssClass = "Textbox_Display"
                txtExpandDefaultValue.ReadOnly = True
                txtExpandDefaultValue.CssClass = "Textbox_Display"
            End If
        End Sub
        Private Function InsertCultureTranslation() As Boolean
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
                CultureTranslation.InsertResourceValue(ddlCulture.SelectedItem.Value.Trim(), txtExpandResourceKey.Text.Trim(), txtExpandDefaultValue.Text.Trim(), txtExpandTranslationText.Text.Trim())
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, ConfigurationManager.AppSettings("ApplicationNameRef") & "," & ddlCulture.SelectedItem.Value.Trim() & "," & txtExpandResourceKey.Text.Trim(), strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertCultureTranslation", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateCultureTranslation() As Boolean
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
                Dim strChangeLog As String = TransactionProcessing.CompareDictionaryValues(SessionManager.RecordTransactionCurrentValues, objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If
                CultureTranslation.UpdateResourceValue(SessionManager.SelectedCultureCode.Trim(), SessionManager.SelectedCultureValue.Trim(), txtExpandDefaultValue.Text, txtExpandTranslationText.Text)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, ConfigurationManager.AppSettings("ApplicationNameRef") & "," & SessionManager.SelectedCultureCode.Trim() & "," & SessionManager.SelectedCultureValue.Trim(), strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateCultureTranslation", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function DeleteCultureTranslation() As Boolean
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
                CultureTranslation.DeleteResourceValue(SessionManager.SelectedCultureCode.Trim(), SessionManager.SelectedCultureValue.Trim())
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, ConfigurationManager.AppSettings("ApplicationNameRef") & "," & SessionManager.SelectedCultureCode.Trim() & "," & SessionManager.SelectedCultureValue.Trim(), "Culture Translation Deleted", SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteCultureTranslation", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
        End Function
        Private Sub BindCulture()
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
                CultureMaster.SelectCultureMasterCodeList(ddlCulture)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindCulture", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

#Region " Get Updated Values"
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
            objDic.Add("Culture", ddlCulture.SelectedItem.Text.Trim())
            objDic.Add("ResourceKey", txtExpandResourceKey.Text.Trim())
            objDic.Add("DefaultValue", txtExpandDefaultValue.Text.Trim())
            objDic.Add("Translation", txtExpandTranslationText.Text.Trim())
            Return objDic
        End Function
#End Region

    End Class
End Namespace