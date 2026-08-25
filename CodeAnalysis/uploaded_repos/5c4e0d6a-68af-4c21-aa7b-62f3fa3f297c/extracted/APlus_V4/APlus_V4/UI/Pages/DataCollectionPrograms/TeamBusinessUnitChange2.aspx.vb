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
    Partial Class TeamBusinessUnitChange2
        Inherits ApplicationBase

#Region " Private Variables"
        Private Shared ReadOnly FormName As String = "Team Business Unit Maintenance"
        Private Shared ReadOnly ProgramName As String = "TeamBusinessUnitChange2"
        Private Shared ReadOnly DBTableName As String = "Teams"
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnExit}
            Dim OverMessageArr() As String = {"OK - Enter", "Exit"}
            Dim OutMessageArr() As String = {"", ""}
            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnExit.UniqueID + "'),window.event)")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
        End Sub
#End Region

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Master.IconImage = Request.ApplicationPath & "/images/boss.gif"
            Master.HeaderMessage = FormName

            LoadCommonJavaScripts()

            mcTeam.StoredProcedureParams.Add("@TeamList", SessionManager.SelectedValue)

            If Not Page.IsPostBack Then
                mcTeam.DataBind(True)

                LoadFilterDropDowns()

                btnOK.Attributes.Add("onclick", "return confirm('Click OK to update selected Teams.');")
            End If
        End Sub
        Private Sub btnOK_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim iTeamID As Integer = 0
            Dim iBusinessUnitID As Integer = -1
            Dim strBusinessUnit As String = String.Empty

            If ddlBusinessUnit.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlBusinessUnit.SelectedItem.Value.ToString) Then
                iBusinessUnitID = Convert.ToInt32(ddlBusinessUnit.SelectedItem.Value)
                strBusinessUnit = ddlBusinessUnit.SelectedItem.Text.Trim
            End If

            For iRow As Integer = 0 To mcTeam.Rows.Count - 1
                Try
                    iTeamID = Convert.ToInt32(mcTeam.MasterControlGrid.DataKeys(iRow)("TeamID").ToString)
                    Teams.UpdateTeamBusinessUnit(iTeamID, iBusinessUnitID)

                    RecordTransactionHistory.InsertRecordTransactionHistory("Teams", iTeamID.ToString, "Business Unit Changed: " & strBusinessUnit, SessionManager.UserID)
                Catch ex As Exception
                    Master.DisplayError(ex.Message)
                    Return
                End Try
            Next

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamBusinessUnitChange1"), False)
        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamBusinessUnitChange1"), False)
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadFilterDropDowns()
            Try
                BusinessUnitMaster.SelectBusinessUnitMasterAbbrevList(ddlBusinessUnit)
                ddlBusinessUnit.Items.Insert(0, "")
            Catch ex As Exception

            End Try
        End Sub
#End Region

    End Class
End Namespace
