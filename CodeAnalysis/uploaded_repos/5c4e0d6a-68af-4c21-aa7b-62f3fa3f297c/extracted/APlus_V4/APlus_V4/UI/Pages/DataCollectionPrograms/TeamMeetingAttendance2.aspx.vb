#Region "Imports "

Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.UI.CustomControls

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class TeamMeetingAttendance2
        Inherits ApplicationBase

#Region "Private/Constant Variables"
        Private Shared ReadOnly FormName As String = "Team Meeting Attendance"
        Private Shared ReadOnly ProgramName As String = "TeamMeetingAttendance2"
        Private blnSuccess As Boolean = False
        Private blnInvited As Boolean = False
        Private blnAttended As Boolean = False
        Private blnEmailUser As Boolean = False
#End Region

#Region " JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel, btnExit}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel", "Exit"}
            Dim OutMessageArr() As String = {"", "", ""}
            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnExit.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
        End Sub
        Private Sub LoadAddModeJavaScript()
            Dim myTabArray() As Object = {ddlUserID}
            Dim TabKeyDownArr() As String = {Tab(ddlUserID, ddlUserID, "No")}
            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
#End Region

#Region " Load Culture Translations "
        Private Sub LoadCultureTranslations()
            Try
                lblMeetingDate.Text = GetTranslationString("meeting date", lblMeetingDate.Text.Replace(":", "")) & ":"
                lblMeetingTime.Text = GetTranslationString("meeting time", lblMeetingTime.Text.Replace(":", "")) & ":"
                lblUserName.Text = GetTranslationString("username", lblUserName.Text.Replace(":", "")) & ":"
                lblOr.Text = GetTranslationString("or", lblOr.Text)
                lblInvited.Text = GetTranslationString("invited", lblInvited.Text.Replace(":", "")) & ":"
                lblAttended.Text = GetTranslationString("attended", lblAttended.Text.Replace(":", "")) & ":"
                lblMaintenanceUserID.Text = GetTranslationString("maintuserid", lblMaintenanceUserID.Text.Replace(":", "")) & ":"
                lblMaintenanceDate.Text = GetTranslationString("maintdate", lblMaintenanceDate.Text.Replace(":", "")) & ":"
                btnOK.Text = GetTranslationString("ok", btnOK.Text)
                btnCancel.Text = GetTranslationString("cancel", btnCancel.Text)
                btnExit.Text = GetTranslationString("exit", btnExit.Text)
                ckAllSites.Text = GetTranslationString("showusersfromallsites", ckAllSites.Text)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadCultureTranslations", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

#Region " Event Handler"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            If Not Page.IsPostBack Then
                LoadCultureTranslations()
            End If

            Master.IconImage = Request.ApplicationPath + "/images/UserMeeting.gif"
            Master.HeaderMessage = GetTranslationString(FormName, FormName) & " - " & GetTranslationString(SessionManager.TeamMeetingAttendanceMode.Replace("Row", ""), SessionManager.TeamMeetingAttendanceMode.Replace("Row", ""))
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                Select Case SessionManager.TeamMeetingAttendanceMode.ToString()
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this  Team Meeting Attendance.');")
                    Case "AddRow"
                        txtMeetingDate.Text = SessionManager.MeetingDate
                        txtMeetingTime.Text = SessionManager.MeetingTime
                        LoadAddModeJavaScript()
                        txtUserID.Visible = False
                        ddlUserID.Visible = True
                        blnInvited = chkInvited.Checked
                        blnAttended = chkAttended.Checked
                        UnEnableRecords()
                        ddlUserID.Focus()
                        BindUserID()
                    Case Else
                        RedirectToPriorProgram()
                End Select
            End If
        End Sub
        Private Sub btnOK_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Select Case SessionManager.TeamMeetingAttendanceMode.ToString()
                Case "DeleteRow"
                    blnSuccess = DeleteTeamMeetingAttendance()
                Case "AddRow"
                    If Not String.IsNullOrEmpty(txtUserName.Text.Trim()) Then
                        If Not String.IsNullOrEmpty(ddlUserID.SelectedItem.ToString.Trim()) Then
                            Master.DisplayError(GetTranslationString("cantselectusername", "Cannot select a UserName in dropdown and Enter a freeformat UserName"))
                            ddlUserID.Focus()
                            Return
                        End If
                    End If
                    If String.IsNullOrEmpty(txtUserName.Text.Trim()) Then
                        If String.IsNullOrEmpty(ddlUserID.SelectedItem.ToString.Trim()) Then
                            Master.DisplayError(GetTranslationString("mustselectusername", "Must select a UserName in dropdown Or Enter a freeformat UserName"))
                            ddlUserID.Focus()
                            Return
                        End If
                    End If
                    If Page.IsValid Then
                        blnInvited = chkInvited.Checked
                        blnAttended = chkAttended.Checked
                        blnSuccess = InsertTeamMeetingAttendance()
                        txtUserID.Text = ddlUserID.SelectedItem.ToString.Trim()
                    End If
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamMeetingAttendanceMode)
                RedirectToPriorProgram()
            End If
        End Sub
        Private Sub btnCancel_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnCancel.Click, btnExit.Click
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamMeetingAttendanceMode)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.MeetingTime)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.MeetingDate)

            RedirectToPriorProgram()
        End Sub
        Private Sub ckAllSites_CheckedChanged(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles ckAllSites.CheckedChanged
            If ckAllSites.Checked Then
                BindUserID(True)
            Else
                BindUserID()
            End If
        End Sub
#End Region

#Region " Custom Method"
        Private Sub LoadSelectedRecord()
            Try
                txtMeetingDate.Text = SessionManager.MeetingDate
                txtMeetingTime.Text = SessionManager.MeetingTime
                txtUserID.Text = SessionManager.SelectedValue
                txtUserID.Visible = True
                ddlUserID.Visible = False
                Dim strDateHolder As String = RegionalConversion.FormatSQLDate(SessionManager.MeetingDate)
                Dim objDt As DataTable = TeamMeetingAttendance.SelectTeamMeetingAttendanceUser(SessionManager.TeamMeetingID, SessionManager.SelectedValue)
                Dim objRow As DataRow = objDt.Rows(0)
                chkInvited.Checked = objRow("Invited")
                chkAttended.Checked = objRow("Attended")
                txtMaintenanceUserID.Text = objRow("MaintenanceUserID")
                txtMaintenanceDate.Text = objRow("MaintenanceDate")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindUserID(Optional ByVal bLoadAll As Boolean = False)
            ddlUserID.Items.Clear()
            Try
                If bLoadAll OrElse SessionManager.WorkingSiteID = 0 Then
                    UserMaster.SelectUserNameList(0, ddlUserID)
                Else
                    UserMaster.SelectUserNameList(SessionManager.WorkingSiteID, ddlUserID)
                End If
                ddlUserID.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindUserID", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub UnEnableRecords()
            Select Case SessionManager.TeamMeetingAttendanceMode.ToString()
                Case "AddRow"
                    txtMaintenanceDate.Visible = False
                    lblMaintenanceDate.Visible = False
                    txtMaintenanceUserID.Visible = False
                    lblMaintenanceUserID.Visible = False
                Case "View"
                    pnlOKCancel.Visible = False
                    txtUserID.ReadOnly = True
                    txtMaintenanceDate.Visible = True
                    lblMaintenanceDate.Visible = True
                    txtMaintenanceUserID.Visible = True
                    lblMaintenanceUserID.Visible = True
                Case "Delete"
                    txtUserName.Visible = False
                    chkInvited.Enabled = False
                    chkAttended.Enabled = False
                    lblOr.Visible = False
                    txtUserName.Visible = False
            End Select
        End Sub
        Private Function InsertTeamMeetingAttendance() As Boolean
            If Page.IsValid Then
                Try
                    Dim dt As DataTable = UserMaster.SelectUserMaster(ddlUserID.SelectedValue.ToString.Trim())
                    Dim strUserName As String
                    If dt.Rows.Count <> 0 Then
                        strUserName = dt.Rows(0).Item("LastName").ToString.Trim() & ", " & dt.Rows(0).Item("FirstName").ToString.Trim()
                    Else
                        strUserName = txtUserName.Text.Trim()
                    End If
                    Dim strDateHolder As String = RegionalConversion.FormatSQLDate(txtMeetingDate.Text)
                    TeamMeetingAttendance.AddTeamMeetingAttendance(SessionManager.SelectedTeamID, _
                                                                   SessionManager.TeamMeetingID, _
                                                                   ddlUserID.SelectedValue.ToString.Trim(), _
                                                                   strUserName.Trim(), _
                                                                   blnInvited, _
                                                                   blnAttended, _
                                                                   SessionManager.UserID)
                    Return True
                Catch Exc As Exception
                    Master.DisplayErrors(ProgramName & " - InsertTeamMeetingAttendance", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                    Return False
                End Try

            End If
        End Function
        Private Function DeleteTeamMeetingAttendance() As Boolean
            Try
                Dim strDateHolder As String = RegionalConversion.FormatSQLDate(txtMeetingDate.Text)
                TeamMeetingAttendance.DeleteTeamMeetingAttended(SessionManager.TeamMeetingID, txtUserID.Text)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteTeamMeetingAttendance", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
        End Function
        Private Sub RedirectToPriorProgram()
            If Not String.IsNullOrEmpty(SessionManager.CallingProgram.Trim()) Then
                Dim strCallingProgram As String = SessionManager.CallingProgram.Trim()
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CallingProgram)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamMeetingAttendanceMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strCallingProgram), False)
            Else
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamMeetingAttendanceMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamMeetingsMaintenance"), False)
            End If
        End Sub
#End Region

    End Class
End Namespace

