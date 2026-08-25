#Region " Imports "
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports System.Diagnostics
Imports System.Net.Mail
Imports System.Text
Imports WebApp.APlus.Helper
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.UI.CustomControls
Imports System.Collections.Generic

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class TeamLog2
        Inherits ApplicationBase

#Region " Constants"
        Private Shared ReadOnly FormName As String = "Team Log"
        Private Shared ReadOnly ProgramName As String = "TeamLog2"
        Private Shared ReadOnly DBTableName As String = "TeamLog"
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel, btnExit}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel", "Exit"}
            Dim OutMessageArr() As String = {"", "", ""}
            Dim strDateFormat As String = SessionManager.DateFormat
            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnExit.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
        End Sub
        Private Sub LoadAddModeJavaScripts()
            Dim myTabArray() As Object = {txtExpandLogEntry, _
                                          txtExpandLogResponse, _
                                          chkSendTeamLogEmail}

            Dim TabKeyDownArr() As String = {Tab(txtExpandLogResponse, chkSendTeamLogEmail, "No"), _
                                                      Tab(chkSendTeamLogEmail, txtExpandLogEntry, "No"), _
                                                      Tab(txtExpandLogEntry, txtExpandLogResponse, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {txtExpandLogEntry, _
                                          txtExpandLogResponse, _
                                          chkSendTeamLogEmail}

            Dim TabKeyDownArr() As String = {Tab(txtExpandLogResponse, chkSendTeamLogEmail, "No"), _
                                                      Tab(chkSendTeamLogEmail, txtExpandLogEntry, "No"), _
                                                      Tab(txtExpandLogEntry, txtExpandLogResponse, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
#End Region

#Region " Load Culture Translations "
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
                lblLogEntry.Text = GetTranslationString("log entry", lblLogEntry.Text.Replace(":", "")) & ":"
                lblLogResponse.Text = GetTranslationString("log response", lblLogResponse.Text.Replace(":", "")) & ":"
                lblCreateUserID.Text = GetTranslationString("createuserid", lblCreateUserID.Text.Replace(":", "")) & ":"
                lblCreateDateTime.Text = GetTranslationString("createdate", lblCreateDateTime.Text.Replace(":", "")) & ":"
                lblMaintenanceUserID.Text = GetTranslationString("maintuserid", lblMaintenanceUserID.Text.Replace(":", "")) & ":"
                lblMaintenanceDate.Text = GetTranslationString("maintdate", lblMaintenanceDate.Text.Replace(":", "")) & ":"
                chkSendTeamLogEmail.Text = GetTranslationString("sendteamemail", chkSendTeamLogEmail.Text)
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

            SessionManager.HeaderMessage = GetTranslationString(FormName, FormName) & " - " & GetTranslationString(SessionManager.TeamLogMode.Replace("Row", ""), SessionManager.TeamLogMode.Replace("Row", ""))
            Master.HeaderMessage = SessionManager.HeaderMessage
            Master.IconImage = Request.ApplicationPath + "/images/usergroup.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                Select Case SessionManager.TeamLogMode
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        pnlOKCancel.Visible = True
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Team Log.');")
                        TransactionHistory1.LockControl = True
                    Case "EditRow"
                        btnOK.Text = "OK"
                        LoadEditModeJavaScripts()
                        LoadSelectedRecord()
                        UnEnableRecords()
                        txtExpandLogEntry.Focus()
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        SessionManager.SelectedValue = RegionalConversion.FormatSQLDate(DateTime.Now, True)
                        txtCreateDateTime.Text = Convert.ToDateTime("" + DateTime.Now).ToShortDateString + " " + Convert.ToDateTime("" + DateTime.Now).ToString("HH:mm:ss")
                        txtCreateUserID.Text = SessionManager.UserID
                        LoadAddModeJavaScripts()
                        UnEnableRecords()
                        txtExpandLogEntry.Focus()
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

            Dim blnSuccess As Boolean

            If SessionManager.TeamLogMode = "DeleteRow" Then
                blnSuccess = DeleteTeamLog()
            ElseIf SessionManager.TeamLogMode = "AddRow" Then
                blnSuccess = InsertTeamLog()
            ElseIf SessionManager.TeamLogMode = "EditRow" Then
                blnSuccess = UpdateTeamLog()
            End If

            If blnSuccess Then
                If chkSendTeamLogEmail.Checked Then
                    SendTeamLogEmail()
                End If

                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamLogMode)
                RedirectToPriorProgram()
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

            If SessionManager.TeamLogMode = "EditRow" Or SessionManager.TeamLogMode = "ViewRow" Or SessionManager.TeamLogMode = "DeleteRow" Or SessionManager.TeamLogMode = "AddRow" Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamLogMode)
            End If
            RedirectToPriorProgram()
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
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamLogMode)
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
                Dim dt As DataTable = TeamLog.SelectTeamLogByID(SessionManager.SelectedValue)
                If dt.Rows.Count <> 0 Then
                    Dim dr As DataRow = dt.Rows(0)
                    If IsDate(dr("CreateDateTime")) Then
                        txtCreateDateTime.Text = Convert.ToDateTime("" + dr("CreateDateTime")).ToShortDateString + " " + Convert.ToDateTime("" + dr("CreateDateTime")).ToString("HH:mm:ss")
                    Else
                        txtCreateDateTime.Text = ""
                    End If
                    txtExpandLogEntry.Text = dr.Item("LogEntry").ToString.Trim()
                    txtExpandLogResponse.Text = dr.Item("LogResponse").ToString.Trim()
                    txtCreateUserID.Text = dr.Item("CreateUserID").ToString.Trim()
                    txtMaintenanceUserID.Text = dr.Item("MaintenanceUserID").ToString.Trim()
                    txtMaintenanceDate.Text = Convert.ToDateTime("" + dr("MaintenanceDate")).ToShortDateString + " " + Convert.ToDateTime("" + dr("MaintenanceDate")).ToString("HH:mm:ss")

                    TransactionHistory1.TableName = DBTableName
                    TransactionHistory1.RecordID = SessionManager.SelectedValue

                    Dim objDic As New Dictionary(Of String, String)
                    objDic.Add("Team", SessionManager.SelectedTeam)
                    objDic.Add("LogEntry", txtExpandLogEntry.Text.Trim())
                    objDic.Add("LogResponse", txtExpandLogResponse.Text.Trim())
                    SessionManager.RecordTransactionCurrentValues = objDic
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - SelectTeamMeeting", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
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

            Select Case SessionManager.TeamLogMode.ToString()
                Case "ViewRow", "DeleteRow"
                    pnlOKCancel.Visible = False
                    txtCreateDateTime.ReadOnly = True
                    txtCreateDateTime.CssClass = "Textbox_Display"
                    txtExpandLogEntry.ReadOnly = True
                    txtExpandLogEntry.CssClass = "Textbox_Display"
                    txtExpandLogResponse.ReadOnly = True
                    txtExpandLogResponse.CssClass = "Textbox_Display"
                    txtCreateUserID.ReadOnly = True
                    txtCreateUserID.CssClass = "Textbox_Display"
                    txtMaintenanceDate.ReadOnly = True
                    txtMaintenanceDate.CssClass = "Textbox_Display"
                    txtMaintenanceUserID.ReadOnly = True
                    txtMaintenanceUserID.CssClass = "Textbox_Display"
                    chkSendTeamLogEmail.Visible = False
                    chkSendTeamLogEmail.Enabled = False
                Case "EditRow"
                    txtCreateDateTime.ReadOnly = True
                    txtCreateDateTime.CssClass = "Textbox_Display"
                    chkSendTeamLogEmail.Visible = True
                    chkSendTeamLogEmail.Enabled = True
                Case "AddRow"
                    txtMaintenanceUserID.Visible = False
                    txtMaintenanceDate.Visible = False
                    lblMaintenanceUserID.Visible = False
                    lblMaintenanceDate.Visible = False
                    chkSendTeamLogEmail.Visible = True
                    chkSendTeamLogEmail.Enabled = True
            End Select
        End Sub
        Private Function InsertTeamLog() As Boolean
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

                Dim intResult As Integer = TeamLog.AddTeamLog(SessionManager.SelectedTeamID, SessionManager.SelectedValue, txtExpandLogEntry.Text.Trim, txtExpandLogResponse.Text.Trim, SessionManager.UserID.Trim, SessionManager.UserID.Trim)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, intResult, strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertTeamLog", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateTeamLog() As Boolean
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
                TeamLog.UpdateTeamLog(SessionManager.SelectedValue, txtExpandLogEntry.Text.Trim, txtExpandLogResponse.Text.Trim, SessionManager.UserID)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValue, strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateTeamLog", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function DeleteTeamLog() As Boolean
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
                TeamLog.DeleteTeamLog(SessionManager.SelectedValue)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValue, "Team Log Deleted", SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteTeamLog", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
        End Function
        Private Function GetUpdatedValues() As Dictionary(Of String, String)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim objDic As New Dictionary(Of String, String)
            objDic.Add("Team", SessionManager.SelectedTeam)
            objDic.Add("LogEntry", txtExpandLogEntry.Text.Trim())
            objDic.Add("LogResponse", txtExpandLogResponse.Text.Trim())
            Return objDic
        End Function
        Private Sub SendTeamLogEmail()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim blnGoodToSendEmail As Boolean = False
            Dim strbTo As New System.Text.StringBuilder
            Dim strSubject As String = ""

            Try
                Dim dt As DataTable = TeamMembership.SelectTeamMembershipDisplayByTeam(SessionManager.SelectedTeamID)
                For Each dr As DataRow In dt.Rows
                    Dim strEmailAddress As String = dr("EmailAddress").ToString
                    If strEmailAddress <> "" Then
                        If Not blnGoodToSendEmail Then
                            strbTo.Append(strEmailAddress)
                        Else
                            strbTo.Append(", " & strEmailAddress)
                        End If
                        blnGoodToSendEmail = True
                    End If
                Next

                If blnGoodToSendEmail Then
                    Dim strDomain As String = ConfigurationManager.AppSettings("DefaultEmailFromDomain")
                    Dim strFrom As String = Replace(SessionManager.SelectedTeam.ToString, " ", "_") & "@" & strDomain
                    If Not String.IsNullOrEmpty(txtExpandLogResponse.Text.Trim()) Then
                        strSubject = "Team Log - Response " & SessionManager.SelectedTeam & "  " & SessionManager.SelectedValue
                    Else
                        strSubject = "Team Log - Entry " & SessionManager.SelectedTeam & "  " & SessionManager.SelectedValue
                    End If
                    Dim strBody As String = "Log Entry from " & UserMaster.GetUserFullNameLastNameFirst(SessionManager.UserID) & ":<br />" & txtExpandLogEntry.Text.Trim
                    strBody += "<br /><br />Log Response:<br />" & txtExpandLogResponse.Text.Trim
                    strBody += "<br /><br />"
                    Dim strURL As String = "http://" & ConfigurationManager.AppSettings("ApplicationServerDNS").ToString & "/aplus/login.aspx"
                    strURL += "?auto=y&TeamLog=" & SessionManager.SelectedTeamID
                    strBody += "<a href='" & strURL & "'>" & GetTranslationString("Click Here to view Team Log for") & ": " & SessionManager.SelectedTeam & "</a>"

                    Dim MailClient As New SmtpClient
                    Dim msg As New MailMessage(strFrom, strbTo.ToString.Trim, strSubject, strBody)
                    MailClient.Host = ConfigurationManager.AppSettings("SMTPServer")
                    msg.IsBodyHtml = True

                    MailClient.Send(msg)
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - SendTeamLogEmail", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub RedirectToPriorProgram()
            If SessionManager.CallingProgram > "" Then
                Dim strCallingProgram As String = SessionManager.CallingProgram
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CallingProgram)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamLogMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strCallingProgram))
            Else
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamLog1"))
            End If
        End Sub
#End Region

    End Class
End Namespace

