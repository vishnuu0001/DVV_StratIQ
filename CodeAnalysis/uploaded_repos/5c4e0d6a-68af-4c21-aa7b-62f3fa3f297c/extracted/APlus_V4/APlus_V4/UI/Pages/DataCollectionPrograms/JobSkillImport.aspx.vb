#Region "Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports System.Text
Imports WebApp.APlus.Helper
Imports WebApp.APlus.DataAccess
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports Microsoft.Office.Interop
Imports System.Web.Security
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class JobSkillImport
        Inherits ApplicationBase

#Region " Private Variables/Constants "
        Private cells As Owc11.Range
        Protected mStrExcelData As String
        Protected mObjDT As DataTable
        Private Shared ReadOnly FormName As String = "Job Skill Import"
        Private Shared ReadOnly ProgramName As String = "JobSkillImport"
        Private Shared ReadOnly TOTAL_COLS As Integer = 7
        Private Shared ReadOnly ERROR_COL As Integer = 8
#End Region

#Region " Enumerations "
        Enum EXCEL_COLUMNS
            JOB = 1
            SKILL_CATEGORY = 2
            SKILL = 3
            ASSESSMENT_CRITERIA = 4
            SEQUENCE = 5
            REQUIRED_RATING = 6
            DESIRED_RATING = 7
        End Enum
#End Region

#Region " Event Handlers "
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

            SessionManager.CurrentProgram = Request.Path
            Master.HeaderMessage = FormName
            Master.IconImage = Request.ApplicationPath + "/images/UserSkillAttachment.gif"

            SetUpGridColumns()
            If Not btnValidate Is Nothing Then
                btnValidate.Attributes.Add("onclick", "ImportFromExcel()")
            End If
        End Sub

        Private Sub btnCancel_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnCancel.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            RemoveCurrentProgramandGoBack()
        End Sub

        Private Sub btnValidate_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnValidate.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, ProgramName, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If ValidateExcelRows() Then
            Else
                HTMLData.Text = mStrExcelData
            End If
        End Sub

#End Region

#Region " Custom Methods "
        Private Function ValidateExcelRows() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim blnResult As Boolean = True
            Dim blnRowError As Boolean = False
            Dim objExcel As New Owc11.Spreadsheet
            Dim iColIdx As Integer = 1
            Dim iRowIdx As Integer = 1
            Dim strErrorMsg As String = String.Empty

            Try
                If Me.HTMLData.Text.Length > 0 Then
                    objExcel.HTMLData = Me.HTMLData.Text
                    objExcel.Cells(1, 1).Select()
                    cells = objExcel.ActivePane.VisibleRange.Cells
                    Do
                        If cells(iRowIdx, iColIdx).Text.ToString().Trim().Length() < 1 _
                        And iColIdx <> JobSkillImport.EXCEL_COLUMNS.ASSESSMENT_CRITERIA Then
                            strErrorMsg &= " " & Me.GetCurrentColumn(iColIdx) & " cannot be empty! "
                            cells(iRowIdx).EntireRow.Interior.Color = "Red"
                            cells(iRowIdx, ERROR_COL).Value &= strErrorMsg
                            blnResult = False
                            blnRowError = True
                        ElseIf iColIdx = JobSkillImport.EXCEL_COLUMNS.SEQUENCE Then
                            If Not IsNumeric(cells(iRowIdx, JobSkillImport.EXCEL_COLUMNS.SEQUENCE).Text) Then
                                strErrorMsg &= " " & Me.GetCurrentColumn(JobSkillImport.EXCEL_COLUMNS.SEQUENCE) & " must be numeric! "
                                cells(iRowIdx).EntireRow.Interior.Color = "Red"
                                cells(iRowIdx, ERROR_COL).Value &= strErrorMsg
                                blnResult = False
                                blnRowError = True
                            End If
                        ElseIf iColIdx = JobSkillImport.EXCEL_COLUMNS.REQUIRED_RATING Then
                            If Not IsNumeric(cells(iRowIdx, JobSkillImport.EXCEL_COLUMNS.REQUIRED_RATING)) Then
                                strErrorMsg &= " " & Me.GetCurrentColumn(JobSkillImport.EXCEL_COLUMNS.REQUIRED_RATING) & " must be numeric! "
                                cells(iRowIdx).EntireRow.Interior.Color = "Red"
                                cells(iRowIdx, ERROR_COL).Value &= strErrorMsg
                                blnResult = False
                                blnRowError = True
                            End If

                        ElseIf iColIdx = JobSkillImport.EXCEL_COLUMNS.DESIRED_RATING Then
                            If Not IsNumeric(cells(iRowIdx, JobSkillImport.EXCEL_COLUMNS.DESIRED_RATING).Text) Then
                                strErrorMsg &= " " & Me.GetCurrentColumn(JobSkillImport.EXCEL_COLUMNS.DESIRED_RATING) & " must be numeric! "
                                cells(iRowIdx).EntireRow.Interior.Color = "Red"
                                cells(iRowIdx, ERROR_COL).Value &= strErrorMsg
                                blnResult = False
                                blnRowError = True
                            End If
                        End If
                        iColIdx += 1
                        If iColIdx > JobSkillImport.TOTAL_COLS Then
                            If cells(iRowIdx, ERROR_COL).Text.ToString.Trim.Length() > 1 Then
                                If Not blnRowError Then
                                    cells(iRowIdx, ERROR_COL).Value = ""
                                    cells(iRowIdx, iColIdx).EntireRow.Interior.Color = ""
                                End If
                            End If

                            If blnRowError Then
                                cells(iRowIdx, iColIdx).EntireRow.Interior.Color = "Red"
                                cells(iRowIdx, ERROR_COL).Value = strErrorMsg
                            End If
                            iRowIdx += 1
                            iColIdx = 1
                            blnRowError = False
                            strErrorMsg = String.Empty
                        End If

                    Loop Until cells(iRowIdx, 1).Text = "" And cells(iRowIdx, 2).Text = "" And cells(iRowIdx, 3).Text = "" _
                    And cells(iRowIdx, 4).Text = "" And cells(iRowIdx, 5).Text = "" _
                    And cells(iRowIdx, 6).Text = "" And cells(iRowIdx, 7).Text = ""

                    mStrExcelData = objExcel.HTMLData
                    If blnResult Then
                        LoadExcelDataToDataTable(objExcel)
                    Else
                        Master.DisplayError("Invalid Activity value(s)!")
                    End If
                End If

            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - ValidateExcelRows", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
            Return blnResult
        End Function

        Public Sub LoadExcelDataToDataTable(ByRef objExcel As Owc11.Spreadsheet)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim iColIdx As Integer = 1
            Dim iRowIdx As Integer = 1
            Dim dr As DataRow
            objExcel.Cells(1, 1).Select()
            cells = objExcel.ActivePane.VisibleRange.Cells

            Try
                mObjDT = New DataTable
                SetupDataTable(mObjDT, gvImport)
                dr = mObjDT.NewRow
                dr.Item(0) = SessionManager.SelectedWorkCenter
                Do
                    dr.Item(iColIdx) = cells(iRowIdx, iColIdx).Text
                    iColIdx += 1
                    If iColIdx = JobSkillImport.TOTAL_COLS Then
                        dr.Item(iColIdx) = cells(iRowIdx, iColIdx).Text
                        iColIdx = 1
                        iRowIdx += 1
                        mObjDT.Rows.Add(dr)
                        dr = mObjDT.NewRow
                        dr.Item(0) = SessionManager.SelectedWorkCenter
                    End If

                Loop Until cells(iRowIdx, 1).Text = "" And cells(iRowIdx, 2).Text = "" And cells(iRowIdx, 3).Text = "" _
                            And cells(iRowIdx, 3).Text = "" And cells(iRowIdx, 4).Text = "" And cells(iRowIdx, 5).Text = "" _
                            And cells(iRowIdx, 6).Text = "" And cells(iRowIdx, 7).Text = ""
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadExcelDataToDataTable", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub

        Public Sub SetExcelColumns()
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
                Dim objExcel As New Owc11.Spreadsheet
                objExcel.ActiveSheet.Cells(1, 1).Value = " Job "
                objExcel.ActiveSheet.Cells(1, 2).Value = " Skill Category "
                objExcel.ActiveSheet.Cells(1, 3).Value = "  Skill "
                objExcel.ActiveSheet.Cells(1, 4).Value = "  Assessment Criteria "
                objExcel.ActiveSheet.Cells(1, 5).Value = " Sequence "
                objExcel.ActiveSheet.Cells(1, 6).Value = " Required Rating "
                objExcel.ActiveSheet.Cells(1, 7).Value = " Desired Rating "
                objExcel.ActiveSheet.Rows().Locked = True
                HTMLData.Text = objExcel.HTMLData
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - SetExcelColumns", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub

        Private Sub SetupDataTable(ByRef dt As DataTable, ByRef gv As GridView)
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
                For i As Integer = 0 To gvImport.Columns.Count - 1
                    If TypeOf gvImport.Columns(i) Is BoundField Then dt.Columns.Add(New DataColumn(CType(gvImport.Columns(i), BoundField).DataField))
                Next
                dt.Columns.Add(New DataColumn("Errors"))
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - SetupDataTable", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub

        Public Function GetCurrentColumn(ByVal intCol As Integer) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, intCol)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim strCol As String = String.Empty
                Select Case intCol
                    Case JobSkillImport.EXCEL_COLUMNS.ASSESSMENT_CRITERIA
                        strCol = "ASSESSMENT CRITERIA"
                    Case JobSkillImport.EXCEL_COLUMNS.JOB
                        strCol = "JOB"
                    Case JobSkillImport.EXCEL_COLUMNS.SKILL
                        strCol = "SKILL"
                    Case JobSkillImport.EXCEL_COLUMNS.SKILL_CATEGORY
                        strCol = "SKILL CATEGORY"
                    Case JobSkillImport.EXCEL_COLUMNS.SEQUENCE
                        strCol = "SEQUENCE"
                    Case JobSkillImport.EXCEL_COLUMNS.DESIRED_RATING
                        strCol = "DESIRED RATING"
                    Case JobSkillImport.EXCEL_COLUMNS.REQUIRED_RATING
                        strCol = "REQUIRED RATING"
                    Case Else
                        strCol = "UNKOWN COLUMN VALUE"
                End Select
                Return strCol
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - GetCurrentColumn", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                Return ""
            End Try
        End Function

        Public Sub SetUpGridColumns()
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
                Dim objCol As BoundField

                objCol = New BoundField
                objCol.HeaderText = "Job"
                objCol.DataField = "Job"
                gvImport.Columns.Add(objCol)

                objCol = New BoundField
                objCol.HeaderText = "Skill Category"
                objCol.DataField = "SkillCategory"
                gvImport.Columns.Add(objCol)

                objCol = New BoundField
                objCol.HeaderText = "Skill"
                objCol.DataField = "Skill"
                gvImport.Columns.Add(objCol)

                objCol = New BoundField
                objCol.HeaderText = "Assessment Criteria"
                objCol.DataField = "AssessmentCriteria"
                gvImport.Columns.Add(objCol)

                objCol = New BoundField
                objCol.HeaderText = "Sequence"
                objCol.DataField = "Sequence"
                gvImport.Columns.Add(objCol)

                objCol = New BoundField
                objCol.HeaderText = "Required Rating"
                objCol.DataField = "RequiredRating"
                gvImport.Columns.Add(objCol)

                objCol = New BoundField
                objCol.HeaderText = "Desired Rating"
                objCol.DataField = "DesiredRating"
                gvImport.Columns.Add(objCol)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - SetUpGridColumns", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub

        Private Sub SetErrorMessageToRow(ByVal intRow As Integer, ByVal strMsg As String)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, intRow, strMsg)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                cells(intRow).EntireRow.Interior.Color = "Red"
                cells(intRow, ERROR_COL).Value &= strMsg
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - SetErrorMessageToRow", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub

#End Region

    End Class
End Namespace
