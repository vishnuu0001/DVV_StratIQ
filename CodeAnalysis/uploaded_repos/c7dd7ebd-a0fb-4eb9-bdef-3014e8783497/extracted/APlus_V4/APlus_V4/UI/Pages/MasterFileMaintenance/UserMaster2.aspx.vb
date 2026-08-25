#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports System.Web.Security
Imports WebApp.APlus.UI.CustomControls
Imports System.Collections.Generic

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class UserMaster2
        Inherits ApplicationBase

#Region " Private Variables"
        Private Shared ReadOnly FormName As String = "User Master"
        Private Shared ReadOnly ProgramName As String = "UserMaster2"
        Private Shared ReadOnly DBTableName As String = "UserMaster"
        Private sInitialProgram As String = String.Empty
        Private sSite As String = String.Empty
        Private intCultureID As Integer
        Private strCulture As String = String.Empty
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel, btnExit}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel", "Exit"}
            Dim OutMessageArr() As String = {"", "", ""}
            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnExit.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
            Master.AddBodyAttribute("onkeydown", "javascript:DisallowViewDeleteModeTab(document.getElementById('" + txtPwd.UniqueID + "'),window.event)")
        End Sub
        Private Sub LoadAddModeJavaScripts()
            Dim myTabArray() As Object = {txtUserID, _
                                           txtPwd, _
                                            txtFirstName, _
                                            txtLastName, _
                                            txtMiddleInitial, _
                                            txtSuffix, _
                                            txtDepartmentNumber, _
                                            ddlInitialProgram, _
                                            ddlSite, _
                                            ddlCulture, _
                                            txtTitle, _
                                            txtEmailAddress, _
                                            chkAdmin, _
                                            chkRegTemp, _
                                            chkActive}

            Dim TabKeyDownArr() As String = {Tab(txtPwd, chkActive, "No"), _
                                                        Tab(txtFirstName, txtUserID, "No"), _
                                                        Tab(txtLastName, txtPwd, "No"), _
                                                        Tab(txtMiddleInitial, txtFirstName, "No"), _
                                                        Tab(txtSuffix, txtLastName, "No"), _
                                                        Tab(txtDepartmentNumber, txtMiddleInitial, "No"), _
                                                        Tab(ddlInitialProgram, txtSuffix, "No"), _
                                                        Tab(ddlSite, txtDepartmentNumber, "No"), _
                                                        Tab(ddlCulture, ddlInitialProgram, "No"), _
                                                        Tab(txtTitle, ddlSite, "No"), _
                                                        Tab(txtEmailAddress, ddlCulture, "No"), _
                                                        Tab(chkAdmin, txtTitle, "No"), _
                                                        Tab(chkRegTemp, txtEmailAddress, "No"), _
                                                        Tab(chkActive, chkAdmin, "No"), _
                                                        Tab(txtUserID, chkRegTemp, "No")}
            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {txtFirstName, _
                                            txtLastName, _
                                            txtMiddleInitial, _
                                            txtSuffix, _
                                            txtDepartmentNumber, _
                                            ddlInitialProgram, _
                                            ddlSite, _
                                            ddlCulture, _
                                            txtTitle, _
                                            txtEmailAddress, _
                                            chkAdmin, _
                                            chkRegTemp, _
                                            chkActive}

            Dim TabKeyDownArr() As String = {Tab(txtLastName, chkActive, "No"), _
                                                        Tab(txtMiddleInitial, txtFirstName, "No"), _
                                                        Tab(txtSuffix, txtLastName, "No"), _
                                                        Tab(txtDepartmentNumber, txtMiddleInitial, "No"), _
                                                        Tab(ddlInitialProgram, txtSuffix, "No"), _
                                                        Tab(ddlSite, txtDepartmentNumber, "No"), _
                                                        Tab(ddlCulture, ddlInitialProgram, "No"), _
                                                        Tab(txtTitle, ddlSite, "No"), _
                                                        Tab(txtEmailAddress, ddlCulture, "No"), _
                                                        Tab(chkAdmin, txtTitle, "No"), _
                                                        Tab(chkRegTemp, txtEmailAddress, "No"), _
                                                        Tab(chkActive, chkAdmin, "No"), _
                                                        Tab(txtFirstName, chkRegTemp, "No")}
            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
        Private Sub LoadChangePasswordJavaScripts()
            Dim myTabArray() As Object = {txtNewPwd, txtConfNewPwd}
            Dim TabKeyDownArr() As String = {Tab(txtConfNewPwd, txtConfNewPwd, "No"), Tab(txtNewPwd, txtNewPwd, "No")}

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

            Master.HeaderMessage = FormName & " - " & SessionManager.UserMasterMode.Replace("Row", "") & " User"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            Select Case SessionManager.UserMasterMode
                Case "AddRow"
                    Master.IconImage = Request.ApplicationPath + "/images/user1_add.gif"
                Case "ADAdd"
                    Master.IconImage = Request.ApplicationPath + "/images/user1_add.gif"
                Case "DeleteRow"
                    Master.IconImage = Request.ApplicationPath + "/images/user1_delete.gif"
                Case "EditRow", "ADEdit"
                    Master.IconImage = Request.ApplicationPath + "/images/user1_preferences.gif"
                Case "ViewRow"
                    Master.IconImage = Request.ApplicationPath + "/images/user1_information.gif"
            End Select

            LoadCommonJavaScripts()
            dgSecurityGroups.StoredProcedureParams.Add("@UserID", SessionManager.SelectedValueUser)
            mcUserSite.StoredProcedureParams.Add("@UserID", SessionManager.SelectedValueUser)
            mcAreaGroupUsers.StoredProcedureParams.Add("@UserID", SessionManager.SelectedValueUser)
            mcKPINotifications.StoredProcedureParams.Add("@UserID", SessionManager.SelectedValueUser)

            If (New System.Globalization.CultureInfo(SessionManager.CulturePref).TwoLetterISOLanguageName.ToUpper = "EN") Then
                mcKPINotifications.GridColumns(0).DataField = "KPIOther"
                mcKPINotifications.GridColumns(0).SortExpression = "KPIOther"
            End If

            If Not Page.IsPostBack Then
                BindDropDownLists()
                Select Case SessionManager.UserMasterMode
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        LoadAddModeJavaScripts()
                        BindDropDownLists()
                        UnEnableRecords()

                        pnlGrids.Visible = False
                        btnSecurityGroups.Visible = True
                        btnUserSiteMaster.Visible = True
                        btnKPIUserNotification.Visible = True
                        btnAreaUser.Visible = True
                    Case "ADAdd"
                        TransactionHistory1.Visible = False
                        LoadAddModeJavaScripts()
                        BindDropDownLists()
                        UnEnableRecords()
                        txtUserID.Text = SessionManager.ADUserID.ToUpper
                        txtLastName.Text = StrConv(SessionManager.ADLastName, VbStrConv.ProperCase)
                        txtMiddleInitial.Text = SessionManager.ADMiddleInitial.Trim
                        txtFirstName.Text = StrConv(SessionManager.ADFirstName, VbStrConv.ProperCase)

                        Dim strDomain As String = ConfigurationManager.AppSettings("DefaultEmailFromDomain")
                        Dim strADDomain As String = ConfigurationManager.AppSettings("ADDomain")
                        txtEmailAddress.Text = SessionManager.ADEmail.ToLower.Replace(strADDomain & ".net", strDomain)

                        'fill in the site
                        Dim objItem As ListItem
                        objItem = ddlSite.Items.FindByValue(SessionManager.WorkingSiteID)
                        If Not objItem Is Nothing Then
                            objItem.Selected = True
                        End If

                        'initial program
                        objItem = ddlInitialProgram.Items.FindByValue("MainMenu")
                        If Not objItem Is Nothing Then
                            objItem.Selected = True
                        End If

                        'culture
                        objItem = ddlCulture.Items.FindByValue("en-US")
                        If Not objItem Is Nothing Then
                            objItem.Selected = True
                        End If

                        pnlGrids.Visible = False
                        btnSecurityGroups.Visible = True
                        btnUserSiteMaster.Visible = True
                        btnKPIUserNotification.Visible = True
                        btnAreaUser.Visible = True
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        ddlInitialProgram.Items.Add(sInitialProgram)
                        ddlSite.Items.Add(sSite)
                        ddlCulture.Items.Add(strCulture)
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this User.');")
                        TransactionHistory1.LockControl = True
                        UnEnableRecords()
                    Case "EditRow", "ADEdit"
                        LoadEditModeJavaScripts()
                        BindDropDownLists()
                        LoadSelectedRecord()
                        UnEnableRecords()
                        If SessionManager.IsAdministrator = True Then
                            btnF7.Visible = True
                        End If
                        btnSecurityGroups.Visible = True
                        btnUserSiteMaster.Visible = True
                        btnKPIUserNotification.Visible = True
                        btnAreaUser.Visible = True
                    Case "ViewRow"
                        pnlExit.Visible = True
                        BindDropDownLists()
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserMaster1"), False)
                End Select
            Else
                Select Case SessionManager.UserMasterMode
                    Case "AddRow"
                        pnlGrids.Visible = False
                        btnSecurityGroups.Visible = True
                        btnUserSiteMaster.Visible = True
                        btnKPIUserNotification.Visible = True
                        btnAreaUser.Visible = True
                    Case "ADAdd"
                        pnlGrids.Visible = False
                        btnSecurityGroups.Visible = True
                        btnUserSiteMaster.Visible = True
                        btnKPIUserNotification.Visible = True
                        btnAreaUser.Visible = True
                    Case "EditRow", "ADEdit"
                        If SessionManager.IsAdministrator = True Then
                            btnF7.Visible = True
                        End If
                        btnSecurityGroups.Visible = True
                        btnUserSiteMaster.Visible = True
                        btnKPIUserNotification.Visible = True
                        btnAreaUser.Visible = True
                End Select
            End If
        End Sub
        Protected Sub btnOK_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If pnlUser.Visible Then
                Dim blnSuccess As Boolean
                Select Case SessionManager.UserMasterMode.ToString
                    Case "EditRow", "ADEdit"
                        blnSuccess = UpdateUser()
                    Case "DeleteRow"
                        blnSuccess = DeleteUser()
                    Case "AddRow", "ADAdd"
                        blnSuccess = InsertUser()
                End Select

                If blnSuccess Then
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueUser)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.ADUserID)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.ADLastName)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.ADFirstName)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.ADEmail)

                    Select Case SessionManager.UserMasterMode.ToString
                        Case "ADAdd", "ADEdit"
                            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.UserMasterMode)
                            Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserMaster7"), False)
                        Case Else
                            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.UserMasterMode)
                            Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserMaster1"), False)
                    End Select
                End If
            ElseIf pnlChangePassword.Visible Then
                Try
                    Dim strPwd As String = FormsAuthentication.HashPasswordForStoringInConfigFile(txtNewPwd.Text.ToUpper.Trim & txtUserID.Text.ToUpper.Trim, "sha1")
                    UserMaster.AddNewPassword(txtUserID.Text.Trim, strPwd)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueUser)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.ADUserID)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.ADLastName)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.ADFirstName)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.ADEmail)
                    Select Case SessionManager.UserMasterMode.ToString
                        Case "ADAdd", "ADEdit"
                            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.UserMasterMode)
                            Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserMaster7"), False)
                        Case Else
                            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.UserMasterMode)
                            Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserMaster1"), False)
                    End Select
                Catch Exc As Exception
                    Master.DisplayErrors(ProgramName & " - btnChangePassword_Click", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                End Try
            End If
        End Sub
        Protected Sub btnCancel_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnCancel.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If pnlUser.Visible Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueUser)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.ADUserID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.ADLastName)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.ADFirstName)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.ADEmail)

                Select Case SessionManager.UserMasterMode.ToString
                    Case "ADAdd", "ADEdit"
                        SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.UserMasterMode)
                        Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserMaster7"), False)
                    Case Else
                        SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.UserMasterMode)
                        Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserMaster1"), False)
                End Select
            ElseIf pnlChangePassword.Visible Then
                pnlUser.Visible = True
                pnlChangePassword.Visible = False
                btnSecurityGroups.Visible = True
                btnUserSiteMaster.Visible = True
                btnKPIUserNotification.Visible = True
                btnAreaUser.Visible = True

                If SessionManager.IsAdministrator = True Then
                    btnF7.Visible = True
                End If
            End If
        End Sub
        Protected Sub btnF7_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnF7.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            pnlChangePassword.Visible = True
            pnlUser.Visible = False
            btnF7.Visible = False
            btnSecurityGroups.Visible = False
            btnUserSiteMaster.Visible = False
            btnKPIUserNotification.Visible = False
            btnAreaUser.Visible = False

            LoadChangePasswordJavaScripts()
            txtNewPwd.Focus()
        End Sub
        Protected Sub btnSecurityGroups_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnSecurityGroups.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.UserMasterMode = "AddRow" Or SessionManager.UserMasterMode = "ADAdd" Then
                If InsertUser() Then
                    SessionManager.SelectedValueUser = txtUserID.Text.Trim
                    If SessionManager.UserMasterMode = "AddRow" Then
                        SessionManager.UserMasterMode = "EditRow"
                    Else
                        SessionManager.UserMasterMode = "ADEdit"
                    End If

                    SessionManager.MasterControlExitProgram = ProgramName
                    Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserSecurityGroupMaster1"), False)
                End If
            Else
                If UpdateUser() Then
                    SessionManager.MasterControlExitProgram = ProgramName
                    Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserSecurityGroupMaster1"), False)
                End If
            End If
        End Sub
        Protected Sub btnUserSiteMaster_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnUserSiteMaster.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.UserMasterMode = "AddRow" Or SessionManager.UserMasterMode = "ADAdd" Then
                If InsertUser() Then
                    SessionManager.SelectedValueUser = txtUserID.Text.Trim
                    If SessionManager.UserMasterMode = "AddRow" Then
                    Else
                        SessionManager.UserMasterMode = "ADEdit"
                    End If
                    SessionManager.MasterControlExitProgram = ProgramName
                    Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserSiteMaster1"), False)
                End If
            Else
                If UpdateUser() Then
                    SessionManager.MasterControlExitProgram = ProgramName
                    Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserSiteMaster1"), False)
                End If
            End If
        End Sub
        Protected Sub btnAreaUser_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnAreaUser.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.UserMasterMode = "AddRow" Or SessionManager.UserMasterMode = "ADAdd" Then
                If InsertUser() Then
                    SessionManager.SelectedValueUser = txtUserID.Text.Trim.ToUpper
                    SessionManager.UserMasterMode = "EditRow"

                    SessionManager.MasterControlExitProgram = ProgramName
                    Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AreaGroupUserMaster1"), False)
                End If
            Else
                If UpdateUser() Then
                    SessionManager.MasterControlExitProgram = ProgramName
                    Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AreaGroupUserMaster1"), False)
                End If
            End If
        End Sub
        Protected Sub btnKPIUserNotification_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnKPIUserNotification.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.UserMasterMode = "AddRow" Or SessionManager.UserMasterMode = "ADAdd" Then
                If InsertUser() Then
                    SessionManager.SelectedValueUser = txtUserID.Text.Trim.ToUpper
                    SessionManager.UserMasterMode = "EditRow"

                    SessionManager.MasterControlExitProgram = ProgramName
                    Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPIUserNotifications1"), False)
                End If
            Else
                If UpdateUser() Then
                    SessionManager.MasterControlExitProgram = ProgramName
                    Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPIUserNotifications1"), False)
                End If
            End If
        End Sub
        Protected Sub btnExit_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnExit.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueUser)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.ADUserID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.ADLastName)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.ADFirstName)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.ADEmail)

            Select Case SessionManager.UserMasterMode.ToString
                Case "ADAdd", "ADEdit"
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.UserMasterMode)
                    Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserMaster7"), False)
                Case Else
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.UserMasterMode)
                    Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserMaster1"), False)
            End Select
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub BindDropDownLists()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            BindInitialProg()
            BindSite()
            BindCulture()
        End Sub
        Private Sub BindInitialProg()
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
                ddlInitialProgram.Items.Clear()
                ProgramMaster.GetInitialProgramList(ddlInitialProgram)
                ddlInitialProgram.Items.Insert(0, " ")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindInitialProg", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindSite()
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
                ddlSite.Items.Clear()
                SiteMaster.SelectSiteMasterActiveList(ddlSite)
                ddlSite.Items.Insert(0, " ")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindSite", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
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
                Dim ds As DataTable = UserMaster.SelectUserMaster(SessionManager.SelectedValueUser)
                If SessionManager.RecordTransactionCurrentValues IsNot Nothing Then
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RecordTransactionCurrentValues)
                End If
                TransactionHistory1.TableName = DBTableName
                TransactionHistory1.RecordID = SessionManager.SelectedValueUser

                If ds.Rows.Count <> 0 Then
                    Dim objItem As ListItem
                    Dim dr As DataRow = ds.Rows(0)
                    txtUserID.Text = dr.Item("UserID").ToString.Trim()
                    txtFirstName.Text = dr.Item("FirstName").ToString.Trim()
                    txtLastName.Text = dr.Item("LastName").ToString.Trim()
                    txtMiddleInitial.Text = dr.Item("MiddleInitial").ToString
                    txtSuffix.Text = dr.Item("Suffix").ToString
                    txtDepartmentNumber.Text = dr.Item("DeptNumber").ToString
                    txtTitle.Text = dr.Item("Title").ToString
                    txtEmailAddress.Text = dr.Item("EmailAddress").ToString
                    chkAdmin.Checked = dr.Item("IsAdministrator")
                    chkRegTemp.Checked = (dr.Item("RegTemp").ToString = "TMP")
                    chkActive.Checked = CType(dr("Active"), Boolean)
                    ckAllTeamView.Checked = CType(dr("AllTeamView"), Boolean)
                    ckAllTeamEdit.Checked = CType(dr("AllTeamEdit"), Boolean)
                    ckAllKPIView.Checked = CType(dr("AllKPIView"), Boolean)
                    ckAllKPIEdit.Checked = CType(dr("AllKPIEdit"), Boolean)
                    objItem = ddlInitialProgram.Items.FindByValue(dr.Item("InitialProgram").ToString.Trim())
                    If Not objItem Is Nothing Then
                        objItem.Selected = True
                        txtInitialProgram.Text = objItem.Text
                    End If

                    objItem = ddlSite.Items.FindByText(dr("Site").ToString.Trim())
                    If Not objItem Is Nothing Then
                        objItem.Selected = True
                        txtSite.Text = objItem.Text
                    ElseIf IsNumeric(dr("SiteID").ToString) Then
                        Dim dtSite As DataTable = SiteMaster.GetSiteMasterBySite(dr("SiteID").ToString)
                        If dtSite IsNot Nothing AndAlso dtSite.Rows.Count = 1 Then
                            objItem = New ListItem(dtSite.Rows(0)("Site").ToString, dtSite.Rows(0)("SiteID").ToString)
                            ddlSite.Items.Add(objItem)
                            objItem.Selected = True
                            txtSite.Text = objItem.Text
                        End If
                    End If

                    objItem = ddlCulture.Items.FindByText(dr.Item("CultureCode").ToString.Trim())
                    If Not objItem Is Nothing Then
                        objItem.Selected = True
                        txtCulture.Text = objItem.Text
                    End If

                    Dim objDic As New Dictionary(Of String, String)
                    objDic.Add("FirstName", txtFirstName.Text.Trim())
                    objDic.Add("LastName", txtLastName.Text.Trim())
                    objDic.Add("MiddleInitial", txtMiddleInitial.Text.Trim())
                    objDic.Add("Suffix", txtSuffix.Text.Trim())
                    objDic.Add("DeptNumber", txtDepartmentNumber.Text.Trim())
                    objDic.Add("InitialProgram", ddlInitialProgram.SelectedItem.Value.Trim())
                    objDic.Add("Site", ddlSite.SelectedItem.Text.Trim())
                    objDic.Add("Culture", ddlCulture.SelectedItem.Text.Trim())
                    objDic.Add("Title", txtTitle.Text.Trim())
                    objDic.Add("EmailAddress", txtEmailAddress.Text.Trim())
                    objDic.Add("IsAdministrator", chkAdmin.Checked)
                    objDic.Add("RegTemp", chkRegTemp.Checked)
                    objDic.Add("Active", chkActive.Checked)
                    objDic.Add("AllTeamView", ckAllTeamView.Checked.ToString)
                    objDic.Add("AllTeamEdit", ckAllTeamEdit.Checked.ToString)
                    objDic.Add("AllKPIView", ckAllKPIView.Checked.ToString)
                    objDic.Add("AllKPIEdit", ckAllKPIEdit.Checked.ToString)

                    SessionManager.RecordTransactionCurrentValues = objDic
                End If

                dgSecurityGroups.DataBind()
                mcUserSite.DataBind()
                mcAreaGroupUsers.DataBind()
                mcKPINotifications.DataBind()
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

            Select Case SessionManager.UserMasterMode.ToString
                Case "ViewRow", "DeleteRow"
                    If SessionManager.UserMasterMode = "ViewRow" Then
                        pnlOKCancel.Visible = False
                    End If
                    txtUserID.ReadOnly = True
                    lblPassword.Visible = False
                    txtPwd.Visible = False
                    txtFirstName.ReadOnly = True
                    txtLastName.ReadOnly = True
                    txtMiddleInitial.ReadOnly = True
                    txtSuffix.ReadOnly = True
                    txtDepartmentNumber.ReadOnly = True
                    txtTitle.ReadOnly = True
                    txtEmailAddress.ReadOnly = True
                    chkAdmin.Enabled = False
                    chkRegTemp.Enabled = False
                    chkActive.Enabled = False
                    ckAllTeamView.Enabled = False
                    ckAllTeamEdit.Enabled = False
                    ckAllKPIView.Enabled = False
                    ckAllKPIEdit.Enabled = False
                    txtUserID.CssClass = "Textbox_Display"
                    txtFirstName.CssClass = "Textbox_Display"
                    txtLastName.CssClass = "Textbox_Display"
                    txtMiddleInitial.CssClass = "Textbox_Display"
                    txtSuffix.CssClass = "Textbox_Display"
                    txtDepartmentNumber.CssClass = "Textbox_Display"
                    txtTitle.CssClass = "Textbox_Display"
                    txtEmailAddress.CssClass = "Textbox_Display"
                    txtInitialProgram.Visible = True
                    ddlInitialProgram.Visible = False
                    txtSite.Visible = True
                    ddlSite.Visible = False
                    txtCulture.Visible = True
                    ddlCulture.Visible = False
                Case "EditRow", "ADEdit"
                    If SessionManager.IsAdministrator = False Then
                        chkAdmin.Enabled = False
                        ckAllTeamView.Enabled = False
                        ckAllTeamEdit.Enabled = False
                        ckAllKPIView.Enabled = False
                        ckAllKPIEdit.Enabled = False
                    End If
                    txtUserID.ReadOnly = True
                    txtUserID.CssClass = "Textbox_Display"
                    txtPwd.Visible = False
                    lblPassword.Visible = False
                    txtFirstName.Focus()
                Case "AddRow"
                    lblPassword.Visible = True
                    txtPwd.Visible = True
                    If SessionManager.IsAdministrator = False Then
                        chkAdmin.Enabled = False
                    End If
                    txtUserID.Focus()
            End Select
        End Sub
        Private Function InsertUser() As Boolean
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
                If ckAllTeamEdit.Checked Then ckAllTeamView.Checked = True
                If ckAllKPIEdit.Checked Then ckAllKPIView.Checked = True

                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If
                Dim strPwd As String = FormsAuthentication.HashPasswordForStoringInConfigFile(txtPwd.Text.ToUpper.Trim & txtUserID.Text.ToUpper.Trim, "sha1")
                UserMaster.AddUserMaster(txtUserID.Text.Trim.ToUpper, ddlSite.SelectedItem.Value, strPwd, ddlInitialProgram.SelectedItem.Value, chkAdmin.Checked, txtLastName.Text.Trim(), txtFirstName.Text.Trim(), txtMiddleInitial.Text.Trim(), txtSuffix.Text.Trim(), txtTitle.Text.Trim(), txtDepartmentNumber.Text.Trim(), chkActive.Checked, txtEmailAddress.Text.Trim(), chkRegTemp.Checked, ddlCulture.SelectedValue.Trim(), False)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, txtUserID.Text.ToUpper.Trim(), strChangeLog, SessionManager.UserID)
                If ckAllTeamView.Checked OrElse ckAllTeamEdit.Checked OrElse ckAllKPIView.Checked OrElse ckAllKPIEdit.Checked Then
                    UserMasterAttributes.AddUserMasterAttributes(txtUserID.Text.ToUpper.Trim(), ckAllTeamView.Checked, ckAllTeamEdit.Checked, ckAllKPIView.Checked, ckAllKPIEdit.Checked)
                End If

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertUser", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateUser() As Boolean
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
                If ckAllTeamEdit.Checked Then ckAllTeamView.Checked = True
                If ckAllKPIEdit.Checked Then ckAllKPIView.Checked = True

                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.CompareDictionaryValues(SessionManager.RecordTransactionCurrentValues, objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If
                UserMaster.UpdateUserMaster(SessionManager.SelectedValueUser, CInt(ddlSite.SelectedItem.Value), ddlInitialProgram.SelectedItem.Value, chkAdmin.Checked, txtLastName.Text.Trim(), txtFirstName.Text.Trim(), txtMiddleInitial.Text.Trim(), txtSuffix.Text.Trim(), txtTitle.Text.Trim(), txtDepartmentNumber.Text.Trim(), chkActive.Checked, txtEmailAddress.Text.Trim(), chkRegTemp.Checked, ddlCulture.SelectedValue.Trim())
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueUser, strChangeLog, SessionManager.UserID)

                UserMasterAttributes.UpdateUserMasterAttributes(SessionManager.SelectedValueUser, ckAllTeamView.Checked, ckAllTeamEdit.Checked, ckAllKPIView.Checked, ckAllKPIEdit.Checked)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateUser", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function DeleteUser() As Boolean
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
                UserMaster.DeleteUserMaster(SessionManager.SelectedValueUser)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueUser, "User Deleted", SessionManager.UserID)
                UserMasterAttributes.DeleteUserMasterAttributes(SessionManager.SelectedValueUser)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteUser", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
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
            objDic.Add("FirstName", txtFirstName.Text.Trim())
            objDic.Add("LastName", txtLastName.Text.Trim())
            objDic.Add("MiddleInitial", txtMiddleInitial.Text.Trim())
            objDic.Add("Suffix", txtSuffix.Text.Trim())
            objDic.Add("DeptNumber", txtDepartmentNumber.Text.Trim())
            objDic.Add("InitialProgram", ddlInitialProgram.SelectedItem.Value.Trim())
            objDic.Add("Site", ddlSite.SelectedItem.Text.Trim())
            objDic.Add("Culture", ddlCulture.SelectedItem.Text.Trim())
            objDic.Add("Title", txtTitle.Text.Trim())
            objDic.Add("EmailAddress", txtEmailAddress.Text.Trim())
            objDic.Add("IsAdministrator", chkAdmin.Checked)
            objDic.Add("RegTemp", chkRegTemp.Checked)
            objDic.Add("Active", chkActive.Checked)
            objDic.Add("AllTeamView", ckAllTeamView.Checked.ToString)
            objDic.Add("AllTeamEdit", ckAllTeamEdit.Checked.ToString)
            objDic.Add("AllKPIView", ckAllKPIView.Checked.ToString)
            objDic.Add("AllKPIEdit", ckAllKPIEdit.Checked.ToString)

            Return objDic
        End Function
#End Region

    End Class
End Namespace
