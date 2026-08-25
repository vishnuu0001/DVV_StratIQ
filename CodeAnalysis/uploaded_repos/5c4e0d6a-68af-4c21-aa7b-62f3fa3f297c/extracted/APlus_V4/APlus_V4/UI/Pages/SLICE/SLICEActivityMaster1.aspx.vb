#Region " Imports"

Imports System.IO
Imports WebApp.APlus.DataAccess.SLICETables
Imports WebApp.APlus.UI.CustomControls
Imports WebApp.APlus.DataAccess.Custom
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Tables

#End Region

Namespace WebApp.APlus.UI.SLICE
    Partial Class SLICEActivityMaster1
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "SLICE Activity Maintenance"
        Private Shared ReadOnly ProgramName As String = "SLICEActivityMaster1"
        Private Shared ReadOnly LINKS_COLUMN As Integer = 9
#End Region

#Region " Event Handlers "
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Master.IconImage = Request.ApplicationPath & "/images/clipboard.png"
            Master.HeaderMessage = FormName
            SessionManager.CurrentProgram = Request.Path
            Master.AddBodyAttribute("onkeydown", "TrapEscKey(document.getElementById('" + MasterControl1.ExitButtonID + "'),window.event)")
            Master.AddBodyAttribute("onkeydown", "TrapEnterKey(document.getElementById('" + MasterControl1.AddButtonID + "'),window.event)")

            If SessionManager.SelectedWorkCenterID <= 0 Then
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("WorkcenterSelection"))
            End If

            MasterControl1.StoredProcedureParams.Add("@ActivityGroupMaster", SessionManager.SLICEActivityGroupMasterID)
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

            SetActivityHyperlinkToSQLreport()

            MasterControl1.DataBind()
        End Sub
        Private Sub Mastercontrol1_ExitClick(ByVal sender As Object, ByVal e As System.EventArgs) Handles MasterControl1.ExitClick
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEActivityGroupMaster1"), False)
        End Sub
        Protected Sub MasterControl1_onRowCommand(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewCommandEventArgs) Handles MasterControl1.onRowCommand
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If e.CommandName = "ViewRow" Or e.CommandName = "DeleteRow" Or e.CommandName = "EditRow" Then
                SessionManager.SelectedValueSLICEActivityID = MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("SLICEActivityID").ToString
                SessionManager.SelectedValueSLICETypeID = MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("SLICEType").ToString
                SessionManager.SLICEActivityMasterMode = e.CommandName
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEActivityMaster2"), False)
            End If
        End Sub
        Protected Sub MasterControl1_onRowDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewRowEventArgs) Handles MasterControl1.onRowDataBound
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If e.Row.RowType = DataControlRowType.DataRow Then
                If e.Row.Cells(LINKS_COLUMN).Text.Trim.Length > 0 And e.Row.Cells(LINKS_COLUMN).Text <> "&nbsp;" Then
                    Dim iActivityID As Integer = CInt(MasterControl1.MasterControlGrid.DataKeys(e.Row.RowIndex)("SLICEActivityID").ToString)
                    Dim objDT As DataTable = SLICEActivityLinks.SelectActivityLinkDataAsDataTable(iActivityID)

                    If Not objDT Is Nothing AndAlso objDT.Rows.Count > 0 Then
                        Dim objLink As HyperLink
                        Dim objBreak As HtmlGenericControl

                        For Each dtRow As DataRow In objDT.Rows
                            objLink = New HyperLink
                            objLink.Text = dtRow("LinkDescription").ToString
                            objLink.NavigateUrl = dtRow("LinkURL").ToString
                            objLink.Target = "_blank"

                            If e.Row.Cells(LINKS_COLUMN).Controls.Count > 0 Then
                                objBreak = New HtmlGenericControl
                                objBreak.InnerHtml = "<BR />"

                                e.Row.Cells(LINKS_COLUMN).Controls.Add(objBreak)
                            End If

                            e.Row.Cells(LINKS_COLUMN).Controls.Add(objLink)
                        Next
                    End If
                End If
                If e.Row.Cells(10).Text.Trim.ToUpper() <> "&NBSP;" Then
                    'CType(e.Row.FindControl("lbtnDelete"), LinkButton).Visible = False
                End If
            End If
        End Sub
#End Region

#Region " Custom Methods "
        Public Sub SetActivityHyperlinkToSQLreport()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim strURL As String = String.Empty

            Try
                Dim dt As Data.DataTable = SLICEActivityGroupMaster.SelectSLICEActivityGroupMasterByID(SessionManager.SLICEActivityGroupMasterID)
                If dt.Rows.Count > 0 Then
                    hlnkShowSLICEActivityGroup.Text = dt.Rows(0)("SLICEActivityGroup").ToString().Trim()
                    strURL = Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & "UI/Pages/DataCollectionPrograms/WebReportPrintPreview.aspx"
                    strURL += "?ReportKey=ActivityMaster"
                    strURL += "&ReportParams=ActivityGroupMasterID=" & SessionManager.SLICEActivityGroupMasterID.ToString()
                    hlnkShowSLICEActivityGroup.NavigateUrl = strURL
                Else
                    hlnkShowSLICEActivityGroup.Text = "No activity group found for ID: " & SessionManager.SLICEActivityGroupMasterID.ToString()
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - SetActivityHyperlinkToSQLreport", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

    End Class
End Namespace

