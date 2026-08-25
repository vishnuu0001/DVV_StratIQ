#Region " Imports"
Imports System.Data
Imports System.IO
Imports System.Net.Mail
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class TeamActionPlan1
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Team Action Plan"
        Private Shared ReadOnly ProgramName As String = "TeamActionPlan1"
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
                chkSendStatusEmail.Text = GetTranslationString("sendactionplanemail", chkSendStatusEmail.Text)
                chkDisplayClosedTeamActions.Text = GetTranslationString("includeclosedteamactions", chkDisplayClosedTeamActions.Text)
                lnkPrintPage.Text = GetTranslationString("printfriendlyversion", lnkPrintPage.Text)
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

            Master.IconImage = Request.ApplicationPath & "/images/TeamAction.gif"
            Master.HeaderMessage = GetTranslationString(FormName, FormName)

            If Not Page.IsPostBack Then
                chkDisplayClosedTeamActions.Checked = SessionManager.DisplayClosedTeamActions

                If SessionManager.SelectedTeamID = 0 Then
                    SessionManager.CurrentProgram = Request.Path
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamSelection"))
                    Return
                End If
            Else
                SessionManager.DisplayClosedTeamActions = chkDisplayClosedTeamActions.Checked
            End If

            If Not IsNothing(SessionManager.CurrentProgram) Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CurrentProgram)
            End If

            Master.AddBodyAttribute("onkeydown", "TrapEscKey(document.getElementById('" + MasterControl1.ExitButtonID + "'),window.event)")
            Master.AddBodyAttribute("onkeydown", "TrapEnterKey(document.getElementById('" + MasterControl1.AddButtonID + "'),window.event)")

            MasterControl1.GridColumns(3).DataFormatString = "{0:" + SessionManager.DateFormat + " HH:mm}"
            MasterControl1.GridColumns(7).DataFormatString = "{0:" + SessionManager.DateFormat + "}"
            MasterControl1.GridColumns(8).DataFormatString = "{0:" + SessionManager.DateFormat + "}"
            MasterControl1.StoredProcedureParams.Add("@TeamID", SessionManager.SelectedTeamID)
            MasterControl1.StoredProcedureParams.Add("@DisplayClosedTeamActions", chkDisplayClosedTeamActions.Checked)

            If Not SessionManager.SelectedTeamAllowEdit AndAlso Not SessionManager.IsAdministrator Then
                MasterControl1.ShowAdd = False
                MasterControl1.ShowEdit = False
                MasterControl1.ShowDelete = False
            End If
        End Sub
        Protected Sub Timer1_Tick(ByVal sender As Object, ByVal e As System.EventArgs) Handles Timer1.Tick
            Timer1.Enabled = False
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            MasterControl1.DataBind()
            Master.MasterScriptManager.RegisterPostBackControl(MasterControl1.ExportButton)
        End Sub
        Protected Sub MasterControl1_onRowDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewRowEventArgs) Handles MasterControl1.onRowDataBound
            If e.Row.RowType = DataControlRowType.DataRow Then
                If IsDate(e.Row.Cells(7).Text) Then
                    Dim dtClosedDate As DateTime
                    Dim dtTargetDate As DateTime = Convert.ToDateTime(e.Row.Cells(7).Text)
                    If e.Row.Cells(8).Text <> "&nbsp;" Then
                        dtClosedDate = Convert.ToDateTime(e.Row.Cells(8).Text)
                        If Convert.ToBoolean(MasterControl1.MasterControlGrid.DataKeys(e.Row.RowIndex)("Cancelled").ToString) = True Then
                            e.Row.Cells(8).BackColor = Drawing.Color.Gray
                        ElseIf DateTime.Compare(dtClosedDate, dtTargetDate) <= 0 Then
                            e.Row.Cells(8).BackColor = Drawing.Color.Green
                        Else
                            e.Row.Cells(8).BackColor = Drawing.Color.Orange
                        End If
                    Else
                        If DateTime.Compare(dtTargetDate, Date.Now) >= 0 Then
                            e.Row.Cells(8).BackColor = Drawing.Color.Yellow
                        Else
                            e.Row.Cells(8).BackColor = Drawing.Color.Red
                        End If
                    End If
                End If

                If Not String.IsNullOrEmpty(MasterControl1.MasterControlGrid.DataKeys(e.Row.RowIndex)("ActionItemDefinition").ToString) Then
                    e.Row.Cells(4).ToolTip = MasterControl1.MasterControlGrid.DataKeys(e.Row.RowIndex)("ActionItemDefinition").ToString.Trim
                End If
            End If
        End Sub
        Protected Sub MasterControl1_onRowCommand(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewCommandEventArgs) Handles MasterControl1.onRowCommand
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", e.CommandName)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Select Case e.CommandName
                Case "ViewRow", "EditRow", "DeleteRow"
                    SessionManager.SelectedValue = MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("ActionNumber").ToString
                    SessionManager.TeamActionPlanMode = e.CommandName
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamActionPlanMaintenance2"), False)
            End Select
        End Sub
        Private Sub chkDisplayClosedTeamActions_CheckedChanged(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles chkDisplayClosedTeamActions.CheckedChanged
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.DisplayClosedTeamActions = chkDisplayClosedTeamActions.Checked
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamActionPlanMaintenance"), False)
        End Sub
        Protected Sub MasterControl3_ExitClick(ByVal sender As Object, ByVal e As System.EventArgs) Handles MasterControl1.ExitClick
            If chkSendStatusEmail.Checked Then
                SendActionPlanEmail()
            End If

            RemoveCurrentProgramandGoBack()
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub SendActionPlanEmail()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            'Sends emails to users with valid EmailAddress
            Dim strbTo As New System.Text.StringBuilder
            strbTo.Append("")

            Try
                Dim strEmailAddress As String = ""
                Dim hEmail As New Hashtable
                Dim objDT As DataTable = TeamMembership.SelectTeamMembershipDisplayByTeam(SessionManager.SelectedTeamID)

                For Each dtRow As DataRow In objDT.Rows
                    strEmailAddress = dtRow("EmailAddress").ToString
                    If strEmailAddress <> "" And strEmailAddress <> "&nbsp;" Then
                        Try
                            hEmail.Add(strEmailAddress, strEmailAddress)
                        Catch ex As Exception
                            'duplicate
                        End Try
                    End If
                Next

                Dim myEnumerator As IDictionaryEnumerator = hEmail.GetEnumerator()
                While myEnumerator.MoveNext
                    strEmailAddress = myEnumerator.Key.ToString
                    strEmailAddress.Replace(" ", "_")

                    If strbTo.Length > 0 Then
                        strbTo.Append(", " & strEmailAddress)
                    Else
                        strbTo.Append(strEmailAddress)
                    End If
                End While

                If strbTo.Length > 0 Then
                    Dim strDomain As String = ConfigurationManager.AppSettings("DefaultEmailFromDomain")
                    Dim strFrom As String = Replace(SessionManager.SelectedTeam, " ", "_") & "@" & strDomain
                    Dim strSubject As String
                    Dim strBody As String = ""

                    If SessionManager.SelectedTeamName.Trim.Length > 50 Then
                        strSubject = SessionManager.SelectedTeam & " - " & SessionManager.SelectedTeamName.Substring(0, 50) & " - " & GetTranslationString("actionplan", "Action Plan")
                    Else
                        strSubject = SessionManager.SelectedTeam & " - " & SessionManager.SelectedTeamName & " - " & GetTranslationString("actionplan", "Action Plan")
                    End If

                    strBody = SessionManager.SelectedTeam & "<br />" & SessionManager.SelectedTeamName & " Action Plan" & vbCrLf
                    strBody += "<br /><br />"
                    Dim strURL As String = "http://" & ConfigurationManager.AppSettings("ApplicationServerDNS").ToString & "/aplus/login.aspx"
                    strURL += "?auto=y&actionplan=" & SessionManager.SelectedTeamID
                    strBody += "<a href='" & strURL & "'>" & GetTranslationString("Click Here to view Team Action Plan for") & ": " & SessionManager.SelectedTeam & "</a>"

                    Dim MailClient As New SmtpClient
                    Dim msg As New MailMessage(strFrom, strbTo.ToString.Trim, strSubject, strBody)
                    MailClient.Host = ConfigurationManager.AppSettings("SMTPServer")
                    msg.IsBodyHtml = True

                    MailClient.Send(msg)
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - SendActionPlanEmail", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

    End Class
End Namespace
