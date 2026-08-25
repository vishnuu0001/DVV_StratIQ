#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports System.Web.Security
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.DataAccess.Custom
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class OPISelection
        Inherits ApplicationBase

#Region " Private Constant Variables"
        Private Shared ReadOnly FormName As String = "OPI Selection"
        Private Shared ReadOnly ProgramName As String = "OPISelection"
#End Region

#Region " Load JavaScripts"
        Private Sub LoadJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel}
            Dim OverMessageArr() As String = {"OK - Enter", "OK - Enter", "Cancel", "Cancel"}
            Dim OutMessageArr() As String = {"", "", "", ""}
            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)
            btnOK.Attributes.Add("onclick", "return CheckTeam(document.getElementById('" + ddlOPI.UniqueID + "'));")

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event)")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
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

            Master.IconImage = Request.ApplicationPath & "/images/OPI.gif"
            Master.HeaderMessage = FormName

            LoadJavaScripts()

            If Not Page.IsPostBack Then
                If SessionManager.SelectedTeamID = 0 Then
                    If SessionManager.CurrentProgram <> String.Empty Then
                        SessionManager.SavedProgram = SessionManager.CurrentProgram
                    End If

                    SessionManager.CurrentProgram = Request.Path
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamSelection"), False)
                    Return
                Else
                    If SessionManager.SavedProgram <> String.Empty Then
                        SessionManager.CurrentProgram = SessionManager.SavedProgram
                        SessionManager.SavedProgram = ""
                    ElseIf SessionManager.CurrentProgram = Request.Path Then
                        SessionManager.CurrentProgram = ""
                    End If
                End If

                BindOPI()
                ddlOPI.Focus()
            End If
        End Sub
        Private Sub btnCancel_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnCancel.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            RemoveCurrentProgramandGoBack()
        End Sub
        Private Sub btnOK_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If ddlOPI.SelectedItem.Value.Trim <> "" Then
                SessionManager.SelectedOPI = ddlOPI.SelectedValue.Trim
            Else
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedOPI)
            End If

            If SessionManager.CurrentProgram <> "" Then
                Response.Redirect(SessionManager.CurrentProgram, False)
            Else
                RemoveCurrentProgramandGoBack()
            End If
        End Sub
#End Region

#Region " Custom Function"
        Private Sub BindOPI()
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
                TeamOPI.SelectOPIsByTeam(ddlOPI, SessionManager.SelectedTeamID)
                If SessionManager.SelectedOPI <> "" Then
                    If Not IsNothing(ddlOPI.Items.FindByValue(SessionManager.SelectedOPI)) Then
                        ddlOPI.Items.FindByValue(SessionManager.SelectedOPI).Selected = True
                    End If
                End If

                If ddlOPI.SelectedIndex = 0 Then
                    If ddlOPI.Items.Count = 2 Then
                        ddlOPI.SelectedIndex = 1
                        btnOK_Click(Nothing, Nothing)
                    End If
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindOPI", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

    End Class
End Namespace
