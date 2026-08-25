#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class MyTrackers
        Inherits ApplicationBase

#Region " Constants"
        Private Shared ReadOnly FormName As String = "My Savings Trackers"
        Private Shared ReadOnly ProgramName As String = "MyTrackers"
        Private dvTrackers As DataView = Nothing
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
                lblSite.Text = GetTranslationString("site", lblSite.Text.Replace(":", "")) & ":"
                lblPillar.Text = GetTranslationString("pillar", lblPillar.Text.Replace(":", "")) & ":"
                lblBA.Text = GetTranslationString("businessarea", lblBA.Text.Replace(":", "")) & ":"
                lblBU.Text = GetTranslationString("businessunit", lblBU.Text.Replace(":", "")) & ":"
                lblCategory.Text = GetTranslationString("category", lblCategory.Text.Replace(":", "")) & ":"
                lblSavingsType.Text = GetTranslationString("savingstype", lblSavingsType.Text.Replace(":", "")) & ":"
                btnExit.Text = GetTranslationString("exit", btnExit.Text)
                btnExport.Text = GetTranslationString("export", btnExport.Text)
                btnApplyFilter.Text = GetTranslationString("applyfilter", btnApplyFilter.Text)
                btnClearFilter.Text = GetTranslationString("clearfilter", btnClearFilter.Text)
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

            Master.IconImage = Request.ApplicationPath & "/images/usergroup.gif"
            Master.HeaderMessage = GetTranslationString(FormName, FormName)
            Master.ProgramName = ProgramName
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnExit.UniqueID + "'),window.event)")
            btnExport.Attributes.Add("onclick", "DisableWaitPanel()")

            If Not Page.IsPostBack Then
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

            BindGrid(False)
            Master.MasterScriptManager.RegisterPostBackControl(btnExport)
        End Sub
        Private Sub ButtonClick(ByVal passArgs As String)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim strTarget() As String
            strTarget = passArgs.Split("~")
            Dim strProgram As String = ""

            If strTarget(1) = "Sort" Then
                SessionManager.OverviewSortColumn = strTarget(2) & "~" & strTarget(3)
                BindGrid(True)
            Else
                If strTarget(2) <> SessionManager.SelectedTeamID.ToString Then
                    PushTeamOntoStack(SessionManager.SelectedTeamID, SessionManager.SelectedTeam, SessionManager.SelectedOPI, "MyTrackers", SessionManager.CurrentMenuProgram)
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

                If strTarget(1) = "Team" Then
                    SessionManager.CurrentMenuProgram = "TeamBoardMenu"
                    strProgram = "TeamBoardMenu"
                ElseIf strTarget(1) = "Tracker" Then
                    SessionManager.SelectedValueTrackerID = strTarget(4)
                    SessionManager.CallingProgram = "MyTrackers"
                    strProgram = "SavingsTracker1"
                End If

                LastPixelPositionUpdate(ProgramName, Master.CurrentPixelPosition)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strProgram), False)
            End If
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.OverviewSortColumn)
            RemoveCurrentProgramandGoBack()
        End Sub
        Protected Sub btnExport_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnExport.Click
            Dim stringWrite As New System.IO.StringWriter
            Dim htmlWrite As New System.Web.UI.HtmlTextWriter(stringWrite)
            Dim dg As New DataGrid

            BindGrid(False)

            dg.DataSource = dvTrackers
            dg.DataBind()

            dg.RenderControl(htmlWrite)

            SessionManager.ExportString = stringWrite.ToString

            HttpContext.Current.Response.Redirect(HttpContext.Current.Request.ApplicationPath.ToString + "/UI/UserControls/Export.aspx")
        End Sub
        Protected Sub btnApplyFilter_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnApplyFilter.Click
            Dim cookie As New HttpCookie("MyTrackersFilter")
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

            If ddlSavingsCategory.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlSavingsCategory.SelectedItem.Value) Then
                cookie.Values("SavingsCategoryID") = ddlSavingsCategory.SelectedItem.Value.ToString
            Else
                cookie.Values.Remove("SavingsCategoryID")
            End If

            If ddlSavingsType.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlSavingsType.SelectedItem.Value) Then
                cookie.Values("SavingsTypeID") = ddlSavingsType.SelectedItem.Value.ToString
            Else
                cookie.Values.Remove("SavingsTypeID")
            End If

            Response.Cookies.Add(cookie)

            BindGrid(False)
        End Sub
        Protected Sub btnClearFilter_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnClearFilter.Click
            Response.Cookies("MyTrackersFilter").Expires = Now

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("MyTrackers"), False)
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

                SavingsCategoryMaster.GetSavingsCategoryList(ddlSavingsCategory)
                ddlSavingsCategory.Items.Insert(0, "")

                SavingsTypeMaster.GetSavingsTypeList(ddlSavingsType)
            Catch ex As Exception

            End Try
        End Sub
        Private Sub ApplyFiltersFromCookie()
            Dim objItem As ListItem

            If Request.Cookies("MyTrackersFilter") IsNot Nothing Then
                Dim cookie As HttpCookie = Request.Cookies("MyTrackersFilter")

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

                If cookie.Values("SavingsCategoryID") IsNot Nothing AndAlso IsNumeric(cookie.Values("SavingsCategoryID")) Then
                    objItem = ddlSavingsCategory.Items.FindByValue(cookie.Values("SavingsCategoryID"))
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

                If cookie.Values("SavingsTypeID") IsNot Nothing AndAlso IsNumeric(cookie.Values("SavingsTypeID")) Then
                    objItem = ddlSavingsType.Items.FindByValue(cookie.Values("SavingsTypeID"))
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                    End If
                End If
                If ddlSavingsType.SelectedItem Is Nothing Then
                    ddlSavingsType.Items(0).Selected = True
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
        Private Sub BindGrid(ByVal bSort As Boolean)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim strSortColumn As String = ""
                Dim strSortOrder As String = ""

                tblTrackers.Rows.Clear()

                If SessionManager.OverviewSortColumn <> "" Then
                    If SessionManager.OverviewSortColumn.ToString.Trim.Length > 0 Then
                        Dim strSort() As String = SessionManager.OverviewSortColumn.ToString.Split("~")
                        Dim strSortCols() As String = strSort(0).Split("|")

                        For iCol As Integer = 0 To strSortCols.Length - 1
                            If strSortColumn.Trim.Length > 0 Then strSortColumn += ", "

                            strSortColumn += strSortCols(iCol)
                        Next

                        'strSortColumn = strSort(0)
                        strSortOrder = strSort(1)
                        If strSortOrder = "" Then
                            strSortOrder = "DESC"
                        End If

                        If bSort = True Then
                            If strSortOrder.ToUpper = "ASC" Then
                                strSortOrder = "DESC"
                            Else
                                strSortOrder = "ASC"
                            End If

                            SessionManager.OverviewSortColumn = strSortColumn & "~" & strSortOrder
                        End If
                    End If
                End If

                Dim iSiteID As Integer = 0
                Dim strPillarAbbrev As String = ""
                Dim iBusinessUnitID As Integer = -1
                Dim iBusinessAreaID As Integer = -1
                Dim iSavingsCategoryID As Integer = -1
                Dim iSavingsTypeID As Integer = 1

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
                If ddlSavingsCategory.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlSavingsCategory.SelectedItem.Value.ToString) Then
                    iSavingsCategoryID = ddlSavingsCategory.SelectedItem.Value
                End If
                If ddlSavingsType.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlSavingsType.SelectedItem.Value.ToString) Then
                    iSavingsTypeID = ddlSavingsType.SelectedItem.Value
                End If

                mcTrackerTotals.StoredProcedureParams.Clear()
                mcTrackerTypeTotals.StoredProcedureParams.Clear()

                mcTrackerTotals.StoredProcedureParams.Add("@UserID", SessionManager.UserID)
                mcTrackerTypeTotals.StoredProcedureParams.Add("@UserID", SessionManager.UserID)
                If iSiteID > 0 Then
                    mcTrackerTotals.StoredProcedureParams.Add("@SiteID", iSiteID)
                    mcTrackerTypeTotals.StoredProcedureParams.Add("@SiteID", iSiteID)
                End If
                If strPillarAbbrev.Trim.Length > 0 Then
                    mcTrackerTotals.StoredProcedureParams.Add("@PillarAbbrev", strPillarAbbrev)
                    mcTrackerTypeTotals.StoredProcedureParams.Add("@PillarAbbrev", strPillarAbbrev)
                End If
                If iBusinessUnitID > 0 Then
                    mcTrackerTotals.StoredProcedureParams.Add("@BusinessUnitID", iBusinessUnitID)
                    mcTrackerTypeTotals.StoredProcedureParams.Add("@BusinessUnitID", iBusinessUnitID)
                End If
                If iBusinessAreaID > 0 Then
                    mcTrackerTotals.StoredProcedureParams.Add("@BusinessAreaID", iBusinessAreaID)
                    mcTrackerTypeTotals.StoredProcedureParams.Add("@BusinessAreaID", iBusinessAreaID)
                End If
                If iSavingsCategoryID > 0 Then
                    mcTrackerTotals.StoredProcedureParams.Add("@SavingsCategoryID", iSavingsCategoryID)
                    mcTrackerTypeTotals.StoredProcedureParams.Add("@SavingsCategoryID", iSavingsCategoryID)
                End If
                mcTrackerTotals.StoredProcedureParams.Add("@SavingsTypeID", iSavingsTypeID)
                mcTrackerTypeTotals.StoredProcedureParams.Add("@SavingsTypeID", iSavingsTypeID)

                mcTrackerTotals.DataBind(True)
                mcTrackerTypeTotals.DataBind(True)

                Dim objDT As DataTable = Trackers.SelectMyTrackers(SessionManager.UserID, iSiteID, strPillarAbbrev, iBusinessUnitID, iBusinessAreaID, iSavingsCategoryID, iSavingsTypeID)
                dvTrackers = objDT.DefaultView
                Dim objRow As TableRow
                Dim objCell As TableCell
                Dim objLink As LinkButton

                If dvTrackers.Count > 0 Then
                    pnlNoData.Visible = False

                    If strSortColumn.Trim.Length > 0 AndAlso strSortOrder.Trim.Length > 0 Then
                        dvTrackers.Sort = strSortColumn & " " & strSortOrder
                    End If

                    'create header
                    objRow = New TableRow

                    'fill in the cells
                    'Team
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objLink = New LinkButton
                    objLink.CssClass = "Table_Teams3_Header"
                    objLink.Text = GetTranslationString("team", "Team")
                    objLink.ID = "PageLink~Sort~Team|SiteAbbrev" & "~"
                    If strSortColumn = "Team|SiteAbbrev" Then
                        objLink.ID += strSortOrder
                    End If
                    objLink.Font.Bold = True
                    objLink.CommandArgument = objLink.ID
                    objCell.Controls.Add(objLink)
                    objRow.Cells.Add(objCell)

                    'Team Name
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objLink = New LinkButton
                    objLink.CssClass = "Table_Teams3_Header"
                    objLink.Text = GetTranslationString("teamname", "Team Name")
                    objLink.ID = "PageLink~Sort~TeamName|SiteAbbrev" & "~"
                    If strSortColumn = "TeamName|SiteAbbrev" Then
                        objLink.ID += strSortOrder
                    End If
                    objLink.CommandArgument = objLink.ID
                    objCell.Controls.Add(objLink)
                    objRow.Cells.Add(objCell)

                    'Tracker
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objLink = New LinkButton
                    objLink.CssClass = "Table_Teams3_Header"
                    objLink.Text = GetTranslationString("savingstracker", "Savings Tracker")
                    objLink.ID = "PageLink~Sort~Tracker" & "~"
                    If strSortColumn = "Tracker" Then
                        objLink.ID += strSortOrder
                    End If
                    objLink.CommandArgument = objLink.ID
                    objCell.Controls.Add(objLink)
                    objRow.Cells.Add(objCell)

                    'Site
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objLink = New LinkButton
                    objLink.CssClass = "Table_Teams3_Header"
                    objLink.Text = GetTranslationString("site", "Site")
                    objLink.ID = "PageLink~Sort~SiteAbbrev|Team" & "~"
                    If strSortColumn = "SiteAbbrev|Team" Then
                        objLink.ID += strSortOrder
                    End If
                    objLink.CommandArgument = objLink.ID
                    objCell.Controls.Add(objLink)
                    objRow.Cells.Add(objCell)

                    'Pillar
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objLink = New LinkButton
                    objLink.CssClass = "Table_Teams3_Header"
                    objLink.Text = GetTranslationString("pillarabbrev", "PIL")
                    objLink.ID = "PageLink~Sort~PillarAbbrev|Team" & "~"
                    If strSortColumn = "PillarAbbrev|Team" Then
                        objLink.ID += strSortOrder
                    End If
                    objLink.CommandArgument = objLink.ID
                    objCell.Controls.Add(objLink)
                    objRow.Cells.Add(objCell)

                    'Bus Area
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objLink = New LinkButton
                    objLink.CssClass = "Table_Teams3_Header"
                    objLink.Text = GetTranslationString("businessareaabbrev", "BA")
                    objLink.ID = "PageLink~Sort~BusinessAreaAbbrev|Team" & "~"
                    If strSortColumn = "BusinessAreaAbbrev|Team" Then
                        objLink.ID += strSortOrder
                    End If
                    objLink.CommandArgument = objLink.ID
                    objCell.Controls.Add(objLink)
                    objRow.Cells.Add(objCell)

                    'Business Unit
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objLink = New LinkButton
                    objLink.CssClass = "Table_Teams3_Header"
                    objLink.Text = GetTranslationString("businessunitabbrev", "BU")
                    objLink.ID = "PageLink~Sort~BusinessUnitAbbrev|Team" & "~"
                    If strSortColumn = "BusinessUnitAbbrev|Team" Then
                        objLink.ID += strSortOrder
                    End If
                    objLink.CommandArgument = objLink.ID
                    objCell.Controls.Add(objLink)
                    objRow.Cells.Add(objCell)

                    'UOM
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objLink = New LinkButton
                    objLink.CssClass = "Table_Teams3_Header"
                    objLink.Text = GetTranslationString("uom", "UOM")
                    objLink.ID = "PageLink~Sort~TrackerValueUOM|Tracker" & "~"
                    If strSortColumn = "TrackerValueUOM|Tracker" Then
                        objLink.ID += strSortOrder
                    End If
                    objLink.CommandArgument = objLink.ID
                    objCell.Controls.Add(objLink)
                    objRow.Cells.Add(objCell)

                    'Start
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objLink = New LinkButton
                    objLink.CssClass = "Table_Teams3_Header"
                    objLink.Text = GetTranslationString("start", "Start")
                    objLink.ID = "PageLink~Sort~StartPeriod|Tracker" & "~"
                    If strSortColumn = "StartPeriod|Tracker" Then
                        objLink.ID += strSortOrder
                    End If
                    objLink.CommandArgument = objLink.ID
                    objCell.Controls.Add(objLink)
                    objRow.Cells.Add(objCell)

                    'Last Value
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objLink = New LinkButton
                    objLink.CssClass = "Table_Teams3_Header"
                    objLink.Text = GetTranslationString("lastvalue", "Last Value")
                    objLink.ID = "PageLink~Sort~LastValueDate" & "~"
                    If strSortColumn = "LastValueDate" Then
                        objLink.ID += strSortOrder
                    End If
                    objLink.CommandArgument = objLink.ID
                    objCell.Controls.Add(objLink)
                    objRow.Cells.Add(objCell)

                    'Currency
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objLink = New LinkButton
                    objLink.CssClass = "Table_Teams3_Header"
                    objLink.Text = GetTranslationString("currencyabbrev", "Cur")
                    objLink.ID = "PageLink~Sort~CurrencyAbbrev" & "~"
                    If strSortColumn = "CurrencyAbbrev" Then
                        objLink.ID += strSortOrder
                    End If
                    objLink.CommandArgument = objLink.ID
                    objCell.Controls.Add(objLink)
                    objRow.Cells.Add(objCell)

                    'Previous Year
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objCell.HorizontalAlign = HorizontalAlign.Right
                    objLink = New LinkButton
                    objLink.CssClass = "Table_Teams3_Header"
                    objLink.Text = GetTranslationString("previousyear", "Prev Year")
                    objLink.ID = "PageLink~Sort~PreviousYearSavings" & "~"
                    If strSortColumn = "PreviousYearSavings" Then
                        objLink.ID += strSortOrder
                    End If
                    objLink.CommandArgument = objLink.ID
                    objCell.Controls.Add(objLink)
                    objRow.Cells.Add(objCell)

                    'Last Year
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objCell.HorizontalAlign = HorizontalAlign.Right
                    objLink = New LinkButton
                    objLink.CssClass = "Table_Teams3_Header"
                    objLink.Text = GetTranslationString("lastyear", "Last Year")
                    objLink.ID = "PageLink~Sort~LastYearSavings" & "~"
                    If strSortColumn = "LastYearSavings" Then
                        objLink.ID += strSortOrder
                    End If
                    objLink.CommandArgument = objLink.ID
                    objCell.Controls.Add(objLink)
                    objRow.Cells.Add(objCell)

                    'Current Year
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objCell.HorizontalAlign = HorizontalAlign.Right
                    objLink = New LinkButton
                    objLink.CssClass = "Table_Teams3_Header"
                    objLink.Text = GetTranslationString("currentyear", "Current Year")
                    objLink.ID = "PageLink~Sort~YearSavings" & "~"
                    If strSortColumn = "YearSavings" Then
                        objLink.ID += strSortOrder
                    End If
                    objLink.CommandArgument = objLink.ID
                    objCell.Controls.Add(objLink)
                    objRow.Cells.Add(objCell)

                    'Last Month
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objCell.HorizontalAlign = HorizontalAlign.Right
                    objLink = New LinkButton
                    objLink.CssClass = "Table_Teams3_Header"
                    objLink.Text = GetTranslationString("lastmonth", "Last Month")
                    objLink.ID = "PageLink~Sort~LastMonthSavings" & "~"
                    If strSortColumn = "LastMonthSavings" Then
                        objLink.ID += strSortOrder
                    End If
                    objLink.CommandArgument = objLink.ID
                    objCell.Controls.Add(objLink)
                    objRow.Cells.Add(objCell)

                    'Total
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objCell.HorizontalAlign = HorizontalAlign.Right
                    objLink = New LinkButton
                    objLink.CssClass = "Table_Teams3_Header"
                    objLink.Text = GetTranslationString("total", "Total")
                    objLink.ID = "PageLink~Sort~TotalSavings" & "~"
                    If strSortColumn = "TotalSavings" Then
                        objLink.ID += strSortOrder
                    End If
                    objLink.CommandArgument = objLink.ID
                    objCell.Controls.Add(objLink)
                    objRow.Cells.Add(objCell)

                    tblTrackers.Rows.Add(objRow)

                    Dim _status As Boolean = True
                    bEnglish = (New System.Globalization.CultureInfo(SessionManager.CulturePref).TwoLetterISOLanguageName.ToUpper = "EN")
                    For Each objDR As DataRowView In dvTrackers
                        'create row
                        objRow = New TableRow

                        'fill in the cells
                        'Team
                        objCell = New TableCell
                        objCell.Width = New Unit(75)
                        RowStyle(_status, objCell)
                        objLink = New LinkButton
                        objLink.Text = objDR("Team").ToString
                        objLink.ID = "PageLink~Team~" + objDR("TeamID").ToString & "~" & objDR("Team").ToString & "~" & objDR("TrackerID").ToString
                        objCell.Controls.Add(objLink)
                        objRow.Cells.Add(objCell)

                        'Team Name
                        objCell = New TableCell
                        RowStyle(_status, objCell)
                        If bEnglish Then
                            objCell.Text = objDR("TeamNameOther").ToString
                            objCell.ToolTip = objDR("TeamName").ToString
                        Else
                            objCell.Text = objDR("TeamName").ToString
                            objCell.ToolTip = objDR("TeamNameOther").ToString
                        End If
                        objRow.Cells.Add(objCell)

                        'Tracker
                        objCell = New TableCell
                        RowStyle(_status, objCell)
                        objLink = New LinkButton
                        If bEnglish Then
                            objLink.Text = objDR("TrackerOther").ToString
                            objLink.ToolTip = objDR("Tracker").ToString
                        Else
                            objLink.Text = objDR("Tracker").ToString
                            objLink.ToolTip = objDR("TrackerOther").ToString
                        End If
                        objLink.ID = "PageLink~Tracker~" & objDR("TeamID").ToString & "~" & objDR("Team").ToString & "~" & objDR("TrackerID").ToString
                        objCell.Controls.Add(objLink)
                        objRow.Cells.Add(objCell)

                        'Site
                        objCell = New TableCell
                        RowStyle(_status, objCell)
                        objCell.Text = objDR("SiteAbbrev").ToString
                        objRow.Cells.Add(objCell)

                        'Pillar
                        objCell = New TableCell
                        RowStyle(_status, objCell)
                        objCell.Text = objDR("PillarAbbrev").ToString
                        objRow.Cells.Add(objCell)

                        'Business Area
                        objCell = New TableCell
                        RowStyle(_status, objCell)
                        objCell.Text = objDR("BusinessAreaAbbrev").ToString
                        objRow.Cells.Add(objCell)

                        'Business Unit
                        objCell = New TableCell
                        RowStyle(_status, objCell)
                        objCell.Text = objDR("BusinessUnitAbbrev").ToString
                        objRow.Cells.Add(objCell)

                        'Tracker UOM
                        objCell = New TableCell
                        RowStyle(_status, objCell)
                        objCell.Text = objDR("TrackerValueUOM").ToString
                        objRow.Cells.Add(objCell)

                        'Start Period
                        objCell = New TableCell
                        RowStyle(_status, objCell)
                        If IsDate(objDR("StartPeriod").ToString) Then
                            objCell.Text = CDate(objDR("StartPeriod")).ToString("yyyy/MM/dd")
                        Else
                            objCell.Text = objDR("StartPeriod").ToString
                        End If
                        objRow.Cells.Add(objCell)

                        'Last Value
                        objCell = New TableCell
                        RowStyle(_status, objCell)
                        If IsDate(objDR("LastValueDate").ToString) Then
                            objCell.Text = CDate(objDR("LastValueDate")).ToString("yyyy/MM")
                            If Convert.ToBoolean(objDR("Active")) Then
                                If IsDate(objDR("BeginPeriod")) AndAlso IsDate(objDR("EndPeriod")) Then
                                    If objDR("LastValueDate") >= objDR("BeginPeriod") AndAlso objDR("LastValueDate") < objDR("EndPeriod") Then
                                        Dim dtLast As DateTime = DateAdd(DateInterval.Month, -1, Now)
                                        dtLast = Convert.ToDateTime(dtLast.Year & "/" & dtLast.Month & "/01")
                                        If DateDiff(DateInterval.Month, objDR("LastValueDate"), dtLast) > 0 Then
                                            objCell.BackColor = Drawing.Color.Yellow
                                        End If
                                    End If
                                End If
                            End If
                        Else
                            objCell.Text = objDR("LastValueDate").ToString
                            If Convert.ToBoolean(objDR("Active")) Then
                                If IsDate(objDR("BeginPeriod")) AndAlso IsDate(objDR("EndPeriod")) Then
                                    Dim dtLast As DateTime = DateAdd(DateInterval.Month, -1, Now)
                                    dtLast = Convert.ToDateTime(dtLast.Year & "/" & dtLast.Month & "/01")

                                    If dtLast >= objDR("BeginPeriod") AndAlso dtLast < objDR("EndPeriod") Then
                                        objCell.BackColor = Drawing.Color.Yellow
                                    End If
                                End If
                            End If
                        End If
                        objRow.Cells.Add(objCell)

                        'Currency
                        objCell = New TableCell
                        RowStyle(_status, objCell)
                        objCell.Text = objDR("CurrencyAbbrev").ToString
                        objRow.Cells.Add(objCell)

                        'Previous Year
                        objCell = New TableCell
                        objCell.HorizontalAlign = HorizontalAlign.Right
                        RowStyle(_status, objCell)
                        If IsNumeric(objDR("PreviousYearSavings").ToString) Then
                            objCell.Text = Convert.ToInt32(objDR("PreviousYearSavings"))
                        End If
                        objRow.Cells.Add(objCell)

                        'Last Year 
                        objCell = New TableCell
                        objCell.HorizontalAlign = HorizontalAlign.Right
                        RowStyle(_status, objCell)
                        If IsNumeric(objDR("LastYearSavings").ToString) Then
                            objCell.Text = Convert.ToInt32(objDR("LastYearSavings"))
                        End If
                        objRow.Cells.Add(objCell)

                        'Current Year
                        objCell = New TableCell
                        objCell.HorizontalAlign = HorizontalAlign.Right
                        RowStyle(_status, objCell)
                        If IsNumeric(objDR("YearSavings").ToString) Then
                            objCell.Text = Convert.ToInt32(objDR("YearSavings"))
                        End If
                        objRow.Cells.Add(objCell)

                        'Last Month
                        objCell = New TableCell
                        objCell.HorizontalAlign = HorizontalAlign.Right
                        RowStyle(_status, objCell)
                        If IsNumeric(objDR("LastMonthSavings").ToString) Then
                            objCell.Text = Convert.ToInt32(objDR("LastMonthSavings"))
                        End If
                        objRow.Cells.Add(objCell)

                        'Total Savings
                        objCell = New TableCell
                        objCell.HorizontalAlign = HorizontalAlign.Right
                        RowStyle(_status, objCell)
                        If IsNumeric(objDR("TotalSavings").ToString) Then
                            objCell.Text = Convert.ToInt32(objDR("TotalSavings"))
                        End If
                        objRow.Cells.Add(objCell)

                        tblTrackers.Rows.Add(objRow)

                        If _status = True Then
                            _status = False
                        Else
                            _status = True
                        End If
                    Next objDR
                Else
                    pnlNoData.Visible = True
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindGrid", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
            End Try
        End Sub
        Private Sub RowStyle(ByVal passDefault As Boolean, ByRef passObj As TableCell)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try


            If passDefault Then
                passObj.CssClass = "Table_Teams3_DefaultRowStyle"
            Else
                passObj.CssClass = "Table_Teams3_AlternatingRowStyle"
            End If
        End Sub
#End Region

    End Class
End Namespace
