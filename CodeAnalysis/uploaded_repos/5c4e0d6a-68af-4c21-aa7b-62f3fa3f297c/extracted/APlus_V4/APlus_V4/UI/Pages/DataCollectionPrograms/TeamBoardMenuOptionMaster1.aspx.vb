#Region " Imports"
Imports System.IO
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.UI.CustomControls

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class TeamBoardMenuOptionMaster1
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Team Board Menu Option Master"
        Private Shared ReadOnly ProgramName As String = "TeamBoardMenuOptionMaster1"
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

            Master.IconImage = Request.ApplicationPath & "/images/TeamBoard.gif"
            Master.HeaderMessage = GetTranslationString(FormName, FormName)
            Master.AddBodyAttribute("onkeydown", "TrapEscKey(document.getElementById('" + MasterControl1.ExitButtonID + "'),window.event)")
            Master.AddBodyAttribute("onkeydown", "TrapEnterKey(document.getElementById('" + MasterControl1.AddButtonID + "'),window.event)")

            Dim iTeamIDHolder As Integer = 0

            If SessionManager.SelectedTeamID > 0 Then
                iTeamIDHolder = SessionManager.SelectedTeamID
            ElseIf SessionManager.SelectedValueTeamID > 0 Then
                iTeamIDHolder = SessionManager.SelectedValueTeamID
            Else
                SessionManager.CurrentProgram = Request.Path
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamSelection"))
                Return
            End If

            If SessionManager.MenuActionCoordinates <> String.Empty Then
                Dim strArgs As String() = SessionManager.MenuActionCoordinates.Split("|")

                MasterControl1.DataFilters.Add(String.Format("BoardRow = {0}", strArgs(0)))
                MasterControl1.DataFilters.Add(String.Format("BoardColumn = {0}", strArgs(1)))
            End If

            If iTeamIDHolder > 0 Then
                MasterControl1.StoredProcedureParams.Add("@TeamID", iTeamIDHolder)
                Dim bAccess As Boolean = DataAccess.Tables.UserSiteMaster.SelectTeamAllowEdit(iTeamIDHolder, SessionManager.UserID)
                If bAccess Then
                    SessionManager.AllowMaintenanceAdd = True
                    SessionManager.AllowMaintenanceEdit = True
                    SessionManager.AllowMaintenanceDelete = True
                Else
                    If Not SessionManager.SelectedTeamAllowEdit AndAlso Not SessionManager.IsAdministrator Then
                        MasterControl1.ShowAdd = False
                        MasterControl1.ShowEdit = False
                        MasterControl1.ShowDelete = False
                    End If
                End If
            End If

            TransactionHistory1.TableName = "TeamBoardMenuOptions"
            TransactionHistory1.RecordID = iTeamIDHolder.ToString

            MasterControl1.RaiseExitEvent = True
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

            Select Case e.CommandName
                Case "ViewRow", "EditRow", "DeleteRow"
                    SessionManager.SelectedValue = MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("MenuOptionID").ToString
                    SessionManager.TeamBoardMenuOptionMasterMode = e.CommandName
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamBoardMenuOptionMaster2"), False)
            End Select
        End Sub
        Protected Sub MasterControl1_ExitClick(ByVal sender As Object, ByVal e As System.EventArgs) Handles MasterControl1.ExitClick
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.MenuActioncoordinates)
            MasterControl1.ControlExit()
        End Sub
#End Region

    End Class
End Namespace
