Namespace WebApp.APlus.UI.Pages
    Partial Class ErrorPage
        Inherits PrinterFriendlyBase

        Protected Sub Page_Load(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.Load
            Master.IconImage = Request.ApplicationPath & "/images/ErrorPage.gif"
        End Sub
        Protected Sub btnOK_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Dim strUser As String = Request("REMOTE_USER")
            If InStr(strUser, "\", CompareMethod.Binary) > 0 Then
                strUser = strUser.Substring(InStr(strUser, "\", CompareMethod.Binary)).ToUpper
            End If

            If Response.Cookies("UserID") IsNot Nothing Then
                Response.Cookies("UserID").Expires = Now
            End If

            If txtExpandFeedback.Text.Trim.Length > 0 Then
                APlus.DataAccess.Tables.EventTracker.AddNoEmail("ErrorPage", "An Application Error has occured." & Environment.NewLine & txtExpandFeedback.Text.Trim, strUser)
            Else
                APlus.DataAccess.Tables.EventTracker.AddNoEmail("ErrorPage", "An Application Error has occured." & Environment.NewLine & "No Feedback Entered", strUser)
            End If

            Session.Abandon()
            Response.Redirect(Request.ApplicationPath & "\Login.aspx")
        End Sub

    End Class
End Namespace