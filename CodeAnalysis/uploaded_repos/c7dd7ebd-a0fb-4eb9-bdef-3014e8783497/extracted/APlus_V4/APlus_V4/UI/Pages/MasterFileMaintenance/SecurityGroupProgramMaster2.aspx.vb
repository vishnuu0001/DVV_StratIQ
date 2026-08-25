#Region " Imports"
Imports System.IO
Imports System.Collections.Generic
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class SecurityGroupProgramMaster2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Security Group Program Master"
        Private Shared ReadOnly ProgramName As String = "SecurityGroupProgramMaster2"
        Private Shared ReadOnly DBTableName As String = "SecurityGroupProgramMaster"
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
            Dim myTabArray() As Object = {ddlSecurityGroup, _
                                          ddlProgram, _
                                          ckAllowAdd, _
                                          ckAllowEdit, _
                                          ckAllowDelete}

            Dim TabKeyDownArr() As String = {Tab(ddlProgram, ckAllowDelete, "No"), _
                                            Tab(ckAllowAdd, ddlSecurityGroup, "No"), _
                                            Tab(ckAllowEdit, ddlProgram, "No"), _
                                            Tab(ckAllowDelete, ckAllowAdd, "No"), _
                                            Tab(ddlSecurityGroup, ckAllowEdit, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {ckAllowAdd, _
                                          ckAllowEdit, _
                                          ckAllowDelete}

            Dim TabKeyDownArr() As String = {Tab(ckAllowEdit, ckAllowDelete, "No"), _
                                            Tab(ckAllowDelete, ckAllowAdd, "No"), _
                                            Tab(ckAllowAdd, ckAllowEdit, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub

#End Region

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, ProgramName, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Master.IconImage = Request.ApplicationPath + "/images/SecurityGroupProgramMaster.gif"
            Master.HeaderMessage = SessionManager.SecurityGroupProgramMasterMode.Replace("Row", "") & " Security Group Program"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                Select Case SessionManager.SecurityGroupProgramMasterMode.ToString
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Security Group Program.');")
                        TransactionHistory1.LockControl = True
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        txtProgram.Visible = False
                        txtSecurityGroup.Visible = False
                        BindProgram()
                        BindSecurityGroup()
                        LoadAddModeJavaScripts()
                        ddlSecurityGroup.Focus()
                    Case "EditRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        LoadEditModeJavaScripts()
                        ckAllowAdd.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SecurityGroupProgramMaster1"), False)
                End Select
            End If
        End Sub
        Private Sub btnOK_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim blnSuccess As Boolean
            Select Case SessionManager.SecurityGroupProgramMasterMode.ToString
                Case "DeleteRow"
                    blnSuccess = DeleteSecurityGroupProgram()
                Case "AddRow"
                    blnSuccess = InsertSecurityGroupProgram()
                    txtSecurityGroup.Text = ddlSecurityGroup.SelectedItem.ToString.Trim()
                    txtProgram.Text = ddlProgram.SelectedItem.ToString.Trim()
                Case "EditRow"
                    blnSuccess = UpdateSecurityGroupProgram()
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SecurityGroupProgramMasterMode)
                Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar & (ProgramSecurity.GetProgramURL("SecurityGroupProgramMaster1")), False)
            End If
        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click, btnCancel.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SecurityGroupProgramMasterMode)
            Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar & (ProgramSecurity.GetProgramURL("SecurityGroupProgramMaster1")), False)
        End Sub
#End Region

#Region " Custom methods"
        Private Sub LoadSelectedRecord()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim objDT As DataTable = SecurityGroupProgramMaster.SelectSecurityGroupProgramMaster(SessionManager.SelectedValue, SessionManager.SelectedValue1)
                If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                    Dim dtRow As DataRow = objDT.Rows(0)
                    txtSecurityGroup.Text = dtRow("SecurityGroup").ToString
                    txtProgram.Text = dtRow("Program").ToString
                    ckAllowAdd.Checked = Convert.ToBoolean(dtRow("AllowAdd"))
                    ckAllowEdit.Checked = Convert.ToBoolean(dtRow("AllowEdit"))
                    ckAllowDelete.Checked = Convert.ToBoolean(dtRow("AllowDelete"))
                End If

                txtSecurityGroup.Visible = True
                ddlSecurityGroup.Visible = False
                txtProgram.Visible = True
                ddlProgram.Visible = False

                If SessionManager.RecordTransactionCurrentValues IsNot Nothing Then
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RecordTransactionCurrentValues)
                End If
                TransactionHistory1.TableName = DBTableName
                TransactionHistory1.RecordID = SessionManager.SelectedValue & "," & SessionManager.SelectedValue1

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("AllowAdd", ckAllowAdd.Checked)
                objDic.Add("AllowEdit", ckAllowEdit.Checked)
                objDic.Add("AllowDelete", ckAllowDelete.Checked)
                SessionManager.RecordTransactionCurrentValues = objDic
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindProgram()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                ProgramMaster.GetProgramList(ddlProgram)
                ddlProgram.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindProgram", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindSecurityGroup()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                SecurityGroupMaster.SelectSecurityGroupMaster(ddlSecurityGroup)
                ddlSecurityGroup.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindSecurityGroup", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub UnEnableRecords()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Select Case SessionManager.SecurityGroupProgramMasterMode
                Case "ViewRow"
                    pnlOKCancel.Visible = False
                    txtSecurityGroup.ReadOnly = True
                    txtSecurityGroup.CssClass = "Textbox_Display"
                    txtProgram.ReadOnly = True
                    txtProgram.CssClass = "Textbox_Display"
                    ckAllowAdd.Enabled = False
                    ckAllowEdit.Enabled = False
                    ckAllowDelete.Enabled = False
                Case "DeleteRow"
                    txtSecurityGroup.ReadOnly = True
                    txtSecurityGroup.CssClass = "Textbox_Display"
                    txtProgram.ReadOnly = True
                    txtProgram.CssClass = "Textbox_Display"
                    ckAllowAdd.Enabled = False
                    ckAllowEdit.Enabled = False
                    ckAllowDelete.Enabled = False
            End Select
        End Sub
        Private Function InsertSecurityGroupProgram() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
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
                SecurityGroupProgramMaster.AddSecurityGroupProgramMaster(CInt(ddlSecurityGroup.SelectedItem.Value), ddlProgram.SelectedItem.Value.ToString.Trim(), ckAllowAdd.Checked, ckAllowEdit.Checked, ckAllowDelete.Checked)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, ddlSecurityGroup.SelectedItem.Value.ToString.Trim() & "," & ddlProgram.SelectedItem.Value.ToString.Trim(), strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertSecurityGroupProgram", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateSecurityGroupProgram() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
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
                SecurityGroupProgramMaster.UpdateSecurityGroupProgramMaster(SessionManager.SelectedValue, SessionManager.SelectedValue1, ckAllowAdd.Checked, ckAllowEdit.Checked, ckAllowDelete.Checked)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValue & "," & SessionManager.SelectedValue1, strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateSecurityGroupProgram", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function DeleteSecurityGroupProgram() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                SecurityGroupProgramMaster.DeleteSecurityGroupProgramMaster(SessionManager.SelectedValue, SessionManager.SelectedValue1)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValue & "," & SessionManager.SelectedValue1, "Security Group Program Deleted", SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteSecurityGroupProgram", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
        End Function
        Private Function GetUpdatedValues() As Dictionary(Of String, String)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim objDic As New Dictionary(Of String, String)
            objDic.Add("AllowAdd", ckAllowAdd.Checked)
            objDic.Add("AllowEdit", ckAllowEdit.Checked)
            objDic.Add("AllowDelete", ckAllowDelete.Checked)
            Return objDic
        End Function
#End Region

    End Class
End Namespace

