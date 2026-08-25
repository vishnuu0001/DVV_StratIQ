#Region "Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports System.Collections.Generic
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.UI.CustomControls
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class UserMaster3
        Inherits ApplicationBase

#Region " Private Variables"
        Private Shared ReadOnly FormName As String = "User Profile"
        Private Shared ReadOnly ProgramName As String = "UserMaster3"
        Private Shared ReadOnly DBTableName As String = "UserMaster"
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel, btnExit, btnChangePassword}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel", "Exit", "New Password"}
            Dim OutMessageArr() As String = {"", "", "", ""}
            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)
            btnChangePassword.Attributes.Add("onclick", "javascript:return NewPassword();")

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnExit.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
        End Sub
        Private Sub LoadPasswordChangeJavaScripts()
            txtConfNewPwd.Attributes.Add("onblur", "javascript:NextField(document.all." & txtNewPwd.ClientID & ");")
        End Sub
#End Region

#Region " Load Culture Translations"
        Private Sub LoadCultureTranslations()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.Add(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                lblUserName.Text = GetTranslationString("username", lblUserName.Text.Replace(":", "")) & ":"
                lblName.Text = GetTranslationString("name", lblName.Text.Replace(":", "")) & ":"
                lblDepartment.Text = GetTranslationString("department", lblDepartment.Text.Replace(":", "")) & ":"
                lblUserTitle.Text = GetTranslationString("title", lblUserTitle.Text.Replace(":", "")) & ":"
                lblInitialProgram.Text = GetTranslationString("initialprogram", lblInitialProgram.Text.Replace(":", "")) & ":"
                lblSite.Text = GetTranslationString("site", lblSite.Text.Replace(":", "")) & ":"
                lblCulture.Text = GetTranslationString("culture", lblCulture.Text.Replace(":", "")) & ":"
                lblWorkingSite.Text = GetTranslationString("workingsite", lblWorkingSite.Text.Replace(":", "")) & ":"
                lblShowMenuOptionNumbers.Text = GetTranslationString("showmenuoptionnumbers", lblShowMenuOptionNumbers.Text.Replace(":", "")) & ":"
                lblShowAllMenuOptions.Text = GetTranslationString("showallmenuoptions", lblShowAllMenuOptions.Text.Replace(":", "")) & ":"
                lblNewCulture.Text = GetTranslationString("newculture", lblNewCulture.Text.Replace(":", "")) & ":"
                lblNewWorkingSite.Text = GetTranslationString("newworkingsite", lblNewWorkingSite.Text.Replace(":", "")) & ":"
                lblNewDepartment.Text = GetTranslationString("newdepartment", lblNewDepartment.Text.Replace(":", "")) & ":"
                lblNewTitle.Text = GetTranslationString("newtitle", lblNewTitle.Text.Replace(":", "")) & ":"
                lblAllTeamView.Text = GetTranslationString("allteamview", lblAllTeamView.Text.Replace(":", "")) & ":"
                lblAllTeamEdit.Text = GetTranslationString("allteamedit", lblAllTeamEdit.Text.Replace(":", "")) & ":"
                lblAllKPIView.Text = GetTranslationString("allkpiview", lblAllKPIView.Text.Replace(":", "")) & ":"
                lblAllKPIEdit.Text = GetTranslationString("allkpiedit", lblAllKPIEdit.Text.Replace(":", "")) & ":"
                btnChangeCulture.Text = GetTranslationString("changeculture", btnChangeCulture.Text)
                btnChangeMenuOption.Text = GetTranslationString("changenenuoption", btnChangeMenuOption.Text)
                btnChangeDepartment.Text = GetTranslationString("changedepartment", btnChangeDepartment.Text)
                btnChangeTitle.Text = GetTranslationString("changetitle", btnChangeTitle.Text)
                btnChangeWorkingSite.Text = GetTranslationString("changeworkingsite", btnChangeWorkingSite.Text)
                btnChangePassword.Text = GetTranslationString("changepassword", btnChangePassword.Text)
                btnExit.Text = GetTranslationString("exit", btnExit.Text)
                lblSecurityGroups.Text = GetTranslationString("securitygroups", lblSecurityGroups.Text)
                lblUserSites.Text = GetTranslationString("usersites", lblUserSites.Text)
                lblAreaUsers.Text = GetTranslationString("areagroupusers", lblAreaUsers.Text)
                lblKPINotifications.Text = GetTranslationString("kpinotifications", lblKPINotifications.Text)
                lblNewPwd.Text = GetTranslationString("newpassword", lblNewPwd.Text.Replace(":", "")) & ":"
                lblConfPwd.Text = GetTranslationString("confirmpassword", lblConfPwd.Text.Replace(":", "")) & ":"
                btnOK.Text = GetTranslationString("ok", btnOK.Text)
                btnCancel.Text = GetTranslationString("cancel", btnCancel.Text)

            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadCultureTranslations", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
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

            If Not Page.IsPostBack Then
                LoadCultureTranslations()
            End If

            Master.IconImage = Request.ApplicationPath + "/images/user1_preferences.gif"
            Master.HeaderMessage = FormName

            LoadCommonJavaScripts()

            If SessionManager.NetworkLogin Then
                btnChangePassword.Visible = False
            End If

            mcSecurityGroups.StoredProcedureParams.Add("@UserID", SessionManager.UserID)
            mcUserSite.StoredProcedureParams.Add("@UserID", SessionManager.UserID)
            mcAreaGroupUsers.StoredProcedureParams.Add("@UserID", SessionManager.UserID)
            mcKPINotifications.StoredProcedureParams.Add("@UserID", SessionManager.UserID)

            If Not Page.IsPostBack Then
                BindTheData()
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

            If txtNewPwd.Text.Trim.Length > 0 Then
                Try
                    Dim strPwd As String = FormsAuthentication.HashPasswordForStoringInConfigFile(txtNewPwd.Text.ToUpper.Trim & SessionManager.UserID.ToString.ToUpper.Trim, "sha1")
                    UserMaster.AddNewPassword(SessionManager.UserID, strPwd)
                    RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.UserID.Trim.ToUpper.Trim(), "User Password Changed", SessionManager.UserID)
                Catch Exc As Exception
                    Master.DisplayErrors(ProgramName & " - AddNewPassword", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                    Return
                End Try
            End If

            If ddlCulture.SelectedValue.Trim.Length > 0 Then
                Try
                    Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                    Dim strChangeLog As String = TransactionProcessing.CompareDictionaryValues(SessionManager.RecordTransactionCurrentValues, objDic)

                    If strChangeLog.Trim.Length > 0 Then
                        UserMaster.UpdateUserCultureByID(SessionManager.UserID, ddlCulture.SelectedValue.Trim)
                        RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.UserID.Trim(), strChangeLog, SessionManager.UserID)
                    End If

                    SessionManager.CulturePref = ddlCulture.SelectedItem.Text
                    txtUserCulture.Text = ddlCulture.SelectedItem.Text.Trim
                Catch Exc As Exception
                    Master.DisplayErrors(ProgramName & " - UpdateCulture", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                    Return
                End Try
            End If

            If ddlWorkingSite.Visible = True Then
                Try
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.WorkingSite)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.WorkingSiteID)

                    txtWorkingSite.Text = ddlWorkingSite.SelectedItem.Text
                    If IsNumeric(ddlWorkingSite.SelectedItem.Value) Then
                        SessionManager.WorkingSite = txtWorkingSite.Text.Trim
                        SessionManager.WorkingSiteID = ddlWorkingSite.SelectedItem.Value
                    End If
                Catch Exc As Exception
                    Master.DisplayErrors(ProgramName & " - UpdateWorkingSite", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                    Return
                End Try
            End If

            If txtNewDepartmentNumber.Visible = True Then
                Try
                    Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                    Dim strChangeLog As String = TransactionProcessing.CompareDictionaryValues(SessionManager.RecordTransactionCurrentValues, objDic)

                    If strChangeLog.Trim.Length > 0 Then
                        UserMaster.UpdateDepartment(SessionManager.UserID, txtNewDepartmentNumber.Text.Trim)
                        RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.UserID, strChangeLog, SessionManager.UserID)
                    End If

                    txtDepartment.Text = txtNewDepartmentNumber.Text
                Catch Exc As Exception
                    Master.DisplayErrors(ProgramName & " - UpdateDepartment", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                    Return
                End Try
            End If

            If txtNewTitle.Visible = True Then
                Try
                    Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                    Dim strChangeLog As String = TransactionProcessing.CompareDictionaryValues(SessionManager.RecordTransactionCurrentValues, objDic)

                    If strChangeLog.Trim.Length > 0 Then
                        UserMaster.UpdateTitle(SessionManager.UserID, txtNewTitle.Text)
                        RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.UserID, strChangeLog, SessionManager.UserID)
                    End If

                    txtTitle.Text = txtNewTitle.Text
                Catch Exc As Exception
                    Master.DisplayErrors(ProgramName & " - UpdateTitle", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                    Return
                End Try
            Else
                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.CompareDictionaryValues(SessionManager.RecordTransactionCurrentValues, objDic)

                If strChangeLog.Trim.Length > 0 Then
                    UserMaster.UpdateMenuOption(SessionManager.UserID, chkShowMenuOptionNumbers.Checked)
                    RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.UserID, strChangeLog, SessionManager.UserID)
                End If
                SessionManager.ShowMenuOptionNumbers = chkShowMenuOptionNumbers.Checked
                SessionManager.ShowAllMenuOptions = chkShowAllMenuOptions.Checked
            End If

            txtNewPwd.Text = String.Empty
            txtConfNewPwd.Text = String.Empty
            txtNewPwd.Visible = False
            txtConfNewPwd.Visible = False
            lblNewPwd.Visible = False
            lblConfPwd.Visible = False
            lblNewCulture.Visible = False
            ddlCulture.Visible = False
            lblNewWorkingSite.Visible = False
            ddlWorkingSite.Visible = False
            txtNewDepartmentNumber.Text = String.Empty
            txtNewTitle.Text = String.Empty
            lblNewDepartment.Visible = False
            lblNewTitle.Visible = False
            txtNewDepartmentNumber.Visible = False
            txtNewTitle.Visible = False
            reqCulture.Enabled = False
            reqTitle.Enabled = False
            chkShowMenuOptionNumbers.Enabled = False
            chkShowAllMenuOptions.Enabled = False
            ChangeFunctionKeysStatus(FunctionKeys.Hide, btnOK, btnCancel)
            ChangeFunctionKeysStatus(FunctionKeys.Show, btnExit)

            Master.HeaderMessage = FormName
        End Sub

        Private Sub btnCancel_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnCancel.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            LoadCultureTranslations()

            txtNewPwd.Text = String.Empty
            txtConfNewPwd.Text = String.Empty
            txtNewPwd.Visible = False
            txtConfNewPwd.Visible = False
            lblNewPwd.Visible = False
            lblConfPwd.Visible = False
            lblNewCulture.Visible = False
            ddlCulture.Visible = False
            lblNewWorkingSite.Visible = False
            ddlWorkingSite.Visible = False
            txtNewDepartmentNumber.Text = String.Empty
            txtNewTitle.Text = String.Empty
            lblNewDepartment.Visible = False
            lblNewTitle.Visible = False
            txtNewDepartmentNumber.Visible = False
            txtNewTitle.Visible = False
            reqCulture.Enabled = False
            reqTitle.Enabled = False
            chkShowMenuOptionNumbers.Enabled = False
            chkShowAllMenuOptions.Enabled = False
            ChangeFunctionKeysStatus(FunctionKeys.Hide, btnOK, btnCancel)
            ChangeFunctionKeysStatus(FunctionKeys.Show, btnExit)

            Master.HeaderMessage = FormName
        End Sub

        Private Sub btnChangePassword_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnChangePassword.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try
            LoadCultureTranslations()
            LoadPasswordChangeJavaScripts()
            txtNewPwd.Focus()
            lblNewPwd.Visible = True
            lblConfPwd.Visible = True
            txtNewPwd.Visible = True
            txtConfNewPwd.Visible = True

            btnChangeCulture.Visible = False
            btnChangeWorkingSite.Visible = False
            btnChangeMenuOption.Visible = False
            btnChangeDepartment.Visible = False
            btnChangeTitle.Visible = False

            ChangeFunctionKeysStatus(FunctionKeys.Show, btnOK, btnCancel)
            ChangeFunctionKeysStatus(FunctionKeys.Hide, btnChangePassword, btnExit)

            Master.HeaderMessage = FormName & " - Change Password"
        End Sub
        Private Sub btnChangeCulture_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnChangeCulture.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try
            LoadCultureTranslations()
            BindCulture()
            lblNewCulture.Visible = True
            ddlCulture.Visible = True
            ddlCulture.Items.FindByText(txtUserCulture.Text).Selected = True
            ddlCulture.Focus()
            reqCulture.Enabled = True

            ChangeFunctionKeysStatus(FunctionKeys.Show, btnOK, btnCancel)
            ChangeFunctionKeysStatus(FunctionKeys.Hide, btnChangePassword, btnExit)

            btnChangeCulture.Visible = False
            btnChangeWorkingSite.Visible = False
            btnChangeMenuOption.Visible = False
            btnChangeDepartment.Visible = False
            btnChangeTitle.Visible = False

            Master.HeaderMessage = FormName + " - Change Culture"
        End Sub

        Private Sub btnChangeWorkingSite_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnChangeWorkingSite.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try
            LoadCultureTranslations()
            BindWorkingSite()
            lblNewWorkingSite.Visible = True
            ddlWorkingSite.Visible = True
            If txtWorkingSite.Text <> "" Then
                ddlWorkingSite.Items.FindByText(txtWorkingSite.Text).Selected = True
            End If
            ddlWorkingSite.Focus()

            ChangeFunctionKeysStatus(FunctionKeys.Show, btnOK, btnCancel)
            ChangeFunctionKeysStatus(FunctionKeys.Hide, btnChangePassword, btnExit)

            btnChangeCulture.Visible = False
            btnChangeWorkingSite.Visible = False
            btnChangeMenuOption.Visible = False
            btnChangeDepartment.Visible = False
            btnChangeTitle.Visible = False

            Master.HeaderMessage = FormName + " - Change Working Site"
        End Sub

        Private Sub btnChangeMenuOption_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnChangeMenuOption.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try
            LoadCultureTranslations()
            chkShowMenuOptionNumbers.Enabled = True
            chkShowAllMenuOptions.Enabled = True
            chkShowMenuOptionNumbers.Focus()
            ChangeFunctionKeysStatus(FunctionKeys.Show, btnOK, btnCancel)
            ChangeFunctionKeysStatus(FunctionKeys.Hide, btnChangePassword, btnExit)

            btnChangeCulture.Visible = False
            btnChangeWorkingSite.Visible = False
            btnChangeMenuOption.Visible = False
            btnChangeDepartment.Visible = False
            btnChangeTitle.Visible = False

            Master.HeaderMessage = FormName + " - Change Menu Option"
        End Sub

        Private Sub btnChangeDepartment_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnChangeDepartment.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try
            LoadCultureTranslations()
            lblNewDepartment.Visible = True
            txtNewDepartmentNumber.Visible = True
            txtNewDepartmentNumber.Attributes.Add("onkeydown", "javascript:Tab(document.all." & txtNewDepartmentNumber.UniqueID & ", document.all." & txtNewDepartmentNumber.UniqueID & ", window.event, 'No');")
            txtNewDepartmentNumber.Focus()

            ChangeFunctionKeysStatus(FunctionKeys.Show, btnOK, btnCancel)
            ChangeFunctionKeysStatus(FunctionKeys.Hide, btnChangePassword, btnExit)
            btnChangeCulture.Visible = False
            btnChangeWorkingSite.Visible = False
            btnChangeMenuOption.Visible = False
            btnChangeDepartment.Visible = False
            btnChangeTitle.Visible = False

            Master.HeaderMessage = FormName + " - Change Department"
        End Sub

        Private Sub btnChangeTitle_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnChangeTitle.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try
            LoadCultureTranslations()
            lblNewTitle.Visible = True
            txtNewTitle.Visible = True
            txtNewTitle.Attributes.Add("onkeydown", "javascript:Tab(document.all." & txtNewTitle.UniqueID & ", document.all." & txtNewTitle.UniqueID & ", window.event, 'No');")
            txtNewTitle.Focus()
            reqTitle.Enabled = True

            ChangeFunctionKeysStatus(FunctionKeys.Show, btnOK, btnCancel)
            ChangeFunctionKeysStatus(FunctionKeys.Hide, btnChangePassword, btnExit)

            btnChangeCulture.Visible = False
            btnChangeWorkingSite.Visible = False
            btnChangeMenuOption.Visible = False
            btnChangeDepartment.Visible = False
            btnChangeTitle.Visible = False

            Master.HeaderMessage = FormName + " - Change Title"
        End Sub

        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try
            If SessionManager.UserID <> "" Then
                RemoveCurrentProgramandGoBack()
            End If
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub BindCulture()
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
                ddlCulture.Items.Clear()
                CultureMaster.SelectCultureMasterList(ddlCulture)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindCulture", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindWorkingSite()
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
                ddlWorkingSite.Items.Clear()
                SiteMaster.SelectSiteMasterActiveList(ddlWorkingSite)
                ddlWorkingSite.Items.Insert(0, " ")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindSite", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindTheData()
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
                Dim dt As DataTable = UserMaster.SelectUserMaster(SessionManager.UserID)
                If dt.Rows.Count <> 0 Then
                    Dim dr As DataRow = dt.Rows(0)
                    txtUserID.Text = dr.Item("UserID").ToString.Trim()
                    txtUserName.Text = dr.Item("FirstName").ToString.Trim() & " " & dr.Item("LastName").ToString.Trim()
                    txtDepartment.Text = dr("DeptNumber").ToString
                    txtTitle.Text = dr("Title").ToString
                    txtInitialProgram.Text = dr.Item("InitialProgram").ToString.Trim()
                    txtSite.Text = dr("Site").ToString.Trim
                    txtUserCulture.Text = dr("CultureCode").ToString.Trim
                    txtWorkingSite.Text = SessionManager.WorkingSite
                    chkShowMenuOptionNumbers.Checked = dr.Item("ShowMenuOptionNumbers")
                    chkShowAllMenuOptions.Checked = SessionManager.ShowAllMenuOptions
                    ckAllTeamView.Checked = dr("AllTeamView")
                    ckAllTeamEdit.Checked = dr("AllTeamEdit")
                    ckAllKPIView.Checked = dr("AllKPIView")
                    ckAllKPIEdit.Checked = dr("AllKPIEdit")
                    If SessionManager.RecordTransactionCurrentValues IsNot Nothing Then
                        SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RecordTransactionCurrentValues)
                    End If
                    Dim objDic As New Dictionary(Of String, String)
                    objDic.Add("DeptNumber", txtDepartment.Text.Trim())
                    objDic.Add("Title", txtTitle.Text.Trim())
                    objDic.Add("InitialProgram", txtInitialProgram.Text.Trim())
                    objDic.Add("Site", txtSite.Text.Trim())
                    objDic.Add("CultureCode", txtUserCulture.Text.Trim())
                    objDic.Add("ShowMenuOptionNumbers", chkShowMenuOptionNumbers.Checked)
                    SessionManager.RecordTransactionCurrentValues = objDic
                End If

                mcSecurityGroups.DataBind()
                mcUserSite.DataBind()
                mcAreaGroupUsers.DataBind()
                mcKPINotifications.DataBind()
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindTheData", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub

#Region " GetUpdatedValues"
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
                If txtNewDepartmentNumber IsNot Nothing AndAlso txtNewDepartmentNumber.Visible = True Then
                    objDic.Add("DeptNumber", txtNewDepartmentNumber.Text.Trim())
                Else
                    objDic.Add("DeptNumber", txtDepartment.Text.Trim())
                End If

                If txtNewTitle IsNot Nothing AndAlso txtNewTitle.Visible = True Then
                    objDic.Add("Title", txtNewTitle.Text.Trim())
                Else
                    objDic.Add("Title", txtTitle.Text.Trim())
                End If

                objDic.Add("InitialProgram", txtInitialProgram.Text.Trim())
                If ddlWorkingSite IsNot Nothing Then
                    If ddlWorkingSite.SelectedItem IsNot Nothing Then
                        objDic.Add("Site", ddlWorkingSite.SelectedItem.Text.Trim())
                    Else
                        objDic.Add("Site", txtSite.Text.Trim())
                    End If
                Else
                    objDic.Add("Site", txtSite.Text.Trim())
                End If
                If ddlCulture IsNot Nothing Then
                    If ddlCulture.SelectedItem IsNot Nothing Then
                        objDic.Add("CultureCode", ddlCulture.SelectedValue.Trim)
                    Else
                        objDic.Add("CultureCode", txtUserCulture.Text.Trim())
                    End If
                Else
                    objDic.Add("CultureCode", txtUserCulture.Text.Trim())
                End If
                objDic.Add("ShowMenuOptionNumbers", chkShowMenuOptionNumbers.Checked)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - GetUpdatedValues", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
            Return objDic
        End Function
#End Region

#End Region

    End Class
End Namespace
