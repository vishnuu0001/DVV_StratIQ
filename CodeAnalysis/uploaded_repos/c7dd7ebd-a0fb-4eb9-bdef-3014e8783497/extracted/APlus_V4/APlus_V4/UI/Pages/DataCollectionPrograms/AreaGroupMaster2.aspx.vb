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
    Partial Class AreaGroupMaster2
        Inherits ApplicationBase

#Region " Private Variables"
        Private Shared ReadOnly FormName As String = "Area Group Maintenance"
        Private Shared ReadOnly ProgramName As String = "AreaGroupMaster2"
        Private Shared ReadOnly DBTableName As String = "AreaGroupMaster"
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
            Dim myTabArray() As Object = {txtAreaGroup, _
                                          txtAreaGroupAbbrev, _
                                          txtSequence, _
                                          ddlArea, _
                                          ckActive}

            Dim TabKeyDownArr() As String = {Tab(txtAreaGroupAbbrev, ckActive, "No"), _
                                             Tab(txtSequence, txtAreaGroup, "No"), _
                                             Tab(ddlArea, txtAreaGroupAbbrev, "Int"), _
                                             Tab(ckActive, txtSequence, "No"), _
                                             Tab(txtAreaGroup, ddlArea, "No")}

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

            Master.HeaderMessage = FormName & " - " & SessionManager.AreaGroupMasterMode.Replace("Row", "")
            Master.IconImage = Request.ApplicationPath + "/images/boss.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            mcAreas.StoredProcedureParams.Add("@AreaGroupID", SessionManager.SelectedValueAreaGroupID)

            mcUsers.StoredProcedureParams.Add("@AreaGroupID", SessionManager.SelectedValueAreaGroupID)

            If Not Page.IsPostBack Then
                BindDropDownLists()

                Select Case SessionManager.AreaGroupMasterMode
                    Case "ViewRow"
                        pnlExit.Visible = True
                        pnlOKCancel.Visible = False
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        pnlOKCancel.Visible = True
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Area Group.');")
                        TransactionHistory1.LockControl = True
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        txtAreaGroupID.Text = "New"
                        LoadAddEditModeJavaScripts()
                        txtAreaGroup.Focus()
                        pnlGrids.Visible = False
                    Case "EditRow"
                        LoadAddEditModeJavaScripts()
                        LoadSelectedRecord()
                        UnEnableRecords()
                        txtAreaGroup.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AreaGroupMaster1"), False)
                End Select
            End If
        End Sub
        Protected Sub btnAreas_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnAreas.Click, btnAreas1.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Select Case SessionManager.AreaGroupMasterMode
                Case "ViewRow", "DeleteRow"
                    SessionManager.MasterControlExitProgram = "AreaGroupMaster2"
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AreaGroupAreaMaster1"), False)
                Case Else
                    If SaveRecord() Then
                        SessionManager.AreaGroupMasterMode = "EditRow"
                        SessionManager.MasterControlExitProgram = "AreaGroupMaster2"
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AreaGroupAreaMaster1"), False)
                    End If
            End Select
        End Sub
        Protected Sub btnUsers_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnUsers.Click, btnUsers1.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Select Case SessionManager.AreaGroupMasterMode
                Case "ViewRow", "DeleteRow"
                    SessionManager.MasterControlExitProgram = "AreaGroupMaster2"
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AreaGroupUserMaster1"), False)
                Case Else
                    If SaveRecord() Then
                        SessionManager.AreaGroupMasterMode = "EditRow"
                        SessionManager.MasterControlExitProgram = "AreaGroupMaster2"
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AreaGroupUserMaster1"), False)
                    End If
            End Select
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

            Dim blnSuccess As Boolean = SaveRecord()

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueAreaGroupID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.AreaGroupMasterMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AreaGroupMaster1"), False)
            End If
        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click, btnCancel.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueAreaGroupID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.AreaGroupMasterMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AreaGroupMaster1"), False)
        End Sub
#End Region

#Region " Custom Methods"
        Private Function SaveRecord() As Boolean
            Dim blnSuccess As Boolean

            Select Case SessionManager.AreaGroupMasterMode
                Case "AddRow"
                    blnSuccess = InsertAreaGroup()
                Case "EditRow"
                    blnSuccess = UpdateAreaGroup()
                Case "DeleteRow"
                    blnSuccess = DeleteAreaGroup()
            End Select

            Return blnSuccess
        End Function
        Private Sub BindDropDownLists()
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
                AreaMaster.GetAreaMasterList(ddlArea, SessionManager.WorkingSiteID)
                ddlArea.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindDropDownLists", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                Return
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

            Dim objDT As DataTable = AreaGroupMaster.SelectAreaGroupMasterByID(Convert.ToInt16(SessionManager.SelectedValueAreaGroupID))
            If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                Dim dtRow As DataRow = objDT.Rows(0)

                txtAreaGroupID.Text = SessionManager.SelectedValueAreaGroupID
                txtSite.Text = dtRow("Site").ToString
                txtAreaGroup.Text = dtRow("AreaGroup").ToString
                txtAreaGroupAbbrev.Text = dtRow("AreaGroupAbbrev").ToString
                txtSequence.Text = dtRow("Sequence").ToString
                Dim objItem As ListItem = ddlArea.Items.FindByValue(dtRow("DefaultAreaID").ToString)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                    txtArea.Text = objItem.Text
                End If
                ckActive.Checked = Convert.ToBoolean(dtRow("Active"))

                mcAreas.DataBind()
                mcUsers.DataBind()

                TransactionHistory1.TableName = DBTableName
                TransactionHistory1.RecordID = SessionManager.SelectedValueAreaGroupID.ToString.Trim()

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("Site", txtSite.Text.Trim)
                objDic.Add("AreaGroup", txtAreaGroup.Text.Trim())
                objDic.Add("AreaGroupAbbrev", txtAreaGroupAbbrev.Text.Trim())
                objDic.Add("Sequence", txtSequence.Text)
                objDic.Add("Area", txtArea.Text.Trim)
                objDic.Add("Active", ckActive.Checked.ToString)
                SessionManager.RecordTransactionCurrentValues = objDic
            End If
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

            Select Case SessionManager.AreaGroupMasterMode.ToString()
                Case "ViewRow", "DeleteRow"
                    pnlOKCancel.Visible = False
                    txtAreaGroup.ReadOnly = True
                    txtAreaGroup.CssClass = "Textbox_Display"
                    txtAreaGroupAbbrev.ReadOnly = True
                    txtAreaGroupAbbrev.CssClass = "Textbox_Display"
                    txtSequence.ReadOnly = True
                    txtSequence.CssClass = "Textbox_Display"
                    ddlArea.Visible = False
                    txtArea.Visible = True
                    ckActive.Enabled = False
            End Select
        End Sub
        Private Function InsertAreaGroup() As Boolean
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

                Dim iAreaID As Integer = 0
                If ddlArea.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlArea.SelectedItem.Value) Then
                    iAreaID = ddlArea.SelectedItem.Value
                End If

                SessionManager.SelectedValueAreaGroupID = AreaGroupMaster.InsertAreaGroup(SessionManager.WorkingSiteID, txtAreaGroup.Text.Trim, txtAreaGroupAbbrev.Text.Trim, txtSequence.Text, iAreaID, ckActive.Checked)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueAreaGroupID.ToString, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertAreaGroup", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateAreaGroup() As Boolean
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

                Dim iAreaID As Integer = 0
                If ddlArea.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlArea.SelectedItem.Value) Then
                    iAreaID = ddlArea.SelectedItem.Value
                End If

                AreaGroupMaster.UpdateAreaGroup(SessionManager.SelectedValueAreaGroupID, txtAreaGroup.Text.Trim, txtAreaGroupAbbrev.Text.Trim, txtSequence.Text, iAreaID, ckActive.Checked)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueAreaGroupID.ToString.Trim(), strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateAreaGroup", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function DeleteAreaGroup() As Boolean
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
                AreaGroupMaster.DeleteAreaGroup(SessionManager.SelectedValueAreaGroupID)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueAreaGroupID.ToString.Trim(), "Area Group Deleted", SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteAreaGroup", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
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
            objDic.Add("Site", txtSite.Text.Trim)
            objDic.Add("AreaGroup", txtAreaGroup.Text.Trim())
            objDic.Add("AreaGroupAbbrev", txtAreaGroupAbbrev.Text.Trim())
            objDic.Add("Sequence", txtSequence.Text)
            If ddlArea.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlArea.SelectedItem.Value) Then
                objDic.Add("Area", ddlArea.SelectedItem.Text)
            Else
                objDic.Add("Area", "")
            End If
            objDic.Add("Active", ckActive.Checked.ToString)

            Return objDic
        End Function
#End Region

    End Class
End Namespace
