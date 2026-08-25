#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class MasterPlanSavings3
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Master Plan Savings"
        Private Shared ReadOnly ProgramName As String = "MasterPlanSavings1"
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
            If Request.Cookies("MasterPlanProgram") IsNot Nothing AndAlso Request.Cookies("MasterPlanProgram").Value.ToString.Trim.Length > 0 Then
                If Request.Cookies("MasterPlanProgram").Value.ToString = "MasterPlanSavings4" Then
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("MasterPlanSavings4"), False)
                    Return
                End If
            End If

            Master.IconImage = Request.ApplicationPath & "/images/TeamAction.gif"
            Master.HeaderMessage = GetTranslationString(FormName, FormName)
            Master.ProgramName = ProgramName

            LoadCommonJavaScripts()

            If SessionManager.WorkingSiteID = 0 Then
                RemoveCurrentProgramandGoBack()
            End If

            If SessionManager.TrackerSelNavYear = 0 Then
                SessionManager.TrackerSelNavYear = Now.Year
            End If

            If Not Page.IsPostBack Then
                chkProjected.Checked = SessionManager.ShowProjected

                LoadCultureTranslations()
                LoadFilterDropDowns()

                ApplyFiltersFromCookie()
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

            BindGrids()
        End Sub
        Protected Sub btnApplyFilter_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnApplyFilter.Click
            SessionManager.ShowProjected = chkProjected.Checked

            Dim cookie As New HttpCookie("MasterPlanFilter")
            cookie.Expires = Now.AddDays(Convert.ToInt16(ConfigurationManager.AppSettings("CookieExpirationTime")))

            If ddlSite.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlSite.SelectedItem.Value) Then
                cookie.Values("SiteID") = ddlSite.SelectedItem.Value.ToString
            Else
                cookie.Values.Remove("SiteID")
            End If

            If ddlPillar.SelectedItem IsNot Nothing AndAlso ddlPillar.SelectedItem.Value.ToString.Trim.Length > 0 Then
                cookie.Values("PillarAbbrev") = ddlPillar.SelectedItem.Value.ToString.Trim
            Else
                cookie.Values.Remove("PillarAbbrev")
            End If

            If ddlBusArea.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlBusArea.SelectedItem.Value) Then
                cookie.Values("BusinessAreaID") = ddlBusArea.SelectedItem.Value.ToString
            Else
                cookie.Values.Remove("BusinessAreaID")
            End If

            If ddlBusinessUnit.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlBusinessUnit.SelectedItem.Value) Then
                cookie.Values("BusinessUnitID") = ddlBusinessUnit.SelectedItem.Value.ToString
            Else
                cookie.Values.Remove("BusinessUnitID")
            End If

            Response.Cookies.Add(cookie)

            BindGrids()
        End Sub
        Protected Sub btnClearFilter_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnClearFilter.Click
            Response.Cookies("MasterPlanFilter").Expires = Now

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("MasterPlanSavings3"), False)
        End Sub
        Protected Sub btnEUR_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnEUR.Click
            Dim cookie As New HttpCookie("MasterPlanProgram", "MasterPlanSavings4")
            If IsNothing(ConfigurationManager.AppSettings("CookieExpirationTime")) Then
                cookie.Expires = DateTime.Now.AddDays(90)
            Else
                If IsNumeric(ConfigurationManager.AppSettings("CookieExpirationTime")) Then
                    cookie.Expires = DateTime.Now.AddHours(Convert.ToInt16(ConfigurationManager.AppSettings("CookieExpirationTime")))
                Else
                    cookie.Expires = DateTime.Now.AddDays(90)
                End If
            End If
            Response.Cookies.Add(cookie)

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("MasterPlanSavings4"), False)
        End Sub
        Private Sub ButtonClick(ByVal passArgs As String)
            Dim strTarget() As String
            strTarget = passArgs.Split("~")

            Select Case strTarget(1)
                Case "Nav"
                    SessionManager.TrackerSelNavYear = strTarget(2)

                    BindGrids()
                Case "Trackers"
                    SessionManager.TrackerSelSiteID = strTarget(2)
                    SessionManager.CallingProgram = "MasterPlanSavings3"
                    LastPixelPositionUpdate(ProgramName, Master.CurrentPixelPosition)
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("MasterPlanSavings1"), False)

                    Return
            End Select
        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TrackerSelNavYear)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TrackerSelSiteID)

            RemoveCurrentProgramandGoBack()
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadFilterDropDowns()
            Try
                SiteMaster.SelectSiteMasterAbbrevList(ddlSite)
                ddlSite.Items.Insert(0, "")

                Pillars.SelectPillarList(ddlPillar)
                ddlPillar.Items.Insert(0, "")

                BusinessUnitMaster.SelectBusinessUnitMasterAbbrevList(ddlBusinessUnit)
                ddlBusinessUnit.Items.Insert(0, "")

                BusinessAreaMaster.GetBusinessAreaMasterAbbrevList(ddlBusArea)
                ddlBusArea.Items.Insert(0, "")
            Catch ex As Exception

            End Try
        End Sub
        Private Sub ApplyFiltersFromCookie()
            Dim objItem As ListItem

            If Request.Cookies("MasterPlanFilter") IsNot Nothing Then
                Dim cookie As HttpCookie = Request.Cookies("MasterPlanFilter")

                If cookie.Values("SiteID") IsNot Nothing AndAlso IsNumeric(cookie.Values("SiteID")) Then
                    objItem = ddlSite.Items.FindByValue(cookie.Values("SiteID"))
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                    End If
                End If
                If ddlSite.SelectedItem Is Nothing AndAlso SessionManager.WorkingSiteID > 0 Then
                    objItem = ddlSite.Items.FindByValue(SessionManager.WorkingSiteID)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                    End If
                End If

                If cookie.Values("PillarAbbrev") IsNot Nothing AndAlso cookie.Values("PillarAbbrev").ToString.Trim.Length > 0 Then
                    objItem = ddlPillar.Items.FindByValue(cookie.Values("PillarAbbrev"))
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                    End If
                End If

                If cookie.Values("BusinessUnitID") IsNot Nothing AndAlso IsNumeric(cookie.Values("BusinessUnitID")) Then
                    objItem = ddlBusinessUnit.Items.FindByValue(cookie.Values("BusinessUnitID"))
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                    End If
                End If

                If cookie.Values("BusinessAreaID") IsNot Nothing AndAlso IsNumeric(cookie.Values("BusinessAreaID")) Then
                    objItem = ddlBusArea.Items.FindByValue(cookie.Values("BusinessAreaID"))
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                    End If
                End If
            Else
                If SessionManager.WorkingSiteID > 0 Then
                    objItem = ddlSite.Items.FindByValue(SessionManager.WorkingSiteID)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                    End If
                End If
            End If
        End Sub
        Private Sub BindGrids()
            Try
                Dim iSiteID As Integer = 0
                Dim strPillarAbbrev As String = ""
                Dim iBusinessUnitID As Integer = 0
                Dim iBusinessAreaID As Integer = 0

                If ddlSite.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlSite.SelectedItem.Value.ToString) Then
                    iSiteID = ddlSite.SelectedItem.Value
                End If
                If ddlPillar.SelectedItem IsNot Nothing AndAlso ddlPillar.SelectedItem.Value.ToString.Trim.Length > 0 Then
                    strPillarAbbrev = ddlPillar.SelectedItem.Value.ToString.Trim
                End If
                If ddlBusinessUnit.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlBusinessUnit.SelectedItem.Value.ToString) Then
                    iBusinessUnitID = ddlBusinessUnit.SelectedItem.Value
                End If
                If ddlBusArea.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlBusArea.SelectedItem.Value.ToString) Then
                    iBusinessAreaID = ddlBusArea.SelectedItem.Value
                End If

                Dim objDT As DataTable = TrackerPlanSavings.SelectTrackerPlanSavingsOverview(SessionManager.TrackerSelNavYear, iSiteID, strPillarAbbrev, iBusinessAreaID, iBusinessUnitID, chkProjected.Checked)
                If objDT IsNot Nothing Then
                    BindGrid(objDT)
                End If
                objDT = TrackerPlanSavings.SelectTrackerPlanSavingsOverview2(SessionManager.TrackerSelNavYear, iSiteID, strPillarAbbrev, iBusinessAreaID, iBusinessUnitID, chkProjected.Checked)
                If objDT IsNot Nothing Then
                    BindSiteTotalsGrid(objDT)
                End If
                objDT = TrackerPlanSavings.SelectTrackerPlanSavingsOverview3(SessionManager.TrackerSelNavYear, iSiteID, strPillarAbbrev, iBusinessAreaID, iBusinessUnitID, chkProjected.Checked)
                If objDT IsNot Nothing Then
                    BindTotalsGrid(objDT)
                End If
            Catch ex As Exception

            End Try
        End Sub
        Private Sub BindGrid(ByVal passData As DataTable)
            tblTrackerSavings.Rows.Clear()

            Dim objRow As TableRow
            Dim objCell As TableCell
            Dim lnkValue As LinkButton = Nothing

            If passData Is Nothing OrElse passData.Rows.Count = 0 Then
                objRow = New TableRow
                objRow.Cells.Add(GenerateTableCell("No Records Exist", New Unit("100%"), New Unit(15), "#FFFFFF", "Red", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.None, "No Records"))
                tblTrackerSavings.Rows.Add(objRow)

                Return
            End If

            'add top for year and nav buttons
            objRow = New TableRow
            objRow.Cells.Add(GenerateTableCell("", New Unit("20%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.None, "", GenerateTableLink("<", "#E7E7FF", "Nav~" & (SessionManager.TrackerSelNavYear - 1).ToString, "Previous Year")))
            objRow.Cells.Add(GenerateTableCell(SessionManager.TrackerSelNavYear.ToString, New Unit((0).ToString & "%"), New Unit(0), "#41519A", "#ffffff", HorizontalAlign.Center, VerticalAlign.NotSet, 13, BorderStyle.None, ""))
            objRow.Cells.Add(GenerateTableCell("", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 2, BorderStyle.None, "", GenerateTableLink(">", "#E7E7FF", "Nav~" & (SessionManager.TrackerSelNavYear + 1).ToString, "Next Year")))
            tblTrackerSavings.Rows.Add(objRow)

            'add Month columns
            'add header columns
            objRow = New TableRow
            objRow.Cells.Add(GenerateTableCell("", New Unit("20%"), New Unit(15), "#41519A", "#FFFFFF", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Prev", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Jan", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Feb", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Mar", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Apr", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("May", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Jun", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Jul", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Aug", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Sep", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Oct", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Nov", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Dec", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("YTD", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Cur", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))

            tblTrackerSavings.Rows.Add(objRow)

            Dim strCatDisplay As String = ""
            Dim strCategoryDisplayName As String = ""
            Dim intRowIndex As Integer = 0
            Dim iRowType As Integer = 0
            Dim strAlternatingRowColor As String = ""
            Dim strIndent As String = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"

            Dim iStretchRow As Integer = 3
            If chkProjected.Checked Then iStretchRow += 1

            For Each dtRow As DataRow In passData.Rows
                iRowType += 1
                'values for this year
                objRow = New TableRow

                strCatDisplay = dtRow("Site").ToString.Trim & " : " & dtRow("CurrencyAbbrev").ToString.Trim

                If strCategoryDisplayName <> strCatDisplay Then
                    tblTrackerSavings.Rows.Add(GenerateTableRow(strIndent & strCatDisplay, "#FFFFFF", "#000000", HorizontalAlign.Left, BorderStyle.None, 15, True))
                    strCategoryDisplayName = strCatDisplay
                    iRowType = 1
                End If

                Select Case Convert.ToInt16(dtRow("RowType"))
                    Case 1
                        strAlternatingRowColor = "#FFFFFF"
                        lnkValue = GenerateTableLink("Savings", "#3333FF", "Trackers~" & dtRow("SiteID").ToString(), "View Master Plan")
                        objRow.Cells.Add(GenerateTableCell("Savings", New Unit("20%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, "", lnkValue))
                    Case 2
                        strAlternatingRowColor = "#CCCCCC"
                        objRow.Cells.Add(GenerateTableCell("Target", New Unit("20%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                    Case 3
                        strAlternatingRowColor = "#CCCCCC"
                        objRow.Cells.Add(GenerateTableCell("Projected", New Unit("20%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                    Case 4
                        strAlternatingRowColor = "#CCCCCC"
                        objRow.Cells.Add(GenerateTableCell("Phantom", New Unit("20%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                    Case 5
                        strAlternatingRowColor = "#CCCCCC"
                        objRow.Cells.Add(GenerateTableCell("Plan", New Unit("20%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                    Case 6
                        strAlternatingRowColor = "#CCCCCC"
                        objRow.Cells.Add(GenerateTableCell("Stretch", New Unit("20%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
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

                For i As Integer = 5 To 17
                    objCell = New TableCell
                    objCell.Width = New Unit("5%")
                    objCell.Height = New Unit(15)
                    objCell.HorizontalAlign = HorizontalAlign.Right
                    objCell.BackColor = System.Drawing.ColorTranslator.FromHtml(strAlternatingRowColor)
                    objCell.BorderStyle = BorderStyle.Solid
                    If dtRow(i) IsNot DBNull.Value AndAlso IsNumeric(dtRow(i)) Then
                        objCell.Text = Math.Round(CDbl(dtRow(i)), 0).ToString("0")

                        If iRowType = 1 Then
                            If (passData.Rows(intRowIndex + 1)(i) IsNot DBNull.Value AndAlso IsNumeric(passData.Rows(intRowIndex + 1)(i))) AndAlso _
                            (passData.Rows(intRowIndex + iStretchRow)(i) IsNot DBNull.Value AndAlso IsNumeric(passData.Rows(intRowIndex + iStretchRow)(i))) Then
                                If Math.Round(CDbl(dtRow(i)), 0) >= Math.Round(CDbl(passData.Rows(intRowIndex + iStretchRow)(i)), 0) Then
                                    objCell.BackColor = Drawing.Color.LightGreen
                                ElseIf Math.Round(CDbl(dtRow(i)), 0) >= Math.Round(CDbl(passData.Rows(intRowIndex + 1)(i)), 0) Then
                                    objCell.BackColor = Drawing.Color.Yellow
                                Else
                                    objCell.BackColor = Drawing.Color.Salmon
                                End If
                            ElseIf (passData.Rows(intRowIndex + iStretchRow)(i) IsNot DBNull.Value AndAlso IsNumeric(passData.Rows(intRowIndex + iStretchRow)(i))) Then
                                If Math.Round(CDbl(dtRow(i)), 0) >= Math.Round(CDbl(passData.Rows(intRowIndex + iStretchRow)(i)), 0) Then
                                    objCell.BackColor = Drawing.Color.LightGreen
                                Else
                                    objCell.BackColor = Drawing.Color.Salmon
                                End If
                            ElseIf (passData.Rows(intRowIndex + 1)(i) IsNot DBNull.Value AndAlso IsNumeric(passData.Rows(intRowIndex + 1)(i))) Then
                                If Math.Round(CDbl(dtRow(i)), 0) >= Math.Round(CDbl(passData.Rows(intRowIndex + 1)(i)), 0) Then
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

                tblTrackerSavings.Rows.Add(objRow)
                intRowIndex += 1
            Next
        End Sub
        Private Sub BindSiteTotalsGrid(ByVal passData As DataTable)
            tblSiteTotals.Rows.Clear()

            Dim objRow As TableRow
            Dim objCell As TableCell
            Dim lnkValue As LinkButton = Nothing

            If passData Is Nothing OrElse passData.Rows.Count = 0 Then
                objRow = New TableRow
                objRow.Cells.Add(GenerateTableCell("No Records Exist", New Unit("100%"), New Unit(15), "#FFFFFF", "Red", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.None, "No Records"))
                tblSiteTotals.Rows.Add(objRow)

                Return
            End If

            'add Month columns
            'add header columns
            objRow = New TableRow
            objRow.Cells.Add(GenerateTableCell("", New Unit("15%"), New Unit(15), "#41519A", "#FFFFFF", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Prev", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Jan", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Feb", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Mar", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Apr", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("May", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Jun", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Jul", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Aug", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Sep", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Oct", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Nov", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Dec", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("YTD", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Cur", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))

            tblSiteTotals.Rows.Add(objRow)

            Dim strCategoryDisplayName As String = ""
            Dim intRowIndex As Integer = 0
            Dim iRowType As Integer = 0
            Dim strAlternatingRowColor As String = ""
            Dim strIndent As String = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"

            Dim iStretchRow As Integer = 3
            If chkProjected.Checked Then iStretchRow += 1

            tblSiteTotals.Rows.Add(GenerateTableRow(strIndent & "Totals", "#FFFFFF", "#000000", HorizontalAlign.Left, BorderStyle.None, 16, True))

            For Each dtRow As DataRow In passData.Rows
                iRowType += 1
                'values for this year
                objRow = New TableRow

                Select Case Convert.ToInt16(dtRow("RowType"))
                    Case 1
                        strAlternatingRowColor = "#FFFFFF"
                        objRow.Cells.Add(GenerateTableCell("Savings", New Unit("15%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                    Case 2
                        strAlternatingRowColor = "#CCCCCC"
                        objRow.Cells.Add(GenerateTableCell("Target", New Unit("15%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                    Case 3
                        strAlternatingRowColor = "#CCCCCC"
                        objRow.Cells.Add(GenerateTableCell("Projected", New Unit("15%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                    Case 4
                        strAlternatingRowColor = "#CCCCCC"
                        objRow.Cells.Add(GenerateTableCell("Phantom", New Unit("15%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                    Case 5
                        strAlternatingRowColor = "#CCCCCC"
                        objRow.Cells.Add(GenerateTableCell("Plan", New Unit("15%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                    Case 6
                        strAlternatingRowColor = "#CCCCCC"
                        objRow.Cells.Add(GenerateTableCell("Stretch", New Unit("15%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                End Select

                ' Currency
                objCell = New TableCell
                objCell.Width = New Unit("5%")
                objCell.Height = New Unit(15)
                objCell.HorizontalAlign = HorizontalAlign.Right
                objCell.BackColor = System.Drawing.ColorTranslator.FromHtml(strAlternatingRowColor)
                objCell.BorderStyle = BorderStyle.Solid
                objCell.Text = dtRow("CurrencyAbbrev").ToString
                objRow.Cells.Add(objCell)

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
                    objCell.Width = New Unit("5%")
                    objCell.Height = New Unit(15)
                    objCell.HorizontalAlign = HorizontalAlign.Right
                    objCell.BackColor = System.Drawing.ColorTranslator.FromHtml(strAlternatingRowColor)
                    objCell.BorderStyle = BorderStyle.Solid
                    If Not dtRow(i) Is DBNull.Value AndAlso IsNumeric(dtRow(i)) Then
                        objCell.Text = Math.Round(CDbl(dtRow(i)), 0).ToString("0")

                        If iRowType = 1 Then
                            If (passData.Rows(intRowIndex + 1)(i) IsNot DBNull.Value AndAlso IsNumeric(passData.Rows(intRowIndex + 1)(i))) AndAlso _
                            (passData.Rows(intRowIndex + iStretchRow)(i) IsNot DBNull.Value AndAlso IsNumeric(passData.Rows(intRowIndex + iStretchRow)(i))) Then
                                If Math.Round(CDbl(dtRow(i)), 0) >= Math.Round(CDbl(passData.Rows(intRowIndex + iStretchRow)(i)), 0) Then
                                    objCell.BackColor = Drawing.Color.LightGreen
                                ElseIf Math.Round(CDbl(dtRow(i)), 0) >= Math.Round(CDbl(passData.Rows(intRowIndex + 1)(i)), 0) Then
                                    objCell.BackColor = Drawing.Color.Yellow
                                Else
                                    objCell.BackColor = Drawing.Color.Salmon
                                End If
                            ElseIf (passData.Rows(intRowIndex + iStretchRow)(i) IsNot DBNull.Value AndAlso IsNumeric(passData.Rows(intRowIndex + iStretchRow)(i))) Then
                                If Math.Round(CDbl(dtRow(i)), 0) >= Math.Round(CDbl(passData.Rows(intRowIndex + iStretchRow)(i)), 0) Then
                                    objCell.BackColor = Drawing.Color.LightGreen
                                Else
                                    objCell.BackColor = Drawing.Color.Salmon
                                End If
                            ElseIf (passData.Rows(intRowIndex + 1)(i) IsNot DBNull.Value AndAlso IsNumeric(passData.Rows(intRowIndex + 1)(i))) Then
                                If Math.Round(CDbl(dtRow(i)), 0) >= Math.Round(CDbl(passData.Rows(intRowIndex + 1)(i)), 0) Then
                                    objCell.BackColor = Drawing.Color.Yellow
                                Else
                                    objCell.BackColor = Drawing.Color.Salmon
                                End If
                            End If
                        End If
                    End If

                    objRow.Cells.Add(objCell)

                    If iRowType = 6 Then iRowType = 0
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
        Private Sub BindTotalsGrid(ByVal passData As DataTable)
            tblTotals.Rows.Clear()

            Dim objRow As TableRow
            Dim objCell As TableCell
            Dim lnkValue As LinkButton = Nothing

            If passData Is Nothing OrElse passData.Rows.Count = 0 Then
                objRow = New TableRow
                objRow.Cells.Add(GenerateTableCell("No Records Exist", New Unit("100%"), New Unit(15), "#FFFFFF", "Red", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.None, "No Records"))
                tblTotals.Rows.Add(objRow)

                Return
            End If

            'add Month columns
            'add header columns
            objRow = New TableRow
            objRow.Cells.Add(GenerateTableCell("", New Unit("15%"), New Unit(15), "#41519A", "#FFFFFF", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Prev", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Jan", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Feb", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Mar", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Apr", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("May", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Jun", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Jul", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Aug", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Sep", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Oct", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Nov", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Dec", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("YTD", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Cur", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.Solid, ""))

            tblTotals.Rows.Add(objRow)

            Dim strCategoryDisplayName As String = ""
            Dim intRowIndex As Integer = 0
            Dim iRowType As Integer = 0
            Dim strAlternatingRowColor As String = ""
            Dim strIndent As String = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"

            Dim iStretchRow As Integer = 3
            If chkProjected.Checked Then iStretchRow += 1

            tblTotals.Rows.Add(GenerateTableRow(strIndent & "Totals", "#FFFFFF", "#000000", HorizontalAlign.Left, BorderStyle.None, 16, True))

            For Each dtRow As DataRow In passData.Rows
                iRowType += 1
                'values for this year
                objRow = New TableRow

                Select Case Convert.ToInt16(dtRow("RowType"))
                    Case 1
                        strAlternatingRowColor = "#FFFFFF"
                        objRow.Cells.Add(GenerateTableCell("Savings", New Unit("15%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                    Case 2
                        strAlternatingRowColor = "#CCCCCC"
                        objRow.Cells.Add(GenerateTableCell("Target", New Unit("15%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                    Case 3
                        strAlternatingRowColor = "#CCCCCC"
                        objRow.Cells.Add(GenerateTableCell("Projected", New Unit("15%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                    Case 4
                        strAlternatingRowColor = "#CCCCCC"
                        objRow.Cells.Add(GenerateTableCell("Phantom", New Unit("15%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                    Case 5
                        strAlternatingRowColor = "#CCCCCC"
                        objRow.Cells.Add(GenerateTableCell("Plan", New Unit("15%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                    Case 6
                        strAlternatingRowColor = "#CCCCCC"
                        objRow.Cells.Add(GenerateTableCell("Stretch", New Unit("15%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                End Select

                ' Currency
                objCell = New TableCell
                objCell.Width = New Unit("5%")
                objCell.Height = New Unit(15)
                objCell.HorizontalAlign = HorizontalAlign.Right
                objCell.BackColor = System.Drawing.ColorTranslator.FromHtml(strAlternatingRowColor)
                objCell.BorderStyle = BorderStyle.Solid
                objCell.Text = dtRow("CurrencyAbbrev").ToString
                objRow.Cells.Add(objCell)

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
                    objCell.Width = New Unit("5%")
                    objCell.Height = New Unit(15)
                    objCell.HorizontalAlign = HorizontalAlign.Right
                    objCell.BackColor = System.Drawing.ColorTranslator.FromHtml(strAlternatingRowColor)
                    objCell.BorderStyle = BorderStyle.Solid
                    If Not dtRow(i) Is DBNull.Value AndAlso IsNumeric(dtRow(i)) Then
                        objCell.Text = Math.Round(CDbl(dtRow(i)), 0).ToString("0")

                        If iRowType = 1 Then
                            If (passData.Rows(intRowIndex + 1)(i) IsNot DBNull.Value AndAlso IsNumeric(passData.Rows(intRowIndex + 1)(i))) AndAlso _
                            (passData.Rows(intRowIndex + iStretchRow)(i) IsNot DBNull.Value AndAlso IsNumeric(passData.Rows(intRowIndex + iStretchRow)(i))) Then
                                If Math.Round(CDbl(dtRow(i)), 0) >= Math.Round(CDbl(passData.Rows(intRowIndex + iStretchRow)(i)), 0) Then
                                    objCell.BackColor = Drawing.Color.LightGreen
                                ElseIf Math.Round(CDbl(dtRow(i)), 0) >= Math.Round(CDbl(passData.Rows(intRowIndex + 1)(i)), 0) Then
                                    objCell.BackColor = Drawing.Color.Yellow
                                Else
                                    objCell.BackColor = Drawing.Color.Salmon
                                End If
                            ElseIf (passData.Rows(intRowIndex + iStretchRow)(i) IsNot DBNull.Value AndAlso IsNumeric(passData.Rows(intRowIndex + iStretchRow)(i))) Then
                                If Math.Round(CDbl(dtRow(i)), 0) >= Math.Round(CDbl(passData.Rows(intRowIndex + iStretchRow)(i)), 0) Then
                                    objCell.BackColor = Drawing.Color.LightGreen
                                Else
                                    objCell.BackColor = Drawing.Color.Salmon
                                End If
                            ElseIf (passData.Rows(intRowIndex + 1)(i) IsNot DBNull.Value AndAlso IsNumeric(passData.Rows(intRowIndex + 1)(i))) Then
                                If Math.Round(CDbl(dtRow(i)), 0) >= Math.Round(CDbl(passData.Rows(intRowIndex + 1)(i)), 0) Then
                                    objCell.BackColor = Drawing.Color.Yellow
                                Else
                                    objCell.BackColor = Drawing.Color.Salmon
                                End If
                            End If
                        End If
                    End If

                    objRow.Cells.Add(objCell)

                    If iRowType = 6 Then iRowType = 0
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

                tblTotals.Rows.Add(objRow)
                intRowIndex += 1
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
