<%@ Application Language="VB" %>

<script RunAt="server">

    Sub Application_Error(ByVal sender As Object, ByVal e As EventArgs)
        Dim ex As Exception = Server.GetLastError().GetBaseException()
        Dim strUser As String = "AppError"
        Dim strProgram As String = "Application Error"

        WebApp.APlus.DataAccess.Tables.EventTracker.Add(strProgram, ex.Message.Trim() + vbCrLf + Server.GetLastError.StackTrace + vbCrLf + ex.StackTrace, strUser)
    End Sub

</script>

