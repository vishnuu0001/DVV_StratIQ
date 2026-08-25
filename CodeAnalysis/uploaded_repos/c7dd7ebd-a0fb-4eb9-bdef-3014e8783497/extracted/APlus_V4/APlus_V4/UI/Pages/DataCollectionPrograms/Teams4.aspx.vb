#Region " Imports"
Imports System.IO
Imports System.Data.SqlClient
Imports System.Data
Imports WebApp.APlus.Helper
Imports WebApp.APlus.UI
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class Teams4
        Inherits PrinterFriendlyBase

#Region " Members / Variables"
        Private bTeamMember As Boolean = False
        Private bPillar As Boolean = False
        Private strStatus As String = ""
        Private strPillar As String = ""
        Private strTeamType As String = ""
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
                lblTeamsListing.Text = GetTranslationString("teamlisting", lblTeamsListing.Text)
            Catch Exc As Exception
                Master.DisplayErrors("Teams4 - LoadCultureTranslations", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "Teams4", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If Not Page.IsPostBack Then
                LoadCultureTranslations()
            End If

            ApplyFiltersFromCookie()
            BindGrid(False)
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub ApplyFiltersFromCookie()
            If Request.Cookies("MyTeamsFilter") IsNot Nothing Then
                Dim cookie As HttpCookie = Request.Cookies("MyTeamsFilter")

                If cookie.Values("TeamMember") IsNot Nothing AndAlso cookie.Values("TeamMember").ToString.Trim.Length > 0 Then
                    bTeamMember = True
                End If

                If cookie.Values("MyPillarTeams") IsNot Nothing AndAlso cookie.Values("MyPillarTeams").ToString.Trim.Length > 0 Then
                    bPillar = True
                End If

                If cookie.Values("TeamStatus") IsNot Nothing AndAlso cookie.Values("TeamStatus").ToString.Trim.Length > 0 Then
                    strStatus = cookie.Values("TeamStatus").ToString
                End If

                If cookie.Values("Pillar") IsNot Nothing AndAlso cookie.Values("Pillar").ToString.Trim.Length > 0 Then
                    strPillar = cookie.Values("Pillar").ToString
                End If

                If cookie.Values("TeamType") IsNot Nothing AndAlso cookie.Values("TeamType").ToString.Trim.Length > 0 Then
                    strTeamType = cookie.Values("TeamType").ToString
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
                Dim strSortColumn As String = "Site|Team"
                Dim strSortOrder As String = "Asc"

                tblTeams.Rows.Clear()

                If Not IsNothing(SessionManager.OverviewSortColumn) Then
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

                If dtView.Count > 0 Then
                    'create header
                    objRow = New TableRow

                    'fill in the cells
                    'Team
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objCell.Text = "Team"
                    objRow.Cells.Add(objCell)

                    'Team Name
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objCell.Text = "Team Name"
                    objRow.Cells.Add(objCell)

                    'Site
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objCell.Text = "Site"
                    objRow.Cells.Add(objCell)

                    'Pillar
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objCell.Text = "Pillar"
                    objRow.Cells.Add(objCell)

                    'Route
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objCell.Text = "Route"
                    objRow.Cells.Add(objCell)

                    'Dept
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objCell.Text = "Dept"
                    objRow.Cells.Add(objCell)

                    'Start
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objCell.Text = "Start"
                    objRow.Cells.Add(objCell)

                    'Finish
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objCell.Text = "Finish"
                    objRow.Cells.Add(objCell)

                    'Duration
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objCell.Text = "Duration"
                    objRow.Cells.Add(objCell)

                    'Status
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objCell.Text = "Status"
                    objRow.Cells.Add(objCell)

                    'Team Type
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objCell.Text = "Type"
                    objRow.Cells.Add(objCell)

                    tblTeams.Rows.Add(objRow)
                End If

                Dim _status As Boolean = True
                For Each objDR As DataRowView In dtView
                    'create row
                    objRow = New TableRow

                    'fill in the cells
                    'Team
                    objCell = New TableCell
                    objCell.Width = New Unit(75)
                    RowStyle(_status, objCell)
                    objCell.Text = objDR("Team").ToString
                    objRow.Cells.Add(objCell)

                    'Team Name
                    objCell = New TableCell
                    objCell.Width = New Unit(275)
                    RowStyle(_status, objCell)
                    objCell.Text = objDR("TeamName").ToString
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
                        objCell.ColumnSpan = 11

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
                            OPICell.Text = drOPI("OPI").ToString
                            OPIRow.Cells.Add(OPICell)

                            OPICell = New TableCell
                            RowStyle(_default, OPICell)
                            strHolder = UserMaster.GetUserFullNameLastNameFirst(drOPI("ResponsibleUser").ToString)
                            If strHolder.Trim.Length = 0 Then
                                strHolder = drOPI("ResponsibleUser").ToString
                            End If
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
                Master.DisplayErrors("Teams4 - BindGrid", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
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