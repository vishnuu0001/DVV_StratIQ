#Region " Imports "

Imports System.IO
Imports System.Data
Imports System.Drawing
Imports WebApp.APlus.UI
Imports WebApp.APlus.UI.CustomControls
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class TeamRouteSteps3
        Inherits PrinterFriendlyBase

#Region " Private Variables "
        Private objPlannedColor As Color = System.Drawing.Color.MistyRose
        Private objActualColor As Color = System.Drawing.Color.LightSteelBlue
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
                lblMasterPlan.Text = GetTranslationString("masterplan", lblMasterPlan.Text)
                lblPlanned.Text = GetTranslationString("planned", lblPlanned.Text)
                lblActual.Text = GetTranslationString("actual", lblActual.Text)
            Catch Exc As Exception
                Master.DisplayErrors("TeamRouteSteps3 - LoadCultureTranslations", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

#Region " Event Handlers "
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "TeamRouteSteps3", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.SelectedTeamID = 0 Then
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamRouteSteps1"), False)
                Return
            End If

            If Not Page.IsPostBack Then
                LoadCultureTranslations()
                BindRouteStepsGrid()
            End If

            PlannedCell.BackColor = objPlannedColor
            PlannedCell.HorizontalAlign = HorizontalAlign.Center
            PlannedCell.Text = "P"
            ActualCell.BackColor = objActualColor
            ActualCell.HorizontalAlign = HorizontalAlign.Center
            ActualCell.Text = "A"

            lblPrintDate.Text = GetTranslationString("printed", "Printed") & ": " & Now.ToLongDateString
        End Sub
        Private Sub BindRouteStepsGrid()
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
                'control references
                Dim objDS As DataTable = TeamRouteSteps.SelectTeamRouteStepsChart(SessionManager.SelectedTeamID)
                Dim iRowCount As Integer
                Dim strHolder As String
                Dim strMasterPlanType As String = Teams.GetMasterPlanType(SessionManager.SelectedTeamID)

                'first, if the dataset if empty, get out of here
                If objDS Is Nothing Or objDS.Rows.Count = 0 Then
                    'not good
                    lblRoute.Text = GetTranslationString("norouteinformationassigedtothisteam", "No Route information assigned to this Team.")
                    Return
                End If


                iRowCount = (objDS.Columns.Count / 2) - 2
                If iRowCount = 0 Then
                    lblRoute.Text = GetTranslationString("noplannedoractualdateinformationavailable", "No Planned or Actual Date information available.")
                Else
                    Dim dt1 As New DataTable
                    Dim dr As DataRow
                    Dim _itemIndex As Integer = 0
                    Dim _rowIndex As Integer = 0

                    lblRoute.Text = "Route : " + objDS.Rows(0)("RouteAbbrev") + " - " + objDS.Rows(0)("Route")

                    'plug in the team
                    lblTeamName.Text = SessionManager.SelectedTeamName
                    lblTeam.Text = SessionManager.SelectedTeam


                    'determine if we were sent back weeks or months
                    Dim bUse1Months As Boolean = False
                    Dim dtOne1 As Date = CDate(Replace(objDS.Columns(4).ColumnName, "-P", ""))
                    Dim dtTwo1 As Date = CDate(Replace(objDS.Columns(6).ColumnName, "-P", ""))
                    'if the two dates are MORE than a week apart then this is a month view
                    If DateDiff(DateInterval.Day, dtOne1, dtTwo1) > 7 Then
                        bUse1Months = True
                    End If
                    Dim strWeekHolder As String
                    Dim cal As System.Globalization.Calendar = System.Globalization.CultureInfo.CurrentCulture.Calendar
                    For iRowCount = 4 To objDS.Columns.Count - 1 Step 2
                        strHolder = Replace(objDS.Columns(iRowCount).ColumnName, "-P", "")
                        If IsDate(strHolder) Then
                            If bUse1Months Then
                                strHolder = Convert.ToDateTime(strHolder).ToString("MMM yyyy")
                            Else
                                If strMasterPlanType = "D" Then
                                    strHolder = Convert.ToDateTime(strHolder).ToString("MMM d")
                                Else
                                    strWeekHolder = cal.GetWeekOfYear(Convert.ToDateTime(strHolder), Globalization.CalendarWeekRule.FirstFourDayWeek, DayOfWeek.Monday).ToString
                                    strHolder = "Week " + strWeekHolder
                                End If
                            End If
                        End If
                        dt1.Columns.Add(New DataColumn(strHolder, GetType(String)))
                        _rowIndex = 0
                        For i As Integer = 0 To objDS.Columns(iRowCount).Table.Rows.Count - 1
                            If dt1.Rows.Count > 0 AndAlso dt1.Rows.Count = (objDS.Columns(iRowCount).Table.Rows.Count * 2) Then
                                If i = 0 Then
                                    _rowIndex += 1
                                    If objDS.Columns(iRowCount).Table.Rows(i).Item(iRowCount).ToString = "False" Then
                                        dt1.Rows(i).Item(_itemIndex) = "0"
                                    Else
                                        dt1.Rows(i).Item(_itemIndex) = "1"
                                    End If
                                    If objDS.Columns(iRowCount + 1).Table.Rows(i).Item(iRowCount + 1).ToString = "False" Then
                                        dt1.Rows(_rowIndex).Item(_itemIndex) = "0"
                                    Else
                                        dt1.Rows(_rowIndex).Item(_itemIndex) = "2"
                                    End If
                                Else
                                    _rowIndex += 1
                                    If objDS.Columns(iRowCount).Table.Rows(i).Item(iRowCount).ToString = "False" Then
                                        dt1.Rows(_rowIndex).Item(_itemIndex) = "0"
                                    Else
                                        dt1.Rows(_rowIndex).Item(_itemIndex) = "1"
                                    End If
                                    _rowIndex += 1
                                    If objDS.Columns(iRowCount + 1).Table.Rows(i).Item(iRowCount + 1).ToString = "False" Then
                                        dt1.Rows(_rowIndex).Item(_itemIndex) = "0"
                                    Else
                                        dt1.Rows(_rowIndex).Item(_itemIndex) = "2"
                                    End If
                                End If
                            Else
                                dr = dt1.NewRow
                                If objDS.Columns(iRowCount).Table.Rows(i).Item(iRowCount).ToString = "False" Then
                                    dr(_itemIndex) = "0"
                                Else
                                    dr(_itemIndex) = "1"
                                End If
                                dt1.Rows.Add(dr)

                                dr = dt1.NewRow
                                If objDS.Columns(iRowCount + 1).Table.Rows(i).Item(iRowCount + 1).ToString = "False" Then
                                    dr(_itemIndex) = "0"
                                Else
                                    dr(_itemIndex) = "2"
                                End If
                                dt1.Rows.Add(dr)
                            End If
                        Next
                        _itemIndex += 1
                    Next

                    Dim dtColumn As BoundField
                    For Each col As DataColumn In dt1.Columns
                        dtColumn = New BoundField
                        dtColumn.HtmlEncode = True
                        dtColumn.DataField = col.ColumnName
                        dtColumn.HeaderStyle.Width = New Unit(15, UnitType.Pixel)
                        dtColumn.HeaderStyle.Height = New Unit(32, UnitType.Pixel)
                        dtColumn.HeaderStyle.HorizontalAlign = HorizontalAlign.Center
                        dtColumn.HeaderStyle.VerticalAlign = VerticalAlign.Middle
                        dtColumn.HeaderText = col.ColumnName
                        gvTeamMeetingAttendance2.Columns.Add(dtColumn)
                    Next

                    gvTeamMeetingAttendance2.DataSource = dt1
                    gvTeamMeetingAttendance2.DataBind()

                    gvTeamMeetingAttendance.DataSource = objDS
                    gvTeamMeetingAttendance.DataBind()

                    For Each item As GridViewRow In gvTeamMeetingAttendance2.Rows
                        For Each cell As TableCell In item.Cells
                            Select Case cell.Text
                                Case "1"
                                    cell.CssClass = "TeamMistyRoseCell"
                                    cell.Text = "P"
                                Case "2"
                                    cell.CssClass = "TeamLightSteelBlue"
                                    cell.Text = "A"
                                Case Else
                                    cell.CssClass = "TeamWhiteCell"
                                    cell.Text = "&nbsp;"
                            End Select
                        Next
                    Next
                End If
            Catch Exc As Exception
                Master.DisplayErrors("TeamRouteSteps3 - BindRouteStepsGrid", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

    End Class
End Namespace

