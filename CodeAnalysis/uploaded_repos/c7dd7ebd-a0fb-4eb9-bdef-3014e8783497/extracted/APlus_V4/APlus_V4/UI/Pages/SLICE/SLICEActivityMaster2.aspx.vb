#Region " Imports "

Imports System.IO
Imports System.Data
Imports System.Text
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.SLICETables
Imports WebApp.APlus.UI.CustomControls
Imports WebApp.APlus.DataAccess.Tables
Imports System.Collections.Generic

#End Region

Namespace WebApp.APlus.UI.SLICE
    Partial Class SLICEActivityMaster2
        Inherits ApplicationBase

#Region " Private Constants "
        Private Shared ReadOnly FormName As String = "SLICE Activity Maintenance"
        Private Shared ReadOnly ProgramName As String = "SLICEActivityMaster2"
        Private Shared ReadOnly DBTableName As String = "SLICEActivityMaster"
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel, btnExit}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel", "Exit"}
            Dim OutMessageArr() As String = {"", "", ""}
            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnExit.UniqueID + "'))")
        End Sub
        Private Sub LoadAddModeJavaScripts()
            Dim myTabArray() As Object = {ddlEntity, _
                                          ddlPosition, _
                                          txtPresentationSequence, _
                                          ddlSLICEFrequency, _
                                          txtExpandMeasurement, _
                                          txtExpandDesiredCondition, _
                                          txtTargetTime}

            Dim TabKeyDownArr() As String = {Tab(ddlPosition, txtTargetTime, "No"), _
                                             Tab(txtPresentationSequence, ddlEntity, "No"), _
                                             Tab(ddlSLICEFrequency, ddlPosition, "Int"), _
                                             Tab(txtExpandMeasurement, txtPresentationSequence, "No"), _
                                             Tab(txtExpandDesiredCondition, ddlSLICEFrequency, "No"), _
                                             Tab(txtTargetTime, txtExpandMeasurement, "No"), _
                                             Tab(ddlEntity, txtExpandDesiredCondition, "Int")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)

        End Sub
        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {ddlEntity, _
                                          ddlPosition, _
                                          txtPresentationSequence, _
                                          ddlSLICEFrequency, _
                                          txtExpandMeasurement, _
                                          txtExpandDesiredCondition, _
                                          txtTargetTime}

            Dim TabKeyDownArr() As String = {Tab(ddlPosition, txtTargetTime, "No"), _
                                             Tab(txtPresentationSequence, ddlEntity, "No"), _
                                             Tab(ddlSLICEFrequency, ddlPosition, "Int"), _
                                             Tab(txtExpandMeasurement, txtPresentationSequence, "No"), _
                                             Tab(txtExpandDesiredCondition, ddlSLICEFrequency, "No"), _
                                             Tab(txtTargetTime, txtExpandMeasurement, "No"), _
                                             Tab(ddlEntity, txtExpandDesiredCondition, "Int")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
#End Region

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim strSelectedSLICEActivityID As String = "0"

            Master.HeaderMessage = FormName & " - " & SessionManager.SLICEActivityMasterMode.Replace("Row", "")
            Master.IconImage = Request.ApplicationPath + "/images/clipboard.png"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                Select Case SessionManager.SLICEActivityMasterMode
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                        ShowActivityButtonsAndMasterControls(True)
                    Case "EditRow"
                        UnEnableRecords()
                        LoadEditModeJavaScripts()
                        LoadSelectedRecord()
                        ShowActivityButtonsAndMasterControls(True)
                        ddlEntity.Focus()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this SLICE Activity.');")
                        TransactionHistory1.LockControl = True
                        ShowActivityButtonsAndMasterControls(True)
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        LoadAddModeJavaScripts()
                        BindDropDownLists()
                        UnEnableRecords()
                        LoadActivityGroupTextBox()
                        ShowActivityButtonsAndMasterControls(False)
                        ddlEntity.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEActivityMaster1"), False)
                End Select
            End If

            If SessionManager.SelectedValueSLICEActivityID > 0 Then
                mcActivityLinks.StoredProcedureParams.Add("@ActivityID", SessionManager.SelectedValueSLICEActivityID)
                mcActivityResults.StoredProcedureParams.Add("@ActivityID", SessionManager.SelectedValueSLICEActivityID)
                mcSliceTypes.StoredProcedureParams.Add("@SLICEActivityID", SessionManager.SelectedValueSLICEActivityID)
            Else
                mcActivityLinks.StoredProcedureParams.Add("@ActivityID", strSelectedSLICEActivityID)
                mcActivityResults.StoredProcedureParams.Add("@ActivityID", strSelectedSLICEActivityID)
                mcSliceTypes.StoredProcedureParams.Add("@SLICEActivityID", strSelectedSLICEActivityID)
                SessionManager.SelectedValueSLICEActivityID = -1
            End If

            If Not Page.IsPostBack Then
                mcActivityLinks.DataBind(True)
                mcActivityResults.DataBind(True)
                mcSliceTypes.DataBind(True)
            End If
        End Sub
        Private Sub btnOK_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim blnSuccess As Boolean
            Select Case SessionManager.SLICEActivityMasterMode
                Case "EditRow"
                    blnSuccess = UpdateSLICEActivityMaster()
                Case "AddRow"
                    blnSuccess = InsertSLICEActivityMaster()
                    If SessionManager.SelectedValueSLICEActivityID > 0 Then
                        SessionManager.SLICEActivityMasterMode = "EditRow"
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEActivityMaster2"), False)

                        Return
                    End If
                Case "DeleteRow"
                    blnSuccess = DeleteSLICEActivityMaster()
            End Select

            If blnSuccess Then
                Master.WriteErrors(FormName, SessionManager.SLICEActivityMaster1 & " SLICE Activity " & SessionManager.SelectedValueActivityID, SessionManager.UserID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SLICEActivityMasterMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEActivityMaster1"), False)
            End If
        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.SLICEActivityMasterMode = "EditRow" Or SessionManager.SLICEActivityMasterMode = "ViewRow" Or _
                SessionManager.SLICEActivityMasterMode = "DeleteRow" Or SessionManager.SLICEActivityMasterMode = "AddRow" Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SLICEActivityMasterMode)
            End If
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEActivityMaster1"), False)
        End Sub
        Private Sub btnCancel_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnCancel.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SLICEActivityMasterMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEActivityMaster1"), False)
        End Sub
        Protected Sub btnSliceTypes_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnSliceTypes.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.MasterControlExitProgram = "SLICEActivityMaster2"
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEActivityTypeMaster1"), False)
        End Sub
        Private Sub btnSLICEActivityLinks_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnSLICEActivityLinks.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.MasterControlExitProgram = "SLICEActivityMaster2"
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEActivityLinksMaster1"), False)
        End Sub
        Protected Sub mcActivityLinks_onRowDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewRowEventArgs) Handles mcActivityLinks.onRowDataBound
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If e.Row.RowType = DataControlRowType.DataRow Then
                If e.Row.Cells(2).Text.Trim.Length > 0 Then
                    Dim strURL As String = e.Row.Cells(2).Text.Trim
                    Dim objLink As New HyperLink
                    objLink.Text = e.Row.Cells(2).Text.Trim
                    objLink.NavigateUrl = strURL
                    objLink.Target = "_blank"
                    e.Row.Cells(2).Controls.Add(objLink)
                End If
            End If
        End Sub
        Private Sub btnSLICEActivityResults_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnSLICEActivityResults.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.MasterControlExitProgram = "SLICEActivityMaster2"
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEActivityResults"), False)
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub ShowActivityButtonsAndMasterControls(ByVal blnShow As Boolean)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, blnShow)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                If blnShow Then
                    If ProgramSecurity.CanUserAccessProgram(SessionManager.UserID, "SLICEActivityTypeMaster1") Then
                        btnSliceTypes.Visible = True
                    End If

                    If ProgramSecurity.CanUserAccessProgram(SessionManager.UserID, "SLICEActivityLinksMaster1") Then
                        btnSLICEActivityLinks.Visible = True
                    End If

                    If ProgramSecurity.CanUserAccessProgram(SessionManager.UserID, "SLICEActivityResults") Then
                        btnSLICEActivityResults.Visible = True
                    End If
                Else
                    pnlSliceTypes.Visible = False
                    pnlActivityLinks.Visible = False
                    pnlActivityResults.Visible = False
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - ShowActivityButtonsAndMasterControls() ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub LoadActivityGroupTextBox()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim objItem As ListItem = ddlSLICEActivityGroup.Items.FindByValue(SessionManager.SLICEActivityGroupMasterID)
                If Not objItem Is Nothing Then
                    objItem.Selected = True
                    txtSLICEActivityGroup.Text = objItem.Text
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadActivityGroupTextBox() ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub LoadSelectedRecord()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim objItem As ListItem
            Try

                Dim dt As DataTable = SLICEActivityMaster.SelectSLICEActivityMasterAsDataTable(SessionManager.SelectedValueSLICEActivityID)
                If dt.Rows.Count <> 0 Then
                    txtSLICEActivityID.Text = dt.Rows(0)("SLICEActivityID").ToString.Trim()
                    BindDropDownLists()
                    objItem = ddlSLICEActivityGroup.Items.FindByValue(dt.Rows(0)("SLICEActivityGroupID").ToString)
                    If Not objItem Is Nothing Then
                        objItem.Selected = True
                        txtSLICEActivityGroup.Text = objItem.Text
                    End If
                    objItem = ddlEntity.Items.FindByValue(dt.Rows(0)("EntityID").ToString)
                    If Not objItem Is Nothing Then
                        objItem.Selected = True
                        txtEntity.Text = objItem.Text
                    End If
                    objItem = ddlPosition.Items.FindByValue(dt.Rows(0)("PositionID").ToString)
                    If Not objItem Is Nothing Then
                        objItem.Selected = True
                        txtPosition.Text = objItem.Text
                    End If

                    txtPresentationSequence.Text = dt.Rows(0)("PresentationSequence").ToString.Trim()
                    objItem = ddlSLICEFrequency.Items.FindByValue(dt.Rows(0)("SLICEFrequencyID").ToString)
                    If Not objItem Is Nothing Then
                        objItem.Selected = True
                        txtSLICEFrequency.Text = objItem.Text
                    End If
                    txtExpandMeasurement.Text = dt.Rows(0)("Measurement").ToString.Trim
                    txtExpandDesiredCondition.Text = dt.Rows(0)("DesiredCondition").ToString.Trim
                    txtTargetTime.Text = dt.Rows(0)("TargetTime").ToString.Trim

                    TransactionHistory1.TableName = DBTableName
                    TransactionHistory1.RecordID = SessionManager.SelectedValueSLICEActivityID

                    Dim objDic As New Dictionary(Of String, String)
                    objDic.Add("SLICEActivityGroup", ddlSLICEActivityGroup.SelectedItem.Text.Trim())
                    objDic.Add("Entity", ddlEntity.SelectedItem.Text.Trim())
                    objDic.Add("Position", ddlPosition.SelectedItem.Text.Trim())
                    objDic.Add("PresentationSequence", txtPresentationSequence.Text.Trim())
                    objDic.Add("SLICEFrequencyID", ddlSLICEFrequency.SelectedItem.Text.Trim())
                    objDic.Add("Measurement", txtExpandMeasurement.Text.Trim())
                    objDic.Add("DesiredCondition", txtExpandDesiredCondition.Text.Trim())
                    objDic.Add("TargetTime", txtTargetTime.Text.Trim())
                    objDic.Add("LastCompletedDate", txtLastCompleted.Text.Trim())
                    SessionManager.RecordTransactionCurrentValues = objDic
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub UnEnableRecords()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.SLICEActivityMasterMode = "ViewRow" Then
                ddlPosition.Visible = False
                ddlEntity.Visible = False
                ddlSLICEActivityGroup.Visible = False
                txtSLICEActivityGroup.Visible = True
                txtEntity.Visible = True
                txtEntity.Text = ddlEntity.SelectedItem.Text
                txtPosition.Visible = True
                btnSLICEActivityLinks.Text = "SLICE Activity Links"
                btnSLICEActivityResults.Text = "SLICE Activity Results"
                txtPresentationSequence.ReadOnly = True
                txtPresentationSequence.CssClass = "Textbox_Display"
                txtSLICEFrequency.Visible = True
                ddlSLICEFrequency.Visible = False
                txtExpandMeasurement.ReadOnly = True
                txtExpandMeasurement.CssClass = "Textbox_Display"
                txtExpandDesiredCondition.ReadOnly = True
                txtExpandDesiredCondition.CssClass = "Textbox_Display"
                txtTargetTime.ReadOnly = True
                txtTargetTime.CssClass = "Textbox_Display"
                pnlOKCancel.Visible = False
            ElseIf SessionManager.SLICEActivityMasterMode = "DeleteRow" Then
                txtSLICEActivityGroup.ReadOnly = True
                ddlSLICEActivityGroup.Visible = False
                ddlPosition.Visible = False
                ddlEntity.Visible = False
                txtPresentationSequence.CssClass = "Textbox_Display"
                ddlSLICEFrequency.Visible = False
                txtExpandMeasurement.CssClass = "Textbox_Display"
                txtExpandDesiredCondition.CssClass = "Textbox_Display"
                txtTargetTime.CssClass = "Textbox_Display"
            ElseIf SessionManager.SLICEActivityMasterMode = "EditRow" Then
                ddlSLICEActivityGroup.Visible = False
                txtSLICEActivityGroup.Visible = True
                txtEntity.Visible = False
                txtPosition.Visible = False
                txtSLICEFrequency.Visible = False
            ElseIf SessionManager.SLICEActivityMasterMode = "AddRow" Then
                txtSLICEActivityID.Text = "New"
                txtSLICEActivityGroup.Visible = True
                ddlSLICEActivityGroup.Visible = False
                txtEntity.Visible = False
                txtPosition.Visible = False
                txtSLICEFrequency.Visible = False
                txtLastCompleted.Visible = True
            End If
        End Sub
        Private Function InsertSLICEActivityMaster() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
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

                SessionManager.SelectedValueSLICEActivityID = SLICEActivityMaster.AddSLICEActivityMaster(ddlSLICEActivityGroup.SelectedValue, _
                                    ddlEntity.SelectedValue, ddlPosition.SelectedValue, txtPresentationSequence.Text.Trim, _
                                    ddlSLICEFrequency.SelectedValue, txtExpandMeasurement.Text.Trim, _
                                    txtExpandDesiredCondition.Text.Trim, txtTargetTime.Text.Trim)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueSLICEActivityID, strChangeLog, SessionManager.UserID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertSLICEActivityMaster", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
            Return True
        End Function
        Private Function DeleteSLICEActivityMaster() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                SLICEActivityMaster.DeleteSLICEActivityMaster(SessionManager.SelectedValueSLICEActivityID)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueSLICEActivityID, "SLICE Activity Deleted", SessionManager.UserID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteSLICEActivityMaster", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
            Return True
        End Function
        Private Function UpdateSLICEActivityMaster() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
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

                SLICEActivityMaster.UpdateSLICEActivityMaster(SessionManager.SelectedValueSLICEActivityID, _
                                                        ddlSLICEActivityGroup.SelectedValue.ToString.Trim(), _
                                                        ddlEntity.SelectedValue.ToString.Trim(), _
                                                        ddlPosition.SelectedValue.ToString.Trim(), _
                                                        ddlSLICEFrequency.SelectedValue.ToString.Trim(), _
                                                        txtPresentationSequence.Text.Trim, _
                                                        txtExpandMeasurement.Text.Trim, _
                                                        txtExpandDesiredCondition.Text.Trim, _
                                                        txtTargetTime.Text.Trim)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueSLICEActivityID, strChangeLog, SessionManager.UserID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateSLICEActivityMaster", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
            Return True
        End Function
        Private Sub BindDropDownLists()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            BindSLICEFrequencyMaster()
            BindEntityMaster()
            BindPositionMaster()
            BindSLICEActivityGroup()
        End Sub
        Private Sub BindSLICEFrequencyMaster()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                SLICEFrequencyMaster.SelectSLICEFrequencyMasterList(ddlSLICEFrequency)
                ddlSLICEFrequency.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindSLICEFrequencyMaster", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindEntityMaster()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                EntityMaster.SelectEntityMasterList(ddlEntity, SessionManager.SelectedWorkCenterID)
                ddlEntity.Items.Insert(0, " ")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindEntityMaster", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindPositionMaster()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                PositionMaster.SelectPositionMasterList(ddlPosition)
                ddlPosition.Items.Insert(0, " ")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindPositionMaster", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindSLICEActivityGroup()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                SLICEActivityGroupMaster.SelectSLICEActivityGroupMasterList(ddlSLICEActivityGroup)
                ddlSLICEActivityGroup.Items.Insert(0, " ")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindSLICEActivityGroup", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Function GetUpdatedValues() As Dictionary(Of String, String)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim objDic As New Dictionary(Of String, String)
            objDic.Add("SLICEActivityGroup", ddlSLICEActivityGroup.SelectedItem.Text.Trim())
            objDic.Add("Entity", ddlEntity.SelectedItem.Text.Trim())
            objDic.Add("Position", ddlPosition.SelectedItem.Text.Trim())
            objDic.Add("PresentationSequence", txtPresentationSequence.Text.Trim())
            objDic.Add("SLICEFrequencyID", ddlSLICEFrequency.SelectedItem.Text.Trim())
            objDic.Add("Measurement", txtExpandMeasurement.Text.Trim())
            objDic.Add("DesiredCondition", txtExpandDesiredCondition.Text.Trim())
            objDic.Add("TargetTime", txtTargetTime.Text.Trim())
            objDic.Add("LastCompletedDate", txtLastCompleted.Text.Trim())
            Return objDic
        End Function
#End Region

    End Class
End Namespace

