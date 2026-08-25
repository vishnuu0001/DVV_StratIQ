#Region " Imports"
Imports System.IO
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class KPIReportCategoryMaster1
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "KPI Group"
        Private Shared ReadOnly ProgramName As String = "KPIReportCategoryMaster1"
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

            Master.IconImage = Request.ApplicationPath & "/images/boss.gif"
            Master.HeaderMessage = FormName
            Master.AddBodyAttribute("onkeydown", "TrapEscKey(document.getElementById('" + MasterControl1.ExitButtonID + "'),window.event)")
            Master.AddBodyAttribute("onkeydown", "TrapEnterKey(document.getElementById('" + MasterControl1.AddButtonID + "'),window.event)")

            If Not Page.IsPostBack Then
                LoadFilterDropDowns()
                ApplyFiltersFromCookie()
            End If
        End Sub
        Protected Sub Timer1_Tick(ByVal sender As Object, ByVal e As System.EventArgs) Handles Timer1.Tick
            Timer1.Enabled = False
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            BindGrid()
            Master.MasterScriptManager.RegisterPostBackControl(MasterControl1.ExportButton)
        End Sub
        Protected Sub MasterControl1_onRowCommand(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewCommandEventArgs) Handles MasterControl1.onRowCommand
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", e.CommandName)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Select Case e.CommandName
                Case "ViewRow", "EditRow", "DeleteRow"
                    SessionManager.SelectedValue = MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("KPIReportCategoryID").ToString
                    SessionManager.Mode = e.CommandName

                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPIReportCategoryMaster2"), False)
            End Select
        End Sub
        Protected Sub btnApplyFilter_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnApplyFilter.Click
            Dim cookie As New HttpCookie("KPIReportFilter")
            cookie.Expires = Now.AddDays(Convert.ToInt16(ConfigurationManager.AppSettings("CookieExpirationTime")))

            If ddlSite.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlSite.SelectedItem.Value) Then
                cookie.Values("SiteID") = ddlSite.SelectedItem.Value.ToString
            Else
                cookie.Values.Remove("SiteID")
            End If

            If ddlReportGroup.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlReportGroup.SelectedItem.Value) Then
                cookie.Values("ReportGroupID") = ddlReportGroup.SelectedItem.Value.ToString
            Else
                cookie.Values.Remove("ReportGroupID")
            End If

            Response.Cookies.Add(cookie)

            BindGrid()
        End Sub
        Protected Sub btnClearFilter_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnClearFilter.Click
            Response.Cookies("KPIReportFilter").Expires = Now

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPIReportCategoryMaster1"), False)
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadFilterDropDowns()
            Try
                SiteMaster.SelectSiteMasterActiveList(ddlSite)
                ddlSite.Items.Insert(0, "")

                KPIReportGroupMaster.SelectKPIReportGroupMasterList(ddlReportGroup)
                ddlReportGroup.Items.Insert(0, "")
            Catch ex As Exception

            End Try
        End Sub
        Private Sub ApplyFiltersFromCookie()
            Dim objItem As ListItem

            If Request.Cookies("KPIReportFilter") IsNot Nothing Then
                Dim cookie As HttpCookie = Request.Cookies("KPIReportFilter")

                If cookie.Values("SiteID") IsNot Nothing AndAlso IsNumeric(cookie.Values("SiteID")) Then
                    objItem = ddlSite.Items.FindByValue(cookie.Values("SiteID"))
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                    End If
                End If

                If cookie.Values("ReportGroupID") IsNot Nothing AndAlso IsNumeric(cookie.Values("ReportGroupID")) Then
                    objItem = ddlReportGroup.Items.FindByValue(cookie.Values("ReportGroupID"))
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                    End If
                End If

            End If
        End Sub
        Private Sub BindGrid()
            If ddlSite.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlSite.SelectedItem.Value) Then
                MasterControl1.StoredProcedureParams.Add("@SiteID", ddlSite.SelectedItem.Value.ToString)
            End If

            If ddlReportGroup.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlReportGroup.SelectedItem.Value) Then
                MasterControl1.StoredProcedureParams.Add("@KPIReportGroupID", ddlReportGroup.SelectedItem.Value)
            End If

            MasterControl1.DataBind(True)
        End Sub
#End Region

    End Class
End Namespace
