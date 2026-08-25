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

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class TeamMeetingAttendance4
        Inherits ApplicationBase

#Region " Constants "
        Private Shared ReadOnly FormName As String = "Team Meeting - Remove User"
        Private Shared ReadOnly ProgramName As String = "TeamMeetingAttendance4"
#End Region

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            SessionManager.CurrentProgram = Request.Path

            If Not Page.IsPostBack Then
                If SessionManager.SelectedTeamID = 0 Then
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamSelection"))
                    Return
                End If
            End If

            MasterControl1.StoredProcedureParams.Add("@TeamMeetingID", SessionManager.TeamMeetingID)

            MasterControl1.GridColumns(0).DataFormatString = "{0:" + SessionManager.DateFormat + "}"
            Master.IconImage = Request.ApplicationPath & "/images/Team.gif"
            Master.HeaderMessage = GetTranslationString(FormName, FormName)

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
            If e.CommandName = "DeleteRow" Then
                SessionManager.SelectedValue = MasterControl1.Rows(CInt(e.CommandArgument)).Cells(2).Text
                SessionManager.TeamMeetingAttendanceMode = e.CommandName
                SessionManager.CallingProgram = "TeamMeetingAttendance4"
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamMeetingAttendance2"), False)
            End If
        End Sub
        Private Sub RedirectToPriorProgram()
            If SessionManager.CallingProgram > "" Then
                Dim strCallingProgram As String = SessionManager.CallingProgram
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CallingProgram)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamMeetingsMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strCallingProgram), False)
            Else
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamMeetings2"), False)
            End If
        End Sub
#End Region

    End Class
End Namespace

