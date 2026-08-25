#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class TrainingDocumentAttachments2
        Inherits ApplicationBase

#Region " Constants"
        Private Shared ReadOnly FormName As String = "Training Attachments"
        Private Shared ReadOnly ProgramName As String = "TrainingDocumentAttachments2"
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
            Dim myTabArray() As Object = {fil, ddlCategory}

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

            Master.HeaderMessage = FormName
            Master.IconImage = Request.ApplicationPath + "/images/attachfile.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()
            LoadDropDownListBoxes()

            If Not Page.IsPostBack Then
                If New System.Globalization.CultureInfo(SessionManager.CulturePref).TwoLetterISOLanguageName = "en" Then
                    trMasterAttachment.Visible = False
                Else
                    trMasterAttachment.Visible = True
                End If

                Select Case SessionManager.TrainingAttachmentMode
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
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Training Document Attachment.');")
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TrainingDocumentAttachments1"), False)
                End Select
            End If
        End Sub
        Private Sub btnOK_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Dim blnSuccess As Boolean
            Dim strFile As String = String.Empty

            Select Case SessionManager.TrainingAttachmentMode
                Case "AddRow"
                    strFile = fil.PostedFile.FileName
                    blnSuccess = SaveAttachment()
                Case "DeleteRow"
                    strFile = SessionManager.SelectedValueAttachment.ToString
                    blnSuccess = DeleteAttachment()
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueAttachmentID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TrainingAttachmentMode)

                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TrainingDocumentAttachments1"), False)
            End If
        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click, btnCancel.Click
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueAttachmentID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TrainingAttachmentMode)

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TrainingDocumentAttachments1"), False)
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadDropDownListBoxes()
            AttachmentCategoryTypes.SelectAttachmentCategoryTypesListByAttachmentType(AttachmentTypes.SelectAttachmentTypeIDByType("Training"), ddlCategory)
            AttachmentsMaster.SelectAttachmentsByTypeList(AttachmentTypes.SelectAttachmentTypeIDByType("Training"), "en", ddlMasterAttachment)
        End Sub
        Private Sub LoadSelectedRecord()
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
                If fil.PostedFile.FileName.Trim.Length > 0 Then
                    'check the file size
                    Dim iFileSize As Integer = Convert.ToInt32("0" + ConfigurationManager.AppSettings("MaxUploadFileSize").ToString)

                    If fil.PostedFile.ContentLength > iFileSize Then
                        Master.DisplayError("File Size must be no greater than " + (iFileSize / 1024).ToString)

                        Return False
                    End If
                Else
                    Master.DisplayError("Attachment File not Selected")

                    Return False
                End If

                'Check whether we have a directory
                If Not Directory.Exists(ConfigurationManager.AppSettings("TrainingAttachmentsRootDirectory")) Then
                    Master.DisplayManualErrors("SaveAttachment", "Training Document Attachments Root Directory Does Not Exist", SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)

                    Return False
                End If
                'Check for culture language directory
                Dim strCultureLanguage As String = New System.Globalization.CultureInfo(SessionManager.CulturePref).TwoLetterISOLanguageName
                If Not Directory.Exists(ConfigurationManager.AppSettings("TrainingAttachmentsRootDirectory") + strCultureLanguage) Then
                    Master.DisplayManualErrors("SaveAttachment", "Training Document Attachments Directory Does Not Exist", SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)

                    Return False
                End If

                Dim iMasterAttachmentID As Integer = 0
                If ddlMasterAttachment.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlMasterAttachment.SelectedItem.Value) Then
                    iMasterAttachmentID = ddlMasterAttachment.SelectedItem.Value
                End If

                AttachmentsMaster.InsertAttachmentsMaster(AttachmentTypes.SelectAttachmentTypeIDByType("Training"), Path.GetFileName(fil.PostedFile.FileName), Convert.ToInt32(ddlCategory.SelectedItem.Value), strCultureLanguage, iMasterAttachmentID)

                'now, move the file
                'Attachment will be saved under same name as the uploaded file 
                Dim strAttachmentFilePath As String = ConfigurationManager.AppSettings("TrainingAttachmentsRootDirectory") & strCultureLanguage & "\" & Path.GetFileName(fil.PostedFile.FileName)

                'Save the uploaded file in the appropriate meeting folder
                fil.PostedFile.SaveAs(strAttachmentFilePath)
            Catch Exa As System.UnauthorizedAccessException
                Master.DisplayErrors("Insert Training Document Attachment", Exa, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            Catch Exc As Exception
                Master.DisplayErrors("Insert Training Document Attachment", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
            Return True
        End Function
        Private Function DeleteAttachment() As Boolean
            Try
                'Check whether we have a directory
                If Not Directory.Exists(ConfigurationManager.AppSettings("TrainingAttachmentsRootDirectory")) Then
                    Master.DisplayManualErrors("DeleteAttachment", "Training Document Attachments Directory Does Not Exist", SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)

                    Return False
                End If

                'Delete From database
                'Convert.ToInt32(ddlTemplateFile.SelectedItem.Value)
                DataAccess.Tables.AttachmentsMaster.DeleteAttachmentsMaster(SessionManager.SelectedValueAttachmentID)

                Dim strAttachmentFilePath As String = (ConfigurationManager.AppSettings("TrainingAttachmentsRootDirectory") & "\" & SessionManager.SelectedValueAttachment).Replace("\\", "\")

                File.Delete(strAttachmentFilePath)
            Catch Exc As Exception
                Master.DisplayErrors("Delete Training Document Attachment", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try

            Return True
        End Function
#End Region

    End Class
End Namespace