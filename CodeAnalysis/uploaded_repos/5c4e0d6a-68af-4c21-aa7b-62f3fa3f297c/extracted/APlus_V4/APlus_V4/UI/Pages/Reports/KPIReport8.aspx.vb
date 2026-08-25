#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports System.Collections.Generic

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class KPIReport8
        Inherits ApplicationBase

#Region " Private Variables"
        Private Shared ReadOnly FormName As String = "Key KPIs"
        Private Shared ReadOnly ProgramName As String = "KPIReport8"
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnExit.UniqueID + "'),window.event)")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnApplyFilter.UniqueID + "'),window.event)")
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

            Master.HeaderMessage = "Key KPIs"
            Master.IconImage = Request.ApplicationPath + "/images/chart.png"
            Master.MasterScriptManager.RegisterPostBackControl(btnExport)
            Master.MasterScriptManager.RegisterPostBackControl(btnRunReport)
            btnApplyFilter.Attributes.Add("onclick", "EnableWaitPanel()")
            btnExport.Attributes.Add("onclick", "DisableWaitPanel()")
            btnRunReport.Attributes.Add("onclick", "DisableWaitPanel()")

            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                SessionManager.SelectedKPIReportGroupID = 7
                LoadDropDownLists()
                ApplyFiltersFromCookie()
            End If

            If ProgramSecurity.CanUserAccessProgram(SessionManager.UserID, "KPIReportCategoryKPIMaster1") Then
                btnEditKPIReport.Visible = True
            Else
                btnEditKPIReport.Visible = False
            End If

            If Page.IsPostBack Then
                BindGrid()
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

            BindGrid()
        End Sub
        Protected Sub btnApplyFilter_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnApplyFilter.Click
            If (ddlBusinessArea.SelectedItem Is Nothing OrElse String.IsNullOrEmpty(ddlBusinessArea.SelectedItem.Value.ToString)) AndAlso _
            (ddlSite.SelectedItem Is Nothing OrElse String.IsNullOrEmpty(ddlSite.SelectedItem.Value.ToString)) Then
                Master.DisplayError("You must select a Business Area or Site")

                Return
            End If

            Dim cookie As New HttpCookie("KPIReport8Filter")
            cookie.Expires = Now.AddDays(Convert.ToInt16(ConfigurationManager.AppSettings("CookieExpirationTime")))

            If IsNumeric(txtYear.Text) Then
                cookie.Values("Year") = txtYear.Text
            Else
                cookie.Values.Remove("Year")
            End If

            If ddlBusinessArea.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlBusinessArea.SelectedItem.Value) Then
                cookie.Values("BusinessAreaID") = ddlBusinessArea.SelectedItem.Value.ToString
            Else
                cookie.Values.Remove("BusinessAreaID")
            End If

            If ddlSite.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlSite.SelectedItem.Value) Then
                cookie.Values("SiteID") = ddlSite.SelectedItem.Value.ToString
            Else
                cookie.Values.Remove("SiteID")
            End If

            Response.Cookies.Add(cookie)

            BindGrid()
        End Sub
        Private Sub Button_Click(ByVal sender As System.Object, ByVal e As WebControls.CommandEventArgs)
            Dim strTarget() As String
            strTarget = (CType(sender, LinkButton).ID).ToString.Split("~")
            Dim strProgram As String = ""

            If strTarget.Length = 2 AndAlso IsNumeric(strTarget(1)) Then
                SessionManager.KPISelNavYear = Convert.ToInt16(txtYear.Text)
                SessionManager.SelectedValueKPIID = strTarget(1)
                SessionManager.CallingProgram = "KPIReport8"

                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPIDailyValues1"), False)
            End If
        End Sub
        Protected Sub btnRunReport_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnRunReport.Click
            Try
                If Not IsNumeric(txtYear.Text) Then
                    Master.DisplayError("You must enter a valid Year")

                    Return
                ElseIf (ddlBusinessArea.SelectedItem Is Nothing OrElse String.IsNullOrEmpty(ddlBusinessArea.SelectedItem.Value.ToString)) AndAlso _
                (ddlSite.SelectedItem Is Nothing OrElse String.IsNullOrEmpty(ddlSite.SelectedItem.Value.ToString)) Then
                    Master.DisplayError("You must select a Business Area or Site")

                    Return
                End If

                Dim strURL As String = ""
                Dim strScript As String = ""
                Dim iYear As Integer = Convert.ToInt16(txtYear.Text)

                strURL = Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & "UI/Pages/DataCollectionPrograms/WebReportPrintPreview.aspx"
                strURL += "?ReportKey=KPIReport8"
                strURL += "&ReportParams="
                strURL += "Year=" & iYear.ToString
                If ddlBusinessArea.SelectedItem IsNot Nothing AndAlso ddlBusinessArea.SelectedItem.ToString.Trim.Length > 0 Then
                    strURL += "|BusinessAreaID=" & ddlBusinessArea.SelectedItem.Value.ToString
                End If
                If ddlSite.SelectedItem IsNot Nothing AndAlso ddlSite.SelectedItem.ToString.Trim.Length > 0 Then
                    strURL += "|SiteID=" & ddlSite.SelectedItem.Value.ToString
                End If

                If Not String.IsNullOrEmpty(strURL) Then
                    strScript = "window.open('" & strURL & "', '_blank');"

                    ClientScript.RegisterStartupScript(Me.GetType, "ReportScript", "<script language='javascript'>" & strScript & "</script>")
                End If
            Catch ex As Exception

            End Try
        End Sub
        Protected Sub btnExport_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnExport.Click
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
                If (ddlBusinessArea.SelectedItem Is Nothing OrElse String.IsNullOrEmpty(ddlBusinessArea.SelectedItem.Value.ToString)) AndAlso _
                (ddlSite.SelectedItem Is Nothing OrElse String.IsNullOrEmpty(ddlSite.SelectedItem.Value.ToString)) Then
                    Master.DisplayError("You must select a Business Area or Site")

                    Return
                End If

                Dim iYear As Integer = Convert.ToInt16(txtYear.Text)
                Dim iBusinessAreaID As Integer = -1
                Dim iSiteID As Integer = -1

                If ddlBusinessArea.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlBusinessArea.SelectedItem.Value) Then
                    iBusinessAreaID = ddlBusinessArea.SelectedItem.Value
                End If
                If ddlSite.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlSite.SelectedItem.Value) Then
                    iSiteID = ddlSite.SelectedItem.Value
                End If

                Dim objDT As DataTable = KPIValues.SelectKPIReport8Collection(iYear, SessionManager.SelectedKPIReportGroupID, iBusinessAreaID, iSiteID)

                Dim strHolder As String
                strHolder = "<table cellspacing='0' rules='all' border='1' id='grdExport' style='width:100%;border-collapse:collapse;'>"
                strHolder += "<tr style='color:White;background-color:DarkBlue;font-weight:bold;'>"
                strHolder += "<td>KPI Group</td><td>KPI</td><td>Legend</><td>UOM</td><td>Prev</td>"
                strHolder += "<td>Jan</td><td>Feb</td><td>Mar</td><td>Apr</td><td>May</td><td>Jun</td>"
                strHolder += "<td>Jul</td><td>Aug</td><td>Sep</td><td>Oct</td><td>Nov</td><td>Dec</td>"
                strHolder += "<td>W-4</td><td>W-3</td><td>W-2</td><td>W-1</td><td>MTD</td><td>YTD</td><td>Target</td><td>Comments</td></tr>"
                For Each dtRow As DataRow In objDT.Rows
                    strHolder += "<tr>"
                    strHolder += "<td>" + dtRow("BusinessArea").ToString.Trim + " : " + dtRow("Site").ToString.Trim + " : " + dtRow("KPIReportName").ToString.Trim + "</td>"

                    strHolder += "<td>" & dtRow("KPIOther").ToString.Trim & "</td>"
                    strHolder += "<td>" & dtRow("ReportLegend").ToString.Trim & "</td>"
                    strHolder += "<td>" & dtRow("UOM").ToString.Trim & "</td>"
                    strHolder += "<td>" & dtRow("Prev").ToString.Trim & "</td>"

                    strHolder += "<td>" & dtRow("Jan").ToString.Trim & "</td>"
                    strHolder += "<td>" & dtRow("Feb").ToString.Trim & "</td>"
                    strHolder += "<td>" & dtRow("Mar").ToString.Trim & "</td>"
                    strHolder += "<td>" & dtRow("Apr").ToString.Trim & "</td>"
                    strHolder += "<td>" & dtRow("May").ToString.Trim & "</td>"
                    strHolder += "<td>" & dtRow("Jun").ToString.Trim & "</td>"
                    strHolder += "<td>" & dtRow("Jul").ToString.Trim & "</td>"
                    strHolder += "<td>" & dtRow("Aug").ToString.Trim & "</td>"
                    strHolder += "<td>" & dtRow("Sep").ToString.Trim & "</td>"
                    strHolder += "<td>" & dtRow("Oct").ToString.Trim & "</td>"
                    strHolder += "<td>" & dtRow("Nov").ToString.Trim & "</td>"
                    strHolder += "<td>" & dtRow("Dec").ToString.Trim & "</td>"

                    strHolder += "<td>" & dtRow("Week-4").ToString.Trim & "</td>"
                    strHolder += "<td>" & dtRow("Week-3").ToString.Trim & "</td>"
                    strHolder += "<td>" & dtRow("Week-2").ToString.Trim & "</td>"
                    strHolder += "<td>" & dtRow("Week-1").ToString.Trim & "</td>"

                    strHolder += "<td>" & dtRow("MTD").ToString.Trim & "</td>"
                    strHolder += "<td>" & dtRow("YTD").ToString.Trim & "</td>"
                    strHolder += "<td>" & dtRow("Target").ToString.Trim & "</td>"

                    strHolder += "<td>" & dtRow("W1ToolTip").ToString.Trim & "</td>"

                    strHolder += "</tr>"
                Next
                strHolder += "</table>"
                SessionManager.ExportString = strHolder
                Response.Redirect(Request.ApplicationPath.ToString + "/UI/UserControls/Export.aspx")
            Catch Exc As Exception
                Throw
            End Try
        End Sub
        Protected Sub btnEditKPIReport_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnEditKPIReport.Click
            SessionManager.MasterControlExitProgram = "KPIReport8"
            If ddlBusinessArea.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlBusinessArea.SelectedItem.Value) Then
                SessionManager.KPIReportFilterBusinessAreaID = ddlBusinessArea.SelectedItem.Value
            Else
                SessionManager.KPIReportFilterBusinessAreaID = 0
            End If
            SessionManager.KPIReportFilterReportID = 0
            If ddlSite.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlSite.SelectedItem.Value) Then
                SessionManager.KPIReportFilterSiteID = ddlSite.SelectedItem.Value
            Else
                SessionManager.KPIReportFilterSiteID = 0
            End If

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPIReportCategoryKPIMaster1"), False)
        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            RemoveCurrentProgramandGoBack()
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadDropDownLists()
            Try
                BusinessAreaMaster.GetBusinessAreaMasterList(ddlBusinessArea)
                ddlBusinessArea.Items.Insert(0, "")

                SiteMaster.SelectSiteMasterActiveList(ddlSite)
                ddlSite.Items.Insert(0, "")

                Dim objDT As DataTable = KPIReports.SelectKPIReportCategoryMasterList(SessionManager.SelectedKPIReportGroupID, 0)
            Catch ex As Exception

            End Try
        End Sub
        Private Sub ApplyFiltersFromCookie()
            Dim objItem As ListItem

            If Request.Cookies("KPIReport8Filter") IsNot Nothing Then
                Dim cookie As HttpCookie = Request.Cookies("KPIReport8Filter")

                If cookie.Values("Year") IsNot Nothing AndAlso IsNumeric(cookie.Values("Year")) Then
                    txtYear.Text = cookie.Values("Year")
                Else
                    txtYear.Text = Now.Year
                End If

                If cookie.Values("BusinessAreaID") IsNot Nothing AndAlso IsNumeric(cookie.Values("BusinessAreaID")) Then
                    objItem = ddlBusinessArea.Items.FindByValue(cookie.Values("BusinessAreaID"))
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                    End If
                End If

                If cookie.Values("SiteID") IsNot Nothing AndAlso IsNumeric(cookie.Values("SiteID")) Then
                    objItem = ddlSite.Items.FindByValue(cookie.Values("SiteID"))
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                    End If
                End If
            Else
                txtYear.Text = Now.Year
            End If
        End Sub
        Private Sub BindGrid()
            tblKPIValues.Rows.Clear()
            btnRunReport.Enabled = False
            btnExport.Enabled = False

            If Not IsNumeric(txtYear.Text) Then
                Return
            End If
            If (ddlBusinessArea.SelectedItem Is Nothing OrElse String.IsNullOrEmpty(ddlBusinessArea.SelectedItem.Value.ToString)) AndAlso _
            (ddlSite.SelectedItem Is Nothing OrElse String.IsNullOrEmpty(ddlSite.SelectedItem.Value.ToString)) Then
                Master.DisplayError("You must select a Business Area or Site")

                Return
            End If

            Dim iYear As Integer = Convert.ToInt16(txtYear.Text)
            Dim iBusinessAreaID As Integer = -1
            Dim iSiteID As Integer = -1

            If ddlBusinessArea.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlBusinessArea.SelectedItem.Value) Then
                iBusinessAreaID = ddlBusinessArea.SelectedItem.Value
            End If
            If ddlSite.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlSite.SelectedItem.Value) Then
                iSiteID = ddlSite.SelectedItem.Value
            End If

            Dim objDT As DataTable = KPIValues.SelectKPIReport8Collection(iYear, SessionManager.SelectedKPIReportGroupID, iBusinessAreaID, iSiteID)
            Dim objRow As TableRow
            Dim objCell As TableCell
            Dim lnkValue As LinkButton = Nothing

            If objDT Is Nothing OrElse objDT.Rows.Count = 0 Then
                objRow = New TableRow
                objRow.Cells.Add(GenerateTableCell("No Records Exist for current filter", New Unit("100%"), New Unit(15), "#FFFFFF", "Red", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.None, "No Records"))
                tblKPIValues.Rows.Add(objRow)

                Return
            End If

            btnRunReport.Enabled = True
            btnExport.Enabled = True
            objRow = New TableRow
            objRow.Cells.Add(GenerateTableCell("", New Unit("10%"), New Unit(15), "#FFFFFF", "#FFFFFF", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Legend", New Unit("8%"), New Unit(15), "#FFFFFF", "#000000", HorizontalAlign.Center, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("UOM", New Unit("4%"), New Unit(15), "#FFFFFF", "#000000", HorizontalAlign.Center, VerticalAlign.Top, 1, BorderStyle.Solid, ""))

            For i As Integer = 12 To 31
                objRow.Cells.Add(GenerateTableCell(objDT.Columns(i).ColumnName, New Unit("4%"), New Unit(15), "#FFFFFF", "#000000", HorizontalAlign.Center, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            Next

            tblKPIValues.Rows.Add(objRow)

            Dim strCatDisplay As String = ""
            Dim strCategoryDisplayName As String = ""
            Dim intRowIndex As Integer = 0
            Dim strAlternatingRowColor As String
            Dim bTargetUp As Boolean = False

            For Each dtRow As DataRow In objDT.Rows
                bTargetUp = Convert.ToBoolean(dtRow("TargetUp"))

                intRowIndex += 1
                'values for this year
                objRow = New TableRow

                strCatDisplay = dtRow("KPIReportName").ToString.Trim + " : " + dtRow("Site").ToString.Trim + " : " + dtRow("BusinessArea").ToString.Trim

                If strCategoryDisplayName <> strCatDisplay Then
                    tblKPIValues.Rows.Add(GenerateTableRow(strCatDisplay, "#CCCCCC", "#000000", HorizontalAlign.Left, BorderStyle.None, 24, True))
                    strCategoryDisplayName = strCatDisplay
                End If

                strAlternatingRowColor = "#FFFFFF"

                lnkValue = GenerateTableLink(dtRow("KPIOther").ToString(), "#3333FF", dtRow("KPIReportCategoryID").ToString() & "~" & dtRow("KPIID").ToString, dtRow("KPI").ToString())
                objRow.Cells.Add(GenerateTableCell(dtRow("KPIOther").ToString(), New Unit("10%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, "", lnkValue))

                objCell = New TableCell
                objCell.Width = New Unit("8%")
                objCell.Height = New Unit(15)
                objCell.HorizontalAlign = HorizontalAlign.Center
                objCell.BackColor = System.Drawing.ColorTranslator.FromHtml(strAlternatingRowColor)
                objCell.BorderStyle = BorderStyle.Solid
                objCell.Text = dtRow("ReportLegend").ToString.Trim
                objCell.ToolTip = dtRow("LegendToolTip").ToString.Trim
                objRow.Cells.Add(objCell)

                objCell = New TableCell
                objCell.Width = New Unit("4%")
                objCell.Height = New Unit(15)
                objCell.HorizontalAlign = HorizontalAlign.Center
                objCell.BackColor = System.Drawing.ColorTranslator.FromHtml(strAlternatingRowColor)
                objCell.BorderStyle = BorderStyle.Solid
                objCell.Text = dtRow("UOM").ToString.Trim
                objRow.Cells.Add(objCell)

                ' Previous year
                objCell = New TableCell
                objCell.Width = New Unit("4%")
                objCell.Height = New Unit(15)
                objCell.HorizontalAlign = HorizontalAlign.Center
                objCell.BackColor = System.Drawing.ColorTranslator.FromHtml(strAlternatingRowColor)
                objCell.BorderStyle = BorderStyle.Solid
                If Not dtRow("Prev") Is DBNull.Value AndAlso IsNumeric(dtRow("Prev")) Then
                    objCell.Text = CDbl(dtRow("Prev")).ToString("0.##")
                End If
                objRow.Cells.Add(objCell)

                For i As Integer = 13 To 31
                    objCell = New TableCell
                    objCell.Width = New Unit("4%")
                    objCell.Height = New Unit(15)
                    objCell.HorizontalAlign = HorizontalAlign.Center
                    objCell.BackColor = System.Drawing.ColorTranslator.FromHtml(strAlternatingRowColor)
                    objCell.BorderStyle = BorderStyle.Solid
                    If Not dtRow(i) Is DBNull.Value AndAlso IsNumeric(dtRow(i)) Then
                        objCell.Text = CDbl(dtRow(i)).ToString("0.##")
                    End If

                    If i > 24 AndAlso i < 29 Then
                        If Not String.IsNullOrEmpty(dtRow(i + 25).ToString) Then
                            objCell.ToolTip = dtRow(i + 25).ToString.Trim
                        End If
                    End If

                    If i < 25 Then
                        If IsNumeric(dtRow(i).ToString) Then
                            If IsNumeric(dtRow(i).ToString) AndAlso IsNumeric(dtRow(i + 19).ToString) AndAlso IsNumeric(dtRow("Prev").ToString) Then
                                If bTargetUp Then
                                    If CDbl(dtRow(i).ToString) >= CDbl(dtRow(i + 19).ToString) Then
                                        objCell.BackColor = Drawing.Color.LightGreen
                                    ElseIf CDbl(dtRow(i).ToString) > CDbl(dtRow("Prev").ToString) Then
                                        objCell.BackColor = Drawing.Color.Yellow
                                    Else
                                        objCell.BackColor = Drawing.Color.Salmon
                                    End If
                                Else
                                    If CDbl(dtRow(i).ToString) <= CDbl(dtRow(i + 19).ToString) Then
                                        objCell.BackColor = Drawing.Color.LightGreen
                                    ElseIf CDbl(dtRow(i).ToString) < CDbl(dtRow("Prev").ToString) Then
                                        objCell.BackColor = Drawing.Color.Yellow
                                    Else
                                        objCell.BackColor = Drawing.Color.Salmon
                                    End If
                                End If
                            ElseIf IsNumeric(dtRow(i).ToString) AndAlso IsNumeric(dtRow(i + 19).ToString) Then
                                If bTargetUp Then
                                    If CDbl(dtRow(i).ToString) >= CDbl(dtRow(i + 19).ToString) Then
                                        objCell.BackColor = Drawing.Color.LightGreen
                                    Else
                                        objCell.BackColor = Drawing.Color.Salmon
                                    End If
                                Else
                                    If CDbl(dtRow(i).ToString) <= CDbl(dtRow(i + 19).ToString) Then
                                        objCell.BackColor = Drawing.Color.LightGreen
                                    Else
                                        objCell.BackColor = Drawing.Color.Salmon
                                    End If
                                End If
                            ElseIf IsNumeric(dtRow(i).ToString) AndAlso IsNumeric(dtRow("Prev").ToString) Then
                                If bTargetUp Then
                                    If CDbl(dtRow(i).ToString) > CDbl(dtRow("Prev").ToString) Then
                                        objCell.BackColor = Drawing.Color.Yellow
                                    Else
                                        objCell.BackColor = Drawing.Color.Salmon
                                    End If
                                Else
                                    If CDbl(dtRow(i).ToString) < CDbl(dtRow("Prev").ToString) Then
                                        objCell.BackColor = Drawing.Color.Yellow
                                    Else
                                        objCell.BackColor = Drawing.Color.Salmon
                                    End If
                                End If
                            End If
                        End If
                    ElseIf i = 30 Then
                        If IsNumeric(dtRow(i).ToString) Then
                            If IsNumeric(dtRow(i).ToString) AndAlso IsNumeric(dtRow("Target").ToString) AndAlso IsNumeric(dtRow("Prev").ToString) Then
                                If bTargetUp Then
                                    If CDbl(dtRow(i).ToString) >= CDbl(dtRow("Target").ToString) Then
                                        objCell.BackColor = Drawing.Color.LightGreen
                                    ElseIf CDbl(dtRow(i).ToString) > CDbl(dtRow("Prev").ToString) Then
                                        objCell.BackColor = Drawing.Color.Yellow
                                    Else
                                        objCell.BackColor = Drawing.Color.Salmon
                                    End If
                                Else
                                    If CDbl(dtRow(i).ToString) <= CDbl(dtRow("Target").ToString) Then
                                        objCell.BackColor = Drawing.Color.LightGreen
                                    ElseIf CDbl(dtRow(i).ToString) < CDbl(dtRow("Prev").ToString) Then
                                        objCell.BackColor = Drawing.Color.Yellow
                                    Else
                                        objCell.BackColor = Drawing.Color.Salmon
                                    End If
                                End If
                            ElseIf IsNumeric(dtRow(i).ToString) AndAlso IsNumeric(dtRow("Target").ToString) Then
                                If bTargetUp Then
                                    If CDbl(dtRow(i).ToString) >= CDbl(dtRow("Target").ToString) Then
                                        objCell.BackColor = Drawing.Color.LightGreen
                                    Else
                                        objCell.BackColor = Drawing.Color.Salmon
                                    End If
                                Else
                                    If CDbl(dtRow(i).ToString) <= CDbl(dtRow("Target").ToString) Then
                                        objCell.BackColor = Drawing.Color.LightGreen
                                    Else
                                        objCell.BackColor = Drawing.Color.Salmon
                                    End If
                                End If
                            ElseIf IsNumeric(dtRow(i).ToString) AndAlso IsNumeric(dtRow("Prev").ToString) Then
                                If bTargetUp Then
                                    If CDbl(dtRow(i).ToString) > CDbl(dtRow("Prev").ToString) Then
                                        objCell.BackColor = Drawing.Color.Yellow
                                    Else
                                        objCell.BackColor = Drawing.Color.Salmon
                                    End If
                                Else
                                    If CDbl(dtRow(i).ToString) < CDbl(dtRow("Prev").ToString) Then
                                        objCell.BackColor = Drawing.Color.Yellow
                                    Else
                                        objCell.BackColor = Drawing.Color.Salmon
                                    End If
                                End If
                            End If
                        End If
                    ElseIf dtRow("DailyKPICompare") AndAlso i > 24 AndAlso i < 30 Then
                        If IsNumeric(dtRow(i).ToString) Then
                            If IsNumeric(dtRow(i).ToString) AndAlso IsNumeric(dtRow("MTDT").ToString) AndAlso IsNumeric(dtRow("Prev").ToString) AndAlso dtRow("SummaryType").ToString.Trim.ToUpper <> "S" Then
                                If bTargetUp Then
                                    If CDbl(dtRow(i).ToString) >= CDbl(dtRow("MTDT").ToString) Then
                                        objCell.BackColor = Drawing.Color.LightGreen
                                    ElseIf CDbl(dtRow(i).ToString) >= CDbl(dtRow("Prev").ToString) Then
                                        objCell.BackColor = Drawing.Color.Yellow
                                    Else
                                        objCell.BackColor = Drawing.Color.Salmon
                                    End If
                                Else
                                    If CDbl(dtRow(i).ToString) <= CDbl(dtRow("MTDT").ToString) Then
                                        objCell.BackColor = Drawing.Color.LightGreen
                                    ElseIf CDbl(dtRow(i).ToString) <= CDbl(dtRow("Prev").ToString) Then
                                        objCell.BackColor = Drawing.Color.Yellow
                                    Else
                                        objCell.BackColor = Drawing.Color.Salmon
                                    End If
                                End If
                            ElseIf IsNumeric(dtRow(i).ToString) AndAlso IsNumeric(dtRow("MTDT").ToString) Then
                                If bTargetUp Then
                                    If CDbl(dtRow(i).ToString) >= CDbl(dtRow("MTDT").ToString) Then
                                        objCell.BackColor = Drawing.Color.LightGreen
                                    Else
                                        objCell.BackColor = Drawing.Color.Salmon
                                    End If
                                Else
                                    If CDbl(dtRow(i).ToString) <= CDbl(dtRow("MTDT").ToString) Then
                                        objCell.BackColor = Drawing.Color.LightGreen
                                    Else
                                        objCell.BackColor = Drawing.Color.Salmon
                                    End If
                                End If
                            End If
                        End If
                    End If

                    objRow.Cells.Add(objCell)
                Next

                tblKPIValues.Rows.Add(objRow)
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
