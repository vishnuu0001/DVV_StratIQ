#Region " Imports"
Imports System.IO
Imports WebApp.APlus.UI.CustomControls
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables

#End Region

Namespace WebApp.APlus.UI.SLICE
    Partial Class SLICEActivityGroupMaster1
        Inherits ApplicationBase

#Region " Private Constants "
        Private Shared ReadOnly FormName As String = "Checksheet Template Master" ' LFS
        Private Shared ReadOnly ProgramName As String = "SLICEActivityGroupMaster1"
#End Region

#Region " Event Handlers"
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

            Dim objCol As ButtonField
            SessionManager.CurrentProgram = Request.Path

            If SessionManager.SelectedWorkCenterID <= 0 Then
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("WorkcenterSelection"), False)
            End If

            Master.IconImage = Request.ApplicationPath & "/images/clipboard.png"
            Master.HeaderMessage = FormName
            Master.AddBodyAttribute("onkeydown", "TrapEscKey(document.getElementById('" + MasterControl1.ExitButtonID + "'),window.event)")
            Master.AddBodyAttribute("onkeydown", "TrapEnterKey(document.getElementById('" + MasterControl1.AddButtonID + "'),window.event)")

            MasterControl1.StoredProcedureParams.Add("@WorkcenterID", SessionManager.SelectedWorkCenterID)

            If ProgramSecurity.CanUserAccessProgram(SessionManager.UserID.ToString(), "SLICEActivityMaster1") Then
                objCol = New ButtonField
                objCol.ButtonType = ButtonType.Link
                objCol.Text = "Activities"
                objCol.CommandName = "cmdActivities"
                MasterControl1.GridColumns.Add(objCol)
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

            MasterControl1.DataBind()
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

            If e.CommandName = "ViewRow" Or e.CommandName = "DeleteRow" Or e.CommandName = "EditRow" Then
                SessionManager.SelectedValueSliceActivityGroupID = MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)(0).ToString()
                SessionManager.SLICEActivityGroupMasterMode = e.CommandName
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEActivityGroupMaster2"), False)
            ElseIf e.CommandName = "cmdActivities" Then
                Try
                    SessionManager.SelectedValueSLICEActivityID = MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)(0).ToString()
                    SessionManager.SLICEActivityGroupMasterID = MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)(0).ToString()
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEActivityMaster1"), False)
                Catch Exc As Exception
                    Master.WriteErrors("SLICEActivityGroupMaster1 - onRowCommand", Exc, SessionManager.UserID.ToString())
                End Try
            End If
        End Sub
        Private Sub Mastercontrol1_ExitClick(ByVal sender As Object, ByVal e As System.EventArgs) Handles MasterControl1.ExitClick
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

        Protected Sub MasterControl1_onRowDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewRowEventArgs) Handles MasterControl1.onRowDataBound
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If e.Row.RowType = DataControlRowType.DataRow Then
                If e.Row.Cells(1).Text.Trim.Length > 0 Then
                    Try
                        SessionManager.SLICEActivityGroupMasterID = MasterControl1.MasterControlGrid.DataKeys(e.Row.RowIndex)("SLICEActivityGroupID").ToString()
                        Dim strURL As String
                        strURL = Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & "UI/Pages/DataCollectionPrograms/WebReportPrintPreview.aspx"
                        strURL += "?ReportKey=ActivityMaster"
                        strURL += "&ReportParams=ActivityGroupMasterID=" & SessionManager.SLICEActivityGroupMasterID.ToString()
                        Dim objLink As New HyperLink
                        objLink.Text = e.Row.Cells(1).Text.Trim
                        objLink.NavigateUrl = strURL
                        objLink.Target = "_blank"
                        e.Row.Cells(1).Controls.Add(objLink)
                    Catch Exc As Exception
                        Dim strTemp As String
                        strTemp = Exc.Message
                    End Try
                End If
            End If
        End Sub
#End Region

    End Class
End Namespace

