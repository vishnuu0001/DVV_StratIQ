#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.DataAccess.Custom
Imports Microsoft.Office.Interop
Imports System.Web.Security
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class TeamOPIValues3
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Team OPI Data Import"
        Private Shared ReadOnly ProgramName As String = "TeamOPIValues3"
#End Region

#Region " Private Variables"
        Private blnDataGridValuesValid As Boolean
        Private cells As Owc11.Range 'Cells collection
        Private blnError As Boolean = False

        Private _TimeRequired As Boolean = False
        Private _OPIType As String = String.Empty
        Private _OPISize As Integer = 0
        Private _NegativeEntryAllowed As Boolean = False
        Private _CalculateValue As Boolean = False
        Private _OPIError As String = String.Empty
        Private _OPIRegEx As String = String.Empty
        Private _OPIFormula As String = String.Empty
        Private _OPICount As Integer = 0

        Private _A1 As String = String.Empty
        Private _A1Type As String = String.Empty
        Private _A1Size As Integer = 0
        Private _A1Error As String = String.Empty
        Private _A1RegEx As String = String.Empty
        Private _A2 As String = String.Empty
        Private _A2Type As String = String.Empty
        Private _A2Size As Integer = 0
        Private _A2Error As String = String.Empty
        Private _A2RegEx As String = String.Empty
        Private _A3 As String = String.Empty
        Private _A3Type As String = String.Empty
        Private _A3Size As Integer = 0
        Private _A3Error As String = String.Empty
        Private _A3RegEx As String = String.Empty
        Private _A4 As String = String.Empty
        Private _A4Type As String = String.Empty
        Private _A4Size As Integer = 0
        Private _A4Error As String = String.Empty
        Private _A4RegEx As String = String.Empty
        Private _A5 As String = String.Empty
        Private _A5Type As String = String.Empty
        Private _A5Size As Integer = 0
        Private _A5Error As String = String.Empty
        Private _A5RegEx As String = String.Empty
        Private _A6 As String = String.Empty
        Private _A6Type As String = String.Empty
        Private _A6Size As Integer = 0
        Private _A6Error As String = String.Empty
        Private _A6RegEx As String = String.Empty
#End Region

#Region " Load Culture Translations"
        Private Sub LoadCultureTranslations()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                btnOK.Text = GetTranslationString("loaddata", btnOK.Text)
                btnCancel.Text = GetTranslationString("cancel", btnCancel.Text)
                btnImport.Text = GetTranslationString("validatedata", btnImport.Text)
                btnCancel2.Text = GetTranslationString("cancel", btnCancel2.Text)
                For i As Integer = 0 To grdImport.Columns.Count - 1
                    grdImport.Columns(i).HeaderText = GetTranslationString(grdImport.Columns(i).HeaderText, grdImport.Columns(i).HeaderText)
                Next
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadCultureTranslations", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

#Region " LoadJavaScripts"
        Private Sub LoadJavaScripts()
            btnImport.Attributes.Add("onclick", "javascript:return ImportFromExcel();")
        End Sub
#End Region

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, ProgramName, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If Not Page.IsPostBack Then
                LoadCultureTranslations()
            End If

            Master.HeaderMessage = GetTranslationString(FormName, FormName) & " - " & GetTranslationString("teamopivaluesimport", "Team OPI Values Import")
            Master.IconImage = Request.ApplicationPath + "/images/TeamOPI.gif"

            LoadJavaScripts()
            LoadPageValidation()

            If Not Page.IsPostBack Then
                InitializeGridView()
                InitializeExcelFromGridView(grdImport)
            End If
        End Sub
        Private Sub grdImport_ItemDataBound(ByVal sender As System.Object, ByVal e As System.Web.UI.WebControls.DataGridItemEventArgs)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If e.Item.ItemType = ListItemType.Item Or e.Item.ItemType = ListItemType.AlternatingItem Then
                e.Item.Cells(0).Text = (e.Item.ItemIndex + 1).ToString
            End If
        End Sub
        Private Sub btnImport_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnImport.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
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
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamOPIValues1"), False)
        End Sub
        Private Sub btnCancel2_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnCancel2.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
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
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
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
                InsertTeamOPIValuesImport(SessionManager.SelectedTeamID, SessionManager.SelectedOPI, SessionManager.UserID, objTable)

                'loop through the datatable and look for errors
                For Each dtRow As DataRow In objTable.Rows
                    If dtRow("Errors").ToString.Trim.Length > 0 Then
                        'error
                        blnError = True
                        strErrors += dtRow("Errors") & ": " & vbCrLf
                    End If
                Next dtRow
            Catch ex As Exception
                blnError = True
                strErrors += "Unknown error occured - " & ex.ToString
            End Try

            If blnError Then
                'now, rebind the datagrid
                objCol = New BoundField
                objCol.DataField = "Errors"
                objCol.HeaderText = "Error"
                grdImport.Columns.Add(objCol)
                grdImport.DataSource = objTable
                grdImport.DataBind()
                Master.DisplayError(strErrors)
                Return
            Else
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamOPIValues1"), False)
            End If
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub InitializeGridView()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim objColumn As BoundField

                If _A1.Length > 0 Then
                    objColumn = New BoundField
                    objColumn.HeaderText = _A1
                    objColumn.DataField = "Attribute1Value"
                    grdImport.Columns.Add(objColumn)
                End If
                'A2
                If _A2.Length > 0 Then
                    objColumn = New BoundField
                    objColumn.HeaderText = _A2
                    objColumn.DataField = "Attribute2Value"
                    grdImport.Columns.Add(objColumn)
                End If
                'A3
                If _A3.Length > 0 Then
                    objColumn = New BoundField
                    objColumn.HeaderText = _A3
                    objColumn.DataField = "Attribute3Value"
                    grdImport.Columns.Add(objColumn)
                End If
                'A4
                If _A4.Length > 0 Then
                    objColumn = New BoundField
                    objColumn.HeaderText = _A4
                    objColumn.DataField = "Attribute4Value"
                    grdImport.Columns.Add(objColumn)
                End If
                'A5
                If _A5.Length > 0 Then
                    objColumn = New BoundField
                    objColumn.HeaderText = _A5
                    objColumn.DataField = "Attribute5Value"
                    grdImport.Columns.Add(objColumn)
                End If
                'A6
                If _A6.Length > 0 Then
                    objColumn = New BoundField
                    objColumn.HeaderText = _A6
                    objColumn.DataField = "Attribute6Value"
                    grdImport.Columns.Add(objColumn)
                End If

                'add value, cost and notes
                objColumn = New BoundField
                objColumn.HeaderText = "OPI Value"
                objColumn.DataField = "OPIValue"
                grdImport.Columns.Add(objColumn)

                objColumn = New BoundField
                objColumn.HeaderText = "Cost"
                objColumn.DataField = "Cost"
                grdImport.Columns.Add(objColumn)

                objColumn = New BoundField
                objColumn.HeaderText = "Notes"
                objColumn.DataField = "Notes"
                grdImport.Columns.Add(objColumn)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InitializeGridView", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub InitializeExcelFromGridView(ByVal dg As GridView)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, dg.ID)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim sbExcel As New StringBuilder

                sbExcel.Append("<table cellspacing='0' rules='all' border='1' id='grdReportSummary' style='width:100%;border-collapse:collapse;'>")
                sbExcel.Append("<tr style='color:White;background-color:DarkBlue;font-weight:bold;'>")
                For Each col As BoundField In dg.Columns
                    If col.HeaderText.Trim <> "" Then
                        sbExcel.Append("<td>" & col.HeaderText & "</td>")
                    End If
                Next
                sbExcel.Append("</tr>")
                sbExcel.Append("</table>")
                HTMLData.Text = sbExcel.ToString
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InitializeExcelFromGridView", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Function ValidateRow(ByVal rowindex As Int16) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, rowindex)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim strError As String = ""
                Dim bError As Boolean = False

                'Setup the cells
                SetupCells(rowindex, 4)

                'DateTime Validation
                If Not IsDate(cells(rowindex, 1).Text) Then
                    strError += "OPI Date/Time is not valid: "
                    bError = True
                End If

                Dim strFormula As String
                Dim bFormulaError As Boolean = False

                If _CalculateValue Then
                    If InStr(_OPIFormula, "[Attribute1]") > 0 Then
                        If _OPICount = 0 Then
                            bFormulaError = True
                        End If
                    End If
                    strFormula = "=(" & _OPIFormula.Replace("[Attribute1]", "(B" & rowindex.ToString & ")")
                    If InStr(_OPIFormula, "[Attribute2]") > 0 Then
                        If _OPICount = 1 Then
                            bFormulaError = True
                        End If
                    End If
                    strFormula = strFormula.Replace("[Attribute2]", "(C" & rowindex.ToString & ")")
                    If InStr(_OPIFormula, "[Attribute3]") > 0 Then
                        If _OPICount = 2 Then
                            bFormulaError = True
                        End If
                    End If
                    strFormula = strFormula.Replace("[Attribute3]", "(D" & rowindex.ToString & ")")
                    If InStr(_OPIFormula, "[Attribute4]") > 0 Then
                        If _OPICount = 3 Then
                            bFormulaError = True
                        End If
                    End If
                    strFormula = strFormula.Replace("[Attribute4]", "(E" & rowindex.ToString & ")")
                    If InStr(_OPIFormula, "[Attribute5]") > 0 Then
                        If _OPICount = 4 Then
                            bFormulaError = True
                        End If
                    End If
                    strFormula = strFormula.Replace("[Attribute5]", "(F" & rowindex.ToString & ")")
                    If InStr(_OPIFormula, "[Attribute6]") > 0 Then
                        If _OPICount = 5 Then
                            bFormulaError = True
                        End If
                    End If
                    strFormula = strFormula.Replace("[Attribute6]", "(G" & rowindex.ToString & ")") & ")"

                    If bFormulaError Then
                        Master.DisplayError(GetTranslationString("badopicalcformula", "Error in OPI Calculation Formula"))

                        Return False
                    End If

                    cells(rowindex, 2 + _OPICount).Formula = strFormula
                End If

                'validate attributes
                'A1
                If _A1.Length > 0 Then
                    If Not Regex.IsMatch(cells(rowindex, 2).Text, _A1RegEx) Then
                        strError += _A1Error & ": "
                        bError = True
                    End If
                End If
                'A2
                If _A2.Length > 0 Then
                    If Not Regex.IsMatch(cells(rowindex, 3).Text, _A2RegEx) Then
                        strError += _A2Error & ": "
                        bError = True
                    End If
                End If
                'A3
                If _A3.Length > 0 Then
                    If Not Regex.IsMatch(cells(rowindex, 4).Text, _A3RegEx) Then
                        strError += _A3Error & ": "
                        bError = True
                    End If
                End If
                'A4
                If _A4.Length > 0 Then
                    If Not Regex.IsMatch(cells(rowindex, 5).Text, _A4RegEx) Then
                        strError += _A4Error & ": "
                        bError = True
                    End If
                End If
                'A5
                If _A5.Length > 0 Then
                    If Not Regex.IsMatch(cells(rowindex, 6).Text, _A5RegEx) Then
                        strError += _A5Error & ": "
                        bError = True
                    End If
                End If
                'A6
                If _A6.Length > 0 Then
                    If Not Regex.IsMatch(cells(rowindex, 7).Text, _A6RegEx) Then
                        strError += _A6Error & ": "
                        bError = True
                    End If
                End If

                'OPI Value validation
                If Not _CalculateValue Then
                    If Not Regex.IsMatch(cells(rowindex, 2 + _OPICount).Text, _OPIRegEx) Then
                        strError += _OPIError & ": "
                        bError = True
                    End If
                Else
                    If Not IsNumeric(cells(rowindex, 2 + _OPICount).Text) Then
                        strError += _OPIError & ": "
                        bError = True
                    End If
                End If

                'Cost validation
                If Not IsNumeric(cells(rowindex, 3 + _OPICount).Text) Then
                    strError += "Enter Cost"
                    bError = True
                End If

                If bError Then
                    cells(rowindex, 5 + _OPICount).value = strError
                    Return False
                Else
                    cells(rowindex, 5 + _OPICount).value = ""
                    Return True
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - ValidateRow", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Function
        Private Sub SetupCells(ByVal rowindex As Integer, ByVal Cellcount As Integer)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, rowindex, Cellcount)
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
        Private Sub SetupDataTable(ByRef dt As DataTable, ByRef grd As GridView)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", grd.ID)
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

                'now, add one more column for errors
                dt.Columns.Add(New DataColumn("Errors"))
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - SetupDataTable", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Function PopulateDataRow(ByVal rowindex As Integer, ByRef dr As DataRow) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, rowindex, dr.ToString)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim colindex As Integer = 0

            Try
                For Each col As DataControlField In grdImport.Columns
                    If TypeOf col Is BoundField Then
                        colindex = colindex + 1
                        Select Case colindex
                            Case 1
                                If _TimeRequired Then
                                    dr(CType(col, BoundField).DataField) = RegionalConversion.FormatSQLDate(cells(rowindex, colindex).Text, True)
                                Else
                                    dr(CType(col, BoundField).DataField) = RegionalConversion.FormatSQLDate(cells(rowindex, colindex).Text)
                                End If
                            Case 2 + _OPICount
                                If IsNumeric(cells(rowindex, colindex).Text) Then
                                    Select Case _OPIType
                                        Case "D"
                                            dr(CType(col, BoundField).DataField) = String.Format("{0:F" + _OPISize.ToString + "}", CDbl(cells(rowindex, colindex).Text))
                                        Case "N"
                                            dr(CType(col, BoundField).DataField) = String.Format("{0:F0}", CDbl(cells(rowindex, colindex).Text))
                                    End Select
                                Else
                                    Master.DisplayError(GetTranslationString("invalidopi", "Invalid OPI Value"))
                                    Return False
                                End If
                            Case Is < _OPICount + 2
                                If _A1.Length > 0 And colindex = 2 Then
                                    Select Case _A1Type
                                        Case "D"
                                            dr(CType(col, BoundField).DataField) = String.Format("{0:F" + _A1Size.ToString + "}", CDbl(cells(rowindex, colindex).Text))
                                        Case "N"
                                            dr(CType(col, BoundField).DataField) = String.Format("{0:F0}", CDbl(cells(rowindex, colindex).Text))
                                        Case Else
                                            dr(CType(col, BoundField).DataField) = cells(rowindex, colindex).Text
                                    End Select
                                ElseIf _A2.Length > 0 And colindex = 3 Then
                                    Select Case _A2Type
                                        Case "D"
                                            dr(CType(col, BoundField).DataField) = String.Format("{0:F" + _A2Size.ToString + "}", CDbl(cells(rowindex, colindex).Text))
                                        Case "N"
                                            dr(CType(col, BoundField).DataField) = String.Format("{0:F0}", CDbl(cells(rowindex, colindex).Text))
                                        Case Else
                                            dr(CType(col, BoundField).DataField) = cells(rowindex, colindex).Text
                                    End Select
                                ElseIf _A3.Length > 0 And colindex = 4 Then
                                    Select Case _A3Type
                                        Case "D"
                                            dr(CType(col, BoundField).DataField) = String.Format("{0:F" + _A3Size.ToString + "}", CDbl(cells(rowindex, colindex).Text))
                                        Case "N"
                                            dr(CType(col, BoundField).DataField) = String.Format("{0:F0}", CDbl(cells(rowindex, colindex).Text))
                                        Case Else
                                            dr(CType(col, BoundField).DataField) = cells(rowindex, colindex).Text
                                    End Select
                                ElseIf _A4.Length > 0 And colindex = 5 Then
                                    Select Case _A4Type
                                        Case "D"
                                            dr(CType(col, BoundField).DataField) = String.Format("{0:F" + _A4Size.ToString + "}", CDbl(cells(rowindex, colindex).Text))
                                        Case "N"
                                            dr(CType(col, BoundField).DataField) = String.Format("{0:F0}", CDbl(cells(rowindex, colindex).Text))
                                        Case Else
                                            dr(CType(col, BoundField).DataField) = cells(rowindex, colindex).Text
                                    End Select
                                ElseIf _A5.Length > 0 And colindex = 6 Then
                                    Select Case _A5Type
                                        Case "D"
                                            dr(CType(col, BoundField).DataField) = String.Format("{0:F" + _A5Size.ToString + "}", CDbl(cells(rowindex, colindex).Text))
                                        Case "N"
                                            dr(CType(col, BoundField).DataField) = String.Format("{0:F0}", CDbl(cells(rowindex, colindex).Text))
                                        Case Else
                                            dr(CType(col, BoundField).DataField) = cells(rowindex, colindex).Text
                                    End Select
                                ElseIf _A6.Length > 0 And colindex = 7 Then
                                    Select Case _A6Type
                                        Case "D"
                                            dr(CType(col, BoundField).DataField) = String.Format("{0:F" + _A6Size.ToString + "}", CDbl(cells(rowindex, colindex).Text))
                                        Case "N"
                                            dr(CType(col, BoundField).DataField) = String.Format("{0:F0}", CDbl(cells(rowindex, colindex).Text))
                                        Case Else
                                            dr(CType(col, BoundField).DataField) = cells(rowindex, colindex).Text
                                    End Select
                                End If
                            Case Else
                                dr(CType(col, BoundField).DataField) = cells(rowindex, colindex).Text
                        End Select
                    End If
                Next

                Return True
            Catch Exc As Exception
                Return False
            End Try
        End Function
        Private Function CheckForDuplicates(ByRef passTable As DataTable, ByRef objRange As Owc11.Range) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim iCounter As Integer
                Dim iRowCounter As Integer
                Dim dtRow As DataRow
                Dim dtCompareRow As DataRow
                Dim bDuplicate As Boolean = False

                For iCounter = 0 To passTable.Rows.Count - 1
                    dtRow = passTable.Rows(iCounter)

                    'now, loop through the REST of the rows
                    For iRowCounter = iCounter + 1 To passTable.Rows.Count - 1
                        dtCompareRow = passTable.Rows(iRowCounter)

                        If dtRow(0) = dtCompareRow(0) Then
                            If dtRow(1) = dtCompareRow(1) Then
                                If _OPICount = 1 Then
                                    bDuplicate = True
                                    Exit For
                                Else
                                    If dtRow(2) = dtCompareRow(2) Then
                                        If _OPICount = 2 Then
                                            bDuplicate = True
                                            Exit For
                                        Else
                                            If dtRow(3) = dtCompareRow(3) Then
                                                If _OPICount = 3 Then
                                                    bDuplicate = True
                                                    Exit For
                                                Else
                                                    If dtRow(4) = dtCompareRow(4) Then
                                                        If _OPICount = 4 Then
                                                            bDuplicate = True
                                                            Exit For
                                                        Else
                                                            If dtRow(5) = dtCompareRow(5) Then
                                                                If _OPICount = 5 Then
                                                                    bDuplicate = True
                                                                    Exit For
                                                                Else
                                                                    If dtRow(6) = dtCompareRow(6) Then
                                                                        If _OPICount = 6 Then
                                                                            bDuplicate = True
                                                                            Exit For
                                                                        End If
                                                                    End If
                                                                End If
                                                            End If
                                                        End If
                                                    End If
                                                End If
                                            End If
                                        End If
                                    End If
                                End If
                            End If
                        End If
                    Next iRowCounter

                    If bDuplicate Then
                        Exit For
                    End If
                Next iCounter

                If bDuplicate Then
                    cells(iCounter + 2).EntireRow.Interior.Color = "Orange"
                    cells(iRowCounter + 2).EntireRow.Interior.Color = "Orange"
                    Master.DisplayError(GetTranslationString("duplicaterows", "Duplicate Rows Detected."))
                    Return False
                Else
                    Return True
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - CheckForDuplicates", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Function
        Private Sub Import()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
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
                    If Not CheckForDuplicates(dt, cells) Then
                        blnError = True
                    End If
                End If

                If Not blnError Then
                    grdImport.DataSource = dt
                    grdImport.DataBind()
                    pnlImport.Visible = True
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
        Private Sub LoadPageValidation()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim dtHolder As DataTable = TeamOPI.SelectTeamOPI(SessionManager.SelectedTeamID, SessionManager.SelectedOPI)
                Dim dr As DataRow = dtHolder.Rows(0)

                _OPIType = dr("OPIEntryType")
                _OPISize = dr("OPISize")
                _TimeRequired = dr("TimeEntryRequired").ToString
                _NegativeEntryAllowed = dr("NegativeEntryAllowed").ToString
                _CalculateValue = dr("CalculateValue").ToString
                _OPIFormula = dr("OPIFormula").ToString

                If (IsDBNull(dr("Attribute1"))) = False Then
                    _OPICount += 1
                    _A1 = dr("Attribute1")
                    _A1Type = dr("Attribute1EntryType")
                    _A1Size = dr("Attribute1Size")
                End If
                If (IsDBNull(dr("Attribute2"))) = False Then
                    _OPICount += 1
                    _A2 = dr("Attribute2")
                    _A2Type = dr("Attribute2EntryType")
                    _A2Size = dr("Attribute2Size")
                End If
                If (IsDBNull(dr("Attribute3"))) = False Then
                    _OPICount += 1
                    _A3 = dr("Attribute3")
                    _A3Type = dr("Attribute3EntryType")
                    _A3Size = dr("Attribute3Size")
                End If
                If (IsDBNull(dr("Attribute4"))) = False Then
                    _OPICount += 1
                    _A4 = dr("Attribute4")
                    _A4Type = dr("Attribute4EntryType")
                    _A4Size = dr("Attribute4Size")
                End If
                If (IsDBNull(dr("Attribute5"))) = False Then
                    _OPICount += 1
                    _A5 = dr("Attribute5")
                    _A5Type = dr("Attribute5EntryType")
                    _A5Size = dr("Attribute5Size")
                End If
                If (IsDBNull(dr("Attribute6"))) = False Then
                    _OPICount += 1
                    _A6 = dr("Attribute6")
                    _A6Type = dr("Attribute6EntryType")
                    _A6Size = dr("Attribute6Size")
                End If
                SetupAttributes()
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadPageValidation", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub SetupAttributes()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim strDecSeperator As String = System.Threading.Thread.CurrentThread.CurrentCulture.NumberFormat.NumberDecimalSeparator

                Select Case _OPIType
                    Case "N"
                        If _NegativeEntryAllowed Then
                            _OPIRegEx = "^-?\d{1," + _OPISize.ToString + "}$"
                            _OPIError = "OPI Value Value must be a numeric value with no more than " + _OPISize.ToString + " digits"
                        Else
                            _OPIRegEx = "^\d{1," + _OPISize.ToString + "}$"
                            _OPIError = "OPI Value Value must be a numeric value with no more than " + _OPISize.ToString + " digits"
                        End If
                    Case "D"
                        If _NegativeEntryAllowed Then
                            _OPIRegEx = "(^-?\d{0,7}\" & strDecSeperator & "{1}\d{0," + _OPISize.ToString + "}$)|(^-?\d{1,7}$)"
                            _OPIError = "OPI Value Value must be decimal value with no more than " + _OPISize.ToString + " decimal places"
                        Else
                            _OPIRegEx = "(^\d{0,7}\" & strDecSeperator & "{1}\d{0," + _OPISize.ToString + "}$)|(^\d{1,7}$)"
                            _OPIError = "OPI Value Value must be decimal value with no more than " + _OPISize.ToString + " decimal places"
                        End If
                        'Case "C"
                        '    _OPIRegEx = "^.{1," + _OPISize.ToString + "}$"
                        '    _OPIError = "OPI Value Value must contain " + (_OPISize).ToString + " or less characters"
                        'Case "R"
                        '    _OPIRegEx = "^.{" + _OPISize.ToString + "}$"
                        '    _OPIError = "OPI Value Value must contain " + _OPISize.ToString + " characters"
                End Select

                'attribute 1
                If _A1.Length > 0 Then
                    Select Case _A1Type.ToUpper
                        Case "N"
                            _A1RegEx = "^\d{1," + _A1Size.ToString + "}$"
                            _A1Error = _A1 + " Value must be a numeric value with no more than " + _A1Size.ToString + " digits"
                        Case "D"
                            _A1RegEx = "(^\d{0,7}\" & strDecSeperator & "{1}\d{0," + _A1Size.ToString + "}$)|(^\d{1,7}$)"
                            _A1Error = _A1 + " Value must be decimal value with no more than " + _A1Size.ToString + " decimal places"
                        Case "C"
                            _A1RegEx = "^.{1," + _A1Size.ToString + "}$"
                            _A1Error = _A1 + " Value must contain " + (_A1Size).ToString + " or less characters"
                        Case "R"
                            _A1RegEx = "^.{" + _A1Size.ToString + "}$"
                            _A1Error = _A1 + " Value must contain " + _A1Size.ToString + " characters"
                    End Select
                End If

                'attribute 2
                If _A2.Length > 0 Then
                    Select Case _A2Type.ToUpper
                        Case "N"
                            _A2RegEx = "^\d{1," + _A2Size.ToString + "}$"
                            _A2Error = _A2 + " Value must be a numeric value with no more than " + _A2Size.ToString + " digits"
                        Case "D"
                            _A2RegEx = "(^\d{0,7}\" & strDecSeperator & "{1}\d{0," + _A2Size.ToString + "}$)|(^\d{1,7}$)"
                            _A2Error = _A2 + " Value must be decimal value with no more than " + _A2Size.ToString + " decimal places"
                        Case "C"
                            _A2RegEx = "^.{1," + _A2Size.ToString + "}$"
                            _A2Error = _A2 + " Value must contain " + (_A2Size).ToString + " or less characters"
                        Case "R"
                            _A2RegEx = "^.{" + _A2Size.ToString + "}$"
                            _A2Error = _A2 + " Value must contain " + _A2Size.ToString + " characters"
                    End Select
                End If

                'attribute 3
                If _A3.Length > 0 Then
                    Select Case _A3Type.ToUpper
                        Case "N"
                            _A3RegEx = "^\d{1," + _A3Size.ToString + "}$"
                            _A3Error = _A3 + " Value must be a numeric value with no more than " + _A3Size.ToString + " digits"
                        Case "D"
                            _A3RegEx = "(^\d{0,7}\" & strDecSeperator & "{1}\d{0," + _A3Size.ToString + "}$)|(^\d{1,7}$)"
                            _A3Error = _A3 + " Value must be decimal value with no more than " + _A3Size.ToString + " decimal places"
                        Case "C"
                            _A3RegEx = "^.{1," + _A3Size.ToString + "}$"
                            _A3Error = _A3 + " Value must contain " + (_A3Size).ToString + " or less characters"
                        Case "R"
                            _A3RegEx = "^.{" + _A3Size.ToString + "}$"
                            _A3Error = _A3 + " Value must contain " + _A3Size.ToString + " characters"
                    End Select
                End If

                'attribute 4
                If _A4.Length > 0 Then
                    Select Case _A4Type.ToUpper
                        Case "N"
                            _A4RegEx = "^\d{1," + _A4Size.ToString + "}$"
                            _A4Error = _A4 + " Value must be a numeric value with no more than " + _A4Size.ToString + " digits"
                        Case "D"
                            _A4RegEx = "(^\d{0,7}\" & strDecSeperator & "{1}\d{0," + _A4Size.ToString + "}$)|(^\d{1,7}$)"
                            _A4Error = _A4 + " Value must be decimal value with no more than " + _A4Size.ToString + " decimal places"
                        Case "C"
                            _A4RegEx = "^.{1," + _A4Size.ToString + "}$"
                            _A4Error = _A4 + " Value must contain " + (_A4Size).ToString + " or less characters"
                        Case "R"
                            _A4RegEx = "^.{" + _A4Size.ToString + "}$"
                            _A4Error = _A4 + " Value must contain " + _A4Size.ToString + " characters"
                    End Select
                End If

                'attribute 5
                If _A5.Length > 0 Then
                    Select Case _A5Type.ToUpper
                        Case "N"
                            _A5RegEx = "^\d{1," + _A5Size.ToString + "}$"
                            _A5Error = _A5 + " Value must be a numeric value with no more than " + _A5Size.ToString + " digits"
                        Case "D"
                            _A5RegEx = "(^\d{0,7}\" & strDecSeperator & "{1}\d{0," + _A5Size.ToString + "}$)|(^\d{1,7}$)"
                            _A5Error = _A5 + " Value must be decimal value with no more than " + _A5Size.ToString + " decimal places"
                        Case "C"
                            _A5RegEx = "^.{1," + _A5Size.ToString + "}$"
                            _A5Error = _A5 + " Value must contain " + (_A5Size).ToString + " or less characters"
                        Case "R"
                            _A5RegEx = "^.{" + _A5Size.ToString + "}$"
                            _A5Error = _A5 + " Value must contain " + _A5Size.ToString + " characters"
                    End Select
                End If

                'attribute 6
                If _A6.Length > 0 Then
                    Select Case _A6Type.ToUpper
                        Case "N"
                            _A6RegEx = "^\d{1," + _A6Size.ToString + "}$"
                            _A6Error = _A6 + " Value must be a numeric value with no more than " + _A6Size.ToString + " digits"
                        Case "D"
                            _A6RegEx = "(^\d{0,7}\" & strDecSeperator & "{1}\d{0," + _A6Size.ToString + "}$)|(^\d{1,7}$)"
                            _A6Error = _A6 + " Value must be decimal value with no more than " + _A6Size.ToString + " decimal places"
                        Case "C"
                            _A6RegEx = "^.{1," + _A6Size.ToString + "}$"
                            _A6Error = _A6 + " Value must contain " + (_A6Size).ToString + " or less characters"
                        Case "R"
                            _A6RegEx = "^.{" + _A6Size.ToString + "}$"
                            _A6Error = _A6 + " Value must contain " + _A6Size.ToString + " characters"
                    End Select
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - SetupAttributes", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub InsertTeamOPIValuesImport(ByVal passTeamID As Integer, ByVal passOPI As String, _
                                                    ByVal passUser As String, ByRef passDataTable As DataTable)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, passOPI, passUser, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnMasterConnection As SqlConnection = DataAccess.Connections.ApplicationConnection.OpenMasterConnection
            Dim trans As SqlTransaction = cnMasterConnection.BeginTransaction(IsolationLevel.ReadUncommitted)
            Dim bError As Boolean = False
            Dim strA1Value = ""
            Dim strA2Value = ""
            Dim strA3Value = ""
            Dim strA4Value = ""
            Dim strA5Value = ""
            Dim strA6Value = ""

            Try
                'loop through table rows and insert
                For Each objRow As DataRow In passDataTable.Rows
                    If passDataTable.Columns.Count > 5 Then
                        If _A1Type = "D" Then
                            strA1Value = RegionalConversion.FormatSQLSingle(objRow("Attribute1Value"))
                        Else
                            strA1Value = objRow("Attribute1Value")
                        End If

                        If passDataTable.Columns.Count > 6 Then
                            If _A2Type = "D" Then
                                strA2Value = RegionalConversion.FormatSQLSingle(objRow("Attribute2Value"))
                            Else
                                strA2Value = objRow("Attribute2Value")
                            End If

                            If passDataTable.Columns.Count > 7 Then
                                If _A3Type = "D" Then
                                    strA3Value = RegionalConversion.FormatSQLSingle(objRow("Attribute3Value"))
                                Else
                                    strA3Value = objRow("Attribute3Value")
                                End If

                                If passDataTable.Columns.Count > 8 Then
                                    If _A4Type = "D" Then
                                        strA4Value = RegionalConversion.FormatSQLSingle(objRow("Attribute4Value"))
                                    Else
                                        strA4Value = objRow("Attribute4Value")
                                    End If

                                    If passDataTable.Columns.Count > 9 Then
                                        If _A5Type = "D" Then
                                            strA5Value = RegionalConversion.FormatSQLSingle(objRow("Attribute5Value"))
                                        Else
                                            strA5Value = objRow("Attribute5Value")
                                        End If

                                        If passDataTable.Columns.Count > 10 Then
                                            If _A6Type = "D" Then
                                                strA6Value = RegionalConversion.FormatSQLSingle(objRow("Attribute6Value"))
                                            Else
                                                strA6Value = objRow("Attribute6Value")
                                            End If
                                        End If
                                    End If
                                End If
                            End If
                        End If
                    End If

                    Dim strOPI As String = ""
                    Dim strCost As String = RegionalConversion.FormatSQLSingle(objRow("Cost"))
                    If _OPIType = "D" Then
                        strOPI = RegionalConversion.FormatSQLSingle(objRow("OPIValue"))
                    Else
                        strOPI = objRow("OPIValue")
                    End If

                    TeamOPIValues.InsertTeamOPIValue(passTeamID, passOPI, RegionalConversion.FormatSQLDate(objRow("OPIValueDateTime")), strOPI, strCost, objRow("Notes"), strA1Value, strA2Value, strA3Value, strA4Value, strA5Value, strA6Value, passUser, cnMasterConnection, trans)
                Next objRow

                trans.Commit()
            Catch Exc As Exception
                trans.Rollback()
                Throw
            Finally
                DataAccess.Connections.ApplicationConnection.CloseMasterConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

    End Class
End Namespace
