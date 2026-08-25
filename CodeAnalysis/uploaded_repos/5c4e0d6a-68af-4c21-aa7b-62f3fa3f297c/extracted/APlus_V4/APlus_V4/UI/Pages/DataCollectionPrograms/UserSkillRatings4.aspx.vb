#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports System.Drawing
Imports WebApp.APlus.UI
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class UserSkillRatings4
        Inherits PrinterFriendlyBase

#Region " Constants and Member Variables"
        Private Shared ReadOnly FormName As String = "User Skill Ratings"
        Private Shared ReadOnly ProgramName As String = "UserSkillRatings4"
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

            If SessionManager.SelectedValueJob = 0 Then
                Return
            End If
            TrainingMatrixLegend1.JobID = SessionManager.SelectedValueJob
            iTeamID = JobMaster.SelectTeamFromJobID(SessionManager.SelectedValueJob)
            lblJob.Text = "Training Matrix - " & SessionManager.SelectedValueJobName.ToString
            lblPrintDate.Text = "Printed : " + Now.ToLongDateString
            BindGrid()
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
                If SessionManager.RatingScale = "True" Then
                    SessionManager.ShowValues = "True"
                    BindDiffValues()
                    TrainingMatrixLegend1.ShowTargets = True
                Else
                    BindRatingsValues()
                End If
            Catch Exc As Exception
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
                Dim strJob As String = SessionManager.SelectedJobName
                Dim objDT As DataTable = UserSkillRatings.SelectUserSkillsByJob(SessionManager.SelectedValueJob)
                Dim objDTSkills As DataTable = SkillRatingMaster.SelectSkillRatingsByJob(SessionManager.SelectedValueJob)
                Dim objDSAttachments As DataSet
                Dim objRow As TableRow
                Dim objCell As TableCell
                Dim iStartCounter As Integer
                Dim iCounter As Integer
                Dim bShowValues As Boolean = (SessionManager.ShowValues = "True")
                Dim bShowCritera As Boolean = (SessionManager.ShowCriteria = "True")
                Dim bShowAttachments As Boolean = (SessionManager.ShowAttachments = "True")

                If objDT IsNot Nothing AndAlso objDT.Rows.Count > 0 Then
                    Dim iColumns As Integer = objDT.Columns.Count

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
                    For iCounter = 7 To objDT.Columns.Count - 1
                        objCell = New TableCell
                        objCell.BorderStyle = BorderStyle.Solid
                        objCell.BorderWidth = New Unit(1)
                        objCell.BorderColor = Color.Black
                        objCell.HorizontalAlign = HorizontalAlign.Center
                        objCell.Width = New Unit(50)
                        objCell.Text = UserMaster.GetUserFullName(objDT.Columns(iCounter).ColumnName.ToUpper)

                        'if the user is a team member then change the cell background color to light blue
                        If TeamMembership.UserIsTeamMember(objDT.Columns(iCounter).ColumnName, iTeamID) Then
                            objCell.BackColor = System.Drawing.Color.LightBlue
                        End If

                        objRow.Cells.Add(objCell)
                    Next
                    tblSkills.Rows.Add(objRow)

                    'now fill the skills and ratings
                    Dim strCat As String = ""
                    For Each objDataRow As DataRow In objDT.Rows
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

                            For iCounter = iStartCounter To objDT.Columns.Count - 1
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
                            objCell.VerticalAlign = VerticalAlign.Top
                            objCell.BorderStyle = BorderStyle.Solid
                            objCell.BorderWidth = New Unit(1)
                            objCell.BorderColor = Color.Black

                            objDSAttachments = JobSkillAttachments.SelectJobSkillAttachments(SessionManager.SelectedValueJob, objDataRow("Skill"))
                            If objDSAttachments.Tables(0).Rows.Count > 0 Then
                                For Each dtRow As DataRow In objDSAttachments.Tables(0).Rows
                                    objCell.Text += dtRow("Attachment").ToString & "<BR>"
                                Next dtRow
                            Else
                                objCell.Text = ""
                            End If

                            objRow.Cells.Add(objCell)
                        End If

                        For iCounter = iStartCounter To objDT.Columns.Count - 1
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
            Catch Sxc As SqlException
                Throw
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
                Dim strJob As String = SessionManager.SelectedJobName
                Dim objDT As DataTable = UserSkillRatings.SelectUserSkillsByJob(SessionManager.SelectedValueJob)
                Dim objDTSkills As DataTable = JobSkillMaster.SelectJobSkillsByJob(SessionManager.SelectedValueJob)
                Dim objDSAttachments As DataSet
                Dim objRow As TableRow
                Dim objCell As TableCell
                Dim iStartCounter As Integer
                Dim iCounter As Integer
                Dim bShowValues As Boolean = (SessionManager.ShowValues = "True")
                Dim bShowCritera As Boolean = (SessionManager.ShowCriteria = "True")
                Dim bShowAttachments As Boolean = (SessionManager.ShowAttachments = "True")

                If objDT IsNot Nothing AndAlso objDT.Rows.Count > 0 Then
                    Dim iColumns As Integer = objDT.Columns.Count

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
                    For iCounter = 7 To objDT.Columns.Count - 1
                        objCell = New TableCell
                        objCell.BorderStyle = BorderStyle.Solid
                        objCell.BorderWidth = New Unit(1)
                        objCell.BorderColor = Color.Black
                        objCell.HorizontalAlign = HorizontalAlign.Center
                        objCell.Width = New Unit(50)
                        objCell.Text = UserMaster.GetUserFullName(objDT.Columns(iCounter).ColumnName.ToUpper)

                        'if the user is a team member then change the cell background color to light blue
                        If TeamMembership.UserIsTeamMember(objDT.Columns(iCounter).ColumnName, iTeamID) Then
                            objCell.BackColor = System.Drawing.Color.LightBlue
                        End If

                        objRow.Cells.Add(objCell)
                    Next
                    tblSkills.Rows.Add(objRow)

                    'now fill the skills and ratings
                    Dim strCat As String = ""
                    For Each objDataRow As DataRow In objDT.Rows
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

                            For iCounter = iStartCounter To objDT.Columns.Count - 1
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
                            If objDSAttachments.Tables(0).Rows.Count > 0 Then
                                For Each dtRow As DataRow In objDSAttachments.Tables(0).Rows
                                    objCell.Text += dtRow("Attachment").ToString & "<BR>"
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

                        For iCounter = 7 To objDT.Columns.Count - 1
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
            Catch Sxc As SqlException
                Throw
            Catch Exc As Exception
                Throw
            End Try
        End Sub
#End Region

    End Class
End Namespace