#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.DataAccess.Custom
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class EventCalendar
        Inherits ApplicationBase

#Region " Constants"
        Private Shared ReadOnly FormName As String = "Event Calendar"
        Private Shared ReadOnly ProgramName As String = "EventCalendar"
        Private ckEvents As Collection = New Collection
#End Region

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            'Put user code to initialize the page here
            Master.HeaderMessage = FormName
            Master.IconImage = Request.ApplicationPath + "/images/Scheduled Tasks.gif"
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnExit.UniqueID + "'),window.event)")

            If Not IsPostBack Then
                ddlRoomGroups.Items.Clear()
                RoomGroupMaster.SelectRoomGroupMasterList(SessionManager.WorkingSiteID, ddlRoomGroups)

                If Not IsNothing(Request.Cookies("Teams")) Then
                    Try
                        rblTeams.SelectedValue = Request.Cookies("Teams").Value
                    Catch ex As Exception
                    End Try
                End If
                If Not IsNothing(Request.Cookies("Meetings")) Then
                    Try
                        rblReservations.SelectedValue = Request.Cookies("Meetings").Value
                        If rblReservations.SelectedValue = "GroupReservations" Then
                            ddlRoomGroups.Visible = True
                        End If
                    Catch ex As Exception
                    End Try
                End If
                If Not IsNothing(Request.Cookies("RoomGroup")) Then
                    Try
                        ddlRoomGroups.Items.FindByValue(Request.Cookies("RoomGroup").Value).Selected = True
                    Catch ex As Exception
                        ddlRoomGroups.SelectedIndex = 0
                    End Try
                End If

                If SessionManager.SelectedTeamID = 0 Then
                    If rblTeams.SelectedValue = "SelectedTeam" Then
                        rblTeams.SelectedValue = "MyTeams"
                    End If
                    rblTeams.Items.RemoveAt(3)
                End If

                calEvents.VisibleDate = Now.Date

                Dim startDate As DateTime = New DateTime(calEvents.VisibleDate.Year, calEvents.VisibleDate.Month, 1).AddDays(-7)
                Dim endDate As DateTime = New DateTime(calEvents.VisibleDate.Date.AddMonths(1).Year, calEvents.VisibleDate.Date.AddMonths(1).Month, 1).AddDays(7)
                calEvents.DataSource = GetEventData(startDate, endDate)
            End If
        End Sub
        Protected Sub RadioButtonChange(ByVal sender As Object, ByVal e As System.EventArgs) Handles rblTeams.SelectedIndexChanged, rblReservations.SelectedIndexChanged
            If rblReservations.SelectedItem.Value = "GroupReservations" Then
                ddlRoomGroups.Visible = True
            Else
                ddlRoomGroups.Visible = False
            End If

            Dim startDate As DateTime = New DateTime(calEvents.VisibleDate.Year, calEvents.VisibleDate.Month, 1).AddDays(-7)
            Dim endDate As DateTime = New DateTime(calEvents.VisibleDate.Date.AddMonths(1).Year, calEvents.VisibleDate.Date.AddMonths(1).Month, 1).AddDays(7)

            calEvents.DataSource = GetEventData(startDate, endDate)
        End Sub
        Protected Sub ddlRoomGroups_SelectedIndexChanged(ByVal sender As Object, ByVal e As System.EventArgs) Handles ddlRoomGroups.SelectedIndexChanged
            Dim startDate As DateTime = New DateTime(calEvents.VisibleDate.Year, calEvents.VisibleDate.Month, 1).AddDays(-7)
            Dim endDate As DateTime = New DateTime(calEvents.VisibleDate.Date.AddMonths(1).Year, calEvents.VisibleDate.Date.AddMonths(1).Month, 1).AddDays(7)

            calEvents.DataSource = GetEventData(startDate, endDate)
        End Sub
        Private Sub calEvents_VisibleMonthChanged(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.MonthChangedEventArgs) Handles calEvents.VisibleMonthChanged
            Try
                Dim startDate As DateTime = e.NewDate.AddDays(-7)
                Dim endDate As DateTime = e.NewDate.AddMonths(1).AddDays(7)
                calEvents.DataSource = GetEventData(startDate, endDate)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - calEvents_VisibleMonthChanged", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub calEvents_AfterDayRender(ByVal cell As System.Web.UI.WebControls.TableCell, ByVal objdv As System.Data.DataView) Handles calEvents.AfterDayRender
            Try
                Dim ctlLink As System.Web.UI.WebControls.HyperLink
                Dim ctlObject As System.Web.UI.HtmlControls.HtmlGenericControl
                Dim strHolder As String

                If objdv.Count > 0 Then
                    ctlObject = New HtmlGenericControl
                    ctlObject.InnerHtml = "<BR>"

                    cell.Controls.Add(ctlObject)
                End If

                For Each objdr As DataRowView In objdv
                    Select Case objdr("EventType").ToString
                        Case "TeamMeeting"
                            ctlLink = New HyperLink
                            If (objdr("Audit") IsNot DBNull.Value) Then
                                If objdr("Audit") = True Then
                                    strHolder = Left(objdr("TeamName").ToString, 10) & " - Audit"
                                Else
                                    strHolder = Left(objdr("TeamName").ToString, 15)
                                End If
                            Else
                                strHolder = Left(objdr("TeamName").ToString, 15)
                            End If

                            If objdr("EventTime").ToString.Trim.Length > 0 Then
                                strHolder = objdr("EventTime").ToString + " " + strHolder
                            End If

                            ctlLink.Text = " " + strHolder + "<BR>"
                            strHolder = Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamMeetings3")
                            strHolder += "?MeetingID=" + objdr("CalendarEventID").ToString.Trim

                            ctlLink.NavigateUrl = strHolder
                            ctlLink.ToolTip = objdr("Team") & " - " & objdr("TeamName")
                            ctlLink.Target = "_blank"

                            cell.Controls.Add(ctlLink)
                        Case "Room"
                            ctlLink = New HyperLink
                            strHolder = objdr("Event").ToString

                            If objdr("EventTime").ToString.Trim.Length > 0 Then
                                strHolder = objdr("EventTime").ToString + " " + strHolder
                            End If

                            ctlLink.Text = " " + strHolder + "<BR>"
                            strHolder = Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RoomReservations3")
                            strHolder += "?RoomReservationID=" + objdr("Audit").ToString

                            ctlLink.NavigateUrl = strHolder
                            If objdr("EventDescription").ToString.Length > 0 Then
                                ctlLink.ToolTip = objdr("EventDescription").ToString
                            Else
                                ctlLink.ToolTip = objdr("Event").ToString
                            End If
                            ctlLink.Target = "_blank"

                            cell.Controls.Add(ctlLink)
                        Case Else
                            ctlLink = New HyperLink
                            strHolder = objdr("Event").ToString

                            If objdr("EventTime").ToString.Trim.Length > 0 Then
                                strHolder = objdr("EventTime").ToString + " " + strHolder
                            End If

                            Dim strSessionID As String = Session.SessionID.ToString
                            strSessionID = "(S(" + strSessionID + "))"

                            ctlLink.Text = " " + strHolder + "<BR>"
                            strHolder = Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar + strSessionID + Path.AltDirectorySeparatorChar + ProgramSecurity.GetProgramURL("CalendarEvents3")
                            'strHolder += "?EventSiteID=" + objdr("SiteID").ToString + "&EventType=" + objdr("EventType") + "&Event=" + objdr("Event").ToString + "&EventDate=" + objdr("EventDate").ToString
                            strHolder += "?CalendarEventID=" + objdr("CalendarEventID").ToString
                            ctlLink.NavigateUrl = strHolder
                            If objdr("EventDescription").ToString.Length > 0 Then
                                ctlLink.ToolTip = objdr("EventDescription").ToString
                            Else
                                ctlLink.ToolTip = objdr("Event").ToString
                            End If
                            ctlLink.Target = "_blank"

                            cell.Controls.Add(ctlLink)
                    End Select
                Next objdr
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - calEvents_AfterDayRender", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Protected Sub btnRoomReservations_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnRoomReservations.Click
            SessionManager.MasterControlExitProgram = "EventCalendar1"
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RoomReservations1"), False)
        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click
            RemoveCurrentProgramandGoBack()
        End Sub
#End Region

#Region " Custom Methods"
        Function GetEventData(ByVal startDate As DateTime, ByVal endDate As DateTime) As DataTable
            Dim objDT As New DataTable

            Try
                Dim bShowMyTeams As Boolean = False
                Dim bShowAllTeams As Boolean = False
                Dim strSelectedTeam As String = ""
                Dim strEvents As String = ""
                Dim bShowReservations As Boolean = False
                Dim iReservations As Integer = 0
                Dim cookie As HttpCookie

                Select Case rblTeams.SelectedItem.Value
                    Case "MyTeams"
                        bShowMyTeams = True
                    Case "AllTeams"
                        bShowAllTeams = True
                    Case "SelectedTeam"
                        bShowAllTeams = True
                        strSelectedTeam = Session("SelectedTeam")
                    Case "NoTeams"
                End Select

                'create cookie for team options
                cookie = New HttpCookie("Teams", rblTeams.SelectedItem.Value)
                cookie.Expires = DateTime.Now.AddHours(72)
                Response.Cookies.Add(cookie)

                Select Case rblReservations.SelectedItem.Value
                    Case "MyReservations"
                        iReservations = 1
                    Case "NoReservations"
                        iReservations = 0
                    Case "GroupReservations"
                        iReservations = -1
                End Select

                'create cookie for meeting options
                cookie = New HttpCookie("Meetings", rblReservations.SelectedItem.Value)
                cookie.Expires = DateTime.Now.AddHours(72)
                Response.Cookies.Add(cookie)

                'create cookie for Room Group
                If ddlRoomGroups.SelectedItem IsNot Nothing Then
                    cookie = New HttpCookie("RoomGroup", ddlRoomGroups.SelectedItem.Value)
                    cookie.Expires = DateTime.Now.AddHours(72)
                    Response.Cookies.Add(cookie)
                End If

                objDT = CalendarEvents.SelectCalendarEvents(SessionManager.UserID, RegionalConversion.FormatSQLDate(startDate), RegionalConversion.FormatSQLDate(endDate), SessionManager.WorkingSiteID, bShowMyTeams, bShowAllTeams, strSelectedTeam, iReservations, ddlRoomGroups.SelectedItem.Value)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - GetEventData", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
            End Try

            Return objDT
        End Function
#End Region

    End Class
End Namespace
