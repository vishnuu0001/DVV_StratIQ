#Region " Imports "

Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports System.Diagnostics
Imports System.Web.Mail
Imports System.Text
Imports WebApp.APlus.Helper
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.UI.CustomControls
Imports System.Collections.Generic

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class TeamMeetings4
        Inherits ApplicationBase

#Region " Private Constants "
        Private Shared ReadOnly FormName As String = "Team Meetings"
        Private Shared ReadOnly ProgramName As String = "TeamMeetings4"
        Private Shared ReadOnly DBTableName As String = "TeamMeetings"
#End Region

#Region " JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel"}
            Dim OutMessageArr() As String = {"", ""}
            Dim strDateFormat As String = SessionManager.DateFormat
            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)
            txtMeetingDate_CalendarExtender.Format = strDateFormat
        End Sub

        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {txtMeetingDate, _
                                          ucMeetingTime.HoursDropdown, _
                                          ucMeetingTime.MinutesDropdown}

            Dim TabKeyDownArr() As String = {Tab(ucMeetingTime.HoursDropdown, ucMeetingTime.MinutesDropdown, "No"), _
                                             Tab(ucMeetingTime.MinutesDropdown, txtMeetingDate, "No"), _
                                             Tab(txtMeetingDate, ucMeetingTime.MinutesDropdown, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub

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
                Label1.Text = GetTranslationString("originalmeetdate", Label1.Text)
                Label2.Text = GetTranslationString("newmeetdate", Label2.Text)
                Label5.Text = GetTranslationString("meeting date", Label5.Text.Replace(":", "")) & ":"
                Label8.Text = GetTranslationString("meeting time", Label8.Text.Replace(":", "")) & ":"
                Label6.Text = GetTranslationString("meeting date", Label6.Text.Replace(":", "")) & ":"
                Label7.Text = GetTranslationString("meeting time", Label7.Text.Replace(":", "")) & ":"
                btnOK.Text = GetTranslationString("ok", btnOK.Text)
                btnCancel.Text = GetTranslationString("cancel", btnCancel.Text)
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

            Master.HeaderMessage = GetTranslationString("rescheduleteammeeting", "Reschedule Team Meeting")
            Master.IconImage = Request.ApplicationPath + "/images/UserMeeting.gif"
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + Me.btnOK.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:IgnoreTab(window.event)")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event")
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                LoadEditModeJavaScripts()
                LoadSelectedRecord()
                txtMeetingDate.Focus()
            End If
        End Sub

        Private Sub btnOK_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If ucMeetingTime.SelectedHour = "" Or ucMeetingTime.SelectedMinute = "" Then
                Master.DisplayError(GetTranslationString("invalidtime", "Invalid Time"))
                Return
            End If

            If (CDate(txtMeetingDate.Text) <> CDate(txtOldMeetingDate.Text)) Or (txtOldMeetingTime.Text <> ucMeetingTime.Time) Then
                'we can save
                Try
                    Dim strMeetingDate As String = RegionalConversion.FormatSQLDate(txtMeetingDate.Text)
                    Dim strOldMeetingDate As String = RegionalConversion.FormatSQLDate(txtOldMeetingDate.Text)
                    Dim objDic As New Dictionary(Of String, String)
                    objDic.Add("Meeting Rescheduled", "")
                    objDic.Add("PreviousDate", RegionalConversion.FormatSQLDate(txtOldMeetingDate.Text.Trim()))
                    objDic.Add("PreviousTime", txtOldMeetingTime.Text.Trim())
                    objDic.Add("MeetingDate", RegionalConversion.FormatSQLDate(txtMeetingDate.Text.Trim()))
                    objDic.Add("MeetingTime", ucMeetingTime.Time)
                    Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)
                    TeamMeetings.RescheduleTeemMeeting(SessionManager.TeamMeetingID, strMeetingDate, ucMeetingTime.Time, SessionManager.UserID)
                    RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.TeamMeetingID, strChangeLog, SessionManager.UserID)
                Catch Exc As Exception
                    Master.DisplayErrors(ProgramName & " - RescheduleTeamMeeting", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                    Return
                End Try
            End If
            SessionManager.MeetingDate = txtMeetingDate.Text.Trim
            SessionManager.MeetingTime = ucMeetingTime.Time
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamMeetings2"), False)
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
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamMeetings2"), False)
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

            Dim strDateHolder As String = CDate(SessionManager.MeetingDate).ToShortDateString
            txtOldMeetingDate.Text = strDateHolder
            txtOldMeetingTime.Text = SessionManager.MeetingTime.ToString

            Dim objDic As New Dictionary(Of String, String)
            objDic.Add("MeetingDate", RegionalConversion.FormatSQLDate(txtOldMeetingDate.Text.Trim()))
            objDic.Add("MeetingTime", txtOldMeetingTime.Text.Trim())
            SessionManager.RecordTransactionCurrentValues = objDic
        End Sub
#End Region

    End Class
End Namespace

