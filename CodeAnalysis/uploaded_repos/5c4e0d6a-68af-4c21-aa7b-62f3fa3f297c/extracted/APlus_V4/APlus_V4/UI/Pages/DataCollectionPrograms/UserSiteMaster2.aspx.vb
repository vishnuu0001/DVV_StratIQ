#Region " Imports"
Imports System.IO
Imports System.Collections.Generic
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class UserSiteMaster2
        Inherits ApplicationBase

#Region " Private Constant Variables"
        Private Shared ReadOnly FormName As String = "User Site Master"
        Private Shared ReadOnly ProgramName As String = "UserSiteMaster2"
        Private Shared ReadOnly DBTableName As String = "UserSiteMaster"
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
        Private Sub LoadAddEditModeJavaScript()
            Dim myTabArray() As Object = {ddlUserID, _
                                          ddlSite, _
                                          ckAllowTeamView, _
                                          ckAllowTeamEdit, _
                                          ckAllowKPIView, _
                                          ckAllowKPIEdit}

            Dim TabKeyDownArr() As String = {Tab(ddlSite, ckAllowKPIEdit, "No"), _
                                            Tab(ckAllowTeamView, ddlUserID, "No"), _
                                            Tab(ckAllowTeamEdit, ddlSite, "No"), _
                                            Tab(ckAllowKPIView, ckAllowTeamView, "No"), _
                                            Tab(ckAllowKPIEdit, ckAllowTeamEdit, "No"), _
                                            Tab(ddlUserID, ckAllowKPIView, "No")}

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

            Master.IconImage = Request.ApplicationPath + "/images/Padlock-User-Control.gif"
            Master.HeaderMessage = FormName & " - " & SessionManager.UserSiteMasterMode.Replace("Row", "")
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                BindLists()

                Select Case SessionManager.UserSiteMasterMode
                    Case "ViewRow"
                        pnlOKCancel.Visible = False
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "EditRow"
                        LoadAddEditModeJavaScript()
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this User Site Record.');")
                        TransactionHistory1.LockControl = True
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        ddlUserID.Focus()

                        If Not String.IsNullOrEmpty(SessionManager.SelectedValueUser.Trim()) Then
                            Dim objItem As ListItem
                            objItem = ddlUserID.Items.FindByValue(SessionManager.SelectedValueUser)

                            If Not IsNothing(objItem) Then
                                objItem.Selected = True
                                txtUserID.Text = objItem.Text
                                txtUserID.Visible = True
                                ddlUserID.Visible = False
                            Else
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
                            End If
                        Else
                            txtUserID.Visible = False
                            ddlUserID.Visible = True
                        End If

                        If ddlUserID.Visible = True Then
                            ddlUserID.Focus()
                        Else
                            ddlSite.Focus()
                        End If

                        LoadAddEditModeJavaScript()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserSiteMaster1"), False)
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue2)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.UserSiteMasterMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserSiteMaster1"), False)
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
            Select Case SessionManager.UserSiteMasterMode
                Case "DeleteRow"
                    blnSuccess = DeleteUserSiteMaster()
                Case "AddRow"
                    blnSuccess = InsertUserSiteMaster()
                Case "EditRow"
                    blnSuccess = UpdateUserSiteMaster()
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue2)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.UserSiteMasterMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserSiteMaster1"), False)
            End If
        End Sub
        Private Sub btnCancel_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnCancel.Click, btnExit.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue2)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.UserSiteMasterMode)

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserSiteMaster1"), False)
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub BindLists()
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

                SiteMaster.SelectSiteMasterActiveList(ddlSite)
                ddlSite.Items.Insert(0, " ")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindLists", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
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

            If SessionManager.RecordTransactionCurrentValues IsNot Nothing Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RecordTransactionCurrentValues)
            End If

            Try
                Dim objDT As DataTable = UserSiteMaster.SelectUserSiteMaster(SessionManager.SelectedValue1, SessionManager.SelectedValue2)
                If objDT IsNot Nothing AndAlso objDT.Rows.Count > 0 Then
                    Dim dtRow As DataRow = objDT.Rows(0)
                    Dim objItem As ListItem

                    objItem = ddlUserID.Items.FindByValue(SessionManager.SelectedValue1)
                    If Not objItem Is Nothing Then
                        objItem.Selected = True
                        txtUserID.Text = objItem.Text
                    Else
                        objItem = New ListItem(UserMaster.GetUserFullName(SessionManager.SelectedValue1), SessionManager.SelectedValue1)
                        ddluserid.items.insert(0, objItem)
                        objItem.Selected = True
                        txtuserid.text = objItem.Text
                    End If
                    objItem = ddlSite.Items.FindByValue(SessionManager.SelectedValue2)
                    If Not objItem Is Nothing Then
                        objItem.Selected = True
                        txtSite.Text = objItem.Text
                    ElseIf IsNumeric(dtRow("SiteID").ToString) Then
                        Dim dtSite As DataTable = SiteMaster.GetSiteMasterBySite(dtRow("SiteID").ToString)
                        If dtSite IsNot Nothing AndAlso dtSite.Rows.Count = 1 Then
                            objItem = New ListItem(dtSite.Rows(0)("Site").ToString, dtSite.Rows(0)("SiteID").ToString)
                            objItem.Selected = True
                            txtSite.Text = objItem.Text
                        End If
                    End If

                    ckAllowTeamView.Checked = Convert.ToBoolean(dtRow("AllowTeamView"))
                    ckAllowTeamEdit.Checked = Convert.ToBoolean(dtRow("AllowTeamEdit"))
                    ckAllowKPIView.Checked = Convert.ToBoolean(dtRow("AllowKPIView"))
                    ckAllowKPIEdit.Checked = Convert.ToBoolean(dtRow("AllowKPIEdit"))

                    TransactionHistory1.TableName = DBTableName
                    TransactionHistory1.RecordID = SessionManager.SelectedValue1 & "," & SessionManager.SelectedValue2

                    Dim objDic As New Dictionary(Of String, String)
                    objDic.Add("UserID", txtUserID.Text)
                    objDic.Add("Site", txtSite.Text)
                    objDic.Add("AllowTeamView", ckAllowTeamView.Checked.ToString)
                    objDic.Add("AllowTeamEdit", ckAllowTeamEdit.Checked.ToString)
                    objDic.Add("AllowKPIView", ckAllowKPIView.Checked.ToString)
                    objDic.Add("AllowKPIEdit", ckAllowKPIEdit.Checked.ToString)

                    SessionManager.RecordTransactionCurrentValues = objDic
                End If
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

            Select Case SessionManager.UserSiteMasterMode
                Case "ViewRow", "DeleteRow"
                    ddlUserID.Visible = False
                    ddlSite.Visible = False
                    txtUserID.Visible = True
                    txtSite.Visible = True
                    ckAllowTeamView.Enabled = False
                    ckAllowTeamEdit.Enabled = False
                    ckAllowKPIView.Enabled = False
                    ckAllowKPIEdit.Enabled = False
            End Select
        End Sub
        Private Function InsertUserSiteMaster() As Boolean
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

                If ckAllowTeamEdit.Checked AndAlso Not ckAllowTeamView.Checked Then
                    Master.DisplayError("Allow Team View must be checked when Allow Edit is checked.")
                    Return False
                End If
                If ckAllowKPIEdit.Checked AndAlso Not ckAllowKPIView.Checked Then
                    Master.DisplayError("Allow KPI View must be checked when Allow Edit is checked.")
                    Return False
                End If

                UserSiteMaster.AddUserSiteMaster(ddlUserID.SelectedItem.Value.ToUpper.Trim(), CInt(ddlSite.SelectedItem.Value()), ckAllowTeamView.Checked, ckAllowTeamEdit.Checked, ckAllowKPIView.Checked, ckAllowKPIEdit.Checked)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, ddlUserID.SelectedItem.Value.ToUpper.Trim() & "," & ddlSite.SelectedItem.Value(), strChangeLog, SessionManager.UserID)
                RecordTransactionHistory.InsertRecordTransactionHistory("UserMaster", ddlUserID.SelectedItem.Value.ToUpper.Trim(), strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertUserSiteMaster", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateUserSiteMaster() As Boolean
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

                If ckAllowTeamEdit.Checked AndAlso Not ckAllowTeamView.Checked Then
                    Master.DisplayError("Allow Team View must be checked when Allow Edit is checked.")
                    Return False
                End If
                If ckAllowKPIEdit.Checked AndAlso Not ckAllowKPIView.Checked Then
                    Master.DisplayError("Allow KPI View must be checked when Allow Edit is checked.")
                    Return False
                End If

                UserSiteMaster.UpdateUserSiteMaster(SessionManager.SelectedValue1, SessionManager.SelectedValue2, ckAllowTeamView.Checked, ckAllowTeamEdit.Checked, ckAllowKPIView.Checked, ckAllowKPIEdit.Checked)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValue1 & "," & SessionManager.SelectedValue2, strChangeLog, SessionManager.UserID)
                RecordTransactionHistory.InsertRecordTransactionHistory("UserMaster", SessionManager.SelectedValue1, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateUserSiteMaster", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function DeleteUserSiteMaster() As Boolean
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
                UserSiteMaster.DeleteUserSiteMaster(SessionManager.SelectedValue1, SessionManager.SelectedValue2)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValue1 & "," & SessionManager.SelectedValue2, "User Site Master Deleted", SessionManager.UserID)
                RecordTransactionHistory.InsertRecordTransactionHistory("UserMaster", SessionManager.SelectedValue1, "User Site Master Deleted: " & txtSite.Text.Trim, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteUserSiteMaster", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
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
            objDic.Add("UserID", ddlUserID.SelectedItem.Value.Trim())
            objDic.Add("Site", ddlSite.SelectedItem.Text.Trim())
            objDic.Add("AllowTeamView", ckAllowTeamView.Checked.ToString)
            objDic.Add("AllowTeamEdit", ckAllowTeamEdit.Checked.ToString)
            objDic.Add("AllowKPIView", ckAllowKPIView.Checked.ToString)
            objDic.Add("AllowKPIEdit", ckAllowKPIEdit.Checked.ToString)

            Return objDic
        End Function
#End Region

    End Class
End Namespace