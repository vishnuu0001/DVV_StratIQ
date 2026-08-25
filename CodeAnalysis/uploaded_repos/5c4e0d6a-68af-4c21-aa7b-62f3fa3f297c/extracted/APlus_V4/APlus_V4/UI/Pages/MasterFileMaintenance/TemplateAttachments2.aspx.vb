#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class TemplateAttachments2
        Inherits ApplicationBase

#Region " Constants"
        Private Shared ReadOnly FormName As String = "Template Attachments"
        Private Shared ReadOnly ProgramName As String = "TemplateAttachments2"
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
        Sub LoadAddModeJavaScripts()
            Dim myTabArray() As Object = {fil, _
                                          ddlCategory}

            Dim TabKeyDownArr() As String = {Tab(ddlCategory, ddlCategory, "No"), _
                                             Tab(fil, fil, "No")}

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

            Master.IconImage = Request.ApplicationPath & "/images/mail_attachment.gif"
            Master.HeaderMessage = FormName
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()
            LoadDropDownListBoxes()

            If Not Page.IsPostBack Then
                If New System.Globalization.CultureInfo(SessionManager.CulturePref).TwoLetterISOLanguageName = "en" Then
                    trMasterAttachment.Visible = False
                Else
                    trMasterAttachment.Visible = True
                End If

                Select Case SessionManager.TemplateAttachmentMode
                    Case "AddRow"
                        LoadAddModeJavaScripts()
                        fil.Focus()
                    Case "ViewRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        pnlExit.Visible = True
                        pnlOKCancel.Visible = False
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Template Attachment.');")
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TemplateAttachments1"), False)
                End Select
            End If
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
            Dim strFile As String = String.Empty

            Select Case SessionManager.TemplateAttachmentMode
                Case "AddRow"
                    strFile = fil.PostedFile.FileName
                    blnSuccess = SaveAttachment()
                Case "DeleteRow"
                    strFile = SessionManager.SelectedValueAttachment.ToString
                    blnSuccess = DeleteAttachment()
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueAttachmentID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TemplateAttachmentMode)

                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TemplateAttachments1"), False)
            End If
        End Sub
        Private Sub btnCancel_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnCancel.Click, btnExit.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueAttachmentID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TemplateAttachmentMode)

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TemplateAttachments1"), False)
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadDropDownListBoxes()
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
                AttachmentCategoryTypes.SelectAttachmentCategoryTypesListByAttachmentType(AttachmentTypes.SelectAttachmentTypeIDByType("Template"), ddlCategory)
                AttachmentsMaster.SelectAttachmentsByTypeList(AttachmentTypes.SelectAttachmentTypeIDByType("Template"), "en", ddlMasterAttachment)
            Catch Exc As Exception
                Master.DisplayErrors(FormName & " - LoadDropDownListBoxes", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
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

            Try
                Dim objDT As DataTable = AttachmentsMaster.SelectAttachmentsMasterByID(SessionManager.SelectedValueAttachmentID)
                If objDT IsNot Nothing AndAlso objDT.Rows.Count > 0 Then
                    Dim objItem As ListItem
                    Dim dtRow As DataRow = objDT.Rows(0)

                    txtAttachment.Text = dtRow("Attachment").ToString.Trim
                    objItem = ddlCategory.Items.FindByValue(dtRow("AttachmentCategoryID").ToString)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                        txtCategory.Text = objItem.Text
                    End If
                    If ddlMasterAttachment.Visible AndAlso IsNumeric(dtRow("MasterAttachmentID").ToString) Then
                        objItem = ddlMasterAttachment.Items.FindByValue(dtRow("MasterAttachmentID").ToString)
                        If objItem IsNot Nothing Then
                            objItem.Selected = True
                            txtMasterAttachment.Text = objItem.Text
                        End If
                    End If
                End If
            Catch Exc As Exception
                Master.DisplayErrors(FormName & " - LoadSelectedRecord", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
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

            'only called for delete
            fil.Visible = False
            txtAttachment.Visible = True
            ddlCategory.Visible = False
            txtCategory.Visible = True
            ddlMasterAttachment.Visible = False
            txtMasterAttachment.Visible = True
        End Sub
        Private Function SaveAttachment() As Boolean
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
                If fil.PostedFile.FileName.Trim.Length > 0 Then
                    Dim iFileSize As Integer = Convert.ToInt32("0" + ConfigurationManager.AppSettings("MaxUploadFileSize").ToString)
                    If fil.PostedFile.ContentLength > iFileSize Then
                        Master.DisplayError("File Size must be no greater than " + (iFileSize / 1024).ToString)
                        Return False
                    End If
                Else
                    Master.DisplayError("Attachment File not Selected")
                    Return False
                End If

                If Not Directory.Exists(ConfigurationManager.AppSettings("TemplateAttachmentsRootDirectory")) Then
                    Master.DisplayManualErrors("SaveAttachment", "Template Attachments Root Directory Does Not Exist", SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                    Return False
                End If
                'Check for culture language directory
                Dim strCultureLanguage As String = New System.Globalization.CultureInfo(SessionManager.CulturePref).TwoLetterISOLanguageName
                If Not Directory.Exists(ConfigurationManager.AppSettings("TemplateAttachmentsRootDirectory") + strCultureLanguage) Then
                    Master.DisplayManualErrors("SaveAttachment", "Template Attachments Root Directory Does Not Exist", SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                    Return False
                End If

                Dim iMasterAttachmentID As Integer = 0
                If ddlMasterAttachment.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlMasterAttachment.SelectedItem.Value) Then
                    iMasterAttachmentID = ddlMasterAttachment.SelectedItem.Value
                End If

                AttachmentsMaster.InsertAttachmentsMaster(AttachmentTypes.SelectAttachmentTypeIDByType("Template"), Path.GetFileName(fil.PostedFile.FileName), Convert.ToInt32(ddlCategory.SelectedItem.Value), strCultureLanguage, iMasterAttachmentID)

                Dim strAttachmentFilePath As String = ConfigurationManager.AppSettings("TemplateAttachmentsRootDirectory") & strCultureLanguage & "\" & Path.GetFileName(fil.PostedFile.FileName)
                fil.PostedFile.SaveAs(strAttachmentFilePath)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(FormName & " - SaveAttachment", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function DeleteAttachment() As Boolean
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
                If Not Directory.Exists(ConfigurationManager.AppSettings("TemplateAttachmentsRootDirectory")) Then
                    Master.DisplayManualErrors("DeleteAttachment", "Template Attachments Directory Does Not Exist", SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                    Return False
                End If
                AttachmentsMaster.DeleteAttachmentsMaster(SessionManager.SelectedValueAttachmentID)
                Dim strAttachmentFilePath As String = (ConfigurationManager.AppSettings("TemplateAttachmentsRootDirectory") & "\" & SessionManager.SelectedValueAttachment).Replace("\\", "\")
                File.Delete(strAttachmentFilePath)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(FormName & " - DeleteAttachment", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
#End Region

    End Class
End Namespace
