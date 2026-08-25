#Region " Imports"
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.CustomControls
    Public Class ApplicationErrorControl
        Inherits System.Web.UI.WebControls.Panel
        Implements INamingContainer

#Region " Lookup Error Messages"
        Public Enum ApplicationErrorMessages
            DeleteError
            InsertError
            UpdateError
            DuplicateError
            CustomError
            LoadError
        End Enum

        Public Function LookupErrorMessages(ByVal MessageType As ApplicationErrorMessages) As String
            Select Case MessageType
                Case ApplicationErrorMessages.DeleteError
                    Return "Cannot Delete"
                    LookupErrorMessages = "Cannot Delete"
                Case ApplicationErrorMessages.InsertError
                    LookupErrorMessages = "Cannot Insert"
                Case ApplicationErrorMessages.UpdateError
                    LookupErrorMessages = "Cannot Update"
                Case ApplicationErrorMessages.DuplicateError
                    LookupErrorMessages = " already exists"
                Case ApplicationErrorMessages.LoadError
                    LookupErrorMessages = "Cannot Load Information"
                Case Else
                    LookupErrorMessages = ""
            End Select
        End Function
#End Region

#Region " Private Variables and Properties"
        Protected WithEvents _lblMessage As New Label
        Protected _imgError As New Image
        Private _Message As String = String.Empty
        Protected WithEvents _table As New Table

        Public Overrides ReadOnly Property Controls() As ControlCollection
            Get
                EnsureChildControls()
                Return MyBase.Controls
            End Get
        End Property
#End Region

#Region " Event Handlers"
        Public Sub New()
            Me.ID = "ApplicationErrorControl"
            Me.Width = New Unit(100, UnitType.Percentage)
            Me.Visible = False
        End Sub

        Private Sub ApplicationErrorControl_Load(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.Load
            If _Message.Trim.Length = 0 Then
                _imgError.Visible = False
                _lblMessage.Visible = False
            End If
        End Sub

        Protected Overrides Sub Finalize()
            MyBase.Finalize()
        End Sub

        Protected Overrides Sub CreateChildControls()
            Dim tRow As New TableRow()
            Dim tCell As TableCell
            _imgError.ImageUrl = "~/images/error.gif"
            _imgError.Visible = False
            tCell = New TableCell
            tCell.CssClass = "ErrControl_Cell1"
            tCell.Controls.Add(_imgError)
            tRow.Cells.Add(tCell)
            _lblMessage.ID = "lblMessage"
            _lblMessage.EnableViewState = False
            _lblMessage.CssClass = "Label_ErrorControl"
            _lblMessage.Visible = False
            tCell = New TableCell
            tCell.CssClass = "ErrControl_Cell2"
            tCell.Controls.Add(_lblMessage)
            tRow.Cells.Add(tCell)
            _table.Rows.Add(tRow)
            _table.CssClass = "Table_ErrorControl"
            Me.Controls.Add(_table)
        End Sub
#End Region

#Region " Custom Methods"
        Public Sub DisplayErrors(ByVal passEventName As String, _
                                 ByVal passError As Exception, _
                                 ByVal passUserID As String, _
                                 ByVal passErrorType As ApplicationErrorMessages)
            EventTracker.AddNoEmail(passEventName, passError.ToString, passUserID)
            _Message = passError.Message
            DisplayError()
        End Sub
        Public Sub DisplayManualErrors(ByVal passEventName As String, _
                                 ByVal passError As String, _
                                 ByVal passUserID As String)
            EventTracker.AddNoEmail(passEventName, passError, passUserID)
            _Message = passError.Trim()
            DisplayError()
        End Sub
        Private Sub DisplayError()
            _imgError.Visible = True
            _lblMessage.Visible = True
            _lblMessage.Text = _Message

            Me.Visible = True
        End Sub
        Public Sub DisplayError(ByVal passMessage As String)
            _Message = passMessage
            _imgError.Visible = True
            _lblMessage.Visible = True
            _lblMessage.Text = _Message
            Me.Visible = True
        End Sub
        Public Sub WriteErrors(ByVal passEventName As String, ByVal passError As Exception, ByVal passUserID As String)
            EventTracker.AddNoEmail(passEventName, passError.ToString, passUserID)
        End Sub
        Public Sub WriteErrors(ByVal passEventName As String, ByVal passMessage As String, ByVal passUserID As String)
            EventTracker.AddNoEmail(passEventName, passMessage, passUserID)
        End Sub
#End Region

    End Class
End Namespace

