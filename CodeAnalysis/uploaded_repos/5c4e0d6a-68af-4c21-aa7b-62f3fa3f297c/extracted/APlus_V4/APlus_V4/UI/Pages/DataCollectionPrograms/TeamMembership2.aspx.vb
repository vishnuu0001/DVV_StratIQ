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
    Partial Class TeamMembership2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Team Membership"
        Private Shared ReadOnly ProgramName As String = "TeamMembership2"
        Private Shared ReadOnly DBTableName As String = "TeamMembership"
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel, btnExit}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel", "Exit"}
            Dim OutMessageArr() As String = {"", "", ""}
            Dim strDateFormat As String = SessionManager.DateFormat

            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)
            txtDateJoined_CalendarExtender.Format = strDateFormat

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnExit.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
        End Sub
        Private Sub LoadAddModeJavaScripts()
            If ddlTeam.Visible Then
                Dim myTabArray() As Object = {ddlTeam, _
                                              ddlUserID, _
                                              ddlRole, _
                                              ddlSecondaryRole, _
                                              txtDateJoined}

                Dim TabKeyDownArr() As String = {Tab(ddlUserID, txtDateJoined, "No"), _
                                                 Tab(ddlRole, ddlTeam, "No"), _
                                                 Tab(ddlSecondaryRole, ddlUserID, "No"), _
                                                 Tab(txtDateJoined, ddlRole, "No"), _
                                                 Tab(ddlTeam, ddlSecondaryRole, "No")}

                AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
            Else
                Dim myTabArray() As Object = {ddlUserID, _
                                              ddlRole, _
                                              ddlSecondaryRole, _
                                              txtDateJoined}

                Dim TabKeyDownArr() As String = {Tab(ddlRole, txtDateJoined, "No"), _
                                                 Tab(ddlSecondaryRole, ddlUserID, "No"), _
                                                 Tab(txtDateJoined, ddlRole, "No"), _
                                                 Tab(ddlUserID, ddlSecondaryRole, "No")}

                AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
            End If
        End Sub
        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {txtTitle, _
                                         ddlRole, _
                                         ddlSecondaryRole, _
                                         txtDateJoined}

            Dim TabKeyDownArr() As String = {Tab(ddlRole, txtDateJoined, "No"), _
                                             Tab(ddlSecondaryRole, txtTitle, "No"), _
                                             Tab(txtDateJoined, ddlRole, "No"), _
                                             Tab(txtTitle, ddlSecondaryRole, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
#End Region

#Region " Load Culture Translations"
        Private Sub LoadCultureTranslations()
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
                lblTeam.Text = GetTranslationString("team", lblTeam.Text.Replace(":", "")) & ":"
                lblUserID.Text = GetTranslationString("user id", lblUserID.Text.Replace(":", "")) & ":"
                lblTitle.Text = GetTranslationString("title", lblTitle.Text.Replace(":", "")) & ":"
                lblRole.Text = GetTranslationString("role", lblRole.Text.Replace(":", "")) & ":"
                lblSecondaryRole.Text = GetTranslationString("secondaryrole", lblSecondaryRole.Text.Replace(":", "")) & ":"
                lblDateJoined.Text = GetTranslationString("date joined", lblDateJoined.Text.Replace(":", "")) & ":"
                btnOK.Text = GetTranslationString("ok", btnOK.Text)
                btnCancel.Text = GetTranslationString("cancel", btnCancel.Text)
                btnExit.Text = GetTranslationString("exit", btnExit.Text)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadCultureTranslations", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
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

            If Not Page.IsPostBack Then
                LoadCultureTranslations()
            End If

            Master.HeaderMessage = GetTranslationString(FormName, FormName) & " - " & GetTranslationString(SessionManager.TeamMembershipMode.Replace("Row", ""), SessionManager.TeamMembershipMode.Replace("Row", ""))
            Master.IconImage = Request.ApplicationPath + "/images/TeamMembership.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                BindSites()

                Select Case SessionManager.TeamMembershipMode.ToString()
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadDropDownLists()
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "DeleteRow"
                        LoadDropDownLists()
                        LoadSelectedRecord()
                        UnEnableRecords()
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Member from Team.');")
                        TransactionHistory1.LockControl = True
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        If SessionManager.SelectedValueTeamID > 0 Then
                            Try
                                Dim dtHolder As DateTime = Teams.GetTeamStartDate(SessionManager.SelectedValueTeamID)
                                If Not IsNothing(dtHolder) Then
                                    txtDateJoined.Text = dtHolder.ToString(SessionManager.DateFormat)
                                Else
                                    txtDateJoined.Text = DateTime.Now.ToString(SessionManager.DateFormat)
                                End If
                            Catch Exc As Exception
                                Master.DisplayErrors(ProgramName & " - Page_Load ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                            End Try
                        Else
                            txtDateJoined.Text = DateTime.Now.ToString(SessionManager.DateFormat)
                        End If
                        UnEnableRecords()
                        LoadDropDownLists()
                        LoadAddModeJavaScripts()
                        If ddlTeam.Visible Then
                            ddlTeam.Focus()
                        Else
                            ddlUserID.Focus()
                        End If
                    Case "EditRow"
                        UnEnableRecords()
                        LoadDropDownLists()
                        LoadSelectedRecord()
                        LoadEditModeJavaScripts()
                        txtTitle.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamMembershipMaintenance"), False)
                End Select
            End If
        End Sub
        Protected Sub ddlSite_SelectedIndexChanged(ByVal sender As Object, ByVal e As System.EventArgs) Handles ddlSite.SelectedIndexChanged
            BindUserID()
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

            If SessionManager.TeamMembershipMode = "DeleteRow" Then
                blnSuccess = DeleteTeamMembership()
            ElseIf SessionManager.TeamMembershipMode = "AddRow" Then
                blnSuccess = InsertTeamMembership()
            ElseIf SessionManager.TeamMembershipMode = "EditRow" Then
                blnSuccess = UpdateTeamMembership()
            End If

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue2)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue3)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamMembershipMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamMembershipMasterMaintenance"), False)
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

            If SessionManager.TeamMembershipMode = "EditRow" Or SessionManager.TeamMembershipMode = "ViewRow" Or SessionManager.TeamMembershipMode = "DeleteRow" Or SessionManager.TeamMembershipMode = "AddRow" Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue2)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue3)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamMembershipMode)
            End If
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamMembershipMasterMaintenance"), False)
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue2)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue3)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamMembershipMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamMembershipMasterMaintenance"), False)
        End Sub
        Private Sub ddlTeam_SelectedIndexChanged(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles ddlTeam.SelectedIndexChanged
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim ds As DataTable = Teams.SelectTeams(ddlTeam.SelectedValue)
                If ds.Rows.Count > 0 Then
                    If IsDate(ds.Rows(0).Item("TeamStartDate")) Then
                        Dim dtHolder As DateTime = ds.Rows(0).Item("TeamStartDate")
                        txtDateJoined.Text = dtHolder.ToString(SessionManager.DateFormat)
                    End If
                End If
                ddlTeam.Focus()
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - ddlTeam_SelectedIndexChanged", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub BindSites()
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
                Dim objItem As ListItem = Nothing

                SiteMaster.SelectSiteMasterActiveList(ddlSite)
                If SessionManager.WorkingSiteID > 0 Then
                    objItem = ddlSite.Items.FindByValue(SessionManager.WorkingSiteID)
                Else
                    objItem = ddlSite.Items.FindByValue(UserMaster.GetUserSite(SessionManager.UserID))
                End If
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                Else
                    If ddlSite.Items.Count > 0 Then
                        ddlSite.Items(0).Selected = True
                    End If
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindSites", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
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
                Dim dt As DataTable = TeamMembership.SelectTeamMembershipByKey(SessionManager.SelectedValue1, SessionManager.SelectedValue)
                If dt.Rows.Count > 0 Then
                    Dim dr As DataRow = dt.Rows(0)
                    Dim objItem As ListItem

                    objItem = ddlTeam.Items.FindByValue(SessionManager.SelectedValue)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                        txtTeam.Text = objItem.Text
                    End If

                    objItem = ddlUserID.Items.FindByValue(SessionManager.SelectedValue1)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                        txtUserID.Text = objItem.Text
                    Else
                        objItem = New ListItem(UserMaster.GetUserFullName(SessionManager.SelectedValue1) & " (" & SessionManager.SelectedValue1 & ")", SessionManager.SelectedValue1)
                        ddlUserID.Items.Insert(1, objItem)
                        objItem.Selected = True
                        txtUserID.Text = objItem.Text
                    End If

                    txtTitle.Text = dr("Title").ToString

                    If dr.Item("Role") IsNot DBNull.Value Then
                        objItem = ddlRole.Items.FindByText(dr.Item("Role"))
                        If objItem IsNot Nothing Then
                            objItem.Selected = True
                            txtRole.Text = objItem.Text
                        End If
                    End If

                    If dr.Item("SecondaryRole") IsNot DBNull.Value Then
                        objItem = ddlSecondaryRole.Items.FindByText(dr.Item("SecondaryRole"))
                        If objItem IsNot Nothing Then
                            objItem.Selected = True
                            txtSecondaryRole.Text = objItem.Text
                        End If
                    End If

                    If IsDate(dr("DateJoined")) Then
                        txtDateJoined.Text = Convert.ToDateTime("" + dr("DateJoined")).ToShortDateString
                    Else
                        txtDateJoined.Text = String.Empty
                    End If

                    TransactionHistory1.TableName = DBTableName
                    TransactionHistory1.RecordID = SessionManager.SelectedValue & "," & SessionManager.SelectedValue1

                    Dim objDic As New Dictionary(Of String, String)
                    objDic.Add("Title", txtTitle.Text.Trim())
                    objDic.Add("Role", ddlRole.SelectedItem.Text.Trim())
                    objDic.Add("SecondaryRole", ddlSecondaryRole.SelectedItem.Text.Trim())
                    objDic.Add("DateJoined", txtDateJoined.Text.Trim())
                    SessionManager.RecordTransactionCurrentValues = objDic
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub LoadDropDownLists()
            Try
                BindTeams()
                BindUserID()
                BindRole()
                BindSecondaryRole()
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadDropDownLists", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindTeams()
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
                If SessionManager.SelectedValueTeamID > 0 Then
                    If (New System.Globalization.CultureInfo(SessionManager.CulturePref).TwoLetterISOLanguageName.ToUpper = "EN") Then
                        ddlTeam.Items.Add(New ListItem(Teams.GetTeamNameOther(SessionManager.SelectedValueTeamID), SessionManager.SelectedValueTeamID))
                    Else
                        ddlTeam.Items.Add(New ListItem(Teams.GetTeamName(SessionManager.SelectedValueTeamID), SessionManager.SelectedValueTeamID))
                    End If

                    ddlTeam.SelectedValue = SessionManager.SelectedValueTeamID
                    txtTeam.Text = ddlTeam.SelectedItem.Text
                    txtTeam.Visible = True
                    ddlTeam.Visible = False
                Else
                    If SessionManager.SelectedTeamID = 0 Then
                        Teams.SelectTeamList(SessionManager.WorkingSiteID, ddlTeam)
                        ddlTeam.Items.Insert(0, "")
                    Else
                        If (New System.Globalization.CultureInfo(SessionManager.CulturePref).TwoLetterISOLanguageName.ToUpper = "EN") Then
                            ddlTeam.Items.Add(New ListItem(Teams.GetTeamNameOther(SessionManager.SelectedTeamID), SessionManager.SelectedTeamID))
                        Else
                            ddlTeam.Items.Add(New ListItem(Teams.GetTeamName(SessionManager.SelectedTeamID), SessionManager.SelectedTeamID))
                        End If

                        ddlTeam.SelectedValue = SessionManager.SelectedTeamID
                        txtTeam.Text = ddlTeam.SelectedItem.Text
                        txtTeam.Visible = True
                        ddlTeam.Visible = False
                    End If
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindTeams", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindSecondaryRole()
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
                RoleMaster.SelectTeamRoleList(ddlSecondaryRole)
                ddlSecondaryRole.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindSecondaryRole", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindRole()
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
                RoleMaster.SelectTeamRoleList(ddlRole)
                ddlRole.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindRole", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindUserID()
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
                ddlUserID.Items.Clear()

                If ddlSite.SelectedItem IsNot Nothing Then
                    UserMaster.SelectUserNameList(ddlSite.SelectedItem.Value, True, ddlUserID)
                Else
                    UserMaster.SelectUserNameList(SessionManager.WorkingSiteID, True, ddlUserID)
                End If

                ddlUserID.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindRole", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
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

            Select Case SessionManager.TeamMembershipMode.ToString()
                Case "ViewRow"
                    pnlOKCancel.Visible = False
                    ddlUserID.Visible = False
                    ddlTeam.Visible = False
                    ddlRole.Visible = False
                    ddlSecondaryRole.Visible = False
                    txtTitle.ReadOnly = True
                    txtTitle.CssClass = "Textbox_Display"
                    txtDateJoined.ReadOnly = True
                    txtDateJoined.CssClass = "Textbox_Display"
                    imgDateJoined.Visible = False
                    txtDateJoined_CalendarExtender.Enabled = False
                    txtTitle.Visible = True
                    rowTitle.Visible = True
                    ddlSite.Visible = False
                Case "DeleteRow"
                    ddlTeam.Visible = False
                    ddlUserID.Visible = False
                    txtTitle.Visible = False
                    ddlRole.Visible = False
                    ddlSecondaryRole.Visible = False
                    txtTitle.ReadOnly = True
                    txtTitle.CssClass = "Textbox_Display"
                    txtDateJoined.ReadOnly = True
                    txtDateJoined.CssClass = "Textbox_Display"
                    imgDateJoined.Visible = False
                    txtDateJoined_CalendarExtender.Enabled = False
                    txtTitle.Visible = True
                    rowTitle.Visible = True
                    ddlSite.Visible = False
                Case "EditRow"
                    txtUserID.Visible = True
                    ddlUserID.Visible = False
                    txtTeam.Visible = True
                    ddlTeam.Visible = False
                    txtRole.Visible = False
                    txtSecondaryRole.Visible = False
                    imgDateJoined.Visible = True
                    txtTitle.Focus()
                    txtTitle.Visible = True
                    rowTitle.Visible = True
                    ddlSite.Visible = False
                Case "AddRow"
                    txtTeam.Visible = False
                    txtUserID.Visible = False
                    txtRole.Visible = False
                    txtSecondaryRole.Visible = False
                    imgDateJoined.Visible = True
                    rowTitle.Visible = False
            End Select
        End Sub
        Private Function InsertTeamMembership() As Boolean
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
                If Not String.IsNullOrEmpty(txtDateJoined.Text.Trim()) Then
                    If Not IsDate(txtDateJoined.Text) Then
                        Master.DisplayError("Invalid Date")
                        txtDateJoined.Focus()
                        Exit Function
                    End If
                End If

                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                Dim strDateJoined As String = RegionalConversion.FormatSQLDate(txtDateJoined.Text)
                TeamMembership.AddTeamMembership(ddlTeam.SelectedValue, ddlUserID.SelectedValue, ddlRole.SelectedValue, ddlSecondaryRole.SelectedValue, strDateJoined, SessionManager.UserID)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, ddlTeam.SelectedItem.Value & "," & ddlUserID.SelectedItem.Value, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - Insert Team Member ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateTeamMembership() As Boolean
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
                If Not String.IsNullOrEmpty(txtDateJoined.Text.Trim()) Then
                    If Not IsDate(txtDateJoined.Text) Then
                        Master.DisplayError("Invalid Date")
                        txtDateJoined.Focus()
                        Exit Function
                    End If
                End If

                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.CompareDictionaryValues(SessionManager.RecordTransactionCurrentValues, objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                Dim strDateJoined As String = RegionalConversion.FormatSQLDate(txtDateJoined.Text)
                TeamMembership.UpdateTeamMembership(SessionManager.SelectedValue, SessionManager.SelectedValue1, txtTitle.Text, ddlRole.SelectedValue, ddlSecondaryRole.SelectedValue, strDateJoined, SessionManager.UserID)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValue & "," & SessionManager.SelectedValue1, strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateTeamMembership ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function DeleteTeamMembership() As Boolean
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
                TeamMembership.DeleteTeamMembership(SessionManager.SelectedValue, SessionManager.SelectedValue1)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValue & "," & SessionManager.SelectedValue1, "Team Membership Deleted", SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteTeamMembership ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
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
            objDic.Add("Title", txtTitle.Text.Trim())
            objDic.Add("Role", ddlRole.SelectedItem.Text.Trim())
            objDic.Add("SecondaryRole", ddlSecondaryRole.SelectedItem.Text.Trim())
            objDic.Add("DateJoined", RegionalConversion.FormatSQLDate(txtDateJoined.Text))
            Return objDic
        End Function
#End Region

    End Class
End Namespace