#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Custom
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class AnomalyOrigins3Master1
        Inherits ApplicationBase

#Region " Constants"
        Private Shared ReadOnly FormName As String = "Anomaly Origins 3"
        Private Shared ReadOnly ProgramName As String = "AnomalyOrigins3Master1"
#End Region

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Master.IconImage = Request.ApplicationPath & "/images/document.gif"
            Master.HeaderMessage = FormName
            Master.AddBodyAttribute("onkeydown", "TrapEscKey(document.getElementById('" + MasterControl1.ExitButtonID + "'),window.event)")
            Master.AddBodyAttribute("onkeydown", "TrapEnterKey(document.getElementById('" + MasterControl1.AddButtonID + "'),window.event)")

            If SessionManager.SelectedValueOrigin2ID = 0 Then
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyOrigins2Master1"))
            End If

            MasterControl1.StoredProcedureParams.Add("@AnomalyOrigin2ID", SessionManager.SelectedValueOrigin2ID)
        End Sub
        Protected Sub MasterControl1_onRowCommand(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewCommandEventArgs) Handles MasterControl1.onRowCommand
            Select Case e.CommandName
                Case "EditRow", "DeleteRow"
                    SessionManager.SelectedValueOrigin3ID = CInt(MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("AnomalyOrigin3ID"))
                    SessionManager.Origin3Mode = e.CommandName
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyOrigins3Master2"))
            End Select
        End Sub
        Protected Sub MasterControl1_ExitClick(ByVal sender As Object, ByVal e As System.EventArgs) Handles MasterControl1.ExitClick
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueOrigin3ID)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyOrigins2Master1"))
        End Sub
        Protected Sub Timer1_Tick(ByVal sender As Object, ByVal e As System.EventArgs) Handles Timer1.Tick
            Try
                Timer1.Enabled = False
                MasterControl1.DataBind()
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - Loading_MasterControl", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

    End Class
End Namespace
