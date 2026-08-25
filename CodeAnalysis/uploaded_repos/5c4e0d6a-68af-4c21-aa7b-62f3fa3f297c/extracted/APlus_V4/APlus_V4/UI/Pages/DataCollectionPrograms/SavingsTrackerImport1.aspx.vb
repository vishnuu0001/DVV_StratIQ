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
    Partial Class SavingsTrackerImport1
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Savings Tracker Import"
        Private Shared ReadOnly ProgramName As String = "SavingsTrackerImport1"
#End Region

#Region " Private Variables"
        Private blnDataGridValuesValid As Boolean
        Private cells As Owc11.Range 'Cells collection
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

            Master.HeaderMessage = "Savings Tracker Import"
            Master.IconImage = Request.ApplicationPath + "/images/TeamOPI.gif"
            LoadJavaScripts()

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

            If SessionManager.CallingProgram.Trim.Length > 0 Then
                Dim strProgram As String = SessionManager.CallingProgram
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CallingProgram)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strProgram), False)
            Else
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SavingsTracker1"), False)
            End If
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

            Dim objDT As DataTable = grdImport.DataSource
            Dim blnError As Boolean = False
            Dim strErrors As String = ""

            Dim cnMasterConnection As SqlConnection = APlus.DataAccess.Connections.ApplicationConnection.OpenMasterConnection
            Dim trans As SqlTransaction = cnMasterConnection.BeginTransaction(IsolationLevel.ReadUncommitted)

            Try
                Dim dtTracker As DataTable = TrackerCollection.SelectTrackerTypesByTracker(SessionManager.SelectedValueTrackerID)
                Dim dtView As DataView = dtTracker.DefaultView
                Dim strDate As String = ""
                Dim strFormula As String = ""
                Dim iTrackerCollectionID As Integer = 0
                Dim strValue As String = ""
                Dim strHistoric As String = ""
                Dim strTarget As String = ""
                Dim strSavings As String = ""
                Dim strTargetSavings As String = ""
                Dim strPlannedSavings As String = ""
                Dim strType As String()

                For iCol As Integer = 1 To 12
                    strDate = RegionalConversion.FormatSQLDate(lblYear.Text & "/" & iCol.ToString & "/01")

                    If objDT.Rows(0)(iCol).ToString.Trim.Length > 0 OrElse _
                    objDT.Rows(1)(iCol).ToString.Trim.Length > 0 OrElse _
                    objDT.Rows(2)(iCol).ToString.Trim.Length > 0 OrElse _
                    objDT.Rows(3)(iCol).ToString.Trim.Length > 0 Then
                        strValue = RegionalConversion.FormatSQLSingle(objDT.Rows(0)(iCol).ToString)
                        strHistoric = RegionalConversion.FormatSQLSingle(objDT.Rows(1)(iCol).ToString)
                        strTarget = RegionalConversion.FormatSQLSingle(objDT.Rows(3)(iCol).ToString)

                        SavingsTracker.UpdateTrackerValue(SessionManager.SelectedValueTrackerID, strDate, strValue, strHistoric, strTarget, strTargetSavings, strPlannedSavings, cnMasterConnection, trans)
                    End If

                    For iRow As Integer = 4 To objDT.Rows.Count - 1
                        strFormula = ""
                        strType = objDT.Rows(iRow)(0).ToString.Split(":")
                        If strType.Length = 2 Then
                            dtView.RowFilter = "TrackerType = '" & strType(0).Trim & "' AND SavingsType = '" & strType(1).Trim & "'"
                            If dtView.Count = 1 Then
                                iTrackerCollectionID = dtView(0)("TrackerCollectionID")

                                Dim blnFormulaExists As Boolean = False
                                Dim objDT1 As DataTable = TrackerCollection.SelectTrackerCollection(iTrackerCollectionID)
                                If Not objDT1 Is Nothing AndAlso objDT1.Rows.Count = 1 AndAlso objDT1.Rows(0)("Formula") IsNot DBNull.Value Then
                                    strFormula = "Import"
                                End If

                                If objDT.Rows(iRow)(iCol).ToString.Trim.Length > 0 AndAlso _
                                IsNumeric(objDT.Rows(iRow)(iCol).ToString) Then
                                    strSavings = RegionalConversion.FormatSQLSingle(objDT.Rows(iRow)(iCol).ToString)

                                    SavingsTracker.UpdateTrackerSavings(iTrackerCollectionID, strDate, strSavings, strFormula, cnMasterConnection, trans)
                                End If
                            End If
                        End If
                    Next
                Next

                trans.Commit()
            Catch ex As Exception
                trans.Rollback()

                blnError = True
                strErrors = "Error occured " & vbCrLf & ex.ToString
            End Try

            If blnError Then
                grdImport.DataSource = objDT
                grdImport.DataBind()
                Master.DisplayError(strErrors)

                Return
            Else
                If SessionManager.CallingProgram.Trim.Length > 0 Then
                    Dim strProgram As String = SessionManager.CallingProgram
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CallingProgram)
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strProgram), False)
                Else
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SavingsTracker1"), False)
                End If
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

                'Type
                objColumn = New BoundField
                objColumn.HeaderText = "Type"
                objColumn.DataField = "TrackerType"
                objColumn.ItemStyle.Width = New Unit(100)
                grdImport.Columns.Add(objColumn)

                'Jan
                objColumn = New BoundField
                objColumn.HeaderText = "Jan"
                objColumn.DataField = "Jan"
                grdImport.Columns.Add(objColumn)

                'Feb
                objColumn = New BoundField
                objColumn.HeaderText = "Feb"
                objColumn.DataField = "Feb"
                grdImport.Columns.Add(objColumn)

                'Mar
                objColumn = New BoundField
                objColumn.HeaderText = "Mar"
                objColumn.DataField = "Mar"
                grdImport.Columns.Add(objColumn)

                'Apr
                objColumn = New BoundField
                objColumn.HeaderText = "Apr"
                objColumn.DataField = "Apr"
                grdImport.Columns.Add(objColumn)

                'May
                objColumn = New BoundField
                objColumn.HeaderText = "May"
                objColumn.DataField = "May"
                grdImport.Columns.Add(objColumn)

                'Jun
                objColumn = New BoundField
                objColumn.HeaderText = "Jun"
                objColumn.DataField = "Jun"
                grdImport.Columns.Add(objColumn)

                'Jul
                objColumn = New BoundField
                objColumn.HeaderText = "Jul"
                objColumn.DataField = "Jul"
                grdImport.Columns.Add(objColumn)

                'Aug
                objColumn = New BoundField
                objColumn.HeaderText = "Aug"
                objColumn.DataField = "Aug"
                grdImport.Columns.Add(objColumn)

                'Sep
                objColumn = New BoundField
                objColumn.HeaderText = "Sep"
                objColumn.DataField = "Sep"
                grdImport.Columns.Add(objColumn)

                'Oct
                objColumn = New BoundField
                objColumn.HeaderText = "Oct"
                objColumn.DataField = "Oct"
                grdImport.Columns.Add(objColumn)

                'Nov
                objColumn = New BoundField
                objColumn.HeaderText = "Nov"
                objColumn.DataField = "Nov"
                grdImport.Columns.Add(objColumn)

                'Dec
                objColumn = New BoundField
                objColumn.HeaderText = "Dec"
                objColumn.DataField = "Dec"
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
                Dim objDT As DataTable = TrackerCollection.SelectTrackerTypesByTracker(SessionManager.SelectedValueTrackerID)

                sbExcel.Append("<table cellspacing='0' rules='all' border='1' id='grdReportSummary' style='width:100%;border-collapse:collapse;'>")
                sbExcel.Append("<tr style='color:White;background-color:DarkBlue;font-weight:bold;'>")
                For Each col As BoundField In dg.Columns
                    If col.HeaderText.Trim <> "" Then
                        sbExcel.Append("<td>" & col.HeaderText & "</td>")
                    End If
                Next
                sbExcel.Append("</tr>")
                sbExcel.Append("<tr><td>Value</td></tr>")
                sbExcel.Append("<tr><td>Historic</td></tr>")
                sbExcel.Append("<tr><td>Historic Short</td></tr>")
                sbExcel.Append("<tr><td>Target</td></tr>")

                If objDT IsNot Nothing Then
                    For Each dtRow As DataRow In objDT.Rows
                        sbExcel.Append("<tr><td>" & dtRow("TrackerType").ToString.Trim & ":" & dtRow("SavingsType").ToString.Trim & "</td></tr>")
                    Next
                End If
                sbExcel.Append("</table>")
                HTMLData.Text = sbExcel.ToString
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InitializeExcelFromGridView", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Function ValidateTypeColumn(ByVal colindex As Int16, ByVal tblTypes As DataTable) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, colindex)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim strError As String = ""
                Dim bError As Boolean = False
                Dim strType As String()

                'Setup the cells
                'SetupCells(colindex, 4)

                If Not cells(2, colindex).Text.ToString.Trim.ToUpper = "VALUE" Then
                    If strError.Trim.Length > 0 Then strError += vbCrLf
                    strError += "Row 1 should be Value: "
                    bError = True
                End If
                If Not cells(3, colindex).Text.ToString.Trim.ToUpper = "HISTORIC" Then
                    If strError.Trim.Length > 0 Then strError += vbCrLf
                    strError += "Row 2 should be Historic: "
                    bError = True
                End If
                If Not cells(5, colindex).Text.ToString.Trim.ToUpper = "TARGET" Then
                    If strError.Trim.Length > 0 Then strError += vbCrLf
                    strError += "Row 3 should be Target: "
                    bError = True
                End If

                If tblTypes IsNot Nothing AndAlso tblTypes.Rows.Count > 0 Then
                    Dim iRowIndex As Integer = 6
                    Dim dtView As DataView = tblTypes.DefaultView()
                    Do
                        strType = cells(iRowIndex, colindex).Text.ToString.Split(":")
                        If strType.Length = 2 Then
                            dtView.RowFilter = "TrackerType = '" & strType(0).Trim & "' AND SavingsType = '" & strType(1).Trim & "'"
                            If dtView.Count = 0 Then
                                If strError.Trim.Length > 0 Then strError += vbCrLf
                                strError += cells(iRowIndex, colindex).Text & " - Invalid Savings Type: "
                                bError = True
                            End If
                        Else
                            If strError.Trim.Length > 0 Then strError += vbCrLf
                            strError += cells(iRowIndex, colindex).Text & " - Invalid Savings Type: "
                            bError = True
                        End If

                        iRowIndex += 1
                    Loop Until cells(iRowIndex, colindex).Text = ""
                End If

                If bError Then
                    Master.DisplayError(strError)
                End If

                Return bError
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - ValidateTypeColumn", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Function
        Private Function ValidateColumn(ByVal colindex As Int16, ByVal tblTypes As DataTable) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, colindex)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim strError As String = ""
                Dim bError As Boolean = False
                Dim strType As String()

                Dim objdt As DataTable = SavingsTracker.SelectSavingsTrackerValuesList(SessionManager.SelectedValueTrackerID, Convert.ToInt16(txtYear.Text))
                If objdt.Rows(0)(colindex + 3).ToString.Trim.Length > 0 Then
                    strError = cells(1, colindex).Text & " already has data entered"
                    bError = True
                End If

                If Not bError Then
                    If Not IsNumeric(cells(2, colindex).Text) AndAlso cells(2, colindex).Text.ToString.Trim.Length > 0 Then
                        strError = "Value must be numeric"
                        bError = True
                    End If
                End If
                If Not bError Then
                    If Not IsNumeric(cells(3, colindex).Text) AndAlso cells(3, colindex).Text.ToString.Trim.Length > 0 Then
                        strError = "Historic must be numeric"
                        bError = True
                    End If
                End If
                If Not bError Then
                    If Not IsNumeric(cells(4, colindex).Text) AndAlso cells(4, colindex).Text.ToString.Trim.Length > 0 Then
                        strError = "Historic Short must be numeric"
                        bError = True
                    End If
                End If
                If Not bError Then
                    If Not IsNumeric(cells(5, colindex).Text) AndAlso cells(5, colindex).Text.ToString.Trim.Length > 0 Then
                        strError = "Target must be numeric"
                        bError = True
                    End If
                End If

                If tblTypes IsNot Nothing AndAlso tblTypes.Rows.Count > 0 Then
                    Dim iRowIndex As Integer = 6
                    Dim dtView As DataView = tblTypes.DefaultView()

                    Do While cells(iRowIndex, 1).Text <> ""
                        strType = cells(iRowIndex, 1).Text.ToString.Split(":")
                        dtView.RowFilter = "TrackerType = '" & strType(0).Trim & "' AND SavingsType = '" & strType(1).Trim & "'"
                        If dtView.Count = 0 Then
                            If strError.Trim.Length > 0 Then strError += vbCrLf

                            strError += cells(iRowIndex, 1).Text & " - Invalid Savings Type"
                            bError = True

                            Exit Do
                        End If

                        If Not IsNumeric(cells(iRowIndex + 1, colindex).Text) AndAlso cells(iRowIndex + 1, colindex).Text.ToString.Trim.Length > 0 Then
                            If strError.Trim.Length > 0 Then strError += vbCrLf

                            strError += cells(iRowIndex, 1).Text & " must be numeric"
                            bError = True

                            Exit Do
                        End If

                        iRowIndex += 1
                    Loop
                End If

                If bError Then
                    Master.DisplayError(strError)
                End If

                Return bError
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - ValidateColumn", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Function
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
            Dim bError As Boolean = False

            Try
                For Each col As DataControlField In grdImport.Columns
                    If TypeOf col Is BoundField Then
                        colindex = colindex + 1
                        Select Case colindex
                            Case Else
                                dr(CType(col, BoundField).DataField) = cells(rowindex, colindex).Text
                        End Select
                    End If
                Next

                Return bError
            Catch Exc As Exception
                Return False
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
                'Validate year first
                If Not IsNumeric(txtYear.Text) Then
                    Master.DisplayError("Enter year")
                    txtYear.Focus()

                    Return
                Else
                    If Convert.ToInt16(txtYear.Text) < 2000 OrElse Convert.ToInt16(txtYear.Text) > 2100 Then
                        Master.DisplayError("Invalid year entered")
                        txtYear.Focus()

                        Return
                    End If
                End If

                Dim iYear As Integer = Convert.ToInt16(txtYear.Text)
                Dim objExcel As New Owc11.Spreadsheet
                Dim dt As New DataTable
                SetupDataTable(dt, grdImport)

                objExcel.DataType = "HTMLData"
                objExcel.HTMLData = HTMLData.Text

                objExcel.Cells(1, 1).Select()
                cells = objExcel.Selection.Cells

                'get datatable with Savings Types
                Dim objDT As DataTable = TrackerCollection.SelectTrackerTypesByTracker(SessionManager.SelectedValueTrackerID)

                If ValidateTypeColumn(1, objDT) Then
                    Return
                End If

                Dim colIndex As Integer = 2
                Dim dr As DataRow

                Do
                    If ValidateColumn(colIndex, objDT) Then
                        Return
                    End If

                    colIndex = colIndex + 1
                Loop Until cells(colIndex, 1).Text = ""

                For iRowIndex As Integer = 2 To colIndex
                    dr = dt.NewRow
                    If PopulateDataRow(iRowIndex, dr) Then
                        Return
                    End If

                    dt.Rows.Add(dr)
                Next

                'if we get here then there were NO errors
                lblYear.Text = txtYear.Text

                grdImport.DataSource = dt
                grdImport.DataBind()
                pnlImport.Visible = True
                pnlSpreadsheet.Visible = False

                HTMLData.Text = objExcel.HTMLData
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - Import", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

    End Class
End Namespace
