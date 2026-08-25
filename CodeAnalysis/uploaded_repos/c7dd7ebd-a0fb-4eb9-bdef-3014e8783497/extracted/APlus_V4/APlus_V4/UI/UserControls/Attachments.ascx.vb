#Region "Imports"
Imports System.IO
Imports System.Configuration
Imports System.Data
#End Region

Namespace WebApp.APlus.UI.UserControls
    Partial Class Attachments
        Inherits System.Web.UI.UserControl

#Region "  Private Variables which are exposed through Public Properties"
        Private _DataTable As DataTable
        Private _AllowEdit As Boolean = True
#End Region

#Region " Public Properties"
        Public Property DataSource() As DataTable
            Get
                Return _DataTable
            End Get
            Set(ByVal Value As DataTable)
                _DataTable = Value
            End Set
        End Property
        Public Property AllowEdit() As Boolean
            Get
                Return _AllowEdit
            End Get
            Set(ByVal value As Boolean)
                _AllowEdit = value
            End Set
        End Property

        Public ReadOnly Property PostedFile() As System.Web.HttpPostedFile
            Get
                Return fil.PostedFile
            End Get
        End Property
#End Region

#Region " Public Events exposed by the control"
        Public Event AttachClick()
        Public Event AttachError(ByVal strErrorMessage As String)
        Public Event DeleteAttachment(ByVal strFileName As String)
#End Region

#Region " Public Methods"
        Public Overrides Sub DataBind()
            gvAttachments.DataSource = _DataTable
            gvAttachments.DataBind()
        End Sub
        Public Overloads Sub Attach(ByVal SaveInServerFolder As String)
            'Check whether we have a directory for the file, if not create one
            If Not Directory.Exists(SaveInServerFolder) Then
                Directory.CreateDirectory(SaveInServerFolder)
            End If

            'Attachment will be saved under same name as the uploaded file 
            Dim strAttachmentFilePath As String = _
            SaveInServerFolder & "\" & Path.GetFileName(Me.PostedFile.FileName)

            'Save the uploaded file in the appropriate meeting folder
            Me.PostedFile.SaveAs(strAttachmentFilePath)
        End Sub
        Public Overloads Sub Attach(ByVal SaveInServerFolder As String, ByVal newFileName As String)
            'Check whether we have a directory for the file, if not create one
            If Not Directory.Exists(SaveInServerFolder) Then
                Directory.CreateDirectory(SaveInServerFolder)
            End If

            'Attachment will be saved under same name as the uploaded file 
            Dim strAttachmentFilePath As String = _
            SaveInServerFolder & "\" & Path.GetFileName(newFileName)

            'Save the uploaded file in the appropriate meeting folder
            Me.PostedFile.SaveAs(strAttachmentFilePath)
        End Sub
        Public Sub Detach(ByVal DeleteInServerFolder As String, ByVal passFileName As String)
            'Check whether we have a directory, if then delete
            If Directory.Exists(DeleteInServerFolder) Then
                'Attachment will be saved under same name as the uploaded file 
                Dim strAttachmentFilePath As String = (DeleteInServerFolder & "\" & passFileName).Replace("\\", "\")

                Try
                    File.Delete(strAttachmentFilePath)
                Catch ex As Exception
                    Throw New Exception(ex.ToString)
                End Try
            End If
        End Sub
#End Region

#Region " Event Handlers"
        Protected Sub Page_Load(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.Load
            gvAttachments.EmptyDataText = GetTranslationString("No Attachments")

            If _AllowEdit Then
                pnlOKCancel.Visible = True
                gvAttachments.Columns(1).Visible = True
            Else
                pnlOKCancel.Visible = False
                gvAttachments.Columns(1).Visible = False
            End If
        End Sub
        Protected Sub gvAttachments_RowDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewRowEventArgs) Handles gvAttachments.RowDataBound
            If e.Row.RowType = DataControlRowType.DataRow Then
                Dim objButton As ImageButton = DirectCast(e.Row.FindControl("btnDelete"), ImageButton)

                objButton.CommandArgument = e.Row.RowIndex.ToString
                objButton.Attributes.Add("onclick", "return confirm('Click OK to Delete this Attachment.');")
            End If
        End Sub
        Protected Sub gvAttachments_RowCommand(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewCommandEventArgs) Handles gvAttachments.RowCommand
            Dim strfile As String = CType(gvAttachments.Rows(CInt(e.CommandArgument)).FindControl("hlAttachment"), HyperLink).Text

            RaiseEvent DeleteAttachment(strfile)
        End Sub
        Private Sub btnAttach_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnAttach.Click
            If fil.PostedFile.FileName.Trim <> "" Then
                'check the file size
                If fil.PostedFile.ContentLength > ConfigurationManager.AppSettings("MaxUploadFileSize") Then
                    RaiseEvent AttachError("File Size must be no greater than 1024K")

                    Return
                End If

                RaiseEvent AttachClick()
            End If
        End Sub
#End Region

    End Class
End Namespace

