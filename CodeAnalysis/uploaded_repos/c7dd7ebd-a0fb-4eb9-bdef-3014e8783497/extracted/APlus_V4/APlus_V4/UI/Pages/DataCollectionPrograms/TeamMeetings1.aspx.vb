
#Region " Imports "

Imports System.IO
Imports WebApp.APlus.UI
Imports WebApp.APlus.UI.CustomControls
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class TeamMeetings1
        Inherits ApplicationBase

#Region " Private Constants "
        Private Shared ReadOnly FormName As String = "Team Meetings"
        Private Shared ReadOnly ProgramName As String = "TeamMeetings1"
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

            Master.IconImage = Request.ApplicationPath & "/images/UserMeeting.gif"
            Master.HeaderMessage = GetTranslationString(FormName, FormName)
            Master.AddBodyAttribute("onkeydown", "TrapEscKey(document.getElementById('" + MasterControl1.ExitButtonID + "'),window.event)")
            Master.AddBodyAttribute("onkeydown", "TrapEnterKey(document.getElementById('" + MasterControl1.AddButtonID + "'),window.event)")

            If Not Page.IsPostBack Then
                If SessionManager.SelectedTeamID = 0 Then
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamSelection"), False)
                    Return
                End If
            End If

            MasterControl1.StoredProcedureParams.Add("@TeamID", SessionManager.SelectedTeamID)
            MasterControl1.GridColumns(1).DataFormatString = "{0:yyyy/MM/dd}"

            If Not SessionManager.SelectedTeamAllowEdit AndAlso Not SessionManager.IsAdministrator Then
                MasterControl1.ShowAdd = False
                MasterControl1.ShowEdit = False
                MasterControl1.ShowDelete = False
            End If
        End Sub
        Protected Sub Timer1_Tick(ByVal sender As Object, ByVal e As System.EventArgs) Handles Timer1.Tick
            Timer1.Enabled = False
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            MasterControl1.DataBind()
        End Sub
        Protected Sub MasterControl1_onRowCommand(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewCommandEventArgs) Handles MasterControl1.onRowCommand
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", e.CommandName)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If e.CommandName = "ViewRow" Or e.CommandName = "DeleteRow" Or e.CommandName = "EditRow" Then
                SessionManager.TeamMeetingID = MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("TeamMeetingID").ToString
                SessionManager.TeamMeetingsMode = e.CommandName
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamMeetings2"), False)
            End If
        End Sub
#End Region

    End Class
End Namespace

