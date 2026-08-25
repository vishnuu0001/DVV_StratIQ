#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class Teams3
        Inherits ApplicationBase

#Region " Constants"
        Private Shared ReadOnly FormName As String = "Teams"
        Private Shared ReadOnly ProgramName As String = "TeamsListing"
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
                ckTeamMember.Text = GetTranslationString("showteammember", ckTeamMember.Text)
                ckMyPillarTeams.Text = GetTranslationString("showpillarmember", ckMyPillarTeams.Text)
                lblStatus.Text = GetTranslationString("status", lblStatus.Text.Replace(":", "")) & ":"
                lblPillar.Text = GetTranslationString("pillar", lblPillar.Text.Replace(":", "")) & ":"
                lblTeamType.Text = GetTranslationString("teamtype", lblTeamType.Text.Replace(":", "")) & ":"
                btnApplyFilter.Text = GetTranslationString("applyfilter", btnApplyFilter.Text)
                btnClearFilter.Text = GetTranslationString("clearfilter", btnClearFilter.Text)
                lnkPrintPage.Text = GetTranslationString("printfriendlyversion", lnkPrintPage.Text)
                btnExit.Text = GetTranslationString("exit", btnExit.Text)
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

            If Not Page.IsPostBack Then
                LoadDropDownListBoxes()
                LoadCultureTranslations()
                ApplyFiltersFromCookie()
            Else
                If Request.Item("__EVENTTARGET").ToString.Contains("TeamBoardLink") Then
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
        End Sub
        Protected Sub btnApplyFilter_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnApplyFilter.Click
            Dim cookie As New HttpCookie("MyTeamsFilter")
            cookie.Expires = Now.AddDays(Convert.ToInt16(ConfigurationManager.AppSettings("CookieExpirationTime")))

            If ckTeamMember.Checked Then
                cookie.Values("TeamMember") = ckTeamMember.Checked.ToString
            Else
                cookie.Values.Remove("TeamMember")
            End If

            If ckMyPillarTeams.Checked Then
                cookie.Values("MyPillarTeams") = ckMyPillarTeams.Checked.ToString
            Else
                cookie.Values.Remove("MyPillarTeams")
            End If

            If ddlStatus.SelectedItem IsNot Nothing Then
                cookie.Values("TeamStatus") = ddlStatus.SelectedItem.Value
            Else
                cookie.Values.Remove("TeamStatus")
            End If

            If ddlPillar.SelectedItem IsNot Nothing AndAlso ddlPillar.SelectedItem.Value.ToString.Trim.Length > 0 Then
                cookie.Values("Pillar") = ddlPillar.SelectedItem.Value
            Else
                cookie.Values.Remove("Pillar")
            End If

            If ddlTeamType.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlTeamType.SelectedItem.Value) Then
                cookie.Values("TeamType") = ddlTeamType.SelectedItem.Value
            Else
                cookie.Values.Remove("TeamType")
            End If

            Response.Cookies.Add(cookie)

            BindGrid(False)
        End Sub
        Protected Sub btnClearFilter_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnClearFilter.Click
            Response.Cookies("MyTeamsFilter").Expires = Now

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamsListing"), False)
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
        Private Sub ButtonClick(ByVal passArgs As String)
            Dim strTarget() As String
            strTarget = passArgs.Split("~")
            Dim strProgram As String = ""

            If strTarget(1) = "Sort" Then
                SessionManager.OverviewSortColumn = strTarget(2) & "~" & strTarget(3)
                BindGrid(True)
            Else
                PushTeamOntoStack(SessionManager.SelectedTeamID, SessionManager.SelectedTeam, SessionManager.SelectedOPI, "TeamsListing", SessionManager.CurrentMenuProgram)
                SessionManager.SelectedTeamID = strTarget(2)
                SessionManager.SelectedTeam = strTarget(3)
                If bEnglish Then
                    SessionManager.SelectedTeamName = Teams.GetTeamNameOther(SessionManager.SelectedTeamID)
                Else
                    SessionManager.SelectedTeamName = Teams.GetTeamName(SessionManager.SelectedTeamID)
                End If
                SessionManager.SelectedTeamAllowEdit = UserSiteMaster.SelectTeamAllowEdit(strTarget(2), SessionManager.UserID)
                Select Case strTarget(1)
                    Case "Team"
                        SessionManager.SelectedOPI = ""
                        SessionManager.CurrentMenuProgram = "TeamBoardMenu"
                        strProgram = "TeamBoardMenu"
                    Case "OPI"
                        SessionManager.SelectedOPI = strTarget(4)
                        strProgram = "TeamOPIReports2"
                End Select

                LastPixelPositionUpdate(ProgramName, Master.CurrentPixelPosition)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strProgram), True)
            End If
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadDropDownListBoxes()
            Pillars.SelectPillarList(ddlPillar)
            ddlPillar.Items.Insert(0, "")

            TeamTypes.SelectTeamTypesMasterList(ddlTeamType)
        End Sub
        Private Sub ApplyFiltersFromCookie()
            If Request.Cookies("MyTeamsFilter") IsNot Nothing Then
                Dim cookie As HttpCookie = Request.Cookies("MyTeamsFilter")
                Dim objItem As ListItem = Nothing

                If cookie.Values("TeamMember") IsNot Nothing AndAlso cookie.Values("TeamMember").ToString.Trim.Length > 0 Then
                    ckTeamMember.Checked = True
                End If

                If cookie.Values("MyPillarTeams") IsNot Nothing AndAlso cookie.Values("MyPillarTeams").ToString.Trim.Length > 0 Then
                    ckMyPillarTeams.Checked = True
                End If

                If cookie.Values("TeamStatus") IsNot Nothing AndAlso cookie.Values("TeamStatus").ToString.Trim.Length > 0 Then
                    objItem = ddlStatus.Items.FindByValue(cookie.Values("TeamStatus").ToString)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                    End If
                Else
                    ddlStatus.Items(1).Selected = True
                End If

                If cookie.Values("Pillar") IsNot Nothing AndAlso cookie.Values("Pillar").ToString.Trim.Length > 0 Then
                    objItem = ddlPillar.Items.FindByValue(cookie.Values("Pillar").ToString)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                    End If
                End If

                If cookie.Values("TeamType") IsNot Nothing AndAlso cookie.Values("TeamType").ToString.Trim.Length > 0 Then
                    objItem = ddlTeamType.Items.FindByValue(cookie.Values("TeamType").ToString)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                    End If
                End If
            Else
                ddlStatus.Items(1).Selected = True
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
                Dim bTeamMember As Boolean = ckTeamMember.Checked
                Dim bPillar As Boolean = ckMyPillarTeams.Checked
                Dim strStatus As String = ""
                Dim strPillar As String = ""
                Dim strTeamType As String = ""
                Dim strSortColumn As String = "Site|TeamSort"
                Dim strSortOrder As String = "Asc"

                tblTeams.Rows.Clear()

                If ddlStatus.SelectedItem IsNot Nothing AndAlso ddlStatus.SelectedItem.Value.ToString.Trim.Length > 0 Then
                    strStatus = ddlStatus.SelectedItem.Value.ToString
                End If
                If ddlPillar.SelectedItem IsNot Nothing AndAlso ddlPillar.SelectedItem.Value.ToString.Trim.Length > 0 Then
                    strPillar = ddlPillar.SelectedItem.Value.ToString
                End If
                If ddlTeamType.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlTeamType.SelectedItem.Value) Then
                    strTeamType = ddlTeamType.SelectedItem.Value.ToString
                End If

                If SessionManager.OverviewSortColumn <> "" Then
                    If SessionManager.OverviewSortColumn.ToString.Trim.Length > 0 Then
                        Dim strSort() As String = SessionManager.OverviewSortColumn.ToString.Split("~")

                        strSortColumn = strSort(0)
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

                Dim objDS As DataTable = Teams.SelectTeamsListing(SessionManager.WorkingSiteID, SessionManager.UserID, bTeamMember, bPillar, strStatus, strPillar, strTeamType)
                Dim dtView As DataView = objDS.DefaultView
                dtView.Sort = strSortColumn.Replace("|", " " & strSortOrder & ", ")
                Dim objRow As TableRow
                Dim objCell As TableCell
                Dim objLink As LinkButton

                If dtView.Count > 0 Then
                    'create header
                    objRow = New TableRow

                    'fill in the cells
                    'Team
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objLink = New LinkButton
                    objLink.CssClass = "Table_Teams3_Header"
                    objLink.Text = "Team"
                    objLink.ID = "TeamBoardLink~Sort~TeamSort|Site" & "~"
                    If strSortColumn = "TeamSort|Site" Then
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
                    objLink.Text = "Team Name"
                    objLink.ID = "TeamBoardLink~Sort~TeamName|Site" & "~"
                    If strSortColumn = "TeamName|Site" Then
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
                    objLink.Text = "Site"
                    objLink.ID = "TeamBoardLink~Sort~Site|TeamSort" & "~"
                    If strSortColumn = "Site|TeamSort" Then
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
                    objLink.Text = "Pillar"
                    objLink.ID = "TeamBoardLink~Sort~PillarAbbrev|TeamSort" & "~"
                    If strSortColumn = "PillarAbbrev|TeamSort" Then
                        objLink.ID += strSortOrder
                    End If
                    objLink.CommandArgument = objLink.ID
                    objCell.Controls.Add(objLink)
                    objRow.Cells.Add(objCell)

                    'Business Area
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objLink = New LinkButton
                    objLink.CssClass = "Table_Teams3_Header"
                    objLink.Text = "BA"
                    objLink.ID = "TeamBoardLink~Sort~BusinessAreaAbbrev|TeamSort" & "~"
                    If strSortColumn = "BusinessAreaAbbrev|TeamSort" Then
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
                    objLink.Text = "BU"
                    objLink.ID = "TeamBoardLink~Sort~BusinessUnitAbbrev|TeamSort" & "~"
                    If strSortColumn = "BusinessUnitAbbrev|TeamSort" Then
                        objLink.ID += strSortOrder
                    End If
                    objLink.CommandArgument = objLink.ID
                    objCell.Controls.Add(objLink)
                    objRow.Cells.Add(objCell)

                    'Route
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objLink = New LinkButton
                    objLink.CssClass = "Table_Teams3_Header"
                    objLink.Text = "Route"
                    objLink.ID = "TeamBoardLink~Sort~Route|TeamSort" & "~"
                    If strSortColumn = "Route|TeamSort" Then
                        objLink.ID += strSortOrder
                    End If
                    objLink.CommandArgument = objLink.ID
                    objCell.Controls.Add(objLink)
                    objRow.Cells.Add(objCell)

                    'Dept
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objLink = New LinkButton
                    objLink.CssClass = "Table_Teams3_Header"
                    objLink.Text = "Dept"
                    objLink.ID = "TeamBoardLink~Sort~DeptNumber|TeamSort" & "~"
                    If strSortColumn = "DeptNumber|TeamSort" Then
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
                    objLink.Text = "Start"
                    objLink.ID = "TeamBoardLink~Sort~TeamStartDate|TeamSort" & "~"
                    If strSortColumn = "TeamStartDate|TeamSort" Then
                        objLink.ID += strSortOrder
                    End If
                    objLink.CommandArgument = objLink.ID
                    objCell.Controls.Add(objLink)
                    objRow.Cells.Add(objCell)

                    'Finish
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objLink = New LinkButton
                    objLink.CssClass = "Table_Teams3_Header"
                    objLink.Text = "Finish"
                    objLink.ID = "TeamBoardLink~Sort~TeamFinishDate|TeamSort" & "~"
                    If strSortColumn = "TeamFinishDate|TeamSort" Then
                        objLink.ID += strSortOrder
                    End If
                    objLink.CommandArgument = objLink.ID
                    objCell.Controls.Add(objLink)
                    objRow.Cells.Add(objCell)

                    'Duration
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objLink = New LinkButton
                    objLink.CssClass = "Table_Teams3_Header"
                    objLink.Text = "Duration"
                    objLink.ID = "TeamBoardLink~Sort~Duration|TeamSort" & "~"
                    If strSortColumn = "Duration|TeamSort" Then
                        objLink.ID += strSortOrder
                    End If
                    objLink.CommandArgument = objLink.ID
                    objCell.Controls.Add(objLink)
                    objRow.Cells.Add(objCell)

                    'Status
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objLink = New LinkButton
                    objLink.CssClass = "Table_Teams3_Header"
                    objLink.Text = "Status"
                    objLink.ID = "TeamBoardLink~Sort~TeamStatusDescription|TeamSort" & "~"
                    If strSortColumn = "TeamStatusDescription|TeamSort" Then
                        objLink.ID += strSortOrder
                    End If
                    objLink.CommandArgument = objLink.ID
                    objCell.Controls.Add(objLink)
                    objRow.Cells.Add(objCell)

                    'Team Type
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objLink = New LinkButton
                    objLink.CssClass = "Table_Teams3_Header"
                    objLink.Text = "Type"
                    objLink.ID = "TeamBoardLink~Sort~TeamTypeID|TeamSort" & "~"
                    If strSortColumn = "TeamTypeID|TeamSort" Then
                        objLink.ID += strSortOrder
                    End If
                    objLink.CommandArgument = objLink.ID
                    objCell.Controls.Add(objLink)
                    objRow.Cells.Add(objCell)
                    tblTeams.Rows.Add(objRow)
                End If

                Dim _status As Boolean = True
                bEnglish = (New System.Globalization.CultureInfo(SessionManager.CulturePref).TwoLetterISOLanguageName.ToUpper = "EN")
                For Each objDR As DataRowView In dtView
                    'create row
                    objRow = New TableRow

                    'fill in the cells
                    'Team
                    objCell = New TableCell
                    objCell.Width = New Unit(75)
                    RowStyle(_status, objCell)

                    objLink = New LinkButton
                    objLink.Text = objDR("Team").ToString
                    objLink.ID = "TeamBoardLink~Team~" & objDR("TeamID").ToString & "~" & objDR("Team").ToString
                    objLink.CommandArgument = "Team~" + objDR("TeamID").ToString & "~" & objDR("Team").ToString
                    objCell.Controls.Add(objLink)
                    objRow.Cells.Add(objCell)

                    'Team Name
                    objCell = New TableCell
                    objCell.Width = New Unit(275)
                    RowStyle(_status, objCell)
                    If bEnglish Then
                        objCell.Text = objDR("TeamNameOther").ToString
                        objCell.ToolTip = objDR("TeamName").ToString
                    Else
                        objCell.Text = objDR("TeamName").ToString
                        objCell.ToolTip = objDR("TeamNameOther").ToString
                    End If
                    objRow.Cells.Add(objCell)

                    'Site
                    objCell = New TableCell
                    RowStyle(_status, objCell)
                    objCell.Text = objDR("Site").ToString
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

                    'Route
                    objCell = New TableCell
                    RowStyle(_status, objCell)
                    objCell.Text = objDR("Route").ToString
                    objRow.Cells.Add(objCell)

                    'Dept
                    objCell = New TableCell
                    RowStyle(_status, objCell)
                    objCell.Text = objDR("DeptNumber").ToString
                    objRow.Cells.Add(objCell)

                    'Start
                    objCell = New TableCell
                    RowStyle(_status, objCell)
                    objCell.Text = objDR("TeamStartDate").ToString
                    objRow.Cells.Add(objCell)

                    'Finish
                    objCell = New TableCell
                    RowStyle(_status, objCell)
                    objCell.Text = objDR("TeamFinishDate").ToString
                    objRow.Cells.Add(objCell)

                    'Duration
                    objCell = New TableCell
                    RowStyle(_status, objCell)
                    objCell.Text = objDR("Duration").ToString
                    objRow.Cells.Add(objCell)

                    'Status
                    objCell = New TableCell
                    RowStyle(_status, objCell)
                    objCell.Text = objDR("TeamStatusDescription").ToString
                    objRow.Cells.Add(objCell)

                    'Team Type
                    objCell = New TableCell
                    RowStyle(_status, objCell)
                    objCell.Text = objDR("TeamType").ToString
                    objRow.Cells.Add(objCell)

                    tblTeams.Rows.Add(objRow)
                    Dim xCell As TableCell = objCell
                    If TeamOPI.TeamHasOPIs(objDR("TeamID")) Then
                        Dim dsOPI As DataTable = TeamOPI.SelectOPIsByTeam(objDR("TeamID"))
                        Dim OPITable As Table
                        Dim OPIRow As TableRow
                        Dim OPICell As TableCell
                        Dim strHolder As String

                        objRow = New TableRow
                        objCell = New TableCell
                        objCell.ColumnSpan = 13

                        OPITable = New Table
                        OPITable.Width = New Unit("100%")
                        OPITable.CellPadding = 0
                        OPITable.CellSpacing = 0

                        Dim _default As Boolean = False
                        For Each drOPI As DataRow In dsOPI.Rows
                            If xCell.CssClass = "Table_Teams3_DefaultRowStyle" Then
                                _default = True
                            End If
                            OPIRow = New TableRow

                            OPICell = New TableCell
                            OPICell.Width = New Unit(115)
                            RowStyle(_default, OPICell)
                            OPIRow.Cells.Add(OPICell)

                            OPICell = New TableCell
                            RowStyle(_default, OPICell)
                            OPICell.Width = New Unit(200)

                            objLink = New LinkButton
                            objLink.Text = drOPI("OPI").ToString
                            objLink.ID = "TeamBoardLink~OPI~" & objDR("TeamID").ToString & "~" & drOPI("Team").ToString & "~" & drOPI("OPI").ToString
                            objLink.CommandArgument = "OPI~" & objDR("TeamID").ToString & "~" & drOPI("Team").ToString & "~" & drOPI("OPI").ToString
                            OPICell.Controls.Add(objLink)
                            OPIRow.Cells.Add(OPICell)

                            OPICell = New TableCell
                            RowStyle(_default, OPICell)
                            strHolder = drOPI("ResponsibleUserName").ToString
                            If strHolder.Trim.Length = 0 Then
                                strHolder = "&nbsp;"
                            End If
                            OPICell.Text = strHolder
                            OPIRow.Cells.Add(OPICell)
                            OPITable.Rows.Add(OPIRow)
                        Next drOPI

                        objCell.Controls.Add(OPITable)
                        objRow.Cells.Add(objCell)
                        tblTeams.Rows.Add(objRow)
                    End If
                    If _status = True Then
                        _status = False
                    Else
                        _status = True
                    End If
                Next objDR
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
