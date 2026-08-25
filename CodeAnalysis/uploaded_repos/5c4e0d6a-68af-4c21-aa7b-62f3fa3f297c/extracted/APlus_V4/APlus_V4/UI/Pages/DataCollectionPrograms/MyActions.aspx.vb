#Region " Imports"
Imports System.IO
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class MyActions
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "My Actions"
        Private Shared ReadOnly ProgramName As String = "MyActions"
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
                lblTeamActions.Text = GetTranslationString("teamactionitems", lblTeamActions.Text)
                lblAnomalyActions.Text = GetTranslationString("anomalyactions", lblAnomalyActions.Text)
                lblAnomaliesAnalysis.Text = GetTranslationString("anoamlypendinganalysis", lblAnomaliesAnalysis.Text)
                lblAnomalyActionPlan.Text = GetTranslationString("anomalies", lblAnomalyActionPlan.Text)
                lblAnomalyEvaluation.Text = GetTranslationString("anoamlypendingevaluation", lblAnomalyEvaluation.Text)
                lblMyKPI.Text = GetTranslationString("kpipendinginput", lblMyKPI.Text)

                btnExit.Text = GetTranslationString("exit", btnExit.Text)
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

            Master.IconImage = Request.ApplicationPath & "/images/TeamAction.gif"
            Master.HeaderMessage = GetTranslationString(FormName, FormName)
            Master.AddBodyAttribute("onkeydown", "TrapEscKey(document.getElementById('" + btnExit.UniqueID + "'),window.event)")

            LoadCultureTranslations()

            Dim objCol As ButtonField
            objCol = New ButtonField
            objCol.ButtonType = ButtonType.Link
            objCol.HeaderText = GetTranslationString("team", "Team")
            objCol.DataTextField = "Team"
            objCol.CommandName = "TeamBoard"
            mcTeamActions.GridColumns.Insert(1, objCol)

            objCol = New ButtonField
            objCol.ButtonType = ButtonType.Link
            objCol.Text = GetTranslationString("actions", "Actions")
            objCol.CommandName = "Actions"
            mcAnomalyActionPlan.GridColumns.Add(objCol)

            mcTeamActions.GridColumns(6).DataFormatString = "{0:yyyy/MM/dd HH:mm}"
            mcTeamActions.GridColumns(9).DataFormatString = "{0:yyyy/MM/dd}"

            mcAnomalyActions.GridColumns(5).DataFormatString = "{0:yyyy/MM/dd}"

            mcAnomalies.GridColumns(4).DataFormatString = "{0:yyyy/MM/dd}"

            mcAnomalyActionPlan.GridColumns(4).DataFormatString = "{0:yyyy/MM/dd}"

            mcAnomalyEvaluation.GridColumns(4).DataFormatString = "{0:yyyy/MM/dd}"
            mcAnomalyEvaluation.GridColumns(6).DataFormatString = "{0:yyyy/MM/dd}"
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

            BindGrid()
        End Sub
        Protected Sub mcTeamActions_onRowDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewRowEventArgs) Handles mcTeamActions.onRowDataBound
            If e.Row.RowType = DataControlRowType.DataRow Then
                If IsDate(e.Row.Cells(9).Text) Then
                    Dim dtTargetDate As DateTime = Convert.ToDateTime(e.Row.Cells(9).Text)

                    If DateTime.Compare(dtTargetDate, Date.Now) <= 0 Then
                        e.Row.Cells(9).BackColor = Drawing.Color.Red
                    End If
                End If

                If IsNumeric(mcTeamActions.MasterControlGrid.DataKeys(e.Row.RowIndex)("AllowEdit").ToString) AndAlso Convert.ToInt16(mcTeamActions.MasterControlGrid.DataKeys(e.Row.RowIndex)("AllowEdit").ToString) <> 1 Then
                    Try
                        CType(e.Row.Cells(12).Controls(0), LinkButton).Enabled = False
                    Catch ex As Exception
                        'do nothing
                    End Try
                End If
            End If
        End Sub
        Protected Sub mcTeamActions_onRowCommand(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewCommandEventArgs) Handles mcTeamActions.onRowCommand
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
                    PushTeamOntoStack(SessionManager.SelectedTeamID, SessionManager.SelectedTeam, SessionManager.SelectedOPI, "MyActions", SessionManager.CurrentMenuProgram)
                    SessionManager.SelectedTeamID = mcTeamActions.MasterControlGrid.DataKeys(e.CommandArgument)("TeamID").ToString
                    SessionManager.SelectedTeam = mcTeamActions.MasterControlGrid.DataKeys(e.CommandArgument)("Team").ToString
                    SessionManager.SelectedTeamName = Teams.GetTeamName(SessionManager.SelectedTeamID)
                    SessionManager.SelectedOPI = ""
                    SessionManager.SelectedTeamAllowEdit = mcTeamActions.MasterControlGrid.DataKeys(e.CommandArgument)("AllowEdit").ToString
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedOPI)

                    SessionManager.SelectedValue = mcTeamActions.MasterControlGrid.DataKeys(e.CommandArgument)("ActionNumber").ToString
                    SessionManager.TeamActionPlanMode = "My" & e.CommandName
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamActionPlanMaintenance2"), False)
                Case "TeamBoard"
                    PushTeamOntoStack(SessionManager.SelectedTeamID, SessionManager.SelectedTeam, SessionManager.SelectedOPI, "MyActions", SessionManager.CurrentMenuProgram)
                    SessionManager.SelectedTeamID = mcTeamActions.MasterControlGrid.DataKeys(e.CommandArgument)("TeamID").ToString
                    SessionManager.SelectedTeam = mcTeamActions.MasterControlGrid.DataKeys(e.CommandArgument)("Team").ToString
                    SessionManager.SelectedTeamName = Teams.GetTeamName(SessionManager.SelectedTeamID)
                    SessionManager.SelectedOPI = ""
                    SessionManager.SelectedTeamAllowEdit = mcTeamActions.MasterControlGrid.DataKeys(e.CommandArgument)("AllowEdit").ToString
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedOPI)

                    SessionManager.CurrentMenuProgram = "TeamBoardMenu"
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamBoardMenu"), False)
            End Select
        End Sub
        Protected Sub mcAnomalyActions_onRowDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewRowEventArgs) Handles mcAnomalyActions.onRowDataBound
            If e.Row.RowType = DataControlRowType.DataRow Then
                If IsDate(e.Row.Cells(5).Text) Then
                    Dim dtTargetDate As DateTime = Convert.ToDateTime(e.Row.Cells(5).Text)

                    If DateTime.Compare(dtTargetDate, Date.Now) <= 0 Then
                        e.Row.Cells(5).BackColor = Drawing.Color.Red
                    End If
                End If
            End If
        End Sub
        Protected Sub mcAnomalyActions_onRowCommand(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewCommandEventArgs) Handles mcAnomalyActions.onRowCommand
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
                    SessionManager.SelectedValueAnomalyID = mcAnomalyActions.MasterControlGrid.DataKeys(e.CommandArgument)("AnomalyID").ToString
                    SessionManager.SelectedValueAnomalyActionID = mcAnomalyActions.MasterControlGrid.DataKeys(e.CommandArgument)("AnomalyActionID").ToString
                    SessionManager.AnomalyActionMode = e.CommandName
                    SessionManager.CallingProgram = "MyActions"

                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyActions2"), False)
            End Select
        End Sub
        Protected Sub mcAnomalies_onRowDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewRowEventArgs) Handles mcAnomalies.onRowDataBound
            If e.Row.RowType = DataControlRowType.DataRow Then
                If Convert.ToBoolean(mcAnomalies.MasterControlGrid.DataKeys(e.Row.RowIndex)("AutoGenerated").ToString) Then
                    Try
                        CType(e.Row.Cells(10).Controls(0), LinkButton).Enabled = False
                    Catch ex As Exception
                        'do nothing
                    End Try
                End If
            End If
        End Sub
        Protected Sub mcAnomalies_onRowCommand(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewCommandEventArgs) Handles mcAnomalies.onRowCommand
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
                    SessionManager.SelectedValueAnomalyID = mcAnomalies.MasterControlGrid.DataKeys(e.CommandArgument)("AnomalyID").ToString
                    SessionManager.AnomalyMode = e.CommandName
                    SessionManager.CallingProgram = "MyActions"

                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyMaster2"), False)
            End Select
        End Sub
        Protected Sub mcAnomalyActionPlan_onRowDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewRowEventArgs) Handles mcAnomalyActionPlan.onRowDataBound
            If e.Row.RowType = DataControlRowType.DataRow Then
                If Not IsNumeric(mcAnomalyActionPlan.MasterControlGrid.DataKeys(e.Row.RowIndex)("EditAnomaly").ToString) _
                OrElse Convert.ToInt16(mcAnomalyActionPlan.MasterControlGrid.DataKeys(e.Row.RowIndex)("EditAnomaly").ToString) = 0 Then
                    Try
                        CType(e.Row.Cells(10).Controls(0), LinkButton).Enabled = False
                    Catch ex As Exception
                        'do nothing
                    End Try
                End If

                If Not IsNumeric(mcAnomalyActionPlan.MasterControlGrid.DataKeys(e.Row.RowIndex)("EditActions").ToString) _
                OrElse Convert.ToInt16(mcAnomalyActionPlan.MasterControlGrid.DataKeys(e.Row.RowIndex)("EditActions").ToString) = 0 Then
                    Try
                        CType(e.Row.Cells(9).Controls(0), LinkButton).Enabled = False
                    Catch ex As Exception
                        'do nothing
                    End Try
                End If
            End If
        End Sub
        Protected Sub mcAnomalyActionPlan_onRowCommand(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewCommandEventArgs) Handles mcAnomalyActionPlan.onRowCommand
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
                    SessionManager.SelectedValueAnomalyID = mcAnomalyActionPlan.MasterControlGrid.DataKeys(e.CommandArgument)("AnomalyID").ToString
                    SessionManager.AnomalyMode = e.CommandName
                    SessionManager.CallingProgram = "MyActions"

                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyMaster2"), False)
                Case "Actions"
                    SessionManager.SelectedValueAnomalyID = mcAnomalyActionPlan.MasterControlGrid.DataKeys(e.CommandArgument)("AnomalyID").ToString
                    SessionManager.AnomalyMode = "Actions"
                    SessionManager.MasterControlExitProgram = "MyActions"

                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyActions1"), False)
            End Select
        End Sub
        Protected Sub mcAnomalyEvaluation_onRowCommand(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewCommandEventArgs) Handles mcAnomalyEvaluation.onRowCommand
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
                Case "ViewRow", "EditRow"
                    SessionManager.SelectedValueAnomalyID = mcAnomalyEvaluation.MasterControlGrid.DataKeys(e.CommandArgument)("AnomalyID").ToString
                    SessionManager.AnomalyMode = e.CommandName
                    SessionManager.CallingProgram = "MyActions"

                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyMaster2"), False)
            End Select
        End Sub
        Protected Sub mcMyKPI_onRowCommand(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewCommandEventArgs) Handles mcMyKPI.onRowCommand
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
                Case "EditRow"
                    SessionManager.SelectedValueKPIID = mcMyKPI.MasterControlGrid.DataKeys(e.CommandArgument)("KPIID").ToString
                    SessionManager.CallingProgram = "MyActions"

                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPIValues1"), False)
            End Select
        End Sub
        Protected Sub btnExit_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnExit.Click
            RemoveCurrentProgramandGoBack()
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub BindGrid()
            mcTeamActions.StoredProcedureParams.Clear()
            mcTeamActions.StoredProcedureParams.Add("@UserID", SessionManager.UserID)
            mcTeamActions.StoredProcedureParams.Add("@SiteID", 0)
            mcTeamActions.DataBind(True)

            mcAnomalyActions.StoredProcedureParams.Clear()
            mcAnomalyActions.StoredProcedureParams.Add("@UserID", SessionManager.UserID)
            mcAnomalyActions.StoredProcedureParams.Add("@SiteID", 0)
            mcAnomalyActions.DataBind(True)

            mcAnomalies.StoredProcedureParams.Clear()
            mcAnomalies.StoredProcedureParams.Add("@UserID", SessionManager.UserID)
            mcAnomalies.StoredProcedureParams.Add("@SiteID", 0)
            mcAnomalies.DataBind(True)

            mcAnomalyActionPlan.StoredProcedureParams.Clear()
            mcAnomalyActionPlan.StoredProcedureParams.Add("@UserID", SessionManager.UserID)
            mcAnomalyActionPlan.StoredProcedureParams.Add("@SiteID", 0)
            mcAnomalyActionPlan.DataBind(True)

            mcAnomalyEvaluation.StoredProcedureParams.Clear()
            mcAnomalyEvaluation.StoredProcedureParams.Add("@UserID", SessionManager.UserID)
            mcAnomalyEvaluation.StoredProcedureParams.Add("@SiteID", 0)
            mcAnomalyEvaluation.DataBind(True)

            mcMyKPI.StoredProcedureParams.Clear()
            mcMyKPI.StoredProcedureParams.Add("@UserID", SessionManager.UserID)
            mcMyKPI.StoredProcedureParams.Add("@SiteID", 0)
            mcMyKPI.DataBind(True)

            If mcAnomalyActions.MasterControlGrid.Rows.Count = 0 AndAlso mcAnomalies.MasterControlGrid.Rows.Count = 0 AndAlso _
            mcAnomalyActionPlan.MasterControlGrid.Rows.Count = 0 AndAlso mcAnomalyEvaluation.MasterControlGrid.Rows.Count = 0 AndAlso _
            AnomalyMaster.SelectAnomalyMasterByUserSite(SessionManager.UserID) = 0 Then
                pnlAnomalies.Visible = False
            Else
                pnlAnomalies.Visible = True
            End If
        End Sub
#End Region

    End Class
End Namespace
