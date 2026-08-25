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
    Partial Class KPIReportCategoryMaster2
        Inherits ApplicationBase

#Region " Private Variables"
        Private Shared ReadOnly FormName As String = "KPI Group"
        Private Shared ReadOnly ProgramName As String = "KPIReportCategoryMaster2"
        Private Shared ReadOnly DBTableName As String = "KPIReportCategoryMaster"
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel, btnExit}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel", "Exit"}
            Dim OutMessageArr() As String = {"", "", ""}
            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnExit.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
        End Sub
        Private Sub LoadAddEditModeJavaScripts()
            Dim myTabArray() As Object = {ddlReportGroup, _
                                          txtReportItem, _
                                          ddlSite, _
                                          ddlReport, _
                                          txtSequence, _
                                          chkActive}

            Dim TabKeyDownArr() As String = {Tab(txtReportItem, chkActive, "No"), _
                                             Tab(ddlSite, ddlReportGroup, "No"), _
                                             Tab(ddlReport, txtReportItem, "No"), _
                                             Tab(txtSequence, ddlSite, "No"), _
                                             Tab(chkActive, ddlReport, "Int"), _
                                             Tab(ddlReportGroup, txtSequence, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
#End Region

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, ProgramName, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Master.HeaderMessage = FormName & " - " & SessionManager.TrackerVariableMode.Replace("Row", "")
            Master.IconImage = Request.ApplicationPath + "/images/boss.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/" & SessionManager.CulturePref & "/DataEntry.js")

            LoadCommonJavaScripts()

            LoadDropDownLists()

            If Not Page.IsPostBack Then
                Select Case SessionManager.Mode
                    Case "ViewRow"
                        pnlOKCancel.Visible = False
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this KPI Group.');")
                        TransactionHistory1.LockControl = True
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        LoadAddEditModeJavaScripts()
                        txtReportCategoryID.Text = "New"

                        Dim objItem As ListItem

                        If Request.Cookies("KPIReportFilter") IsNot Nothing Then
                            Dim cookie As HttpCookie = Request.Cookies("KPIReportFilter")

                            If cookie.Values("ReportGroupID") IsNot Nothing AndAlso IsNumeric(cookie.Values("ReportGroupID")) Then
                                objItem = ddlReportGroup.Items.FindByValue(cookie.Values("ReportGroupID"))
                                If objItem IsNot Nothing Then
                                    objItem.Selected = True
                                    txtReportItem.Focus()
                                End If
                            Else
                                ddlReportGroup.Focus()
                            End If
                        Else
                            ddlReportGroup.Focus()
                        End If

                    Case "EditRow"
                        LoadAddEditModeJavaScripts()
                        LoadSelectedRecord()
                        UnEnableRecords()
                        txtReportItem.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPIReportCategoryMaster1"), False)
                End Select
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

            Dim blnSuccess As Boolean
            Select Case SessionManager.Mode
                Case "AddRow"
                    blnSuccess = InsertKPIReport()
                Case "EditRow"
                    blnSuccess = UpdateKPIReport()
                Case "DeleteRow"
                    blnSuccess = DeleteKPIReport()
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue2)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue3)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Mode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPIReportCategoryMaster1"), False)
            End If
        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click, btnCancel.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue2)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue3)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Mode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPIReportCategoryMaster1"), False)
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadDropDownLists()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                KPIReportGroupMaster.SelectKPIReportGroupMasterList(ddlReportGroup)
                ddlReportGroup.Items.Insert(0, "")

                SiteMaster.SelectSiteMasterActiveList(ddlSite)
                ddlSite.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadDropDownLists", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub LoadSelectedRecord()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.RecordTransactionCurrentValues IsNot Nothing Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RecordTransactionCurrentValues)
            End If

            Dim objDT As DataTable = KPIReportCategoryMaster.SelectKPIReportCategoryMasterByID(Convert.ToInt16(SessionManager.SelectedValue))
            If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                Dim dtRow As DataRow = objDT.Rows(0)
                Dim objItem As ListItem

                txtReportCategoryID.Text = dtRow("KPIReportCategoryID").ToString
                objItem = ddlReportGroup.Items.FindByValue(dtRow("KPIReportGroupID").ToString)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                    txtReportGroup.Text = objItem.Text
                End If
                txtReportItem.Text = dtRow("KPIReportName").ToString
                objItem = ddlSite.Items.FindByValue(dtRow("SiteID").ToString)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                    txtSite.Text = objItem.Text
                ElseIf IsNumeric(dtRow("SiteID").ToString) Then
                    Dim dtSite As DataTable = SiteMaster.GetSiteMasterBySite(dtRow("SiteID").ToString)
                    If dtSite IsNot Nothing AndAlso dtSite.Rows.Count = 1 Then
                        objItem = New ListItem(dtSite.Rows(0)("Site").ToString, dtSite.Rows(0)("SiteID").ToString)
                        objItem.Selected = True
                        txtSite.Text = objItem.Text
                    End If
                End If
                objItem = ddlReport.Items.FindByValue(dtRow("ReportID").ToString)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                    txtReport.Text = objItem.Text
                End If
                txtSequence.Text = dtRow("Sequence").ToString
                chkActive.Checked = Convert.ToBoolean(dtRow("Active").ToString)

                TransactionHistory1.TableName = DBTableName
                TransactionHistory1.RecordID = SessionManager.SelectedValue.Trim()

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("KPIReportGroup", txtReportGroup.Text)
                objDic.Add("KPIReportName", txtReportItem.Text)
                objDic.Add("Site", txtSite.Text)
                objDic.Add("Report", txtReport.Text)
                objDic.Add("Sequence", txtSequence.Text.Trim)
                objDic.Add("Active", chkActive.Checked.ToString)

                SessionManager.RecordTransactionCurrentValues = objDic
            End If
        End Sub
        Private Sub UnEnableRecords()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Select Case SessionManager.Mode.ToString()
                Case "ViewRow", "DeleteRow"
                    ddlReportGroup.Visible = False
                    txtReportGroup.Visible = True
                    txtReportItem.ReadOnly = True
                    txtReportItem.CssClass = "Textbox_Display"
                    ddlSite.Visible = False
                    txtSite.Visible = True
                    ddlReport.Visible = False
                    txtReport.Visible = True
                    txtSequence.ReadOnly = True
                    txtSequence.CssClass = "Textbox_Display"
                    chkActive.Enabled = False
            End Select
        End Sub
        Private Function InsertKPIReport() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                Dim iSiteID As Integer = 0
                If ddlSite.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlSite.SelectedItem.Value) Then
                    iSiteID = ddlSite.SelectedItem.Value
                End If

                Dim iReportCategoryID As Integer = KPIReportCategoryMaster.AddKPIReportCategoryMaster(Convert.ToInt16(ddlReportGroup.SelectedItem.Value), txtReportItem.Text.Trim, iSiteID, Convert.ToInt16(ddlReport.SelectedItem.Value), Convert.ToInt16(txtSequence.Text), chkActive.Checked)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, iReportCategoryID.ToString, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertKPIReport", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateKPIReport() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.CompareDictionaryValues(SessionManager.RecordTransactionCurrentValues, objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                Dim iSiteID As Integer = 0
                If ddlSite.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlSite.SelectedItem.Value) Then
                    iSiteID = ddlSite.SelectedItem.Value
                End If

                KPIReportCategoryMaster.UpdateKPIReportCategoryMaster(Convert.ToInt16(SessionManager.SelectedValue), Convert.ToInt16(ddlReportGroup.SelectedItem.Value), txtReportItem.Text.Trim, iSiteID, Convert.ToInt16(ddlReport.SelectedItem.Value), Convert.ToInt16(txtSequence.Text), chkActive.Checked)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValue.Trim(), strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateKPIReport", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function DeleteKPIReport() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                KPIReportCategoryMaster.DeleteKPIReportCategoryMaster(Convert.ToInt16(SessionManager.SelectedValue))

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValue.Trim(), "KPI Group Deleted", SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteKPIReport", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
        End Function
        Private Function GetUpdatedValues() As Dictionary(Of String, String)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim objDic As New Dictionary(Of String, String)

            If ddlReportGroup.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlReportGroup.SelectedItem.Value) Then
                objDic.Add("KPIReportGroup", ddlReportGroup.SelectedItem.Text)
            Else
                objDic.Add("KPIReportGroup", "")
            End If
            objDic.Add("KPIReportName", txtReportItem.Text)
            If ddlSite.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlSite.SelectedItem.Value) Then
                objDic.Add("Site", ddlSite.SelectedItem.Text)
            Else
                objDic.Add("Site", "")
            End If
            If ddlReport.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlReport.SelectedItem.Value) Then
                objDic.Add("Report", ddlReport.SelectedItem.Text)
            Else
                objDic.Add("Report", "")
            End If
            objDic.Add("Sequence", txtSequence.Text.Trim)
            objDic.Add("Active", chkActive.Checked.ToString)

            Return objDic
        End Function
#End Region

    End Class
End Namespace
