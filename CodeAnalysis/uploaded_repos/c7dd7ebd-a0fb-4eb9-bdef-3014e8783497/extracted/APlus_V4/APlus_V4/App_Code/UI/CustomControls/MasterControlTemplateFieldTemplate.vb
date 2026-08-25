#Region " Imports"
#End Region

Namespace WebApp.APlus.UI.CustomControls
    Public Class ImageFieldTemplate
        Implements ITemplate

        Private _ImageID As String = ""
        Private _AltText As String = ""

        Public Sub New(ByVal passImageID As String, ByVal passAltText As String)
            _ImageID = passImageID
            _AltText = passAltText
        End Sub

        Public Sub InstantiateIn(ByVal container As System.Web.UI.Control) Implements System.Web.UI.ITemplate.InstantiateIn
            Dim objI As New Image
            objI.ID = _ImageID
            objI.AlternateText = _AltText
            objI.Visible = False

            container.Controls.Add(objI)
        End Sub
    End Class
    Public Class CheckBoxFieldTemplate
        Implements ITemplate

        Private _ControlID As String = ""

        Public Sub New(ByVal passCheckboxID As String)
            _ControlID = passCheckboxID
        End Sub

        Public Sub InstantiateIn(ByVal container As System.Web.UI.Control) Implements System.Web.UI.ITemplate.InstantiateIn
            Dim objCTL As New CheckBox
            objCTL.ID = _ControlID

            container.Controls.Add(objCTL)
        End Sub
    End Class
End Namespace
