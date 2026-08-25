#Region " Imports"
Imports System.IO
Imports System.Data.SqlClient
Imports WebApp.APlus.UI
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class PopupAttachments1
        Inherits ApplicationBase

#Region " Constants"
        Private Shared ReadOnly FormName As String = "Popup Attachments"
        Private Shared ReadOnly ProgramName As String = "PopupAttachments1"
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

            Master.IconImage = Request.ApplicationPath & "/images/attachfile.gif"
            Master.HeaderMessage = FormName

            Master.AddBodyAttribute("onkeydown", "TrapEscKey(document.getElementById('" + MasterControl1.ExitButtonID + "'),window.event)")
            Master.AddBodyAttribute("onkeydown", "TrapEnterKey(document.getElementById('" + MasterControl1.AddButtonID + "'),window.event)")

            MasterControl1.StoredProcedureParams.Add("@SiteID", SessionManager.WorkingSiteID)

            Dim objCol As New ButtonField
            objCol.ButtonType = ButtonType.Link
            objCol.Text = "View File"
            objCol.CommandName = "ViewFile"
            MasterControl1.GridColumns.Add(objCol)
        End Sub
        Protected Sub Timer1_Tick(ByVal sender As Object, ByVal e As System.EventArgs) Handles Timer1.Tick
            Timer1.Enabled = False

            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            MasterControl1.DataBind()
            Master.MasterScriptManager.RegisterPostBackControl(MasterControl1.ExportButton)
        End Sub
        Protected Sub MasterControl1_onRowCommand(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewCommandEventArgs) Handles MasterControl1.onRowCommand
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", e.CommandName)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Select Case e.CommandName
                Case "DeleteRow", "EditRow", "ViewRow"
                    SessionManager.SelectedValueAttachmentID = MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("AttachmentID").ToString
                    SessionManager.PopupAttachmentMode = e.CommandName

                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("PopupAttachments2"), False)
                Case "ViewFile"
                    Dim strDir As String = ConfigurationManager.AppSettings("PopupAttachmentsVirtualRootDirectory")
                    Dim strScript As String
                    strScript = "<script language='javascript'>LaunchExplorer('http://" & ConfigurationManager.AppSettings("ApplicationServerDNS").ToString & strDir & MasterControl1.Rows(CInt(e.CommandArgument)).Cells(2).Text & "')" & "</script>"
                    ScriptManager.RegisterStartupScript(sender, sender.GetType, "ShowAttachment", strScript, False)
            End Select
        End Sub
#End Region

    End Class
End Namespace
