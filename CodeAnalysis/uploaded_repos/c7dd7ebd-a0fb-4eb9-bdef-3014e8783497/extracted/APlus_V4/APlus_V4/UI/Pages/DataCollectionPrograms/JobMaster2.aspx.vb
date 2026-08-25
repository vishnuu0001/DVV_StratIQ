#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class JobMaster2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Job Master"
        Private Shared ReadOnly ProgramName As String = "JobMaster2"
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

            Master.HeaderMessage = FormName & " - " & SessionManager.JobMode.Replace("Row", "") & " Job"
            Master.IconImage = Request.ApplicationPath + "/images/TeamAction.gif"

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnExit.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            TrainingMatrixLegend.JobID = SessionManager.SelectedValueJob

            If Not Page.IsPostBack Then
                'load job specific data here
                BindDropDownLists()
                LoadSelectedRecord()
            End If

            Select Case SessionManager.JobMode
                Case "EditRow"
                    Master.HeaderMessage = FormName
                    If ProgramSecurity.CanUserAccessProgram(SessionManager.UserID, "JobMaster3") Then
                        btnEdit.Visible = True
                    End If
                Case "EditRowMatrix"
                    Master.HeaderMessage = "My Teams Training Matrix Master"
                    lblJob.Text = "Training Matrix"
                    btnJobSkills.Text = "Training Matrix Skills"
                    btnEdit.Text = "Edit Training Matrix"
                    If ProgramSecurity.CanUserAccessProgram(SessionManager.UserID, "JobMaster3") Then
                        btnEdit.Visible = True
                    End If
                Case "ViewRow"
                    Master.HeaderMessage = FormName
                    btnEdit.Visible = False
                Case "ViewRowMatrix"
                    Master.HeaderMessage = "My Teams Training Matrix Master"
                    lblJob.Text = "Training Matrix"
                    btnJobSkills.Text = "Training Matrix Skills"
                    btnEdit.Visible = False
            End Select

            BindGrid()
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueJob)
            Select Case SessionManager.JobMode
                Case "ViewRow", "EditRow"
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.JobMode)
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("JobMaster1"), False)
                Case "ViewRowMatrix", "EditRowMatrix"
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.JobMode)
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("MyTeamsTrainingMatrixMaster"), False)
            End Select
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueJob)
            Select Case SessionManager.JobMode
                Case "ViewRow", "EditRow"
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.JobMode)
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("JobMaster1"), False)
                Case "ViewRowMatrix", "EditRowMatrix"
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.JobMode)
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("MyTeamsTrainingMatrixMaster"), False)
            End Select
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueJob)
            Select Case SessionManager.JobMode
                Case "ViewRow", "EditRow"
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.JobMode)
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("JobMaster1"), False)
                Case "ViewRowMatrix", "EditRowMatrix"
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.JobMode)
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("MyTeamsTrainingMatrixMaster"), False)
            End Select
        End Sub

        Private Sub btnJobSkills_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnJobSkills.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try
            SessionManager.MasterControlExitProgram = "JobMaster2"
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("JobSkillMaster1"), False)
        End Sub

        Private Sub Link_Click(ByVal sender As System.Object, ByVal e As WebControls.CommandEventArgs)
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
                Case "EditRow", "EditRowMatrix"
                    SessionManager.JobSkillMode = "EditRowJobMaster"
                    SessionManager.SelectedValueJobSkillID = CType(sender, LinkButton).CommandArgument
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("JobSkillMaster2"), False)
            End Select
        End Sub

        Private Sub btnEdit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnEdit.Click
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
                Case "ViewRow"
                    SessionManager.JobMode = "EditRow"
                Case "ViewRowMatrix"
                    SessionManager.JobMode = "EditRowMatrix"
            End Select

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("JobMaster3"), False)
        End Sub
#End Region

#Region " Custom Methods"
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
                Master.DisplayErrors(ProgramName & " - BindDropDownLists", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
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
                Dim objDS As DataTable = JobMaster.SelectJob(SessionManager.SelectedValueJob)
                Dim objItem As ListItem
                Dim objDR As DataRow

                If Not IsNothing(objDS) Then
                    If objDS.Rows.Count > 0 Then
                        txtJob.Text = SessionManager.SelectedValueJobName
                        objDR = objDS.Rows(0)
                        objItem = ddlRatingType.Items.FindByValue(objDR("RatingType").ToString)
                        If Not IsNothing(objItem) Then
                            objItem.Selected = True
                            txtRatingType.Text = objItem.Text
                        End If

                        objItem = ddlTeam.Items.FindByValue(objDR("TeamID").ToString)
                        If Not IsNothing(objItem) Then
                            objItem.Selected = True
                            txtTeam.Text = objItem.Text
                        End If
                        If txtTeam.Text.Trim.Length = 0 Then
                            txtTeam.Visible = False
                            lblTeam.Visible = False
                        End If
                    End If
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
            End Try

            UnEnableControls()
        End Sub
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

            pnlExit.Visible = True
            pnlOKCancel.Visible = False

            Select Case SessionManager.JobMode
                Case "EditRow", "EditMatrix"
                    btnJobSkills.Visible = True
                Case "ViewRow", "ViewMatrix"
                    btnJobSkills.Visible = False
            End Select
        End Sub
        Private Sub BindGrid()
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
                SessionManager.RatingScale = "False"
                ckShowValues.Enabled = True

                BindRatingsValues()

                If ckShowValues.Checked Then
                    SessionManager.ShowValues = "True"
                Else
                    SessionManager.ShowValues = "False"
                End If

                If ckCriteria.Checked Then
                    SessionManager.ShowCriteria = "True"
                Else
                    SessionManager.ShowCriteria = "False"
                End If

                If ckAttachments.Checked Then
                    SessionManager.ShowAttachments = "True"
                Else
                    SessionManager.ShowAttachments = "False"
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindGrid", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
            End Try
        End Sub
        Private Sub BindRatingsValues()
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
                Dim strJob As String = SessionManager.SelectedValueJobName
                Dim objDT As DataTable = JobMaster.SelectJobDetail(SessionManager.SelectedValueJob)
                Dim objDTSkills As DataTable = SkillRatingMaster.SelectSkillRatingsByJob(SessionManager.SelectedValueJob)
                Dim objDSAttachments As DataTable
                Dim objRow As TableRow
                Dim objCell As TableCell
                Dim ctlLink As LinkButton
                Dim bShowValues As Boolean = ckShowValues.Checked
                Dim bShowCritera As Boolean = ckCriteria.Checked
                Dim bShowAttachments As Boolean = ckAttachments.Checked
                Dim bEdit As Boolean = SessionManager.IsAdministrator = "True"

                If SessionManager.JobMode = "ViewRow" Or SessionManager.JobMode = "ViewRowMatrix" Then
                    bEdit = False
                End If

                If objDT IsNot Nothing AndAlso objDT.Rows.Count > 0 Then
                    'get the skills table
                    Dim objTable As DataTable = objDT
                    Dim iColumns As Integer = objTable.Columns.Count

                    'go through the table and create grid
                    'create header row first
                    objRow = New TableRow

                    objCell = New TableCell
                    objCell.HorizontalAlign = HorizontalAlign.Center
                    objCell.Font.Bold = True
                    objCell.BorderStyle = BorderStyle.Solid
                    objCell.BorderWidth = New Unit(1)
                    objCell.BorderColor = Drawing.Color.Black
                    objCell.Width = New Unit(250)
                    objCell.Text = strJob
                    objRow.Cells.Add(objCell)

                    If bShowCritera Then
                        objCell = New TableCell
                        objCell.BorderStyle = BorderStyle.Solid
                        objCell.BorderWidth = New Unit(1)
                        objCell.BorderColor = Drawing.Color.Black
                        objCell.HorizontalAlign = HorizontalAlign.Center
                        objCell.Width = New Unit(300)
                        objCell.Font.Bold = True
                        objCell.Text = "Criteria"
                        objRow.Cells.Add(objCell)
                    End If

                    If bShowAttachments Then
                        objCell = New TableCell
                        objCell.BorderStyle = BorderStyle.Solid
                        objCell.BorderWidth = New Unit(1)
                        objCell.BorderColor = Drawing.Color.Black
                        objCell.HorizontalAlign = HorizontalAlign.Center
                        objCell.Width = New Unit(200)
                        objCell.Font.Bold = True
                        objCell.Text = "Skill Attachments"
                        objRow.Cells.Add(objCell)
                    End If

                    If bShowValues Then
                        objCell = New TableCell
                        objCell.BorderStyle = BorderStyle.Solid
                        objCell.BorderWidth = New Unit(1)
                        objCell.BorderColor = Drawing.Color.Black
                        objCell.HorizontalAlign = HorizontalAlign.Center
                        objCell.Width = New Unit(55)
                        objCell.Font.Bold = True
                        objCell.Text = "Required"
                        objRow.Cells.Add(objCell)

                        objCell = New TableCell
                        objCell.BorderStyle = BorderStyle.Solid
                        objCell.BorderWidth = New Unit(1)
                        objCell.BorderColor = Drawing.Color.Black
                        objCell.HorizontalAlign = HorizontalAlign.Center
                        objCell.Font.Bold = True
                        objCell.Width = New Unit(55)
                        objCell.Text = "Desired"
                        objRow.Cells.Add(objCell)
                    End If

                    If bEdit Then
                        'add the edit column
                        objCell = New TableCell
                        objCell.BorderStyle = BorderStyle.Solid
                        objCell.BorderWidth = New Unit(1)
                        objCell.BorderColor = Drawing.Color.Black
                        objCell.HorizontalAlign = HorizontalAlign.Center
                        objCell.Font.Bold = True
                        objCell.Width = New Unit(55)
                        objCell.Text = ""
                        objRow.Cells.Add(objCell)
                    End If

                    tblSkills.Rows.Add(objRow)

                    'now fill the skills and ratings
                    Dim strCat As String = ""
                    For Each objDataRow As DataRow In objTable.Rows
                        If strCat <> objDataRow("SkillCategory").ToString Then
                            'new category
                            objRow = New TableRow
                            objCell = New TableCell
                            objCell.Width = New Unit(250)
                            objCell.Font.Bold = True
                            objCell.HorizontalAlign = HorizontalAlign.Center
                            objCell.Text = objDataRow("SkillCategory").ToString
                            objRow.Cells.Add(objCell)

                            tblSkills.Rows.Add(objRow)
                        End If

                        'Skill
                        objRow = New TableRow
                        objCell = New TableCell
                        objCell.Width = New Unit(250)
                        objCell.HorizontalAlign = HorizontalAlign.Left
                        objCell.VerticalAlign = VerticalAlign.Top
                        objCell.BorderStyle = BorderStyle.Solid
                        objCell.BorderWidth = New Unit(1)
                        objCell.BorderColor = Drawing.Color.Black
                        objCell.Text = objDataRow("Skill").ToString
                        objRow.Cells.Add(objCell)
                        strCat = objDataRow("SkillCategory").ToString

                        If bShowCritera Then
                            objCell = New TableCell
                            objCell.Width = New Unit(300)
                            objCell.HorizontalAlign = HorizontalAlign.Left
                            objCell.BorderStyle = BorderStyle.Solid
                            objCell.BorderWidth = New Unit(1)
                            objCell.BorderColor = Drawing.Color.Black
                            If (objDataRow("AssessmentCriteria") Is DBNull.Value) Then
                                objCell.Text = ""
                            Else
                                objCell.Text = Replace(objDataRow("AssessmentCriteria").ToString, vbCrLf, "<br>")
                            End If
                            objRow.Cells.Add(objCell)
                        End If

                        If bShowAttachments Then
                            objCell = New TableCell
                            objCell.Width = New Unit(200)
                            objCell.HorizontalAlign = HorizontalAlign.Left
                            objCell.BorderStyle = BorderStyle.Solid
                            objCell.BorderWidth = New Unit(1)
                            objCell.BorderColor = Drawing.Color.Black

                            objDSAttachments = JobSkillAttachments.SelectJobSkillAttachments(SessionManager.SelectedValueJob, objDataRow("Skill").ToString)
                            If objDSAttachments.Rows.Count > 0 Then
                                For Each dtRow As DataRow In objDSAttachments.Rows
                                    ctlLink = New LinkButton
                                    ctlLink.Text = dtRow("Attachment").ToString
                                    ctlLink.Attributes.Add("onclick", "javascript:LaunchExplorer('" & dtRow("AttachmentURL").ToString.Replace("\", "\\") & "');")

                                    objCell.Controls.Add(ctlLink)
                                    objCell.Controls.Add(New LiteralControl("<BR>"))
                                Next dtRow
                            Else
                                objCell.Text = ""
                            End If

                            objRow.Cells.Add(objCell)
                        End If

                        If bShowValues Then
                            'required
                            objCell = New TableCell
                            objCell.BorderStyle = BorderStyle.Solid
                            objCell.BorderWidth = New Unit(1)
                            objCell.BorderColor = Drawing.Color.Black
                            objCell.HorizontalAlign = HorizontalAlign.Center
                            objCell.VerticalAlign = VerticalAlign.Top
                            objCell.Height = New Unit(15)
                            objCell.Text = objDataRow.Item("RequiredRating").ToString
                            'if we have a color use if
                            For Each SkillRow As DataRow In objDTSkills.Rows
                                If SkillRow("SkillRating").ToString = objCell.Text Then
                                    If Not (SkillRow("DisplayColor") Is DBNull.Value) Then
                                        Try
                                            objCell.BackColor = Drawing.Color.FromName(SkillRow("DisplayColor"))
                                        Catch ex As Exception
                                            'no need to do anything here
                                        End Try
                                    End If

                                    Exit For
                                End If
                            Next
                            objRow.Cells.Add(objCell)

                            'desired
                            objCell = New TableCell
                            objCell.BorderStyle = BorderStyle.Solid
                            objCell.BorderWidth = New Unit(1)
                            objCell.BorderColor = Drawing.Color.Black
                            objCell.HorizontalAlign = HorizontalAlign.Center
                            objCell.VerticalAlign = VerticalAlign.Top
                            objCell.Height = New Unit(15)
                            objCell.Text = objDataRow.Item("DesiredRating").ToString
                            'if we have a color use if
                            For Each SkillRow As DataRow In objDTSkills.Rows
                                If SkillRow("SkillRating").ToString = objCell.Text Then
                                    If Not (SkillRow("DisplayColor") Is DBNull.Value) Then
                                        Try
                                            objCell.BackColor = Drawing.Color.FromName(SkillRow("DisplayColor"))
                                        Catch ex As Exception
                                            'no need to do anything here
                                        End Try
                                    End If

                                    Exit For
                                End If
                            Next
                            objRow.Cells.Add(objCell)
                        End If

                        If bEdit Then
                            'add the edit column
                            objCell = New TableCell
                            objCell.BorderStyle = BorderStyle.Solid
                            objCell.BorderWidth = New Unit(1)
                            objCell.BorderColor = Drawing.Color.Black
                            objCell.HorizontalAlign = HorizontalAlign.Center
                            objCell.Width = New Unit(55)

                            ctlLink = New LinkButton
                            AddHandler ctlLink.Command, AddressOf Link_Click
                            ctlLink.Text = "Edit"
                            ctlLink.CommandArgument = objDataRow.Item("JobSkillID").ToString
                            ctlLink.ID = objDataRow.Item("JobSkillID").ToString

                            objCell.Controls.Add(ctlLink)

                            objRow.Cells.Add(objCell)
                        End If

                        tblSkills.Rows.Add(objRow)
                    Next
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindRatingsValues", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
            End Try
        End Sub
#End Region

    End Class
End Namespace
