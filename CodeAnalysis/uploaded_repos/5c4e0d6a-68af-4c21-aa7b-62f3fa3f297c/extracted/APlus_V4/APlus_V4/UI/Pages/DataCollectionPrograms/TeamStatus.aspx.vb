#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports System.Web.Security
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.DataAccess.Custom
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class TeamStatus
        Inherits ApplicationBase

#Region " Private Variables"
        Private Shared ReadOnly FormName As String = "Team Status"
        Private Shared ReadOnly ProgramName As String = "TeamStatus"
        Private blnSuccess As Boolean
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
                lblPillar.Text = GetTranslationString("pillar", lblPillar.Text.Replace(":", "")) & ":"
                lblDept.Text = GetTranslationString("department", lblDept.Text.Replace(":", "")) & ":"
                lblRoute.Text = GetTranslationString("route", lblRoute.Text.Replace(":", "")) & ":"
                lblTeamActionPlan.Text = GetTranslationString("teamaction plan", lblTeamActionPlan.Text.Replace(":", "")) & ":"
                lblTeamFinishDate.Text = GetTranslationString("finishdate", lblTeamFinishDate.Text.Replace(":", "")) & ":"
                lblTeamMeetingAttendance.Text = GetTranslationString("team meeting attendance", lblTeamMeetingAttendance.Text.Replace(":", "")) & ":"
                lblTeamStartDate.Text = GetTranslationString("start date", lblTeamStartDate.Text.Replace(":", "")) & ":"
                lblTeamStatus.Text = GetTranslationString("team status", lblTeamStatus.Text.Replace(":", "")) & ":"
                lnkPrintPage.Text = GetTranslationString("printfriendlyversion", lnkPrintPage.Text)
                lnkPrintPage1.Text = GetTranslationString("printfriendlyversion", lnkPrintPage1.Text)
                chkAttendance.Text = GetTranslationString("showteammembers", chkAttendance.Text)
                chkLatestMeetings.Text = GetTranslationString("newestmeetings", chkLatestMeetings.Text)
                chkDisplayClosedTeamActions.Text = GetTranslationString("includeclosedteamactions", chkDisplayClosedTeamActions.Text)
                btnExit.Text = GetTranslationString("exit", btnExit.Text)
                btnTeamActionPlan.Text = GetTranslationString("teamaction plan", btnTeamActionPlan.Text)
                btnTeamBoard.Text = GetTranslationString("teamboard", btnTeamBoard.Text)
                btnTeamInquiry.Text = GetTranslationString("teaminquiry", btnTeamInquiry.Text)
                btnTeamLog.Text = GetTranslationString("team log", btnTeamLog.Text)
                btnTeamMasterPlan.Text = GetTranslationString("teammaster plan", btnTeamMasterPlan.Text)
                btnTeamMeeting.Text = GetTranslationString("team meetings", btnTeamMeeting.Text)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadCultureTranslations", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub LoadGridsCultureTranslations()
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
                For i As Integer = 0 To gvTeamMeetingAttendance.Columns.Count - 1
                    gvTeamMeetingAttendance.Columns(i).HeaderText = GetTranslationString(gvTeamMeetingAttendance.Columns(i).HeaderText, gvTeamMeetingAttendance.Columns(i).HeaderText)
                Next
                For i As Integer = 0 To gvTeamActionPlan.Columns.Count - 1
                    gvTeamActionPlan.Columns(i).HeaderText = GetTranslationString(gvTeamActionPlan.Columns(i).HeaderText, gvTeamActionPlan.Columns(i).HeaderText)
                Next
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

            Master.IconImage = Request.ApplicationPath + "/images/usergroup.gif"

            If Not SessionManager.TeamStatusMode = String.Empty Then
                Master.HeaderMessage = GetTranslationString(FormName, FormName) & " - " & GetTranslationString(SessionManager.TeamStatusMode.Replace("Row", ""), SessionManager.TeamStatusMode.Replace("Row", "")) & " " & GetTranslationString("TeamMeetingAttendance", "Team Meeting Attendance")
            Else
                Master.HeaderMessage = GetTranslationString(FormName, FormName) & " - " & SessionManager.TeamStatusMode.Replace("Row", "") & " " & GetTranslationString("TeamMeetingAttendance", "Team Meeting Attendance")
            End If

            LoadCommonJavaScripts()

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.AllowMaintenanceAdd)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.AllowMaintenanceDelete)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.AllowMaintenanceEdit)
            SessionManager.TeamStatusMode = "ViewRow"
            SessionManager.CurrentProgram = Request.Path

            'if the user has rights to edit TeamOPI then show the button
            If ProgramSecurity.CanUserAccessProgram(SessionManager.UserID, "TeamBoardMenu") = False Then
                btnTeamBoard.Visible = False
            End If

            If Not Page.IsPostBack Then
                chkDisplayClosedTeamActions.Checked = SessionManager.DisplayClosedTeamActions

                If SessionManager.TeamStatusMode = "ViewRow" Then
                    If SessionManager.SelectedTeamID = 0 Then
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamSelection"), False)
                        Return
                    End If
                    pnlExit.Visible = True
                    LoadSelectedRecord()
                Else
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & (ProgramSecurity.GetProgramURL("TeamStatus")), False)
                    Return
                End If
            Else
                SessionManager.DisplayClosedTeamActions = chkDisplayClosedTeamActions.Checked
            End If

            LoadGridsCultureTranslations()

            SelectTeamMeetingAttendanceByTeam()
            SelectTeamActionPlansByTeam()
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamStatusMode)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CurrentProgram)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.DisplayClosedTeamActions)
            RemoveCurrentProgramandGoBack()
        End Sub
        Private Sub btnTeamInquiry_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnTeamInquiry.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.SelectedValueTeamID = SessionManager.SelectedTeamID
            SessionManager.TeamsMode = "ViewRow"
            SessionManager.CallingProgram = "TeamStatus"
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamsMaintenance2"), False)
        End Sub
        Private Sub btnTeamMeeting_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnTeamMeeting.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.MasterControlExitProgram = "TeamStatus"
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamMeetings1"), False)
        End Sub
        Private Sub btnTeamActionPlan_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnTeamActionPlan.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.MasterControlExitProgram = "TeamStatus"
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamActionPlanMaintenance"), False)
        End Sub
        Private Sub btnTeamMasterPlan_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnTeamMasterPlan.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.CallingProgram = "TeamStatus"
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamRouteSteps1"), False)
        End Sub
        Private Sub btnTeamLog_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnTeamLog.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.MasterControlExitProgram = "TeamStatus"
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamLog1"), False)
        End Sub
        Private Sub btnTeamBoard_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnTeamBoard.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamBoardMenu"), False)
        End Sub
        Protected Sub gvTeamMeetingAttendance2_Sorting(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewSortEventArgs) Handles gvTeamMeetingAttendance2.Sorting
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.TeamMeetingID = e.SortExpression
            SessionManager.TeamMeetingsMode = "ViewRow"
            SessionManager.CallingProgram = "TeamStatus"
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamMeetings2"), False)
        End Sub
#End Region

#Region " Custom Methods"
        Public Function BuildDataTable() As DataTable
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
                Dim ds1 As DataTable = TeamAttachments.SelectTeamAttachments(SessionManager.SelectedTeamID)
                Dim dt As New DataTable
                dt.Columns.Add(New DataColumn("AttachmentsText"))
                dt.Columns.Add(New DataColumn("AttachmentsURL"))
                For Each row As DataRow In ds1.Rows
                    Dim dr As DataRow = dt.NewRow()
                    dr = dt.NewRow
                    dr("AttachmentsText") = GetLinkText(row("Attachment"))
                    dr("AttachmentsURL") = GetNavigateURL(row("Attachment"))
                    dt.Rows.Add(dr)
                Next
                Return dt
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BuildDataTable", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                Return Nothing
            End Try
        End Function
        Public Function GetLinkText(ByVal Attachment As String) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, Attachment)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Return Path.GetFileName(ConfigurationManager.AppSettings("TeamAttachmentsRootDirectory") & SessionManager.SelectedTeam & "\" & Attachment)
        End Function
        Public Function GetNavigateURL(ByVal Attachment As String) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, Attachment)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Return "javascript:window.open('http://" & ConfigurationManager.AppSettings("ApplicationServerDNS").ToString & ConfigurationManager.AppSettings("TeamAttachmentsVirtualRootDirectory") & SessionManager.SelectedTeam & "/" & Attachment & "')"
        End Function
        Private Sub SelectTeamMeetingAttendanceByTeam()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If chkAttendance.Checked Then
                SessionManager.ShowAttendance = "Team"
            Else
                SessionManager.ShowAttendance = "All"
            End If
            Dim bShowAll As Boolean = (SessionManager.ShowAttendance = "All")

            Try
                gvTeamMeetingAttendance.DataSource = Nothing
                gvTeamMeetingAttendance.DataBind()
                gvTeamMeetingAttendance2.Columns.Clear()
                gvTeamMeetingAttendance2.DataSource = Nothing
                gvTeamMeetingAttendance2.DataBind()

                Dim strMeetingDate() As String

                Dim ds As DataTable = TeamMeetingAttendance.SelectTeamMeetingAttendanceByTeam(SessionManager.SelectedTeamID, bShowAll, chkLatestMeetings.Checked)
                Dim dc As DataColumn
                Dim dtColumn As BoundField
                Dim strDate As String
                For Each dc In ds.Columns
                    Select Case dc.ColumnName
                        Case "Team", "UserID", "UserName", "Title", "Role", "SortOrder"
                            'we don't care about these
                        Case Else
                            dtColumn = New BoundField
                            dtColumn.HtmlEncode = True
                            strMeetingDate = dc.ColumnName.Split("|")
                            dtColumn.HeaderText = strMeetingDate(1)
                            Dim arr() As String = dtColumn.HeaderText.Split(" ")
                            Dim blnAudit As Boolean
                            blnAudit = TeamMeetings.SelectTeamMeetingAudit(arr(0), arr(1))
                            dtColumn.SortExpression = strMeetingDate(0)
                            dtColumn.DataField = dc.ColumnName
                            dtColumn.HeaderStyle.Width = New Unit(30, UnitType.Pixel)
                            dtColumn.HeaderStyle.Height = New Unit(20, UnitType.Pixel)
                            dtColumn.HeaderStyle.Font.Size = New FontUnit(6)
                            dtColumn.HeaderStyle.HorizontalAlign = HorizontalAlign.Center
                            dtColumn.HeaderStyle.VerticalAlign = VerticalAlign.Middle
                            dtColumn.HtmlEncode = False
                            If blnAudit Then
                                dtColumn.HeaderStyle.BackColor = Drawing.Color.MediumBlue
                            End If
                            strDate = dtColumn.HeaderText.ToString
                            Dim strYear As String
                            Dim strTime As String = Right(dtColumn.DataField.ToString, 5)
                            If IsDate(strDate) Then
                                strYear = Convert.ToDateTime(strDate).ToString("yyyy")
                                strDate = Replace(Convert.ToDateTime(strDate).ToString("MMM d"), " ", " ")
                                dtColumn.HeaderText = strYear & " " & strDate.Replace(" ", "&nbsp;") & " " & strTime
                            End If
                            gvTeamMeetingAttendance2.Columns.Add(dtColumn)
                    End Select
                Next dc

                gvTeamMeetingAttendance2.AllowSorting = True
                gvTeamMeetingAttendance2.DataSource = ds
                gvTeamMeetingAttendance2.DataBind()
                gvTeamMeetingAttendance.DataSource = ds
                gvTeamMeetingAttendance.DataBind()

                For Each item As GridViewRow In gvTeamMeetingAttendance2.Rows
                    For Each cell As TableCell In item.Cells
                        cell.HorizontalAlign = HorizontalAlign.Center
                        cell.BorderStyle = BorderStyle.Solid
                        cell.BorderWidth = New Unit(1)

                        Dim i As Integer = item.Cells.GetCellIndex(cell) + 6
                        strMeetingDate = ds.Columns(i).ColumnName.ToString.Split("|")
                        Dim dtDateTime As DateTime = Convert.ToDateTime(strMeetingDate(1))
                        If DateTime.Compare(CType((dtDateTime.ToShortDateString), Date), CType(DateAdd(DateInterval.Day, 1, Date.Now).ToShortDateString, Date)) < 0 Then
                            Select Case cell.Text
                                Case "1"
                                    cell.CssClass = "TeamGreenCell"
                                    cell.Text = "X"
                                Case "2"
                                    cell.CssClass = "TeamWhiteCell"
                                    cell.Text = "&nbsp;"
                                Case Else
                                    cell.CssClass = "TeamRedCell"
                                    cell.Text = "O"
                            End Select
                        Else
                            cell.CssClass = "TeamWhiteCell"
                            cell.Text = "&nbsp;"
                        End If
                    Next
                Next

                'Panel1.Height = New Unit(gvTeamMeetingAttendance2.Rows.Count * 27 + 65)
                'Panel1.Height = New Unit(gvTeamMeetingAttendance2.Rows.Count * 16 + 65)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - SelectTeamMeetingAttendanceByTeam", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub SelectTeamActionPlansByTeam()
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
                Dim bShowClosedItems As Boolean = chkDisplayClosedTeamActions.Checked
                Dim ds As DataTable = TeamActionPlan.SelectTeamActionPlansByTeam(SessionManager.SelectedTeamID, bShowClosedItems)

                gvTeamActionPlan.DataSource = ds
                gvTeamActionPlan.DataBind()

                'Color Closed Date TextBox
                For Each item As GridViewRow In gvTeamActionPlan.Rows
                    Dim dtClosedDate As DateTime
                    Dim dtTargetDate As DateTime = Convert.ToDateTime(item.Cells(5).Text)
                    If item.Cells(6).Text <> "&nbsp;" Then
                        dtClosedDate = Convert.ToDateTime(item.Cells(6).Text)
                        If Convert.ToBoolean(gvTeamActionPlan.DataKeys(item.RowIndex)("Cancelled").ToString) = True Then
                            item.Cells(6).BackColor = Drawing.Color.Gray
                        ElseIf DateTime.Compare(dtClosedDate, dtTargetDate) <= 0 Then
                            item.Cells(6).BackColor = Drawing.Color.Green
                        Else
                            item.Cells(6).BackColor = Drawing.Color.Orange
                        End If
                    Else
                        If DateTime.Compare(dtTargetDate, Date.Now) >= 0 Then
                            item.Cells(6).BackColor = Drawing.Color.Yellow
                        Else
                            item.Cells(6).BackColor = Drawing.Color.Red
                        End If
                    End If

                    If Not String.IsNullOrEmpty(gvTeamActionPlan.DataKeys(item.RowIndex)("ActionItemDefinition").ToString) Then
                        item.Cells(4).ToolTip = gvTeamActionPlan.DataKeys(item.RowIndex)("ActionItemDefinition").ToString.Trim
                    End If

                    item.Cells(0).BackColor = Drawing.Color.White
                    item.Cells(1).BackColor = Drawing.Color.LemonChiffon
                    item.Cells(2).BackColor = Drawing.Color.LemonChiffon
                    item.Cells(3).BackColor = Drawing.Color.LemonChiffon
                    item.Cells(4).BackColor = Drawing.Color.LemonChiffon
                    item.Cells(5).BackColor = Drawing.Color.LemonChiffon
                Next
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - SelectTeamActionPlansByTeam", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub LoadSelectedRecord()
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
                Dim ds As DataTable = Teams.SelectTeams(SessionManager.SelectedTeamID)
                If ds IsNot Nothing AndAlso ds.Rows.Count <> 0 Then
                    Dim dr As DataRow = ds.Rows(0)
                    txtPillar.Text = dr("PillarAbbrev").ToString() + "-" + dr("Pillar").ToString()
                    txtRoute.Text = dr("RouteAbbrev").ToString() + "-" + dr("Route").ToString()
                    txtDept.Text = dr("DeptNumber").ToString
                    If IsDate(dr("TeamStartDate").ToString()) Then
                        txtTeamStartDate.Text = CDate(dr("TeamStartDate").ToString).ToShortDateString
                    Else
                        txtTeamStartDate.Text = ""
                    End If
                    If IsDate(dr("TeamFinishDate").ToString()) Then
                        txtTeamFinishDate.Text = CDate(dr("TeamFinishDate").ToString).ToShortDateString
                    Else
                        txtTeamFinishDate.Text = ""
                    End If
                    txtTeamStatus.Text = dr.Item("Description").ToString.Trim()
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

    End Class
End Namespace
