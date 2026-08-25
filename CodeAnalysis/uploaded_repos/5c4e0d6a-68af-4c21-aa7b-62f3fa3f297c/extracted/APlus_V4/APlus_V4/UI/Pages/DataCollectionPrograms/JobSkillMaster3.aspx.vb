#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports Microsoft.Office.Interop
Imports System.Web.Security
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class JobSkillMaster3
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Job Skill Master"
        Private Shared ReadOnly ProgramName As String = "JobSkillMaster2"
#End Region

#Region " Private Variables"
        Private blnDataGridValuesValid As Boolean
        Private cells As Owc11.Range  'Cells collection
        Private blnError As Boolean = False
#End Region

#Region " LoadJavaScripts"
        Private Sub LoadJavaScripts()
            btnImport.Attributes.Add("onclick", "javascript:return ImportFromExcel();")
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

            Master.HeaderMessage = FormName & " - " & SessionManager.JobSkillMode.Replace("Row", "") & "Import Job Skill"
            Master.IconImage = Request.ApplicationPath + "/images/UserSkill.gif"

            LoadJavaScripts()

            If Not Page.IsPostBack Then
                InitializeDataGrid()
                InitializeExcelFromDataGrid(grdImport)
            End If
        End Sub

        Protected Sub grdImport_RowDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewRowEventArgs) Handles grdImport.RowDataBound
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If e.Row.RowType = DataControlRowType.DataRow Then
                e.Row.Cells(0).Text = (e.Row.RowIndex + 1).ToString
            End If
        End Sub

        Private Sub btnImport_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnImport.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Import()
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

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("JobSkillMaster1"), False)
        End Sub

        Private Sub btnCancel2_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnCancel2.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            pnlSpreadsheet.Visible = True
            pnlImport.Visible = False
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

            Import()

            Dim objTable As DataTable = grdImport.DataSource
            Dim blnError As Boolean = False
            Dim strErrors As String = ""
            Dim objCol As BoundField

            Try
                JobSkillMaster.InsertJobSkillsImport(SessionManager.SelectedValueJob, SessionManager.UserID, objTable)
                For Each dtRow As DataRow In objTable.Rows
                    If dtRow("Errors").ToString.Trim.Length > 0 Then
                        blnError = True
                        strErrors += dtRow("Errors") & ": " & vbCrLf
                    End If
                Next dtRow
            Catch Exc As Exception
                blnError = True
                strErrors += "Unknown error occured - " & Exc.ToString
            End Try

            If blnError Then
                objCol = New BoundField
                objCol.DataField = "Errors"
                objCol.HeaderText = "Error"
                grdImport.Columns.Add(objCol)
                grdImport.DataSource = objTable
                grdImport.DataBind()
                Master.DisplayError(strErrors)
                Return
            Else
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("JobSkillMaster1"), False)
            End If
        End Sub
#End Region

#Region " Custom Functions"

#Region " Initialize DataGrid"
        Private Sub InitializeDataGrid()
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
                Dim objColumn As BoundField

                'Job
                objColumn = New BoundField
                objColumn.HeaderText = "Job"
                objColumn.DataField = "Job"
                objColumn.ItemStyle.Width = New Unit("100px")
                grdImport.Columns.Add(objColumn)

                'Skill Category
                objColumn = New BoundField
                objColumn.HeaderText = "Skill Category"
                objColumn.DataField = "SkillCategory"
                objColumn.ItemStyle.Width = New Unit("200px")
                grdImport.Columns.Add(objColumn)

                'Skill
                objColumn = New BoundField
                objColumn.HeaderText = "Skill"
                objColumn.DataField = "Skill"
                objColumn.ItemStyle.Width = New Unit("100px")
                grdImport.Columns.Add(objColumn)

                'Sequence
                objColumn = New BoundField
                objColumn.HeaderText = "Sequence"
                objColumn.DataField = "Sequence"
                objColumn.ItemStyle.Width = New Unit("100px")
                grdImport.Columns.Add(objColumn)

                'Assessment Criteria
                objColumn = New BoundField
                objColumn.HeaderText = "Assessment Criteria"
                objColumn.DataField = "AssessmentCriteria"
                objColumn.ItemStyle.Width = New Unit("200px")
                grdImport.Columns.Add(objColumn)

                'Required Rating
                objColumn = New BoundField
                objColumn.HeaderText = "Required Rating"
                objColumn.DataField = "RequiredRating"
                objColumn.ItemStyle.Width = New Unit("200px")
                grdImport.Columns.Add(objColumn)

                'Desired Rating
                objColumn = New BoundField
                objColumn.HeaderText = "Desired Rating"
                objColumn.DataField = "DesiredRating"
                objColumn.ItemStyle.Width = New Unit("200px")
                grdImport.Columns.Add(objColumn)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InitializeDataGrid", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

#Region " Initialize Excel From DataGrid"
        Private Sub InitializeExcelFromDataGrid(ByVal dg As GridView)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try
            Try
                Dim sbExcel As New StringBuilder
                sbExcel.Append("<table cellspacing='0' rules='all' border='1' id='grdReportSummary' style='width:100%;border-collapse:collapse;'>")
                sbExcel.Append("<tr style='color:#ffffff;background-color:#41519a;font-weight:bold;'>")
                For Each col As BoundField In dg.Columns
                    If col.HeaderText.Trim <> "" Then
                        sbExcel.Append("<td>" & col.HeaderText & "</td>")
                    End If
                Next
                sbExcel.Append("</tr>")
                sbExcel.Append("</table>")
                HTMLData.Text = sbExcel.ToString
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InitializeExcelFromDataGrid", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

#Region " Validate Row"
        Private Function ValidateRow(ByVal rowindex As Int16) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim strError As String = String.Empty
                Dim bError As Boolean = False

                'Setup the cells
                SetupCells(rowindex, 4)

                cells(rowindex, 4).Value = (rowindex - 1).ToString

                'Job - Verify that this job exists
                If JobMaster.SelectJobNameFromJobID(Session("SelectedValueJob")).ToUpper <> cells(rowindex, 1).Text.ToString.ToUpper Then
                    strError += "Job does not match Selected Job: "
                    bError = True
                End If

                'Skill Category
                If SkillCategoryMaster.SelectSkillCategoryID(cells(rowindex, 2).Text) = 0 Then
                    strError += "Skill Category doesn't exist: "
                    bError = True
                End If

                'Skill
                If cells(rowindex, 3).Text.ToString.Trim.Length = 0 Then
                    strError += "Skill is required: "
                    bError = True
                End If

                'Required rating
                If cells(rowindex, 6).Text.ToString.Trim.Length = 0 Then
                    strError += "Required Rating is required: "
                    bError = True
                ElseIf Not IsNumeric(cells(rowindex, 6).Text) Then
                    strError += "Invalid Required Rating: "
                    bError = True
                End If

                'Desired Rating
                If cells(rowindex, 7).Text.ToString.Trim.Length = 0 Then
                    strError += "Desired Rating is required: "
                    bError = True
                ElseIf Not IsNumeric(cells(rowindex, 7).Text) Then
                    strError += "Invalid Desired Rating: "
                    bError = True
                End If

                If bError Then
                    cells(rowindex, 8).value = "Row " & strError.Trim()
                    Return False
                Else
                    cells(rowindex, 8).value = ""
                    Return True
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - ValidateRow", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Function
#End Region

#Region " Setup Cells"
        Private Sub SetupCells(ByVal rowindex As Integer, ByVal Cellcount As Integer)
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
                For cellindex As Integer = 1 To Cellcount
                    cells(rowindex, cellindex).Font.Color = 0 'Black
                    cells(rowindex, cellindex).Font.Bold = False
                Next
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - SetupCells", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

#Region " Setup DataTable"
        Private Sub SetupDataTable(ByRef dt As DataTable, ByRef grd As GridView)
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
                For Each col As DataControlField In grdImport.Columns
                    If TypeOf col Is BoundField Then
                        dt.Columns.Add(New DataColumn(CType(col, BoundField).DataField))
                    End If
                Next
                dt.Columns.Add(New DataColumn("Errors"))
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - SetupDataTable", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

#Region " Populate DataRow"
        Private Function PopulateDataRow(ByVal rowindex As Integer, ByRef dr As DataRow) As Boolean
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
                Dim colindex As Integer = 0
                For Each col As DataControlField In grdImport.Columns
                    If TypeOf col Is BoundField Then
                        colindex = colindex + 1
                        dr(CType(col, BoundField).DataField) = cells(rowindex, colindex).Text
                    End If
                Next
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - PopulateDataRow", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                Return False
            End Try
        End Function
#End Region

#Region " Import"
        Private Sub Import()
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
                Dim dt As New DataTable
                SetupDataTable(dt, grdImport)

                objExcel.DataType = "HTMLData"
                objExcel.HTMLData = HTMLData.Text

                objExcel.Cells(1, 1).Select()
                cells = objExcel.Selection.Cells

                Dim rowindex As Integer = 2
                Dim dr As DataRow

                Do
                    If ValidateRow(rowindex) = False Then
                        cells(rowindex).EntireRow.Interior.Color = "Red"
                        blnError = True
                    Else
                        cells(rowindex).EntireRow.Interior.Color = ""
                    End If
                    dr = dt.NewRow
                    If Not PopulateDataRow(rowindex, dr) Then
                        blnError = True
                    End If
                    dt.Rows.Add(dr)
                    rowindex = rowindex + 1
                Loop Until cells(rowindex, 1).Text = "" And cells(rowindex, 2).Text = "" And cells(rowindex, 3).text = "" And cells(rowindex, 4).text = "" And cells(rowindex, 5).Text = "" And cells(rowindex, 6).Text = "" And cells(rowindex, 7).Text = ""

                If Not blnError Then
                    grdImport.DataSource = dt
                    grdImport.DataBind()
                    pnlImport.Visible = True
                    grdImport.Visible = True
                    pnlSpreadsheet.Visible = False
                Else
                    pnlImport.Visible = False
                    pnlSpreadsheet.Visible = True
                End If
                HTMLData.Text = objExcel.HTMLData
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - Import", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

#End Region

    End Class
End Namespace
