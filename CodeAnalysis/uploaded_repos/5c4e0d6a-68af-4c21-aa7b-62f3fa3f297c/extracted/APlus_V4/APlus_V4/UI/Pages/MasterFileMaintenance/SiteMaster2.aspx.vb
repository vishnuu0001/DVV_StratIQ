#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports System.Collections.Generic

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class SiteMaster2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Site Master"
        Private Shared ReadOnly ProgramName As String = "SiteMaster2"
        Private Shared ReadOnly DBTableName As String = "SiteMaster"
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
            Dim myTabArray() As Object = {txtSite, _
                                          txtExpandFolderLink, _
                                          txtADSite, _
                                          txtSiteAbbrev, _
                                          txtCurrencyAbbrev, _
                                          txtTimeOffset, _
                                          ckActive, _
                                          txtTeamAction, _
                                          txtTeamActionReminder, _
                                          txtKPIValue, _
                                          txtKPIValueReminder, _
                                          txtKPITarget, _
                                          txtKPITargetReminder, _
                                          txtAnomalyPending, _
                                          txtAnomalyPendingReminder, _
                                          txtAnomalyActions, _
                                          txtAnomalyActionsReminder, _
                                          txtTeamMeetings, _
                                          ckAnomalySGI}

            Dim TabKeyDownArr() As String = {Tab(txtExpandFolderLink, ckAnomalySGI, "No"), _
                                             Tab(txtADSite, txtSite, "No"), _
                                             Tab(txtSiteAbbrev, txtExpandFolderLink, "No"), _
                                             Tab(txtCurrencyAbbrev, txtADSite, "No"), _
                                             Tab(txtTimeOffset, txtSiteAbbrev, "No"), _
                                             Tab(ckActive, txtCurrencyAbbrev, "Neg"), _
                                             Tab(txtTeamAction, txtTimeOffset, "Int"), _
                                             Tab(txtTeamActionReminder, ckActive, "Int"), _
                                             Tab(txtKPIValue, txtTeamAction, "Int"), _
                                             Tab(txtKPIValueReminder, txtTeamActionReminder, "Int"), _
                                             Tab(txtKPITarget, txtKPIValue, "Int"), _
                                             Tab(txtKPITargetReminder, txtKPIValueReminder, "Int"), _
                                             Tab(txtAnomalyPending, txtKPITarget, "Int"), _
                                             Tab(txtAnomalyPendingReminder, txtKPITargetReminder, "Int"), _
                                             Tab(txtAnomalyActions, txtAnomalyPending, "Int"), _
                                             Tab(txtAnomalyActionsReminder, txtAnomalyPendingReminder, "Int"), _
                                             Tab(txtTeamMeetings, txtAnomalyActions, "Int"), _
                                             Tab(ckAnomalySGI, txtAnomalyActionsReminder, "Int"), _
                                             Tab(txtSite, txtTeamMeetings, "NO")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
        Private Sub LoadEditModeJavaScripts()
            If SessionManager.IsAdministrator = False Then
                Dim myTabArray() As Object = {txtExpandFolderLink, _
                                              txtADSite, _
                                              txtSiteAbbrev, _
                                              txtTimeOffset, _
                                              ckActive}

                Dim TabKeyDownArr() As String = {Tab(txtADSite, ckActive, "No"), _
                                                 Tab(txtSiteAbbrev, txtExpandFolderLink, "No"), _
                                                 Tab(txtTimeOffset, txtADSite, "No"), _
                                                 Tab(ckActive, txtSiteAbbrev, "Neg"), _
                                                 Tab(txtExpandFolderLink, txtTimeOffset, "No")}

                AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
            Else
                Dim myTabArray() As Object = {txtExpandFolderLink, _
                                              txtADSite, _
                                              txtSiteAbbrev, _
                                              txtCurrencyAbbrev, _
                                              txtTimeOffset, _
                                              ckActive, _
                                              txtTeamAction, _
                                              txtTeamActionReminder, _
                                              txtKPIValue, _
                                              txtKPIValueReminder, _
                                              txtKPITarget, _
                                              txtKPITargetReminder, _
                                              txtAnomalyPending, _
                                              txtAnomalyPendingReminder, _
                                              txtAnomalyActions, _
                                              txtAnomalyActionsReminder, _
                                              txtTeamMeetings, _
                                              ckAnomalySGI}

                Dim TabKeyDownArr() As String = {Tab(txtADSite, ckAnomalySGI, "No"), _
                                                 Tab(txtSiteAbbrev, txtExpandFolderLink, "No"), _
                                                 Tab(txtCurrencyAbbrev, txtADSite, "No"), _
                                                 Tab(txtTimeOffset, txtSiteAbbrev, "No"), _
                                                 Tab(ckActive, txtCurrencyAbbrev, "Neg"), _
                                                 Tab(txtTeamAction, txtTimeOffset, "Int"), _
                                                 Tab(txtTeamActionReminder, ckActive, "Int"), _
                                                 Tab(txtKPIValue, txtTeamAction, "Int"), _
                                                 Tab(txtKPIValueReminder, txtTeamActionReminder, "Int"), _
                                                 Tab(txtKPITarget, txtKPIValue, "Int"), _
                                                 Tab(txtKPITargetReminder, txtKPIValueReminder, "Int"), _
                                                 Tab(txtAnomalyPending, txtKPITarget, "Int"), _
                                                 Tab(txtAnomalyPendingReminder, txtKPITargetReminder, "Int"), _
                                                 Tab(txtAnomalyActions, txtAnomalyPending, "Int"), _
                                                 Tab(txtAnomalyActionsReminder, txtAnomalyPendingReminder, "Int"), _
                                                 Tab(txtTeamMeetings, txtAnomalyActions, "Int"), _
                                                 Tab(ckAnomalySGI, txtAnomalyActionsReminder, "Int"), _
                                                 Tab(txtExpandFolderLink, txtTeamMeetings, "NO")}

                AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
            End If
        End Sub
#End Region

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, ProgramName, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Master.HeaderMessage = SessionManager.SiteMasterMode.Replace("Row", "") & " Site"
            Master.IconImage = Request.ApplicationPath + "/images/earth_location.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                Select Case SessionManager.SiteMasterMode
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "EditRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        LoadEditModeJavaScripts()
                        txtExpandFolderLink.Focus()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Site.');")
                        TransactionHistory1.LockControl = True
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        LoadAddModeJavaScripts()
                        txtSite.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SiteMasterMaintenance"), False)
                End Select
            End If
        End Sub
        Private Sub btnOK_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim blnSuccess As Boolean

            Select Case SessionManager.SiteMasterMode
                Case "EditRow"
                    blnSuccess = UpdateSite()
                Case "DeleteRow"
                    blnSuccess = DeleteSite()
                Case "AddRow"
                    blnSuccess = InsertSite()
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueSiteID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SiteMasterMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SiteMasterMaintenance"), False)
            End If
        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click, btnCancel.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueSiteID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SiteMasterMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SiteMasterMaintenance"), False)
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadSelectedRecord()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim dr As DataRow = Nothing

                Dim objDT As DataTable = SiteMaster.GetSiteMasterBySite(SessionManager.SelectedValueSiteID)
                If objDT IsNot Nothing AndAlso objDT.Rows.Count <> 0 Then
                    dr = objDT.Rows(0)

                    txtSite.Text = SessionManager.SelectedValueSite
                    txtExpandFolderLink.Text = dr.Item("FolderIconLink").ToString.Trim()
                    txtADSite.Text = dr.Item("ADSite").ToString.Trim()
                    txtSiteAbbrev.Text = dr("SiteAbbrev").ToString.Trim
                    txtCurrencyAbbrev.Text = dr("CurrencyAbbrev").ToString.Trim()
                    txtTimeOffset.Text = dr("TimeOffsetHours").ToString
                    ckActive.Checked = Convert.ToBoolean(dr("Active"))
                End If

                objDT = SiteMaster.GetSiteMasterAttributesBySite(SessionManager.SelectedValueSiteID)
                If objDT IsNot Nothing AndAlso objDT.Rows.Count > 0 Then
                    dr = objDT.Rows(0)

                    txtTeamAction.Text = dr("TeamActions").ToString
                    txtTeamActionReminder.Text = dr("TeamActionsReminder").ToString
                    txtKPIValue.Text = dr("KPIValueEntry").ToString
                    txtKPIValueReminder.Text = dr("KPIValueEntryReminder").ToString
                    txtKPITarget.Text = dr("KPITargetEntry").ToString
                    txtKPITargetReminder.Text = dr("KPITargetEntryReminder").ToString
                    txtAnomalyPending.Text = dr("AnomalyPending").ToString
                    txtAnomalyPendingReminder.Text = dr("AnomalyPendingReminder").ToString
                    txtAnomalyActions.Text = dr("AnomalyActions").ToString
                    txtAnomalyActionsReminder.Text = dr("AnomalyActionsReminder").ToString
                    txtTeamMeetings.Text = dr("TeamMeetingReminder").ToString
                    ckAnomalySGI.Checked = Convert.ToBoolean(dr("ShowAnomalySGI"))
                End If

                If SessionManager.RecordTransactionCurrentValues IsNot Nothing Then
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RecordTransactionCurrentValues)
                End If
                TransactionHistory1.TableName = DBTableName
                TransactionHistory1.RecordID = SessionManager.SelectedValueSiteID

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("Site", txtSite.Text.Trim())
                objDic.Add("FolderIconLink", txtExpandFolderLink.Text.Trim())
                objDic.Add("ADSite", txtADSite.Text.Trim())
                objDic.Add("SiteAbbrev", txtSiteAbbrev.Text.Trim)
                objDic.Add("CurrencyAbbrev", txtCurrencyAbbrev.Text.Trim)
                objDic.Add("TimeOffsetHours", txtTimeOffset.Text.Trim())
                objDic.Add("Active", ckActive.Checked)

                objDic.Add("TeamActions", txtTeamAction.Text.Trim())
                objDic.Add("TeamActionsReminder", txtTeamActionReminder.Text.Trim())
                objDic.Add("KPIValueEntry", txtKPIValue.Text.Trim())
                objDic.Add("KPIValueEntryReminder", txtKPIValueReminder.Text.Trim())
                objDic.Add("KPITargetEntry", txtKPITarget.Text.Trim())
                objDic.Add("KPITargetEntryReminder", txtKPITargetReminder.Text.Trim())
                objDic.Add("AnomalyPending", txtAnomalyPending.Text.Trim())
                objDic.Add("AnomalyPendingReminder", txtAnomalyPendingReminder.Text.Trim())
                objDic.Add("AnomalyActions", txtAnomalyActions.Text.Trim())
                objDic.Add("AnomalyActionsReminder", txtAnomalyActionsReminder.Text.Trim())
                objDic.Add("TeamMeeting", txtTeamMeetings.Text.Trim())
                objDic.Add("AnomalySGI", ckAnomalySGI.Checked.ToString())

                SessionManager.RecordTransactionCurrentValues = objDic
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub UnEnableRecords()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.SiteMasterMode = "ViewRow" Then
                pnlOKCancel.Visible = False
                txtSite.ReadOnly = True
                txtSite.CssClass = "Textbox_Display"
                txtExpandFolderLink.ReadOnly = True
                txtExpandFolderLink.CssClass = "Textbox_Display"
                txtADSite.ReadOnly = True
                txtADSite.CssClass = "Textbox_Display"
                txtSiteAbbrev.ReadOnly = True
                txtSiteAbbrev.CssClass = "Textbox_Display"
                txtCurrencyAbbrev.ReadOnly = True
                txtCurrencyAbbrev.CssClass = "Textbox_Display"
                txtTimeOffset.ReadOnly = True
                txtTimeOffset.CssClass = "Textbox_Display"
                ckActive.Enabled = False

                txtTeamAction.ReadOnly = True
                txtTeamAction.CssClass = "Textbox_Display"
                txtTeamActionReminder.ReadOnly = True
                txtTeamActionReminder.CssClass = "Textbox_Display"
                txtKPITarget.ReadOnly = True
                txtKPITarget.CssClass = "Textbox_Display"
                txtKPITargetReminder.ReadOnly = True
                txtKPITargetReminder.CssClass = "Textbox_Display"
                txtKPIValue.ReadOnly = True
                txtKPIValue.CssClass = "Textbox_Display"
                txtKPIValueReminder.ReadOnly = True
                txtKPIValueReminder.CssClass = "Textbox_Display"
                txtAnomalyPending.ReadOnly = True
                txtAnomalyPending.CssClass = "Textbox_Display"
                txtAnomalyPendingReminder.ReadOnly = True
                txtAnomalyPendingReminder.CssClass = "Textbox_Display"
                txtAnomalyActions.ReadOnly = True
                txtAnomalyActions.CssClass = "Textbox_Display"
                txtAnomalyActionsReminder.ReadOnly = True
                txtAnomalyActionsReminder.CssClass = "Textbox_Display"
                txtTeamMeetings.ReadOnly = True
                txtTeamMeetings.CssClass = "Textbox_Display"
                ckAnomalySGI.Enabled = False
            ElseIf SessionManager.SiteMasterMode = "DeleteRow" Then
                txtSite.ReadOnly = True
                txtSite.CssClass = "Textbox_Display"
                txtExpandFolderLink.ReadOnly = True
                txtExpandFolderLink.CssClass = "Textbox_Display"
                txtADSite.ReadOnly = True
                txtADSite.CssClass = "Textbox_Display"
                txtSiteAbbrev.ReadOnly = True
                txtSiteAbbrev.CssClass = "Textbox_Display"
                txtCurrencyAbbrev.ReadOnly = True
                txtCurrencyAbbrev.CssClass = "Textbox_Display"
                txtTimeOffset.ReadOnly = True
                txtTimeOffset.CssClass = "Textbox_Display"
                ckActive.Enabled = False

                txtTeamAction.ReadOnly = True
                txtTeamAction.CssClass = "Textbox_Display"
                txtTeamActionReminder.ReadOnly = True
                txtTeamActionReminder.CssClass = "Textbox_Display"
                txtKPITarget.ReadOnly = True
                txtKPITarget.CssClass = "Textbox_Display"
                txtKPITargetReminder.ReadOnly = True
                txtKPITargetReminder.CssClass = "Textbox_Display"
                txtKPIValue.ReadOnly = True
                txtKPIValue.CssClass = "Textbox_Display"
                txtKPIValueReminder.ReadOnly = True
                txtKPIValueReminder.CssClass = "Textbox_Display"
                txtAnomalyPending.ReadOnly = True
                txtAnomalyPending.CssClass = "Textbox_Display"
                txtAnomalyPendingReminder.ReadOnly = True
                txtAnomalyPendingReminder.CssClass = "Textbox_Display"
                txtAnomalyActions.ReadOnly = True
                txtAnomalyActions.CssClass = "Textbox_Display"
                txtAnomalyActionsReminder.ReadOnly = True
                txtAnomalyActionsReminder.CssClass = "Textbox_Display"
                txtTeamMeetings.ReadOnly = True
                txtTeamMeetings.CssClass = "Textbox_Display"
                ckAnomalySGI.Enabled = False
            ElseIf SessionManager.IsAdministrator = False Then
                txtSite.ReadOnly = True
                txtSite.CssClass = "Textbox_Display"
                txtADSite.ReadOnly = True
                txtADSite.CssClass = "Textbox_Display"
                txtSiteAbbrev.ReadOnly = True
                txtSiteAbbrev.CssClass = "Textbox_Display"
                txtCurrencyAbbrev.ReadOnly = True
                txtCurrencyAbbrev.CssClass = "Textbox_Display"
                txtTimeOffset.ReadOnly = True
                txtTimeOffset.CssClass = "Textbox_Display"
                ckActive.Enabled = False
            End If
        End Sub
        Private Function UpdateSite() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
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

                SiteMaster.UpdateSiteMaster(SessionManager.SelectedValueSiteID, txtSite.Text, txtExpandFolderLink.Text, txtADSite.Text.Trim.ToUpper, txtSiteAbbrev.Text.Trim.ToUpper, txtCurrencyAbbrev.Text.Trim.ToUpper, txtTimeOffset.Text, ckActive.Checked)
                SiteMaster.UpdateSiteMasterAttributes(SessionManager.SelectedValueSiteID, txtTeamAction.Text.Trim, txtTeamActionReminder.Text.Trim, txtKPIValue.Text.Trim, txtKPIValueReminder.Text.Trim, txtKPITarget.Text.Trim, txtKPITargetReminder.Text.Trim, txtAnomalyPending.Text.Trim, txtAnomalyPendingReminder.Text.Trim, txtAnomalyActions.Text.Trim, txtAnomalyActionsReminder.Text.Trim, txtTeamMeetings.Text.Trim, ckAnomalySGI.Checked)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueSiteID, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateSite ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function InsertSite() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
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

                Dim intReturn As Integer = SiteMaster.AddSiteMaster(txtSite.Text, txtExpandFolderLink.Text, txtADSite.Text.Trim.ToUpper, txtSiteAbbrev.Text.Trim.ToUpper, txtCurrencyAbbrev.Text.Trim.ToUpper, txtTimeOffset.Text, ckActive.Checked)
                If intReturn > 0 Then
                    SiteMaster.UpdateSiteMasterAttributes(intReturn, txtTeamAction.Text.Trim, txtTeamActionReminder.Text.Trim, txtKPIValue.Text.Trim, txtKPIValueReminder.Text.Trim, txtKPITarget.Text.Trim, txtKPITargetReminder.Text.Trim, txtAnomalyPending.Text.Trim, txtAnomalyPendingReminder.Text.Trim, txtAnomalyActions.Text.Trim, txtAnomalyActionsReminder.Text.Trim, txtTeamMeetings.Text.Trim, ckAnomalySGI.Checked)
                End If
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, intReturn.ToString.Trim(), strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertSite", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function DeleteSite() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                SiteMaster.DeleteSiteMaster(SessionManager.SelectedValueSiteID)
                SiteMaster.DeleteSiteMasterAttributes(SessionManager.SelectedValueSiteID)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueSiteID, "Site Deleted", SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteSite", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
        End Function
        Private Function GetUpdatedValues() As Dictionary(Of String, String)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim objDic As New Dictionary(Of String, String)
            objDic.Add("Site", txtSite.Text.Trim())
            objDic.Add("FolderIconLink", txtExpandFolderLink.Text.Trim())
            objDic.Add("ADSite", txtADSite.Text.Trim())
            objDic.Add("SiteAbbrev", txtSiteAbbrev.Text.Trim)
            objDic.Add("CurrencyAbbrev", txtCurrencyAbbrev.Text.Trim)
            objDic.Add("TimeOffsetHours", txtTimeOffset.Text.Trim())
            objDic.Add("Active", ckActive.Checked)

            objDic.Add("TeamActions", txtTeamAction.Text.Trim())
            objDic.Add("TeamActionsReminder", txtTeamActionReminder.Text.Trim())
            objDic.Add("KPIValueEntry", txtKPIValue.Text.Trim())
            objDic.Add("KPIValueEntryReminder", txtKPIValueReminder.Text.Trim())
            objDic.Add("KPITargetEntry", txtKPITarget.Text.Trim())
            objDic.Add("KPITargetEntryReminder", txtKPITargetReminder.Text.Trim())
            objDic.Add("AnomalyPending", txtAnomalyPending.Text.Trim())
            objDic.Add("AnomalyPendingReminder", txtAnomalyPendingReminder.Text.Trim())
            objDic.Add("AnomalyActions", txtAnomalyActions.Text.Trim())
            objDic.Add("AnomalyActionsReminder", txtAnomalyActionsReminder.Text.Trim())
            objDic.Add("TeamMeeting", txtTeamMeetings.Text.Trim())
            objDic.Add("AnomalySGI", ckAnomalySGI.Checked.ToString())

            Return objDic
        End Function
#End Region

    End Class
End Namespace