#Region " Imports"
Option Explicit On
Imports System.IO
Imports System.Data.SqlClient
Imports WebApp.APlus.UI
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class OEEReports1
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "OEE Reports"
        Private Shared ReadOnly ProgramName As String = "OEEReports1"
#End Region

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, ProgramName, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Master.IconImage = Request.ApplicationPath & "/images/document.gif"
            Master.HeaderMessage = FormName
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" & btnExit.UniqueID & "'),window.event)")

            If Not SessionManager.AllowMaintenanceEdit Then
                dgOEEReports.Columns(dgOEEReports.Columns.Count - 2).Visible = False
            End If
            If Not SessionManager.AllowMaintenanceDelete Then
                dgOEEReports.Columns(dgOEEReports.Columns.Count - 1).Visible = False
            End If
            If Not SessionManager.AllowMaintenanceAdd Then
                btnNew.Visible = False
            End If

            If Not Page.IsPostBack Then
                dgOEEReports.DataSource = OEEReports.SelectOEEReports(SessionManager.WorkingSiteID)
                dgOEEReports.DataBind()
            End If
        End Sub
        Private Sub dgOEEReports_ItemDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.DataGridItemEventArgs) Handles dgOEEReports.ItemDataBound
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If e.Item.ItemType = ListItemType.Item Or e.Item.ItemType = ListItemType.AlternatingItem Then
                CType(e.Item.Cells(1).FindControl("lbtnReport"), LinkButton).Attributes.Add("onclick", "javascript:LaunchExplorer(" & Chr(39) & (DataBinder.Eval(e.Item.DataItem, "URL")).Replace("\", "\\") & Chr(39) & ");")
            End If
        End Sub
        Private Sub dgOEEReports_ItemCommand(ByVal source As Object, ByVal e As System.Web.UI.WebControls.DataGridCommandEventArgs) Handles dgOEEReports.ItemCommand
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If e.CommandName = "DeleteRow" Or e.CommandName = "EditRow" Then
                SessionManager.OEEReportsMode = e.CommandName
                Dim dg As DataGrid = CType(source, DataGrid)
                SessionManager.SelectedValue = dg.Items(e.Item.ItemIndex).Cells(0).Text
                SessionManager.SelectedValue1 = dg.Items(e.Item.ItemIndex).Cells(1).Text
                SessionManager.SelectedValue2 = dg.Items(e.Item.ItemIndex).Cells(2).Text
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("OEEReports2"), False)
            End If
        End Sub

        Private Sub btnExit_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnExit.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(SessionManager.CurrentMenuProgram), False)
        End Sub

        Private Sub btnNew_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnNew.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.OEEReportsMode = "AddRow"
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("OEEReports2"), False)
        End Sub
#End Region

    End Class
End Namespace
