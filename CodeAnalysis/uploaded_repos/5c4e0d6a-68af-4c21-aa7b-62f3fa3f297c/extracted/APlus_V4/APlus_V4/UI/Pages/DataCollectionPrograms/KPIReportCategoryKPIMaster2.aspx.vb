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
    Partial Class KPIReportCategoryKPIMaster2
        Inherits ApplicationBase

#Region " Private Variables"
        Private Shared ReadOnly FormName As String = "KPI Group Item Maintenance"
        Private Shared ReadOnly ProgramName As String = "KPIReportCategoryKPIMaster2"
        Private Shared ReadOnly DBTableName As String = "KPIReportCategoryKPIMaster"
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
        Private Sub LoadAddModeJavaScripts()
            Dim myTabArray() As Object = {ddlKPIReportCategory, _
                                          ddlKPI, _
                                          txtLegend, _
                                          txtSequence}

            Dim TabKeyDownArr() As String = {Tab(ddlKPI, txtSequence, "No"), _
                                             Tab(txtLegend, ddlKPIReportCategory, "No"), _
                                             Tab(txtSequence, ddlKPI, "No"), _
                                             Tab(ddlKPIReportCategory, txtLegend, "Int")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {txtLegend, _
                                          txtSequence}

            Dim TabKeyDownArr() As String = {Tab(txtSequence, txtSequence, "No"), _
                                             Tab(txtLegend, txtLegend, "Int")}

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

            If Not Page.IsPostBack Then
                LoadDropDownLists()

                If SessionManager.KPIReportFilterSiteID = 0 Then
                    ckShowAllKPI.Visible = False
                End If

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
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this KPI Group Item.');")
                        TransactionHistory1.LockControl = True
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        LoadAddModeJavaScripts()
                        ddlKPIReportCategory.Focus()
                    Case "EditRow"
                        LoadEditModeJavaScripts()
                        LoadSelectedRecord()
                        UnEnableRecords()
                        txtLegend.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPIReportCategoryKPIMaster1"), False)
                End Select
            End If
        End Sub
        Protected Sub ckShowAllKPI_CheckedChanged(ByVal sender As Object, ByVal e As System.EventArgs) Handles ckShowAllKPI.CheckedChanged
            LoadKPIDDL(Not ckShowAllKPI.Checked)
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
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPIReportCategoryKPIMaster1"), False)
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
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPIReportCategoryKPIMaster1"), False)
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
                KPIReports.GetKPIReportCategoryMasterList(ddlKPIReportCategory, Convert.ToInt16(SessionManager.SelectedKPIReportGroupID), SessionManager.KPIReportFilterSiteID)
                ddlKPIReportCategory.Items.Insert(0, "")

                LoadKPIDDL(True)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadDropDownLists", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub LoadKPIDDL(ByVal passFilterSite As Boolean)
            Dim iSiteID As Integer = 0
            If passFilterSite AndAlso SessionManager.KPIReportFilterSiteID > 0 Then
                iSiteID = SessionManager.KPIReportFilterSiteID
            End If

            ddlKPI.Items.Clear()

            KPIMaster.GetKPISiteList(ddlKPI, iSiteID, "EN")
            ddlKPI.Items.Insert(0, "")
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

            Dim objDT As DataTable = KPIReportCategoryKPIMaster.SelectKPIReportCategoryKPIMasterByID(Convert.ToInt16(SessionManager.SelectedValue), Convert.ToInt16(SessionManager.SelectedValue1))
            If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                Dim dtRow As DataRow = objDT.Rows(0)
                Dim objItem As ListItem

                objItem = ddlKPIReportCategory.Items.FindByValue(SessionManager.SelectedValue)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                    txtKPIReportCategory.Text = objItem.Text
                Else
                    Dim dtReport As DataTable = KPIReports.SelectKPIReportCategoryMasterByID(SessionManager.SelectedValue)
                    If dtReport IsNot Nothing AndAlso dtReport.Rows.Count = 1 Then
                        objItem = New ListItem(dtReport.Rows(0)("KPIReportName").ToString, SessionManager.SelectedValue)
                        objItem.Selected = True
                        ddlKPIReportCategory.Items.Add(objItem)
                        txtKPIReportCategory.Text = objItem.Text
                    End If
                End If
                objItem = ddlKPI.Items.FindByValue(SessionManager.SelectedValue1)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                    txtKPI.Text = objItem.Text
                Else
                    Dim dtKPI As DataTable = KPIMaster.SelectKPIMasterByID(SessionManager.SelectedValue1)
                    If dtKPI IsNot Nothing AndAlso dtKPI.Rows.Count = 1 Then
                        objItem = New ListItem(dtKPI.Rows(0)("SiteAbbrev").ToString & " - " & dtKPI.Rows(0)("KPIOther").ToString, SessionManager.SelectedValue1)
                        objItem.Selected = True
                        ddlKPI.Items.Add(objItem)
                        txtKPI.Text = objItem.Text
                    End If
                End If
                txtLegend.Text = dtRow("ReportLegend").ToString.Trim
                txtSequence.Text = dtRow("Sequence").ToString

                TransactionHistory1.TableName = DBTableName
                TransactionHistory1.RecordID = SessionManager.SelectedValue.Trim() & "," & SessionManager.SelectedValue1.Trim()

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("KPIReportCategory", txtKPIReportCategory.Text.Trim())
                objDic.Add("KPI", txtKPI.Text.Trim())
                objDic.Add("ReportLegend", txtLegend.Text.Trim())
                objDic.Add("Sequence", txtSequence.Text.Trim)

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
                    ddlKPIReportCategory.Visible = False
                    txtKPIReportCategory.Visible = True
                    ddlKPI.Visible = False
                    txtKPI.Visible = True
                    ckShowAllKPI.Visible = False
                    txtLegend.ReadOnly = True
                    txtLegend.CssClass = "Textbox_Display"
                    txtSequence.ReadOnly = True
                    txtSequence.CssClass = "Textbox_Display"
                Case "EditRow"
                    ddlKPIReportCategory.Visible = False
                    txtKPIReportCategory.Visible = True
                    ddlKPI.Visible = False
                    txtKPI.Visible = True
                    ckShowAllKPI.Visible = False
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

                KPIReportCategoryKPIMaster.AddKPIReportCategoryKPIMaster(Convert.ToInt16(ddlKPIReportCategory.SelectedItem.Value), Convert.ToInt16(ddlKPI.SelectedItem.Value), txtLegend.Text.Trim, Convert.ToInt16(txtSequence.Text))

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValue.Trim() & "," & SessionManager.SelectedValue1.Trim, strChangeLog, SessionManager.UserID)

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

                KPIReportCategoryKPIMaster.UpdateKPIReportCategoryKPIMaster(Convert.ToInt16(SessionManager.SelectedValue), Convert.ToInt16(SessionManager.SelectedValue1), txtLegend.Text.Trim, Convert.ToInt16(txtSequence.Text))

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValue.Trim() & "," & SessionManager.SelectedValue1.Trim, strChangeLog, SessionManager.UserID)

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
                KPIReportCategoryKPIMaster.DeleteKPIReportCategoryKPIMaster(Convert.ToInt16(SessionManager.SelectedValue), Convert.ToInt16(SessionManager.SelectedValue1))

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValue.Trim() & "," & SessionManager.SelectedValue1.Trim, "KPI Group KPI Deleted", SessionManager.UserID)

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
            objDic.Add("KPI", ddlKPI.SelectedItem.Text.Trim())
            objDic.Add("ReportLegend", txtLegend.Text.Trim())
            objDic.Add("Sequence", txtSequence.Text.Trim)

            Return objDic
        End Function
#End Region

    End Class
End Namespace
