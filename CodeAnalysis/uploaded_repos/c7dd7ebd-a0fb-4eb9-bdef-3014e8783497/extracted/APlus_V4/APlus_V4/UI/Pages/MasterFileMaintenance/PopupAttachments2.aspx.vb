#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class PopupAttachments2
        Inherits ApplicationBase

#Region " Constants"
        Private Shared ReadOnly FormName As String = "Popup Attachments"
        Private Shared ReadOnly ProgramName As String = "PopupAttachments2"
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
                                          ddlSite, _
                                          txtPopupAttempts, _
                                          chkPopupActive _
                                         }

            Dim TabKeyDownArr() As String = {Tab(ddlSite, chkPopupActive, "No"), _
                                             Tab(txtPopupAttempts, fil, "No"), _
                                             Tab(chkPopupActive, ddlSite, "Yes"), _
                                             Tab(fil, txtPopupAttempts, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
        Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {txtPopupAttempts, _
                                          chkPopupActive _
                                         }

            Dim TabKeyDownArr() As String = {Tab(chkPopupActive, chkPopupActive, "Yes"), _
                                             Tab(txtPopupAttempts, txtPopupAttempts, "No")}

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

            Master.HeaderMessage = SessionManager.PopupAttachmentMode & " Popup Attachment"
            Master.IconImage = Request.ApplicationPath + "/images/mail_attachment.gif"

            LoadCommonJavaScripts()
            LoadDropDownListBoxes()

            If Not Page.IsPostBack Then
                Select Case SessionManager.PopupAttachmentMode
                    Case "AddRow"
                        LoadAddModeJavaScripts()
                        fil.Focus()
                    Case "EditRow"
                        LoadEditModeJavaScripts()
                        LoadSelectedRecord()
                        UnEnableRecords()
                        txtPopupAttempts.Focus()
                    Case "ViewRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        pnlOKCancel.Visible = False
                        pnlExit.Visible = True
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Popup Attachment.');")
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("PopupAttachments1"))
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

            Select Case SessionManager.PopupAttachmentMode
                Case "AddRow"
                    strFile = fil.PostedFile.FileName
                    blnSuccess = SaveAttachment()
                Case "EditRow"
                    strFile = txtAttachment.Text
                    blnSuccess = UpdateAttachment()
                Case "DeleteRow"
                    strFile = txtAttachment.Text
                    blnSuccess = DeleteAttachment()
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueAttachmentID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.PopupAttachmentMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("PopupAttachments1"), False)
            End If
        End Sub
        Private Sub btnCancel_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnCancel.Click
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
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.PopupAttachmentMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("PopupAttachments1"), False)
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueAttachmentID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.PopupAttachmentMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("PopupAttachments1"), False)
        End Sub
        Private Sub btnClearUserLogins_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnClearUserLogins.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                PopupUserLogins.ClearPopupUserLogins()
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - ClearPopupUserLogins", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
            End Try
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
                SiteMaster.SelectSiteMasterActiveList(ddlSite)
                ddlSite.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadDropDownListBoxes", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
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
                Dim dsHolder As DataTable = AttachmentsMaster.SelectAttachmentsMasterPopup(SessionManager.SelectedValueAttachmentID)

                If Not dsHolder Is Nothing AndAlso dsHolder.Rows.Count > 0 AndAlso dsHolder.Rows.Count > 0 Then
                    Dim dtRow As DataRow = dsHolder.Rows(0)
                    Dim objItem As ListItem

                    txtAttachment.Text = dtRow("Attachment").ToString
                    objItem = ddlSite.Items.FindByValue(dtRow("SiteID").ToString)
                    If Not objItem Is Nothing Then
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

                    txtPopupAttempts.Text = dtRow("PopupAttempts").ToString
                    chkPopupActive.Checked = dtRow("PopupActive")
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

            Select Case SessionManager.PopupAttachmentMode
                Case "DeleteRow", "ViewRow"
                    fil.Visible = False
                    txtAttachment.Visible = True
                    ddlSite.Visible = False
                    txtSite.Visible = True
                    txtPopupAttempts.ReadOnly = True
                    txtPopupAttempts.CssClass = "Textbox_Display"
                    chkPopupActive.Enabled = False
                Case "EditRow"
                    fil.Visible = False
                    txtAttachment.Visible = True
                    ddlSite.Visible = False
                    txtSite.Visible = True
            End Select
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
                    Master.DisplayError(GetTranslationString("noattach", "Attachment File not Selected"))
                    Return False
                End If

                If Not Directory.Exists(ConfigurationManager.AppSettings("PopupAttachmentsRootDirectory")) Then
                    Master.DisplayManualErrors("SaveAttachment", "Popup Attachments Root Directory Does Not Exist", SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                    Return False
                End If

                Try
                    DataAccess.Tables.AttachmentsMaster.InsertAttachmentsMasterPopup(Path.GetFileName(fil.PostedFile.FileName), ddlSite.SelectedItem.Value, Convert.ToInt32(txtPopupAttempts.Text), chkPopupActive.Checked)
                Catch Exc As Exception
                    Master.DisplayErrors("Insert Popup Attachment " & fil.PostedFile.FileName + " Attachment already exists", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                    Return False
                End Try

                Dim strAttachmentFilePath As String = ConfigurationManager.AppSettings("PopupAttachmentsRootDirectory") & "\" & Path.GetFileName(fil.PostedFile.FileName)
                fil.PostedFile.SaveAs(strAttachmentFilePath)
            Catch Exa As System.UnauthorizedAccessException
                Master.DisplayErrors("Insert Popup Attachment", Exa, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                Return False
            Catch Exc As Exception
                Master.DisplayErrors("Insert Popup Attachment", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
            Return True
        End Function
        Private Function UpdateAttachment() As Boolean
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
                DataAccess.Tables.AttachmentsMaster.UpdateAttachmentsMasterPopup(SessionManager.SelectedValueAttachmentID, Convert.ToInt32("0" + txtPopupAttempts.Text), chkPopupActive.Checked)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors("Update Popup Attachment", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
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
                If Not Directory.Exists(ConfigurationManager.AppSettings("PopupAttachmentsRootDirectory")) Then
                    Master.DisplayManualErrors("DeleteAttachment", "Popup Attachments Directory Does Not Exist", SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                    Return False
                End If
                DataAccess.Tables.AttachmentsMaster.DeleteAttachmentsMaster(SessionManager.SelectedValueAttachmentID)
                Dim strAttachmentFilePath As String = (ConfigurationManager.AppSettings("PopupAttachmentsRootDirectory") & "\" & txtAttachment.Text).Replace("\\", "\")
                File.Delete(strAttachmentFilePath)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors("Delete Popup Attachment", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
        End Function
#End Region

    End Class
End Namespace
