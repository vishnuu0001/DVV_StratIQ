#Region " Imports"

Imports System.IO
Imports WebApp.APlus.UI.CustomControls
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.UI.UserControls
Imports WebApp.APlus.DataAccess.SLICETables
Imports System.Data.SqlClient
Imports System.Data
Imports WebApp.APlus.DataAccess.Tables

#End Region

Namespace WebApp.APlus.UI.SLICE
    Partial Class SLICEChecksheetMaster1
        Inherits ApplicationBase

#Region " Private Constants "
        Private Shared ReadOnly FormName As String = "SLICE Checksheet "
        Private Shared ReadOnly ProgramName As String = "SLICEChecksheetMaster1"
        Private Shared ReadOnly STATUS_COL As Integer = 4
        Private Shared ReadOnly ACTIVITIES_WITH_RESULTS As Integer = 7
        Private Shared ReadOnly ACTIVITIES_WITH_OUT_RESULTS As Integer = 8
        Private Shared ReadOnly ACTIVITY_GRP_ID_COL As Integer = 9
        Private Shared ReadOnly CHECKSHEET_RELEASE_COL As Integer = 10
        Protected mStrStatusText As String = "Status Text Not Yet Set"
        Protected objTCol As TemplateField
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
            Master.AddBodyAttribute("onkeydown", "TrapEscKey(document.getElementById('" + MasterControl1.ExitButtonID + "'),window.event)")
            Master.AddBodyAttribute("onkeydown", "TrapEnterKey(document.getElementById('" + MasterControl1.AddButtonID + "'),window.event)")

            SessionManager.CurrentProgram = Request.Path

            Dim strDateFormat As String = SessionManager.DateFormat

            txtStartDate_CalendarExtender.Format = strDateFormat
            txtEndDate_CalendarExtender.Format = strDateFormat

            If SessionManager.SelectedWorkCenterID <= 0 Then
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("WorkcenterSelection"), False)
            End If

            Dim objCol As ButtonField
            objCol = New ButtonField
            objCol.ButtonType = ButtonType.Link
            objCol.Text = "Release"
            objCol.CommandName = "UpdateLinkButtonStatus"
            MasterControl1.GridColumns.Add(objCol)

            If Not Page.IsPostBack Then
                If Not IsNothing(Request.Cookies("ChecksheetShowClosed")) AndAlso Request.Cookies("ChecksheetShowClosed").Value.ToString.Trim.Length > 0 Then
                    ckIncludeClosed.Checked = CBool(Request.Cookies("ChecksheetShowClosed").Value)
                End If
                If Not IsNothing(Request.Cookies("ChecksheetStartDate")) AndAlso IsDate(Request.Cookies("ChecksheetStartDate").Value.ToString) Then
                    txtStartDate.Text = Request.Cookies("ChecksheetStartDate").Value.ToString.Trim
                End If
                If Not IsNothing(Request.Cookies("ChecksheetEndDate")) AndAlso IsDate(Request.Cookies("ChecksheetEndDate").Value.ToString) Then
                    txtEndDate.Text = Request.Cookies("ChecksheetEndDate").Value.ToString.Trim
                End If
            End If

            If ckIncludeClosed.Checked AndAlso (Not IsDate(txtStartDate.Text) OrElse Not IsDate(txtEndDate.Text)) Then
                MasterControl1.StoredProcedureParams.Add("@WorkcenterID", -1)
            Else
                MasterControl1.StoredProcedureParams.Add("@WorkcenterID", SessionManager.SelectedWorkCenterID)
                If ckIncludeClosed.Checked Then
                    MasterControl1.StoredProcedureParams.Add("@IncludeClosed", ckIncludeClosed.Checked)
                End If
                If IsDate(txtStartDate.Text) AndAlso IsDate(txtEndDate.Text) Then
                    MasterControl1.StoredProcedureParams.Add("@StartDate", RegionalConversion.FormatSQLDate(txtStartDate.Text, False))
                    MasterControl1.StoredProcedureParams.Add("@EndDate", RegionalConversion.FormatSQLDate(txtEndDate.Text, False))
                End If
            End If

            MasterControl1.DataBind()
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

            Try
                If (e.CommandName = "ViewRow" OrElse e.CommandName = "DeleteRow" OrElse e.CommandName = "EditRow") AndAlso IsNumeric(e.CommandArgument) Then
                    SessionManager.SelectedValueCheckSheetID = MasterControl1.Rows(CInt(e.CommandArgument)).Cells(1).Text
                    SessionManager.SLICEChecksheetMasterMode = e.CommandName

                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEChecksheetMaster2"), False)
                ElseIf e.CommandName = "UpdateLinkButtonStatus" Then
                    Dim strArg As String() = e.CommandArgument.ToString.Split("|")
                    If strArg.Length = 2 AndAlso IsNumeric(strArg(0)) Then
                        Dim iRow As Integer = Convert.ToInt16(strArg(0))

                        If strArg(1).ToString().ToUpper() = "RELEASE" Then
                            SLICEChecksheetMaster.InsertValuesToSLICEChecksheetActivityMaster(MasterControl1.MasterControlGrid.DataKeys(iRow)("SLICEChecksheetID").ToString, MasterControl1.MasterControlGrid.DataKeys(iRow)("SLICEActivityGroupID").ToString)

                            If UpdateChecksheetStatusID(MasterControl1.MasterControlGrid.DataKeys(iRow)("SLICEChecksheetID").ToString, "Released") Then
                                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEChecksheetMaster1"), True)
                            End If
                        ElseIf strArg(1).ToString().ToUpper() = "CLOSE" Then
                            If UpdateChecksheetStatusID(MasterControl1.MasterControlGrid.DataKeys(iRow)("SLICEChecksheetID").ToString, "Closed") Then
                                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEChecksheetMaster1"), True)
                            End If
                        End If
                    End If
                End If
            Catch ex As Exception
                Master.DisplayErrors(ProgramName & " - MasterControl1_onRowCommand", ex, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SLICEChecksheetMasterMode)
            RemoveCurrentProgramandGoBack()
        End Sub
        Private Sub Mastercontrol1_AddClick(ByVal sender As Object, ByVal e As System.EventArgs) Handles MasterControl1.AddClick
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.SLICEActivityGroupMasterID = SetSLICEActivityGroupMasterSession()
            SessionManager.SLICEChecksheetMasterMode = "AddRow"
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEChecksheetMaster2"), False)
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

            Try
                If e.Row.RowType = DataControlRowType.DataRow Then
                    If e.Row.Cells(STATUS_COL).Text.Trim().ToUpper() = "RELEASED" Then
                        mStrStatusText = "Close"
                    ElseIf e.Row.Cells(STATUS_COL).Text.Trim().ToUpper() = "PLANNED" Then
                        mStrStatusText = "Release"
                    ElseIf e.Row.Cells(STATUS_COL).Text.Trim().ToUpper() = "CLOSED" Then
                        mStrStatusText = ""
                    End If
                    If e.Row.Cells(ACTIVITIES_WITH_OUT_RESULTS).Text.Trim() = "0" Then
                        e.Row.Cells(ACTIVITIES_WITH_OUT_RESULTS).Text = ""
                    End If
                    If e.Row.Cells(ACTIVITIES_WITH_RESULTS).Text.Trim() = "0" Then
                        e.Row.Cells(ACTIVITIES_WITH_RESULTS).Text = ""
                    End If

                    If e.Row.Cells(CHECKSHEET_RELEASE_COL).Controls.Count > 0 Then
                        Dim objL As LinkButton = CType(e.Row.Cells(CHECKSHEET_RELEASE_COL).Controls(0), LinkButton)
                        If objL IsNot Nothing Then
                            If mStrStatusText.Trim().Length > 0 Then
                                objL.CommandArgument = e.Row.RowIndex.ToString & "|" & mStrStatusText
                                objL.Text = mStrStatusText
                                mStrStatusText = ""
                            Else
                                objL.Visible = False
                            End If
                        End If
                    End If

                    If e.Row.Cells(0).Text.Trim.Length > 0 Then
                        Dim strURL As String = String.Empty
                        strURL = Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & "UI/Pages/DataCollectionPrograms/WebReportPrintPreview.aspx"
                        strURL += "?ReportKey=ChecksheetReport"
                        strURL += "&ReportParams=intCheckSheetID=" & e.Row.Cells(1).Text.ToString.Trim()
                        Dim objLink As New HyperLink
                        objLink.Text = e.Row.Cells(0).Text.Trim
                        objLink.NavigateUrl = strURL
                        objLink.Target = "_blank"
                        e.Row.Cells(0).Controls.Add(objLink)
                    End If

                    If e.Row.Cells(1).Text.Trim().Length > 0 Then
                        Dim objLinkBtn As New LinkButton
                        objLinkBtn.Text = e.Row.Cells(1).Text.Trim()
                        objLinkBtn.ID = "lbtnGetChecksheetInputPage"
                        objLinkBtn.CommandName = "ACCESS_CHECKSHEET_DATA_INPUT"
                        objLinkBtn.CommandArgument = e.Row.Cells(1).Text.Trim()
                        objLinkBtn.ToolTip = "Checksheet Data Entry Screen"
                        AddHandler objLinkBtn.Click, AddressOf LinkButton_Click
                        e.Row.Cells(1).Controls.Add(objLinkBtn)
                    End If
                End If
            Catch ex As Exception

            End Try
        End Sub
        Private Sub LinkButton_Click(ByVal sender As System.Object, ByVal e As System.EventArgs)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                SessionManager.SelectedValueCheckSheetID = sender.CommandArgument
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEChecksheetDataInput"), False)
            Catch ex As Exception
                EventTracker.Add("LinkButton_Click", ex.Message, SessionManager.UserID)
            End Try
        End Sub
        Private Sub btnApplyFilter_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnApplyFilter.Click
            If ckIncludeClosed.Checked Then
                If Not IsDate(txtStartDate.Text) OrElse Not IsDate(txtEndDate.Text) Then
                    Master.DisplayError("You must enter start and end date filters to display closed checksheets")
                    Return
                ElseIf IsDate(txtStartDate.Text) AndAlso IsDate(txtEndDate.Text) Then
                    If CDate(txtStartDate.Text) >= CDate(txtEndDate.Text) Then
                        Master.DisplayError("End date must be greater than Start date")
                        Return
                    ElseIf CDate(txtEndDate.Text).AddMonths(-6) > CDate(txtStartDate.Text) Then
                        Master.DisplayError("Date Range must not be greater than 6 months")
                        Return
                    End If
                End If
            End If

            Dim cookie As HttpCookie

            cookie = New HttpCookie("ChecksheetShowClosed", ckIncludeClosed.Checked.ToString)
            cookie.Expires = DateTime.Now.AddHours(120)
            Response.Cookies.Add(cookie)

            cookie = New HttpCookie("ChecksheetStartDate", txtStartDate.Text.Trim)
            cookie.Expires = DateTime.Now.AddHours(120)
            Response.Cookies.Add(cookie)

            cookie = New HttpCookie("ChecksheetEndDate", txtEndDate.Text.Trim)
            cookie.Expires = DateTime.Now.AddHours(120)
            Response.Cookies.Add(cookie)

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEChecksheetMaster1"), False)
        End Sub
        Private Sub btnClearFilter_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnClearFilter.Click
            Dim cookie As HttpCookie

            cookie = New HttpCookie("ChecksheetShowClosed")
            cookie.Expires = DateTime.Now.AddHours(-1)
            Response.Cookies.Add(cookie)

            cookie = New HttpCookie("ChecksheetStartDate")
            cookie.Expires = DateTime.Now.AddHours(-1)
            Response.Cookies.Add(cookie)

            cookie = New HttpCookie("ChecksheetEndDate")
            cookie.Expires = DateTime.Now.AddHours(-1)
            Response.Cookies.Add(cookie)

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEChecksheetMaster1"), False)
        End Sub
#End Region

#Region " Custom Methods "
        Public Function UpdateChecksheetStatusID(ByVal strChecksheetID As String, ByVal strChecksheetStatusDesc As String) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, strChecksheetID, strChecksheetStatusDesc)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                SLICEChecksheetMaster.UpdateSLICEChecksheetMasterStatusID(strChecksheetID, strChecksheetStatusDesc)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateChecksheetStatusID", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                Return False
            End Try

            Return True
        End Function
        Function SetSLICEActivityGroupMasterSession() As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim intResult As Integer = 0
            Try
                Dim dt As DataTable = SLICEChecksheetMaster.SelectChecksheetDataByWorkcenterID(SessionManager.SelectedWorkCenterID)
                If dt.Rows.Count > 0 Then
                    intResult = dt.Rows(0)("SLICEActivityGroupID")
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - SetSLICEActivityGroupMasterSession", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try

            Return intResult
        End Function
#End Region

    End Class
End Namespace

