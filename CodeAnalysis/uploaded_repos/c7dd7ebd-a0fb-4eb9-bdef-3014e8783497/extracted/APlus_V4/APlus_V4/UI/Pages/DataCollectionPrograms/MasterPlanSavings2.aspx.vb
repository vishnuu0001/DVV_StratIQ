#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class MasterPlanSavings2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Master Plan Savings"
        Private Shared ReadOnly ProgramName As String = "MasterPlanSavings2"
        Private bEnglish As Boolean = True
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
                chkProjected.Text = GetTranslationString("showprojected", chkProjected.Text)
                btnApplyFilter.Text = GetTranslationString("applyfilter", btnApplyFilter.Text)
                btnExit.Text = GetTranslationString("exit", btnExit.Text)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadCultureTranslations", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnExit}
            Dim OverMessageArr() As String = {"Exit"}
            Dim OutMessageArr() As String = {""}

            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnExit.UniqueID + "'),window.event)")
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

            Master.IconImage = Request.ApplicationPath & "/images/TeamAction.gif"
            Master.HeaderMessage = GetTranslationString(FormName, FormName)
            Master.ProgramName = ProgramName

            LoadCommonJavaScripts()

            If SessionManager.WorkingSiteID = 0 AndAlso SessionManager.TrackerSelSiteID = 0 Then
                RemoveCurrentProgramandGoBack()
            End If

            If SessionManager.TrackerSelNavYear = 0 Then
                SessionManager.TrackerSelNavYear = Now.Year
            End If

            If Not Page.IsPostBack Then
                chkProjected.Checked = SessionManager.ShowProjected

                LoadCultureTranslations()
            Else
                If Request.Item("__EVENTTARGET").ToString.Contains("PageLink") Then
                    ButtonClick(Request.Item("__EVENTTARGET"))
                End If
            End If
        End Sub
        Protected Sub Timer1_Tick(ByVal sender As Object, ByVal e As System.EventArgs) Handles Timer1.Tick
            Timer1.Enabled = False
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            BindSiteTotalsGrid()
            BindGrid()
            BindTeamGrid()
        End Sub
        Protected Sub btnApplyFilter_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnApplyFilter.Click
            SessionManager.ShowProjected = chkProjected.Checked

            BindSiteTotalsGrid()
            BindGrid()
            BindTeamGrid()
        End Sub
        Private Sub ButtonClick(ByVal passArgs As String)
            Dim strTarget() As String
            strTarget = passArgs.Split("~")
            Dim strProgram As String = ""

            Select Case strTarget(1)
                Case "Nav"
                    SessionManager.TrackerSelNavYear = strTarget(2)

                    BindSiteTotalsGrid()
                    BindGrid()
                    BindTeamGrid()
                Case "Tracker"
                    SessionManager.SelectedValueTrackerID = strTarget(2)
                    SessionManager.CallingProgram = "MasterPlanSavings2"
                    strProgram = "SavingsTracker1"
                    LastPixelPositionUpdate(ProgramName, Master.CurrentPixelPosition)

                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strProgram), False)

                    Return
                Case "Team"
                    If strTarget(2) <> SessionManager.SelectedTeamID.ToString Then
                        PushTeamOntoStack(SessionManager.SelectedTeamID, SessionManager.SelectedTeam, SessionManager.SelectedOPI, "MasterPlanSavings2", SessionManager.CurrentMenuProgram)
                        SessionManager.SelectedTeamID = strTarget(2)
                        SessionManager.SelectedTeam = strTarget(3)
                        If bEnglish Then
                            SessionManager.SelectedTeamName = Teams.GetTeamNameOther(SessionManager.SelectedTeamID)
                        Else
                            SessionManager.SelectedTeamName = Teams.GetTeamName(SessionManager.SelectedTeamID)
                        End If
                        SessionManager.SelectedOPI = ""
                        SessionManager.SelectedTeamAllowEdit = UserSiteMaster.SelectTeamAllowEdit(SessionManager.SelectedTeamID, SessionManager.UserID)
                    End If

                    SessionManager.CallingProgram = "MasterPlanSavings2"
                    strProgram = "TeamBoardMenu"
                    LastPixelPositionUpdate(ProgramName, Master.CurrentPixelPosition)

                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strProgram), False)

                    Return
            End Select
        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("MasterPlanSavings1"), False)
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub BindSiteTotalsGrid()
            tblSiteTotals.Rows.Clear()

            Dim iSiteID As Integer = 0
            If SessionManager.TrackerSelSiteID > 0 Then
                iSiteID = SessionManager.TrackerSelSiteID
            Else
                iSiteID = SessionManager.WorkingSiteID
            End If

            Dim objDT As DataTable = TrackerPlanSavings.SelectTrackerPlanSavingsTotalsYTDBySite(iSiteID, SessionManager.TrackerSelNavYear, SessionManager.SelectedValueTrackerPlanID, chkProjected.Checked)
            Dim objRow As TableRow
            Dim objCell As TableCell
            Dim lnkValue As LinkButton = Nothing

            If objDT Is Nothing OrElse objDT.Rows.Count = 0 Then
                objRow = New TableRow
                objRow.Cells.Add(GenerateTableCell("No Records Exist", New Unit("100%"), New Unit(15), "#FFFFFF", "Red", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.None, "No Records"))
                tblSiteTotals.Rows.Add(objRow)

                Return
            End If

            'add top for year and nav buttons
            objRow = New TableRow
            objRow.Cells.Add(GenerateTableCell("", New Unit("7%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.None, "", GenerateTableLink("<", "#E7E7FF", "Nav~" & (SessionManager.TrackerSelNavYear - 1).ToString, "Previous Year")))
            objRow.Cells.Add(GenerateTableCell(SessionManager.TrackerSelNavYear.ToString, New Unit("86%"), New Unit(0), "#41519A", "#ffffff", HorizontalAlign.Center, VerticalAlign.NotSet, 14, BorderStyle.None, ""))
            objRow.Cells.Add(GenerateTableCell("", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 2, BorderStyle.None, "", GenerateTableLink(">", "#E7E7FF", "Nav~" & (SessionManager.TrackerSelNavYear + 1).ToString, "Next Year")))
            tblSiteTotals.Rows.Add(objRow)

            'add Month columns
            'add header columns
            objRow = New TableRow
            objRow.Cells.Add(GenerateTableCell("", New Unit("7%"), New Unit(15), "#41519A", "#FFFFFF", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("", New Unit("30%"), New Unit(15), "#41519A", "#FFFFFF", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.Solid, ""))

            objRow.Cells.Add(GenerateTableCell("Previous", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
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
            objRow.Cells.Add(GenerateTableCell("YTD", New Unit("4%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Current", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))

            tblSiteTotals.Rows.Add(objRow)

            Dim strCatDisplay As String = ""
            Dim strCategoryDisplayName As String = ""
            Dim intRowIndex As Integer = 0
            Dim iRowType As Integer = 0
            Dim strAlternatingRowColor As String = ""
            Dim strTrackingPlan As String = ""

            For Each dtRow As DataRow In objDT.Rows
                iRowType += 1
                'values for this year
                objRow = New TableRow

                strCatDisplay = dtRow("SiteAbbrev").ToString.Trim

                If strCategoryDisplayName <> strCatDisplay Then
                    tblSiteTotals.Rows.Add(GenerateTableRow("", "#FFFFFF", "#000000", HorizontalAlign.Left, BorderStyle.None, 15, True))
                    strCategoryDisplayName = strCatDisplay
                    iRowType = 1
                End If

                Select Case Convert.ToInt16(dtRow("RowType"))
                    Case 1
                        strAlternatingRowColor = "#FFFFFF"
                        objRow.Cells.Add(GenerateTableCell("Savings", New Unit("7%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                        objRow.Cells.Add(GenerateTableCell(TrackerPlanMaster.SelectTrackerPlanHeader(iSiteID, SessionManager.SelectedValueTrackerPlanID), New Unit("31%"), New Unit(15), strAlternatingRowColor, "#000000", HorizontalAlign.Center, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
                    Case 2
                        strAlternatingRowColor = "#CCCCCC"
                        objRow.Cells.Add(GenerateTableCell("Target", New Unit("7%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                        objRow.Cells.Add(GenerateTableCell("", New Unit("31%"), New Unit(15), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
                    Case 3
                        strAlternatingRowColor = "#CCCCCC"
                        objRow.Cells.Add(GenerateTableCell("Projected", New Unit("7%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                        objRow.Cells.Add(GenerateTableCell("", New Unit("31%"), New Unit(15), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
                    Case 4
                        strAlternatingRowColor = "#CCCCCC"
                        objRow.Cells.Add(GenerateTableCell("Phantom", New Unit("7%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                        objRow.Cells.Add(GenerateTableCell("", New Unit("31%"), New Unit(15), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
                    Case 5
                        strAlternatingRowColor = "#CCCCCC"
                        objRow.Cells.Add(GenerateTableCell("Plan", New Unit("7%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                        objRow.Cells.Add(GenerateTableCell("", New Unit("31%"), New Unit(15), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
                    Case 6
                        strAlternatingRowColor = "#CCCCCC"
                        objRow.Cells.Add(GenerateTableCell("Stretch", New Unit("7%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                        objRow.Cells.Add(GenerateTableCell("", New Unit("31%"), New Unit(15), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
                End Select

                ' Previous year
                objCell = New TableCell
                objCell.Width = New Unit("5%")
                objCell.Height = New Unit(15)
                objCell.HorizontalAlign = HorizontalAlign.Right
                objCell.BackColor = System.Drawing.ColorTranslator.FromHtml(strAlternatingRowColor)
                objCell.BorderStyle = BorderStyle.Solid
                If Not dtRow("Prev") Is DBNull.Value AndAlso IsNumeric(dtRow("Prev")) Then
                    objCell.Text = Math.Round(CDbl(dtRow("Prev")), 0).ToString("0")
                End If
                objRow.Cells.Add(objCell)

                For i As Integer = 4 To 16
                    objCell = New TableCell
                    objCell.Width = New Unit("4%")
                    objCell.Height = New Unit(15)
                    objCell.HorizontalAlign = HorizontalAlign.Right
                    objCell.BackColor = System.Drawing.ColorTranslator.FromHtml(strAlternatingRowColor)
                    objCell.BorderStyle = BorderStyle.Solid
                    If Not dtRow(i) Is DBNull.Value AndAlso IsNumeric(dtRow(i)) Then
                        objCell.Text = Math.Round(CDbl(dtRow(i)), 0).ToString("0")

                        If iRowType = 1 Then
                            If (objDT.Rows(intRowIndex + 1)(i) IsNot DBNull.Value AndAlso IsNumeric(objDT.Rows(intRowIndex + 1)(i))) AndAlso _
                            (objDT.Rows(intRowIndex + 3)(i) IsNot DBNull.Value AndAlso IsNumeric(objDT.Rows(intRowIndex + 3)(i))) Then
                                If Math.Round(CDbl(dtRow(i)), 0) >= Math.Round(CDbl(objDT.Rows(intRowIndex + 3)(i)), 0) Then
                                    objCell.BackColor = Drawing.Color.LightGreen
                                ElseIf Math.Round(CDbl(dtRow(i)), 0) >= Math.Round(CDbl(objDT.Rows(intRowIndex + 1)(i)), 0) Then
                                    objCell.BackColor = Drawing.Color.Yellow
                                Else
                                    objCell.BackColor = Drawing.Color.Salmon
                                End If
                            ElseIf (objDT.Rows(intRowIndex + 3)(i) IsNot DBNull.Value AndAlso IsNumeric(objDT.Rows(intRowIndex + 3)(i))) Then
                                If Math.Round(CDbl(dtRow(i)), 0) >= Math.Round(CDbl(objDT.Rows(intRowIndex + 3)(i)), 0) Then
                                    objCell.BackColor = Drawing.Color.LightGreen
                                Else
                                    objCell.BackColor = Drawing.Color.Salmon
                                End If
                            ElseIf (objDT.Rows(intRowIndex + 1)(i) IsNot DBNull.Value AndAlso IsNumeric(objDT.Rows(intRowIndex + 1)(i))) Then
                                If Math.Round(CDbl(dtRow(i)), 0) >= Math.Round(CDbl(objDT.Rows(intRowIndex + 1)(i)), 0) Then
                                    objCell.BackColor = Drawing.Color.Yellow
                                Else
                                    objCell.BackColor = Drawing.Color.Salmon
                                End If
                            End If
                        End If
                    End If

                    objRow.Cells.Add(objCell)
                Next

                ' Current year
                objCell = New TableCell
                objCell.Width = New Unit("5%")
                objCell.Height = New Unit(15)
                objCell.HorizontalAlign = HorizontalAlign.Right
                objCell.BackColor = System.Drawing.ColorTranslator.FromHtml(strAlternatingRowColor)
                objCell.BorderStyle = BorderStyle.Solid
                If Not dtRow("Cur") Is DBNull.Value AndAlso IsNumeric(dtRow("Cur")) Then
                    objCell.Text = Math.Round(CDbl(dtRow("Cur")), 0).ToString("0")
                End If
                objRow.Cells.Add(objCell)

                tblSiteTotals.Rows.Add(objRow)
                intRowIndex += 1
            Next
        End Sub
        Private Sub BindGrid()
            tblTrackerSavings.Rows.Clear()

            Dim iSiteID As Integer = 0
            If SessionManager.TrackerSelSiteID > 0 Then
                iSiteID = SessionManager.TrackerSelSiteID
            Else
                iSiteID = SessionManager.WorkingSiteID
            End If

            Dim objDT As DataTable = SavingsTracker.SelectTrackerSavingsByTrackerPlan(SessionManager.UserID, iSiteID, SessionManager.TrackerSelNavYear, SessionManager.SelectedValueTrackerPlanID)
            Dim objRow As TableRow
            Dim objCell As TableCell
            Dim lnkValue As LinkButton = Nothing
            Dim lnkTeam As LinkButton = Nothing

            If objDT Is Nothing OrElse objDT.Rows.Count = 0 Then
                objRow = New TableRow
                objRow.Cells.Add(GenerateTableCell("No Records Exist", New Unit("100%"), New Unit(15), "#FFFFFF", "Red", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.None, "No Records"))
                tblTrackerSavings.Rows.Add(objRow)

                Return
            End If

            'add Month columns
            'add header columns
            objRow = New TableRow
            objRow.Cells.Add(GenerateTableCell("", New Unit("7%"), New Unit(15), "#41519A", "#FFFFFF", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("", New Unit("22%"), New Unit(15), "#41519A", "#FFFFFF", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("PIL", New Unit("2%"), New Unit(15), "#41519A", "#FFFFFF", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("BU", New Unit("2%"), New Unit(15), "#41519A", "#FFFFFF", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Start", New Unit("5%"), New Unit(15), "#41519A", "#FFFFFF", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.Solid, ""))

            objRow.Cells.Add(GenerateTableCell("Previous", New Unit("5%"), New Unit(15), "#41519A", "#FFFFFF", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Jan", New Unit("4%"), New Unit(15), "#41519A", "#FFFFFF", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Feb", New Unit("4%"), New Unit(15), "#41519A", "#FFFFFF", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Mar", New Unit("4%"), New Unit(15), "#41519A", "#FFFFFF", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Apr", New Unit("4%"), New Unit(15), "#41519A", "#FFFFFF", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("May", New Unit("4%"), New Unit(15), "#41519A", "#FFFFFF", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Jun", New Unit("4%"), New Unit(15), "#41519A", "#FFFFFF", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Jul", New Unit("4%"), New Unit(15), "#41519A", "#FFFFFF", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Aug", New Unit("4%"), New Unit(15), "#41519A", "#FFFFFF", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Sep", New Unit("4%"), New Unit(15), "#41519A", "#FFFFFF", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Oct", New Unit("4%"), New Unit(15), "#41519A", "#FFFFFF", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Nov", New Unit("4%"), New Unit(15), "#41519A", "#FFFFFF", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Dec", New Unit("4%"), New Unit(15), "#41519A", "#FFFFFF", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("YTD", New Unit("4%"), New Unit(15), "#41519A", "#FFFFFF", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Current", New Unit("5%"), New Unit(15), "#41519A", "#FFFFFF", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))

            tblTrackerSavings.Rows.Add(objRow)

            Dim strCatDisplay As String = ""
            Dim strCategoryDisplayName As String = ""
            Dim intRowIndex As Integer = 0
            Dim strAlternatingRowColor As String = ""
            Dim strIndent As String = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            bEnglish = (New System.Globalization.CultureInfo(SessionManager.CulturePref).TwoLetterISOLanguageName.ToUpper = "EN")
            Dim strCommandArg As String = ""
            Dim strTeamName As String = ""
            Dim strStartPeriod As String = ""
            Dim strTeamPillarAbbrev As String = ""
            Dim strTeamBusinessUnitAbbrev As String = ""
            Dim dtStartDate As DateTime = Nothing
            Dim dtEndDate As DateTime = Nothing
            Dim dtTeamStartDate As DateTime = Nothing
            Dim dtTeamEndDate As DateTime = Nothing
            Dim dtCurMonth As DateTime = Nothing
            Dim bActiveCell As Boolean = False

            For Each dtRow As DataRow In objDT.Rows
                intRowIndex += 1

                'values for this year
                objRow = New TableRow

                If SessionManager.SelectedValueTrackerPlanID = 0 Then
                    strCatDisplay = dtRow("SiteAbbrev").ToString.Trim
                Else
                    strCatDisplay = dtRow("SiteAbbrev").ToString.Trim & ":"
                    strCatDisplay += dtRow("PillarAbbrev").ToString.Trim & ":"
                    strCatDisplay += dtRow("BusinessAreaAbbrev").ToString.Trim & ":"
                    strCatDisplay += dtRow("BusinessUnitAbbrev").ToString.Trim & ":"
                    strCatDisplay += dtRow("SavingsCategory").ToString.Trim
                End If
                strTeamPillarAbbrev = dtRow("TeamPillarAbbrev").ToString.Trim
                strTeamBusinessUnitAbbrev = dtRow("TeamBusinessUnitAbbrev").ToString.Trim

                If strCategoryDisplayName <> strCatDisplay Then
                    tblTrackerSavings.Rows.Add(GenerateTableRow(strIndent & strCatDisplay, "#FFFFFF", "#000000", HorizontalAlign.Left, BorderStyle.None, 17, True))
                    strCategoryDisplayName = strCatDisplay
                End If

                If intRowIndex Mod 2 = 0 Then
                    strAlternatingRowColor = "#CCCCCC"
                    objRow.Cells.Add(GenerateTableCell("", New Unit("7%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                    objRow.Cells.Add(GenerateTableCell("Target", New Unit("22%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                    objRow.Cells.Add(GenerateTableCell("", New Unit("2%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                    objRow.Cells.Add(GenerateTableCell("", New Unit("2%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                    objRow.Cells.Add(GenerateTableCell("", New Unit("5%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                Else
                    strAlternatingRowColor = "#FFFFFF"
                    If IsDate(dtRow("StartPeriod").ToString) Then
                        strStartPeriod = Convert.ToDateTime(dtRow("StartPeriod")).ToString("yyyy/MM/dd")
                    Else
                        strStartPeriod = ""
                    End If

                    If bEnglish Then
                        strTeamName = Teams.GetTeamNameOther(dtRow("TeamID"))
                        lnkValue = GenerateTableLink(dtRow("TrackerOther").ToString, "#3333FF", "Tracker~" & dtRow("TrackerID").ToString, dtRow("Tracker").ToString)
                        lnkTeam = GenerateTableLink(dtRow("Team").ToString, "#3333FF", "Team~" & dtRow("TeamID").ToString & "~" & dtRow("Team").ToString & "~" & dtRow("TrackerID").ToString, strTeamName)
                    Else
                        strTeamName = Teams.GetTeamName(dtRow("TeamID"))
                        lnkValue = GenerateTableLink(dtRow("Tracker").ToString, "#3333FF", "Tracker~" & dtRow("TrackerID").ToString & "~" & dtRow("TrackerID").ToString, dtRow("TrackerOther").ToString)
                        lnkTeam = GenerateTableLink(dtRow("Team").ToString, "#3333FF", "Team~" & dtRow("TeamID").ToString & "~" & dtRow("Team").ToString & "~" & dtRow("TrackerID").ToString, strTeamName)
                    End If

                    If Convert.ToBoolean(dtRow("AllowView")) Then
                        objRow.Cells.Add(GenerateTableCell(dtRow("Team").ToString.Trim, New Unit("7%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, "", lnkTeam))
                    Else
                        objRow.Cells.Add(GenerateTableCell(dtRow("Team").ToString.Trim, New Unit("7%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, strTeamName))
                    End If
                    objRow.Cells.Add(GenerateTableCell("Savings", New Unit("22%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, "", lnkValue))
                    objRow.Cells.Add(GenerateTableCell(strTeamPillarAbbrev, New Unit("2%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                    objRow.Cells.Add(GenerateTableCell(strTeamBusinessUnitAbbrev, New Unit("2%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                    objRow.Cells.Add(GenerateTableCell(strStartPeriod, New Unit("5%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))

                    If IsDate(dtRow("StartPeriod").ToString) Then
                        dtStartDate = Convert.ToDateTime(dtRow("StartPeriod").ToString)
                        dtStartDate = Convert.ToDateTime(dtStartDate.Year.ToString & "/" & dtStartDate.Month.ToString & "/01")
                        dtStartDate = dtStartDate.AddDays(-1)

                        dtEndDate = dtStartDate.AddYears(1).AddDays(1)
                    Else
                        dtStartDate = DateTime.MinValue
                        dtEndDate = DateTime.MaxValue
                    End If

                    If IsDate(dtRow("TeamStartDate").ToString) Then
                        dtTeamStartDate = Convert.ToDateTime(dtRow("TeamStartDate").ToString)
                        dtTeamStartDate = Convert.ToDateTime(dtTeamStartDate.Year.ToString & "/" & dtTeamStartDate.Month.ToString & "/01")
                        dtTeamStartDate = dtTeamStartDate.AddDays(-1)
                    Else
                        dtTeamStartDate = DateTime.MinValue
                    End If
                    If IsDate(dtRow("TeamFinishDate").ToString) Then
                        dtTeamEndDate = Convert.ToDateTime(dtRow("TeamFinishDate").ToString)
                        dtTeamEndDate = Convert.ToDateTime(dtTeamEndDate.Year.ToString & "/" & dtTeamEndDate.Month.ToString & "/01")
                        dtTeamEndDate = dtTeamEndDate.AddMonths(1)
                    Else
                        dtTeamEndDate = DateTime.MaxValue
                    End If
                End If

                ' Previous year
                objCell = New TableCell
                objCell.Width = New Unit("5%")
                objCell.Height = New Unit(15)
                objCell.HorizontalAlign = HorizontalAlign.Right
                objCell.VerticalAlign = VerticalAlign.Top
                objCell.BackColor = System.Drawing.ColorTranslator.FromHtml(strAlternatingRowColor)
                objCell.BorderStyle = BorderStyle.Solid
                If Not dtRow("Prev") Is DBNull.Value AndAlso IsNumeric(dtRow("Prev")) Then
                    objCell.Text = Math.Round(CDbl(dtRow("Prev")), 0).ToString("0")
                End If
                objRow.Cells.Add(objCell)

                Dim bCurYearActive As Boolean = False
                For i As Integer = 18 To 30
                    bActiveCell = False

                    objCell = New TableCell
                    objCell.Width = New Unit("4%")
                    objCell.Height = New Unit(15)
                    objCell.HorizontalAlign = HorizontalAlign.Right
                    objCell.VerticalAlign = VerticalAlign.Top
                    objCell.BorderStyle = BorderStyle.Solid
                    If Not dtRow(i) Is DBNull.Value AndAlso IsNumeric(dtRow(i)) Then
                        objCell.Text = Math.Round(CDbl(dtRow(i)), 0).ToString("0")
                    End If

                    objCell.BackColor = System.Drawing.ColorTranslator.FromHtml(strAlternatingRowColor)
                    If intRowIndex Mod 2 <> 0 AndAlso i < 30 Then
                        dtCurMonth = Convert.ToDateTime(SessionManager.TrackerSelNavYear.ToString & "/" & (i - 17).ToString & "/01")
                        If dtCurMonth > dtStartDate AndAlso dtCurMonth < dtEndDate Then
                            objCell.BackColor = Drawing.Color.LightBlue
                            bActiveCell = True
                            bCurYearActive = True
                        ElseIf dtCurMonth > dtTeamStartDate AndAlso dtCurMonth < dtTeamEndDate Then
                            objCell.BackColor = Drawing.Color.LightYellow
                            bActiveCell = True
                            bCurYearActive = True
                        End If
                    End If

                    If bCurYearActive Then
                        If IsNumeric(dtRow(i).ToString()) AndAlso IsNumeric(objDT.Rows(intRowIndex)(i).ToString()) Then
                            If CDbl(dtRow(i)) < CDbl(objDT.Rows(intRowIndex)(i)) Then
                                objCell.BackColor = Drawing.Color.Salmon
                            Else
                                objCell.BackColor = Drawing.Color.LightGreen
                            End If
                        End If
                    End If

                    objRow.Cells.Add(objCell)
                Next

                ' Current year
                objCell = New TableCell
                objCell.Width = New Unit("5%")
                objCell.Height = New Unit(15)
                objCell.HorizontalAlign = HorizontalAlign.Right
                objCell.VerticalAlign = VerticalAlign.Top
                objCell.BackColor = System.Drawing.ColorTranslator.FromHtml(strAlternatingRowColor)
                objCell.BorderStyle = BorderStyle.Solid
                If Not dtRow("Cur") Is DBNull.Value AndAlso IsNumeric(dtRow("Cur")) Then
                    objCell.Text = Math.Round(CDbl(dtRow("Cur")), 0).ToString("0")
                End If
                objRow.Cells.Add(objCell)

                tblTrackerSavings.Rows.Add(objRow)
            Next
        End Sub
        Private Sub BindTeamGrid()
            tblTeams.Rows.Clear()

            Dim iSiteID As Integer = 0
            If SessionManager.TrackerSelSiteID > 0 Then
                iSiteID = SessionManager.TrackerSelSiteID
            Else
                iSiteID = SessionManager.WorkingSiteID
            End If

            Dim objDT As DataTable = TrackerPlanSavings.SelectTrackerPlanTeams(SessionManager.UserID, iSiteID, SessionManager.SelectedValueTrackerPlanID)
            Dim objRow As TableRow
            Dim objCell As TableCell
            Dim lnkValue As LinkButton = Nothing

            If objDT Is Nothing OrElse objDT.Rows.Count = 0 Then
                objRow = New TableRow
                objRow.Cells.Add(GenerateTableCell("No Records Exist", New Unit("100%"), New Unit(15), "#FFFFFF", "Red", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.None, "No Records"))
                tblTeams.Rows.Add(objRow)

                Return
            End If

            'add Month columns
            'add header columns
            objRow = New TableRow
            objRow.Cells.Add(GenerateTableCell("", New Unit("7%"), New Unit(15), "#41519A", "#FFFFFF", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("", New Unit("22%"), New Unit(15), "#41519A", "#FFFFFF", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("PIL", New Unit("2%"), New Unit(15), "#41519A", "#FFFFFF", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("BU", New Unit("2%"), New Unit(15), "#41519A", "#FFFFFF", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Start", New Unit("5%"), New Unit(15), "#41519A", "#FFFFFF", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.Solid, ""))

            objRow.Cells.Add(GenerateTableCell("", New Unit("7%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
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
            objRow.Cells.Add(GenerateTableCell("", New Unit("7%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))

            tblTeams.Rows.Add(objRow)

            Dim intRowIndex As Integer = 0
            Dim strAlternatingRowColor As String = ""
            Dim strTrackingPlan As String = ""
            Dim dtStartDate As DateTime = Nothing
            Dim dtEndDate As DateTime = Nothing
            Dim dtCurMonth As DateTime = Nothing
            Dim strStartDate As String = ""
            Dim lnkTeam As LinkButton = Nothing

            For Each dtRow As DataRow In objDT.Rows
                intRowIndex += 1
                'values for this year
                objRow = New TableRow

                If IsDate(dtRow("TeamStartDate").ToString) Then
                    dtStartDate = Convert.ToDateTime(dtRow("TeamStartDate").ToString)
                    dtStartDate = Convert.ToDateTime(dtStartDate.Year.ToString & "/" & dtStartDate.Month.ToString & "/01")
                    dtStartDate = dtStartDate.AddDays(-1)
                Else
                    dtStartDate = DateTime.MinValue
                End If
                If IsDate(dtRow("TeamFinishDate").ToString) Then
                    dtEndDate = Convert.ToDateTime(dtRow("TeamFinishDate").ToString)
                    dtEndDate = Convert.ToDateTime(dtEndDate.Year.ToString & "/" & dtEndDate.Month.ToString & "/01")
                    dtEndDate = dtEndDate.AddMonths(1)
                Else
                    dtEndDate = DateTime.MaxValue
                End If

                If intRowIndex Mod 2 = 0 Then
                    strAlternatingRowColor = "#CCCCCC"
                Else
                    strAlternatingRowColor = "#FFFFFF"
                End If

                If Convert.ToBoolean(dtRow("AllowView")) Then
                    lnkTeam = GenerateTableLink(dtRow("Team").ToString, "#3333FF", "Team~" & dtRow("TeamID").ToString & "~" & dtRow("Team").ToString, "")
                    objRow.Cells.Add(GenerateTableCell(dtRow("Team").ToString.Trim, New Unit("7%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, "", lnkTeam))
                Else
                    objRow.Cells.Add(GenerateTableCell(dtRow("Team").ToString.Trim, New Unit("7%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                End If
                If bEnglish Then
                    objRow.Cells.Add(GenerateTableCell(dtRow("TeamNameOther").ToString, New Unit("22%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, dtRow("TeamName").ToString))
                Else
                    objRow.Cells.Add(GenerateTableCell(dtRow("TeamName").ToString, New Unit("22%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, dtRow("TeamNameOther").ToString))
                End If
                objRow.Cells.Add(GenerateTableCell(dtRow("PillarAbbrev").ToString, New Unit("2%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                objRow.Cells.Add(GenerateTableCell(dtRow("BusinessUnitAbbrev").ToString, New Unit("2%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                If IsDate(dtRow("TeamStartDate").ToString) Then
                    strStartDate = Convert.ToDateTime(dtRow("TeamStartDate").ToString).ToString("yyyy/MM/dd")
                Else
                    strStartDate = dtRow("TeamStartDate").ToString
                End If
                objRow.Cells.Add(GenerateTableCell(strStartDate, New Unit("5%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))

                ' Status
                objCell = New TableCell
                objCell.Width = New Unit("7%")
                objCell.Height = New Unit(15)
                objCell.HorizontalAlign = HorizontalAlign.Right
                objCell.BackColor = System.Drawing.ColorTranslator.FromHtml(strAlternatingRowColor)
                objCell.BorderStyle = BorderStyle.Solid
                objCell.Text = dtRow("Description").ToString
                objRow.Cells.Add(objCell)

                For i As Integer = 9 To 20
                    objCell = New TableCell
                    objCell.Width = New Unit("4%")
                    objCell.Height = New Unit(15)
                    objCell.HorizontalAlign = HorizontalAlign.Right
                    objCell.BorderStyle = BorderStyle.Solid
                    objCell.Text = ""

                    dtCurMonth = Convert.ToDateTime(SessionManager.TrackerSelNavYear.ToString & "/" & (i - 8).ToString & "/01")
                    If dtCurMonth > dtStartDate AndAlso dtCurMonth < dtEndDate Then
                        objCell.BackColor = Drawing.Color.LightYellow
                    End If

                    objRow.Cells.Add(objCell)
                Next

                ' Current year
                objCell = New TableCell
                objCell.Width = New Unit("7%")
                objCell.Height = New Unit(15)
                objCell.HorizontalAlign = HorizontalAlign.Right
                objCell.BackColor = System.Drawing.ColorTranslator.FromHtml(strAlternatingRowColor)
                objCell.BorderStyle = BorderStyle.Solid
                objCell.Text = ""
                objRow.Cells.Add(objCell)

                tblTeams.Rows.Add(objRow)
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
            objLink.Text = strText
            objLink.ID = "PageLink~" + strElementID
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
