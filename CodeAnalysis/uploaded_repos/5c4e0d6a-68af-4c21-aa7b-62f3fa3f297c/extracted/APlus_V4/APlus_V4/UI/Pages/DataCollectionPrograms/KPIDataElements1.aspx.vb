#Region " Imports"
Imports System.IO
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class KPIDataElements1
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "KPI Data Elements"
        Private Shared ReadOnly ProgramName As String = "KPIDataElements1"
#End Region

#Region " Event Handlers"
        Protected Sub InterfaceDataElementsMaster1_PreInit(sender As Object, e As System.EventArgs) Handles Me.PreInit
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
            Master.ProgramName = "KPIDataElements1"

            If String.IsNullOrEmpty(SessionManager.SelectedValueDataElement) Then
                Master.ShowWorkingSiteDropDown = True
            End If

            Master.AddBodyAttribute("onkeydown", "TrapEscKey(document.getElementById('" + MasterControl1.ExitButtonID + "'),window.event)")

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueKPIID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.KPIMasterMode)

            MasterControl1.StoredProcedureParams.Add("@SiteID", SessionManager.WorkingSiteID)
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

            BindData()

            Master.MasterScriptManager.RegisterPostBackControl(MasterControl1.ExportButton)
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

            Select Case e.CommandName
                Case "ViewRow", "EditRow", "DeleteRow"
                    SessionManager.SelectedValueKPIID = MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("KPIID").ToString
                    SessionManager.KPIMasterMode = e.CommandName
                    LastPixelPositionUpdate(ProgramName, Master.CurrentPixelPosition)

                    SessionManager.CallingProgram = "KPIDataElements1"
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPIMaster2"), False)
            End Select
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub RefreshWorkingSite()
            MasterControl1.StoredProcedureParams.Clear()
            MasterControl1.StoredProcedureParams.Add("@SiteID", SessionManager.WorkingSiteID)

            BindData()
        End Sub
        Private Sub BindData()
            If SessionManager.WorkingSiteID > 0 Then
                If Not String.IsNullOrEmpty(SessionManager.SelectedValueDataElement) Then
                    MasterControl1.StoredProcedureParams.Add("@DataElement", SessionManager.SelectedValueDataElement)
                End If

                MasterControl1.DataBind(True)
            Else
                Master.DisplayError("Working Site is required")
            End If
        End Sub
#End Region

    End Class
End Namespace
