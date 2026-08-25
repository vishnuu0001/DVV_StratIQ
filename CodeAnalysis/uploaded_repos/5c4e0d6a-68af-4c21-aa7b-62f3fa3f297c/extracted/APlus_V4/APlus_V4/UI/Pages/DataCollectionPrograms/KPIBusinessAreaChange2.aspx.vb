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
    Partial Class KPIBusinessAreaChange2
        Inherits ApplicationBase

#Region " Private Variables"
        Private Shared ReadOnly FormName As String = "Business Area Maintenance"
        Private Shared ReadOnly ProgramName As String = "KPIBusinessAreaChange2"
        Private Shared ReadOnly DBTableName As String = "KPIMaster"
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

            mcKPI.StoredProcedureParams.Add("@KPIList", SessionManager.SelectedValue)

            If Not Page.IsPostBack Then
                mcKPI.DataBind(True)

                LoadFilterDropDowns()

                btnOK.Attributes.Add("onclick", "return confirm('Click OK to Update selected KPIs.');")
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

            Dim iKPIID As Integer = 0
            Dim iBusinessAreaID As Integer = -1
            Dim strBusinessArea As String = String.Empty

            If ddlBusinessArea.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlBusinessArea.SelectedItem.Value.ToString) Then
                iBusinessAreaID = Convert.ToInt32(ddlBusinessArea.SelectedItem.Value)
                strBusinessArea = ddlBusinessArea.SelectedItem.Text.Trim
            End If

            For iRow As Integer = 0 To mcKPI.Rows.Count - 1
                Try
                    iKPIID = Convert.ToInt32(mcKPI.MasterControlGrid.DataKeys(iRow)("KPIID").ToString)
                    KPIMaster.UpdateKPIMasterBusinessArea(iKPIID, iBusinessAreaID)

                    RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, iKPIID.ToString, "Business Area Changed: " & strBusinessArea, SessionManager.UserID)
                Catch ex As Exception
                    Master.DisplayError(ex.Message)
                    Return
                End Try
            Next

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPIBusinessAreaChange1"), False)
        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPIBusinessAreaChange1"), False)
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadFilterDropDowns()
            Try
                BusinessAreaMaster.GetBusinessAreaMasterAbbrevList(ddlBusinessArea)
                ddlBusinessArea.Items.Insert(0, "")
            Catch ex As Exception

            End Try
        End Sub
#End Region

    End Class
End Namespace
