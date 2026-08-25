#Region " Imports"
Imports System.IO
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class TrackerMaster1
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Savings Trackers"
        Private Shared ReadOnly ProgramName As String = "TrackerMaster1"
#End Region

#Region " Event Handlers"
        Protected Sub TrackerMaster1_PreInit(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.PreInit
            AddHandler Master.RefreshWorkingSite, AddressOf RefreshWorkingSite
        End Sub
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

            Master.IconImage = Request.ApplicationPath & "/images/boss.gif"
            Master.HeaderMessage = FormName
            Master.ProgramName = ProgramName
            Master.ShowWorkingSiteDropDown = True

            Master.AddBodyAttribute("onkeydown", "TrapEscKey(document.getElementById('" + MasterControl1.ExitButtonID + "'),window.event)")
            Master.AddBodyAttribute("onkeydown", "TrapEnterKey(document.getElementById('" + MasterControl1.AddButtonID + "'),window.event)")

            Dim objCol As New ButtonField
            objCol.ButtonType = ButtonType.Link
            objCol.Text = "Savings Tracker"
            objCol.CommandName = "SavingsTracker"
            MasterControl1.GridColumns.Add(objCol)

            MasterControl1.StoredProcedureParams.Add("@UserID", SessionManager.UserID)
            If SessionManager.SelectedValueTeamID > 0 Then
                MasterControl1.StoredProcedureParams.Add("@TeamID", SessionManager.SelectedValueTeamID)
            End If
            MasterControl1.StoredProcedureParams.Add("@SiteID", SessionManager.WorkingSiteID)
            Dim strLanguage As String = New System.Globalization.CultureInfo(SessionManager.CulturePref).TwoLetterISOLanguageName.ToUpper
            MasterControl1.StoredProcedureParams.Add("@Language", strLanguage)
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

            LastPixelPositionUpdate(ProgramName, Master.CurrentPixelPosition)

            Select Case e.CommandName
                Case "ViewRow", "EditRow", "DeleteRow"
                    SessionManager.SelectedValueTrackerID = MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("TrackerID").ToString
                    SessionManager.TrackerMode = e.CommandName

                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TrackerMaster2"), False)
                Case "SavingsTracker"
                    SessionManager.CallingProgram = "TrackerMaster1"
                    SessionManager.SelectedValueTrackerID = MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("TrackerID").ToString
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SavingsTracker1"), False)
            End Select
        End Sub
        Private Sub RefreshWorkingSite()
            MasterControl1.StoredProcedureParams.Clear()

            MasterControl1.StoredProcedureParams.Add("@UserID", SessionManager.UserID)
            If SessionManager.SelectedValueTeamID > 0 Then
                MasterControl1.StoredProcedureParams.Add("@TeamID", SessionManager.SelectedValueTeamID)
            End If
            MasterControl1.StoredProcedureParams.Add("@SiteID", SessionManager.WorkingSiteID)
            Dim strLanguage As String = New System.Globalization.CultureInfo(SessionManager.CulturePref).TwoLetterISOLanguageName.ToUpper
            MasterControl1.StoredProcedureParams.Add("@Language", strLanguage)
            MasterControl1.DataBind(True)
        End Sub
#End Region

    End Class
End Namespace
