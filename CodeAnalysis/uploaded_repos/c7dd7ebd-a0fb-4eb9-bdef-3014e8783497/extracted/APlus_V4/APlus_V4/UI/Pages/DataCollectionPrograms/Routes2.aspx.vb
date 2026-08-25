#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports System.Collections.Generic

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class Routes2
        Inherits ApplicationBase

#Region " Private/Constants Variables"
        Private Shared ReadOnly FormName As String = "Route Master"
        Private Shared ReadOnly ProgramName As String = "RoutesMasterMaintenance2"
        Private Shared ReadOnly DBTableName As String = "Routes"
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel, btnExit}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel", "Exit"}
            Dim OutMessageArr() As String = {"", "", ""}
            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnExit.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
        End Sub
        Private Sub LoadAddModeJavaScripts()
            Dim myTabArray() As Object = {txtRouteAbbrev, _
                                          txtRoute, _
                                          txtExpandRouteDefinition, _
                                          txtMasterTemplatePath, _
                                          ddlOwningPillar}

            Dim TabKeyDownArr() As String = {Tab(txtRoute, ddlOwningPillar, "No"), _
                                             Tab(txtExpandRouteDefinition, txtRouteAbbrev, "No"), _
                                             Tab(txtMasterTemplatePath, txtRoute, "No"), _
                                             Tab(ddlOwningPillar, txtExpandRouteDefinition, "No"), _
                                             Tab(txtRouteAbbrev, txtMasterTemplatePath, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {txtRoute, _
                                          txtExpandRouteDefinition, _
                                          txtMasterTemplatePath, _
                                          ddlOwningPillar}

            Dim TabKeyDownArr() As String = {Tab(txtExpandRouteDefinition, ddlOwningPillar, "No"), _
                                            Tab(txtMasterTemplatePath, txtRoute, "No"), _
                                            Tab(ddlOwningPillar, txtExpandRouteDefinition, "No"), _
                                            Tab(txtRoute, txtMasterTemplatePath, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
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
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                Select Case SessionManager.RoutesMode
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Route.');")
                        TransactionHistory1.LockControl = True
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        LoadAddModeJavaScripts()
                        BindOwningPillar()
                        txtOwningPillar.Visible = False
                        lnkPrintPage.Visible = False
                        txtRouteAbbrev.Focus()
                    Case "EditRow"
                        LoadEditModeJavaScripts()
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RoutesMasterMaintenance"), False)
                End Select
            End If
        End Sub
        Private Sub btnOK_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim blnSuccess As Boolean

            Select Case SessionManager.RoutesMode
                Case "DeleteRow"
                    blnSuccess = DeleteRoutes()
                Case "AddRow"
                    blnSuccess = InsertRoutes()
                Case "EditRow"
                    blnSuccess = UpdateRoutes()
            End Select

            If blnSuccess Then
                If SessionManager.RoutesMode = "EditRow" Then
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RoutesMode)
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RouteOverview"), False)
                Else
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedRoute)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RoutesMode)
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RoutesMasterMaintenance"), False)
                End If
            End If
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

            If SessionManager.RoutesMode = "EditRow" Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RoutesMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RouteOverview"), False)
            Else
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedRoute)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RoutesMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RoutesMasterMaintenance"), False)
            End If
        End Sub
        Private Sub btnCancel_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnCancel.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.RoutesMode = "EditRow" Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RoutesMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RouteOverview"), False)
            Else
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedRoute)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RoutesMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RoutesMasterMaintenance"), False)
            End If
        End Sub
        Private Sub btnRouteSteps_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnRouteSteps.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            UpdateRoutes()
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RouteStepsMasterMaintenance"), False)
        End Sub
        Private Sub btnRouteStepsView_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnRouteStepsView.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RouteStepsMasterMaintenance"), False)
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadSelectedRecord()
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
                Dim dt As DataTable = Routes.SelectRoutesByKey(SessionManager.SelectedRoute)
                Dim dr As DataRow = dt.Rows(0)

                txtRouteAbbrev.Text = dr("RouteAbbrev")
                txtRoute.Text = dr("Route")
                txtExpandRouteDefinition.Text = dr("RouteDefinition").ToString
                txtMasterTemplatePath.Text = dr("MasterTemplatePath").ToString

                BindOwningPillar()
                Dim lstitem As ListItem = ddlOwningPillar.Items.FindByValue(dr("OwningPillarAbbrev").ToString.Trim)

                If Not lstitem Is Nothing Then
                    lstitem.Selected = True
                    txtOwningPillar.Text = lstitem.Text
                End If

                If SessionManager.RoutesMode = "EditRow" Then
                    txtOwningPillar.Visible = False
                    ddlOwningPillar.Visible = True
                Else
                    txtOwningPillar.Visible = True
                    ddlOwningPillar.Visible = False
                End If

                TransactionHistory1.TableName = DBTableName
                TransactionHistory1.RecordID = SessionManager.SelectedRoute

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("RouteAbbrev", txtRouteAbbrev.Text.Trim())
                objDic.Add("Route", txtRoute.Text.Trim())
                objDic.Add("RouteDefinition", txtExpandRouteDefinition.Text.Trim())
                objDic.Add("MasterTemplatePath", txtMasterTemplatePath.Text.Trim())
                objDic.Add("OwningPillarAbbrev", txtOwningPillar.Text.Trim())
                SessionManager.RecordTransactionCurrentValues = objDic
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub UnEnableRecords()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.RoutesMode = "ViewRow" Then
                pnlOKCancel.Visible = False
                txtRouteAbbrev.ReadOnly = True
                txtRouteAbbrev.CssClass = "Textbox_Display"
                txtRoute.ReadOnly = True
                txtRoute.CssClass = "Textbox_Display"
                txtExpandRouteDefinition.ReadOnly = True
                txtExpandRouteDefinition.CssClass = "Textbox_Display"
                txtMasterTemplatePath.ReadOnly = True
                txtMasterTemplatePath.CssClass = "Textbox_Display"
            ElseIf SessionManager.RoutesMode = "DeleteRow" Then
                txtRoute.ReadOnly = True
                txtRoute.CssClass = "Textbox_Display"
                txtRouteAbbrev.ReadOnly = True
                txtRouteAbbrev.CssClass = "Textbox_Display"
                txtExpandRouteDefinition.ReadOnly = True
                txtExpandRouteDefinition.CssClass = "Textbox_Display"
                txtMasterTemplatePath.ReadOnly = True
                txtMasterTemplatePath.CssClass = "Textbox_Display"
            ElseIf SessionManager.RoutesMode = "EditRow" Then
                txtRouteAbbrev.ReadOnly = True
                txtRouteAbbrev.CssClass = "Textbox_Display"
                txtRoute.Focus()
            End If
        End Sub
        Private Function InsertRoutes() As Boolean
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
                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                Routes.AddRoutes(txtRouteAbbrev.Text.ToUpper, txtRoute.Text.Trim, txtExpandRouteDefinition.Text.Trim, txtMasterTemplatePath.Text.Trim, ddlOwningPillar.SelectedValue)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, txtRouteAbbrev.Text.Trim(), strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertRoutes ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateRoutes() As Boolean
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
                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.CompareDictionaryValues(SessionManager.RecordTransactionCurrentValues, objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                Routes.UpdateRoutes(txtRouteAbbrev.Text.ToUpper, txtRoute.Text.Trim, txtExpandRouteDefinition.Text.Trim, txtMasterTemplatePath.Text.Trim, ddlOwningPillar.SelectedValue)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, txtRouteAbbrev.Text.Trim(), strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateRoutes ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function DeleteRoutes() As Boolean
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
                Routes.DeleteRoutes(txtRouteAbbrev.Text.Trim)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, txtRouteAbbrev.Text.Trim(), "Route Deleted", SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteRoutes ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
        End Function
        Private Sub BindOwningPillar()
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
                Pillars.SelectPillarList(ddlOwningPillar)
                ddlOwningPillar.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindOwningPillar", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Function GetUpdatedValues() As Dictionary(Of String, String)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim objDic As New Dictionary(Of String, String)
            objDic.Add("RouteAbbrev", txtRouteAbbrev.Text.Trim())
            objDic.Add("Route", txtRoute.Text.Trim())
            objDic.Add("RouteDefinition", txtExpandRouteDefinition.Text.Trim())
            objDic.Add("MasterTemplatePath", txtMasterTemplatePath.Text.Trim())
            objDic.Add("OwningPillarAbbrev", ddlOwningPillar.SelectedItem.Text.Trim)
            Return objDic
        End Function
#End Region

    End Class
End Namespace
