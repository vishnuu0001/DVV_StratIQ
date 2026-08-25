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
    Partial Class TeamActionPlan2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Team Action Plan"
        Private Shared ReadOnly ProgramName As String = "TeamActionPlan2"
        Private Shared ReadOnly DBTableName As String = "TeamActionPlan"
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel, btnExit}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel", "Exit"}
            Dim OutMessageArr() As String = {"", "", ""}
            Dim strDateFormat As String = SessionManager.DateFormat

            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)

            txtTargetDate_CalendarExtender.Format = strDateFormat
            txtClosedDate_CalendarExtender.Format = strDateFormat

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnExit.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
        End Sub
        Private Sub LoadAddModeJavaScripts()
            Select Case SessionManager.TeamActionPlanMode
                Case "AddMeeting"
                    Dim myTabArray() As Object = {ddlStepNo, _
                                                  txtActionItem, _
                                                  txtExpandActionItemDefinition, _
                                                  ddlAssignedTo, _
                                                  txtAssignedToOther, _
                                                  txtTargetDate, _
                                                  txtExpandActions, _
                                                  txtClosedDate}

                    Dim TabKeyDownArr() As String = {Tab(txtActionItem, txtClosedDate, "No"), _
                                                     Tab(txtExpandActionItemDefinition, ddlStepNo, "No"), _
                                                     Tab(ddlAssignedTo, txtActionItem, "No"), _
                                                     Tab(txtAssignedToOther, txtExpandActionItemDefinition, "No"), _
                                                     Tab(txtTargetDate, ddlAssignedTo, "No"), _
                                                     Tab(txtExpandActions, txtAssignedToOther, "No"), _
                                                     Tab(txtClosedDate, txtTargetDate, "No"), _
                                                     Tab(ddlStepNo, txtExpandActions, "No")}

                    AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
                Case "AddRow"
                    Dim myTabArray() As Object = {ddlMeetings, _
                                                  ddlStepNo, _
                                                  txtActionItem, _
                                                  txtExpandActionItemDefinition, _
                                                  ddlAssignedTo, _
                                                  txtAssignedToOther, _
                                                  txtTargetDate, _
                                                  txtExpandActions, _
                                                  txtClosedDate}

                    Dim TabKeyDownArr() As String = {Tab(ddlStepNo, txtClosedDate, "No"), _
                                                     Tab(txtActionItem, ddlMeetings, "No"), _
                                                     Tab(txtExpandActionItemDefinition, ddlStepNo, "No"), _
                                                     Tab(ddlAssignedTo, txtActionItem, "No"), _
                                                     Tab(txtAssignedToOther, txtExpandActionItemDefinition, "No"), _
                                                     Tab(txtTargetDate, ddlAssignedTo, "No"), _
                                                     Tab(txtExpandActions, txtAssignedToOther, "No"), _
                                                     Tab(txtClosedDate, txtTargetDate, "No"), _
                                                     Tab(ddlMeetings, txtExpandActions, "No")}

                    AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
            End Select
        End Sub
        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {ddlStepNo, _
                                          txtActionItem, _
                                          txtExpandActionItemDefinition, _
                                          ddlAssignedTo, _
                                          txtAssignedToOther, _
                                          txtTargetDate, _
                                          txtExpandActions, _
                                          txtClosedDate _
                                         }

            Dim TabKeyDownArr() As String = {Tab(txtActionItem, txtClosedDate, "No"), _
                                             Tab(txtExpandActionItemDefinition, ddlStepNo, "No"), _
                                             Tab(ddlAssignedTo, txtActionItem, "No"), _
                                             Tab(txtAssignedToOther, txtExpandActionItemDefinition, "No"), _
                                             Tab(txtTargetDate, ddlAssignedTo, "No"), _
                                             Tab(txtExpandActions, txtAssignedToOther, "No"), _
                                             Tab(txtClosedDate, txtTargetDate, "No"), _
                                             Tab(ddlStepNo, txtExpandActions, "No")}

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
                lblActionNumber.Text = GetTranslationString("actionnumber", lblActionNumber.Text.Replace(":", "")) & ":"
                lblMeeting.Text = GetTranslationString("meeting", lblMeeting.Text.Replace(":", "")) & ":"
                lblStepNo.Text = GetTranslationString("stepnumber", lblStepNo.Text.Replace(":", "")) & ":"
                lblActionItem.Text = GetTranslationString("action item", lblActionItem.Text.Replace(":", "")) & ":"
                lblActionItemDefinition.Text = GetTranslationString("actionitemdefinition", lblActionItemDefinition.Text.Replace(":", "")) & ":"
                lblAssignedTo.Text = GetTranslationString("assignedto", lblAssignedTo.Text.Replace(":", "")) & ":"
                lblAssignedToOther.Text = GetTranslationString("assignedtoother", lblAssignedToOther.Text.Replace(":", "")) & ":"
                lblTargetDate.Text = GetTranslationString("target date", lblTargetDate.Text.Replace(":", "")) & ":"
                lblClosedDate.Text = GetTranslationString("closed date", lblClosedDate.Text.Replace(":", "")) & ":"
                lblActions.Text = GetTranslationString("actions", lblActions.Text.Replace(":", "")) & ":"
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

            Master.HeaderMessage = GetTranslationString(FormName, FormName) & " - " & GetTranslationString(SessionManager.TeamActionPlanMode.Replace("Row", ""), SessionManager.TeamActionPlanMode.Replace("Row", ""))
            Master.IconImage = Request.ApplicationPath + "/images/TeamAction.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                Select Case SessionManager.TeamActionPlanMode
                    Case "ViewRow", "MyViewRow"
                        pnlExit.Visible = True
                        BindDropdownList()
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "DeleteRow"
                        BindDropdownList()
                        LoadSelectedRecord()
                        UnEnableRecords()
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Team Action Plan.');")
                        TransactionHistory1.LockControl = True
                    Case "AddMeeting"
                        TransactionHistory1.Visible = False
                        Master.HeaderMessage = FormName & " - Add Meeting Team Meeting Action"
                        LoadAddModeJavaScripts()
                        lblActionNumber.Visible = False
                        txtActionNumber.Visible = False
                        BindDropdownList()
                        Dim objItem As ListItem = ddlMeetings.Items.FindByValue(SessionManager.TeamMeetingID)
                        If objItem IsNot Nothing Then
                            objItem.Selected = True
                            txtTeamMeeting.Text = objItem.Text
                            txtTeamMeeting.Visible = True
                            ddlMeetings.Visible = False
                        End If
                        UnEnableRecords()
                        ddlStepNo.Focus()
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        LoadAddModeJavaScripts()
                        lblActionNumber.Visible = False
                        txtActionNumber.Visible = False
                        BindDropdownList()
                        UnEnableRecords()
                        ddlMeetings.Focus()
                    Case "EditRow", "MyEditRow"
                        LoadEditModeJavaScripts()
                        BindDropdownList()
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case Else
                        RedirectToPriorProgram()
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

            Dim blnSuccess As Boolean = False

            If SessionManager.TeamActionPlanMode = "DeleteRow" Then
                blnSuccess = DeleteTeamActionPlan()
            ElseIf SessionManager.TeamActionPlanMode = "AddRow" OrElse SessionManager.TeamActionPlanMode = "AddMeeting" Then
                If Not String.IsNullOrEmpty(txtClosedDate.Text.Trim()) Then
                    If Not IsDate(txtClosedDate.Text) Then
                        Master.DisplayError("Invalid Closed Date")
                        txtClosedDate.Focus()
                        Return
                    End If
                End If
                blnSuccess = InsertTeamActionPlan()
            ElseIf SessionManager.TeamActionPlanMode = "EditRow" OrElse SessionManager.TeamActionPlanMode = "MyEditRow" Then
                If Not String.IsNullOrEmpty(txtClosedDate.Text.Trim()) Then
                    If Not IsDate(txtClosedDate.Text) Then
                        Master.DisplayError("Invalid Closed Date")
                        txtClosedDate.Focus()
                        Return
                    End If
                End If
                blnSuccess = UpdateTeamActionPlan()
            End If

            If blnSuccess Then
                RedirectToPriorProgram()
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

            RedirectToPriorProgram()
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
                Dim ds As DataTable = TeamActionPlan.SelectTeamActionPlan(SessionManager.SelectedTeamID, SessionManager.SelectedValue)
                Dim dr As DataRow = ds.Rows(0)
                If ds.Rows.Count <> 0 Then
                    Dim objItem As ListItem
                    txtActionNumber.Text = dr("ActionNumber")

                    objItem = ddlMeetings.Items.FindByValue(dr("TeamMeetingID").ToString)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                        txtTeamMeeting.Text = objItem.Text
                    Else
                        pnlAction.Visible = False
                    End If

                    txtActionItem.Text = dr("ActionItem").ToString
                    txtExpandActionItemDefinition.Text = dr("ActionItemDefinition").ToString
                    txtAssignedToOther.Text = dr("AssignedToOther").ToString

                    If IsDate(dr("TargetDate")) Then
                        txtTargetDate.Text = Convert.ToDateTime("" + dr("TargetDate")).ToShortDateString
                    Else
                        txtTargetDate.Text = ""
                    End If
                    If IsDate(dr("ClosedDate")) Then
                        txtClosedDate.Text = Convert.ToDateTime("" + dr("ClosedDate")).ToShortDateString
                    Else
                        txtClosedDate.Text = ""
                    End If
                    txtExpandActions.Text = dr("Actions").ToString
                    If txtClosedDate.Text.Trim.Length > 0 Then
                        If Convert.ToBoolean(dr("Cancelled")) Then
                            rblCancelled.SelectedValue = 1
                        Else
                            rblCancelled.SelectedValue = 0
                        End If
                    End If

                    objItem = ddlAssignedTo.Items.FindByValue(dr("AssignedTo"))
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                        txtAssignedTo.Text = objItem.Text
                    Else
                        ddlAssignedTo.Items.Add(New ListItem(dr("AssignedTo").ToString.Trim(), dr("AssignedTo").ToString.Trim()))
                        objItem = ddlAssignedTo.Items.FindByValue(dr("AssignedTo"))
                        objItem.Selected = True
                        txtAssignedTo.Text = objItem.Text
                    End If

                    If dr("StepNo") IsNot DBNull.Value Then
                        objItem = ddlStepNo.Items.FindByValue(dr("StepNo"))
                        If objItem IsNot Nothing Then
                            objItem.Selected = True
                            txtStepNo.Text = objItem.Text
                        End If
                    End If

                    If SessionManager.TeamActionPlanMode = "EditRow" OrElse SessionManager.TeamActionPlanMode = "MyEditRow" Then
                        txtAssignedTo.Visible = False
                        ddlAssignedTo.Visible = True
                        txtStepNo.Visible = False
                        ddlStepNo.Visible = True
                    Else
                        txtAssignedTo.Visible = True
                        ddlAssignedTo.Visible = False
                        txtStepNo.Visible = True
                        ddlStepNo.Visible = False
                    End If

                    TransactionHistory1.TableName = DBTableName
                    TransactionHistory1.RecordID = SessionManager.SelectedTeamID & "," & SessionManager.SelectedValue

                    Dim objDic As New Dictionary(Of String, String)
                    objDic.Add("Team", SessionManager.SelectedTeam)
                    objDic.Add("TeamMeeting", ddlMeetings.SelectedItem.Text.Trim())
                    objDic.Add("StepNo", ddlStepNo.SelectedItem.Text.Trim())
                    objDic.Add("ActionItem", txtActionItem.Text.Trim())
                    objDic.Add("ActionItemDefinition", txtExpandActionItemDefinition.Text.Trim())
                    objDic.Add("AssignedTo", ddlAssignedTo.SelectedItem.Text.Trim())
                    objDic.Add("AssignedToOther", txtAssignedToOther.Text.Trim())
                    objDic.Add("TargetDate", txtTargetDate.Text.Trim())
                    objDic.Add("ClosedDate", txtClosedDate.Text.Trim())
                    objDic.Add("Actions", txtExpandActions.Text.Trim())

                    SessionManager.RecordTransactionCurrentValues = objDic
                End If
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

            Select Case SessionManager.TeamActionPlanMode.ToString()
                Case "ViewRow", "MyViewRow", "DeleteRow"
                    If SessionManager.TeamActionPlanMode = "ViewRow" OrElse SessionManager.TeamActionPlanMode = "MyViewRow" Then
                        pnlOKCancel.Visible = False
                    End If
                    imgTargetDate.Visible = False
                    imgClosedDate.Visible = False
                    txtActionItem.ReadOnly = True
                    txtActionItem.CssClass = "Textbox_Display"
                    txtExpandActionItemDefinition.ReadOnly = True
                    txtExpandActionItemDefinition.CssClass = "Textbox_Display"
                    txtAssignedTo.ReadOnly = True
                    txtAssignedTo.CssClass = "Textbox_Display"
                    txtAssignedToOther.ReadOnly = True
                    txtAssignedToOther.CssClass = "Textbox_Display"
                    txtTargetDate.ReadOnly = True
                    txtTargetDate.CssClass = "Textbox_Display"
                    txtTargetDate_CalendarExtender.Enabled = False
                    txtExpandActions.ReadOnly = True
                    txtExpandActions.CssClass = "Textbox_Display"
                    txtClosedDate.ReadOnly = True
                    txtClosedDate.CssClass = "Textbox_Display"
                    txtClosedDate_CalendarExtender.Enabled = False
                    ddlMeetings.Visible = False
                    txtTeamMeeting.Visible = True
                    rblCancelled.Enabled = False
                Case "EditRow", "MyEditRow"
                    txtExpandActionItemDefinition.CssClass = "Textbox_Entry"
                    txtAssignedToOther.CssClass = "Textbox_Entry"
                    imgTargetDate.Visible = True
                    imgClosedDate.Visible = True
                    ddlMeetings.Visible = False
                    txtTeamMeeting.Visible = True
                    ddlStepNo.Focus()
                Case "AddMeeting"
                    imgClosedDate.Visible = True
                    txtAssignedTo.Visible = False
                Case "AddRow"
                    imgTargetDate.Visible = True
                    imgClosedDate.Visible = True
                    txtAssignedTo.Visible = False
            End Select
        End Sub
        Private Sub BindDropdownList()
            Try
                BindMeetings()
                BindAssignedTo()
                BindStepNo()
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindDropdownList", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindMeetings()
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
                TeamMeetings.SelectTeamMeetingList(ddlMeetings, SessionManager.SelectedTeamID)
                ddlMeetings.Items.Insert(0, "")
            Catch Exc As Exception
                Throw
            End Try
        End Sub
        Private Sub BindAssignedTo()
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
                If SessionManager.TeamMeetingID > 0 Then
                    If SessionManager.TeamActionPlanMode = "AddRow" Then
                        TeamMembership.SelectTeamMembershipList(ddlAssignedTo, SessionManager.SelectedTeamID)
                    Else
                        TeamMeetingAttendance.SelectTeamMeetingAttendanceList(SessionManager.TeamMeetingID, ddlAssignedTo)
                    End If
                Else
                    TeamMembership.SelectTeamMembershipList(ddlAssignedTo, SessionManager.SelectedTeamID)
                End If

                ddlAssignedTo.Items.Insert(0, "")
            Catch Exc As Exception
                Throw
            End Try
        End Sub
        Private Sub BindStepNo()
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
                TeamRouteSteps.SelectTeamRouteStepsListByTeam(SessionManager.SelectedTeamID, ddlStepNo)
                ddlStepNo.Items.Insert(0, "")
            Catch Exc As Exception
                Throw
            End Try
        End Sub
        Private Sub RedirectToPriorProgram()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.TeamActionPlanMode.Contains("My") Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamActionPlanMode)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)

                Dim objTeamStack As TeamStackItem = CType(SessionManager.TeamStack, Stack).Pop

                If objTeamStack.TeamName = "" Then
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedTeamName)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedTeamID)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedTeam)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedOPI)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedTeamAllowEdit)

                    If objTeamStack.LastMenu.Trim.Length > 0 Then
                        SessionManager.CurrentMenuProgram = objTeamStack.LastMenu
                    End If
                    If objTeamStack.ProgramName.ToString.Trim.Length > 0 Then
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & DataAccess.Custom.ProgramSecurity.GetProgramURL(objTeamStack.ProgramName), False)
                    End If
                Else
                    SessionManager.SelectedOPI = objTeamStack.OPIName
                    SessionManager.SelectedTeamID = objTeamStack.TeamID
                    SessionManager.SelectedTeam = objTeamStack.TeamName
                    SessionManager.SelectedTeamName = DataAccess.Tables.Teams.GetTeamName(SessionManager.SelectedTeamID)
                    SessionManager.CurrentMenuProgram = objTeamStack.LastMenu
                    SessionManager.SelectedTeamAllowEdit = UserSiteMaster.SelectTeamAllowEdit(SessionManager.SelectedTeamID, SessionManager.UserID)
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & DataAccess.Custom.ProgramSecurity.GetProgramURL(objTeamStack.ProgramName), False)
                End If
            Else
                If SessionManager.CallingProgram > "" Then
                    Dim strCallingProgram As String = SessionManager.CallingProgram
                    'SessionManager.TeamActionPlanMode = SessionManager.CallingMode
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamActionPlanMode)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CallingProgram)
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strCallingProgram), False)
                Else
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamMeetingID)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamActionPlanMode)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CurrentProgram)
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamActionPlanMaintenance"), False)
                End If
            End If
        End Sub
        Private Function InsertTeamActionPlan() As Boolean
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
                Dim iMeetingID As Integer = -1
                If Not String.IsNullOrEmpty(txtTargetDate.Text.Trim()) Then
                    If Not IsDate(txtTargetDate.Text) Then
                        Master.DisplayError("Invalid Target Date")
                        txtTargetDate.Focus()
                        Return False
                    Else
                        If ddlMeetings.SelectedItem IsNot Nothing AndAlso ddlMeetings.SelectedItem.Value.ToString.Trim.Length > 0 Then
                            iMeetingID = ddlMeetings.SelectedItem.Value

                            Dim strMeetingDate() As String = ddlMeetings.SelectedItem.Text.Split("-")

                            If Date.Compare(CDate(strMeetingDate(0).Trim()), CDate(txtTargetDate.Text.Trim())) > 0 Then
                                Master.DisplayError("Target Date must be greater than or equal to Meeting Date")
                                txtTargetDate.Focus()
                                Return False
                            End If
                        End If
                    End If
                End If

                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)
                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                Dim strTargetDate As String = RegionalConversion.FormatSQLDate(txtTargetDate.Text)
                Dim strClosedDate As String = RegionalConversion.FormatSQLDate(txtClosedDate.Text)
                Dim bCancelled As Boolean = False

                If strClosedDate.Trim.Length > 0 Then
                    If txtExpandActions.Text.Trim.Length = 0 Then
                        Master.DisplayError("You must enter Actions text to Close an Action")
                        Return False
                    ElseIf rblCancelled.SelectedItem Is Nothing Then
                        Master.DisplayError("You must select a status to Close an Action")
                        Return False
                    End If

                    bCancelled = rblCancelled.SelectedValue
                End If

                Dim iActionNumber As Integer = TeamActionPlan.AddTeamActionPlan(SessionManager.SelectedTeamID, iMeetingID, txtActionItem.Text.Trim, txtExpandActionItemDefinition.Text.Trim, ddlAssignedTo.SelectedValue, txtAssignedToOther.Text.Trim, strTargetDate, strClosedDate, ddlStepNo.SelectedValue, txtExpandActions.Text.Trim, bCancelled)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedTeamID & "," & iActionNumber.ToString, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertTeamActionPlan ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateTeamActionPlan() As Boolean
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
                If Not String.IsNullOrEmpty(txtTargetDate.Text.Trim()) Then
                    If Not IsDate(txtTargetDate.Text) Then
                        Master.DisplayError("Invalid Target Date")
                        txtTargetDate.Focus()
                        Return False
                    End If
                End If

                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.CompareDictionaryValues(SessionManager.RecordTransactionCurrentValues, objDic)
                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                Dim strTargetDate As String = RegionalConversion.FormatSQLDate(txtTargetDate.Text)
                Dim strClosedDate As String = RegionalConversion.FormatSQLDate(txtClosedDate.Text)
                Dim bCancelled As Boolean = False
                Dim iTeamMeetingID As Integer = 0
                If IsNumeric(ddlMeetings.SelectedItem.Value.ToString) Then
                    iTeamMeetingID = ddlMeetings.SelectedItem.Value
                End If
                If strClosedDate.Trim.Length > 0 Then
                    If txtExpandActions.Text.Trim.Length = 0 Then
                        Master.DisplayError("You must enter Actions text to Close an Action")
                        Return False
                    ElseIf rblCancelled.SelectedItem Is Nothing Then
                        Master.DisplayError("You must select a status to Close an Action")
                        Return False
                    End If

                    bCancelled = rblCancelled.SelectedValue
                End If

                TeamActionPlan.UpdateTeamActionPlan(SessionManager.SelectedTeamID, SessionManager.SelectedValue, iTeamMeetingID, txtActionItem.Text.Trim, txtExpandActionItemDefinition.Text.Trim, ddlAssignedTo.SelectedValue, txtAssignedToOther.Text.Trim, strTargetDate, strClosedDate, ddlStepNo.SelectedValue, txtExpandActions.Text.Trim, bCancelled)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedTeamID & "," & SessionManager.SelectedValue, strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - Update TeamActionPlan", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function DeleteTeamActionPlan() As Boolean
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
                TeamActionPlan.DeleteTeamActionPlan(SessionManager.SelectedTeamID, SessionManager.SelectedValue)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedTeamID & "," & SessionManager.SelectedValue, "Team Action Plan Deleted", SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - Delete TeamActionPlan ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
            Return True
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
            objDic.Add("Team", SessionManager.SelectedTeam)
            objDic.Add("TeamMeeting", ddlMeetings.SelectedItem.Text.Trim())
            objDic.Add("StepNo", ddlStepNo.SelectedItem.Text.Trim())
            objDic.Add("ActionItem", txtActionItem.Text.Trim())
            objDic.Add("ActionItemDefinition", txtExpandActionItemDefinition.Text.Trim())
            objDic.Add("AssignedTo", ddlAssignedTo.SelectedItem.Text.Trim())
            objDic.Add("AssignedToOther", txtAssignedToOther.Text.Trim())
            objDic.Add("TargetDate", RegionalConversion.FormatSQLDate(txtTargetDate.Text.Trim()))
            objDic.Add("ClosedDate", RegionalConversion.FormatSQLDate(txtClosedDate.Text.Trim()))
            objDic.Add("Actions", txtExpandActions.Text.Trim())
            Return objDic
        End Function
#End Region

    End Class
End Namespace
