#Region " Imports"

Imports System.IO
Imports WebApp.APlus.UI.CustomControls
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables

#End Region

Namespace WebApp.APlus.UI.SLICE
    Partial Class EntityMaster1
        Inherits ApplicationBase

#Region " Private Constants "
        Private Shared ReadOnly FormName As String = "Entity Master"
        Private Shared ReadOnly ProgramName As String = "EntityMaster1"
#End Region

#Region " Event Handlers "
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, ProgramName, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Master.IconImage = Request.ApplicationPath & "/images/clipboard.png"
            Master.HeaderMessage = FormName
            Master.AddBodyAttribute("onkeydown", "TrapEscKey(document.getElementById('" + MasterControl1.ExitButtonID + "'),window.event)")
            Master.AddBodyAttribute("onkeydown", "TrapEnterKey(document.getElementById('" + MasterControl1.AddButtonID + "'),window.event)")

            If Not Page.IsPostBack Then
                LoadDDL()
                LoadFilter()
            End If
        End Sub
        Protected Sub Timer1_Tick(ByVal sender As Object, ByVal e As System.EventArgs) Handles Timer1.Tick
            Timer1.Enabled = False
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            BindGrid()
        End Sub
        Protected Sub btnApplyFilter_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnApplyFilter.Click
            If ddlWorkcenter.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlWorkcenter.SelectedItem.Value) _
            AndAlso Convert.ToInt16(ddlWorkcenter.SelectedItem.Value) > 0 Then
                SessionManager.EntityFilterWorkcenterID = Convert.ToInt32(ddlWorkcenter.SelectedItem.Value)
            Else
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.EntityFilterWorkcenterID)
            End If
            If Not String.IsNullOrEmpty(txtEntity.Text) Then
                SessionManager.EntityFilterEntity = txtEntity.Text.Trim
            Else
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.EntityFilterEntity)
            End If
            If Not String.IsNullOrEmpty(txtLocation.Text) Then
                SessionManager.EntityFilterLocation = txtLocation.Text.Trim
            Else
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.EntityFilterLocation)
            End If

            BindGrid()
        End Sub
        Protected Sub MasterControl1_onRowCommand(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewCommandEventArgs) Handles MasterControl1.onRowCommand
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", e.CommandName)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If e.CommandName = "ViewRow" OrElse e.CommandName = "DeleteRow" OrElse e.CommandName = "EditRow" Then
                SessionManager.SelectedValueEntityID = CInt(MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("EntityID"))
                SessionManager.EntityMasterMode = e.CommandName
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("EntityMaster2"), False)
            End If
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadDDL()
            ddlWorkcenter.Items.Clear()

            DataAccess.SLICETables.WorkcenterMaster.SelectWorkcenterMasterList(ddlWorkcenter, SessionManager.WorkingSiteID)
        End Sub
        Private Sub LoadFilter()
            If SessionManager.EntityFilterWorkcenterID > 0 Then
                Dim objItem As ListItem = ddlWorkcenter.Items.FindByValue(SessionManager.EntityFilterWorkcenterID)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                End If
            End If
            txtEntity.Text = SessionManager.EntityFilterEntity.Trim
            txtLocation.Text = SessionManager.EntityFilterLocation.Trim
        End Sub
        Private Sub BindGrid()
            MasterControl1.StoredProcedureParams.Clear()

            MasterControl1.StoredProcedureParams.Add("@WorkingSiteID", SessionManager.WorkingSiteID)
            If ddlWorkcenter.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlWorkcenter.SelectedItem.Value) _
            AndAlso Convert.ToInt16(ddlWorkcenter.SelectedItem.Value) > 0 Then
                MasterControl1.StoredProcedureParams.Add("@WorkcenterID", ddlWorkcenter.SelectedItem.Value)
            End If
            If Not String.IsNullOrEmpty(txtEntity.Text) Then
                MasterControl1.StoredProcedureParams.Add("@Entity", txtEntity.Text.Trim)
            End If
            If Not String.IsNullOrEmpty(txtLocation.Text) Then
                MasterControl1.StoredProcedureParams.Add("@Location", txtLocation.Text.Trim)
            End If

            MasterControl1.DataBind(True)
        End Sub
#End Region

    End Class
End Namespace

