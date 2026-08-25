#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports System.IO
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class TrackerPlanMaster1
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Master Plan Maintenance"
        Private Shared ReadOnly ProgramName As String = "TrackerPlanMaster1"
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
                chkShowInactive.Text = GetTranslationString("showinactive", chkShowInactive.Text)
                chkShowPlan.Text = GetTranslationString("showplan", chkShowPlan.Text)
                btnExit.Text = GetTranslationString("exit", btnExit.Text)
                btnAdd.Text = GetTranslationString("newsavingsplan", btnAdd.Text)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadCultureTranslations", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
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

            Master.IconImage = Request.ApplicationPath & "/images/boss.gif"
            Master.HeaderMessage = FormName
            Master.ProgramName = ProgramName
            LoadCultureTranslations()

            Master.AddBodyAttribute("onkeydown", "TrapEscKey(document.getElementById('" + btnExit.UniqueID + "'),window.event)")

            If SessionManager.WorkingSiteID = 0 Then
                btnAdd.Visible = False
            End If

            If SessionManager.TrackerSelNavYear = 0 Then
                SessionManager.TrackerSelNavYear = Now.Year
            End If

            BindGrid()
            BindSiteTotalsGrid()
        End Sub
        Protected Sub btnAdd_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnAdd.Click
            SessionManager.TrackerPlanMode = "AddRow"

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TrackerPlanMaster2"), False)
        End Sub
        Protected Sub btnExit_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnExit.Click
            If SessionManager.MasterControlExitProgram.Trim.Length > 0 Then
                Dim strProgram As String = SessionManager.MasterControlExitProgram
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.MasterControlExitProgram)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strProgram), False)
            Else
                RemoveCurrentProgramandGoBack()
            End If
        End Sub
        Private Sub Button_Click(ByVal sender As System.Object, ByVal e As WebControls.CommandEventArgs)
            Dim strTarget() As String
            strTarget = (CType(sender, LinkButton).ID).ToString.Split("~")
            Dim strProgram As String = ""

            Select Case strTarget(0).ToUpper
                Case "PLAN"
                    SessionManager.CallingProgram = "TrackerPlanMaster1"
                    SessionManager.SelectedValueTrackerPlanID = strTarget(1)
                    LastPixelPositionUpdate(ProgramName, Master.CurrentPixelPosition)
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TrackerPlanSavings1"), False)

                    Return
                Case "NAV"
                    SessionManager.TrackerSelNavYear = strTarget(1)

                    BindGrid()
                    BindSiteTotalsGrid()
            End Select

        End Sub
#End Region

#Region " Custom Methods"
        Private Sub BindGrid()
            tblMasterPlan.Rows.Clear()

            Dim objDT As DataTable = TrackerPlanMaster.SelectTrackerPlanMasterSavings(SessionManager.WorkingSiteID, SessionManager.TrackerSelNavYear, chkShowInactive.Checked, chkShowPlan.Checked)
            If objDT Is Nothing OrElse objDT.Rows.Count = 0 Then
                Return
            End If

            Dim objRow As TableRow
            Dim objCell As TableCell
            Dim lnkValue As LinkButton = Nothing

            'add top for year and nav buttons
            objRow = New TableRow
            objRow.Cells.Add(GenerateTableCell("", New Unit((4).ToString & "%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.None, "", GenerateTableLink("<", "#E7E7FF", "Nav~" & (SessionManager.TrackerSelNavYear - 1).ToString, "Previous Year")))
            objRow.Cells.Add(GenerateTableCell(SessionManager.TrackerSelNavYear.ToString, New Unit((0).ToString & "%"), New Unit(0), "#41519A", "#ffffff", HorizontalAlign.Center, VerticalAlign.NotSet, 19, BorderStyle.None, ""))
            objRow.Cells.Add(GenerateTableCell("", New Unit((14).ToString & "%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.None, "", GenerateTableLink(">", "#E7E7FF", "Nav~" & (SessionManager.TrackerSelNavYear + 1).ToString, "Next Year")))
            tblMasterPlan.Rows.Add(objRow)

            'add Month columns
            'add header columns
            objRow = New TableRow

            objRow.Cells.Add(GenerateTableCell("Site", New Unit("4%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("PIL", New Unit("4%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("BA", New Unit("4%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("BU", New Unit("4%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("CAT", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Active", New Unit("4%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Center, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Previous", New Unit("6%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))

            objRow.Cells.Add(GenerateTableCell("Jan", New Unit("4%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Feb", New Unit("4%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Mar", New Unit("4%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Apr", New Unit("4%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("May", New Unit("4%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Jun", New Unit("4%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Jul", New Unit("4%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Aug", New Unit("4%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Sep", New Unit("4%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Oct", New Unit("4%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Nov", New Unit("4%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Dec", New Unit("4%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))

            objRow.Cells.Add(GenerateTableCell("Current", New Unit("6%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))

            objRow.Cells.Add(GenerateTableCell("", New Unit("14%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Center, VerticalAlign.Top, 1, BorderStyle.Solid, ""))

            tblMasterPlan.Rows.Add(objRow)

            Dim intRowIndex As Int16 = 0
            Dim strAlternatingRowColor As String
            Dim bFormulaDif As Boolean = False
            Dim bAllNull As Boolean = True
            Dim objCheck As CheckBox = Nothing

            For Each dtRow As DataRow In objDT.Rows
                intRowIndex += 1
                'values for this year
                objRow = New TableRow

                'alternating row color code
                If intRowIndex Mod 2 = 0 Then
                    strAlternatingRowColor = "#E7E7E7"
                Else
                    strAlternatingRowColor = "#f5f5f5"
                End If

                objRow.Cells.Add(GenerateTableCell(dtRow("SiteAbbrev").ToString, New Unit("4%"), New Unit(15), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.Middle, 1, BorderStyle.Solid, ""))
                objRow.Cells.Add(GenerateTableCell(dtRow("PillarAbbrev").ToString, New Unit("4%"), New Unit(15), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.Middle, 1, BorderStyle.Solid, ""))
                objRow.Cells.Add(GenerateTableCell(dtRow("BusinessAreaAbbrev").ToString, New Unit("4%"), New Unit(15), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.Middle, 1, BorderStyle.Solid, ""))
                objRow.Cells.Add(GenerateTableCell(dtRow("BusinessUnitAbbrev").ToString, New Unit("4%"), New Unit(15), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.Middle, 1, BorderStyle.Solid, ""))
                objRow.Cells.Add(GenerateTableCell(dtRow("SavingsCategory").ToString, New Unit("5%"), New Unit(15), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.Middle, 1, BorderStyle.Solid, ""))

                objCell = New TableCell
                objCell.Width = New Unit("4%")
                objCell.Height = New Unit(15)
                objCell.HorizontalAlign = HorizontalAlign.Center
                objCell.VerticalAlign = VerticalAlign.Middle
                objCell.BackColor = System.Drawing.ColorTranslator.FromHtml(strAlternatingRowColor)
                objCell.BorderStyle = BorderStyle.Solid
                objCheck = New CheckBox
                objCheck.Enabled = False
                objCheck.Checked = Convert.ToBoolean(dtRow("Active"))
                objCell.Controls.Add(objCheck)
                objRow.Cells.Add(objCell)

                If IsNumeric(dtRow("PreviousYearPlan").ToString) Then
                    objRow.Cells.Add(GenerateTableCell(CDbl(dtRow("PreviousYearPlan")).ToString("0.##"), New Unit("6%"), New Unit(15), strAlternatingRowColor, "#000000", HorizontalAlign.Right, VerticalAlign.Middle, 1, BorderStyle.Solid, ""))
                Else
                    objRow.Cells.Add(GenerateTableCell("", New Unit("6%"), New Unit(15), strAlternatingRowColor, "#000000", HorizontalAlign.Right, VerticalAlign.Middle, 1, BorderStyle.Solid, ""))
                End If

                ' Month Values
                For i As Integer = 9 To 20
                    objCell = New TableCell
                    objCell.Width = New Unit("4%")
                    objCell.Height = New Unit(15)
                    objCell.HorizontalAlign = HorizontalAlign.Right
                    If intRowIndex Mod 2 = 0 Then
                        objCell.BackColor = System.Drawing.ColorTranslator.FromHtml("#E7E7E7")
                    Else
                        objCell.BackColor = System.Drawing.ColorTranslator.FromHtml("#f5f5f5")
                    End If

                    objCell.BorderStyle = BorderStyle.Solid
                    If IsNumeric(dtRow(i).ToString) Then
                        objCell.Text = CDbl(dtRow(i)).ToString("0.##")
                    End If

                    objRow.Cells.Add(objCell)
                Next

                If IsNumeric(dtRow("CurrentYearPlan").ToString) Then
                    objRow.Cells.Add(GenerateTableCell(CDbl(dtRow("CurrentYearPlan")).ToString("0.##"), New Unit("6%"), New Unit(15), strAlternatingRowColor, "#000000", HorizontalAlign.Right, VerticalAlign.Middle, 1, BorderStyle.Solid, ""))
                Else
                    objRow.Cells.Add(GenerateTableCell("", New Unit("6%"), New Unit(15), strAlternatingRowColor, "#000000", HorizontalAlign.Right, VerticalAlign.Middle, 1, BorderStyle.Solid, ""))
                End If

                ' Savings Plan Link
                lnkValue = GenerateTableLink("Savings Plan", "#3333FF", "Plan~" & dtRow("TrackerPlanID").ToString, "Savings Plan")
                objRow.Cells.Add(GenerateTableCell("Savings Plan", New Unit("14%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Center, VerticalAlign.Middle, 1, BorderStyle.Solid, "", lnkValue))

                tblMasterPlan.Rows.Add(objRow)
            Next
        End Sub
        Private Sub BindSiteTotalsGrid()
            tblSiteTotals.Rows.Clear()

            Dim iSiteID As Integer = SessionManager.WorkingSiteID

            Dim objDT As DataTable = TrackerPlanSavings.SelectTrackerPlanSavingsTotalsBySite(iSiteID, SessionManager.TrackerSelNavYear, 0)
            Dim objRow As TableRow
            Dim objCell As TableCell
            Dim lnkValue As LinkButton = Nothing

            If objDT Is Nothing OrElse objDT.Rows.Count = 0 Then
                objRow = New TableRow
                objRow.Cells.Add(GenerateTableCell("No Records Exist", New Unit("100%"), New Unit(15), "#FFFFFF", "Red", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.None, "No Records"))
                tblSiteTotals.Rows.Add(objRow)

                Return
            End If

            'add Month columns
            'add header columns
            objRow = New TableRow
            objRow.Cells.Add(GenerateTableCell("", New Unit("14%"), New Unit(15), "#41519A", "#FFFFFF", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.Solid, ""))

            objRow.Cells.Add(GenerateTableCell("Prev", New Unit("4%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Jan", New Unit("4%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Feb", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Mar", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Apr", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("May", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Jun", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Jul", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Aug", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Sep", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Aug", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Nov", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Dec", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Cur", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))

            tblSiteTotals.Rows.Add(objRow)

            Dim strCatDisplay As String = ""
            Dim strCategoryDisplayName As String = ""
            Dim strAlternatingRowColor As String = ""
            Dim strIndent As String = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"

            For Each dtRow As DataRow In objDT.Rows
                'values for this year
                objRow = New TableRow

                strCatDisplay = dtRow("SiteAbbrev").ToString.Trim

                If strCategoryDisplayName <> strCatDisplay Then
                    tblSiteTotals.Rows.Add(GenerateTableRow(strIndent & strCatDisplay, "#FFFFFF", "#000000", HorizontalAlign.Left, BorderStyle.None, 15, True))
                    strCategoryDisplayName = strCatDisplay
                End If

                Select Case Convert.ToInt16(dtRow("RowType"))
                    Case 1
                        strAlternatingRowColor = "#FFFFFF"
                        objRow.Cells.Add(GenerateTableCell("Savings", New Unit("14%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                    Case 2
                        strAlternatingRowColor = "#CCCCCC"
                        objRow.Cells.Add(GenerateTableCell("Target", New Unit("14%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                    Case 3
                        strAlternatingRowColor = "#CCCCCC"
                        objRow.Cells.Add(GenerateTableCell("Projected", New Unit("14%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                    Case 4
                        strAlternatingRowColor = "#CCCCCC"
                        objRow.Cells.Add(GenerateTableCell("Phantom", New Unit("14%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                    Case 5
                        strAlternatingRowColor = "#CCCCCC"
                        objRow.Cells.Add(GenerateTableCell("Plan", New Unit("14%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                    Case 6
                        strAlternatingRowColor = "#CCCCCC"
                        objRow.Cells.Add(GenerateTableCell("Stretch", New Unit("14%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                End Select

                ' Previous year
                objCell = New TableCell
                objCell.Width = New Unit("4%")
                objCell.Height = New Unit(15)
                objCell.HorizontalAlign = HorizontalAlign.Right
                objCell.BackColor = System.Drawing.ColorTranslator.FromHtml(strAlternatingRowColor)
                objCell.BorderStyle = BorderStyle.Solid
                If Not dtRow("Prev") Is DBNull.Value AndAlso IsNumeric(dtRow("Prev")) Then
                    objCell.Text = Math.Round(CDbl(dtRow("Prev")), 0).ToString("0")
                End If
                objRow.Cells.Add(objCell)

                For i As Integer = 4 To 15
                    objCell = New TableCell
                    objCell.Width = New Unit("4%")
                    objCell.Height = New Unit(15)
                    objCell.HorizontalAlign = HorizontalAlign.Right
                    objCell.BackColor = System.Drawing.ColorTranslator.FromHtml(strAlternatingRowColor)
                    objCell.BorderStyle = BorderStyle.Solid
                    If Not dtRow(i) Is DBNull.Value AndAlso IsNumeric(dtRow(i)) Then
                        objCell.Text = Math.Round(CDbl(dtRow(i)), 0).ToString("0")
                    End If

                    objRow.Cells.Add(objCell)
                Next

                ' Current year
                objCell = New TableCell
                objCell.Width = New Unit("4%")
                objCell.Height = New Unit(15)
                objCell.HorizontalAlign = HorizontalAlign.Right
                objCell.BackColor = System.Drawing.ColorTranslator.FromHtml(strAlternatingRowColor)
                objCell.BorderStyle = BorderStyle.Solid
                If Not dtRow("Cur") Is DBNull.Value AndAlso IsNumeric(dtRow("Cur")) Then
                    objCell.Text = Math.Round(CDbl(dtRow("Cur")), 0).ToString("0")
                End If
                objRow.Cells.Add(objCell)

                tblSiteTotals.Rows.Add(objRow)
            Next
        End Sub
        Private Function GenerateTableCell(ByVal strText As String, ByVal strCellWidth As Unit, ByVal intCellHeight As Unit, ByVal strBackColor As String, ByVal strForeColor As String, ByVal intHorizontalCellAlign As Integer, ByVal intVerticalCellAlign As Integer, ByVal intColSpan As Integer, ByVal intBorderStyle As Integer, ByVal strToolTip As String, Optional ByVal objLink As LinkButton = Nothing) As TableCell
            Dim objCell = New TableCell
            objCell.HorizontalAlign = intHorizontalCellAlign
            objCell.VerticalAlign = intVerticalCellAlign
            objCell.Width = strCellWidth
            objCell.Height = intCellHeight
            objCell.BackColor = System.Drawing.ColorTranslator.FromHtml(strBackColor)
            objCell.ForeColor = System.Drawing.ColorTranslator.FromHtml(strForeColor)
            objCell.ColumnSpan = intColSpan
            objCell.Text = strText
            objCell.BorderStyle = intBorderStyle
            objCell.ToolTip = strToolTip

            If objLink IsNot Nothing Then
                objCell.Controls.Add(objLink)
            End If

            Return objCell
        End Function
        Private Function GenerateTableLink(ByVal strText As String, ByVal strForeColor As String, ByVal strElementID As String, ByVal strToolTip As String) As LinkButton
            Dim objLink As New LinkButton
            AddHandler objLink.Command, AddressOf Button_Click
            objLink.Text = strText
            objLink.ID = strElementID
            objLink.ToolTip = strToolTip
            objLink.ForeColor = System.Drawing.ColorTranslator.FromHtml(strForeColor)

            Return objLink
        End Function
        Private Function GenerateTableRow(ByVal strText As String, ByVal strBackColor As String, ByVal strForeColor As String, ByVal intHorizontalAlign As Integer, ByVal intBorderStyle As Integer, ByVal intColSpan As Integer, ByVal blnBold As Boolean) As TableRow
            Try
                Dim objRow As New TableRow
                Dim objCell As New TableCell
                objCell.ColumnSpan = intColSpan
                objCell.BackColor = System.Drawing.ColorTranslator.FromHtml(strBackColor)
                objCell.ForeColor = System.Drawing.ColorTranslator.FromHtml(strForeColor)
                objCell.Text = strText
                objCell.BorderStyle = intBorderStyle
                If blnBold Then
                    objCell.Font.Bold = True
                End If
                objCell.HorizontalAlign = intHorizontalAlign
                objRow.Cells.Add(objCell)

                Return objRow
            Catch Exc As Exception
                Throw
            End Try
        End Function
#End Region

    End Class
End Namespace
