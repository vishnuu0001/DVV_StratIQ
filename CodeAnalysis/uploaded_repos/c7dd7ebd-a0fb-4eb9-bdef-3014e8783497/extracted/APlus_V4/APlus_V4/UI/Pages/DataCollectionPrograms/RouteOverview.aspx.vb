#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class RouteOverview
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Route Overview"
        Private Shared ReadOnly ProgramName As String = "RouteOverview"
        Protected WithEvents rpKeyActions As System.Web.UI.WebControls.Repeater
        Protected WithEvents rpTools As System.Web.UI.WebControls.Repeater
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnExit}
            Dim OverMessageArr() As String = {"Exit"}
            Dim OutMessageArr() As String = {""}
            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)
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

            Master.HeaderMessage = FormName & " - " & SessionManager.RoutesMode.Replace("Row", "")
            Master.IconImage = Request.ApplicationPath + "/images/Routes.gif"
            Master.AddBodyAttribute("onkeydown", "TrapEscKey(document.getElementById('" + btnExit.UniqueID + "'),window.event)")

            'add event handlers for link buttons
            AddHandler lnkAddStep.Click, AddressOf LinkButtonClick
            AddHandler lnkEditRoute.Click, AddressOf LinkButtonClick

            BindRoute()
        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedRoute)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RoutesMasterMaintenance"))
        End Sub
        Private Sub rpSteps_ItemDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.RepeaterItemEventArgs) Handles rpSteps.ItemDataBound
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                If e.Item.ItemType = ListItemType.Item OrElse e.Item.ItemType = ListItemType.AlternatingItem Then
                    Dim iRouteStep As Integer = rpSteps.DataSource.rows(e.Item.ItemIndex)("StepNo").ToString
                    Dim strRouteStep As String = rpSteps.DataSource.rows(e.Item.ItemIndex)("Step").ToString
                    Dim objLink As LinkButton
                    CType(e.Item.FindControl("lblStep"), Label).Text = iRouteStep.ToString + " - " + strRouteStep

                    objLink = CType(e.Item.FindControl("lnkEditStep"), LinkButton)
                    objLink.CommandName = "Step|EditRow"
                    objLink.CommandArgument = iRouteStep.ToString + "|0|0"
                    AddHandler objLink.Click, AddressOf LinkButtonClick
                    objLink = CType(e.Item.FindControl("lnkDeleteStep"), LinkButton)
                    objLink.CommandName = "Step|DeleteRow"
                    objLink.CommandArgument = iRouteStep.ToString + "|0|0"
                    AddHandler objLink.Click, AddressOf LinkButtonClick
                    objLink = CType(e.Item.FindControl("lnkAddKeyAction"), LinkButton)
                    objLink.CommandName = "KeyAction|AddRow"
                    objLink.CommandArgument = iRouteStep.ToString + "|0|0"
                    AddHandler objLink.Click, AddressOf LinkButtonClick

                    If iRouteStep > 0 Then
                        Dim objDT As DataTable = RouteStepKeyActions.SelectRouteStepKeyActionsByRouteStep(SessionManager.SelectedRoute, iRouteStep)

                        If Not objDT Is Nothing AndAlso objDT.Rows.Count > 0 Then
                            rpKeyActions = CType(e.Item.FindControl("rpKeyActions"), Repeater)
                            rpKeyActions.DataSource = objDT
                            rpKeyActions.DataBind()
                        End If
                    End If
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - rpSteps_ItemDataBound", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub rpKeyActions_ItemDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.RepeaterItemEventArgs) Handles rpKeyActions.ItemDataBound
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                If e.Item.ItemType = ListItemType.Item OrElse e.Item.ItemType = ListItemType.AlternatingItem Then
                    Dim iStep As Integer = rpKeyActions.DataSource.rows(e.Item.ItemIndex)("StepNo").ToString
                    Dim iKeyAction As Integer = rpKeyActions.DataSource.rows(e.Item.ItemIndex)("KeyActionNo").ToString
                    Dim strKeyAction As String = rpKeyActions.DataSource.rows(e.Item.ItemIndex)("KeyAction").ToString
                    Dim objLink As LinkButton

                    CType(e.Item.FindControl("lblKeyAction"), Label).Text = iKeyAction.ToString + " - " + strKeyAction

                    objLink = CType(e.Item.FindControl("lnkEditKeyAction"), LinkButton)
                    objLink.CommandName = "KeyAction|EditRow"
                    objLink.CommandArgument = iStep.ToString + "|" + iKeyAction.ToString + "|0"
                    AddHandler objLink.Click, AddressOf LinkButtonClick
                    objLink = CType(e.Item.FindControl("lnkDeleteKeyAction"), LinkButton)
                    objLink.CommandName = "KeyAction|DeleteRow"
                    objLink.CommandArgument = iStep.ToString + "|" + iKeyAction.ToString + "|0"
                    AddHandler objLink.Click, AddressOf LinkButtonClick
                    objLink = CType(e.Item.FindControl("lnkAddTool"), LinkButton)
                    objLink.CommandName = "Tool|AddRow"
                    objLink.CommandArgument = iStep.ToString + "|" + iKeyAction.ToString + "|0"
                    AddHandler objLink.Click, AddressOf LinkButtonClick

                    If iKeyAction > 0 Then
                        Dim objDS As DataTable = RouteStepsKeyActionsTools.SelectRouteStepsKeyActionsToolsByKeyAction(SessionManager.SelectedRoute, iStep, iKeyAction)

                        If Not objDS Is Nothing AndAlso objDS.Rows.Count > 0 AndAlso objDS.Rows.Count > 0 Then
                            rpTools = CType(e.Item.FindControl("rpTools"), Repeater)
                            rpTools.DataSource = objDS
                            rpTools.DataBind()
                        End If
                    End If
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - rpKeyActions_ItemDataBound", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub rpTools_ItemDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.RepeaterItemEventArgs) Handles rpTools.ItemDataBound
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                If e.Item.ItemType = ListItemType.Item OrElse e.Item.ItemType = ListItemType.AlternatingItem Then
                    Dim dtRow As DataRow = rpTools.DataSource.rows(e.Item.ItemIndex)

                    Dim strTool As String = dtRow("Tool").ToString
                    Dim iToolID As Integer = dtRow("ToolID").ToString
                    Dim objLink As LinkButton

                    objLink = CType(e.Item.FindControl("lnkEditTool"), LinkButton)
                    objLink.CommandName = "Tool|EditRow"
                    objLink.CommandArgument = "0|0|" + iToolID.ToString
                    AddHandler objLink.Click, AddressOf LinkButtonClick
                    objLink = CType(e.Item.FindControl("lnkDeleteTool"), LinkButton)
                    objLink.CommandName = "Tool|DeleteRow"
                    objLink.CommandArgument = "0|0|" + iToolID.ToString
                    AddHandler objLink.Click, AddressOf LinkButtonClick

                    'we need to create a link for this to open up the document in a different window
                    'based on if the tool is a template, training document or URL
                    Dim hlFile As HyperLink = CType(e.Item.FindControl("lnkTool"), HyperLink)
                    Dim strLink As String

                    hlFile.Text = strTool

                    If dtRow("Attachment") IsNot DBNull.Value AndAlso dtRow("Attachment").ToString.Trim.Length > 0 Then
                        Select Case dtRow("AttachmentType").ToString.Trim()
                            Case "Template"
                                hlFile.Text = strTool

                                strLink = "http://" & ConfigurationManager.AppSettings("ApplicationServerDNS").ToString
                                strLink += ConfigurationManager.AppSettings("TemplateAttachmentsVirtualRootDirectory").ToString
                                strLink += New System.Globalization.CultureInfo(SessionManager.CulturePref).TwoLetterISOLanguageName + "/"
                                strLink += dtRow("Attachment").ToString

                                hlFile.ToolTip = strLink
                                hlFile.NavigateUrl = strLink
                                hlFile.Target = "_blank"
                            Case "Training"
                                strLink = "http://" & ConfigurationManager.AppSettings("ApplicationServerDNS").ToString
                                strLink += ConfigurationManager.AppSettings("TrainingAttachmentsVirtualRootDirectory").ToString
                                strLink += New System.Globalization.CultureInfo(SessionManager.CulturePref).TwoLetterISOLanguageName + "/"
                                strLink += dtRow("Attachment").ToString

                                hlFile.ToolTip = strLink
                                hlFile.NavigateUrl = strLink
                                hlFile.Target = "_blank"

                        End Select
                    ElseIf dtRow("URLLink").ToString.Trim.Length > 0 Then
                        hlFile.Text = strTool

                        strLink = dtRow("URLLink").ToString

                        hlFile.ToolTip = strLink
                        hlFile.NavigateUrl = strLink
                        hlFile.Target = "_blank"

                    End If
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - rpTools_ItemDataBound", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub LinkButtonClick(ByVal sender As Object, ByVal e As System.EventArgs)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim strCommand As String() = CType(sender, LinkButton).CommandName.Split("|")
                Dim strArgument As String() = CType(sender, LinkButton).CommandArgument.Split("|")

                Select Case strCommand(0)
                    Case "Route"
                        'we can only edit the route from here
                        'we have the route abbrev so just forward to route edit page
                        SessionManager.RoutesMode = "EditRow"
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RoutesMasterMaintenance2"), False)
                    Case "Step"
                        Select Case strCommand(1)
                            Case "AddRow"
                                SessionManager.RoutesStepsMode = "AddRow"
                            Case "EditRow"
                                SessionManager.RoutesStepsMode = "EditRow"
                            Case "DeleteRow"
                                SessionManager.RoutesStepsMode = "DeleteRow"
                        End Select

                        SessionManager.SelectedRouteStepNo = strArgument(0)
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RouteStepsMasterMaintenance2"), False)
                    Case "KeyAction"
                        Select Case strCommand(1)
                            Case "AddRow"
                                SessionManager.RouteStepsKeyActionsMode = "AddRow"
                            Case "EditRow"
                                SessionManager.RouteStepsKeyActionsMode = "EditRow"
                            Case "DeleteRow"
                                SessionManager.RouteStepsKeyActionsMode = "DeleteRow"
                        End Select

                        SessionManager.SelectedRouteStepNo = strArgument(0)
                        SessionManager.SelectedKeyActionNo = strArgument(1)
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RouteStepsKeyActions2"), False)
                    Case "Tool"
                        Select Case strCommand(1)
                            Case "AddRow"
                                SessionManager.RouteStepsKeyActionsToolsMode = "AddRow"
                            Case "EditRow"
                                SessionManager.RouteStepsKeyActionsToolsMode = "EditRow"
                            Case "DeleteRow"
                                SessionManager.RouteStepsKeyActionsToolsMode = "DeleteRow"
                        End Select

                        SessionManager.SelectedRouteStepNo = strArgument(0)
                        SessionManager.SelectedKeyActionNo = strArgument(1)
                        SessionManager.SelectedKeyActionToolID = strArgument(2)
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RouteStepsKeyActionsTools2"), False)
                End Select
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LinkButtonClick", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub BindRoute()
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
                'before we do anything, we need to get the route from the team if required
                Dim strRoute As String = ""

                If Not IsNothing(SessionManager.SelectedRoute) Then
                    If SessionManager.SelectedRoute <> String.Empty Then
                        strRoute = SessionManager.SelectedRoute
                    End If
                End If

                If strRoute.Trim.Length = 0 Then
                    lblRoute.Text = "No Route information assigned to this Team."

                    Return
                End If

                Dim objDS As DataSet = RouteSteps.SelectRouteSteps(strRoute)

                'first, if the dataset if empty, get out of here
                If (objDS Is Nothing) Or (objDS.Tables.Count = 0) Or (objDS.Tables(0).Rows.Count = 0) Then
                    'not good
                    lblRoute.Text = "No Route information assigned to this Team."

                    Return
                End If

                'plug in Route
                lblRoute.Text = objDS.Tables(0).Rows(0)("RouteAbbrev") + " - " + objDS.Tables(0).Rows(0)("Route")

                If Not objDS.Tables(0).Rows(objDS.Tables(0).Rows.Count - 1)("StepNo") Is DBNull.Value Then
                    rpSteps.DataSource = objDS.Tables(0)
                    rpSteps.DataBind()
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindRoute", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

    End Class
End Namespace