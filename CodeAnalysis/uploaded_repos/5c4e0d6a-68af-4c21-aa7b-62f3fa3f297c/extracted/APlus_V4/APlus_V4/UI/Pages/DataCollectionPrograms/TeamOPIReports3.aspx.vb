#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper
Imports WebApp.APlus.UI
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.UI.Pages
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class TeamOPIReports3
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Team OPI Reports"
        Private Shared ReadOnly ProgramName As String = "TeamOPIReports3"
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
                lblNoData.Text = GetTranslationString("nodataavailableforselectedtimeframe", lblNoData.Text)
                btnCancel.Text = GetTranslationString("exit", btnCancel.Text)
                btnExport.Text = GetTranslationString("export", btnExport.Text)
                For i As Integer = 0 To grdReportSummary.Columns.Count - 1
                    grdReportSummary.Columns(i).HeaderText = GetTranslationString(grdReportSummary.Columns(i).HeaderText, grdReportSummary.Columns(i).HeaderText)
                Next
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
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event)")

            If SessionManager.SelectedValue3 = "" Then
                Master.HeaderMessage = GetTranslationString(FormName, FormName) & " - " & GetTranslationString("viewalldetail", "View All Detail")
            Else
                Master.HeaderMessage = GetTranslationString(FormName, FormName) & " - " & GetTranslationString("viewdetail", "View Detail")
            End If

            ConfigureParameterColumns()
            BindGrid()
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
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamOPIReports2"), False)
        End Sub
        Protected Sub grdReportSummary_RowDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewRowEventArgs) Handles grdReportSummary.RowDataBound
            If e.Row.RowType = DataControlRowType.DataRow Then
                If e.Row.Cells(0).Text = GetTranslationString("total", "Total") Then
                    e.Row.Cells(0).Font.Bold = True
                    e.Row.Cells(5).Font.Bold = True
                    e.Row.Cells(6).Font.Bold = True
                Else
                    Try
                        For i As Integer = 1 To grdReportSummary.Columns.Count - 8
                            If CType(grdReportSummary.Columns(i + 2), BoundField).DataFormatString.Contains("0:F") Then
                                e.Row.Cells(i + 2).Text = Convert.ToDecimal(e.Row.Cells(i + 2).Text.Replace(".", System.Threading.Thread.CurrentThread.CurrentCulture.NumberFormat.NumberDecimalSeparator))
                            End If
                        Next
                    Catch ex As Exception

                    End Try
                End If
            End If
        End Sub

#End Region

#Region "Custom Methods"
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
                Dim strDateHolder As String = ""
                If SessionManager.SelectedValue3 = "" Then
                    'use all dates
                Else
                    strDateHolder = RegionalConversion.FormatSQLDate(SessionManager.SelectedValue3)
                End If

                Dim objDT As DataTable = TeamOPIValues.SelectTeamOPIReportDetailByDate(SessionManager.SelectedValue1, SessionManager.SelectedValue2, strDateHolder)

                'only bind if we have a table
                If objDT IsNot Nothing Then
                    If objDT.Rows.Count > 1 Then
                        grdReportSummary.DataSource = objDT
                        grdReportSummary.DataBind()
                    Else
                        grdReportSummary.Visible = False
                        lnkPrintPage.Visible = False
                        lblNoData.Visible = True
                    End If
                Else
                    grdReportSummary.Visible = False
                    lnkPrintPage.Visible = False
                    lblNoData.Visible = True
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindGrid", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
            End Try
        End Sub
        Private Sub ConfigureParameterColumns()
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
                Dim objDT As DataTable = TeamOPI.SelectTeamOPI(SessionManager.SelectedTeamID, SessionManager.SelectedValue2)
                If objDT Is Nothing OrElse objDT.Rows.Count <> 1 Then
                    Return
                End If

                Dim dr As DataRow = objDT.Rows(0)
                Dim dtColumn As BoundField

                'First, add the Date Column
                dtColumn = New BoundField
                dtColumn.HeaderText = "Date"
                dtColumn.DataField = "OPIDate"

                'determine how the column should be formmated
                Select Case dr("TimeEntryRequired").ToString
                    Case "True"
                        dtColumn.DataFormatString = "{0:" + SessionManager.DateTimeFormat + "}"
                    Case "False"
                        dtColumn.DataFormatString = "{0:" + SessionManager.DateFormat + "}"
                End Select
                grdReportSummary.Columns.Add(dtColumn)

                'cycle through the paramters and add a column to the grid for each one
                Dim iCounter As Integer
                For iCounter = 1 To 6
                    If IsDBNull(dr("Attribute" + iCounter.ToString)) Then
                        'nothing
                        Exit For
                    Else
                        dtColumn = New BoundField
                        dtColumn.HeaderText = dr("Attribute" + iCounter.ToString)
                        dtColumn.DataField = "Attribute" + iCounter.ToString + "Value"

                        Select Case dr("Attribute" & iCounter.ToString & "EntryType").ToString
                            Case "N"
                                dtColumn.DataFormatString = "{0:F0}"
                            Case "D"
                                dtColumn.DataFormatString = "{0:F" & dr("Attribute" & iCounter.ToString & "Size") & "}"
                        End Select

                        grdReportSummary.Columns.Add(dtColumn)
                    End If
                Next iCounter

                'now, add the Value and Notes columns
                'Value
                dtColumn = New BoundField
                dtColumn.HeaderText = "OPI Value"
                dtColumn.DataField = "OPIValue"

                'determine how the column should be formmated
                Select Case dr("OPIEntryType").ToString
                    Case "D"
                        dtColumn.DataFormatString = "{0:F" + dr("OPISize").ToString + "}"
                    Case "N"
                        dtColumn.DataFormatString = "{0:F0}"
                End Select

                grdReportSummary.Columns.Add(dtColumn)

                'cost
                dtColumn = New BoundField
                dtColumn.HeaderText = "Cost"
                dtColumn.DataField = "Cost"
                grdReportSummary.Columns.Add(dtColumn)

                'Benefit
                dtColumn = New BoundField
                dtColumn.HeaderText = "Benefit"
                dtColumn.DataField = "Benefit"
                dtColumn.DataFormatString = "{0:F2}"
                grdReportSummary.Columns.Add(dtColumn)

                'Benefit Percentage
                dtColumn = New BoundField
                dtColumn.HeaderText = "Benefit %"
                dtColumn.DataField = "BenefitPercentage"
                dtColumn.DataFormatString = "{0:F4}"
                grdReportSummary.Columns.Add(dtColumn)

                'Notes
                dtColumn = New BoundField
                dtColumn.HeaderText = "Notes"
                dtColumn.DataField = "Notes"
                grdReportSummary.Columns.Add(dtColumn)
            Catch Exc As Exception
                Throw
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
                Dim iCounter As Integer
                Dim strHolder As String
                Dim objColumn As BoundField

                strHolder = "<table cellspacing='0' rules='all' border='1' id='grdReportSummary' style='width:100%;border-collapse:collapse;'>"
                strHolder += "<tr style='color:White;background-color:DarkBlue;font-weight:bold;'>"

                For iCounter = 0 To grdReportSummary.Columns.Count - 1
                    strHolder += "<td>" + grdReportSummary.Columns(iCounter).HeaderText + "</td>"
                Next
                strHolder += "</tr>"

                Dim objDR As DataRow
                For Each objDR In grdReportSummary.DataSource.rows
                    strHolder += "<tr>"
                    For Each objColumn In grdReportSummary.Columns
                        strHolder += "<td>" + objDR(objColumn.DataField).ToString + "</td>"
                    Next
                    strHolder += "</tr>"
                Next
                strHolder += "</table>"
                SessionManager.ExportString = strHolder
                Response.Redirect(Request.ApplicationPath.ToString + "/UI/UserControls/Export.aspx")
            Catch Exc As Exception
                Throw
            End Try
        End Sub
#End Region

    End Class
End Namespace
