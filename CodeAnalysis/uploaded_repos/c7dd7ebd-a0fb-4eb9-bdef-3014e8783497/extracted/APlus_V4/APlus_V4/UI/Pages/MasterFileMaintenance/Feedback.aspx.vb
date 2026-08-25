#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports System.Web.Mail
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class Feedback
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Feedback"
        Private Shared ReadOnly ProgramName As String = "Feedback"
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
                Try
                    FeedbackEmailAddressMaster.SelectFeedbackEmailAddressList(chklstEmail)
                Catch Exc As Exception
                    ErrorControl.DisplayErrors(ProgramName & " - Page_Load", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                End Try

                If SessionManager.IsAdministrator Then
                    chklstEmail.Visible = True
                Else
                    Dim dtMode As DataTable = ProgramSecurity.ProgramModeFromProgram(SessionManager.UserID, "Feedback")
                    If dtMode.Rows.Count > 0 Then
                        If CType(dtMode.Rows(0).Item("AllowEdit"), Boolean) = True Then
                            chklstEmail.Visible = True
                        Else
                            chklstEmail.Visible = False
                        End If
                    Else
                        chklstEmail.Visible = False
                    End If
                End If

                txtExpandFeedback.Focus()
            End If
        End Sub
        Public Sub SendMail()
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
                Dim objMail As New Net.Mail.SmtpClient()
                objMail.Host = ConfigurationManager.AppSettings("SMTPServer")

                Dim strTo As String = ""
                Dim selectedcount As Int16 = 0

                For Each lst As ListItem In chklstEmail.Items
                    If lst.Selected Then
                        selectedcount = selectedcount + 1
                        strTo = strTo & lst.Value & ","
                    End If
                Next

                If selectedcount = 0 Then
                    Exit Sub
                End If

                strTo = strTo.Remove(strTo.Length - 1, 1)
                Dim strFrom As String = ConfigurationManager.AppSettings("SendEmailFrom")
                objMail.Send(strFrom, strTo, ConfigurationManager.AppSettings("ApplicationNameRef") & " Feedback", txtExpandFeedback.Text)
            Catch Exc As Exception
                ErrorControl.DisplayErrors(ProgramName & " - SendMail", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub btnSend_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnSend.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim strProgram As String = ProgramMaster.SelectProgramForURL(SessionManager.CurrentProgramURL).Trim
                FeedbackMaster.AddFeedbackMaster(txtExpandFeedback.Text, Trim(SessionManager.UserID), strProgram)
                If chklstEmail.Items.Count > 0 Then
                    SendMail()
                End If

                txtExpandFeedback.Text = String.Empty
                txtExpandFeedback.Focus()
                pnlSuccess.Visible = True
                lblSuccess.Text = "Feedback has successfully been sent."
            Catch Exc As Exception
                ErrorControl.DisplayErrors(ProgramName & " - btnSend_Click", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                txtExpandFeedback.Focus()
            End Try
        End Sub
#End Region

    End Class
End Namespace

