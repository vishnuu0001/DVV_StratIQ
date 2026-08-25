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
    Partial Class JobSkillMaster2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Job Skill Master"
        Private Shared ReadOnly ProgramName As String = "JobSkillMaster2"
        Private Shared ReadOnly DBTableName As String = "JobSkillMaster"
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
        Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {ddlSkillCategory, txtSkill, txtExpandCriteria, txtSequence, _
                                          txtRequiredRating, txtDesiredRating}

            Dim TabKeyDownArr() As String = {Tab(txtSkill, txtDesiredRating, "No"), _
                                             Tab(txtExpandCriteria, ddlSkillCategory, "No"), _
                                             Tab(txtSequence, txtSkill, "No"), _
                                             Tab(txtRequiredRating, txtExpandCriteria, "Yes"), _
                                             Tab(txtDesiredRating, txtSequence, "Yes"), _
                                             Tab(ddlSkillCategory, txtRequiredRating, "Yes")}

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

            Master.HeaderMessage = FormName & " - " & SessionManager.JobSkillMode.Replace("Row", "") & " Job"
            Master.IconImage = Request.ApplicationPath + "/images/UserSkill.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            'check the MasterControlExitProgram variable
            If Not IsNothing(SessionManager.MasterControlExitProgram2) Then
                If SessionManager.MasterControlExitProgram2 <> "" Then
                    SessionManager.MasterControlExitProgram = SessionManager.MasterControlExitProgram2
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.MasterControlExitProgram2)
                End If
            End If

            LoadCommonJavaScripts()
            txtJob.Text = SessionManager.SelectedValueJobName.ToString
            TrainingMatrixLegend1.JobID = SessionManager.SelectedValueJob

            If Not Page.IsPostBack Then
                BindDropDownLists()

                Select Case SessionManager.JobSkillMode
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        lblDelete.Visible = True
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Job Skill.');")
                        TransactionHistory1.LockControl = True
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        LoadEditModeJavaScripts()
                        ddlSkillCategory.Visible = True
                        txtSkillCategory.Visible = False
                        btnAttachments2.Visible = False
                        txtSequence.Text = JobSkillMaster.GetNextJobSkillSequenceNumber(SessionManager.SelectedValueJob).ToString
                        ddlSkillCategory.Focus()
                    Case "EditRow", "EditRowJobMaster"
                        LoadEditModeJavaScripts()
                        LoadSelectedRecord()
                        ddlSkillCategory.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("OPIMasterMaintenance"), False)
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

            Select Case SessionManager.JobSkillMode
                Case "DeleteRow"
                    blnSuccess = DeleteJobSkill()
                Case "AddRow"
                    blnSuccess = InsertJobSkill()
                Case "EditRow", "EditRowJobMaster"
                    blnSuccess = UpdateJobSkill()
            End Select

            If blnSuccess Then
                Dim strMode As String = SessionManager.JobSkillMode

                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueJobSkillID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.JobSkillMode)
                If strMode = "EditRowJobMaster" Then
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("JobMaster2"), False)
                Else
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("JobSkillMaster1"), False)
                End If
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

            Dim strMode As String = SessionManager.JobSkillMode
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueJobSkillID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.JobSkillMode)
            If strMode = "EditRowJobMaster" Then
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("JobMaster2"), False)
            Else
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("JobSkillMaster1"), False)
            End If
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

            Dim strMode As String = SessionManager.JobSkillMode
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueJobSkillID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.JobSkillMode)
            If strMode = "EditRowJobMaster" Then
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("JobMaster2"), False)
            Else
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("JobSkillMaster1"), False)
            End If
        End Sub

        Private Sub btnAttachments_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnAttachments.Click, btnAttachments2.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.JobSkillMode = "EditRow" Then
                If UpdateJobSkill() Then
                    SessionManager.AttachmentJobSkillID = SessionManager.SelectedValueJobSkillID
                    SessionManager.AttachmentSkillCategory = txtSkillCategory.Text
                    SessionManager.AttachmentSkill = txtSkill.Text

                    SessionManager.MasterControlExitProgram2 = SessionManager.MasterControlExitProgram
                    SessionManager.MasterControlExitProgram = "JobSkillMaster2"

                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("JobSkillAttachments1"), False)
                End If
            Else
                SessionManager.AttachmentJobSkillID = SessionManager.SelectedValueJobSkillID
                SessionManager.AttachmentSkillCategory = txtSkillCategory.Text
                SessionManager.AttachmentSkill = txtSkill.Text

                SessionManager.MasterControlExitProgram2 = SessionManager.MasterControlExitProgram
                SessionManager.MasterControlExitProgram = "JobSkillMaster2"

                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("JobSkillAttachments1"), False)
            End If
        End Sub
#End Region

#Region " Custom Functions"
        Private Sub BindDropDownLists()
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
                SkillCategoryMaster.SelectSkillCategoryMasterList(ddlSkillCategory)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindDropDownLists", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub LoadSelectedRecord()
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
                Dim ds As DataTable = JobSkillMaster.SelectJobSkill(SessionManager.SelectedValueJobSkillID)
                Dim dr As DataRow = ds.Rows(0)
                Dim objItem As ListItem

                objItem = ddlSkillCategory.Items.FindByValue(dr("SkillCategoryID"))
                If Not objItem Is Nothing Then
                    objItem.Selected = True
                    txtSkillCategory.Text = objItem.Text
                End If

                txtSkill.Text = dr("Skill").ToString
                txtExpandCriteria.Text = dr("AssessmentCriteria").ToString
                txtSequence.Text = dr("Sequence").ToString
                txtRequiredRating.Text = dr("RequiredRating").ToString
                txtDesiredRating.Text = dr("DesiredRating").ToString

                TransactionHistory1.TableName = DBTableName
                TransactionHistory1.RecordID = SessionManager.SelectedValueJobSkillID

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("SkillCategory", ddlSkillCategory.SelectedItem.Text.Trim())
                objDic.Add("Skill", txtSkill.Text.Trim())
                objDic.Add("AssessmentCriteria", txtExpandCriteria.Text.Trim())
                objDic.Add("Sequence", txtSequence.Text.Trim())
                objDic.Add("RequiredRating", txtRequiredRating.Text.Trim())
                objDic.Add("DesiredRating", txtDesiredRating.Text.Trim())
                SessionManager.RecordTransactionCurrentValues = objDic
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub UnEnableRecords()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.JobSkillMode = "ViewRow" Then
                pnlOKCancel.Visible = False
            ElseIf SessionManager.JobSkillMode = "DeleteRow" Then
                btnAttachments2.Visible = False
            End If
            ddlSkillCategory.Visible = False
            txtSkillCategory.Visible = True
            txtSkill.CssClass = "Textbox_Display"
            txtSkill.ReadOnly = True
            txtExpandCriteria.CssClass = "Textbox_Display"
            txtExpandCriteria.ReadOnly = True
            txtSequence.CssClass = "Textbox_Display"
            txtSequence.ReadOnly = True
            txtRequiredRating.CssClass = "Textbox_Display"
            txtRequiredRating.ReadOnly = True
            txtDesiredRating.CssClass = "Textbox_Display"
            txtDesiredRating.ReadOnly = True
        End Sub
        Private Function InsertJobSkill() As Boolean
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

                Dim intResult As Integer = JobSkillMaster.InsertJobSkill(SessionManager.SelectedValueJob, ddlSkillCategory.SelectedItem.Value, txtSkill.Text.Trim, txtExpandCriteria.Text.Trim, txtSequence.Text, txtRequiredRating.Text, txtDesiredRating.Text)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, intResult, strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertJobSkill", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateJobSkill() As Boolean
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

                JobSkillMaster.UpdateJobSkill(SessionManager.SelectedValueJobSkillID, ddlSkillCategory.SelectedItem.Value, txtSkill.Text, txtExpandCriteria.Text, txtSequence.Text, txtRequiredRating.Text, txtDesiredRating.Text)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueJobSkillID, strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateJobSkill", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function DeleteJobSkill() As Boolean
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
                JobSkillMaster.DeleteJobSkill(SessionManager.SelectedValueJobSkillID)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueJobSkillID, "Job Skill Deleted", SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteJobSkill", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
        End Function
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
            objDic.Add("SkillCategory", ddlSkillCategory.SelectedItem.Text.Trim())
            objDic.Add("Skill", txtSkill.Text.Trim())
            objDic.Add("AssessmentCriteria", txtExpandCriteria.Text.Trim())
            objDic.Add("Sequence", txtSequence.Text.Trim())
            objDic.Add("RequiredRating", txtRequiredRating.Text.Trim())
            objDic.Add("DesiredRating", txtDesiredRating.Text.Trim())
            Return objDic
        End Function
#End Region

    End Class
End Namespace
