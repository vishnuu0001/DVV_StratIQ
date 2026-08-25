#Region "Imports"
Imports System.IO
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess
#End Region

Namespace WebApp.APlus
    Public Class PopupBase
        Inherits System.Web.UI.Page

#Region " Private Variables"
        Private html As String
#End Region

#Region " Common page load for all pages"
        Private Sub Page_Load(ByVal sender As Object, ByVal e As System.EventArgs) Handles MyBase.Load
            CheckSessionTimeout()
            DisablePageCaching()
            RegionalConversion.ValidateRegionalSettings()
        End Sub
#End Region

#Region " Page Render Functions"
        Protected Overrides Sub Render(ByVal writer As System.Web.UI.HtmlTextWriter)
            DisableF1()

            MyBase.Render(writer)
        End Sub
#End Region

#Region " Disable F1/Help Key"
        Private Sub DisableF1()
            Dim sScript As New System.Text.StringBuilder
            sScript.Append("<SCRIPT language=""javascript"">" & vbCrLf)
            sScript.Append("window.document.onhelp=openHelp;" & vbCrLf)
            sScript.Append("</SCRIPT>" & vbCrLf)
            ClientScript.RegisterStartupScript(Me.GetType, "DisableF1Script", sScript.ToString)
        End Sub

#End Region

#Region " Server Side Close"
        Public Sub ServerSideClose()
            Dim sScript As New System.Text.StringBuilder
            sScript.Append("<SCRIPT language=""javascript"">" & vbCrLf)
            sScript.Append("window.close();" & vbCrLf)
            sScript.Append("</SCRIPT>" & vbCrLf)
            ClientScript.RegisterStartupScript(Me.GetType, "ForceDefaultToScript", sScript.ToString)
        End Sub
#End Region

    End Class
End Namespace
