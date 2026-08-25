#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports System.Web.Security

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class TrainingDocumentAttachments
        Inherits ApplicationBase

#Region " Constant Variables"
        Private Shared ReadOnly FormName As String = "Training Attachments"
        Private Shared ReadOnly ProgramName As String = "TrainingDocumentAttachments"
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

            SessionManager.AttachmentType = "Training"
            SessionManager.AttachmentTypeID = AttachmentTypes.SelectAttachmentTypeIDByType("Training")

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("Attachments"), False)
        End Sub
#End Region

    End Class
End Namespace