'@ -----------------------------------------------------------------------------
'@ Project	 : APlus
'@ Class	 : Template.UI.Controls.Custom.LinkColumnTemplate
'@ 
'@ -----------------------------------------------------------------------------
'@ <summary>
'@
'@ allows programmer to edit linkbutton controls within a buttoncolumn
'@ in a data grid or mastercontrol
'@
'@ </summary>
'@ <history>
'@ Copied from Greenbay project so as to make life easier for me
'@  Lawrence F. Sullivan    5-4-07  converted to VS.NET 2005
'@ </history>
'@ -----------------------------------------------------------------------------

#Region " Imports "

Imports Microsoft.VisualBasic

#End Region

Namespace WebApp.APlus.UI.CustomControls

    Public Class LinkColumnTemplate
        Implements ITemplate

        Private _ButtonID As String = ""
        Private _ButtonCommand As String = ""
        Private _ButtonText As String = ""

        Public Sub New(ByVal passButtonID As String, ByVal passButtonCommand As String, ByVal passButtonText As String)
            _ButtonID = passButtonID
            _ButtonCommand = passButtonCommand
            _ButtonText = passButtonText
        End Sub

        Public Sub InstantiateIn(ByVal container As System.Web.UI.Control) Implements System.Web.UI.ITemplate.InstantiateIn

            Dim objL As New LinkButton
            objL.ID = _ButtonID
            objL.CommandName = _ButtonCommand
            objL.Text = _ButtonText
            objL.CausesValidation = False

            container.Controls.Add(objL)
        End Sub

    End Class

End Namespace

