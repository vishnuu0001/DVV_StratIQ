#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class HelpAttachments2
        Inherits ApplicationBase

#Region " Constant Variables"
        Private Shared ReadOnly FormName As String = "Help Attachments"
        Private Shared ReadOnly ProgramName As String = "HelpAttachments2"
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

            LoadCommonJavaScripts()
            LoadDropDownListBoxes()

            If Not Page.IsPostBack Then
                Select Case SessionManager.HelpAttachmentMode
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
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Help Attachment.');")
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("HelpAttachments1"), False)
                End Select
            End If
        End Sub
        Protected Sub btnOK_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Dim blnSuccess As Boolean

            Select Case SessionManager.HelpAttachmentMode
                Case "AddRow"
                    blnSuccess = SaveAttachment()
                Case "DeleteRow"
                    blnSuccess = DeleteAttachment()
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueAttachmentID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueAttachment)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueCategoryTypeID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.HelpAttachmentMode)

                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("HelpAttachments1"), False)
            End If
        End Sub
        Protected Sub btnCancel_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnCancel.Click, btnExit.Click
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueAttachmentID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueAttachment)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueCategoryTypeID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.HelpAttachmentMode)

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("HelpAttachments1"), False)
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

            AttachmentCategoryTypes.SelectAttachmentCategoryTypesListByAttachmentType(AttachmentTypes.SelectAttachmentTypeIDByType("Help"), ddlCategory)
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

            Dim objItem As ListItem

            txtAttachment.Text = SessionManager.SelectedValueAttachment.Trim
            objItem = ddlCategory.Items.FindByValue(SessionManager.SelectedValueCategoryID)
            If Not objItem Is Nothing Then
                objItem.Selected = True
                txtCategory.Text = objItem.Text
            End If
        End Sub
        Private Sub UnEnableRecords()
            'only called for delete
            fil.Visible = False
            txtAttachment.Visible = True

            ddlCategory.Visible = False
            txtCategory.Visible = True
        End Sub
        Private Function SaveAttachment() As Boolean
            Try
                If fil.PostedFile.FileName.Trim.Length > 0 Then
                    'check the file size
                    Dim iFileSize As Integer = Convert.ToInt32("0" + ConfigurationManager.AppSettings("MaxUploadFileSize").ToString)

                    If fil.PostedFile.ContentLength > iFileSize Then
                        Master.DisplayError(GetTranslationString("filesizetoobig", "File Size must be no greater than ") + (iFileSize / 1024).ToString)

                        Return False
                    End If
                Else
                    Master.DisplayError(GetTranslationString("noattach", "Attachment File not Selected"))

                    Return False
                End If

                'Check whether we have a directory
                If Not Directory.Exists(ConfigurationManager.AppSettings("HelpAttachmentsRootDirectory")) Then
                    Master.DisplayError("Help Attachments Root Directory Does Not Exist")

                    Return False
                End If
                'Check for culture language directory
                Dim strCultureLanguage As String = New System.Globalization.CultureInfo(SessionManager.CulturePref).TwoLetterISOLanguageName
                If Not Directory.Exists(ConfigurationManager.AppSettings("HelpAttachmentsRootDirectory") + strCultureLanguage) Then
                    Master.DisplayError("Help Attachments Directory Does Not Exist")

                    Return False
                End If

                DataAccess.Tables.AttachmentsMaster.InsertAttachmentsMaster(AttachmentTypes.SelectAttachmentTypeIDByType("Help"), Path.GetFileName(fil.PostedFile.FileName), Convert.ToInt32(ddlCategory.SelectedItem.Value), strCultureLanguage, 0)

                'now, move the file
                'Attachment will be saved under same name as the uploaded file 
                Dim strAttachmentFilePath As String = ConfigurationManager.AppSettings("HelpAttachmentsRootDirectory") & strCultureLanguage & "\" & Path.GetFileName(fil.PostedFile.FileName)

                'Save the uploaded file in the appropriate meeting folder
                fil.PostedFile.SaveAs(strAttachmentFilePath)
            Catch Exa As System.UnauthorizedAccessException
                Master.DisplayErrors("Insert Help Attachment", Exa, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)

                Return False
            Catch Exc As Exception
                Master.DisplayErrors("Insert Help Attachment", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)

                Return False
            End Try

            Return True
        End Function
        Private Function DeleteAttachment() As Boolean
            Try
                'Check whether we have a directory
                If Not Directory.Exists(ConfigurationManager.AppSettings("HelpAttachmentsRootDirectory")) Then
                    Master.DisplayError("Help Attachments Directory Does Not Exist")

                    Return False
                End If

                DataAccess.Tables.AttachmentsMaster.DeleteAttachmentsMaster(SessionManager.SelectedValueAttachmentID)

                Dim strAttachmentFilePath As String = ConfigurationManager.AppSettings("HelpAttachmentsRootDirectory") & "\" & SessionManager.SelectedValueAttachment.Replace("\\", "\")
                File.Delete(strAttachmentFilePath)
            Catch Exc As Exception
                Master.DisplayErrors("Delete Help Attachment", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)

                Return False
            End Try

            Return True
        End Function
#End Region

    End Class
End Namespace

