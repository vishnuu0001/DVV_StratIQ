#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class KPIBusinessUnitChange1
        Inherits ApplicationBase

#Region " Members"
        Private Shared ReadOnly FormName As String = "KPI Business Unit Change"
        Private Shared ReadOnly ProgramName As String = "KPIBusinessUnitChange1"

        Private Enum GridColumns As Integer
            KPIID = 0
            KPI
            KPIOther
            UOM
            TeamCategory
            SortSequence
            Site
            PillarAbbrev
            BusinessAreaAbbrev
            BusinessUnitAbbrev
            AreaAbbrev
            ResponsibleUser
            DailyKPI
            Active
            ChangeKPI
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
            Dim strKPI As String = ""

            For iRow As Integer = 0 To grdKPI.Rows.Count - 1
                If TypeOf grdKPI.Rows(iRow).Cells(GridColumns.ChangeKPI).Controls(1) Is CheckBox Then
                    If DirectCast(grdKPI.Rows(iRow).Cells(GridColumns.ChangeKPI).Controls(1), CheckBox).Checked Then
                        If strKPI.Trim.Length > 0 Then
                            strKPI += ","
                        End If

                        strKPI += grdKPI.DataKeys(iRow)("KPIID").ToString
                    End If
                End If
            Next

            If strKPI.Trim.Length > 0 Then
                SessionManager.SelectedValue = strKPI
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPIBusinessUnitChange2"), False)
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

                Dim objDT As DataTable = KPIMaster.SelectKPIMasterByBusinessUnitID(iBusinessUnitID)

                grdKPI.DataSource = objDT
                grdKPI.DataBind()
            Catch ex As Exception
            End Try
        End Sub
#End Region

    End Class
End Namespace
