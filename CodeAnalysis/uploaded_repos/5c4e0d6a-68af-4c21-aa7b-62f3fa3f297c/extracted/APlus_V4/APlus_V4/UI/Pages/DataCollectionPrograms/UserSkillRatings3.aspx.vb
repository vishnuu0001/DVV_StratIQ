#Region " Imports"
Imports System.IO
Imports WebApp.APlus.UI
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports System.Data
Imports System.Data.SqlClient
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class UserSkillRatings3
        Inherits PrinterFriendlyBase

#Region " Constants and Member Variables"
        Private Shared ReadOnly FormName As String = "User Skill Ratings"
        Private Shared ReadOnly ProgramName As String = "UserSkillRatings3"
        Private _JobID As Integer = 0
        Private _JobName As String = ""
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

            'if we have no session variables, exit out
            _JobID = SessionManager.SelectedValueJob
            _JobName = SessionManager.SelectedValueJobName
            TrainingMatrixLegend1.JobID = _JobID
            lblJob.Text = "Job Skills Training Assessment"
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
                Dim objDS As DataTable = JobSkillMaster.SelectJobSkillsByJob(_JobID)
                Dim objRow As TableRow
                Dim objCell As TableCell
                Dim txtCounter As Integer = 0

                If Not IsNothing(objDS) And objDS.Rows.Count > 0 Then
                    'get the skills table
                    Dim objTable As DataTable = objDS

                    'go through the table and create grid
                    'create header row first
                    objRow = New TableRow

                    objCell = New TableCell
                    objCell.HorizontalAlign = HorizontalAlign.Center
                    objCell.Font.Bold = True
                    objCell.BorderStyle = BorderStyle.Solid
                    objCell.BorderWidth = New Unit(1)
                    objCell.BorderColor = Drawing.Color.Black
                    objCell.Width = New Unit(350)
                    objCell.Text = _JobName
                    objRow.Cells.Add(objCell)

                    objCell = New TableCell
                    objCell.BorderStyle = BorderStyle.Solid
                    objCell.BorderWidth = New Unit(1)
                    objCell.BorderColor = Drawing.Color.Black
                    objCell.HorizontalAlign = HorizontalAlign.Center
                    objCell.Width = New Unit(350)
                    objCell.Font.Bold = True
                    objCell.Text = "Criteria"
                    objRow.Cells.Add(objCell)

                    'New Value
                    objCell = New TableCell
                    objCell.BorderStyle = BorderStyle.Solid
                    objCell.BorderWidth = New Unit(1)
                    objCell.BorderColor = Drawing.Color.Black
                    objCell.HorizontalAlign = HorizontalAlign.Center
                    objCell.Width = New Unit(75)
                    objCell.Text = "Assessment"
                    objRow.Cells.Add(objCell)

                    tblSkills.Rows.Add(objRow)

                    'now fill the skills and ratings
                    Dim strCat As String = ""
                    For Each objDataRow As DataRow In objTable.Rows
                        If strCat.ToUpper <> objDataRow("SkillCategory").ToString.ToUpper Then
                            'new category
                            objRow = New TableRow
                            objCell = New TableCell
                            objCell.Font.Bold = True
                            objCell.HorizontalAlign = HorizontalAlign.Center
                            objCell.Text = objDataRow("SkillCategory").ToString
                            objRow.Cells.Add(objCell)

                            objCell = New TableCell
                            objCell.Text = ""
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
                        objCell.Text = objDataRow("Skill")
                        objRow.Cells.Add(objCell)
                        strCat = objDataRow("SkillCategory").ToString

                        objCell = New TableCell
                        objCell.Width = New Unit(350)
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

                        'new value
                        objCell = New TableCell
                        objCell.BorderStyle = BorderStyle.Solid
                        objCell.BorderWidth = New Unit(1)
                        objCell.BorderColor = Drawing.Color.Black
                        objCell.HorizontalAlign = HorizontalAlign.Center
                        objCell.Height = New Unit(15)
                        objRow.Cells.Add(objCell)
                        tblSkills.Rows.Add(objRow)
                    Next
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindGrid", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

    End Class
End Namespace
