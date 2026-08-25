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
    Partial Class JobMaster3
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Job Master"
        Private Shared ReadOnly ProgramName As String = "JobMaster3"
        Private Shared ReadOnly DBTableName As String = "JobMaster"
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel"}
            Dim OutMessageArr() As String = {"", ""}

            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event)")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
        End Sub
        Private Sub LoadAddModeJavaScripts()
            Dim myTabArray() As Object = {txtJob, ddlRatingType}

            Dim TabKeyDownArr() As String = {Tab(ddlRatingType, ddlRatingType, "No"), _
                                             Tab(txtJob, txtJob, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
        Private Sub LoadAddMatrixModeJavaScripts()
            Dim myTabArray() As Object = {txtJob, ddlRatingType, ddlTeam}

            Dim TabKeyDownArr() As String = {Tab(ddlRatingType, ddlTeam, "No"), _
                                             Tab(ddlTeam, txtJob, "No"), _
                                             Tab(txtJob, ddlRatingType, "No")}

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

            Master.IconImage = Request.ApplicationPath + "/images/TeamAction.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")
            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                BindDropDownLists()

                Select Case SessionManager.JobMode
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        Master.HeaderMessage = FormName & " - " & SessionManager.JobMode.Replace("Row", "") & " Job"
                        pnlTeam.Visible = False
                        reqTeam.Enabled = False
                        LoadAddModeJavaScripts()
                        txtJobID.Text = "New"
                        txtJob.Focus()
                    Case "AddMatrix"
                        TransactionHistory1.Visible = False
                        Master.HeaderMessage = FormName & " - " & SessionManager.JobMode.Replace("Row", "") & " Team Training Matrices"
                        LoadAddMatrixModeJavaScripts()
                        txtJobID.Text = "New"
                        lblJobID.Text = "Training Matrix ID:"
                        lblJob.Text = "Training Matrix:"
                        reqJob.ErrorMessage = "Enter Training Matrix Name"
                        txtJob.Focus()
                    Case "EditRow"
                        Master.HeaderMessage = FormName & " - " & SessionManager.JobMode.Replace("Row", "") & " Job"
                        LoadAddModeJavaScripts()
                        LoadSelectedRecord()
                        reqTeam.Enabled = False
                        txtJob.Focus()
                    Case "EditMatrix"
                        Master.HeaderMessage = FormName & " - " & SessionManager.JobMode.Replace("Row", "") & " Team Training Matrices"
                        LoadAddMatrixModeJavaScripts()
                        LoadSelectedRecord()
                        lblJobID.Text = "Training Matrix ID:"
                        lblJob.Text = "Training Matrix:"
                        reqJob.ErrorMessage = "Enter Training Matrix Name"
                        txtJob.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("JobMaster1"), False)
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

            Select Case SessionManager.JobMode
                Case "AddRow", "AddMatrix"
                    blnSuccess = InsertJob()
                Case "EditRow", "EditMatrix"
                    blnSuccess = UpdateJob()
            End Select

            If blnSuccess Then
                Select Case SessionManager.JobMode
                    Case "AddRow"
                        SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.JobMode)
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("JobMaster1"), False)
                    Case "AddMatrix"
                        SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.JobMode)
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("MyTeamsTrainingMatrixMaster"), False)
                    Case "EditRow", "EditMatrix"
                        SessionManager.SelectedValueJobName = txtJob.Text
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("JobMaster2"), False)
                End Select
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

            Select Case SessionManager.JobMode
                Case "AddRow"
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.JobMode)
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("JobMaster1"), False)
                Case "AddMatrix"
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.JobMode)
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("MyTeamsTrainingMatrixMaster"), False)
                Case "EditRow", "EditMatrix"
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("JobMaster2"), False)
            End Select
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
                Teams.SelectTeamList(ddlTeam, SessionManager.UserID, SessionManager.WorkingSiteID)
                ddlTeam.Items.Insert(0, "")
                SkillRatingMaster.SelectSkillRatingMasterList(ddlRatingType)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindDropDownLists", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
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
                Dim dt As DataTable = JobMaster.SelectJob(SessionManager.SelectedValueJob)

                If Not dt Is Nothing AndAlso dt.Rows.Count > 0 Then
                    Dim dr As DataRow = dt.Rows(0)

                    txtJobID.Text = SessionManager.SelectedValueJob
                    txtOldJobName.Text = dr("Job").ToString
                    txtJob.Text = dr("Job").ToString()

                    Dim objItem As ListItem

                    objItem = ddlRatingType.Items.FindByValue(dr("RatingType").ToString())
                    If Not objItem Is Nothing Then
                        objItem.Selected = True
                    End If

                    objItem = ddlTeam.Items.FindByValue(dr("TeamID").ToString())
                    If Not objItem Is Nothing Then
                        objItem.Selected = True
                    End If

                    TransactionHistory1.TableName = DBTableName
                    TransactionHistory1.RecordID = SessionManager.SelectedValueJob

                    Dim objDic As New Dictionary(Of String, String)
                    objDic.Add("Job", txtJob.Text.Trim())
                    objDic.Add("Site", SessionManager.WorkingSite.Trim())
                    objDic.Add("RatingType", ddlRatingType.SelectedItem.Text.Trim())
                    objDic.Add("Team", ddlTeam.SelectedItem.Text.Trim())
                    SessionManager.RecordTransactionCurrentValues = objDic
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
            End Try
        End Sub
        Private Function InsertJob() As Boolean
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
                Dim intResult As Integer = JobMaster.InsertJob(txtJob.Text, SessionManager.WorkingSiteID, ddlRatingType.SelectedItem.Value, ddlTeam.SelectedItem.Value)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, intResult, strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertJob", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateJob() As Boolean
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

                JobMaster.UpdateJob(SessionManager.SelectedValueJob, txtJob.Text, ddlRatingType.SelectedItem.Value, ddlTeam.SelectedItem.Value)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueJob, strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateJob", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
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
            objDic.Add("Job", txtJob.Text.Trim())
            objDic.Add("Site", SessionManager.WorkingSite.Trim())
            objDic.Add("RatingType", ddlRatingType.SelectedItem.Text.Trim())
            If ddlTeam.Visible AndAlso ddlTeam.SelectedItem IsNot Nothing Then
                objDic.Add("Team", ddlTeam.SelectedItem.Text.Trim())
            Else
                objDic.Add("Team", "")
            End If

            Return objDic
        End Function
#End Region

    End Class
End Namespace
