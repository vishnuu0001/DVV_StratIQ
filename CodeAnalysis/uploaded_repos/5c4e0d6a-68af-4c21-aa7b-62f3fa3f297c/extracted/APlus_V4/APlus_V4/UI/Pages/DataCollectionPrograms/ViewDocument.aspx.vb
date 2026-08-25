#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports System.DirectoryServices
Imports System.Globalization
Imports WebApp.APlus
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class ViewDocument
        Inherits System.Web.UI.Page

#Region " Constants"
        Private Shared ReadOnly FormName As String = "View Document"
        Private Shared ReadOnly ProgramName As String = "ViewDocument"
#End Region

#Region " Event Handler"
        Protected Sub ViewDocument_Load(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.Load
            Try
                Dim iAttachmentID As Integer
                Dim objDT As New DataTable

                iAttachmentID = Request.Params("AttachmentID")

                objDT = AnomalyAttachments.SelectAnomalyAttachmentByID(iAttachmentID)

                If Not objDT Is Nothing AndAlso objDT.Rows.Count = 1 Then
                    Dim dtRow As DataRow = objDT.Rows(0)
                    Response.ContentType = "application/x-unknown"
                    Response.AddHeader("Content-Disposition", "attachment;filename=" + dtRow("Filename").ToString())
                    Response.BinaryWrite(dtRow("FileAttachment"))
                Else
                    lblFileNotFound.Visible = True
                End If
            Catch Exc As Exception
                lblFileNotFound.Visible = True
                EventTracker.AddNoEmail(ProgramName & " - AttachAttachment", Exc.ToString(), SessionManager.UserID)
            End Try
        End Sub
#End Region

    End Class
End Namespace
