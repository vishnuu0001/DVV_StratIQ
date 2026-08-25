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
    Partial Class RouteSteps2
        Inherits ApplicationBase

#Region " Private/Constants Variables"
        Private Shared ReadOnly FormName As String = "Route Steps Master"
        Private Shared ReadOnly ProgramName As String = "RouteSteps2"
        Private Shared ReadOnly DBTableName As String = "RouteSteps"
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
            Dim myTabArray() As Object = {txtStepNumber, _
                                          txtStep, _
                                          txtExpandStepDefinition, _
                                          txtStartDateOffset, _
                                          txtPlannedDuration _
                                         }

            Dim TabKeyDownArr() As String = {Tab(txtStep, txtPlannedDuration, "Yes"), _
                                             Tab(txtExpandStepDefinition, txtStepNumber, "No"), _
                                             Tab(txtStartDateOffset, txtStep, "No"), _
                                             Tab(txtPlannedDuration, txtExpandStepDefinition, "Yes"), _
                                             Tab(txtStepNumber, txtStartDateOffset, "Yes")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {txtStep, _
                                          txtExpandStepDefinition, _
                                          txtStartDateOffset, _
                                          txtPlannedDuration _
                                         }

            Dim TabKeyDownArr() As String = {Tab(txtExpandStepDefinition, txtPlannedDuration, "No"), _
                                             Tab(txtStartDateOffset, txtStep, "No"), _
                                             Tab(txtPlannedDuration, txtExpandStepDefinition, "Yes"), _
                                             Tab(txtStep, txtStartDateOffset, "Yes")}

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

            Master.HeaderMessage = FormName & " - " & SessionManager.RoutesStepsMode.Replace("Row", "")
            Master.IconImage = Request.ApplicationPath + "/images/globe-compass.gif"
            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                If SessionManager.RoutesStepsMode = "ViewRow" Then
                    pnlExit.Visible = True
                    LoadSelectedRecord()
                    UnEnableRecords()
                ElseIf SessionManager.RoutesStepsMode = "DeleteRow" Then
                    LoadSelectedRecord()
                    UnEnableRecords()
                    btnOK.CausesValidation = False
                    btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Route Step.');")
                    TransactionHistory1.LockControl = True
                ElseIf SessionManager.RoutesStepsMode = "AddRow" Then
                    TransactionHistory1.Visible = False
                    LoadAddModeJavaScripts()
                    txtStepNumber.Focus()
                    txtRouteAbbrev.Text = SessionManager.SelectedRoute + " - " + Routes.GetRoute(SessionManager.SelectedRoute)
                ElseIf SessionManager.RoutesStepsMode = "EditRow" Then
                    LoadEditModeJavaScripts()
                    LoadSelectedRecord()
                    UnEnableRecords()
                Else
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RouteOverview"))
                End If
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
            If SessionManager.RoutesStepsMode = "DeleteRow" Then
                blnSuccess = DeleteRouteSteps()
            ElseIf SessionManager.RoutesStepsMode = "AddRow" Then
                blnSuccess = InsertRouteSteps()
            ElseIf SessionManager.RoutesStepsMode = "EditRow" Then
                blnSuccess = UpdateRouteSteps()
            End If

            If blnSuccess Then
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RouteOverview"), False)
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

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RouteOverview"), False)
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

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RouteOverview"), False)
        End Sub
        Private Sub btnKeyActions_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnKeyActions.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            UpdateRouteSteps()
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RouteStepsKeyActions1"), False)
        End Sub
        Private Sub btnKeyActionsView_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnKeyActionsView.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RouteStepsKeyActions1"), False)
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
                Dim dt As DataTable = RouteSteps.SelectRouteStepsByKey(SessionManager.SelectedRoute, SessionManager.SelectedRouteStepNo)
                Dim dr As DataRow = dt.Rows(0)
                Dim dtRoutes As DataTable = Routes.SelectRoutesByKey(dr("RouteAbbrev"))
                Dim drRoutes As DataRow = dtRoutes.Rows(0)

                txtStepNumber.Text = dr("StepNo")
                txtStep.Text = dr("Step").ToString
                txtExpandStepDefinition.Text = dr("StepDefinition").ToString
                txtStartDateOffset.Text = dr("StartDateOffset").ToString
                txtPlannedDuration.Text = dr("PlannedDuration").ToString
                txtRouteAbbrev.Text = drRoutes("RouteAbbrev").ToString & " - " & drRoutes("Route").ToString

                TransactionHistory1.TableName = DBTableName
                TransactionHistory1.RecordID = SessionManager.SelectedRoute & "," & SessionManager.SelectedRouteStepNo

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("RouteAbbrev", txtRouteAbbrev.Text.Trim())
                objDic.Add("StepNo", txtStepNumber.Text.Trim())
                objDic.Add("Step", txtStep.Text.Trim())
                objDic.Add("StepDefinition", txtExpandStepDefinition.Text.Trim())
                objDic.Add("StartDateOffset", txtStartDateOffset.Text.Trim())
                objDic.Add("PlannedDuration", txtPlannedDuration.Text.Trim())
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

            Select Case SessionManager.RoutesStepsMode.ToString()
                Case "ViewRow"
                    pnlOKCancel.Visible = False
                    txtStepNumber.ReadOnly = True
                    txtStepNumber.CssClass = "Textbox_Display"
                    txtStep.ReadOnly = True
                    txtStep.CssClass = "Textbox_Display"
                    txtExpandStepDefinition.ReadOnly = True
                    txtExpandStepDefinition.CssClass = "Textbox_Display"
                    txtStartDateOffset.ReadOnly = True
                    txtStartDateOffset.CssClass = "Textbox_Display"
                    txtPlannedDuration.ReadOnly = True
                    txtPlannedDuration.CssClass = "Textbox_Display"
                Case "DeleteRow"
                    txtStepNumber.ReadOnly = True
                    txtStepNumber.CssClass = "Textbox_Display"
                    txtStep.ReadOnly = True
                    txtStep.CssClass = "Textbox_Display"
                    txtExpandStepDefinition.ReadOnly = True
                    txtExpandStepDefinition.CssClass = "Textbox_Display"
                    txtStartDateOffset.ReadOnly = True
                    txtStartDateOffset.CssClass = "Textbox_Display"
                    txtPlannedDuration.ReadOnly = True
                    txtPlannedDuration.CssClass = "Textbox_Display"
                Case "EditRow"
                    txtRouteAbbrev.ReadOnly = True
                    txtRouteAbbrev.Visible = True
                    txtStepNumber.ReadOnly = True
                    txtStepNumber.CssClass = "Textbox_Display"
                    txtStep.Focus()
            End Select
        End Sub
        Private Function InsertRouteSteps() As Boolean
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

                RouteSteps.AddRouteSteps(SessionManager.SelectedRoute, txtStepNumber.Text, txtStep.Text, txtExpandStepDefinition.Text, txtStartDateOffset.Text, txtPlannedDuration.Text)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedRoute & "," & txtStepNumber.Text, strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertRouteStep ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateRouteSteps() As Boolean
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

                RouteSteps.UpdateRouteSteps(SessionManager.SelectedRoute, txtStepNumber.Text, txtStep.Text, txtExpandStepDefinition.Text, txtStartDateOffset.Text, txtPlannedDuration.Text)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedRoute & "," & txtStepNumber.Text, strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateRouteSteps ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function DeleteRouteSteps() As Boolean
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
                'RouteAbbrev Texbox contains text of form RouteAbbrev - Route
                'eg: AUTMG - Autonomous Management, we need just AUTMG from it
                RouteSteps.DeleteRouteSteps(SessionManager.SelectedRoute, txtStepNumber.Text)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedRoute & "," & txtStepNumber.Text, "Route Step Deleted", SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteRouteSteps ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
        End Function
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
            objDic.Add("StepNo", txtStepNumber.Text.Trim())
            objDic.Add("Step", txtStep.Text.Trim())
            objDic.Add("StepDefinition", txtExpandStepDefinition.Text.Trim())
            objDic.Add("StartDateOffset", txtStartDateOffset.Text.Trim())
            objDic.Add("PlannedDuration", txtPlannedDuration.Text.Trim())
            Return objDic
        End Function
#End Region

    End Class
End Namespace
