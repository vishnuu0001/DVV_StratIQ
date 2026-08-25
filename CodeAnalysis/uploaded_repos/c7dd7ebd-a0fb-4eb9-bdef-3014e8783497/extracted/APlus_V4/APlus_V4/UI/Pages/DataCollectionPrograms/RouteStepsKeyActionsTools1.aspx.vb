#Region " Imports"
Imports System.IO
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class RouteStepsKeyActionsTools1
        Inherits ApplicationBase

#Region " Constants"
        Private Shared ReadOnly FormName As String = "Route Steps Key Actions Tools"
        Private Shared ReadOnly ProgramName As String = "RouteStepsKeyActionsTools1"
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

            Master.IconImage = Request.ApplicationPath & "/images/Routes.gif"
            Master.HeaderMessage = FormName

            Master.AddBodyAttribute("onkeydown", "TrapEscKey(document.getElementById('" + MasterControl1.ExitButtonID + "'),window.event)")
            Master.AddBodyAttribute("onkeydown", "TrapEnterKey(document.getElementById('" + MasterControl1.AddButtonID + "'),window.event)")

            Dim strRouteHolder As String = ""
            Dim strStepHolder As String = ""
            Dim strKeyActionHolder As String = ""

            If SessionManager.SelectedRoute <> String.Empty Then
                strRouteHolder = SessionManager.SelectedRoute

                SessionManager.MasterControlExitProgram = "RouteStepsKeyActions2"
            End If

            If SessionManager.SelectedRouteStepNo <> String.Empty Then
                strStepHolder = SessionManager.SelectedRouteStepNo
            End If

            If SessionManager.SelectedKeyActionNo <> String.Empty Then
                strKeyActionHolder = SessionManager.SelectedKeyActionNo
            End If

            If strRouteHolder.Trim.Length > 0 And strStepHolder.Trim.Length > 0 Then
                'filter the grid by the selected Route Information
                MasterControl1.StoredProcedureParams.Add("@RouteAbbrev", strRouteHolder)
                MasterControl1.StoredProcedureParams.Add("@StepNo", strStepHolder)
                MasterControl1.StoredProcedureParams.Add("@KeyActionNo", strKeyActionHolder)
            End If

            If SessionManager.RouteStepsKeyActionsMode = "ViewRow" Then
                MasterControl1.ShowAdd = False
                MasterControl1.ShowDelete = False
                MasterControl1.ShowEdit = False
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
                SessionManager.SelectedKeyActionToolID = MasterControl1.Rows(CInt(e.CommandArgument)).Cells(0).Text
                SessionManager.RouteStepsKeyActionsToolsMode = e.CommandName
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RouteStepsKeyActionsTools2"), False)
            End If
        End Sub
#End Region

    End Class
End Namespace
