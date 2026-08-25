#Region " Imports"
Imports System.Data
Imports System.IO
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class AnomalyActions1
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Anomaly Actions"
        Private Shared ReadOnly ProgramName As String = "AnomalyActions1"
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
                lblAnomalyCauses.Text = GetTranslationString("anomalycauses", lblAnomalyCauses.Text)
                lblAnomalyActions.Text = GetTranslationString("anomalyactions", lblAnomalyActions.Text)
                lblAnomalyAttachments.Text = GetTranslationString("anomalyattachments", lblAnomalyAttachments.Text)
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

            Master.IconImage = Request.ApplicationPath & "/images/data_information.gif"
            Master.HeaderMessage = GetTranslationString(FormName, FormName)

            Master.AddBodyAttribute("onkeydown", "TrapEscKey(document.getElementById('" + mcActions.ExitButtonID + "'),window.event)")
            Master.AddBodyAttribute("onkeydown", "TrapEnterKey(document.getElementById('" + mcActions.AddButtonID + "'),window.event)")

            If Not Page.IsPostBack Then
                LoadCultureTranslations()
            End If

            If AnomalyMaster.AnomalyIsClosed(SessionManager.SelectedValueAnomalyID) OrElse (SessionManager.AnomalyMode <> "EditRow" AndAlso SessionManager.AnomalyMode <> "Actions") Then
                mcCauses.ShowEdit = False
                mcCauses.ShowDelete = False

                mcActions.ShowEdit = False
                mcActions.ShowDelete = False
                mcActions.ShowAdd = False
                mcActions.ShowFunctionButtonOne = False
            ElseIf AnomalyMaster.AnomalyActionRequiresCause(SessionManager.SelectedValueAnomalyID) Then
                Dim objDT As DataTable = AnomalyCauses.SelectAnomalyCausesByAnomalyID(SessionManager.SelectedValueAnomalyID)
                If objDT Is Nothing OrElse objDT.Rows.Count = 0 Then
                    'mcActions.ShowAdd = False
                    mcActions.AddButton.Enabled = False
                End If
            End If

            mcAnomaly.StoredProcedureParams.Add("@AnomalyID", SessionManager.SelectedValueAnomalyID)
            mcAnomaly.StoredProcedureParams.Add("@UserID", SessionManager.UserID)
            mcCauses.StoredProcedureParams.Add("@AnomalyID", SessionManager.SelectedValueAnomalyID)
            mcActions.StoredProcedureParams.Add("@AnomalyID", SessionManager.SelectedValueAnomalyID)

            mcAnomaly.GridColumns(7).DataFormatString = "{0:yyyy/MM/dd}"
            mcAnomaly.GridColumns(9).DataFormatString = "{0:yyyy/MM/dd}"

            mcActions.GridColumns(6).DataFormatString = "{0:yyyy/MM/dd}"
            mcActions.GridColumns(9).DataFormatString = "{0:yyyy/MM/dd}"
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

            mcAnomaly.DataBind(True)
            mcCauses.DataBind(True)
            mcActions.DataBind(True)
            Master.MasterScriptManager.RegisterPostBackControl(mcActions.ExportButton)
            LoadAttachments()
        End Sub
        Protected Sub mcAnomaly_onRowDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewRowEventArgs) Handles mcAnomaly.onRowDataBound
            If e.Row.RowType = DataControlRowType.DataRow Then
                If mcAnomaly.MasterControlGrid.DataKeys(e.Row.RowIndex)("ResponsibleUserID").ToString <> SessionManager.UserID _
                AndAlso mcAnomaly.MasterControlGrid.DataKeys(e.Row.RowIndex)("CreatedUserID").ToString <> SessionManager.UserID _
                AndAlso mcAnomaly.MasterControlGrid.DataKeys(e.Row.RowIndex)("EditAnomaly").ToString <> "1" Then
                    mcActions.AddButton.Enabled = False
                    mcActions.FunctionButtonOne.Enabled = False
                End If
            End If
        End Sub
        Protected Sub mcCauses_onRowDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewRowEventArgs) Handles mcCauses.onRowDataBound
            If e.Row.RowType = DataControlRowType.DataRow Then
                If mcCauses.MasterControlGrid.DataKeys(e.Row.RowIndex)("ResponsibleUserID").ToString <> SessionManager.UserID _
                AndAlso mcCauses.MasterControlGrid.DataKeys(e.Row.RowIndex)("CreatedUserID").ToString <> SessionManager.UserID Then
                    Try
                        CType(e.Row.Cells(5).Controls(0), LinkButton).Enabled = False
                        CType(e.Row.Cells(6).Controls(0), LinkButton).Enabled = False
                    Catch ex As Exception
                        'do nothing
                    End Try
                End If
            End If
        End Sub
        Protected Sub mcCauses_onRowCommand(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewCommandEventArgs) Handles mcCauses.onRowCommand
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
                    SessionManager.SelectedValueAnomalyCauseID = mcCauses.MasterControlGrid.DataKeys(e.CommandArgument)("AnomalyCauseID").ToString
                    SessionManager.AnomalyCauseMode = e.CommandName

                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyCauses2"), False)
            End Select
        End Sub
        Protected Sub mcActions_onRowDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewRowEventArgs) Handles mcActions.onRowDataBound
            If e.Row.RowType = DataControlRowType.DataRow Then
                If IsDate(e.Row.Cells(6).Text) AndAlso Not IsDate(e.Row.Cells(9).Text) Then
                    Dim dtTargetDate As DateTime = Convert.ToDateTime(e.Row.Cells(6).Text)

                    If DateTime.Compare(dtTargetDate, Date.Now) <= 0 Then
                        e.Row.Cells(6).BackColor = Drawing.Color.Red
                    End If
                End If

                If mcActions.MasterControlGrid.DataKeys(e.Row.RowIndex)("AnomalyResponsibleUserID").ToString <> SessionManager.UserID _
                AndAlso mcActions.MasterControlGrid.DataKeys(e.Row.RowIndex)("CreatedUserID").ToString <> SessionManager.UserID _
                AndAlso mcAnomaly.MasterControlGrid.DataKeys(0)("EditAnomaly").ToString <> "1" Then
                    Try
                        CType(e.Row.Cells(15).Controls(0), LinkButton).Enabled = False
                    Catch ex As Exception
                        'do nothing
                    End Try

                    If mcActions.MasterControlGrid.DataKeys(e.Row.RowIndex)("ResponsibleUserID").ToString <> SessionManager.UserID Then
                        Try
                            CType(e.Row.Cells(14).Controls(0), LinkButton).Enabled = False
                        Catch ex As Exception
                            'do nothing
                        End Try
                    End If
                End If
            End If
        End Sub
        Protected Sub mcActions_onRowCommand(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewCommandEventArgs) Handles mcActions.onRowCommand
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
                    SessionManager.SelectedValueAnomalyActionID = mcActions.MasterControlGrid.DataKeys(e.CommandArgument)("AnomalyActionID").ToString
                    SessionManager.AnomalyActionMode = e.CommandName

                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyActions2"), False)
            End Select
        End Sub
        Protected Sub mcActions_FunctionButtonOneClick(ByVal sender As Object, ByVal e As System.EventArgs) Handles mcActions.FunctionButtonOneClick
            SessionManager.AnomalyCauseMode = "AddRow"

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyCauses2"), False)
        End Sub
        Protected Sub gvAttachments_RowDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewRowEventArgs) Handles gvAttachments.RowDataBound
            If e.Row.RowType = DataControlRowType.DataRow Then
                Try
                    For Each objCtl As Control In e.Row.Cells(0).Controls
                        If TypeOf objCtl Is LinkButton Then
                            Master.MasterScriptManager.RegisterPostBackControl(CType(objCtl, LinkButton))
                            Exit For
                        End If
                    Next
                Catch ex As Exception
                    'just exit gracefully
                End Try
            End If
        End Sub
        Protected Sub gvAttachments_RowCommand(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewCommandEventArgs) Handles gvAttachments.RowCommand
            Select Case e.CommandName
                Case "ViewAttachment"
                    Response.Redirect("ViewDocument.aspx?AttachmentID=" & e.CommandArgument.ToString)
            End Select
        End Sub
        Protected Sub btnAttach_Click(sender As Object, e As System.EventArgs) Handles btnAttach.Click
            SessionManager.CallingProgram = "AnomalyActions1"
            SessionManager.AnomalyMode = "AddAttachment"
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyMaster2"), False)
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadAttachments()
            Dim objDT As DataTable = AnomalyAttachments.SelectAnomalyAttachments(SessionManager.SelectedValueAnomalyID)

            If Not objDT Is Nothing AndAlso objDT.Rows.Count > 0 Then
                gvAttachments.DataSource = objDT
            Else
                gvAttachments.DataSource = Nothing
            End If

            gvAttachments.DataBind()

            CheckAttachments()
        End Sub
        Private Sub CheckAttachments()
            pnlAddAttachment.Visible = False

            For iRow As Integer = 0 To mcActions.Rows.Count - 1
                Try
                    If CType(mcActions.Rows(iRow).Cells(14).Controls(0), LinkButton).Enabled Then
                        pnlAddAttachment.Visible = True

                        Return
                    End If
                Catch ex As Exception
                    'do nothing
                End Try
            Next

            If mcActions.AddButton.Enabled Then
                pnlAddAttachment.Visible = True
            End If
        End Sub
#End Region

    End Class
End Namespace
