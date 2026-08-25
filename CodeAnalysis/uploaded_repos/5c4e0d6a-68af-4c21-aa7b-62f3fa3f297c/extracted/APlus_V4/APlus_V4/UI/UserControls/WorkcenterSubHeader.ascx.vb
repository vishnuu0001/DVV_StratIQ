Namespace WebApp.APlus.UI.UserControls
    Partial Class WorkcenterSubHeader
        Inherits System.Web.UI.UserControl

        Protected Sub WorkcenterSubHeader_Load(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.Load
            If SessionManager.SelectedWorkCenterID > 0 AndAlso SessionManager.SelectedWorkCenter.Trim.Length > 0 Then
                lblSelectedWorkcenter.Text = SessionManager.SelectedWorkCenter.ToString.Trim
            Else
                Me.Visible = False
            End If
        End Sub
    End Class
End Namespace
