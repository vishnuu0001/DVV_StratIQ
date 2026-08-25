#Region " Imports "
Imports System.IO
Imports System.Data
Imports System.Drawing
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper
Imports WebApp.APlus.UI
Imports WebApp.APlus.UI.CustomControls
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class TeamMeetingAttendance3
        Inherits PrinterFriendlyBase

#Region " Protected Variables"
        Private Shared ReadOnly ProgramName As String = "TeamMeetingAttendance3"
#End Region

#Region " Load Culture Translations"
        Private Sub LoadCultureTranslations()
            lblAttendance1.Text = GetTranslationString("attendance", lblAttendance1.Text)
            lblAttended1.Text = GetTranslationString("attended", lblAttended1.Text)
            lblAbsent1.Text = GetTranslationString("absent", lblAbsent1.Text)
            For i As Integer = 0 To gvTeamMeetingAttendance.Columns.Count - 1
                gvTeamMeetingAttendance.Columns(i).HeaderText = GetTranslationString(gvTeamMeetingAttendance.Columns(i).HeaderText, gvTeamMeetingAttendance.Columns(i).HeaderText)
            Next
        End Sub
#End Region

#Region " Event Handlers "
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Master.AddBodyAttribute("onkeydown", "javascript:DisableFunctionKeys(window.event);")
            If SessionManager.SelectedTeamID = 0 Then
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamRouteSteps1"), False)
                Return
            End If

            If Not Page.IsPostBack Then
                LoadCultureTranslations()
            End If

            lblTeamName.Text = SessionManager.SelectedTeamName
            lblTeam.Text = SessionManager.SelectedTeam
            SelectTeamMeetingAttendanceByTeam()
            If Directory.Exists(ConfigurationManager.AppSettings("TeamAttachmentsRootDirectory") & lblTeam.Text) Then
                Dim di As DirectoryInfo = New DirectoryInfo(ConfigurationManager.AppSettings("TeamAttachmentsRootDirectory") & lblTeam.Text)
                Dim files As FileInfo()
                files = di.GetFiles("*TeamPhoto*")
                If files.GetLength(0) > 0 Then
                    imgTeamPhoto.ImageUrl = "http://" & ConfigurationManager.AppSettings("ApplicationServerDNS").ToString & ConfigurationManager.AppSettings("TeamAttachmentsVirtualRootDirectory") & lblTeam.Text & "/" & files(0).Name
                Else
                    'todo: Put in TeamPhoto NotFound .gif or .bmp
                    imgTeamPhoto.AlternateText = "Attachment TeamPhoto not found"
                End If
            Else
                'todo: Put in Team directory no found
                imgTeamPhoto.AlternateText = "Attachment TeamPhoto not found"
            End If
            lblPrintDate.Text = GetTranslationString("printed", "Printed") & ": " & Now.ToLongDateString & "   " & Now.ToLongTimeString
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub SelectTeamMeetingAttendanceByTeam()
            Try
                Dim bShowAll As Boolean
                If IsNothing(SessionManager.ShowAttendance) Then
                    bShowAll = True
                Else
                    bShowAll = (SessionManager.ShowAttendance = "All")
                End If

                Dim dt As DataTable = TeamMeetingAttendance.SelectTeamMeetingAttendanceByTeam(SessionManager.SelectedTeamID, bShowAll, True)
                Dim dc As DataColumn
                Dim dtCol As BoundField
                Dim strDate As String
                Dim iRowCount As Integer = 1
                Dim strMeetingDate() As String

                Dim iMeetingsCount As Integer = TeamMeetings.GetTeamMeetingsCount(SessionManager.SelectedTeamID)
                If iMeetingsCount > 12 Then
                    lblAttendance.Text = "Last 12 of " & iMeetingsCount.ToString & " Meetings"
                    lblAttendance.Visible = True
                End If

                For Each dc In dt.Columns
                    Select Case dc.ColumnName
                        Case "Team", "UserID", "UserName", "Title", "Role", "SortOrder"
                            'we don't care about these
                        Case Else
                            If iRowCount > dt.Columns.Count - 12 Then
                                dtCol = New BoundField
                                dtCol.HtmlEncode = True
                                strMeetingDate = dc.ColumnName.Split("|")
                                dtCol.HeaderText = strMeetingDate(1)
                                dtCol.SortExpression = strMeetingDate(0)
                                dtCol.DataField = dc.ColumnName
                                dtCol.HeaderStyle.Width = New Unit(30, UnitType.Pixel)
                                dtCol.HtmlEncode = False
                                strDate = dtCol.HeaderText.ToString
                                Dim strYear As String
                                Dim strTime As String = Right(dtCol.DataField.ToString, 5)
                                If IsDate(strDate) Then
                                    strYear = Convert.ToDateTime(strDate).ToString("yyyy")
                                    strDate = Replace(Convert.ToDateTime(strDate).ToString("MMM d"), " ", "&nbsp;")
                                    dtCol.HeaderText = strYear & " " & strDate.Replace(" ", "&nbsp;") & " " & strTime
                                End If
                                gvTeamMeetingAttendance2.Columns.Add(dtCol)
                            End If
                    End Select

                    iRowCount += 1
                Next dc
                gvTeamMeetingAttendance.DataSource = dt
                gvTeamMeetingAttendance.DataBind()
                gvTeamMeetingAttendance2.DataSource = dt
                gvTeamMeetingAttendance2.DataBind()

                Dim iCellOffset As Integer = 6

                'if we have more than 12 meetings than the offset needs to be modified
                If dt.Columns.Count > 18 Then
                    iCellOffset = dt.Columns.Count - 12
                End If

                For Each item As GridViewRow In gvTeamMeetingAttendance.Rows
                    For Each cell As TableCell In item.Cells
                        cell.HorizontalAlign = HorizontalAlign.Left
                        cell.VerticalAlign = VerticalAlign.Middle
                        cell.BorderStyle = BorderStyle.Solid
                        cell.BorderWidth = New Unit(1)
                    Next
                Next

                For Each item As GridViewRow In gvTeamMeetingAttendance2.Rows
                    For Each cell As TableCell In item.Cells
                        cell.HorizontalAlign = HorizontalAlign.Center
                        cell.BorderStyle = BorderStyle.Solid
                        cell.BorderWidth = New Unit(1)

                        Dim i As Integer = item.Cells.GetCellIndex(cell) + iCellOffset
                        strMeetingDate = dt.Columns(i).ColumnName.ToString.Split("|")
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
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - SelectTeamMeetingAttendanceByTeam", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

    End Class
End Namespace
