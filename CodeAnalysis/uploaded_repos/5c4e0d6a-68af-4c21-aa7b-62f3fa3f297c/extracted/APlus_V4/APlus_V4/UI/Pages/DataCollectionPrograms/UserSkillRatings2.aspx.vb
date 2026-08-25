#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Drawing
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports System.Collections.Generic

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class UserSkillRatings2
        Inherits ApplicationBase

#Region " Constants and Member Variables"
        Private Shared ReadOnly FormName As String = "User Skill Ratings"
        Private Shared ReadOnly ProgramName As String = "UserSkillRatings2"
        Private Shared ReadOnly DBTableName As String = "UserSkillRatings"
        Private colControls As Collection = New Collection
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel"}
            Dim OutMessageArr() As String = {"", ""}

            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)

            Dim strDateFormat As String = SessionManager.DateFormat
            txtEvaluationDate_CalendarExtender.Format = strDateFormat

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event)")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
        End Sub
        Private Sub LoadEditModeJavaScripts()
            Dim objTextBox As TextBox
            Dim iCounter As Integer
            Dim strNext As String
            Dim strPrevious As String

            If colControls.Count > 1 Then
                For iCounter = 1 To colControls.Count
                    objTextBox = colControls.Item(iCounter)

                    If iCounter = 1 Then
                        strNext = "ctl00_ContentPlaceHolder1_" + CType(colControls.Item(iCounter + 1), TextBox).ID
                        strPrevious = "ctl00_ContentPlaceHolder1_" + CType(colControls.Item(colControls.Count), TextBox).ID
                    ElseIf iCounter = colControls.Count Then
                        strNext = "ctl00_ContentPlaceHolder1_" + CType(colControls.Item(1), TextBox).ID
                        strPrevious = "ctl00_ContentPlaceHolder1_" + CType(colControls.Item(iCounter - 1), TextBox).ID
                    Else
                        strNext = "ctl00_ContentPlaceHolder1_" + CType(colControls.Item(iCounter + 1), TextBox).ID
                        strPrevious = "ctl00_ContentPlaceHolder1_" + CType(colControls.Item(iCounter - 1), TextBox).ID
                    End If

                    objTextBox.Attributes.Add("onkeydown", "Tab(" + strNext + ", " + strPrevious + ", window.event, 'No');")
                Next

                CType(colControls(1), Control).Focus()
            End If
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

            Master.HeaderMessage = FormName & " - " & SessionManager.UserSkillRatingsMode.Replace("Row", "")
            Master.IconImage = Request.ApplicationPath + "/images/UserSkill.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()
            TrainingMatrixLegend1.JobID = SessionManager.SelectedValueJob

            If Not Page.IsPostBack Then
                txtEvaluationDate.Text = Date.Today.Date.ToString(SessionManager.DateFormat)
            End If

            If SessionManager.UserSkillRatingsMode = "EditRow" Then
                BindGrid()

                LoadEditModeJavaScripts()
            Else
                RemoveCurrentProgramandGoBack()
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

            If SessionManager.UserSkillRatingsMode = "EditRow" Then
                blnSuccess = UpdateSkills()
            End If

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.UserSkillRatingsMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserSkillRatings1"), False)
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.UserSkillRatingsMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserSkillRatings1"), False)
        End Sub
#End Region

#Region " BindGrid"
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
                lblUser.Text = SessionManager.SelectedValue1.ToString

                Dim strJob As String = SessionManager.SelectedValueJobName
                Dim strUser As String = SessionManager.SelectedValue
                Dim objDT As DataTable = UserSkillRatings.SelectUserSkills(SessionManager.SelectedValueJob, strUser)
                Dim objDTSkills As DataTable = SkillRatingMaster.SelectSkillRatingsByJob(SessionManager.SelectedValueJob)
                Dim objRow As TableRow
                Dim objCell As TableCell
                Dim ctlTextBox As TextBox
                Dim bShowValues As Boolean = ckShowValues.Checked
                Dim bShowCritera As Boolean = ckCriteria.Checked

                If objDT IsNot Nothing AndAlso objDT.Rows.Count > 0 Then
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

                    'add date
                    objCell = New TableCell
                    objCell.BorderStyle = BorderStyle.Solid
                    objCell.BorderWidth = New Unit(1)
                    objCell.BorderColor = Color.Black
                    objCell.HorizontalAlign = HorizontalAlign.Center
                    objCell.Width = New Unit(90)
                    objCell.Text = "Evaluation Date"
                    objRow.Cells.Add(objCell)

                    'add Evaluation User
                    objCell = New TableCell
                    objCell.BorderStyle = BorderStyle.Solid
                    objCell.BorderWidth = New Unit(1)
                    objCell.BorderColor = Color.Black
                    objCell.HorizontalAlign = HorizontalAlign.Center
                    objCell.Width = New Unit(90)
                    objCell.Text = "Evaluation User"
                    objRow.Cells.Add(objCell)

                    'add user
                    objCell = New TableCell
                    objCell.BorderStyle = BorderStyle.Solid
                    objCell.BorderWidth = New Unit(1)
                    objCell.BorderColor = Color.Black
                    objCell.HorizontalAlign = HorizontalAlign.Center
                    objCell.Width = New Unit(50)
                    objRow.Cells.Add(objCell)

                    'New Value
                    objCell = New TableCell
                    objCell.BorderStyle = BorderStyle.Solid
                    objCell.BorderWidth = New Unit(1)
                    objCell.BorderColor = Color.Black
                    objCell.HorizontalAlign = HorizontalAlign.Center
                    objCell.Width = New Unit(75)
                    objCell.Text = "New Value"
                    objRow.Cells.Add(objCell)

                    tblSkills.Rows.Add(objRow)

                    'now fill the skills and ratings
                    Dim strCat As String = ""
                    For Each objDataRow As DataRow In objDT.Rows
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

                            If bShowValues Then
                                objCell.ColumnSpan = 6
                            Else
                                objCell.ColumnSpan = 4
                            End If

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

                        If bShowValues Then
                            'required
                            objCell = New TableCell
                            objCell.BorderStyle = BorderStyle.Solid
                            objCell.BorderWidth = New Unit(1)
                            objCell.BorderColor = Color.Black
                            objCell.HorizontalAlign = HorizontalAlign.Center
                            objCell.VerticalAlign = VerticalAlign.Top
                            objCell.Height = New Unit(15)
                            objCell.Text = objDataRow.Item("RequiredRating").ToString
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

                            'desired
                            objCell = New TableCell
                            objCell.BorderStyle = BorderStyle.Solid
                            objCell.BorderWidth = New Unit(1)
                            objCell.BorderColor = Color.Black
                            objCell.HorizontalAlign = HorizontalAlign.Center
                            objCell.VerticalAlign = VerticalAlign.Top
                            objCell.Height = New Unit(15)
                            objCell.Text = objDataRow.Item("DesiredRating").ToString
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
                        End If

                        'evaluation date
                        objCell = New TableCell
                        objCell.BorderStyle = BorderStyle.Solid
                        objCell.BorderWidth = New Unit(1)
                        objCell.BorderColor = Color.Black
                        objCell.HorizontalAlign = HorizontalAlign.Center
                        objCell.VerticalAlign = VerticalAlign.Top
                        objCell.Height = New Unit(15)
                        If IsDate(objDataRow("EvaluationDate").ToString) Then
                            objCell.Text = Convert.ToDateTime(objDataRow("EvaluationDate")).ToString(SessionManager.DateFormat)
                        Else
                            objCell.Text = ""
                        End If
                        objRow.Cells.Add(objCell)

                        'evaluation User
                        objCell = New TableCell
                        objCell.BorderStyle = BorderStyle.Solid
                        objCell.BorderWidth = New Unit(1)
                        objCell.BorderColor = Color.Black
                        objCell.HorizontalAlign = HorizontalAlign.Center
                        objCell.VerticalAlign = VerticalAlign.Top
                        objCell.Height = New Unit(15)
                        objCell.Text = objDataRow.Item("EvaluationUser").ToString
                        objRow.Cells.Add(objCell)

                        'user
                        objCell = New TableCell
                        objCell.BorderStyle = BorderStyle.Solid
                        objCell.BorderWidth = New Unit(1)
                        objCell.BorderColor = Color.Black
                        objCell.HorizontalAlign = HorizontalAlign.Center
                        objCell.VerticalAlign = VerticalAlign.Top
                        objCell.Height = New Unit(15)
                        objCell.Text = objDataRow.Item(9).ToString

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

                        'new value
                        objCell = New TableCell
                        objCell.BorderStyle = BorderStyle.Solid
                        objCell.BorderWidth = New Unit(1)
                        objCell.BorderColor = Color.Black
                        objCell.HorizontalAlign = HorizontalAlign.Center
                        objCell.VerticalAlign = VerticalAlign.Middle
                        objCell.Height = New Unit(15)
                        ctlTextBox = New TextBox
                        ctlTextBox.Text = ""
                        ctlTextBox.CssClass = "Textbox_Entry_UserSkillRatings"
                        ctlTextBox.MaxLength = 1
                        ctlTextBox.ID = "TextBox" & objDataRow("JobSkillID").ToString
                        ctlTextBox.ToolTip = objDataRow("Skill")
                        colControls.Add(ctlTextBox, ctlTextBox.ID)
                        objCell.Controls.Add(ctlTextBox)
                        objRow.Cells.Add(objCell)

                        tblSkills.Rows.Add(objRow)
                    Next
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindGrid", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

#Region " UpdateSkills"
        Private Function UpdateSkills() As Boolean
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
                Dim objText As TextBox
                If Not IsDate(txtEvaluationDate.Text) Then
                    Master.DisplayError("Invalid Evaluation Date.")
                    txtEvaluationDate.Focus()
                    Return False
                End If

                Dim strDateHolder As String = RegionalConversion.FormatSQLDate(txtEvaluationDate.Text)
                Dim bUpdate As Boolean = False
                Dim bNewValue As String = ""
                Dim iLower As Integer
                Dim iUpper As Integer
                Dim iColCount As Integer
                Dim bShowValues As Boolean = ckShowValues.Checked
                Dim bShowCritera As Boolean = ckCriteria.Checked

                If bShowValues Then
                    iColCount = 7
                Else
                    iColCount = 5
                End If

                If bShowCritera Then
                    iColCount += 1
                End If

                'get the limits
                SkillRatingMaster.GetSkillRatingLimits(SessionManager.SelectedValueJob, iLower, iUpper)

                For Each objRow As TableRow In tblSkills.Rows
                    If objRow.Cells.Count = iColCount Then
                        If objRow.Cells(iColCount - 1).Controls.Count > 0 Then
                            objText = objRow.Cells(iColCount - 1).Controls(0)
                            If objText.Text.Trim.Length > 0 Then
                                If objRow.Cells(iColCount - 2).Text <> objText.Text Then
                                    bUpdate = True
                                ElseIf (objRow.Cells(iColCount - 2).Text = objText.Text) And objRow.Cells(1).Text <> strDateHolder Then
                                    bUpdate = True
                                End If

                                If bUpdate = True Then
                                    If objText.Text.ToUpper = "X" Then
                                        Dim objDic As New Dictionary(Of String, String)
                                        objDic.Add("JobID", Replace(objText.ID, "TextBox", ""))
                                        objDic.Add("UserID", SessionManager.SelectedValue)
                                        objDic.Add("EvaluationDate", strDateHolder)
                                        objDic.Add("SkillRating", "")
                                        objDic.Add("MaintenanceUserID", SessionManager.UserID)
                                        objDic.Add("MaintenanceDate", Now.ToString.Trim())
                                        Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)
                                        If strChangeLog.Trim.Length = 0 Then
                                            Return True
                                        End If
                                        UserSkillRatings.UpdateUserSkill(SessionManager.SelectedValue, Replace(objText.ID, "TextBox", ""), "", strDateHolder, SessionManager.UserID)
                                        RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, Replace(objText.ID, "TextBox", "") & "," & SessionManager.SelectedValue, strChangeLog, SessionManager.UserID)
                                        objDic = Nothing
                                    ElseIf (Convert.ToInt16(objText.Text) >= iLower) And (Convert.ToInt16(objText.Text) <= iUpper) Then
                                        Dim objDic As New Dictionary(Of String, String)
                                        objDic.Add("JobID", Replace(objText.ID, "TextBox", ""))
                                        objDic.Add("UserID", SessionManager.SelectedValue)
                                        objDic.Add("EvaluationDate", strDateHolder)
                                        objDic.Add("SkillRating", objText.Text)
                                        objDic.Add("MaintenanceUserID", SessionManager.UserID)
                                        objDic.Add("MaintenanceDate", Now.ToString.Trim())
                                        Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)
                                        If strChangeLog.Trim.Length = 0 Then
                                            Return True
                                        End If
                                        UserSkillRatings.UpdateUserSkill(SessionManager.SelectedValue, Replace(objText.ID, "TextBox", ""), objText.Text, strDateHolder, SessionManager.UserID)
                                        RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, Replace(objText.ID, "TextBox", "") & "," & SessionManager.SelectedValue, strChangeLog, SessionManager.UserID)
                                    Else
                                        Master.DisplayError("New Rating must be 'X' or between " & iLower.ToString & " and " & iUpper)
                                        Return False
                                    End If
                                End If
                            End If
                        End If
                    End If
                Next
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateSkills", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
#End Region

    End Class
End Namespace