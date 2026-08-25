#Region " Imports"
Imports System.IO
Imports System.Collections.Generic
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class KPITeamMaster2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "KPI Team Maintenance"
        Private Shared ReadOnly ProgramName As String = "KPITeamMaster2"
        Private Shared ReadOnly DBTableName As String = "KPITeamMaster"
#End Region

#Region " Load Culture Translations"
        Private Sub LoadCultureTranslations()
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
                lblKPI.Text = GetTranslationString("kpi", lblKPI.Text.Replace(":", "")) & ":"
                lblTeam.Text = GetTranslationString("team", lblTeam.Text.Replace(":", "")) & ":"
                lblKPIView.Text = GetTranslationString("kpiview", lblKPIView.Text.Replace(":", "")) & ":"
                lblKPIEdit.Text = GetTranslationString("kpiedit", lblKPIEdit.Text.Replace(":", "")) & ":"
                btnOK.Text = GetTranslationString("ok", btnOK.Text)
                btnCancel.Text = GetTranslationString("cancel", btnCancel.Text)
                btnExit.Text = GetTranslationString("exit", btnExit.Text)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadCultureTranslations", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
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
            Dim myTabArray() As Object = {ckKPIView, _
                                          ckKPIEdit}

            Dim TabKeyDownArr() As String = {Tab(ckKPIEdit, ckKPIEdit, "No"), _
                                             Tab(ckKPIView, ckKPIView, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
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

            Master.IconImage = Request.ApplicationPath + "/images/SecurityGroupProgramMaster.gif"
            Master.HeaderMessage = GetTranslationString(FormName, FormName) & " - " & GetTranslationString(SessionManager.KPITeamMasterMode.Replace("Row", ""), SessionManager.KPITeamMasterMode.Replace("Row", ""))
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                LoadCultureTranslations()

                BindKPISites()
                BindKPI()
                BindTeams()

                Select Case SessionManager.KPITeamMasterMode
                    Case "EditRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        LoadAddEditModeJavaScripts()
                        ckKPIView.Focus()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this KPI Team.');")
                        TransactionHistory1.LockControl = True
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        LoadAddEditModeJavaScripts()
                        Dim objItem As ListItem = Nothing

                        If SessionManager.SelectedValueTeamID > 0 Then
                            objItem = ddlTeam.Items.FindByValue(SessionManager.SelectedValueTeamID)
                            If objItem IsNot Nothing Then
                                objItem.Selected = True
                                txtTeam.Text = objItem.Text

                                ddlTeam.Visible = False
                                txtTeam.Visible = True
                            End If
                        End If

                        If SessionManager.SelectedValueKPIID > 0 Then
                            objItem = ddlKPI.Items.FindByValue(SessionManager.SelectedValueKPIID)
                            If objItem IsNot Nothing Then
                                objItem.Selected = True
                                txtKPI.Text = objItem.Text

                                ddlKPI.Visible = False
                                txtKPI.Visible = True
                                ddlKPISite.Visible = False
                            End If
                        End If

                        ddlKPI.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPITeamMaster1"), False)
                End Select
            End If
        End Sub
        Protected Sub ddlKPISite_SelectedIndexChanged(ByVal sender As Object, ByVal e As System.EventArgs) Handles ddlKPISite.SelectedIndexChanged
            BindKPI()
        End Sub
        Private Sub btnOK_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnOK.Click
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
            Select Case SessionManager.KPITeamMasterMode
                Case "EditRow"
                    blnSuccess = UpdateKPITeamMaster()
                Case "DeleteRow"
                    blnSuccess = DeleteKPITeamMaster()
                Case "AddRow"
                    blnSuccess = InsertKPITeamMaster()
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueTeam)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.KPITeamMasterMode)
                Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar & (ProgramSecurity.GetProgramURL("KPITeamMaster1")), False)
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueTeam)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.KPITeamMasterMode)
            Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar & (ProgramSecurity.GetProgramURL("KPITeamMaster1")), False)
        End Sub
#End Region

#Region " Custom methods"
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
                Dim objDT As DataTable = KPITeamMaster.SelectKPITeamByID(SessionManager.SelectedValue, SessionManager.SelectedValueTeamID)
                If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                    Dim objItem As ListItem
                    Dim dtRow As DataRow = objDT.Rows(0)

                    objItem = ddlKPI.Items.FindByValue(dtRow("KPIID").ToString)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                        txtKPI.Text = objItem.Text
                    End If
                    objItem = ddlTeam.Items.FindByValue(dtRow("TeamID").ToString)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                        txtTeam.Text = objItem.Text
                    End If

                    ckKPIView.Checked = Convert.ToBoolean(dtRow("AllowKPIView"))
                    ckKPIEdit.Checked = Convert.ToBoolean(dtRow("AllowKPIEdit"))
                End If


                If SessionManager.RecordTransactionCurrentValues IsNot Nothing Then
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RecordTransactionCurrentValues)
                End If
                TransactionHistory1.TableName = DBTableName
                TransactionHistory1.RecordID = SessionManager.SelectedValue.ToString & "," & SessionManager.SelectedValueTeam

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("KPI", txtKPI.Text.Trim)
                objDic.Add("Team", txtTeam.Text.Trim)
                objDic.Add("AllowView", ckKPIView.Checked.ToString)
                objDic.Add("AllowEdit", ckKPIEdit.Checked.ToString)
                SessionManager.RecordTransactionCurrentValues = objDic
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindKPISites()
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
                Dim objItem As ListItem = Nothing

                SiteMaster.SelectSiteMasterActiveList(ddlKPISite)
                If SessionManager.WorkingSiteID > 0 Then
                    objItem = ddlKPISite.Items.FindByValue(SessionManager.WorkingSiteID)
                Else
                    objItem = ddlKPISite.Items.FindByValue(UserMaster.GetUserSite(SessionManager.UserID))
                End If
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                Else
                    If ddlKPISite.Items.Count > 0 Then
                        ddlKPISite.Items(0).Selected = True
                    End If
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindKPISites", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindKPI()
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
                ddlKPI.Items.Clear()

                If ddlKPISite.SelectedItem IsNot Nothing Then
                    KPIMaster.GetKPISiteList(ddlKPI, ddlKPISite.SelectedItem.Value)
                Else
                    KPIMaster.GetKPISiteList(ddlKPI, SessionManager.WorkingSiteID)
                End If

                ddlKPI.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindKPI", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindTeams()
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
                Teams.FillTeamSelectionList(ddlTeam, SessionManager.UserID, SessionManager.WorkingSiteID, False)
                ddlTeam.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindTeams", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
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

            Select Case SessionManager.KPITeamMasterMode
                Case "EditRow"
                    ddlKPI.Visible = False
                    txtKPI.Visible = True
                    ddlKPISite.Visible = False
                    ddlTeam.Visible = False
                    txtTeam.Visible = True
                Case "ViewRow"
                    pnlOKCancel.Visible = False
                    ddlKPI.Visible = False
                    txtKPI.Visible = True
                    ddlKPISite.Visible = False
                    ddlTeam.Visible = False
                    txtTeam.Visible = True
                    ckKPIView.Enabled = False
                    ckKPIEdit.Enabled = False
                Case "DeleteRow"
                    ddlKPI.Visible = False
                    txtKPI.Visible = True
                    ddlKPISite.Visible = False
                    ddlTeam.Visible = False
                    txtTeam.Visible = True
                    ckKPIView.Enabled = False
                    ckKPIEdit.Enabled = False
            End Select
        End Sub
        Private Function InsertKPITeamMaster() As Boolean
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

                KPITeamMaster.InsertKPITeamMaster(ddlKPI.SelectedItem.Value, ddlTeam.SelectedItem.Value, ckKPIView.Checked, ckKPIEdit.Checked)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, ddlKPI.SelectedItem.Value.ToString.Trim() & "," & ddlTeam.SelectedItem.Value.ToString.Trim(), strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertKPITeamMaster", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateKPITeamMaster() As Boolean
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

                KPITeamMaster.UpdateKPITeamMaster(ddlKPI.SelectedItem.Value, ddlTeam.SelectedItem.Value, ckKPIView.Checked, ckKPIEdit.Checked)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, ddlKPI.SelectedItem.Value.ToString.Trim() & "," & ddlTeam.SelectedItem.Value.ToString.Trim(), strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertKPITeamMaster", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function DeleteKPITeamMaster() As Boolean
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
                KPITeamMaster.DeleteKPITeamMaster(SessionManager.SelectedValue, SessionManager.SelectedValueTeamID)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValue.ToString & "," & SessionManager.SelectedValueTeam, "KPI Team Deleted", SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteKPITeamMaster", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
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
            objDic.Add("KPI", ddlKPI.SelectedItem.Text.Trim)
            objDic.Add("Team", ddlTeam.SelectedItem.Text.Trim)
            objDic.Add("AllowView", ckKPIView.Checked.ToString)
            objDic.Add("AllowEdit", ckKPIEdit.Checked.ToString)

            Return objDic
        End Function
#End Region

    End Class
End Namespace

