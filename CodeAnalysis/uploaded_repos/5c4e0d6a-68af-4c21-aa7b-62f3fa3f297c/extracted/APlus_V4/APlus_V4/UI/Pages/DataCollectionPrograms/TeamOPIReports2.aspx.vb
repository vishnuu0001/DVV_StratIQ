#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.UI
Imports WebApp.APlus.UI.CustomControls
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class TeamOPIReports2
        Inherits ApplicationBase

#Region " Constants"
        Private Shared ReadOnly FormName As String = "Team OPI Reports"
        Private Shared ReadOnly ProgramName As String = "TeamOPIReports2"
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
                lnkPrintPage.Text = GetTranslationString("printfriendlyversion", lnkPrintPage.Text)
                lnkCostBenefit.Text = GetTranslationString("costbenefitprinterfriendlyversion", lnkCostBenefit.Text)
                btnCancel.Text = GetTranslationString("exit", btnCancel.Text)
                btnTeamOPI.Text = GetTranslationString("teamopimaintenance", btnTeamOPI.Text)
                btnDataEntry.Text = GetTranslationString("team opi data entry", btnDataEntry.Text)
                btnControlLimits.Text = GetTranslationString("team opi control limits", btnControlLimits.Text)
                btnTeamOPIEvents.Text = GetTranslationString("team opi events", btnTeamOPIEvents.Text)
                btnViewData.Text = GetTranslationString("viewalldetail", btnViewData.Text)
                btnExport.Text = GetTranslationString("export", btnExport.Text)
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

            If Not Page.IsPostBack Then
                LoadCultureTranslations()
            End If

            Master.IconImage = Request.ApplicationPath & "/images/TeamGraph.gif"
            Master.HeaderMessage = GetTranslationString(FormName, FormName)
            Master.AddBodyAttribute("onkeydown", "TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event)")

            'Team and OPI Selection
            SessionManager.CurrentProgram = Request.Path
            If SessionManager.SelectedTeamID = 0 Then
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamSelection"), False)
                Return
            End If
            If SessionManager.SelectedOPI = String.Empty Then
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("OPISelection"), False)
                Return
            End If

            Dim strUOM As String = TeamOPI.GetUOM(SessionManager.SelectedTeamID, SessionManager.SelectedOPI)

            SessionManager.OPIUOM = strUOM

            If Not Page.IsPostBack Then
                TeamOPIGraph1.ChartWidth = 800
                TeamOPIGraph1.ChartHeight = 400
                TeamOPIGraph1.WhiteChart = False
                TeamOPIGraph1.DetailChart = False
                TeamOPIGraph1.ChartTeamID = SessionManager.SelectedTeamID
                TeamOPIGraph1.ChartOPI = SessionManager.SelectedOPI
                TeamOPIGraph1.ChartTitle = TeamOPI.GetPresentationName(SessionManager.SelectedTeamID, SessionManager.SelectedOPI)
                TeamOPIGraph1.OPIUOM = strUOM
                TeamOPIGraph1.ChartType = "OPI"
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CurrentProgram)

                BindGrid()
                ShowTeamOPIButton()
            End If
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue2)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue3)
            RemoveCurrentProgramandGoBack()
        End Sub
        Private Sub btnViewData_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnViewData.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.SelectedValue1 = SessionManager.SelectedTeamID
            SessionManager.SelectedValue2 = SessionManager.SelectedOPI
            SessionManager.SelectedValue3 = String.Empty
            ShowDetail()
        End Sub
        Private Sub btnTeamOPI_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnTeamOPI.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.OPIEntrySelectedValue = SessionManager.SelectedTeamID
            SessionManager.OPIEntrySelectedValue1 = SessionManager.SelectedOPI

            If SessionManager.SelectedTeamAllowEdit Then
                SessionManager.OPIMode = "Edit-OPI Entry"
            Else
                SessionManager.OPIMode = "View-OPI Entry"
            End If
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamOPIMaintenance2"), False)
        End Sub
        Private Sub btnDataEntry_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnDataEntry.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.MasterControlExitProgram = "TeamOPIReports2"
            Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamOPIValues1"), False)
        End Sub
        Private Sub btnControlLimits_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnControlLimits.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.MasterControlExitProgram = "TeamOPIReports2"
            Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamOPIControlLimits1"), False)
        End Sub
        Private Sub btnTeamOPIEvents_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnTeamOPIEvents.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.MasterControlExitProgram = "TeamOPIReports2"
            Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamOPIEvents1"), False)
        End Sub
        Private Sub btnExport_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExport.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Export()
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - btnExport_Click", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
            End Try
        End Sub
        Protected Sub grdReportSummary_RowCommand(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewCommandEventArgs) Handles grdReportSummary.RowCommand
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                If grdReportSummary.Rows(CInt(e.CommandArgument)).Cells(0).Text = "Total Benefit" Then
                    SessionManager.SelectedValue1 = SessionManager.SelectedTeamID 'grdReportSummary.DataKeys(e.CommandArgument)("Team").ToString
                    SessionManager.SelectedValue2 = SessionManager.SelectedOPI 'grdReportSummary.DataKeys(e.CommandArgument)("OPI").ToString
                    SessionManager.SelectedValue3 = ""
                Else
                    SessionManager.SelectedValue1 = grdReportSummary.DataKeys(e.CommandArgument)("TeamID").ToString
                    SessionManager.SelectedValue2 = grdReportSummary.DataKeys(e.CommandArgument)("OPI").ToString
                    SessionManager.SelectedValue3 = grdReportSummary.DataKeys(e.CommandArgument)("ReportPeriod").ToString
                End If

                ShowDetail()
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - grdReportSummary1_RowCommand ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Protected Sub grdReportSummary_RowDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewRowEventArgs) Handles grdReportSummary.RowDataBound
            If e.Row.RowType = DataControlRowType.DataRow Then
                If e.Row.Cells(0).Text = "Total Benefit" Then
                    e.Row.Cells(0).Font.Bold = True
                    e.Row.Cells(4).Font.Bold = True
                    e.Row.Cells(5).Font.Bold = True
                End If
            End If
        End Sub
#End Region

#Region "Custom Methods"
        Private Sub ShowTeamOPIButton()
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
                'if the user has rights to edit TeamOPI then show the button
                If ProgramSecurity.CanUserAccessProgram(SessionManager.UserID, "TeamOPIMaintenance2") = False Then
                    btnTeamOPI.Visible = False
                    Return
                End If

                If Teams.UserHasAccessToTeam(SessionManager.UserID, SessionManager.SelectedTeamID, SessionManager.WorkingSiteID) = False Then
                    btnTeamOPI.Visible = False
                    Return
                End If

                btnTeamOPI.Visible = True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - ShowTeamOPIButton ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub ShowDetail()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamOPIReports3"), False)
        End Sub
        Private Sub BindGrid()
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
                ConfigureColumns()
                Dim objDT As DataTable = TeamOPIValues.SelectTeamOPIValuesReportSummary(SessionManager.SelectedTeamID, SessionManager.SelectedOPI)
                grdReportSummary.DataSource = objDT
                grdReportSummary.DataBind()

                Dim objLink As LinkButton
                objLink = CType(grdReportSummary.Rows(grdReportSummary.Rows.Count - 1).Cells(grdReportSummary.Rows(0).Cells.Count - 2).Controls(0), LinkButton)
                objLink.Text = "View All Detail"
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindGrid ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub Export()
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
                ConfigureColumns()
                Dim objDT As DataTable = TeamOPIValues.SelectTeamOPIValuesReportSummary(SessionManager.SelectedTeamID, SessionManager.SelectedOPI)
                grdReportSummary.DataSource = objDT
                grdReportSummary.DataBind()

                Dim strHolder As String
                strHolder = "<table cellspacing='0' rules='all' border='1' id='grdReportSummary' style='width:100%;border-collapse:collapse;'>"
                strHolder += "<tr style='color:White;background-color:DarkBlue;font-weight:bold;'>"
                strHolder += "<td>Team</td><td>OPI</td><td>Report Period</><td>Value</td><td>Benefit</td><td>Benefit %</td>"
                Dim objDR As DataRow
                For Each objDR In grdReportSummary.DataSource.rows
                    strHolder += "<tr>"
                    strHolder += "<td>" + objDR(0).ToString + "</td>"
                    strHolder += "<td>" + objDR(1).ToString + "</td>"
                    strHolder += "<td>" + objDR(2).ToString + "</td>"
                    strHolder += "<td>" + objDR(3).ToString + "</td>"
                    strHolder += "<td>" + objDR(6).ToString + "</td>"
                    strHolder += "<td>" + objDR(7).ToString + "</td>"
                    strHolder += "</tr>"
                Next
                strHolder += "</table>"
                SessionManager.ExportString = strHolder
                Response.Redirect(Request.ApplicationPath.ToString + "/UI/UserControls/Export.aspx")
            Catch Exc As Exception
                Throw
            End Try
        End Sub
        Private Sub ConfigureColumns()
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
                Dim dt As DataTable = TeamOPI.SelectTeamOPI(SessionManager.SelectedTeamID, SessionManager.SelectedOPI)
                Dim dr As DataRow = dt.Rows(0)
                Dim dtColumn As BoundField

                'TeamID
                dtColumn = New BoundField
                dtColumn.HeaderText = GetTranslationString("teamid", "TeamID")
                dtColumn.DataField = "TeamID"
                dtColumn.Visible = False
                grdReportSummary.Columns.Insert(0, dtColumn)

                'Team
                dtColumn = New BoundField
                dtColumn.HeaderText = GetTranslationString("team", "Team")
                dtColumn.DataField = "Team"
                grdReportSummary.Columns.Insert(0, dtColumn)

                'OPI
                dtColumn = New BoundField
                dtColumn.HeaderText = GetTranslationString("opi", "OPI")
                dtColumn.DataField = "OPI"
                grdReportSummary.Columns.Insert(1, dtColumn)

                'End Date
                dtColumn = New BoundField
                dtColumn.HeaderText = GetTranslationString("periodenddate", "Period End Date")
                dtColumn.DataField = "ReportPeriod"
                dtColumn.DataFormatString = "{0:" + SessionManager.DateFormat + "}"
                grdReportSummary.Columns.Insert(2, dtColumn)

                'OPI Value
                dtColumn = New BoundField
                dtColumn.HeaderText = GetTranslationString("opi value", "OPI Value")
                dtColumn.DataField = "OPIValue"
                Select Case dr("OPIEntryType").ToString
                    Case "D"
                        dtColumn.DataFormatString = "{0:F" + dr("OPISize").ToString + "}"
                    Case "N"
                        If dr("SummaryType") = "A" Then
                            dtColumn.DataFormatString = "{0:F2}"
                        Else
                            dtColumn.DataFormatString = "{0:F0}"
                        End If
                End Select
                grdReportSummary.Columns.Insert(3, dtColumn)

                'Benefit
                dtColumn = New BoundField
                dtColumn.HeaderText = GetTranslationString("benefit", "Benefit")
                dtColumn.DataField = "Benefit"
                dtColumn.DataFormatString = "{0:F2}"
                grdReportSummary.Columns.Insert(4, dtColumn)

                'Benefit Percentage
                dtColumn = New BoundField
                dtColumn.HeaderText = GetTranslationString("benefit", "Benefit") & " %"
                dtColumn.DataField = "BenefitPercentage"
                dtColumn.DataFormatString = "{0:F2}"
                grdReportSummary.Columns.Insert(5, dtColumn)

                Dim btnButtonField As New ButtonField
                btnButtonField.CommandName = "ItemDetail"
                btnButtonField.Text = GetTranslationString("viewdetail", "View Detail")

                grdReportSummary.Columns.Insert(6, btnButtonField)
            Catch Exc As Exception
                Throw
            End Try
        End Sub
#End Region

    End Class
End Namespace
