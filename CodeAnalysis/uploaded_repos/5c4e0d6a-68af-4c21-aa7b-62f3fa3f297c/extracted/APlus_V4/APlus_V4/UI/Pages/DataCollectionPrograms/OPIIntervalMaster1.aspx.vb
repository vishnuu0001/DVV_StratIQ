#Region " Imports"
Option Explicit On
Imports System.IO
Imports System.Data.SqlClient
Imports WebApp.APlus.UI
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class OPIIntervalMaster1
        Inherits ApplicationBase

#Region " Constants"
        Private Shared ReadOnly FormName As String = "OPI Interval Master"
        Private Shared ReadOnly ProgramName As String = "OPIIntervalMaster1"
#End Region

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Master.IconImage = Request.ApplicationPath & "/images/padlock.gif"
            Master.HeaderMessage = FormName
            Master.AddBodyAttribute("onkeydown", "TrapEscKey(document.getElementById('" + MasterControl1.ExitButtonID + "'),window.event)")
            Master.AddBodyAttribute("onkeydown", "TrapEnterKey(document.getElementById('" + MasterControl1.AddButtonID + "'),window.event)")
        End Sub
        Protected Sub Timer1_Tick(ByVal sender As Object, ByVal e As System.EventArgs) Handles Timer1.Tick
            Timer1.Enabled = False
            MasterControl1.DataBind()
        End Sub
        Protected Overrides Sub Finalize()
            MyBase.Finalize()
        End Sub
#End Region

    End Class
End Namespace