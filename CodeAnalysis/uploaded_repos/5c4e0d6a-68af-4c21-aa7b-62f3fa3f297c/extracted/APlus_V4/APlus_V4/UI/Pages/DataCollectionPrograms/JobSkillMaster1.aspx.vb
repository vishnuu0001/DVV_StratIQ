#Region " Imports"
Imports System.IO
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class JobSkillMaster1
        Inherits ApplicationBase

#Region " Constants"
        Private Shared ReadOnly FormName As String = "Job Skill Master"
        Private Shared ReadOnly ProgramName As String = "JobSkillMaster1"
#End Region

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, ProgramName, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Master.IconImage = Request.ApplicationPath & "/images/UserSkill.gif"

            Master.AddBodyAttribute("onkeydown", "TrapEscKey(document.getElementById('" + MasterControl1.ExitButtonID + "'),window.event)")
            Master.AddBodyAttribute("onkeydown", "TrapEnterKey(document.getElementById('" + MasterControl1.AddButtonID + "'),window.event)")

            'iJobID = SessionManager.SelectedValueJob
            'strJob = SessionManager.SelectedValueJobName

            Select Case SessionManager.JobMode
                Case "EditRow"
                    Master.HeaderMessage = FormName
                Case "EditMatrix"
                    Master.HeaderMessage = "Training Matrix Skill Master"
            End Select

            MasterControl1.StoredProcedureParams.Add("@JobID", SessionManager.SelectedValueJob)

            'Dim objCol As ButtonField

            'objCol = New ButtonField
            'objCol.ButtonType = ButtonType.Link
            'objCol.Text = "/\"
            'objCol.CommandName = "Up"
            'objCol.ControlStyle.CssClass = "Link_Default"
            'MasterControl1.GridColumns.Add(objCol)

            'objCol = New ButtonField
            'objCol.ButtonType = ButtonType.Link
            'objCol.Text = "\/"
            'objCol.CommandName = "Down"
            'objCol.ControlStyle.CssClass = "Link_Default"
            'MasterControl1.GridColumns.Add(objCol)

            If UserSkillRatings.UserSkillsExistsByJob(SessionManager.SelectedValueJob) Then
                MasterControl1.FunctionButtonOne.Visible = False
            Else
                MasterControl1.FunctionButtonOne.Visible = True
            End If
        End Sub

        Protected Sub Timer1_Tick(ByVal sender As Object, ByVal e As System.EventArgs) Handles Timer1.Tick
            Timer1.Enabled = False
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            MasterControl1.DataBind()
            Master.MasterScriptManager.RegisterPostBackControl(MasterControl1.ExportButton)
        End Sub

        Protected Sub MasterControl1_FunctionButtonOneClick(ByVal sender As Object, ByVal e As System.EventArgs) Handles MasterControl1.FunctionButtonOneClick
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("JobSkillMaster3"), False)
        End Sub

        Protected Sub MasterControl1_onRowCommand(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewCommandEventArgs) Handles MasterControl1.onRowCommand
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", e.CommandName)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If e.CommandName = "ViewRow" OrElse e.CommandName = "EditRow" OrElse e.CommandName = "DeleteRow" Then
                SessionManager.SelectedValueJobSkillID = MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("JobSkillID").ToString
                SessionManager.JobSkillMode = e.CommandName
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("JobSkillMaster2"), False)
            ElseIf e.CommandName = "Up" Then
                'if we're at the top then don't do anything
                If e.CommandArgument = 0 Then
                    Return
                Else
                    'update
                    JobSkillMaster.MoveSkillJob(MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("JobSkillID").ToString, MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument - 1)("JobSkillID").ToString)
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("JobSkillMaster1"), False)
                End If
            ElseIf e.CommandName = "Down" Then
                'if we're at the bottom, don't do anything
                If e.CommandArgument = MasterControl1.MasterControlGrid.Rows.Count - 1 Then
                    Return
                Else
                    JobSkillMaster.MoveSkillJob(MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("JobSkillID").ToString, MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument + 1)("JobSkillID").ToString)
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("JobSkillMaster1"), False)
                End If
            End If
        End Sub
#End Region

    End Class
End Namespace
