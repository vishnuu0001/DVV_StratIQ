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
    Partial Class RouteStepsKeyActions2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Route Steps Key Actions"
        Private Shared ReadOnly ProgramName As String = "RouteStepsKeyActions2"
        Private Shared ReadOnly DBTableName As String = "RouteStepsKeyActions"
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
            Dim myTabArray() As Object = {txtKeyActionNumber, _
                                          txtKeyAction _
                                         }

            Dim TabKeyDownArr() As String = {Tab(txtKeyAction, txtKeyAction, "Int"), _
                                             Tab(txtKeyActionNumber, txtKeyActionNumber, "No")}

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

            Master.HeaderMessage = FormName & " - " & SessionManager.RouteStepsKeyActionsMode.Replace("Row", "")
            Master.IconImage = Request.ApplicationPath + "/images/Routes.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                Select Case SessionManager.RouteStepsKeyActionsMode
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Key Action.');")
                        TransactionHistory1.LockControl = True
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        LoadAddModeJavaScripts()
                        txtRouteAbbrev.Text = SessionManager.SelectedRoute + " - " + Routes.GetRoute(SessionManager.SelectedRoute)
                        txtStepNumber.Text = SessionManager.SelectedRouteStepNo
                        txtStepNumber.ReadOnly = True
                        txtStepNumber.CssClass = "Textbox_Display"
                        txtKeyActionNumber.Focus()
                    Case "EditRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RouteOverview"), False)
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
            If SessionManager.RouteStepsKeyActionsMode = "DeleteRow" Then
                blnSuccess = DeleteRouteStepsKeyAction()
            ElseIf SessionManager.RouteStepsKeyActionsMode = "AddRow" Then
                blnSuccess = InsertRouteStepsKeyAction()
            ElseIf SessionManager.RouteStepsKeyActionsMode = "EditRow" Then
                blnSuccess = UpdateRouteStepsKeyAction()
            End If
            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedKeyActionNo)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RouteStepsKeyActionsMode)
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

            If SessionManager.RouteStepsKeyActionsMode = "Edit" Or SessionManager.RouteStepsKeyActionsMode = "View" Or SessionManager.RouteStepsKeyActionsMode = "Delete" Or SessionManager.RouteStepsKeyActionsMode = "AddRow" Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedKeyActionNo)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RouteStepsKeyActionsMode)
            End If
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedKeyActionNo)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RouteStepsKeyActionsMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RouteOverview"), False)
        End Sub

        Private Sub btnTools_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnTools.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            UpdateRouteStepsKeyAction()
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RouteStepsKeyActionsTools1"), False)
        End Sub

        Private Sub btnToolsView_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnToolsView.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RouteStepsKeyActionsTools1"), False)
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
                Dim dt As DataTable = RouteStepKeyActions.SelectRouteStepKeyAction(SessionManager.SelectedRoute, SessionManager.SelectedRouteStepNo, SessionManager.SelectedKeyActionNo)
                Dim dr As DataRow = dt.Rows(0)
                Dim dtRoutes As DataTable = Routes.SelectRoutesByKey(dr("RouteAbbrev"))
                Dim drRoutes As DataRow = dtRoutes.Rows(0)

                txtStepNumber.Text = dr("StepNo")
                txtKeyActionNumber.Text = dr("KeyActionNo")
                txtKeyAction.Text = dr("KeyAction")
                txtRouteAbbrev.Text = drRoutes("RouteAbbrev").ToString & " - " & drRoutes("Route").ToString

                TransactionHistory1.TableName = DBTableName
                TransactionHistory1.RecordID = SessionManager.SelectedRoute & "," & SessionManager.SelectedRouteStepNo & "," & SessionManager.SelectedKeyActionNo

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("RouteAbbrev", txtRouteAbbrev.Text.Trim())
                objDic.Add("StepNo", txtStepNumber.Text.Trim())
                objDic.Add("KeyActionNo", txtKeyActionNumber.Text.Trim())
                objDic.Add("KeyAction", txtKeyAction.Text.Trim())
                SessionManager.RecordTransactionCurrentValues = objDic

            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
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

            Select Case SessionManager.RouteStepsKeyActionsMode
                Case "ViewRow"
                    pnlOKCancel.Visible = False
                    txtStepNumber.ReadOnly = True
                    txtStepNumber.CssClass = "Textbox_Display"
                    txtKeyActionNumber.ReadOnly = True
                    txtKeyActionNumber.CssClass = "Textbox_Display"
                    txtKeyAction.ReadOnly = True
                    txtKeyAction.CssClass = "Textbox_Display"
                Case "DeleteRow"
                    txtStepNumber.ReadOnly = True
                    txtStepNumber.CssClass = "Textbox_Display"
                    txtKeyActionNumber.ReadOnly = True
                    txtKeyActionNumber.CssClass = "Textbox_Display"
                    txtKeyAction.ReadOnly = True
                    txtKeyAction.CssClass = "Textbox_Display"
                Case "EditRow"
                    txtStepNumber.ReadOnly = True
                    txtStepNumber.CssClass = "Textbox_Display"
                    txtKeyActionNumber.ReadOnly = True
                    txtKeyActionNumber.CssClass = "Textbox_Display"
                    txtKeyAction.Focus()
            End Select
        End Sub
        Private Function InsertRouteStepsKeyAction() As Boolean
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

                RouteStepKeyActions.AddRouteStepsKeyAction(SessionManager.SelectedRoute, txtStepNumber.Text, txtKeyActionNumber.Text, txtKeyAction.Text)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedRoute & "," & SessionManager.SelectedRouteStepNo & "," & SessionManager.SelectedKeyActionNo, strChangeLog, SessionManager.UserID)
                RecordTransactionHistory.InsertRecordTransactionHistory("RouteSteps", SessionManager.SelectedRoute & "," & SessionManager.SelectedRouteStepNo, "Route Step Key Action Inserted:" & vbCrLf & strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertRouteStepsKeyAction ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateRouteStepsKeyAction() As Boolean
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

                RouteStepKeyActions.UpdateRouteStepsKeyAction(SessionManager.SelectedRoute, CInt(SessionManager.SelectedRouteStepNo), CInt(SessionManager.SelectedKeyActionNo), txtKeyAction.Text.Trim)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedRoute & "," & SessionManager.SelectedRouteStepNo & "," & SessionManager.SelectedKeyActionNo, strChangeLog, SessionManager.UserID)
                RecordTransactionHistory.InsertRecordTransactionHistory("RouteSteps", SessionManager.SelectedRoute & "," & SessionManager.SelectedRouteStepNo, "Route Step Key Action Updated:" & vbCrLf & strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateRouteStepsKeyAction ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function DeleteRouteStepsKeyAction() As Boolean
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
                RouteStepKeyActions.DeleteRouteStepsKeyAction(SessionManager.SelectedRoute, CInt(SessionManager.SelectedRouteStepNo), CInt(SessionManager.SelectedKeyActionNo))
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedRoute & "," & SessionManager.SelectedRouteStepNo & "," & SessionManager.SelectedKeyActionNo, "Route Step Key Action Deleted", SessionManager.UserID)
                RecordTransactionHistory.InsertRecordTransactionHistory("RouteSteps", SessionManager.SelectedRoute & "," & SessionManager.SelectedRouteStepNo, "Route Step Key Action Deleted", SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteRouteStepsKeyAction ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
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
            objDic.Add("KeyActionNo", txtKeyActionNumber.Text.Trim())
            objDic.Add("KeyAction", txtKeyAction.Text.Trim())
            Return objDic
        End Function
#End Region

    End Class
End Namespace
