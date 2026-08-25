#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Text
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper

Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.SLICETables
Imports WebApp.APlus.UI.CustomControls
Imports WebApp.APlus.DataAccess.Tables

#End Region

Namespace WebApp.APlus.UI.SLICE
    Partial Class SLICEActivityResults
        Inherits ApplicationBase

#Region " Member Variables "
        Protected mIntResultsCount As Integer
        Private Shared ReadOnly FormName As String = "SLICE Activity Results Maintenance"
        Private Shared ReadOnly ProgramName As String = "SLICEActivityResults"
#End Region

#Region " JavaScript Functions "
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel"}
            Dim OutMessageArr() As String = {"", ""}
            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnExit.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
        End Sub
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

            Master.HeaderMessage = FormName & " - " & SessionManager.SLICEActivityMasterMode.Replace("Row", "")
            Master.IconImage = Request.ApplicationPath + "/images/clipboard.png"
            LoadCommonJavaScripts()

            LoadSelectedRecord()

            DisableControls()

            If Not Page.IsPostBack Then
                LoadDataActivityResultsDataGrid()
                mIntResultsCount = 0
            End If

            If SessionManager.SLICEActivityMasterMode.Trim.ToUpper() = "VIEWROW" Then
                pnlOKCancel.Visible = False
                pnlExit.Visible = True
                grdResultsGrid.Enabled = False
            End If
        End Sub
        Private Sub btnCancel_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnCancel.Click, btnExit.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SLICEActivityLinkMasterMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEActivityMaster2"), False)
        End Sub
        Private Sub btnOK_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim strData As String = "" ' the list of SLICE Activity Result Text selections
            Dim objCheck As CheckBox
            Dim blnSuccess As Boolean
            Dim intPreviousResults As Integer

            Try
                For i As Integer = 0 To grdResultsGrid.Rows.Count - 1
                    objCheck = DirectCast(grdResultsGrid.Rows(i).FindControl("chkSLICEResultText"), CheckBox)
                    If objCheck.Checked = True Then
                        If strData.Trim.Length() < 1 Then
                            strData = objCheck.Text
                        ElseIf i = grdResultsGrid.Rows.Count - 1 Then
                            strData &= "," & objCheck.Text
                        Else
                            strData = strData & "," & objCheck.Text
                        End If
                    End If
                Next
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - btnOK_Click() ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try

            intPreviousResults = PreviousResultsSelected()
            If intPreviousResults Then
                blnSuccess = DeleteRecordsInSLICEActivityResultsMasterByActivityID(SessionManager.SelectedValueSLICEActivityID)
            End If

            If blnSuccess And strData.Length > 0 Or intPreviousResults = 0 Then
                blnSuccess = UpdateActivityResults(SessionManager.SelectedValueSLICEActivityID, strData)
                If blnSuccess Then
                    Master.WriteErrors(FormName, SessionManager.SLICEActivityResults & " SLICE Activity Results " & SessionManager.SelectedValueSLICEActivityID, SessionManager.UserID)
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEActivityMaster2"), False)
                End If
            Else
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEActivityMaster2"), False)
            End If
        End Sub
        Protected Sub grdResultsGrid_RowDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewRowEventArgs) Handles grdResultsGrid.RowDataBound
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If e.Row.RowType = DataControlRowType.DataRow Then
                Try
                    Dim objCheck As CheckBox = DirectCast(e.Row.FindControl("chkSLICEResultText"), CheckBox)
                    If Not IsNothing(objCheck) AndAlso IsCheckBoxChecked(objCheck.Text) Then
                        objCheck.Checked = True
                    End If
                Catch Exc As Exception
                    Master.DisplayErrors(ProgramName & " - grdResultsGrid_ItemDataBound ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                End Try
            End If
        End Sub
#End Region

#Region " Custom Methods "
        Private Sub LoadDataActivityResultsDataGrid()
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
                Dim dt As DataTable = SLICEActivityResultMaster.SelectSLICEResultTextAndPassAsDataTable()
                grdResultsGrid.DataSource = dt
                grdResultsGrid.DataBind()
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadDataActivityResultsDataGrid", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Function IsCheckBoxChecked(ByVal strResultText As String) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, strResultText)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim strResult As String = "False"
            Dim blnResult As Boolean = False
            Dim iTotalRecs As Integer
            Dim iCur As Integer
            Try
                Dim dt As DataTable = SLICEActivityResultMaster.SelectSLICEActivityResultsBasedOnSLICEActivityID(SessionManager.SelectedValueSLICEActivityID)
                mIntResultsCount = dt.Rows.Count
                If dt.Rows.Count > 0 Then
                    iTotalRecs = dt.Rows.Count
                    For iCur = 0 To iTotalRecs - 1
                        If dt.Rows(iCur)("SLICEResultText").ToString.Trim().CompareTo(strResultText.Trim()) = 0 Then
                            blnResult = True
                            Exit For
                        End If
                    Next
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - IsCheckBoxChecked", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
            Return blnResult
        End Function
        Public Function UpdateActivityResults(ByVal strActivityID As String, ByVal strResultTextList As String) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, strActivityID, strResultTextList)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                SLICEActivityResultMaster.InsertSLICEActivityResultMaster(strActivityID, strResultTextList)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateSLICEActivityResult", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
            Return True
        End Function
        Public Function DeleteRecordsInSLICEActivityResultsMasterByActivityID(ByVal strActivityID As String) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, strActivityID)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                SLICEActivityResultMaster.DeleteSLICEActivityResultByActivityId(strActivityID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteRecordsInSLICEActivityResultsMasterByActivityID", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
            Return True
        End Function
        Public Function PreviousResultsSelected() As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim intTotalRecs As Integer = 0
            Try
                Dim dt As DataTable = SLICEActivityResultMaster.SelectSLICEActivityResultsBasedOnSLICEActivityID(SessionManager.SelectedValueSLICEActivityID)
                intTotalRecs = dt.Rows.Count
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindSite", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
            Return intTotalRecs
        End Function
        Private Sub LoadSelectedRecord()
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
                Dim dt As DataTable = SLICEActivityMaster.SelectSLICEActivityMasterAsDataTable(SessionManager.SelectedValueSLICEActivityID)
                If dt.Rows.Count <> 0 Then
                    Dim objItem As ListItem

                    txtSLICEActivityID.Text = dt.Rows(0)("SLICEActivityID").ToString.Trim()
                    BindDropDownLists()
                    objItem = ddlSLICEActivityGroup.Items.FindByValue(dt.Rows(0)("SLICEActivityGroupID").ToString)
                    If Not objItem Is Nothing Then
                        objItem.Selected = True
                        txtSLICEActivityGroup.Text = objItem.Text
                    End If
                    objItem = ddlEntity.Items.FindByValue(dt.Rows(0)("EntityID").ToString)
                    If Not objItem Is Nothing Then
                        objItem.Selected = True
                        txtEntity.Text = objItem.Text
                    End If
                    objItem = ddlPosition.Items.FindByValue(dt.Rows(0)("PositionID").ToString)
                    If Not objItem Is Nothing Then
                        objItem.Selected = True
                        txtPosition.Text = objItem.Text
                    End If
                    txtSLICEType.Text = dt.Rows(0)("SLICEType").ToString().Trim()
                    txtPresentationSequence.Text = dt.Rows(0)("PresentationSequence").ToString.Trim
                    objItem = ddlSLICEFrequency.Items.FindByValue(dt.Rows(0)("SLICEFrequencyID").ToString)
                    If Not objItem Is Nothing Then
                        objItem.Selected = True
                        txtSLICEFrequency.Text = objItem.Text
                    End If
                    txtExpandMeasurement.Text = dt.Rows(0)("Measurement").ToString.Trim
                    txtExpandDesiredCondition.Text = dt.Rows(0)("DesiredCondition").ToString.Trim
                    txtTargetTime.Text = dt.Rows(0)("TargetTime").ToString.Trim
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub DisableControls()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            txtSLICEActivityID.ReadOnly = True
            txtSLICEActivityGroup.ReadOnly = True
            txtEntity.ReadOnly = True
            txtPosition.ReadOnly = True
            txtSLICEType.ReadOnly = True
            txtPresentationSequence.ReadOnly = True
            txtSLICEFrequency.ReadOnly = True
            txtExpandMeasurement.ReadOnly = True
            txtExpandDesiredCondition.ReadOnly = True
            txtSLICEFrequency.ReadOnly = True
            txtTargetTime.ReadOnly = True
            txtSLICEActivityID.CssClass = "Textbox_Display"
            txtSLICEActivityGroup.CssClass = "Textbox_Display"
            txtEntity.CssClass = "Textbox_Display"
            txtPosition.CssClass = "Textbox_Display"
            txtSLICEType.CssClass = "Textbox_Display"
            txtPresentationSequence.CssClass = "Textbox_Display"
            txtSLICEFrequency.CssClass = "Textbox_Display"
            txtExpandMeasurement.CssClass = "Textbox_Display"
            txtExpandDesiredCondition.CssClass = "Textbox_Display"
            txtSLICEFrequency.CssClass = "Textbox_Display"
            txtTargetTime.CssClass = "Textbox_Display"
        End Sub
        Private Sub BindDropDownLists()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            BindSLICEFrequencyMaster()
            BindEntityMaster()
            BindPositionMaster()
            BindSLICETypeMaster()
            BindSLICEActivityGroup()
        End Sub
        Private Sub BindSLICEFrequencyMaster()
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
                SLICEFrequencyMaster.SelectSLICEFrequencyMasterList(ddlSLICEFrequency)
                ddlSLICEFrequency.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindSLICEFrequencyMaster", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindEntityMaster()
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
                EntityMaster.SelectEntityMasterList(ddlEntity, SessionManager.SelectedWorkCenterID)
                ddlEntity.Items.Insert(0, " ")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindEntityMaster", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindPositionMaster()
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
                PositionMaster.SelectPositionMasterList(ddlPosition)
                ddlPosition.Items.Insert(0, " ")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindPositionMaster", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindSLICETypeMaster()
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
                SLICETypeMaster.SelectSLICETypeMasterList(ddlSLICEType)
                ddlSLICEType.Items.Insert(0, " ")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindSLICETypeMaster", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindSLICEActivityGroup()
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
                SLICEActivityGroupMaster.SelectSLICEActivityGroupMasterList(ddlSLICEActivityGroup)
                ddlSLICEActivityGroup.Items.Insert(0, " ")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindSLICEActivityGroup", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

    End Class
End Namespace

