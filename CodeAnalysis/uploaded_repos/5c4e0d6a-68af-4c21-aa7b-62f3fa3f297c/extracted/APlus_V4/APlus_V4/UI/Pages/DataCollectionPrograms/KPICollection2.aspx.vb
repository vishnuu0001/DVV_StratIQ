#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class KPICollection2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "KPI Collection"
        Private Shared ReadOnly ProgramName As String = "KPICollection2"
        Private htKPI As New Hashtable()
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
                lblSite.Text = GetTranslationString("site", lblSite.Text.Replace(":", "")) & ":"
                lblPillar.Text = GetTranslationString("pillar", lblPillar.Text.Replace(":", "")) & ":"
                lblBA.Text = GetTranslationString("businessarea", lblBA.Text.Replace(":", "")) & ":"
                lblBU.Text = GetTranslationString("businessunit", lblBU.Text.Replace(":", "")) & ":"
                lblCategory.Text = GetTranslationString("category", lblCategory.Text.Replace(":", "")) & ":"
                lblReportingLevel.Text = GetTranslationString("reportinglevel", lblReportingLevel.Text.Replace(":", "")) & ":"
                lblPeriodView.Text = GetTranslationString("periodview", lblPeriodView.Text.Replace(":", "")) & ":"
                lblArea.Text = GetTranslationString("area", lblArea.Text.Replace(":", "")) & ":"
                ckAllAreas.Text = GetTranslationString("allareakpi", ckAllAreas.Text)
                ckShowSupportingKPI.Text = GetTranslationString("showsupportingkpi", ckShowSupportingKPI.Text)
                ckResponsibleUser.Text = GetTranslationString("myresponsibleuser", ckResponsibleUser.Text)
                btnApplyFilter.Text = GetTranslationString("applyfilter", btnApplyFilter.Text)
                btnClearFilter.Text = GetTranslationString("clearfilter", btnClearFilter.Text)
                btnExit.Text = GetTranslationString("exit", btnExit.Text)
                btnExport.Text = GetTranslationString("export", btnExport.Text)
                btnShowTargets.Text = GetTranslationString("showtargets", btnShowTargets.Text)
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
            btnRunReport1.Attributes.Add("onclick", "DisableWaitPanel()")
            btnRunReport2.Attributes.Add("onclick", "DisableWaitPanel()")
            btnRunReport3.Attributes.Add("onclick", "DisableWaitPanel()")
            Master.MasterScriptManager.RegisterPostBackControl(btnRunReport1)
            Master.MasterScriptManager.RegisterPostBackControl(btnRunReport2)
            Master.MasterScriptManager.RegisterPostBackControl(btnRunReport3)

            LoadCommonJavaScripts()

            If SessionManager.KPISelNavYear = 0 Then
                SessionManager.KPISelNavYear = Now.Year
            End If

            If Not Page.IsPostBack Then
                LoadCultureTranslations()

                LoadFilterDropDowns()
                ApplyFiltersFromCookie()
            Else
                If Request.Item("__EVENTTARGET").ToString.Contains("PageLink") Then
                    ButtonClick(Request.Item("__EVENTTARGET"))
                    Return
                End If

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
        Private Sub ButtonClick(ByVal passArgs As String)
            Dim strTarget() As String
            strTarget = passArgs.Split("~")

            Select Case strTarget(1)
                Case "Nav"
                    SessionManager.KPISelNavYear = strTarget(2)

                    BindGrid()
                Case "Value"
                    SessionManager.SelectedValueKPIID = strTarget(2)
                    SessionManager.CallingProgram = "KPICollection2"
                    LastPixelPositionUpdate(ProgramName, Master.CurrentPixelPosition)
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPIValues1"), False)
                    Return
            End Select
        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.KPISelNavYear)

            RemoveCurrentProgramandGoBack()
        End Sub
        Protected Sub btnRunReport1_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnRunReport1.Click
            Try
                htKPI = DirectCast(ViewState("KPIList"), Hashtable)
                Dim strKPI As String = ""

                If htKPI.Count > 0 Then
                    Dim myEnumerator As IDictionaryEnumerator = htKPI.GetEnumerator()

                    While myEnumerator.MoveNext
                        If strKPI.Trim.Length > 0 Then
                            strKPI += ","
                        End If
                        strKPI += myEnumerator.Value
                    End While
                End If

                If strKPI.Length > 0 Then
                    Dim strURL As String = Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & "UI/Pages/DataCollectionPrograms/WebReportPrintPreview.aspx"
                    strURL += "?ReportKey=KPIReportSummary"
                    strURL += "&ReportParams="
                    strURL += "KPIID=" & strKPI
                    strURL += "|KPIYear=" & SessionManager.KPISelNavYear.ToString

                    ClientScript.RegisterStartupScript(Me.GetType, "ReportScript", "<script language='javascript'>window.open('" & strURL & "', '_blank')</script>")
                End If
            Catch ex As Exception

            End Try
        End Sub
        Protected Sub btnRunReport2_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnRunReport2.Click
            Try
                htKPI = DirectCast(ViewState("KPIList"), Hashtable)
                Dim strKPI As String = ""

                If htKPI.Count > 0 Then
                    Dim myEnumerator As IDictionaryEnumerator = htKPI.GetEnumerator()

                    While myEnumerator.MoveNext
                        If strKPI.Trim.Length > 0 Then
                            strKPI += ","
                        End If
                        strKPI += myEnumerator.Value
                    End While
                End If

                If strKPI.Length > 0 Then
                    Dim strURL As String = Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & "UI/Pages/DataCollectionPrograms/WebReportPrintPreview.aspx"
                    strURL += "?ReportKey=KPIReportSummaryBar"
                    strURL += "&ReportParams="
                    strURL += "KPIID=" & strKPI
                    strURL += "|KPIYear=" & SessionManager.KPISelNavYear.ToString

                    ClientScript.RegisterStartupScript(Me.GetType, "ReportScript", "<script language='javascript'>window.open('" & strURL & "', '_blank')</script>")
                End If
            Catch ex As Exception

            End Try
        End Sub
        Protected Sub btnRunReport3_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnRunReport3.Click
            Try
                htKPI = DirectCast(ViewState("KPIList"), Hashtable)
                Dim strKPI As String = ""

                If htKPI.Count > 0 Then
                    Dim myEnumerator As IDictionaryEnumerator = htKPI.GetEnumerator()

                    While myEnumerator.MoveNext
                        If strKPI.Trim.Length > 0 Then
                            strKPI += ","
                        End If
                        strKPI += myEnumerator.Value
                    End While
                End If

                If strKPI.Length > 0 Then
                    Dim strURL As String = Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & "UI/Pages/DataCollectionPrograms/WebReportPrintPreview.aspx"
                    strURL += "?ReportKey=KPIReportSummaryBar2"
                    strURL += "&ReportParams="
                    strURL += "KPIID=" & strKPI
                    strURL += "|KPIPeriod=" & Format(Now, "yyyy/MM/01")

                    ClientScript.RegisterStartupScript(Me.GetType, "ReportScript", "<script language='javascript'>window.open('" & strURL & "', '_blank')</script>")
                End If
            Catch ex As Exception

            End Try
        End Sub
        Protected Sub btnExport_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnExport.Click
            tblKPIValues.Rows.Clear()

            Dim iSiteID As Integer = -1
            Dim strPillarAbbrev As String = ""
            Dim iBusinessUnitID As Integer = -1
            Dim iBusinessAreaID As Integer = -1
            Dim iTeamCategoryID As Integer = -1
            Dim iReportingLevelID As Integer = -1
            Dim iAreaID As Integer = -1
            Dim strResponsibleUserID As String = ""

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
            If ddlTeamCategory.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlTeamCategory.SelectedItem.Value) Then
                iTeamCategoryID = ddlTeamCategory.SelectedItem.Value
            End If
            If ddlReportingLevel.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlReportingLevel.SelectedItem.Value) Then
                iReportingLevelID = ddlReportingLevel.SelectedItem.Value
            End If
            If ddlArea.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlArea.SelectedItem.Value) Then
                iAreaID = ddlArea.SelectedItem.Value
            End If
            If ckResponsibleUser.Checked Then
                strResponsibleUserID = SessionManager.UserID
            End If

            Dim objDT As DataTable = KPIValues.SelectKPICollectionNoTarget(SessionManager.KPISelNavYear, iSiteID, strPillarAbbrev, iBusinessAreaID, iBusinessUnitID, iTeamCategoryID, iReportingLevelID, strResponsibleUserID, SessionManager.UserID, ckShowSupportingKPI.Checked, iAreaID, ckAllAreas.Checked)

            If ddlViewMode.SelectedItem IsNot Nothing AndAlso ddlViewMode.SelectedItem.Value = "Quarter" Then
                LoadQuarterGrid(objDT)
            Else
                LoadMonthGrid(objDT)
            End If

            If objDT.Rows.Count > 0 Then
                Dim stringWrite As New System.IO.StringWriter
                Dim htmlWrite As New System.Web.UI.HtmlTextWriter(stringWrite)
                Dim dg As New DataGrid
                dg.HeaderStyle.HorizontalAlign = HorizontalAlign.Left
                dg.HeaderStyle.VerticalAlign = VerticalAlign.Top
                dg.HeaderStyle.Font.Bold = True
                dg.ItemStyle.VerticalAlign = VerticalAlign.Top
                dg.ItemStyle.HorizontalAlign = HorizontalAlign.Left

                dg.DataSource = objDT
                dg.DataBind()
                dg.RenderControl(htmlWrite)

                SessionManager.ExportString = stringWrite.ToString

                HttpContext.Current.Response.Redirect(HttpContext.Current.Request.ApplicationPath.ToString + "/UI/UserControls/Export.aspx")
            End If
        End Sub
        Protected Sub btnApplyFilter_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnApplyFilter.Click
            Dim cookie As New HttpCookie("KPICollectionFilter")
            cookie.Expires = Now.AddDays(Convert.ToInt16(ConfigurationManager.AppSettings("CookieExpirationTime")))

            If ddlSite.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlSite.SelectedItem.Value) Then
                cookie.Values("SiteID") = ddlSite.SelectedItem.Value.ToString
                If Request.Cookies("KPICollectionFilter") IsNot Nothing AndAlso Request.Cookies("KPICollectionFilter")("SiteID") IsNot Nothing AndAlso ddlSite.SelectedItem.Value.ToString <> Request.Cookies("KPICollectionFilter")("SiteID") Then
                    ddlSite_SelectedIndexChanged()
                End If
            Else
                cookie.Values.Remove("SiteID")
                ddlSite_SelectedIndexChanged()
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

            If ddlTeamCategory.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlTeamCategory.SelectedItem.Value) Then
                cookie.Values("TeamCategoryID") = ddlTeamCategory.SelectedItem.Value.ToString
            Else
                cookie.Values.Remove("TeamCategoryID")
            End If

            If ddlReportingLevel.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlReportingLevel.SelectedItem.Value) Then
                cookie.Values("ReportingLevelID") = ddlReportingLevel.SelectedItem.Value.ToString
            Else
                cookie.Values.Remove("ReportingLevelID")
            End If

            If ckResponsibleUser.Checked Then
                cookie.Values("ResponsibleKPIs") = ckResponsibleUser.Checked.ToString
            Else
                cookie.Values.Remove("ResponsibleKPIs")
            End If

            If ckShowSupportingKPI.Checked Then
                cookie.Values("ShowSupportingKPIs") = ckShowSupportingKPI.Checked.ToString
            Else
                cookie.Values.Remove("ShowSupportingKPIs")
            End If

            If ddlArea.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlArea.SelectedItem.Value) Then
                cookie.Values("AreaGroupID") = ddlArea.SelectedItem.Value.ToString
            Else
                cookie.Values.Remove("AreaGroupID")
            End If

            If ckAllAreas.Checked Then
                cookie.Values("AllAreas") = ckAllAreas.Checked
            Else
                cookie.Values.Remove("AllAreas")
            End If

            Response.Cookies.Add(cookie)

            cookie = New HttpCookie("KPICollectionView")
            If ddlViewMode.SelectedItem IsNot Nothing Then
                cookie.Value = ddlViewMode.SelectedItem.Value.ToString.Trim
            End If
            Response.Cookies.Add(cookie)

            BindGrid()
        End Sub
        Protected Sub btnClearFilter_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnClearFilter.Click
            Response.Cookies("KPICollectionFilter").Expires = Now

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPICollection2"), False)
        End Sub
        Protected Sub btnShowTargets_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnShowTargets.Click
            Dim cookie As New HttpCookie("KPICollectionProgram", "KPICollection")
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

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPICollection"), False)
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadFilterDropDowns()
            Try
                SiteMaster.SelectSiteMasterActiveList(ddlSite)
                ddlSite.Items.Insert(0, "")

                Pillars.SelectPillarList(ddlPillar)
                ddlPillar.Items.Insert(0, "")

                BusinessUnitMaster.SelectBusinessUnitMasterAbbrevList(ddlBusinessUnit)
                ddlBusinessUnit.Items.Insert(0, "")

                BusinessAreaMaster.GetBusinessAreaMasterAbbrevList(ddlBusArea)
                ddlBusArea.Items.Insert(0, "")

                TeamCategoryMaster.GetTeamCategoryList(ddlTeamCategory)
                ddlTeamCategory.Items.Insert(0, "")

                ReportingLevelMaster.GetReportingLevelList(ddlReportingLevel)
                ddlReportingLevel.Items.Insert(0, "")
            Catch ex As Exception

            End Try
        End Sub
        Protected Sub ddlSite_SelectedIndexChanged()
            ddlArea.Items.Clear()

            If ddlSite.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlSite.SelectedItem.Value) Then
                AreaGroupMaster.GetAreaGroupMasterList(ddlArea, ddlSite.SelectedItem.Value)
                ddlArea.Items.Insert(0, "")
            End If
        End Sub
        Private Sub ApplyFiltersFromCookie()
            Dim objItem As ListItem

            If Request.Cookies("KPICollectionFilter") IsNot Nothing Then
                Dim cookie As HttpCookie = Request.Cookies("KPICollectionFilter")

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

                If cookie.Values("TeamCategoryID") IsNot Nothing AndAlso IsNumeric(cookie.Values("TeamCategoryID")) Then
                    objItem = ddlTeamCategory.Items.FindByValue(cookie.Values("TeamCategoryID"))
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                    End If
                End If

                If cookie.Values("ReportingLevelID") IsNot Nothing AndAlso IsNumeric(cookie.Values("ReportingLevelID")) Then
                    objItem = ddlReportingLevel.Items.FindByValue(cookie.Values("ReportingLevelID"))
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                    End If
                End If

                If cookie.Values("ResponsibleKPIs") IsNot Nothing AndAlso Convert.ToBoolean(cookie.Values("ResponsibleKPIs")) = True Then
                    ckResponsibleUser.Checked = True
                End If

                If cookie.Values("ShowSupportingKPIs") IsNot Nothing AndAlso Convert.ToBoolean(cookie.Values("ShowSupportingKPIs")) = True Then
                    ckShowSupportingKPI.Checked = True
                End If

                ddlSite_SelectedIndexChanged()
                If cookie.Values("AreaGroupID") IsNot Nothing AndAlso IsNumeric(cookie.Values("AreaGroupID").ToString) Then
                    objItem = ddlArea.Items.FindByValue(cookie.Values("AreaGroupID"))
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                    End If
                End If

                If cookie.Values("AllAreas") IsNot Nothing Then
                    ckAllAreas.Checked = cookie.Values("AllAreas")
                End If
            Else
                If SessionManager.WorkingSiteID > 0 Then
                    objItem = ddlSite.Items.FindByValue(SessionManager.WorkingSiteID)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                    End If
                Else
                    objItem = ddlSite.Items.FindByValue(UserMaster.GetUserSite(SessionManager.UserID))
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                    End If
                End If

                ddlSite_SelectedIndexChanged()
            End If

            If Request.Cookies("KPICollectionView") IsNot Nothing AndAlso Request.Cookies("KPICollectionView").Value.ToString.Trim.Length > 0 Then
                objItem = ddlViewMode.Items.FindByValue(Request.Cookies("KPICollectionView").Value.ToString)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                End If
            Else
                objItem = ddlViewMode.Items.FindByValue("Month")
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                End If
            End If
        End Sub
        Private Sub BindGrid()
            tblKPIValues.Rows.Clear()

            Dim iSiteID As Integer = -1
            Dim strPillarAbbrev As String = ""
            Dim iBusinessUnitID As Integer = -1
            Dim iBusinessAreaID As Integer = -1
            Dim iTeamCategoryID As Integer = -1
            Dim iReportingLevelID As Integer = -1
            Dim iAreaGroupID As Integer = -1
            Dim strResponsibleUserID As String = ""

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
            If ddlTeamCategory.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlTeamCategory.SelectedItem.Value) Then
                iTeamCategoryID = ddlTeamCategory.SelectedItem.Value
            End If
            If ddlReportingLevel.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlReportingLevel.SelectedItem.Value) Then
                iReportingLevelID = ddlReportingLevel.SelectedItem.Value
            End If
            If ddlArea.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlArea.SelectedItem.Value) Then
                iAreaGroupID = ddlArea.SelectedItem.Value
            End If
            If ckResponsibleUser.Checked Then
                strResponsibleUserID = SessionManager.UserID
            End If

            Dim objDT As DataTable = KPIValues.SelectKPICollectionNoTarget(SessionManager.KPISelNavYear, iSiteID, strPillarAbbrev, iBusinessAreaID, iBusinessUnitID, iTeamCategoryID, iReportingLevelID, strResponsibleUserID, SessionManager.UserID, ckShowSupportingKPI.Checked, iAreaGroupID, ckAllAreas.Checked)

            If ddlViewMode.SelectedItem IsNot Nothing AndAlso ddlViewMode.SelectedItem.Value = "Quarter" Then
                LoadQuarterGrid(objDT)
            Else
                LoadMonthGrid(objDT)
            End If
        End Sub
        Private Sub LoadMonthGrid(ByVal objDT As DataTable)
            Dim objRow As TableRow
            Dim objCell As TableCell
            Dim lnkValue As LinkButton = Nothing

            If objDT Is Nothing OrElse objDT.Rows.Count = 0 Then
                objRow = New TableRow
                objRow.Cells.Add(GenerateTableCell("No Records Exist for current filter", New Unit("100%"), New Unit(15), "#FFFFFF", "Red", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.None, "No Records"))
                tblKPIValues.Rows.Add(objRow)

                Return
            End If

            'add top for year and nav buttons
            objRow = New TableRow
            objRow.Cells.Add(GenerateTableCell("", New Unit("14%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.None, "", GenerateTableLink("<", "#E7E7FF", "Nav~" & (SessionManager.KPISelNavYear - 1).ToString, "Previous Year")))
            objRow.Cells.Add(GenerateTableCell(SessionManager.KPISelNavYear.ToString, New Unit((0).ToString & "%"), New Unit(0), "#41519A", "#ffffff", HorizontalAlign.Center, VerticalAlign.NotSet, 19, BorderStyle.None, ""))
            objRow.Cells.Add(GenerateTableCell("", New Unit("4%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.None, "", GenerateTableLink(">", "#E7E7FF", "Nav~" & (SessionManager.KPISelNavYear + 1).ToString, "Next Year")))
            tblKPIValues.Rows.Add(objRow)

            'add Month columns
            'add header columns
            objRow = New TableRow
            objRow.Cells.Add(GenerateTableCell("", New Unit("14%"), New Unit(15), "#FFFFFF", "#FFFFFF", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.Solid, ""))

            objRow.Cells.Add(GenerateTableCell("UOM", New Unit("5%"), New Unit(15), "#FFFFFF", "#000000", HorizontalAlign.Center, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("PIL", New Unit("2%"), New Unit(15), "#FFFFFF", "#000000", HorizontalAlign.Center, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("BA", New Unit("2%"), New Unit(15), "#FFFFFF", "#000000", HorizontalAlign.Center, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("BU", New Unit("2%"), New Unit(15), "#FFFFFF", "#000000", HorizontalAlign.Center, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Area", New Unit("3%"), New Unit(15), "#FFFFFF", "#000000", HorizontalAlign.Center, VerticalAlign.Top, 1, BorderStyle.Solid, ""))

            For i As Integer = 14 To 26
                objRow.Cells.Add(GenerateTableCell(objDT.Columns(i).ColumnName, New Unit("4%"), New Unit(15), "#FFFFFF", "#000000", HorizontalAlign.Center, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            Next
            objRow.Cells.Add(GenerateTableCell("YTD", New Unit("4%"), New Unit(15), "#FFFFFF", "#000000", HorizontalAlign.Center, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Target", New Unit("4%"), New Unit(15), "#FFFFFF", "#000000", HorizontalAlign.Center, VerticalAlign.Top, 1, BorderStyle.Solid, ""))

            tblKPIValues.Rows.Add(objRow)

            Dim strCatDisplay As String = ""
            Dim strCategoryDisplayName As String = ""
            Dim intRowIndex As Integer = 0
            Dim strAlternatingRowColor As String
            Dim bTargetUp As Boolean = False
            Dim iAlign As Integer = HorizontalAlign.Left

            Dim bEnglish As Boolean = (New System.Globalization.CultureInfo(SessionManager.CulturePref).TwoLetterISOLanguageName.ToUpper = "EN")
            htKPI = New Hashtable()
            For Each dtRow As DataRow In objDT.Rows
                If Not htKPI.ContainsKey(dtRow("KPIID").ToString) Then
                    htKPI.Add(dtRow("KPIID").ToString, dtRow("KPIID").ToString)
                End If
                bTargetUp = Convert.ToBoolean(dtRow("TargetUp"))

                intRowIndex += 1
                'values for this year
                objRow = New TableRow

                strCatDisplay = dtRow("Site").ToString.Trim & " : " & dtRow("TeamCategory").ToString.Trim

                If strCategoryDisplayName <> strCatDisplay Then
                    tblKPIValues.Rows.Add(GenerateTableRow(strCatDisplay, "#CCCCCC", "#000000", HorizontalAlign.Left, BorderStyle.None, 21, True))
                    strCategoryDisplayName = strCatDisplay
                End If

                strAlternatingRowColor = "#FFFFFF"

                If IsNumeric(dtRow("PrimaryKPIID").ToString) Then
                    iAlign = HorizontalAlign.Center
                Else
                    iAlign = HorizontalAlign.Left
                End If

                If bEnglish Then
                    lnkValue = GenerateTableLink(dtRow("KPIOther").ToString(), "#3333FF", dtRow("KPIType").ToString() & "~" & dtRow("KPIID").ToString, dtRow("KPI").ToString())
                    objRow.Cells.Add(GenerateTableCell(dtRow("KPIOther").ToString(), New Unit("14%"), New Unit(5), strAlternatingRowColor, "#000000", iAlign, VerticalAlign.NotSet, 1, BorderStyle.Solid, "", lnkValue))
                Else
                    lnkValue = GenerateTableLink(dtRow("KPI").ToString(), "#3333FF", dtRow("KPIType").ToString() & "~" & dtRow("KPIID").ToString, dtRow("KPIOther").ToString())
                    objRow.Cells.Add(GenerateTableCell(dtRow("KPI").ToString(), New Unit("14%"), New Unit(5), strAlternatingRowColor, "#000000", iAlign, VerticalAlign.NotSet, 1, BorderStyle.Solid, "", lnkValue))
                End If

                objRow.Cells.Add(GenerateTableCell(dtRow("UOM").ToString(), New Unit("5%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, dtRow("LegendToolTip").ToString()))

                For i = 1 To 3
                    objCell = New TableCell
                    objCell.Width = New Unit("2%")
                    objCell.Height = New Unit(15)
                    objCell.HorizontalAlign = HorizontalAlign.Center

                    If i = 2 AndAlso IsNumeric(dtRow("GroupReports").ToString) AndAlso Convert.ToInt32(dtRow("GroupReports").ToString) > 0 Then
                        objCell.BackColor = System.Drawing.ColorTranslator.FromHtml("#99CCFF")
                    Else
                        objCell.BackColor = System.Drawing.ColorTranslator.FromHtml(strAlternatingRowColor)
                    End If

                    objCell.BorderStyle = BorderStyle.Solid
                    objCell.Text = dtRow(i).ToString.Trim

                    objRow.Cells.Add(objCell)
                Next

                objCell = New TableCell
                objCell.Width = New Unit("3%")
                objCell.Height = New Unit(15)
                objCell.HorizontalAlign = HorizontalAlign.Center
                objCell.BackColor = System.Drawing.ColorTranslator.FromHtml(strAlternatingRowColor)
                objCell.BorderStyle = BorderStyle.Solid
                objCell.Text = dtRow("AreaAbbrev").ToString.Trim
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

                'Month Values
                For i As Integer = 15 To 26
                    objCell = New TableCell
                    objCell.Width = New Unit("4%")
                    objCell.Height = New Unit(15)
                    objCell.HorizontalAlign = HorizontalAlign.Center
                    objCell.BackColor = System.Drawing.ColorTranslator.FromHtml(strAlternatingRowColor)

                    objCell.BorderStyle = BorderStyle.Solid
                    If Not dtRow(i) Is DBNull.Value AndAlso IsNumeric(dtRow(i)) Then
                        objCell.Text = CDbl(dtRow(i)).ToString("0.##")
                    End If

                    ' Color Logic
                    If IsNumeric(dtRow(i).ToString) Then
                        If IsNumeric(dtRow(i).ToString) AndAlso IsNumeric(dtRow(i + 17).ToString) AndAlso IsNumeric(dtRow("Prev").ToString) Then
                            If bTargetUp Then
                                If CDbl(dtRow(i).ToString) >= CDbl(dtRow(i + 17).ToString) Then
                                    objCell.BackColor = Drawing.Color.LightGreen
                                    objCell.ToolTip = CDbl(dtRow(i + 17)).ToString("0.##")
                                ElseIf CDbl(dtRow(i).ToString) > CDbl(dtRow("Prev").ToString) Then
                                    objCell.BackColor = Drawing.Color.Yellow
                                    objCell.ToolTip = CDbl(dtRow("Prev")).ToString("0.##")
                                Else
                                    objCell.BackColor = Drawing.Color.Salmon
                                    objCell.ToolTip = CDbl(dtRow(i + 17)).ToString("0.##")
                                End If
                            Else
                                If CDbl(dtRow(i).ToString) <= CDbl(dtRow(i + 17).ToString) Then
                                    objCell.BackColor = Drawing.Color.LightGreen
                                    objCell.ToolTip = CDbl(dtRow(i + 17)).ToString("0.##")
                                ElseIf CDbl(dtRow(i).ToString) < CDbl(dtRow("Prev").ToString) Then
                                    objCell.BackColor = Drawing.Color.Yellow
                                    objCell.ToolTip = CDbl(dtRow("Prev")).ToString("0.##")
                                Else
                                    objCell.BackColor = Drawing.Color.Salmon
                                    objCell.ToolTip = CDbl(dtRow(i + 17)).ToString("0.##")
                                End If
                            End If
                        ElseIf IsNumeric(dtRow(i).ToString) AndAlso IsNumeric(dtRow(i + 17).ToString) Then
                            If bTargetUp Then
                                If CDbl(dtRow(i).ToString) >= CDbl(dtRow(i + 17).ToString) Then
                                    objCell.BackColor = Drawing.Color.LightGreen
                                    objCell.ToolTip = CDbl(dtRow(i + 17)).ToString("0.##")
                                Else
                                    objCell.BackColor = Drawing.Color.Salmon
                                    objCell.ToolTip = CDbl(dtRow(i + 17)).ToString("0.##")
                                End If
                            Else
                                If CDbl(dtRow(i).ToString) <= CDbl(dtRow(i + 17).ToString) Then
                                    objCell.BackColor = Drawing.Color.LightGreen
                                    objCell.ToolTip = CDbl(dtRow(i + 17)).ToString("0.##")
                                Else
                                    objCell.BackColor = Drawing.Color.Salmon
                                    objCell.ToolTip = CDbl(dtRow(i + 17)).ToString("0.##")
                                End If
                            End If
                        ElseIf IsNumeric(dtRow(i).ToString) AndAlso IsNumeric(dtRow("Prev").ToString) Then
                            If bTargetUp Then
                                If CDbl(dtRow(i).ToString) > CDbl(dtRow("Prev").ToString) Then
                                    objCell.BackColor = Drawing.Color.Yellow
                                    objCell.ToolTip = CDbl(dtRow("Prev")).ToString("0.##")
                                Else
                                    objCell.BackColor = Drawing.Color.Salmon
                                    objCell.ToolTip = CDbl(dtRow("Prev")).ToString("0.##")
                                End If
                            Else
                                If CDbl(dtRow(i).ToString) < CDbl(dtRow("Prev").ToString) Then
                                    objCell.BackColor = Drawing.Color.Yellow
                                    objCell.ToolTip = CDbl(dtRow("Prev")).ToString("0.##")
                                Else
                                    objCell.BackColor = Drawing.Color.Salmon
                                    objCell.ToolTip = CDbl(dtRow("Prev")).ToString("0.##")
                                End If
                            End If
                        End If
                    End If

                    objRow.Cells.Add(objCell)
                Next

                ' YTD
                objCell = New TableCell
                objCell.Width = New Unit("4%")
                objCell.Height = New Unit(15)
                objCell.HorizontalAlign = HorizontalAlign.Center
                objCell.BackColor = System.Drawing.ColorTranslator.FromHtml(strAlternatingRowColor)
                objCell.BorderStyle = BorderStyle.Solid
                If Not dtRow("YTD") Is DBNull.Value AndAlso IsNumeric(dtRow("YTD")) Then
                    objCell.Text = CDbl(dtRow("YTD")).ToString("0.##")
                End If
                objRow.Cells.Add(objCell)

                If IsNumeric(dtRow("YTD").ToString) Then
                    If IsNumeric(dtRow("YTD").ToString) AndAlso IsNumeric(dtRow("YTDT").ToString) AndAlso IsNumeric(dtRow("Prev").ToString) Then
                        If bTargetUp Then
                            If CDbl(dtRow("YTD").ToString) >= CDbl(dtRow("YTDT").ToString) Then
                                objCell.BackColor = Drawing.Color.LightGreen
                            ElseIf CDbl(dtRow("YTD").ToString) > CDbl(dtRow("Prev").ToString) Then
                                objCell.BackColor = Drawing.Color.Yellow
                            Else
                                objCell.BackColor = Drawing.Color.Salmon
                            End If
                        Else
                            If CDbl(dtRow("YTD").ToString) <= CDbl(dtRow("YTDT").ToString) Then
                                objCell.BackColor = Drawing.Color.LightGreen
                            ElseIf CDbl(dtRow("YTD").ToString) < CDbl(dtRow("Prev").ToString) Then
                                objCell.BackColor = Drawing.Color.Yellow
                            Else
                                objCell.BackColor = Drawing.Color.Salmon
                            End If
                        End If
                    ElseIf IsNumeric(dtRow("YTD").ToString) AndAlso IsNumeric(dtRow("YTDT").ToString) Then
                        If bTargetUp Then
                            If CDbl(dtRow("YTD").ToString) >= CDbl(dtRow("YTDT").ToString) Then
                                objCell.BackColor = Drawing.Color.LightGreen
                            Else
                                objCell.BackColor = Drawing.Color.Salmon
                            End If
                        Else
                            If CDbl(dtRow("YTD").ToString) <= CDbl(dtRow("YTDT").ToString) Then
                                objCell.BackColor = Drawing.Color.LightGreen
                            Else
                                objCell.BackColor = Drawing.Color.Salmon
                            End If
                        End If
                    ElseIf IsNumeric(dtRow("YTD").ToString) AndAlso IsNumeric(dtRow("Prev").ToString) Then
                        If bTargetUp Then
                            If CDbl(dtRow("YTD").ToString) > CDbl(dtRow("Prev").ToString) Then
                                objCell.BackColor = Drawing.Color.Yellow
                            Else
                                objCell.BackColor = Drawing.Color.Salmon
                            End If
                        Else
                            If CDbl(dtRow("YTD").ToString) < CDbl(dtRow("Prev").ToString) Then
                                objCell.BackColor = Drawing.Color.Yellow
                            Else
                                objCell.BackColor = Drawing.Color.Salmon
                            End If
                        End If
                    End If
                End If

                ' Target
                objCell = New TableCell
                objCell.Width = New Unit("4%")
                objCell.Height = New Unit(15)
                objCell.HorizontalAlign = HorizontalAlign.Center
                objCell.BackColor = System.Drawing.ColorTranslator.FromHtml(strAlternatingRowColor)
                objCell.BorderStyle = BorderStyle.Solid
                If Not dtRow("YTDT") Is DBNull.Value AndAlso IsNumeric(dtRow("YTDT")) Then
                    objCell.Text = CDbl(dtRow("YTDT")).ToString("0.##")
                End If
                objRow.Cells.Add(objCell)

                tblKPIValues.Rows.Add(objRow)
            Next

            ViewState("KPIList") = htKPI
        End Sub
        Private Sub LoadQuarterGrid(ByVal objDT As DataTable)
            Dim objRow As TableRow
            Dim objCell As TableCell
            Dim lnkValue As LinkButton = Nothing

            If objDT Is Nothing OrElse objDT.Rows.Count = 0 Then
                objRow = New TableRow
                objRow.Cells.Add(GenerateTableCell("No Records Exist for current filter", New Unit("100%"), New Unit(15), "#FFFFFF", "Red", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.None, "No Records"))
                tblKPIValues.Rows.Add(objRow)

                Return
            End If

            'add top for year and nav buttons
            objRow = New TableRow
            objRow.Cells.Add(GenerateTableCell("", New Unit("14%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.None, "", GenerateTableLink("<", "#E7E7FF", "Nav~" & (SessionManager.KPISelNavYear - 1).ToString, "Previous Year")))
            objRow.Cells.Add(GenerateTableCell(SessionManager.KPISelNavYear.ToString, New Unit((0).ToString & "%"), New Unit(0), "#41519A", "#ffffff", HorizontalAlign.Center, VerticalAlign.NotSet, 11, BorderStyle.None, ""))
            objRow.Cells.Add(GenerateTableCell("", New Unit("4%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.None, "", GenerateTableLink(">", "#E7E7FF", "Nav~" & (SessionManager.KPISelNavYear + 1).ToString, "Next Year")))
            tblKPIValues.Rows.Add(objRow)

            'add Month columns
            'add header columns
            objRow = New TableRow
            objRow.Cells.Add(GenerateTableCell("", New Unit("14%"), New Unit(15), "#FFFFFF", "#FFFFFF", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.Solid, ""))

            objRow.Cells.Add(GenerateTableCell("UOM", New Unit("5%"), New Unit(15), "#FFFFFF", "#000000", HorizontalAlign.Center, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("PIL", New Unit("2%"), New Unit(15), "#FFFFFF", "#000000", HorizontalAlign.Center, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("BA", New Unit("2%"), New Unit(15), "#FFFFFF", "#000000", HorizontalAlign.Center, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("BU", New Unit("2%"), New Unit(15), "#FFFFFF", "#000000", HorizontalAlign.Center, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Area", New Unit("3%"), New Unit(15), "#FFFFFF", "#000000", HorizontalAlign.Center, VerticalAlign.Top, 1, BorderStyle.Solid, ""))

            objRow.Cells.Add(GenerateTableCell(objDT.Columns(12).ColumnName, New Unit("4%"), New Unit(15), "#FFFFFF", "#000000", HorizontalAlign.Center, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            For i As Integer = 27 To 31
                objRow.Cells.Add(GenerateTableCell(objDT.Columns(i).ColumnName, New Unit("4%"), New Unit(15), "#FFFFFF", "#000000", HorizontalAlign.Center, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            Next
            objRow.Cells.Add(GenerateTableCell("Target", New Unit("4%"), New Unit(15), "#FFFFFF", "#000000", HorizontalAlign.Center, VerticalAlign.Top, 1, BorderStyle.Solid, ""))

            tblKPIValues.Rows.Add(objRow)

            Dim strCatDisplay As String = ""
            Dim strCategoryDisplayName As String = ""
            Dim intRowIndex As Integer = 0
            Dim strAlternatingRowColor As String
            Dim bTargetUp As Boolean = False
            Dim iAlign As Integer = HorizontalAlign.Left

            Dim bEnglish As Boolean = (New System.Globalization.CultureInfo(SessionManager.CulturePref).TwoLetterISOLanguageName.ToUpper = "EN")
            htKPI = New Hashtable()
            For Each dtRow As DataRow In objDT.Rows
                If Not htKPI.ContainsKey(dtRow("KPIID").ToString) Then
                    htKPI.Add(dtRow("KPIID").ToString, dtRow("KPIID").ToString)
                End If
                bTargetUp = Convert.ToBoolean(dtRow("TargetUp"))

                intRowIndex += 1
                'values for this year
                objRow = New TableRow

                strCatDisplay = dtRow("Site").ToString.Trim & " : " & dtRow("TeamCategory").ToString.Trim

                If strCategoryDisplayName <> strCatDisplay Then
                    tblKPIValues.Rows.Add(GenerateTableRow(strCatDisplay, "#CCCCCC", "#000000", HorizontalAlign.Left, BorderStyle.None, 13, True))
                    strCategoryDisplayName = strCatDisplay
                End If

                strAlternatingRowColor = "#FFFFFF"

                If IsNumeric(dtRow("PrimaryKPIID").ToString) Then
                    iAlign = HorizontalAlign.Right
                Else
                    iAlign = HorizontalAlign.Left
                End If

                If bEnglish Then
                    lnkValue = GenerateTableLink(dtRow("KPIOther").ToString(), "#3333FF", dtRow("KPIType").ToString() & "~" & dtRow("KPIID").ToString, dtRow("KPI").ToString())
                    objRow.Cells.Add(GenerateTableCell(dtRow("KPIOther").ToString(), New Unit("14%"), New Unit(5), strAlternatingRowColor, "#000000", iAlign, VerticalAlign.NotSet, 1, BorderStyle.Solid, "", lnkValue))
                Else
                    lnkValue = GenerateTableLink(dtRow("KPI").ToString(), "#3333FF", dtRow("KPIType").ToString() & "~" & dtRow("KPIID").ToString, dtRow("KPIOther").ToString())
                    objRow.Cells.Add(GenerateTableCell(dtRow("KPI").ToString(), New Unit("14%"), New Unit(5), strAlternatingRowColor, "#000000", iAlign, VerticalAlign.NotSet, 1, BorderStyle.Solid, "", lnkValue))
                End If

                objRow.Cells.Add(GenerateTableCell(dtRow("UOM").ToString(), New Unit("5%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, dtRow("LegendToolTip").ToString()))

                For i = 1 To 3
                    objCell = New TableCell
                    objCell.Width = New Unit("2%")
                    objCell.Height = New Unit(15)
                    objCell.HorizontalAlign = HorizontalAlign.Center

                    If i = 2 AndAlso IsNumeric(dtRow("GroupReports").ToString) AndAlso Convert.ToInt32(dtRow("GroupReports").ToString) > 0 Then
                        objCell.BackColor = System.Drawing.ColorTranslator.FromHtml("#99CCFF")
                    Else
                        objCell.BackColor = System.Drawing.ColorTranslator.FromHtml(strAlternatingRowColor)
                    End If

                    objCell.BorderStyle = BorderStyle.Solid
                    objCell.Text = dtRow(i).ToString.Trim

                    objRow.Cells.Add(objCell)
                Next

                objCell = New TableCell
                objCell.Width = New Unit("3%")
                objCell.Height = New Unit(15)
                objCell.HorizontalAlign = HorizontalAlign.Center
                objCell.BackColor = System.Drawing.ColorTranslator.FromHtml(strAlternatingRowColor)
                objCell.BorderStyle = BorderStyle.Solid
                objCell.Text = dtRow("AreaAbbrev").ToString.Trim
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

                'Quarter Values
                For i As Integer = 27 To 30
                    objCell = New TableCell
                    objCell.Width = New Unit("4%")
                    objCell.Height = New Unit(15)
                    objCell.HorizontalAlign = HorizontalAlign.Center
                    objCell.BackColor = System.Drawing.ColorTranslator.FromHtml(strAlternatingRowColor)

                    objCell.BorderStyle = BorderStyle.Solid
                    If Not dtRow(i) Is DBNull.Value AndAlso IsNumeric(dtRow(i)) Then
                        objCell.Text = CDbl(dtRow(i)).ToString("0.##")
                    End If

                    ' Color Logic
                    If IsNumeric(dtRow(i).ToString) Then
                        If IsNumeric(dtRow(i).ToString) AndAlso IsNumeric(dtRow(i + 17).ToString) AndAlso IsNumeric(dtRow("Prev").ToString) Then
                            If bTargetUp Then
                                If CDbl(dtRow(i).ToString) >= CDbl(dtRow(i + 17).ToString) Then
                                    objCell.BackColor = Drawing.Color.LightGreen
                                    objCell.ToolTip = CDbl(dtRow(i + 17)).ToString("0.##")
                                ElseIf CDbl(dtRow(i).ToString) > CDbl(dtRow("Prev").ToString) Then
                                    objCell.BackColor = Drawing.Color.Yellow
                                    objCell.ToolTip = CDbl(dtRow("Prev")).ToString("0.##")
                                Else
                                    objCell.BackColor = Drawing.Color.Salmon
                                    objCell.ToolTip = CDbl(dtRow(i + 17)).ToString("0.##")
                                End If
                            Else
                                If CDbl(dtRow(i).ToString) <= CDbl(dtRow(i + 17).ToString) Then
                                    objCell.BackColor = Drawing.Color.LightGreen
                                    objCell.ToolTip = CDbl(dtRow(i + 17)).ToString("0.##")
                                ElseIf CDbl(dtRow(i).ToString) < CDbl(dtRow("Prev").ToString) Then
                                    objCell.BackColor = Drawing.Color.Yellow
                                    objCell.ToolTip = CDbl(dtRow("Prev")).ToString("0.##")
                                Else
                                    objCell.BackColor = Drawing.Color.Salmon
                                    objCell.ToolTip = CDbl(dtRow(i + 17)).ToString("0.##")
                                End If
                            End If
                        ElseIf IsNumeric(dtRow(i).ToString) AndAlso IsNumeric(dtRow(i + 17).ToString) Then
                            If bTargetUp Then
                                If CDbl(dtRow(i).ToString) >= CDbl(dtRow(i + 17).ToString) Then
                                    objCell.BackColor = Drawing.Color.LightGreen
                                    objCell.ToolTip = CDbl(dtRow(i + 17)).ToString("0.##")
                                Else
                                    objCell.BackColor = Drawing.Color.Salmon
                                    objCell.ToolTip = CDbl(dtRow(i + 17)).ToString("0.##")
                                End If
                            Else
                                If CDbl(dtRow(i).ToString) <= CDbl(dtRow(i + 17).ToString) Then
                                    objCell.BackColor = Drawing.Color.LightGreen
                                    objCell.ToolTip = CDbl(dtRow(i + 17)).ToString("0.##")
                                Else
                                    objCell.BackColor = Drawing.Color.Salmon
                                    objCell.ToolTip = CDbl(dtRow(i + 17)).ToString("0.##")
                                End If
                            End If
                        ElseIf IsNumeric(dtRow(i).ToString) AndAlso IsNumeric(dtRow("Prev").ToString) Then
                            If bTargetUp Then
                                If CDbl(dtRow(i).ToString) > CDbl(dtRow("Prev").ToString) Then
                                    objCell.BackColor = Drawing.Color.Yellow
                                    objCell.ToolTip = CDbl(dtRow("Prev")).ToString("0.##")
                                Else
                                    objCell.BackColor = Drawing.Color.Salmon
                                    objCell.ToolTip = CDbl(dtRow("Prev")).ToString("0.##")
                                End If
                            Else
                                If CDbl(dtRow(i).ToString) < CDbl(dtRow("Prev").ToString) Then
                                    objCell.BackColor = Drawing.Color.Yellow
                                    objCell.ToolTip = CDbl(dtRow("Prev")).ToString("0.##")
                                Else
                                    objCell.BackColor = Drawing.Color.Salmon
                                    objCell.ToolTip = CDbl(dtRow("Prev")).ToString("0.##")
                                End If
                            End If
                        End If
                    End If

                    objRow.Cells.Add(objCell)
                Next

                ' YTD
                objCell = New TableCell
                objCell.Width = New Unit("4%")
                objCell.Height = New Unit(15)
                objCell.HorizontalAlign = HorizontalAlign.Center
                objCell.BackColor = System.Drawing.ColorTranslator.FromHtml(strAlternatingRowColor)
                objCell.BorderStyle = BorderStyle.Solid
                If Not dtRow("YTD") Is DBNull.Value AndAlso IsNumeric(dtRow("YTD")) Then
                    objCell.Text = CDbl(dtRow("YTD")).ToString("0.##")
                End If
                objRow.Cells.Add(objCell)

                If IsNumeric(dtRow("YTD").ToString) Then
                    If IsNumeric(dtRow("YTD").ToString) AndAlso IsNumeric(dtRow("YTDT").ToString) AndAlso IsNumeric(dtRow("Prev").ToString) Then
                        If bTargetUp Then
                            If CDbl(dtRow("YTD").ToString) >= CDbl(dtRow("YTDT").ToString) Then
                                objCell.BackColor = Drawing.Color.LightGreen
                            ElseIf CDbl(dtRow("YTD").ToString) > CDbl(dtRow("Prev").ToString) Then
                                objCell.BackColor = Drawing.Color.Yellow
                            Else
                                objCell.BackColor = Drawing.Color.Salmon
                            End If
                        Else
                            If CDbl(dtRow("YTD").ToString) <= CDbl(dtRow("YTDT").ToString) Then
                                objCell.BackColor = Drawing.Color.LightGreen
                            ElseIf CDbl(dtRow("YTD").ToString) < CDbl(dtRow("Prev").ToString) Then
                                objCell.BackColor = Drawing.Color.Yellow
                            Else
                                objCell.BackColor = Drawing.Color.Salmon
                            End If
                        End If
                    ElseIf IsNumeric(dtRow("YTD").ToString) AndAlso IsNumeric(dtRow("YTDT").ToString) Then
                        If bTargetUp Then
                            If CDbl(dtRow("YTD").ToString) >= CDbl(dtRow("YTDT").ToString) Then
                                objCell.BackColor = Drawing.Color.LightGreen
                            Else
                                objCell.BackColor = Drawing.Color.Salmon
                            End If
                        Else
                            If CDbl(dtRow("YTD").ToString) <= CDbl(dtRow("YTDT").ToString) Then
                                objCell.BackColor = Drawing.Color.LightGreen
                            Else
                                objCell.BackColor = Drawing.Color.Salmon
                            End If
                        End If
                    ElseIf IsNumeric(dtRow("YTD").ToString) AndAlso IsNumeric(dtRow("Prev").ToString) Then
                        If bTargetUp Then
                            If CDbl(dtRow("YTD").ToString) > CDbl(dtRow("Prev").ToString) Then
                                objCell.BackColor = Drawing.Color.Yellow
                            Else
                                objCell.BackColor = Drawing.Color.Salmon
                            End If
                        Else
                            If CDbl(dtRow("YTD").ToString) < CDbl(dtRow("Prev").ToString) Then
                                objCell.BackColor = Drawing.Color.Yellow
                            Else
                                objCell.BackColor = Drawing.Color.Salmon
                            End If
                        End If
                    End If
                End If

                ' Target
                objCell = New TableCell
                objCell.Width = New Unit("4%")
                objCell.Height = New Unit(15)
                objCell.HorizontalAlign = HorizontalAlign.Center
                objCell.BackColor = System.Drawing.ColorTranslator.FromHtml(strAlternatingRowColor)
                objCell.BorderStyle = BorderStyle.Solid
                If Not dtRow("YTDT") Is DBNull.Value AndAlso IsNumeric(dtRow("YTDT")) Then
                    objCell.Text = CDbl(dtRow("YTDT")).ToString("0.##")
                End If
                objRow.Cells.Add(objCell)

                tblKPIValues.Rows.Add(objRow)
            Next

            ViewState("KPIList") = htKPI
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
