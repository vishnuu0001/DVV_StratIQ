#Region " Imports"
Imports System.IO
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper
Imports WebApp.APlus.UI
Imports WebApp.APlus.UI.CustomControls
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class TeamOPIReports6
        Inherits PrinterFriendlyBase

#Region " Event Hanlders"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "TeamOPIReports6", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            'Put user code to initialize the page here
            lblOPI.Text = SessionManager.SelectedOPI
            lblTeam.Text = SessionManager.SelectedTeam
            lblTeamName.Text = SessionManager.SelectedTeamName

            TeamOPIGraph1.ChartWidth = 950
            TeamOPIGraph1.ChartHeight = 550
            TeamOPIGraph1.ChartTitle = ""
            TeamOPIGraph1.ChartTeamID = SessionManager.SelectedTeamID
            TeamOPIGraph1.ChartOPI = SessionManager.SelectedOPI
            TeamOPIGraph1.OPIUOM = SessionManager.OPIUOM
            TeamOPIGraph1.WhiteChart = True
            TeamOPIGraph1.DetailChart = True
            TeamOPIGraph1.ChartType = "AllDetails"
        End Sub
#End Region

    End Class
End Namespace
