#Region " Imports"
Option Explicit On
Imports System.IO
Imports System.Data.SqlClient
Imports WebApp.APlus.UI
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class TeamOPIControlLimits1
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Team OPI Control Limits"
        Private Shared ReadOnly ProgramName As String = "TeamOPIControlLimits1"
#End Region

#Region " Protected Variables"
        Protected WithEvents valErrors As System.Web.UI.WebControls.ValidationSummary
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

            Master.IconImage = Request.ApplicationPath & "/images/TeamOPI.gif"
            Master.HeaderMessage = GetTranslationString(FormName, FormName)

            Master.AddBodyAttribute("onkeydown", "TrapEscKey(document.getElementById('" + MasterControl1.ExitButtonID + "'),window.event)")
            Master.AddBodyAttribute("onkeydown", "TrapEnterKey(document.getElementById('" + MasterControl1.AddButtonID + "'),window.event)")

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue2)

            'Team and OPI Selection
            SessionManager.CurrentProgram = Request.Path
            If SessionManager.SelectedTeamID = 0 Then
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamSelection"))
            End If
            If SessionManager.SelectedOPI = String.Empty Or IsNothing(SessionManager.SelectedOPI) Then
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("OPISelection"))
            End If

            If SessionManager.SelectedTeamID > 0 AndAlso SessionManager.SelectedOPI.Trim.Length > 0 Then
                MasterControl1.StoredProcedureParams.Add("@TeamID", SessionManager.SelectedTeamID)
                MasterControl1.StoredProcedureParams.Add("@OPI", SessionManager.SelectedOPI.Trim)
            End If

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
                SessionManager.SelectedValue = MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("TeamID").ToString 'MasterControl1.Rows(CInt(e.CommandArgument)).Cells(0).Text
                SessionManager.SelectedValue1 = MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("OPI").ToString 'MasterControl1.Rows(CInt(e.CommandArgument)).Cells(1).Text
                SessionManager.SelectedValue2 = MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("StartDate").ToString 'MasterControl1.Rows(CInt(e.CommandArgument)).Cells(2).Text
                SessionManager.TeamOPIControlLimitsMode = e.CommandName
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamOPIControlLimits2"), False)
            End If
        End Sub
#End Region

    End Class
End Namespace
