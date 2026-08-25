#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports System.Drawing

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class UserSkillRatings1
        Inherits ApplicationBase

#Region " Constants"
        Private Shared ReadOnly FormName As String = "User Skill Ratings"
        Private Shared ReadOnly ProgramName As String = "UserSkillRatings1"
        Private iTeamID As Integer = 0
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

            Master.IconImage = Request.ApplicationPath & "/images/UserSkill.gif"
            Master.HeaderMessage = FormName

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnExit.UniqueID + "'),window.event)")

            iTeamID = JobMaster.SelectTeamFromJobID(SessionManager.SelectedValueJob)
            TrainingMatrixLegend1.JobID = SessionManager.SelectedValueJob
            BindGrid()
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

            Try
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.UserSkillRatingsMode)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueJob)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueJobName)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RatingScale)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.ShowValues)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.ShowAttachments)

                If SessionManager.MasterControlExitProgram.Trim.Length > 0 Then
                    Dim strExitProgram As String = SessionManager.MasterControlExitProgram
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.MasterControlExitProgram)
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strExitProgram), False)

                    Return
                End If

                RemoveCurrentProgramandGoBack()
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - btnExit_Click", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub btnAddUser_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnAddUser.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                SessionManager.MasterControlExitProgram = "UserSkillRatings1"
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserJobMaster1"), False)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - btnAddUser_Click", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
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

            Try
                Dim strUser As String
                Dim strUserName As String
                strUser = CType(sender, LinkButton).CommandArgument
                strUserName = (CType(sender, LinkButton).Text).ToString

                SessionManager.UserSkillRatingsMode = "EditRow"
                SessionManager.SelectedValue = strUser
                SessionManager.SelectedValue1 = strUserName

                'Get the Program URL and redirect
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserSkillRatings2"), False)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - Link_Click", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

#Region " Custom Methods"
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
                If SessionManager.AllowMaintenanceAdd = True Then
                    btnAddUser.Visible = True
                Else
                    btnAddUser.Visible = False
                End If

                If ckRatingScale.Checked Then
                    SessionManager.RatingScale = "True"

                    ckShowValues.Checked = True
                    ckShowValues.Enabled = False
                    BindDiffValues()
                    TrainingMatrixLegend1.ShowTargets = True
                Else
                    SessionManager.RatingScale = "False"

                    ckShowValues.Enabled = True
                    BindRatingsValues()
                End If

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
                Master.DisplayErrors(ProgramName & " - BindGrid", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
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
                Dim objDT As DataTable = UserSkillRatings.SelectUserSkillsByJob(SessionManager.SelectedValueJob)
                Dim objDTSkills As DataTable = SkillRatingMaster.SelectSkillRatingsByJob(SessionManager.SelectedValueJob)
                Dim objDSAttachments As DataTable
                Dim objRow As TableRow
                Dim objCell As TableCell
                Dim iStartCounter As Integer
                Dim iCounter As Integer
                Dim ctlLink As LinkButton
                Dim bShowValues As Boolean = ckShowValues.Checked
                Dim bShowCritera As Boolean = ckCriteria.Checked
                Dim bShowAttachments As Boolean = ckAttachments.Checked

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
                    objCell.BorderColor = Color.Black
                    objCell.Width = New Unit(250)
                    objCell.Text = strJob
                    objRow.Cells.Add(objCell)

                    If bShowCritera Then
                        objCell = New TableCell
                        objCell.BorderStyle = BorderStyle.Solid
                        objCell.BorderWidth = New Unit(1)
                        objCell.BorderColor = Color.Black
                        objCell.HorizontalAlign = HorizontalAlign.Center
                        objCell.Width = New Unit(350)
                        objCell.Font.Bold = True
                        objCell.Text = "Criteria"
                        objRow.Cells.Add(objCell)
                    End If

                    If bShowAttachments Then
                        objCell = New TableCell
                        objCell.BorderStyle = BorderStyle.Solid
                        objCell.BorderWidth = New Unit(1)
                        objCell.BorderColor = Color.Black
                        objCell.HorizontalAlign = HorizontalAlign.Center
                        objCell.Width = New Unit(250)
                        objCell.Font.Bold = True
                        objCell.Text = "Skill Attachments"
                        objRow.Cells.Add(objCell)
                    End If

                    If bShowValues Then
                        objCell = New TableCell
                        objCell.BorderStyle = BorderStyle.Solid
                        objCell.BorderWidth = New Unit(1)
                        objCell.BorderColor = Color.Black
                        objCell.HorizontalAlign = HorizontalAlign.Center
                        objCell.Width = New Unit(55)
                        objCell.Font.Bold = True
                        objCell.Text = "Required"
                        objRow.Cells.Add(objCell)

                        objCell = New TableCell
                        objCell.BorderStyle = BorderStyle.Solid
                        objCell.BorderWidth = New Unit(1)
                        objCell.BorderColor = Color.Black
                        objCell.HorizontalAlign = HorizontalAlign.Center
                        objCell.Font.Bold = True
                        objCell.Width = New Unit(55)
                        objCell.Text = "Desired"
                        objRow.Cells.Add(objCell)
                    End If

                    'add users
                    For iCounter = 7 To objTable.Columns.Count - 1
                        objCell = New TableCell
                        objCell.BorderStyle = BorderStyle.Solid
                        objCell.BorderWidth = New Unit(1)
                        objCell.BorderColor = Color.Black
                        objCell.HorizontalAlign = HorizontalAlign.Center
                        objCell.Width = New Unit(50)

                        If SessionManager.AllowMaintenanceEdit = True Then
                            ctlLink = New LinkButton
                            AddHandler ctlLink.Command, AddressOf Link_Click
                            ctlLink.Text = UserMaster.GetUserFullName(objTable.Columns(iCounter).ColumnName.ToUpper)
                            ctlLink.CommandArgument = objTable.Columns(iCounter).ColumnName.ToUpper
                            ctlLink.ID = objTable.Columns(iCounter).ColumnName.ToUpper

                            objCell.Controls.Add(ctlLink)
                        Else
                            objCell.Text = UserMaster.GetUserFullName(objTable.Columns(iCounter).ColumnName.ToUpper)
                        End If

                        'if the user is a team member then change the cell background color to light blue
                        If TeamMembership.UserIsTeamMember(objTable.Columns(iCounter).ColumnName, iTeamID) Then
                            objCell.BackColor = System.Drawing.Color.LightBlue
                        End If

                        objRow.Cells.Add(objCell)
                    Next
                    tblSkills.Rows.Add(objRow)

                    'now fill the skills and ratings
                    Dim strCat As String = ""
                    For Each objDataRow As DataRow In objTable.Rows
                        If strCat.ToUpper <> objDataRow("SkillCategory").ToString.ToUpper Then
                            'new category
                            objRow = New TableRow
                            objCell = New TableCell
                            objCell.Width = New Unit(250)
                            objCell.Font.Bold = True
                            objCell.HorizontalAlign = HorizontalAlign.Center
                            objCell.Text = objDataRow("SkillCategory").ToString
                            objRow.Cells.Add(objCell)

                            If bShowValues Then
                                iStartCounter = 5
                            Else
                                iStartCounter = 7
                            End If

                            For iCounter = iStartCounter To objTable.Columns.Count - 1
                                objCell = New TableCell
                                objCell.Text = ""
                                objRow.Cells.Add(objCell)
                            Next

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
                        objCell.BorderColor = Color.Black
                        objCell.Text = objDataRow("Skill")
                        objRow.Cells.Add(objCell)
                        strCat = objDataRow("SkillCategory").ToString

                        If bShowValues Then
                            iStartCounter = 5
                        Else
                            iStartCounter = 7
                        End If

                        If bShowCritera Then
                            objCell = New TableCell
                            objCell.Width = New Unit(350)
                            objCell.HorizontalAlign = HorizontalAlign.Left
                            objCell.BorderStyle = BorderStyle.Solid
                            objCell.BorderWidth = New Unit(1)
                            objCell.BorderColor = Color.Black
                            If (objDataRow("AssessmentCriteria") Is DBNull.Value) Then
                                objCell.Text = ""
                            Else
                                objCell.Text = Replace(objDataRow("AssessmentCriteria").ToString, vbCrLf, "<br>")
                            End If
                            objRow.Cells.Add(objCell)
                        End If

                        If bShowAttachments Then
                            objCell = New TableCell
                            objCell.Width = New Unit(250)
                            objCell.HorizontalAlign = HorizontalAlign.Left
                            objCell.BorderStyle = BorderStyle.Solid
                            objCell.BorderWidth = New Unit(1)
                            objCell.BorderColor = Color.Black

                            objDSAttachments = JobSkillAttachments.SelectJobSkillAttachments(SessionManager.SelectedValueJob, objDataRow("Skill"))
                            If objDSAttachments IsNot Nothing AndAlso objDSAttachments.Rows.Count > 0 Then
                                For Each dtRow As DataRow In objDSAttachments.Rows
                                    If dtRow("AttachmentURL").ToString.Trim.Length > 0 Then
                                        ctlLink = New LinkButton
                                        ctlLink.Text = dtRow("Attachment").ToString
                                        ctlLink.Attributes.Add("onclick", "javascript:LaunchExplorer('" & dtRow("AttachmentURL").ToString.Replace("\", "\\") & "');")

                                        objCell.Controls.Add(ctlLink)
                                        objCell.Controls.Add(New LiteralControl("<BR>"))
                                    Else
                                        objCell.Text = dtRow("Attachment").ToString
                                    End If
                                Next dtRow
                            Else
                                objCell.Text = ""
                            End If

                            objRow.Cells.Add(objCell)
                        End If

                        For iCounter = iStartCounter To objTable.Columns.Count - 1
                            objCell = New TableCell
                            objCell.BorderStyle = BorderStyle.Solid
                            objCell.BorderWidth = New Unit(1)
                            objCell.BorderColor = Color.Black
                            objCell.HorizontalAlign = HorizontalAlign.Center
                            objCell.VerticalAlign = VerticalAlign.Top
                            objCell.Height = New Unit(15)
                            objCell.Text = objDataRow.Item(iCounter).ToString

                            'if we have a color use if
                            For Each SkillRow As DataRow In objDTSkills.Rows
                                If SkillRow("SkillRating").ToString = objCell.Text Then
                                    If Not (SkillRow("DisplayColor") Is DBNull.Value) Then
                                        Try
                                            objCell.BackColor = Color.FromName(SkillRow("DisplayColor"))
                                        Catch ex As Exception
                                            'no need to do anything here
                                        End Try
                                    End If

                                    Exit For
                                End If
                            Next

                            objRow.Cells.Add(objCell)
                        Next

                        tblSkills.Rows.Add(objRow)
                    Next
                End If
            Catch Exc As Exception
                Throw
            End Try
        End Sub
        Private Sub BindDiffValues()
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
                Dim objDT As DataTable = UserSkillRatings.SelectUserSkillsByJob(SessionManager.SelectedValueJob)
                Dim objDTSkills As DataTable = JobSkillMaster.SelectJobSkillsByJob(SessionManager.SelectedValueJob)
                Dim objDSAttachments As DataTable
                Dim objRow As TableRow
                Dim objCell As TableCell
                Dim iStartCounter As Integer
                Dim iCounter As Integer
                Dim ctlLink As LinkButton
                Dim bShowValues As Boolean = ckShowValues.Checked
                Dim bShowCritera As Boolean = ckCriteria.Checked
                Dim bShowAttachments As Boolean = ckAttachments.Checked

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
                    objCell.BorderColor = Color.Black
                    objCell.Width = New Unit(250)
                    objCell.Text = strJob
                    objRow.Cells.Add(objCell)

                    If bShowCritera Then
                        objCell = New TableCell
                        objCell.BorderStyle = BorderStyle.Solid
                        objCell.BorderWidth = New Unit(1)
                        objCell.BorderColor = Color.Black
                        objCell.HorizontalAlign = HorizontalAlign.Center
                        objCell.Width = New Unit(350)
                        objCell.Font.Bold = True
                        objCell.Text = "Criteria"
                        objRow.Cells.Add(objCell)
                    End If

                    If bShowAttachments Then
                        objCell = New TableCell
                        objCell.BorderStyle = BorderStyle.Solid
                        objCell.BorderWidth = New Unit(1)
                        objCell.BorderColor = Color.Black
                        objCell.HorizontalAlign = HorizontalAlign.Center
                        objCell.Width = New Unit(250)
                        objCell.Font.Bold = True
                        objCell.Text = "Skill Attachments"
                        objRow.Cells.Add(objCell)
                    End If

                    If bShowValues Then
                        objCell = New TableCell
                        objCell.BorderStyle = BorderStyle.Solid
                        objCell.BorderWidth = New Unit(1)
                        objCell.BorderColor = Color.Black
                        objCell.HorizontalAlign = HorizontalAlign.Center
                        objCell.Width = New Unit(55)
                        objCell.Font.Bold = True
                        objCell.Text = "Required"
                        objRow.Cells.Add(objCell)

                        objCell = New TableCell
                        objCell.BorderStyle = BorderStyle.Solid
                        objCell.BorderWidth = New Unit(1)
                        objCell.BorderColor = Color.Black
                        objCell.HorizontalAlign = HorizontalAlign.Center
                        objCell.Font.Bold = True
                        objCell.Width = New Unit(55)
                        objCell.Text = "Desired"
                        objRow.Cells.Add(objCell)
                    End If

                    'add users
                    For iCounter = 7 To objTable.Columns.Count - 1
                        objCell = New TableCell
                        objCell.BorderStyle = BorderStyle.Solid
                        objCell.BorderWidth = New Unit(1)
                        objCell.BorderColor = Color.Black
                        objCell.HorizontalAlign = HorizontalAlign.Center
                        objCell.Width = New Unit(50)

                        If SessionManager.AllowMaintenanceEdit = True Then
                            ctlLink = New LinkButton
                            AddHandler ctlLink.Command, AddressOf Link_Click
                            ctlLink.Text = UserMaster.GetUserFullName(objTable.Columns(iCounter).ColumnName.ToUpper)
                            ctlLink.ID = objTable.Columns(iCounter).ColumnName.ToUpper

                            objCell.Controls.Add(ctlLink)
                        Else
                            objCell.Text = UserMaster.GetUserFullName(objTable.Columns(iCounter).ColumnName.ToUpper)
                        End If

                        'if the user is a team member then change the cell background color to light blue
                        If TeamMembership.UserIsTeamMember(objTable.Columns(iCounter).ColumnName, iTeamID) Then
                            objCell.BackColor = System.Drawing.Color.LightBlue
                        End If

                        objRow.Cells.Add(objCell)
                    Next
                    tblSkills.Rows.Add(objRow)

                    'now fill the skills and ratings
                    Dim strCat As String = ""
                    For Each objDataRow As DataRow In objTable.Rows
                        If strCat.ToUpper <> objDataRow("SkillCategory").ToString.ToUpper Then
                            'new category
                            objRow = New TableRow
                            objCell = New TableCell
                            objCell.Width = New Unit(250)
                            objCell.Font.Bold = True
                            objCell.HorizontalAlign = HorizontalAlign.Center
                            objCell.Text = objDataRow("SkillCategory").ToString
                            objRow.Cells.Add(objCell)

                            If bShowValues Then
                                iStartCounter = 5
                            Else
                                iStartCounter = 7
                            End If

                            For iCounter = iStartCounter To objTable.Columns.Count - 1
                                objCell = New TableCell
                                objCell.Text = ""
                                objRow.Cells.Add(objCell)
                            Next

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
                        objCell.BorderColor = Color.Black
                        objCell.Text = objDataRow("Skill")
                        objRow.Cells.Add(objCell)
                        strCat = objDataRow("SkillCategory").ToString

                        If bShowCritera Then
                            objCell = New TableCell
                            objCell.Width = New Unit(350)
                            objCell.HorizontalAlign = HorizontalAlign.Left
                            objCell.BorderStyle = BorderStyle.Solid
                            objCell.BorderWidth = New Unit(1)
                            objCell.BorderColor = Color.Black
                            If (objDataRow("AssessmentCriteria") Is DBNull.Value) Then
                                objCell.Text = ""
                            Else
                                objCell.Text = Replace(objDataRow("AssessmentCriteria").ToString, vbCrLf, "<br>")
                            End If
                            objRow.Cells.Add(objCell)
                        End If

                        If bShowAttachments Then
                            objCell = New TableCell
                            objCell.Width = New Unit(250)
                            objCell.HorizontalAlign = HorizontalAlign.Left
                            objCell.BorderStyle = BorderStyle.Solid
                            objCell.BorderWidth = New Unit(1)
                            objCell.BorderColor = Color.Black

                            objDSAttachments = JobSkillAttachments.SelectJobSkillAttachments(SessionManager.SelectedValueJob, objDataRow("Skill"))
                            If objDSAttachments.Rows.Count > 0 Then
                                For Each dtRow As DataRow In objDSAttachments.Rows
                                    If dtRow("AttachmentURL").ToString.Trim.Length > 0 Then
                                        ctlLink = New LinkButton
                                        ctlLink.Text = dtRow("Attachment").ToString
                                        ctlLink.Attributes.Add("onclick", "javascript:LaunchExplorer('" & dtRow("AttachmentURL").ToString.Replace("\", "\\") & "');")

                                        objCell.Controls.Add(ctlLink)
                                        objCell.Controls.Add(New LiteralControl("<BR>"))
                                    Else
                                        objCell.Text = dtRow("Attachment").ToString
                                    End If
                                Next dtRow
                            Else
                                objCell.Text = ""
                            End If

                            objRow.Cells.Add(objCell)
                        End If

                        If bShowValues Then
                            objCell = New TableCell
                            objCell.BorderStyle = BorderStyle.Solid
                            objCell.BorderWidth = New Unit(1)
                            objCell.BorderColor = Color.Black
                            objCell.HorizontalAlign = HorizontalAlign.Center
                            objCell.VerticalAlign = VerticalAlign.Top
                            objCell.Height = New Unit(15)
                            objCell.Text = objDataRow("RequiredRating").ToString
                            objRow.Cells.Add(objCell)

                            objCell = New TableCell
                            objCell.BorderStyle = BorderStyle.Solid
                            objCell.BorderWidth = New Unit(1)
                            objCell.BorderColor = Color.Black
                            objCell.HorizontalAlign = HorizontalAlign.Center
                            objCell.VerticalAlign = VerticalAlign.Top
                            objCell.Height = New Unit(15)
                            objCell.Text = objDataRow("DesiredRating").ToString
                            objRow.Cells.Add(objCell)
                        End If

                        For iCounter = 7 To objTable.Columns.Count - 1
                            objCell = New TableCell
                            objCell.BorderStyle = BorderStyle.Solid
                            objCell.BorderWidth = New Unit(1)
                            objCell.BorderColor = Color.Black
                            objCell.HorizontalAlign = HorizontalAlign.Center
                            objCell.VerticalAlign = VerticalAlign.Top
                            objCell.Height = New Unit(15)
                            objCell.Text = objDataRow.Item(iCounter).ToString

                            'if we have a color use if
                            For Each SkillRow As DataRow In objDTSkills.Rows
                                If SkillRow("SkillCategory").ToString = objDataRow("SkillCategory").ToString Then
                                    If SkillRow("Skill").ToString = objDataRow("Skill").ToString Then
                                        'this is the row
                                        'now test the values
                                        If objDataRow.Item(iCounter) Is DBNull.Value Then
                                            'no rating
                                            objCell.BackColor = Color.LightGray
                                        ElseIf (Not (SkillRow("RequiredRating") Is DBNull.Value)) And (Convert.ToInt16("0" & objDataRow.Item(iCounter).ToString) < Convert.ToInt16("0" & SkillRow("RequiredRating").ToString)) Then
                                            'red
                                            objCell.BackColor = Color.Crimson
                                        ElseIf (Not (SkillRow("DesiredRating") Is DBNull.Value)) And (Convert.ToInt16("0" & objDataRow.Item(iCounter).ToString) >= Convert.ToInt16("0" & SkillRow("DesiredRating").ToString)) Then
                                            'green
                                            objCell.BackColor = Color.Green
                                        ElseIf SkillRow("RequiredRating") Is DBNull.Value Then
                                            'don't do anything!
                                        Else
                                            'yellow
                                            objCell.BackColor = Color.Yellow
                                        End If
                                    End If
                                End If
                            Next

                            objRow.Cells.Add(objCell)
                        Next

                        tblSkills.Rows.Add(objRow)
                    Next
                End If
            Catch Exc As Exception
                Throw
            End Try
        End Sub
#End Region

    End Class
End Namespace