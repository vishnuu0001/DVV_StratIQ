#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class TeamBusinessUnitChange1
        Inherits ApplicationBase

#Region " Members"
        Private Shared ReadOnly FormName As String = "Team Business Unit Change"
        Private Shared ReadOnly ProgramName As String = "TeamBusinessUnitChange1"

        Private Enum GridColumns As Integer
            TeamID = 0
            Team
            TeamName
            Site
            PillarAbbrev
            BusinessAreaAbbrev
            BusinessUnitAbbrev
            DeptNumber
            TeamStartDate
            TeamFinishDate
            Duration
            TeamStatusDescription
            TeamType
            ChangeTeam
        End Enum
#End Region

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Master.IconImage = Request.ApplicationPath & "/images/boss.gif"
            Master.HeaderMessage = FormName
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnExit.UniqueID + "'),window.event)")

            If Not Page.IsPostBack Then
                LoadFilterDropDowns()
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
        End Sub
        Protected Sub btnApply_Click(sender As Object, e As System.EventArgs) Handles btnApply.Click
            BindGrid()
        End Sub
        Protected Sub btnExit_Click(sender As Object, e As System.EventArgs) Handles btnExit.Click
            RemoveCurrentProgramandGoBack()
        End Sub
        Protected Sub btnProcess_Click(sender As Object, e As System.EventArgs) Handles btnProcess.Click
            Dim strTeam As String = ""

            For iRow As Integer = 0 To grdTeam.Rows.Count - 1
                If TypeOf grdTeam.Rows(iRow).Cells(GridColumns.ChangeTeam).Controls(1) Is CheckBox Then
                    If DirectCast(grdTeam.Rows(iRow).Cells(GridColumns.ChangeTeam).Controls(1), CheckBox).Checked Then
                        If strTeam.Trim.Length > 0 Then
                            strTeam += ","
                        End If

                        strTeam += grdTeam.DataKeys(iRow)("TeamID").ToString
                    End If
                End If
            Next

            If strTeam.Trim.Length > 0 Then
                SessionManager.SelectedValue = strTeam
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamBusinessUnitChange2"), False)
            End If
        End Sub
#End Region

#Region " Methods"
        Private Sub LoadFilterDropDowns()
            Try
                BusinessUnitMaster.SelectBusinessUnitMasterAbbrevList(ddlBusinessUnit)
                ddlBusinessUnit.Items.Insert(0, "")
            Catch ex As Exception

            End Try
        End Sub
        Private Sub BindGrid()
            Try
                Dim iBusinessUnitID As Integer = -1
                If ddlBusinessUnit.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlBusinessUnit.SelectedItem.Value) Then
                    iBusinessUnitID = ddlBusinessUnit.SelectedItem.Value
                End If

                Dim objDT As DataTable = Teams.SelectTeamsByBusinessUnitID(iBusinessUnitID)

                grdTeam.DataSource = objDT
                grdTeam.DataBind()
            Catch ex As Exception
            End Try
        End Sub
#End Region

    End Class
End Namespace
