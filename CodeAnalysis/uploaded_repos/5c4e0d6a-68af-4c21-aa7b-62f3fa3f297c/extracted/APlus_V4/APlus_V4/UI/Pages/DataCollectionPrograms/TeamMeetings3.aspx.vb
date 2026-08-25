#Region " Imports "

Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports System.Diagnostics
Imports System.Web.Mail
Imports System.Text
Imports WebApp.APlus.DataAccess.Tables

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class TeamMeetings3
        Inherits PrinterFriendlyBase

#Region " Private Variables"
        Private iTeamMeetingID As Integer = 0
#End Region

#Region " Load Culture Translations"
        Private Sub LoadCultureTranslations()
            lblTeamMeeting.Text = GetTranslationString("team meetings", lblTeamMeeting.Text)
            lblMeetingDate.Text = GetTranslationString("meeting date", lblMeetingDate.Text.Replace(":", "")) & ":"
            lblMeetingTime.Text = GetTranslationString("meeting time", lblMeetingTime.Text.Replace(":", "")) & ":"
            lblMeetingLocation.Text = GetTranslationString("Meeting Location", lblMeetingLocation.Text.Replace(":", "")) & ":"
            lblAgenda.Text = GetTranslationString("agenda", lblAgenda.Text.Replace(":", "")) & ":"
            lblTeamMeetingAttendance.Text = GetTranslationString("team meeting attendance", lblTeamMeetingAttendance.Text.Replace(":", "")) & ":"
            lblMinutes.Text = GetTranslationString("minutes", lblMinutes.Text.Replace(":", "")) & ":"
            lblTeamActionPlan.Text = GetTranslationString("teamaction plan", lblTeamActionPlan.Text.Replace(":", "")) & ":"
            lblAgendaNextMeeting.Text = GetTranslationString("nextmeetagenda", lblAgendaNextMeeting.Text.Replace(":", "")) & ":"
            lblNextMeetingDate.Text = GetTranslationString("nextmeetdate", lblNextMeetingDate.Text.Replace(":", "")) & ":"
            lblMaintenanceUserID.Text = GetTranslationString("maintuserid", lblMaintenanceUserID.Text.Replace(":", "")) & ":"
            lblMaintenanceDate.Text = GetTranslationString("maintdate", lblMaintenanceDate.Text.Replace(":", "")) & ":"
            chkAudit.Text = GetTranslationString("audit", chkAudit.Text)
            For i As Integer = 0 To gvTeamMeetingAttendance.Columns.Count - 1
                gvTeamMeetingAttendance.Columns(i).HeaderText = GetTranslationString(gvTeamMeetingAttendance.Columns(i).HeaderText, gvTeamMeetingAttendance.Columns(i).HeaderText)
            Next
            For i As Integer = 0 To gvTeamActionPlan.Columns.Count - 1
                gvTeamActionPlan.Columns(i).HeaderText = GetTranslationString(gvTeamActionPlan.Columns(i).HeaderText, gvTeamActionPlan.Columns(i).HeaderText)
            Next
        End Sub
#End Region

#Region " Event Handler"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            If Not Page.IsPostBack Then
                LoadCultureTranslations()
            End If

            Master.AddBodyAttribute("onkeydown", "javascript:DisableFunctionKeys(window.event);")

            'before we do ANYTHING, determine if the page is called from event calendar
            If Request.Params("MeetingID") IsNot Nothing AndAlso IsNumeric(Request.Params("MeetingID")) Then
                iTeamMeetingID = Convert.ToInt16(Request.Params("MeetingID"))
            End If
            If SessionManager.UserID.Trim.Length = 0 Then
                Dim strUser As String = String.Empty
                strUser = Request("REMOTE_USER")
                If InStr(strUser, "\", CompareMethod.Binary) > 0 Then
                    strUser = strUser.Substring(InStr(strUser, "\", CompareMethod.Binary))
                End If

                SessionManager.UserID = strUser
            End If

            LoadSelectedRecord()
        End Sub
#End Region

#Region " Custom Events"
        Private Sub LoadSelectedRecord()
            Try
                Dim dt As DataTable = TeamMeetings.SelectTeamMeeting(iTeamMeetingID)
                If dt.Rows.Count <> 0 Then
                    Dim dr As DataRow = dt.Rows(0)

                    lblTeam.Text = dr("Team").ToString
                    lblTeamName.Text = Teams.GetTeamName(dr("TeamID").ToString)

                    If IsDate(dr("MeetingDate")) Then
                        txtMeetingDate.Text = Convert.ToDateTime("" + dr("MeetingDate")).ToShortDateString
                    Else
                        txtMeetingDate.Text = ""
                    End If

                    txtMeetingTime.Text = dr.Item("MeetingTime").ToString.Trim()
                    txtMeetingLocation.Text = dr.Item("MeetingLocation").ToString.Trim()
                    txtExpandAgenda.Text = dr.Item("Agenda").ToString.Trim()
                    txtExpandMinutes.Text = dr.Item("Highlights").ToString.Trim()
                    txtExpandAgendaNextMeeting.Text = dr.Item("AgendaNextMeeting").ToString.Trim()
                    chkAudit.Checked = dr.Item("Audit")
                    If IsDate(dr("NextMeetingDate")) Then
                        txtNextMeeting.Text = CDate(dr("NextMeetingDate")).ToShortDateString
                    Else
                        txtNextMeeting.Text = ""
                    End If
                    txtMaintenanceUserID.Text = dr.Item("MaintenanceUserID").ToString.Trim()
                    txtMaintenanceDate.Text = Convert.ToDateTime("" + dr.Item("MaintenanceDate")).ToShortDateString + " " + Convert.ToDateTime("" + dr.Item("MaintenanceDate")).ToString("HH:mm:ss")
                End If
            Catch Exc As Exception
                Master.WriteErrors("TeamMeetings3 - btnCheckAllAttended_Click", Exc, SessionManager.UserID)
            End Try

            LoadTeamMeetingAttendanceUpdate()
            SelectTeamActionPlansByMeetingDate()
        End Sub
        Private Sub LoadTeamMeetingAttendanceUpdate()
            Try
                Dim dt As DataTable = TeamMeetingAttendance.SelectTeamMeetingAttendance(iTeamMeetingID)
                gvTeamMeetingAttendance.DataSource = dt
                gvTeamMeetingAttendance.DataBind()
            Catch Exc As Exception
                Master.WriteErrors("TeamMeetings3 - btnCheckAllAttended_Click", Exc, SessionManager.UserID)
            End Try
        End Sub
        Private Sub SelectTeamActionPlansByMeetingDate()
            Try
                Dim dt As DataTable = TeamActionPlan.TeamActionPlansByMeetingDate(iTeamMeetingID)
                gvTeamActionPlan.DataSource = dt
                gvTeamActionPlan.DataBind()
            Catch Exc As Exception
                Master.WriteErrors("TeamMeetings3 - btnCheckAllAttended_Click", Exc, SessionManager.UserID)
            End Try
        End Sub
#End Region

    End Class
End Namespace

