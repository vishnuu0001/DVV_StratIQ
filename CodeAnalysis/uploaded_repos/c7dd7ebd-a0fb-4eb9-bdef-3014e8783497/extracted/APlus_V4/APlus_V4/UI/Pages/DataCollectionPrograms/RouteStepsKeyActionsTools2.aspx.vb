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
    Partial Class RouteStepsKeyActionsTools2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Route Steps Key Actions Tools"
        Private Shared ReadOnly ProgramName As String = "RouteStepsKeyActionsTools2"
        Private Shared ReadOnly DBTableName As String = "RouteStepsKeyActionsTools"
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
        Private Sub LoadAddEditModeJavaScripts()
            Dim myTabArray() As Object = {ddlTemplateFile, _
                                          ddlTrainingFile, _
                                          txtExpandURLLink}

            Dim TabKeyDownArr() As String = {Tab(ddlTrainingFile, txtExpandURLLink, "No"), _
                                             Tab(txtExpandURLLink, ddlTemplateFile, "No"), _
                                             Tab(ddlTemplateFile, ddlTrainingFile, "No")}

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

            Master.HeaderMessage = FormName & " - " & SessionManager.RouteStepsKeyActionsToolsMode.Replace("Row", "")
            Master.IconImage = Request.ApplicationPath + "/images/Routes.gif"
            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                LoadDropDownListBoxes()

                Select Case SessionManager.RouteStepsKeyActionsToolsMode
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Route Step.');")
                        TransactionHistory1.LockControl = True
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        LoadAddEditModeJavaScripts()
                        txtRouteAbbrev.Text = SessionManager.SelectedRoute + " - " + Routes.GetRoute(SessionManager.SelectedRoute)
                        txtStepNumber.Text = SessionManager.SelectedRouteStepNo
                        txtKeyActionNumber.Text = SessionManager.SelectedKeyActionNo
                        txtTool.Focus()
                    Case "EditRow"
                        LoadAddEditModeJavaScripts()
                        LoadSelectedRecord()
                        UnEnableRecords()
                        'ddlTemplateFile.Focus()
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
            Select Case SessionManager.RouteStepsKeyActionsToolsMode
                Case "DeleteRow"
                    blnSuccess = DeleteRouteStepsKeyActionsTool()
                Case "AddRow"
                    blnSuccess = InsertRouteStepsKeyActionsTool()
                Case "EditRow"
                    blnSuccess = UpdateRouteStepsKeyActionsTool()
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedKeyActionToolID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RouteStepsKeyActionsToolsMode)
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

            If SessionManager.RouteStepsKeyActionsToolsMode = "EditRow" Or SessionManager.RouteStepsKeyActionsToolsMode = "ViewRow" Or SessionManager.RouteStepsKeyActionsToolsMode = "DeleteRow" Or SessionManager.RouteStepsKeyActionsToolsMode = "AddRow" Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedKeyActionToolID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RouteStepsKeyActionsToolsMode)
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedKeyActionToolID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RouteStepsKeyActionsToolsMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RouteOverview"), False)
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadDropDownListBoxes()
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
                ddlTemplateFile.Items.Clear()
                ddlTrainingFile.Items.Clear()
                AttachmentsMaster.SelectAttachmentsByTypeList(AttachmentTypes.SelectAttachmentTypeIDByType("Template"), "en", ddlTemplateFile)
                AttachmentsMaster.SelectAttachmentsByTypeList(AttachmentTypes.SelectAttachmentTypeIDByType("Training"), "en", ddlTrainingFile)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadDropDownListBoxes ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
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
                Dim ds As DataTable = RouteStepsKeyActionsTools.SelectRouteStepsKeyActionsTool(SessionManager.SelectedKeyActionToolID)
                Dim dr As DataRow = ds.Rows(0)
                Dim objItem As ListItem

                txtRouteAbbrev.Text = SessionManager.SelectedRoute.ToString + " - " + Routes.GetRoute(SessionManager.SelectedRoute.ToString)
                txtStepNumber.Text = dr("StepNo")
                txtKeyActionNumber.Text = dr("KeyActionNo")
                txtTool.Text = dr("Tool").ToString


                If dr("AttachmentType") IsNot DBNull.Value Then
                    If dr("AttachmentType").ToString = "Template" Then
                        objItem = ddlTemplateFile.Items.FindByValue(dr("AttachmentID").ToString)
                        If Not objItem Is Nothing Then
                            objItem.Selected = True
                            txtTemplateFile.Text = objItem.Text
                        End If
                    Else
                        objItem = ddlTrainingFile.Items.FindByValue(dr("AttachmentID").ToString)
                        If Not objItem Is Nothing Then
                            objItem.Selected = True
                            txtTrainingFile.Text = objItem.Text
                        End If
                    End If
                End If

                txtExpandURLLink.Text = dr("URLLink").ToString

                TransactionHistory1.TableName = DBTableName
                TransactionHistory1.RecordID = SessionManager.SelectedKeyActionToolID

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("RouteAbbrev", txtRouteAbbrev.Text.Trim())
                objDic.Add("StepNo", txtStepNumber.Text.Trim())
                objDic.Add("KeyActionNo", txtKeyActionNumber.Text.Trim())
                objDic.Add("Tool", txtTool.Text.Trim())
                objDic.Add("URLLink", txtExpandURLLink.Text.Trim())
                If Not String.IsNullOrEmpty(ddlTemplateFile.SelectedItem.Text.Trim()) Then
                    objDic.Add("Attachment", ddlTemplateFile.SelectedItem.Text.Trim())
                ElseIf Not String.IsNullOrEmpty(ddlTrainingFile.SelectedItem.Text.Trim()) Then
                    objDic.Add("Attachment", ddlTrainingFile.SelectedItem.Text.Trim())
                Else
                    objDic.Add("Attachment", "")
                End If
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

            Select Case SessionManager.RouteStepsKeyActionsToolsMode
                Case "DeleteRow"
                    txtTool.ReadOnly = True
                    txtTool.CssClass = "Textbox_Display"
                    ddlTemplateFile.Visible = False
                    txtTemplateFile.Visible = True
                    ddlTrainingFile.Visible = False
                    txtTrainingFile.Visible = True
                    txtExpandURLLink.ReadOnly = True
                    txtExpandURLLink.CssClass = "Textbox_Display"
                Case "ViewRow"
                    pnlOKCancel.Visible = False
                    txtTool.ReadOnly = True
                    txtTool.CssClass = "Textbox_Display"
                    ddlTemplateFile.Visible = False
                    txtTemplateFile.Visible = True
                    ddlTrainingFile.Visible = False
                    txtTrainingFile.Visible = True
                    txtExpandURLLink.ReadOnly = True
                    txtExpandURLLink.CssClass = "Textbox_Display"
            End Select
        End Sub
        Private Function InsertRouteStepsKeyActionsTool() As Boolean
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
                'Dim iTrainingAttachment As Integer = 0
                'If ddlTemplateFile.SelectedItem.Value.Trim.Length > 0 Then
                '    iTemplateAttachment = ddlTemplateFile.SelectedItem.Value
                'End If
                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                Dim iAttachment As Integer = 0
                If Not String.IsNullOrEmpty(ddlTemplateFile.SelectedItem.Text.Trim()) Then
                    iAttachment = ddlTemplateFile.SelectedItem.Value
                ElseIf Not String.IsNullOrEmpty(ddlTrainingFile.SelectedItem.Text.Trim()) Then
                    iAttachment = ddlTrainingFile.SelectedItem.Value
                End If

                Dim intResult As Integer = RouteStepsKeyActionsTools.AddRouteStepsKeyActionsTool(txtTool.Text.Trim(), txtRouteAbbrev.Text.Trim(), CInt(txtStepNumber.Text), CInt(txtKeyActionNumber.Text), txtExpandURLLink.Text.Trim(), iAttachment)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, intResult, strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertRouteStepsKeyActionsTool ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function

        Private Function UpdateRouteStepsKeyActionsTool() As Boolean
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

                Dim iAttachment As Integer = 0
                If Not String.IsNullOrEmpty(ddlTemplateFile.SelectedItem.Text.Trim()) Then
                    iAttachment = ddlTemplateFile.SelectedItem.Value
                ElseIf Not String.IsNullOrEmpty(ddlTrainingFile.SelectedItem.Text.Trim()) Then
                    iAttachment = ddlTrainingFile.SelectedItem.Value
                End If
                RouteStepsKeyActionsTools.UpdateRouteStepsKeyActionsTool(SessionManager.SelectedKeyActionToolID, txtTool.Text.Trim(), txtExpandURLLink.Text.Trim(), iAttachment)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedKeyActionToolID, strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateRouteStepsKeyActionsTool ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function

        Private Function DeleteRouteStepsKeyActionsTool() As Boolean
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
                RouteStepsKeyActionsTools.DeleteRouteStepsKeyActionsTool(SessionManager.SelectedKeyActionToolID)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedKeyActionToolID, "Route Step Key Action Tool Deleted", SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteRouteStepsKeyActionsTool ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
        End Function
#End Region

#Region " Get Updated Values"
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
            objDic.Add("Tool", txtTool.Text.Trim())
            objDic.Add("URLLink", txtExpandURLLink.Text.Trim())
            If Not String.IsNullOrEmpty(ddlTemplateFile.SelectedItem.Text.Trim()) Then
                objDic.Add("Attachment", ddlTemplateFile.SelectedItem.Text.Trim())
            ElseIf Not String.IsNullOrEmpty(ddlTrainingFile.SelectedItem.Text.Trim()) Then
                objDic.Add("Attachment", ddlTrainingFile.SelectedItem.Text.Trim())
            Else
                objDic.Add("Attachment", "")
            End If
            Return objDic
        End Function
#End Region

    End Class
End Namespace
