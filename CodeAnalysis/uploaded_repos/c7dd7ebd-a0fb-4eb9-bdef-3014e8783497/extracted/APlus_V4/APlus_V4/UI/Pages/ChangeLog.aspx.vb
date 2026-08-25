
Namespace WebApp.APlus.UI.Pages
    Partial Class ChangeLog
        Inherits PrinterFriendlyBase

#Region " Event Handlers"
        Protected Sub ChangeLog_Load(sender As Object, e As System.EventArgs) Handles Me.Load
            Master.HeaderMessage = "Change Log"
            Master.IconImage = Request.ApplicationPath & "/images/data_scroll.gif"

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnExit.UniqueID + "'),window.event)")
        End Sub
        Protected Sub btnExit_Click(sender As Object, e As System.EventArgs) Handles btnExit.Click
            RemoveCurrentProgramandGoBack()
        End Sub
#End Region

    End Class
End Namespace

