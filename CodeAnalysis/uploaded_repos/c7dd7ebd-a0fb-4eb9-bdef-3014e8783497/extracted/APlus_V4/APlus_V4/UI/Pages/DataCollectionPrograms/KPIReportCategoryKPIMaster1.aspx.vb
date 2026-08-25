#Region " Imports"
Imports System.IO
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class KPIReportCategoryKPIMaster1
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "KPI Group KPI Master"
        Private Shared ReadOnly ProgramName As String = "KPIReportCategoryKPIMaster1"
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
                ApplyFilters()
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
                    SessionManager.SelectedValue1 = MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("KPIID").ToString
                    SessionManager.Mode = e.CommandName

                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPIReportCategoryKPIMaster2"), False)
            End Select
        End Sub
        Protected Sub btnApplyFilter_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnApplyFilter.Click
            If ddlSite.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlSite.SelectedItem.Value) Then
                If (ddlSite.SelectedItem.Value.ToString <> SessionManager.KPIReportFilterSiteID) Then
                    SessionManager.KPIReportFilterSiteID = ddlSite.SelectedItem.Value.ToString
                    LoadReportCategoryList()
                End If
            Else
                If SessionManager.KPIReportFilterSiteID > 0 Then
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.KPIReportFilterSiteID)
                    LoadReportCategoryList()
                End If
            End If

            If ddlBusinessArea.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlBusinessArea.SelectedItem.Value) Then
                SessionManager.KPIReportFilterBusinessAreaID = ddlBusinessArea.SelectedItem.Value.ToString
            Else
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.KPIReportFilterBusinessAreaID)
            End If

            If ddlKPIGroup.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlKPIGroup.SelectedItem.Value) Then
                SessionManager.KPIReportFilterReportID = ddlKPIGroup.SelectedItem.Value.ToString
            Else
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.KPIReportFilterReportID)
            End If

            BindGrid()
        End Sub
        Protected Sub btnClearFilter_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnClearFilter.Click
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.KPIReportFilterBusinessAreaID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.KPIReportFilterReportID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.KPIReportFilterSiteID)

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPIReportCategoryKPIMaster1"), False)
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadFilterDropDowns()
            Try
                SiteMaster.SelectSiteMasterActiveList(ddlSite)
                ddlSite.Items.Insert(0, "")

                BusinessAreaMaster.GetBusinessAreaMasterAbbrevList(ddlBusinessArea)
                ddlBusinessArea.Items.Insert(0, "")
            Catch ex As Exception

            End Try
        End Sub
        Private Sub LoadReportCategoryList()
            Dim iSiteID As Integer = 0
            If ddlSite.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlSite.SelectedItem.Value) Then
                iSiteID = ddlSite.SelectedItem.Value
            End If

            ddlKPIGroup.Items.Clear()

            KPIReports.GetKPIReportCategoryMasterList(ddlKPIGroup, Convert.ToInt16(SessionManager.SelectedKPIReportGroupID), iSiteID)
            ddlKPIGroup.Items.Insert(0, "")
        End Sub
        Private Sub ApplyFilters()
            Dim objItem As ListItem

            If SessionManager.KPIReportFilterSiteID > 0 Then
                objItem = ddlSite.Items.FindByValue(SessionManager.KPIReportFilterSiteID)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                End If
            End If

            If SessionManager.KPIReportFilterBusinessAreaID > 0 Then
                objItem = ddlBusinessArea.Items.FindByValue(SessionManager.KPIReportFilterBusinessAreaID)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                End If
            End If

            LoadReportCategoryList()
            If SessionManager.KPIReportFilterReportID > 0 Then
                objItem = ddlKPIGroup.Items.FindByValue(SessionManager.KPIReportFilterReportID)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                End If
            End If
        End Sub
        Private Sub BindGrid()
            MasterControl1.StoredProcedureParams.Add("@KPIReportGroupID", SessionManager.SelectedKPIReportGroupID)

            If ddlSite.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlSite.SelectedItem.Value) Then
                MasterControl1.StoredProcedureParams.Add("@SiteID", ddlSite.SelectedItem.Value.ToString)
            End If
            If ddlBusinessArea.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlBusinessArea.SelectedItem.Value) Then
                MasterControl1.StoredProcedureParams.Add("@BusinessAreaID", ddlBusinessArea.SelectedItem.Value)
            End If
            If ddlKPIGroup.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlKPIGroup.SelectedItem.Value) Then
                MasterControl1.StoredProcedureParams.Add("@KPIReportCategoryID", ddlKPIGroup.SelectedItem.Value)
            End If

            MasterControl1.DataBind(True)
        End Sub
#End Region

    End Class
End Namespace
