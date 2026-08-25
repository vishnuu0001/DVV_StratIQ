#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class Logout
        Inherits ApplicationBase

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            If Not Page.IsPostBack Then
                'Display Remove AutoLogin checkbox only if we have UserID cookie
                If Not IsNothing(Request.Cookies("UserID")) Then
                    chkAutoLogin.Visible = True
                End If
                If Session.IsNewSession = True Then
                    Session.Abandon()
                    Response.Redirect("Login.aspx")
                    Exit Sub
                End If

                Master.HeaderMessage = "Leave the Application"
                Master.IconImage = Request.ApplicationPath & "/images/Log Off.gif"
                Master.HideIcons = True

                Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event)")
                Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnLogout.UniqueID + "'),window.event)")
            End If
        End Sub
        Private Sub btnLogout_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnLogout.Click
            'if Remove AutoLogin was checked remove all cookies
            If chkAutoLogin.Checked Then
                Response.Cookies("UserID").Expires = Now
            End If
            Master.WriteErrors("Logout", "Logout", SessionManager.UserID)
            Session.Abandon()
            Response.Redirect(Request.ApplicationPath & "\Login.aspx")
        End Sub
        Protected Overrides Sub Finalize()
            MyBase.Finalize()
            GC.Collect()
        End Sub
        Private Sub btnCancel_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnCancel.Click
            If SessionManager.CurrentProgram <> String.Empty Then
                Response.Redirect(SessionManager.CurrentProgram)
            Else
                RemoveCurrentProgramandGoBack()
            End If
        End Sub
#End Region

    End Class
End Namespace

