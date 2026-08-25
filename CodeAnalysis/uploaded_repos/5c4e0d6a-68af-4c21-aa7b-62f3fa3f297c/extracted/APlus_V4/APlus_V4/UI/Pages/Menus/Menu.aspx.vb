#Region " Imports"
Imports System.IO
#End Region

Namespace WebApp.APlus.UI.Pages
    Public Class Menu
        Inherits ApplicationBase

        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Master.IconImage = Request.ApplicationPath + "/images/home.gif"
            Master.HeaderMessage = MenuControl1.MenuTitle
            Master.AddBodyAttribute("onkeydown", "TrapKeysForMenu(window.event)")
            Master.ShowWorkingSiteDropDown = True

            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/" & SessionManager.CulturePref & "/DataEntry.js")
        End Sub
    End Class
End Namespace
