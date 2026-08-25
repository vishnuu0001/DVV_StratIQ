#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports System.Diagnostics
Imports System.Net.Mail
Imports System.Text
Imports WebApp.APlus.Helper

Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.UI.CustomControls
Imports System.Collections.Generic

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class TeamMeetings2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Team Meetings"
        Private Shared ReadOnly ProgramName As String = "TeamMeetings2"
        Private Shared ReadOnly DBTableName As String = "TeamMeetings"
        Private blnAudit As Boolean
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel, btnExit}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel", "Exit"}
            Dim OutMessageArr() As String = {"", "", ""}
            Dim strDateFormat As String = SessionManager.DateFormat

            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)

            txtMeetingDate_CalendarExtender.Format = strDateFormat
            txtNextMeeting_CalendarExtender.Format = strDateFormat

            Dim objDT As DataTable = Teams.SelectTeams(SessionManager.SelectedTeamID)
            If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                SessionManager.SelectedValueTeamSiteID = objDT.Rows(0)("SiteID").ToString
            End If

            btnLookupRoom.Attributes.Add("onclick", "javascript:OpenLookupPage('../Lookup/RoomLookup.aspx');")

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnExit.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
        End Sub

        Private Sub LoadAddModeJavaScripts()
            Dim myTabArray() As Object = {txtMeetingDate, _
                                          ucMeetingTime.HoursDropdown, _
                                          ucMeetingTime.MinutesDropdown, _
                                          txtMeetingLength, _
                                          txtMeetingLocation, _
                                          txtExpandAgenda, _
                                          txtExpandMinutes, _
                                          txtExpandAgendaNextMeeting, _
                                          txtNextMeeting}

            Dim TabKeyDownArr() As String = {Tab(ucMeetingTime.HoursDropdown, txtNextMeeting, "No"), _
                                             Tab(ucMeetingTime.MinutesDropdown, txtMeetingDate, "No"), _
                                             Tab(txtMeetingLength, ucMeetingTime.HoursDropdown, "No"), _
                                             Tab(txtMeetingLocation, ucMeetingTime.MinutesDropdown, "No"), _
                                             Tab(txtExpandAgenda, txtMeetingLength, "No"), _
                                             Tab(txtExpandMinutes, txtMeetingLocation, "No"), _
                                             Tab(txtExpandAgendaNextMeeting, txtExpandAgenda, "No"), _
                                             Tab(txtNextMeeting, txtExpandMinutes, "No"), _
                                             Tab(txtMeetingDate, txtExpandAgendaNextMeeting, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {txtMeetingLength, _
                                          txtMeetingLocation, _
                                          txtExpandAgenda, _
                                          txtExpandMinutes, _
                                          txtExpandAgendaNextMeeting, _
                                          txtNextMeeting}

            Dim TabKeyDownArr() As String = {Tab(txtMeetingLocation, txtNextMeeting, "No"), _
                                             Tab(txtExpandAgenda, txtMeetingLength, "No"), _
                                             Tab(txtExpandMinutes, txtMeetingLocation, "No"), _
                                             Tab(txtExpandAgendaNextMeeting, txtExpandAgenda, "No"), _
                                             Tab(txtNextMeeting, txtExpandMinutes, "No"), _
                                             Tab(txtMeetingLength, txtExpandAgendaNextMeeting, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
#End Region

#Region " Load Culture Translations "
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
                lblMeetingDate.Text = GetTranslationString("meeting date", lblMeetingDate.Text.Replace(":", "")) & ":"
                lblMeetingTime.Text = GetTranslationString("meeting time", lblMeetingTime.Text.Replace(":", "")) & ":"
                lblDuration.Text = GetTranslationString("duration", lblDuration.Text.Replace(":", "")) & ":"
                chkAudit.Text = GetTranslationString("audit", chkAudit.Text)
                lblMeetingLocation.Text = GetTranslationString("Meeting Location", lblMeetingLocation.Text.Replace(":", "")) & ":"
                lblAgenda.Text = GetTranslationString("agenda", lblAgenda.Text.Replace(":", "")) & ":"
                lblMinutes.Text = GetTranslationString("minutes", lblMinutes.Text.Replace(":", "")) & ":"
                lblAgendaNextMeeting.Text = GetTranslationString("nextmeetingagenda", lblAgendaNextMeeting.Text.Replace(":", "")) & ":"
                Label2.Text = GetTranslationString("nextmeetingdate", Label2.Text.Replace(":", "")) & ":"
                lblMaintenanceUserID.Text = GetTranslationString("maintuserid", lblMaintenanceUserID.Text.Replace(":", "")) & ":"
                lblMaintenanceDate.Text = GetTranslationString("maintdate", lblMaintenanceDate.Text.Replace(":", "")) & ":"
                lblTeamMeetingAttendance.Text = GetTranslationString("team meeting attendance", lblTeamMeetingAttendance.Text.Replace(":", "")) & ":"
                lblTeamActionPlan.Text = GetTranslationString("teamaction plan", lblTeamActionPlan.Text.Replace(":", "")) & ":"
                chkSendMeetingStatusEmail.Text = GetTranslationString("sendmeetstatusmail", chkSendMeetingStatusEmail.Text)
                chkEmailInvited.Text = GetTranslationString("sendinvitedonly", chkEmailInvited.Text)
                lnkPrintPage.Text = GetTranslationString("printfriendlyversion", lnkPrintPage.Text)
                lnkAddToCalendar.Text = GetTranslationString("addtocalendar", lnkAddToCalendar.Text)
                Label3.Text = GetTranslationString("nextmeetdate", Label3.Text)
                btnConfirm.Text = GetTranslationString("yes", btnConfirm.Text)
                btnConfirmCancel.Text = GetTranslationString("no", btnConfirmCancel.Text)
                btnNewUserToAttendMeeting.Text = GetTranslationString("addnewuser", btnNewUserToAttendMeeting.Text)
                btnCheckAllAttended.Text = GetTranslationString("checkattended", btnCheckAllAttended.Text)
                btnRemoveUsers.Text = GetTranslationString("removeusers", btnRemoveUsers.Text)
                btnNewTeamActionPlan.Text = GetTranslationString("teamaction plan", btnNewTeamActionPlan.Text)
                btnCancel.Text = GetTranslationString("cancel", btnCancel.Text)
                btnReschedule.Text = GetTranslationString("resked", btnReschedule.Text)
                btnExit.Text = GetTranslationString("exit", btnExit.Text)
                btnReserveRoom.Text = GetTranslationString("reserveroom", btnReserveRoom.Text)
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

            If Not SessionManager.TeamMeetingsMode = String.Empty Then
                Master.HeaderMessage = GetTranslationString(FormName, FormName) & " - " & GetTranslationString(SessionManager.TeamMeetingsMode.Replace("Row", ""), SessionManager.TeamMeetingsMode.Replace("Row", ""))
            Else
                Master.HeaderMessage = GetTranslationString(FormName, FormName) & " - " & SessionManager.TeamMeetingsMode.Replace("Row", "")
            End If

            Master.IconImage = Request.ApplicationPath + "/images/UserMeeting.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not IsNothing(SessionManager.MasterControlExitProgram2) Then
                If SessionManager.MasterControlExitProgram2 <> "" Then
                    SessionManager.MasterControlExitProgram = SessionManager.MasterControlExitProgram2
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.MasterControlExitProgram2)
                End If
            End If

            If Not Page.IsPostBack Then
                Select Case SessionManager.TeamMeetingsMode.ToString()
                    Case "ViewRow"
                        btnLookupRoom.Visible = False
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                        lnkPrintPage.Visible = True
                        lnkAddToCalendar.Visible = True
                        SelectTeamActionPlansByMeetingDate()
                    Case "DeleteRow"
                        btnOK.Text = GetTranslationString("ok", btnOK.Text)
                        btnLookupRoom.Visible = False
                        LoadSelectedRecord()
                        UnEnableRecords()
                        SelectTeamActionPlansByMeetingDate()
                        pnlOKCancel.Visible = True
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Team Meeting.');")
                        TransactionHistory1.LockControl = True
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        btnOK.Text = GetTranslationString("saveandeditattendanceandactions", "Save and Edit Attendance And Actions")
                        btnOK.Width = New Unit(240)
                        LoadTeamMeetingAttendanceAdd()
                        LoadAddModeJavaScripts()
                        UnEnableRecords()
                        txtMeetingDate.Focus()
                        If SessionManager.TeamMeetingNewDate IsNot Nothing AndAlso SessionManager.TeamMeetingNewDate.Trim.Length > 0 Then
                            txtMeetingDate.Text = SessionManager.TeamMeetingNewDate
                        End If
                        If SessionManager.TeamMeetingNewAgenda IsNot Nothing AndAlso SessionManager.TeamMeetingNewAgenda.Trim.Length > 0 Then
                            txtExpandAgenda.Text = SessionManager.TeamMeetingNewAgenda
                        End If
                        SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamMeetingNewDate)
                        SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamMeetingNewAgenda)
                    Case "EditRow"
                        btnOK.Text = GetTranslationString("ok", btnOK.Text)
                        btnReschedule.Visible = True
                        btnReserveRoom.Visible = True
                        LoadEditModeJavaScripts()
                        LoadSelectedRecord()
                        UnEnableRecords()
                        SelectTeamActionPlansByMeetingDate()
                        txtMeetingLocation.Focus()
                    Case Else
                        RedirectToPriorProgram()
                End Select
            Else
                Select Case SessionManager.TeamMeetingsMode
                    Case "AddRow", "EditRow"
                        If SessionManager.LookupRoomItem IsNot Nothing AndAlso SessionManager.LookupRoomItem.Trim.Length > 0 Then
                            txtMeetingLocation.Text = SessionManager.LookupRoomItem
                            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.LookupRoomItem)
                        End If
                    Case Else
                End Select
            End If
        End Sub
        Private Sub btnOK_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim blnSuccess As Boolean

            Select Case SessionManager.TeamMeetingsMode
                Case "DeleteRow"
                    blnSuccess = DeleteTeamMeetings()
                Case "AddRow"
                    blnSuccess = InsertTeamMeetings()
                Case "EditRow"
                    blnSuccess = UpdateTeamMeetings()
            End Select

            'Post Processing
            Select Case SessionManager.TeamMeetingsMode
                Case "DeleteRow"
                    'do nothing here with attendance
                Case "AddRow"
                    blnSuccess = InsertTeamMeetingAttendance()
                    SessionManager.TeamMeetingsMode = "EditRow"
                    SessionManager.MeetingDate = txtMeetingDate.Text
                    SessionManager.MeetingTime = ucMeetingTime.Time
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamMeetings2"), False)
                    Return
                Case "EditRow"
                    blnSuccess = UpdateTeamMeetingAttendance()
                    If blnSuccess Then
                        If chkSendMeetingStatusEmail.Checked Then
                            SendMeetingStatusEmail()
                        End If
                    End If
                    If IsDate(txtNextMeeting.Text) Then
                        Dim strNextMeeting As String = RegionalConversion.FormatSQLDate(txtNextMeeting.Text)

                        Dim dtMeetings As DataTable = TeamMeetings.SelectTeamMeetingsByDateNoDDL(SessionManager.SelectedTeamID, strNextMeeting)
                        If dtMeetings.Rows.Count > 0 Then
                            'Team has meetings for this date, do nothing!
                        Else
                            pnlConfirm.Visible = True
                            pnlOKCancel.Visible = False
                            SessionManager.TeamMeetingsMode = "ViewRow"
                            SessionManager.CallingProgram = ""
                            LoadTeamMeetingAttendanceUpdate()
                            UnEnableRecords()
                            Return
                        End If
                    End If
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue2)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamMeetingsMode)

                If chkSendMeetingStatusEmail.Checked Then
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamMeetings1"), False)
                Else
                    RedirectToPriorProgram()
                End If
            End If
        End Sub
        Private Sub btnConfirm_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnConfirm.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.TeamMeetingsMode = "AddRow"
            SessionManager.TeamMeetingNewDate = txtNextMeeting.Text
            SessionManager.TeamMeetingNewAgenda = txtExpandAgendaNextMeeting.Text
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamMeetings2"), False)
        End Sub
        Private Sub btnConfirmCancel_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnConfirmCancel.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamMeetingsMode)
            RedirectToPriorProgram()
        End Sub
        Private Sub btnReserveRoom_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnReserveRoom.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            ValidateChanges()
            SessionManager.RoomReservationsMode = "AddTeamMeeting"
            SessionManager.SelectedValueLocation = txtMeetingLocation.Text
            SessionManager.SelectedValueDate = RegionalConversion.FormatSQLDate(txtMeetingDate.Text)
            SessionManager.SelectedValueDateTime = ucMeetingTime.Time
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RoomReservations2"), False)
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

            If SessionManager.TeamMeetingsMode = "EditRow" OrElse SessionManager.TeamMeetingsMode = "ViewRow" OrElse SessionManager.TeamMeetingsMode = "DeleteRow" OrElse SessionManager.TeamMeetingsMode = "AddRow" Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamMeetingsMode)
            End If
            RedirectToPriorProgram()
        End Sub
        Private Sub btnCancel_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnCancel.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamMeetingsMode)
            RedirectToPriorProgram()
        End Sub
        Private Sub btnNewTeamActionPlan_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnNewTeamActionPlan.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            ValidateChanges()
            SessionManager.MeetingDate = txtMeetingDate.Text.Trim
            SessionManager.MeetingTime = ucMeetingTime.Time
            SessionManager.TeamActionPlanMode = "AddMeeting"
            SessionManager.CallingProgram = "TeamMeetings2"
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamActionPlanMaintenance2"), False)
        End Sub
        Private Sub btnNewUserToAttendMeeting_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnNewUserToAttendMeeting.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            ValidateChanges()
            SessionManager.MeetingDate = txtMeetingDate.Text.Trim
            SessionManager.MeetingTime = ucMeetingTime.Time
            SessionManager.TeamMeetingAttendanceMode = "AddRow"
            SessionManager.CallingProgram = "TeamMeetings2"
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamMeetingAttendance2"), False)
        End Sub
        Private Sub btnRemoveUsers_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnRemoveUsers.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            ValidateChanges()
            SessionManager.MeetingDate = txtMeetingDate.Text.Trim
            SessionManager.MeetingTime = ucMeetingTime.Time
            SessionManager.CallingProgram = "TeamMeetings2"
            SessionManager.MasterControlExitProgram2 = SessionManager.MasterControlExitProgram
            SessionManager.MasterControlExitProgram = "TeamMeetings2"
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamMeetingAttendance4"), False)
        End Sub
        Private Sub btnReschedule_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnReschedule.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try
            SessionManager.MeetingDate = txtMeetingDate.Text.Trim
            SessionManager.MeetingTime = ucMeetingTime.Time
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamMeetings4"), False)
        End Sub
        Private Sub btnCheckAllAttended_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnCheckAllAttended.Click
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
                For Each obj As GridViewRow In gvTeamMeetingAttendance.Rows
                    If obj.RowType = DataControlRowType.DataRow Then CType(obj.FindControl("chkAttended"), CheckBox).Checked = True
                Next
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - btnCheckAllAttended_Click", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Protected Sub gvTeamMeetingAttendance_RowDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewRowEventArgs) Handles gvTeamMeetingAttendance.RowDataBound
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If e.Row.RowType = DataControlRowType.DataRow Then
                If SessionManager.TeamMeetingsMode = "ViewRow" OrElse SessionManager.TeamMeetingsMode = "DeleteRow" Then
                    CType(e.Row.FindControl("chkInvited"), CheckBox).Enabled = False
                    CType(e.Row.FindControl("chkAttended"), CheckBox).Enabled = False
                End If

            End If
        End Sub
#End Region

#Region " Custom Methods"
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
                Dim strDateHolder As String = RegionalConversion.FormatSQLDate(SessionManager.MeetingDate)
                Dim dt As DataTable = TeamMeetings.SelectTeamMeeting(SessionManager.TeamMeetingID)
                If dt.Rows.Count <> 0 Then
                    Dim dr As DataRow = dt.Rows(0)
                    If IsDate(dr("MeetingDate")) Then
                        txtMeetingDate.Text = Convert.ToDateTime("" + dr("MeetingDate")).ToShortDateString
                    Else
                        txtMeetingDate.Text = String.Empty
                    End If
                    ucMeetingTime.Time = dr.Item("MeetingTime").ToString.Trim()
                    txtMeetingTime.Text = dr.Item("MeetingTime").ToString.Trim()
                    txtMeetingLocation.Text = dr.Item("MeetingLocation").ToString.Trim()
                    txtExpandAgenda.Text = dr.Item("Agenda").ToString.Trim()
                    txtExpandMinutes.Text = dr.Item("Highlights").ToString.Trim()
                    txtExpandAgendaNextMeeting.Text = dr.Item("AgendaNextMeeting").ToString.Trim()
                    chkAudit.Checked = dr.Item("Audit")
                    txtMeetingLength.Text = dr("MeetingLength").ToString
                    If IsDate(dr("NextMeetingDate")) Then
                        txtNextMeeting.Text = CDate(dr("NextMeetingDate")).ToShortDateString
                    Else
                        txtNextMeeting.Text = String.Empty
                    End If
                    txtMaintenanceUserID.Text = dr.Item("MaintenanceUserID").ToString.Trim()
                    txtMaintenanceDate.Text = Convert.ToDateTime("" + dr.Item("MaintenanceDate")).ToShortDateString + " " + Convert.ToDateTime("" + dr.Item("MaintenanceDate")).ToString("HH:mm:ss")

                    Dim strHolder As String
                    Dim strSessionID As String = Session.SessionID.ToString
                    strSessionID = "(S(" + strSessionID + "))"
                    strHolder = Context.Request.ApplicationPath & "/" & strSessionID & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamMeetings3")
                    strHolder += "?MeetingID=" + SessionManager.TeamMeetingID.ToString
                    lnkPrintPage.NavigateUrl = strHolder
                    lnkPrintPage.Target = "_blank"

                    strHolder = Context.Request.ApplicationPath & "/UI/UserControls/TeamMeetingCalendarEvent.aspx"
                    strHolder += "?TeamMeetingID=" + SessionManager.TeamMeetingID.ToString
                    lnkAddToCalendar.NavigateUrl = strHolder
                    lnkAddToCalendar.Target = "_blank"

                    TransactionHistory1.TableName = DBTableName
                    TransactionHistory1.RecordID = SessionManager.TeamMeetingID

                    Dim objDic As New Dictionary(Of String, String)
                    objDic.Add("Team", SessionManager.SelectedTeam)
                    objDic.Add("MeetingDate", txtMeetingDate.Text.Trim())
                    objDic.Add("MeetingTime", txtMeetingTime.Text.Trim())
                    objDic.Add("MeetingLocation", txtMeetingLocation.Text.Trim())
                    objDic.Add("Agenda", txtExpandAgenda.Text.Trim())
                    objDic.Add("Highlights", txtExpandMinutes.Text.Trim())
                    objDic.Add("AgendaNextMeeting", txtExpandAgendaNextMeeting.Text.Trim())
                    objDic.Add("Audit", chkAudit.Checked)
                    objDic.Add("MeetingLength", txtMeetingLength.Text.Trim())
                    objDic.Add("NextMeetingDate", txtNextMeeting.Text.Trim())
                    SessionManager.RecordTransactionCurrentValues = objDic
                End If

                LoadTeamMeetingAttendanceUpdate()
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - SelectTeamMeeting", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub LoadTeamMeetingAttendanceAdd()
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
                Dim dt As DataTable = TeamMeetingAttendance.SelectTeamMeetingAttendanceAdd(SessionManager.SelectedTeamID)
                gvTeamMeetingAttendance.DataSource = dt
                gvTeamMeetingAttendance.DataBind()
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - SelectTeamMeetingAttendanceAdd", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub LoadTeamMeetingAttendanceUpdate()
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
                Dim dt As DataTable = TeamMeetingAttendance.SelectTeamMeetingAttendance(SessionManager.TeamMeetingID)
                gvTeamMeetingAttendance.DataSource = dt
                gvTeamMeetingAttendance.DataBind()
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - SelectTeamMeetingAttendance", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
            End Try
        End Sub
        Private Sub SelectTeamActionPlansByMeetingDate()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim strDateHolder As String = RegionalConversion.FormatSQLDate(SessionManager.MeetingDate)
            Try
                Dim dt As DataTable = TeamActionPlan.TeamActionPlansByMeetingDate(SessionManager.TeamMeetingID)
                gvTeamActionPlan.DataSource = dt
                gvTeamActionPlan.DataBind()
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - TeamActionPlansByMeetingDate", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub UnEnableRecords()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Select Case SessionManager.TeamMeetingsMode.ToString()
                Case "ViewRow", "DeleteRow"
                    pnlOKCancel.Visible = False
                    txtMeetingDate.ReadOnly = True
                    txtMeetingDate.CssClass = "Textbox_Display"
                    ucMeetingTime.Visible = False
                    txtMeetingTime.Visible = True
                    txtMeetingTime.ReadOnly = True
                    txtMeetingTime.CssClass = "Textbox_Display"
                    txtMeetingLocation.ReadOnly = True
                    txtMeetingLocation.CssClass = "Textbox_Display"
                    txtExpandAgenda.ReadOnly = True
                    txtExpandAgenda.CssClass = "Textbox_Display"
                    txtExpandMinutes.ReadOnly = True
                    txtExpandMinutes.CssClass = "Textbox_Display"
                    txtExpandAgendaNextMeeting.ReadOnly = True
                    txtExpandAgendaNextMeeting.CssClass = "Textbox_Display"
                    imgMeetingDate.Visible = False
                    txtMeetingDate_CalendarExtender.Enabled = False
                    lblTeamActionPlan.Visible = True
                    chkSendMeetingStatusEmail.Visible = False
                    chkSendMeetingStatusEmail.Enabled = False
                    chkEmailInvited.Visible = False
                    chkEmailInvited.Enabled = False
                    btnNewTeamActionPlan.Visible = False
                    btnNewTeamActionPlan.Enabled = False
                    btnNewUserToAttendMeeting.Visible = False
                    btnNewUserToAttendMeeting.Enabled = False
                    btnCheckAllAttended.Visible = False
                    btnCheckAllAttended.Enabled = False
                    btnRemoveUsers.Visible = False
                    btnRemoveUsers.Enabled = False
                    lblTeamMeetingAttendance.Visible = True
                    gvTeamMeetingAttendance.Visible = True
                    chkAudit.Visible = True
                    chkAudit.Enabled = False
                    txtMeetingLength.ReadOnly = True
                    txtMeetingLength.CssClass = "Textbox_Display"
                    txtNextMeeting.ReadOnly = True
                    txtNextMeeting.CssClass = "Textbox_Display"
                    imgNextMeeting.Visible = False
                    txtNextMeeting_CalendarExtender.Enabled = False
                Case "EditRow"
                    txtMeetingDate.ReadOnly = True
                    txtMeetingDate.CssClass = "Textbox_Display"
                    ucMeetingTime.Visible = False
                    txtMeetingTime.Visible = True
                    txtMeetingTime.ReadOnly = True
                    txtMeetingTime.CssClass = "Textbox_Display"
                    imgMeetingDate.Visible = False
                    txtMeetingDate_CalendarExtender.Enabled = False
                    lblTeamActionPlan.Visible = True
                    btnNewTeamActionPlan.Visible = True
                    btnNewTeamActionPlan.Enabled = True
                    chkSendMeetingStatusEmail.Visible = True
                    chkSendMeetingStatusEmail.Enabled = True
                    chkEmailInvited.Visible = True
                    chkEmailInvited.Enabled = True
                    btnNewUserToAttendMeeting.Visible = True
                    btnNewUserToAttendMeeting.Enabled = True
                    btnRemoveUsers.Visible = True
                    btnRemoveUsers.Enabled = True
                    chkAudit.Visible = True
                    chkAudit.Enabled = True
                Case "AddRow"
                    txtMeetingDate.CssClass = "Textbox_Entry"
                    txtMaintenanceUserID.Visible = False
                    txtMaintenanceDate.Visible = False
                    lblMaintenanceUserID.Visible = False
                    lblMaintenanceDate.Visible = False
                    imgMeetingDate.Visible = True
                    txtMeetingTime.Visible = False
                    lblTeamActionPlan.Visible = False
                    btnNewTeamActionPlan.Visible = False
                    btnNewTeamActionPlan.Enabled = False
                    chkSendMeetingStatusEmail.Visible = False
                    chkSendMeetingStatusEmail.Enabled = False
                    chkEmailInvited.Visible = False
                    chkEmailInvited.Enabled = False
                    btnNewUserToAttendMeeting.Visible = False
                    btnNewUserToAttendMeeting.Enabled = False
                    lblTeamMeetingAttendance.Visible = False
                    gvTeamMeetingAttendance.Visible = False
                    btnCheckAllAttended.Visible = False
                    btnCheckAllAttended.Enabled = False
                    btnRemoveUsers.Visible = False
                    btnRemoveUsers.Enabled = False
                    chkAudit.Visible = True
                    chkAudit.Enabled = True
            End Select
        End Sub
        Private Sub ValidateChanges()
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
                Dim strDateHolder As String = RegionalConversion.FormatSQLDate(SessionManager.MeetingDate)
                Dim dt As DataTable = TeamMeetings.SelectTeamMeeting(SessionManager.TeamMeetingID)
                Dim bChanged As Boolean = False
                Dim blnSuccess As Boolean
                If dt.Rows.Count <> 0 Then
                    Dim dr As DataRow = dt.Rows(0)
                    If txtMeetingLocation.Text.Trim <> dr.Item("MeetingLocation").ToString.Trim() Then
                        bChanged = True
                    ElseIf txtExpandAgenda.Text.Trim <> dr.Item("Agenda").ToString.Trim() Then
                        bChanged = True
                    ElseIf txtExpandMinutes.Text.Trim <> dr.Item("Highlights").ToString.Trim() Then
                        bChanged = True
                    ElseIf txtExpandAgendaNextMeeting.Text.Trim <> dr.Item("AgendaNextMeeting").ToString.Trim() Then
                        bChanged = True
                    ElseIf chkAudit.Checked <> dr.Item("Audit") Then
                        bChanged = True
                    End If
                    If IsDate(dr("NextMeetingDate")) Then
                        If txtNextMeeting.Text <> CDate(dr("NextMeetingDate")).ToShortDateString Then
                            bChanged = True
                        End If
                    Else
                        If txtNextMeeting.Text <> "" Then
                            bChanged = True
                        End If
                    End If
                End If

                If bChanged = True Then
                    blnSuccess = UpdateTeamMeetings()
                    If Not blnSuccess Then
                        Return
                    End If
                End If

                UpdateTeamMeetingAttendance()
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - ValidateChanges", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub SendMeetingStatusEmail()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            'SendS emails to users with valid EmailAddress
            Dim blnGoodToSendEmail As Boolean = False
            Dim strbTo As New System.Text.StringBuilder
            Dim strSubject As String = ""
            Dim strBody As String = ""
            strbTo.Append("")

            Try
                Dim strEmailAddress As String = ""
                Dim hEmail As New Hashtable
                Dim bValidUser As Boolean = False

                For Each obj As GridViewRow In gvTeamMeetingAttendance.Rows
                    bValidUser = False
                    strEmailAddress = obj.Cells(4).Text.Trim
                    If strEmailAddress <> "" And strEmailAddress <> "&nbsp;" Then
                        'If invited only option checked then verify user is invited
                        If Not chkEmailInvited.Checked Then
                            bValidUser = True
                        Else
                            If obj.Cells(2).Controls.Count > 0 Then
                                For Each objCtl As Control In obj.Cells(2).Controls
                                    If TypeOf objCtl Is CheckBox Then
                                        If DirectCast(objCtl, CheckBox).Checked Then
                                            bValidUser = True
                                        End If

                                        Exit For
                                    End If
                                Next
                            End If
                        End If

                        If bValidUser Then
                            Try
                                hEmail.Add(strEmailAddress, strEmailAddress)
                            Catch ex As Exception
                                'duplicate
                            End Try
                        End If
                    End If
                Next

                Dim myEnumerator As IDictionaryEnumerator = hEmail.GetEnumerator()
                While myEnumerator.MoveNext
                    strEmailAddress = myEnumerator.Key.ToString
                    strEmailAddress.Replace(" ", "_")

                    If Not blnGoodToSendEmail Then
                        strbTo.Append(strEmailAddress)
                    Else
                        strbTo.Append(", " & strEmailAddress)
                    End If
                    blnGoodToSendEmail = True
                End While

                Dim strDomain As String = ConfigurationManager.AppSettings("DefaultEmailFromDomain")
                SessionManager.TeamMeetingEmailFrom = Replace(SessionManager.SelectedTeam, " ", "_") & "@" & strDomain
                SessionManager.TeamMeetingEmailDateTime = RegionalConversion.FormatSQLDate(SessionManager.MeetingDate & " " & SessionManager.MeetingTime, True)
                Dim strMeetingDate As String = RegionalConversion.FormatSQLDate(txtMeetingDate.Text)
                If SessionManager.SelectedTeamName.Trim.Length > 50 Then
                    strSubject = SessionManager.SelectedTeam & " - " & SessionManager.SelectedTeamName.Substring(0, 50) & " - " & GetTranslationString("Meeting") & " - " & txtMeetingLocation.Text.Trim & " - " & strMeetingDate & " - " & ucMeetingTime.Time
                Else
                    strSubject = SessionManager.SelectedTeam & " - " & SessionManager.SelectedTeamName & " - " & GetTranslationString("Meeting") & " - " & txtMeetingLocation.Text.Trim & " - " & strMeetingDate & " - " & ucMeetingTime.Time
                End If

                strBody = SessionManager.SelectedTeam & "<br />" & SessionManager.SelectedTeamName & " Meeting" & vbCrLf
                strBody += "<br /><br />"
                strBody += "http://" & ConfigurationManager.AppSettings("ApplicationServerDNS").ToString & "/aplus/UI/Pages/DataCollectionPrograms/TeamMeetings3.aspx?MeetingID=" & SessionManager.TeamMeetingID.ToString
                strBody += "<br /><br />"

                Dim strURL As String = "http://" & ConfigurationManager.AppSettings("ApplicationServerDNS").ToString & "/aplus/login.aspx"
                strURL += "?auto=y&team=" & SessionManager.SelectedTeamID
                strBody += "<a href='" & strURL & "'>" & GetTranslationString("Click Here to view Team Status for") & ": " & SessionManager.SelectedTeam & "</a>"
                strBody += "<br /><br />"

                strURL = "http://" & ConfigurationManager.AppSettings("ApplicationServerDNS").ToString & "/aplus/UI/UserControls/TeamMeetingCalendarEvent.aspx"
                strURL += "?TeamMeetingID=" & SessionManager.TeamMeetingID.ToString
                strBody += "<a href='" & strURL & "'>" & GetTranslationString("Click Here to add this team meeting to your Outlook Calendar") & "</a>"

                Dim MailClient As New SmtpClient
                Dim msg As New MailMessage(Replace(SessionManager.SelectedTeam, " ", "_") & "@" & strDomain, strbTo.ToString.Trim, strSubject, strBody)
                MailClient.Host = ConfigurationManager.AppSettings("SMTPServer")
                msg.IsBodyHtml = True

                MailClient.Send(msg)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - SendMeetingStatusEmail", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub RedirectToPriorProgram()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.CallingProgram > "" Then
                Dim strCallingProgram As String = SessionManager.CallingProgram
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CallingProgram)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamMeetingsMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strCallingProgram), False)
            Else
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamMeetings1"), False)
            End If
        End Sub
        Private Function InsertTeamMeetings() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If Me.ucMeetingTime.SelectedHour = "" Or Me.ucMeetingTime.SelectedMinute = "" Then
                Master.DisplayError(GetTranslationString("invalidtime", "Invalid Time"))
                Return False
            End If

            Try
                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                Dim blnAudit As Boolean = CType((chkAudit), CheckBox).Checked
                Dim strMeetingDate As String = RegionalConversion.FormatSQLDate(txtMeetingDate.Text)
                Dim strNextMeeting As String = RegionalConversion.FormatSQLDate(txtNextMeeting.Text)

                SessionManager.TeamMeetingID = TeamMeetings.AddTeamMeetings(SessionManager.SelectedTeamID, strMeetingDate, _
                                                 ucMeetingTime.Time, txtMeetingLocation.Text, txtExpandAgenda.Text, _
                                                 txtExpandMinutes.Text, txtExpandAgendaNextMeeting.Text, blnAudit, _
                                                 txtMeetingLength.Text, strNextMeeting, SessionManager.UserID)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.TeamMeetingID, strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertTeamMeetings", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function InsertTeamMeetingAttendance() As Boolean
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
                Dim dt As DataTable = TeamMeetingAttendance.SelectTeamMeetingAttendanceAdd(SessionManager.SelectedTeamID)
                If dt.Rows.Count <> 0 Then
                    Dim strDateHolder As String = RegionalConversion.FormatSQLDate(txtMeetingDate.Text.Trim)
                    For Each dr As DataRow In dt.Rows
                        Dim objDic As New Dictionary(Of String, String)
                        objDic.Add("Team", SessionManager.SelectedTeam)
                        objDic.Add("TeamMeetingID", SessionManager.TeamMeetingID)
                        objDic.Add("UserID", dr.Item("UserID").Trim())
                        objDic.Add("UserName", dr.Item("UserName").Trim())
                        objDic.Add("Invited", dr.Item("Invited"))
                        objDic.Add("Attended", dr.Item("Attended"))
                        Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)
                        Dim intResult As Integer = TeamMeetingAttendance.AddTeamMeetingAttendance(SessionManager.SelectedTeamID, _
                                                                       SessionManager.TeamMeetingID, _
                                                                       dr.Item("UserID"), _
                                                                       dr.Item("UserName"), _
                                                                       dr.Item("Invited"), _
                                                                       dr.Item("Attended"), _
                                                                       SessionManager.UserID)

                        RecordTransactionHistory.InsertRecordTransactionHistory("TeamMeetingAttendance", intResult, strChangeLog, SessionManager.UserID)
                    Next
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertTeamMeetingAttendance", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
            Return True
        End Function
        Private Function UpdateTeamMeetings() As Boolean
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
                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.CompareDictionaryValues(SessionManager.RecordTransactionCurrentValues, objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                Dim blnAudit As Boolean = CType((chkAudit), CheckBox).Checked
                Dim strMeetingDate As String = RegionalConversion.FormatSQLDate(txtMeetingDate.Text)
                Dim strNextMeeting As String = RegionalConversion.FormatSQLDate(txtNextMeeting.Text)
                TeamMeetings.UpdateTeamMeetings(SessionManager.TeamMeetingID, _
                                                txtMeetingLocation.Text, _
                                                txtExpandAgenda.Text, _
                                                txtExpandMinutes.Text, _
                                                txtExpandAgendaNextMeeting.Text, _
                                                blnAudit, _
                                                txtMeetingLength.Text, _
                                                strNextMeeting, _
                                                SessionManager.UserID)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.TeamMeetingID, strChangeLog, SessionManager.UserID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateTeamMeetings", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
            Return True
        End Function
        Private Function UpdateTeamMeetingAttendance() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim strDateHolder As String = RegionalConversion.FormatSQLDate(txtMeetingDate.Text.Trim)
            Try
                For Each obj As GridViewRow In gvTeamMeetingAttendance.Rows
                    If obj.RowType = DataControlRowType.DataRow Then

                        Dim strUserID As String = gvTeamMeetingAttendance.DataKeys(obj.RowIndex)("UserID").ToString.Trim()
                        Dim strUserName As String = obj.Cells(1).Text
                        Dim blnInvited As Boolean = CType(obj.FindControl("chkInvited"), CheckBox).Checked
                        Dim blnAttended As Boolean = CType(obj.FindControl("chkAttended"), CheckBox).Checked
                        TeamMeetingAttendance.UpdateTeamMeetingAttendance(SessionManager.SelectedTeamID, _
                                                                          SessionManager.TeamMeetingID, _
                                                                          strUserID, _
                                                                          strUserName, _
                                                                          blnInvited, _
                                                                          blnAttended, _
                                                                          txtMaintenanceUserID.Text.Trim)
                        Dim dt As DataTable = TeamMeetingAttendance.SelectTeamMeetingAttendanceUser(SessionManager.TeamMeetingID, strUserName)
                        Dim objDic As New Dictionary(Of String, String)
                        objDic.Add("Team", SessionManager.SelectedTeam)
                        objDic.Add("TeamMeetingID", SessionManager.TeamMeetingID)
                        objDic.Add("UserID", strUserID)
                        objDic.Add("UserName", strUserName)
                        objDic.Add("Invited", blnInvited)
                        objDic.Add("Attended", blnAttended)
                        Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)
                        RecordTransactionHistory.InsertRecordTransactionHistory("TeamMeetingAttendance", dt.Rows(0).Item("TeamMeetingAttendanceID"), strChangeLog, SessionManager.UserID)
                    End If
                Next
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateTeamMeetingAttendance", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
            Return True
        End Function
        Private Function DeleteTeamMeetings() As Boolean
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
                Dim strMeetingDate As String = RegionalConversion.FormatSQLDate(txtMeetingDate.Text)
                TeamMeetings.DeleteTeamMeetings(SessionManager.TeamMeetingID)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.TeamMeetingID, "Team Meeting Deleted", SessionManager.UserID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteTeamMeetings", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
            Return True
        End Function
        Private Function GetUpdatedValues() As Dictionary(Of String, String)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim objDic As New Dictionary(Of String, String)
            objDic.Add("Team", SessionManager.SelectedTeam)
            objDic.Add("MeetingDate", RegionalConversion.FormatSQLDate(txtMeetingDate.Text))
            objDic.Add("MeetingTime", txtMeetingTime.Text.Trim())
            objDic.Add("MeetingLocation", txtMeetingLocation.Text.Trim())
            objDic.Add("Agenda", txtExpandAgenda.Text.Trim())
            objDic.Add("Highlights", txtExpandMinutes.Text.Trim())
            objDic.Add("AgendaNextMeeting", txtExpandAgendaNextMeeting.Text.Trim())
            objDic.Add("Audit", chkAudit.Checked)
            objDic.Add("MeetingLength", txtMeetingLength.Text.Trim())
            objDic.Add("NextMeetingDate", RegionalConversion.FormatSQLDate(txtNextMeeting.Text))

            Return objDic
        End Function
#End Region

    End Class
End Namespace

