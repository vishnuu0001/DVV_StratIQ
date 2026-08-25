#Region " Imports"
Imports System.IO
Imports System.Data
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.DataAccess.Custom
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class DashboardMenu
        Inherits ApplicationBase

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            SessionManager.CurrentMenuProgram = "DashBoardMenu"
            Master.IconImage = Request.ApplicationPath + "/images/home.gif"
            Master.HeaderMessage = GetTranslationString("mydashboard", "My Dashboard")
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/" & SessionManager.CulturePref & "/DataEntry.js")

            If Not Page.IsPostBack Then
                LoadDashboard()
            End If
        End Sub
        Protected Sub btnActions_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnActions.Click
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("MyActions"), False)
        End Sub
#End Region

#Region "Custom Methods"
        Private Sub LoadDashboard()
            Try
                Dim iSiteID As Integer = SessionManager.WorkingSiteID
                If iSiteID = 0 Then
                    iSiteID = UserMaster.GetUserSite(SessionManager.UserID)
                End If
                Dim objDT As DataTable = Nothing
                Dim bActions As Boolean = False

                objDT = TeamActionPlan.SelectMyActionItems(SessionManager.UserID, 0)
                If objDT IsNot Nothing AndAlso objDT.Rows.Count > 0 Then
                    lblTeamActions.Visible = True
                    bActions = True
                End If
                objDT = AnomalyMaster.SelectMyDashboardAnomalies(SessionManager.UserID)
                If objDT IsNot Nothing AndAlso objDT.Rows.Count > 0 Then
                    lblAnomalyActions.Visible = True
                    bActions = True
                End If
                If bActions Then
                    lblNoActions.Visible = False
                End If

                objDT = TeamMembership.SelectAPlusParticipationChart(iSiteID)
                chtParticipation.Series("Series1").Label = "#VALY (#PERCENT{P0})"
                chtParticipation.Series("Series1").LegendText = "#AXISLABEL"
                chtParticipation.DataSource = objDT
                chtParticipation.DataBind()

                objDT = TeamMembership.SelectAPlusNewParticipationChart(iSiteID)
                chtNewParticipation.Series("Series1").Label = "#VALY (#PERCENT{P0})"
                chtNewParticipation.Series("Series1").LegendText = "#AXISLABEL"
                chtNewParticipation.DataSource = objDT
                chtNewParticipation.DataBind()

                objDT = Teams.SelectDashboardTeams(SessionManager.UserID, iSiteID)
                chtTeams.Series("Series1").Label = "#VALY (#PERCENT{P0})"
                chtTeams.Series("Series1").LegendText = "#AXISLABEL"
                chtTeams.DataSource = objDT
                chtTeams.DataBind()

            Catch ex As Exception

            End Try
        End Sub
#End Region

    End Class
End Namespace
