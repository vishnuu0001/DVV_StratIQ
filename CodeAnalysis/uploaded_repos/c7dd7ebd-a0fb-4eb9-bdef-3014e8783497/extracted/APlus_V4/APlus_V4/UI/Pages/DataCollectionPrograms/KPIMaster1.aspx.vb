#Region " Imports"
Imports System.IO
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class KPIMaster1
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "KPI Maintenance"
        Private Shared ReadOnly ProgramName As String = "KPIMaster1"
#End Region

#Region " Event Handlers"
        Protected Sub KPIMaster1_PreInit(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.PreInit
            AddHandler Master.RefreshWorkingSite, AddressOf RefreshWorkingSite
        End Sub
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
            Master.HeaderMessage = GetTranslationString(FormName, FormName)
            Master.ProgramName = ProgramName
            Master.ShowWorkingSiteDropDown = True

            Master.AddBodyAttribute("onkeydown", "TrapEscKey(document.getElementById('" + MasterControl1.ExitButtonID + "'),window.event)")
            Master.AddBodyAttribute("onkeydown", "TrapEnterKey(document.getElementById('" + MasterControl1.AddButtonID + "'),window.event)")

            Dim objCol As New ButtonField
            objCol.ButtonType = ButtonType.Link
            objCol.Text = "KPI Values"
            objCol.CommandName = "KPIValues"
            MasterControl1.GridColumns.Add(objCol)

            If Not Page.IsPostBack Then
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
        Protected Sub MasterControl1_onRowDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewRowEventArgs) Handles MasterControl1.onRowDataBound
            If e.Row.RowType = DataControlRowType.DataRow Then
                If IsNumeric(MasterControl1.MasterControlGrid.DataKeys(e.Row.RowIndex)("AllowEdit").ToString) AndAlso Convert.ToInt16(MasterControl1.MasterControlGrid.DataKeys(e.Row.RowIndex)("AllowEdit").ToString) <> 1 Then
                    Try
                        CType(e.Row.Cells(22).Controls(0), LinkButton).Enabled = False
                        CType(e.Row.Cells(23).Controls(0), LinkButton).Enabled = False
                    Catch ex As Exception
                        'do nothing
                    End Try
                End If
            End If
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

            LastPixelPositionUpdate(ProgramName, Master.CurrentPixelPosition)

            Select Case e.CommandName
                Case "ViewRow", "EditRow", "DeleteRow"
                    SessionManager.SelectedValueKPIID = MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("KPIID").ToString
                    SessionManager.KPIMasterMode = e.CommandName

                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPIMaster2"), False)
                Case "KPIValues"
                    SessionManager.SelectedValueKPIID = MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("KPIID").ToString

                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPIValues1"), False)
            End Select
        End Sub
        Protected Sub btnApplyFilter_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnApplyFilter.Click
            Dim cookie As New HttpCookie("KPIMasterFilter")
            cookie.Expires = Now.AddDays(Convert.ToInt16(ConfigurationManager.AppSettings("CookieExpirationTime")))

            If Not String.IsNullOrEmpty(txtSearch.Text.Trim) Then
                cookie.Values("SearchText") = txtSearch.Text
            Else
                cookie.Values.Remove("SearchText")
            End If

            cookie.Values("Active") = chkActive.Checked.ToString

            Response.Cookies.Add(cookie)

            BindGrid()
        End Sub
        Protected Sub btnClearFilter_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnClearFilter.Click
            Response.Cookies("KPIMasterFilter").Expires = Now
            txtSearch.Text = String.Empty
            chkActive.Checked = False

            BindGrid()
        End Sub
        Private Sub RefreshWorkingSite()
            MasterControl1.StoredProcedureParams.Clear()

            BindGrid()
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub ApplyFiltersFromCookie()
            If Request.Cookies("KPIMasterFilter") IsNot Nothing Then
                Dim cookie As HttpCookie = Request.Cookies("KPIMasterFilter")

                If cookie.Values("SearchText") IsNot Nothing AndAlso Not String.IsNullOrEmpty(cookie.Values("SearchText")) Then
                    txtSearch.Text = cookie.Values("SearchText")
                End If

                If cookie.Values("Active") IsNot Nothing AndAlso Convert.ToBoolean(cookie.Values("Active")) = True Then
                    chkActive.Checked = True
                End If
            Else
                txtSearch.Text = String.Empty
                chkActive.Checked = False
            End If
        End Sub
        Private Sub BindGrid()
            MasterControl1.StoredProcedureParams.Clear()

            MasterControl1.StoredProcedureParams.Add("@UserID", SessionManager.UserID)
            MasterControl1.StoredProcedureParams.Add("@SiteID", SessionManager.WorkingSiteID)
            If Not String.IsNullOrEmpty(txtSearch.Text.Trim) Then
                MasterControl1.StoredProcedureParams.Add("@Search", txtSearch.Text.Trim)
            End If
            If chkActive.Checked Then
                MasterControl1.StoredProcedureParams.Add("@ShowInactive", True)
            End If

            MasterControl1.DataBind(True)
        End Sub
#End Region

    End Class
End Namespace
