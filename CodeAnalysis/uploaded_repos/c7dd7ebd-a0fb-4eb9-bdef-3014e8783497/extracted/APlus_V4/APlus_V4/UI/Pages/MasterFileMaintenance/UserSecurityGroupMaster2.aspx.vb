#Region " Imports"
Imports System.IO
Imports System.Collections.Generic
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class UserSecurityGroupMaster2
        Inherits ApplicationBase

#Region " Private Constant Variables"
        Private Shared ReadOnly FormName As String = "User Security Group Master"
        Private Shared ReadOnly ProgramName As String = "UserSecurityGroupMaster2"
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

        Private Sub LoadAddModeJavaScript()
            Dim myTabArray() As Object = {ddlUserID, _
                                          ddlSecurityGroup}

            Dim TabKeyDownArr() As String = {Tab(ddlSecurityGroup, ddlSecurityGroup, "No"), _
                                            Tab(ddlUserID, ddlUserID, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
#End Region

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, CType(sender, Page).Title.Trim(), "Page_Load")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Master.IconImage = Request.ApplicationPath + "/images/user1_lock.gif"
            Master.HeaderMessage = FormName & " - " & SessionManager.UserSecurityGroupMasterMode.Replace("Row", "") & " User Security Group"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                Select Case SessionManager.UserSecurityGroupMasterMode
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this User Security Group.');")
                        TransactionHistory.LockControl = True
                    Case "AddRow"
                        TransactionHistory.Visible = False
                        BindUserName()
                        BindSecurityGroup()
                        If Not String.IsNullOrEmpty(SessionManager.SelectedValueUser.Trim()) Then
                            Dim objItem As ListItem
                            objItem = ddlUserID.Items.FindByValue(SessionManager.SelectedValueUser)
                            If Not IsNothing(objItem) Then
                                objItem.Selected = True
                                txtUserID.Text = objItem.Text
                                txtUserID.Visible = True
                                ddlUserID.Visible = False
                            Else
                                txtUserID.Visible = False
                                ddlUserID.Visible = True
                            End If
                        Else
                            txtUserID.Visible = False
                            ddlUserID.Visible = True
                        End If

                        If ddlUserID.Visible = True Then
                            ddlUserID.Focus()
                        Else
                            ddlSecurityGroup.Focus()
                        End If
                        txtSecurityGroup.Visible = False
                        ddlSecurityGroup.Visible = True
                        LoadAddModeJavaScript()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserSecurityGroupMaster1"), False)
                End Select
            End If
        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, CType(sender, Button).ID, "btnExit_Click")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue2)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue3)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue4)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.UserSecurityGroupMasterMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserSecurityGroupMaster1"), False)
        End Sub
        Private Sub btnOK_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, CType(sender, Button).ID, "btnOK_Click")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim blnSuccess As Boolean
            Select Case SessionManager.UserSecurityGroupMasterMode
                Case "DeleteRow"
                    txtUserID.Text = SessionManager.SelectedValue2
                    blnSuccess = DeleteUserSecurityGroup()
                Case "AddRow"
                    txtUserID.Text = ddlUserID.SelectedValue.ToString.Trim()
                    txtSecurityGroup.Text = ddlSecurityGroup.SelectedItem.Text.Trim()
                    blnSuccess = InsertUserSecurityGroup()
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue2)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue3)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue4)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.UserSecurityGroupMasterMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserSecurityGroupMaster1"), False)
            End If
        End Sub
        Private Sub btnCancel_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnCancel.Click
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
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue2)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue3)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue4)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.UserSecurityGroupMasterMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserSecurityGroupMaster1"), False)
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub AddUserToList()
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
                Dim da As DataTable = UserMaster.SelectUserMaster(SessionManager.SelectedValueUser)
                If da.Rows.Count > 0 Then
                    ddlUserID.Items.Add(New ListItem(da.Rows(0).Item("LastName").ToString.Trim() + ", " + da.Rows(0).Item("FirstName").ToString.Trim() + " (" + da.Rows(0).Item("UserID").ToString.Trim() + ")", da.Rows(0).Item("UserID").ToString.Trim()))
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - AddUserToList", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindUserName()
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
                UserMaster.SelectUserNameList(SessionManager.WorkingSiteID, ddlUserID)
                ddlUserID.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindUserName", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
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
                If SessionManager.RecordTransactionCurrentValues IsNot Nothing Then
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RecordTransactionCurrentValues)
                End If
                TransactionHistory.RecordID = SessionManager.SelectedValue2 & "," & SessionManager.SelectedValue4

                txtUserID.Text = SessionManager.SelectedValue + ", " + SessionManager.SelectedValue1 + " (" + SessionManager.SelectedValue2 + ")"
                txtSecurityGroup.Text = SessionManager.SelectedValue3
                txtUserID.Visible = True
                ddlUserID.Visible = False
                txtSecurityGroup.Visible = True
                ddlSecurityGroup.Visible = False

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("User", SessionManager.SelectedValue + ", " + SessionManager.SelectedValue1 + " (" + SessionManager.SelectedValue2 + ")")
                objDic.Add("SecurityGroup", SessionManager.SelectedValue3)
                SessionManager.RecordTransactionCurrentValues = objDic
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
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

            Select Case SessionManager.UserSecurityGroupMasterMode
                Case "ViewRow"
                    pnlOKCancel.Visible = False
                    txtUserID.ReadOnly = True
                    txtUserID.CssClass = "Textbox_Display"
                    txtSecurityGroup.ReadOnly = True
                    txtSecurityGroup.CssClass = "Textbox_Display"
                Case "DeleteRow"
                    txtSecurityGroup.ReadOnly = True
                    txtSecurityGroup.CssClass = "Textbox_Display"
            End Select
        End Sub
        Private Function InsertUserSecurityGroup() As Boolean
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

                UserSecurityGroupMaster.AddUserSecurityGroupMaster(txtUserID.Text.Trim(), CInt(ddlSecurityGroup.SelectedItem.Value))
                RecordTransactionHistory.InsertRecordTransactionHistory("UserSecurityGroupMaster", txtUserID.Text.ToUpper.Trim() & "," & ddlSecurityGroup.SelectedItem.Value.ToString.Trim(), strChangeLog, SessionManager.UserID)
                RecordTransactionHistory.InsertRecordTransactionHistory("UserMaster", txtUserID.Text.ToUpper.Trim(), strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertUserSecurityGroup", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function DeleteUserSecurityGroup() As Boolean
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
                UserSecurityGroupMaster.DeleteUserSecurityGroupMaster(SessionManager.SelectedValue2, CInt(SessionManager.SelectedValue4))
                RecordTransactionHistory.InsertRecordTransactionHistory("UserSecurityGroupMaster", SessionManager.SelectedValue2 & "," & SessionManager.SelectedValue4, "User Security Group Deleted", SessionManager.UserID)
                RecordTransactionHistory.InsertRecordTransactionHistory("UserMaster", SessionManager.SelectedValue2, "User Security Group Deleted: " & txtSecurityGroup.Text.Trim, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteUserSecurityGroup", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
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
            Try
                objDic.Add("User", ddlUserID.SelectedItem.Text.Trim())
                objDic.Add("SecurityGroup", ddlSecurityGroup.SelectedItem.Text.Trim())
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - GetUpdatedValues", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
            Return objDic
        End Function
#End Region

    End Class
End Namespace