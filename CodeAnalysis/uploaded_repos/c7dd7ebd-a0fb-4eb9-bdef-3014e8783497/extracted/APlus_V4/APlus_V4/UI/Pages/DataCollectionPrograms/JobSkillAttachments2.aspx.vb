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
    Partial Class JobSkillAttachments2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Job Skill Document"
        Private Shared ReadOnly ProgramName As String = "JobSkillAttachments2"
        Private Shared ReadOnly DBTableName As String = "JobSkillAttachments"
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
            Dim myTabArray() As Object = {txtAttachment, txtExpandURL}

            Dim TabKeyDownArr() As String = {Tab(txtExpandURL, txtExpandURL, "No"), _
                                             Tab(txtAttachment, txtAttachment, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
#End Region

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, ProgramName, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Master.HeaderMessage = FormName & " - " & SessionManager.JobSkillAttachmentsMode.Replace("Row", "") & " Job Skill"
            Master.IconImage = Request.ApplicationPath + "/images/UserSkillAttachment.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            ClientScript.RegisterStartupScript(Me.GetType, "", "")

            If Not Page.IsPostBack Then
                Select Case SessionManager.JobSkillAttachmentsMode
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        LoadAddModeJavaScripts()
                        txtSkillCategory.Text = SessionManager.AttachmentSkillCategory
                        txtSkill.Text = SessionManager.AttachmentSkill
                        txtAttachment.Focus()
                    Case "DeleteRow"
                        LoadCurrentRecord()
                        UnEnableControls()
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Job Skill Document.');")
                        TransactionHistory1.LockControl = True
                    Case "EditRow"
                        LoadCurrentRecord()
                        UnEnableControls()
                        txtExpandURL.Focus()
                    Case "ViewRow"
                        LoadCurrentRecord()
                        UnEnableControls()
                        pnlOKCancel.Visible = False
                        pnlExit.Visible = True
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("JobSkillMaster2"))
                End Select
            End If
        End Sub
        Private Sub btnOK_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim blnSuccess As Boolean

            Select Case SessionManager.JobSkillAttachmentsMode
                Case "AddRow"
                    blnSuccess = InsertJobSkillAttachment()
                Case "DeleteRow"
                    blnSuccess = DeleteJobSkillAttachment()
                Case "EditRow"
                    blnSuccess = UpdateJobSkillAttachment()
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue3)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue2)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.JobSkillAttachmentsMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("JobSkillAttachments1"), False)
            End If
        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue3)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue2)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.JobSkillAttachmentsMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("JobSkillAttachments1"), False)
        End Sub
        Private Sub btnCancel_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnCancel.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue3)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue2)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.JobSkillAttachmentsMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("JobSkillAttachments1"), False)
        End Sub
#End Region

#Region " Custom Functions"
        Private Sub LoadCurrentRecord()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim objDS As DataTable = JobSkillAttachments.SelectJobSkillAttachment(SessionManager.AttachmentJobSkillID, SessionManager.SelectedValue2)
                Dim objRow As DataRow = objDS.Rows(0)
                txtSkillCategory.Text = objRow("SkillCategory")
                txtSkill.Text = objRow("Skill")
                txtAttachment.Text = objRow("Attachment")
                txtExpandURL.Text = objRow("AttachmentURL")
                txtAttachment.Focus()

                TransactionHistory1.TableName = DBTableName
                TransactionHistory1.RecordID = SessionManager.AttachmentJobSkillID & "," & SessionManager.SelectedValue2

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("Attachment", txtAttachment.Text.Trim())
                objDic.Add("AttachmentURL", txtExpandURL.Text.Trim())
                SessionManager.RecordTransactionCurrentValues = objDic

            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadCurrentRecord", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Function InsertJobSkillAttachment() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
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

                JobSkillAttachments.InsertJobSkillAttachment(SessionManager.AttachmentJobSkillID, txtAttachment.Text.Trim, txtExpandURL.Text.Trim)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.AttachmentJobSkillID & "," & txtAttachment.Text.Trim(), strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertJobSkillAttachment", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateJobSkillAttachment() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
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

                JobSkillAttachments.UpdateJobSkillAttachment(SessionManager.AttachmentJobSkillID, txtAttachment.Text.Trim, txtExpandURL.Text.Trim)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.AttachmentJobSkillID & "," & txtAttachment.Text.Trim(), strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateJobSkillAttachment", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function DeleteJobSkillAttachment() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                JobSkillAttachments.DeleteJobSkillAttachment(SessionManager.AttachmentJobSkillID, txtAttachment.Text.Trim)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.AttachmentJobSkillID & "," & txtAttachment.Text.Trim(), "Job Skill Attachment Deleted", SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteJobSkillAttachment", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
        End Function
        Private Sub UnEnableControls()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Select Case SessionManager.JobSkillAttachmentsMode
                Case "DeleteRow", "ViewRow"
                    txtAttachment.CssClass = "Textbox_Display"
                    txtAttachment.ReadOnly = True
                    txtExpandURL.CssClass = "Textbox_Display"
                    txtExpandURL.ReadOnly = True
                Case "EditRow"
                    txtAttachment.CssClass = "Textbox_Display"
                    txtAttachment.ReadOnly = True
            End Select
        End Sub
        Private Function GetUpdatedValues() As Dictionary(Of String, String)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim objDic As New Dictionary(Of String, String)
            objDic.Add("Attachment", txtAttachment.Text.Trim())
            objDic.Add("AttachmentURL", txtExpandURL.Text.Trim())
            Return objDic
        End Function
#End Region

    End Class
End Namespace
