#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class UserJobMaster3
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "User Job Master"
        Private Shared ReadOnly ProgramName As String = "UserJobMaster3"
#End Region

#Region " Load JavaScripts"
        Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel"}
            Dim OutMessageArr() As String = {"", ""}

            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event)")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
        End Sub
#End Region

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Master.IconImage = Request.ApplicationPath + "/images/usergroup.gif"
            Master.HeaderMessage = FormName & " - " & SessionManager.UserJobMode.Replace("Row", "")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                Select Case SessionManager.UserJobMode
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this User.  This will remove all Skill Ratings for this User');")
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserJobMaster1"), False)
                End Select
            End If
        End Sub

        Private Sub btnOK_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Dim blnSuccess As Boolean = False

            If SessionManager.UserJobMode = "DeleteRow" Then
                blnSuccess = DeleteUser()
            End If

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueUserJobUser)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.UserJobMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserJobMaster1"), False)
            End If
        End Sub

        Private Sub btnCancel_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnCancel.Click
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.UserJobMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserJobMaster1"), False)
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadSelectedRecord()
            Try
                Dim dt As DataTable = UserJobMaster.SelectUserJobMasterByKey(SessionManager.SelectedValueJob, SessionManager.SelectedValueUserJobUser)
                If dt.Rows.Count <> 0 Then
                    Dim dr As DataRow = dt.Rows(0)
                    txtJobID.Text = SessionManager.SelectedValueJob.ToString()
                    txtJob.Text = dr("Job").ToString()
                    txtUserID.Text = dr("UserID").ToString()
                    txtUser.Text = dr("UserName").ToString()
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Function DeleteUser() As Boolean
            Try
                UserJobMaster.DeleteUserJobMasterByKey(SessionManager.SelectedValueJob, SessionManager.SelectedValueUserJobUser)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteUser", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
        End Function
#End Region

    End Class
End Namespace