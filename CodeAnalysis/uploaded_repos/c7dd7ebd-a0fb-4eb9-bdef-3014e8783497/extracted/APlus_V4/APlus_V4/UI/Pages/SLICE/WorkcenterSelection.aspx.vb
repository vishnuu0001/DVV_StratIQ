#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus
Imports WebApp.APlus.UI
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.UI.CustomControls
Imports WebApp.APlus.DataAccess.SLICETables

#End Region

Namespace WebApp.APlus.UI.SLICE
    Partial Class WorkcenterSelection
        Inherits ApplicationBase

#Region " Private Constant Variables"
        Private Shared ReadOnly FormName As String = "Workcenter Selection"
        Private Shared ReadOnly ProgramName As String = "WorkcenterSelection"
#End Region

#Region " Load JavaScripts"
        Private Sub LoadJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel}
            Dim OverMessageArr() As String = {"OK - Enter", "OK - Enter", "Cancel", "Cancel"}
            Dim OutMessageArr() As String = {"", "", "", ""}
            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)
            btnOK.Attributes.Add("onclick", "javascript:return CheckWorkcenter();")
        End Sub
#End Region

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Master.IconImage = Request.ApplicationPath & "/images/WorkCenter.gif"
            Master.HeaderMessage = FormName
            LoadJavaScripts()

            If Not Page.IsPostBack Then
                BindWorkcenters()
                ddlWorkcenter.Focus()
            End If
        End Sub
        Private Sub btnOK_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                If ddlWorkcenter.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlWorkcenter.SelectedItem.Value) AndAlso Convert.ToInt32(ddlWorkcenter.SelectedItem.Value) > 0 Then
                    SessionManager.SelectedWorkCenterID = ddlWorkcenter.SelectedItem.Value
                    SessionManager.SelectedWorkCenter = ddlWorkcenter.SelectedItem.Text
                Else
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedWorkcenterID)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedWorkCenter)
                    SessionManager.CurrentProgram = ""
                End If
            Finally
            End Try

            If SessionManager.CurrentProgram <> "" Then
                Response.Redirect(SessionManager.CurrentProgram)
            Else
                RemoveCurrentProgramandGoBack()
            End If
        End Sub
        Private Sub btnCancel_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnCancel.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
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
        Private Sub BindWorkcenters()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                WorkcenterMaster.SelectWorkcenterMasterList(ddlWorkcenter, SessionManager.WorkingSiteID)

                If SessionManager.SelectedWorkCenterID > 0 Then
                    Dim objItem As ListItem = ddlWorkcenter.Items.FindByValue(SessionManager.SelectedWorkCenterID)
                    If Not objItem Is Nothing Then
                        objItem.Selected = True
                    End If
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindWorkcenters", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

    End Class
End Namespace
