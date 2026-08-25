#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports System.Collections.Generic

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class AnomalyActionsSummary
        Inherits ApplicationBase

#Region " Private Variables"
        Private Shared ReadOnly FormName As String = "Anomaly Actions Summary"
        Private Shared ReadOnly ProgramName As String = "AnomalyActionsSummary"
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnExit.UniqueID + "'),window.event)")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnRunReport.UniqueID + "'),window.event)")
        End Sub
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

            Master.HeaderMessage = FormName
            Master.IconImage = Request.ApplicationPath + "/images/chart.png"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                LoadDropDownLists()

                Dim objItem As ListItem = ddlSite.Items.FindByValue(SessionManager.WorkingSiteID)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                    ddlSite_SelectedIndexChanged(Nothing, Nothing)
                End If
            End If
        End Sub
        Protected Sub ddlSite_SelectedIndexChanged(ByVal sender As Object, ByVal e As System.EventArgs) Handles ddlSite.SelectedIndexChanged
            ddlAreaGroup.Items.Clear()

            If ddlSite.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlSite.SelectedItem.Value) Then
                AreaGroupMaster.GetAreaGroupMasterBaseList(ddlAreaGroup, ddlSite.SelectedItem.Value)
            End If

            ddlAreaGroup.Items.Insert(0, "")
        End Sub
        Protected Sub btnRunReport_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnRunReport.Click
            Dim strURL As String = ""

            strURL = Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & "UI/Pages/DataCollectionPrograms/WebReportPrintPreview.aspx"
            strURL += "?ReportKey=AnomalyActionsSummary"
            If ddlSite.SelectedItem IsNot Nothing AndAlso ddlSite.SelectedItem.ToString.Trim.Length > 0 Then
                strURL += "&ReportParams=SiteID=" & ddlSite.SelectedItem.Value.ToString
            Else
                Return
            End If

            If ddlAreaGroup.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlAreaGroup.SelectedItem.Value) Then
                strURL += "|AreaGroupID=" & ddlAreaGroup.SelectedItem.Value.ToString
            Else
                strURL += "|AreaGroupID=0"
            End If

            If Not String.IsNullOrEmpty(strURL) Then
                Dim strScript As String = "window.open('" & strURL & "', '_blank');"

                ClientScript.RegisterStartupScript(Me.GetType, "ReportScript", "<script language='javascript'>" & strScript & "</script>")
            End If

        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            RemoveCurrentProgramandGoBack()
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadDropDownLists()
            Try
                SiteMaster.SelectSiteMasterActiveList(ddlSite)
                ddlSite.Items.Insert(0, "")
            Catch ex As Exception

            End Try
        End Sub
#End Region

    End Class
End Namespace
