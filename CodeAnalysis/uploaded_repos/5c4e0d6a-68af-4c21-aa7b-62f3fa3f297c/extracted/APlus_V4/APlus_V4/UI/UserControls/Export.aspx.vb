Namespace WebApp.APlus.UI.UserControls
    Partial Class Export
        Inherits System.Web.UI.Page

        Protected Sub Page_Load(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.Load
            Dim strHolder As String = SessionManager.ExportString

            Response.Clear()
            Response.ContentType = "application/vnd.ms-excel"
            Response.AddHeader("Content-Disposition", "attachment;filename=DataQuery.xls")
            Response.Buffer = True
            Response.Write(strHolder)

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.ExportString)

            Response.End()
        End Sub
    End Class
End Namespace
