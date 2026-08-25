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
    Partial Class TrackerPlanMaster2
        Inherits ApplicationBase

#Region " Private Variables"
        Private Shared ReadOnly FormName As String = "Master Plan Maintenance"
        Private Shared ReadOnly ProgramName As String = "TrackerPlanMaster2"
        Private Shared ReadOnly DBTableName As String = "TrackerPlanMaster"
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
                lblSavingsTracker.Text = GetTranslationString("savingstracker", lblSavingsTracker.Text.Replace(":", "")) & ":"
                lblSite.Text = GetTranslationString("team", lblSite.Text.Replace(":", "")) & ":"
                lblPillar.Text = GetTranslationString("savingscategory", lblPillar.Text.Replace(":", "")) & ":"
                lblBusinessArea.Text = GetTranslationString("businessarea", lblBusinessArea.Text.Replace(":", "")) & ":"
                lblBusinessUnit.Text = GetTranslationString("businessunit", lblBusinessUnit.Text.Replace(":", "")) & ":"
                lblSavingsCategory.Text = GetTranslationString("savingscategory", lblSavingsCategory.Text.Replace(":", "")) & ":"
                lblActive.Text = GetTranslationString("active", lblActive.Text.Replace(":", "")) & ":"
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
        Private Sub LoadAddModeJavaScripts()
            Dim myTabArray() As Object = {ddlPillar, _
                                          ddlBusinessArea, _
                                          ddlBusinessUnit, _
                                          ddlSavingsCategory, _
                                          cbActive}

            Dim TabKeyDownArr() As String = {Tab(ddlBusinessArea, cbActive, "No"), _
                                             Tab(ddlBusinessUnit, ddlPillar, "No"), _
                                             Tab(ddlSavingsCategory, ddlBusinessArea, "No"), _
                                             Tab(cbActive, ddlBusinessUnit, "No"), _
                                             Tab(ddlPillar, ddlSavingsCategory, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {cbActive}

            Dim TabKeyDownArr() As String = {Tab(cbActive, cbActive, "No")}

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

            If SessionManager.WorkingSiteID = 0 Then
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TrackerPlanMaster1"), False)
            End If

            Master.HeaderMessage = GetTranslationString(FormName, FormName) & " - " & GetTranslationString(SessionManager.TrackerPlanMode.Replace("Row", ""), SessionManager.TrackerPlanMode.Replace("Row", ""))
            Master.IconImage = Request.ApplicationPath + "/images/boss.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/" & SessionManager.CulturePref & "/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                LoadCultureTranslations()

                BindDropDownLists()

                Select Case SessionManager.TrackerPlanMode
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        pnlOKCancel.Visible = True
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Tracker Plan.');")
                        UnEnableRecords()
                        TransactionHistory1.LockControl = True
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        LoadAddModeJavaScripts()
                        txtSite.Text = SessionManager.WorkingSite
                        ddlPillar.Focus()
                        txtTrackerPlanID.Text = "New"
                        cbActive.Checked = True
                    Case "EditRow"
                        LoadEditModeJavaScripts()
                        LoadSelectedRecord()
                        UnEnableRecords()
                        cbActive.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TrackerPlanMaster1"), False)
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
            Select Case SessionManager.TrackerPlanMode
                Case "AddRow"
                    blnSuccess = InsertTrackerPlan()
                Case "EditRow"
                    blnSuccess = UpdateTrackerPlan()
                Case "DeleteRow"
                    blnSuccess = DeleteTrackerPlan()
            End Select

            Dim strReturn As String = "TrackerPlanSavings1"
            If SessionManager.TrackerPlanMode = "DeleteRow" Then
                strReturn = "TrackerPlanMaster1"
            End If
            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TrackerPlanMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strReturn), False)
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

            Dim strReturn As String = "TrackerPlanSavings1"
            If SessionManager.TrackerPlanMode = "AddRow" Then
                strReturn = "TrackerPlanMaster1"
            End If
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TrackerPlanMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strReturn), False)
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub BindDropDownLists()
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
                Pillars.SelectPillarList(ddlPillar)
                ddlPillar.Items.Insert(0, "")

                BusinessAreaMaster.GetBusinessAreaMasterList(ddlBusinessArea)
                ddlBusinessArea.Items.Insert(0, "")

                BusinessUnitMaster.SelectBusinessUnitMasterList(ddlBusinessUnit)
                ddlBusinessUnit.Items.Insert(0, "")

                SavingsCategoryMaster.GetSavingsCategoryList(ddlSavingsCategory)
                ddlSavingsCategory.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - SelectTeamList", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                Return
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

            Dim objDT As DataTable = TrackerPlanMaster.SelectTrackerPlan(SessionManager.SelectedValueTrackerPlanID)
            If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                Dim dtRow As DataRow = objDT.Rows(0)
                Dim objItem As ListItem

                If dtRow("PillarAbbrev").ToString.Trim.Length = 0 AndAlso dtRow("BusinessAreaID").ToString.Trim.Length = 0 AndAlso _
                dtRow("BusinessUnitID").ToString.Trim.Length = 0 AndAlso dtRow("SavingsCategoryID").ToString.Trim.Length = 0 Then
                    SessionManager.TrackerPlanMode = "ViewRow"
                End If

                txtTrackerPlanID.Text = SessionManager.SelectedValueTrackerPlanID
                txtSite.Text = SessionManager.WorkingSite
                objItem = ddlPillar.Items.FindByValue(dtRow("PillarAbbrev").ToString)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                    txtPillar.Text = objItem.Text
                End If
                objItem = ddlBusinessArea.Items.FindByValue(dtRow("BusinessAreaID").ToString)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                    txtBusinessArea.Text = objItem.Text
                End If
                objItem = ddlBusinessUnit.Items.FindByValue(dtRow("BusinessUnitID").ToString)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                    txtBusinessUnit.Text = objItem.Text
                End If
                objItem = ddlSavingsCategory.Items.FindByValue(dtRow("SavingsCategoryID").ToString)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                    txtSavingsCategory.Text = objItem.Text
                End If
                cbActive.Checked = Convert.ToBoolean(dtRow("Active").ToString)

                TransactionHistory1.TableName = DBTableName
                TransactionHistory1.RecordID = SessionManager.SelectedValueTrackerPlanID.ToString

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("Site", txtSite.Text.Trim())
                objDic.Add("Pillar", txtPillar.Text.Trim)
                objDic.Add("BusinessArea", txtBusinessArea.Text.Trim)
                objDic.Add("BusinessUnit", txtBusinessUnit.Text.Trim)
                objDic.Add("SavingsCategory", txtSavingsCategory.Text.Trim)
                objDic.Add("Active", cbActive.Checked.ToString)

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

            Select Case SessionManager.TrackerPlanMode.ToString()

                Case "ViewRow"
                    pnlExit.Visible = True
                    pnlOKCancel.Visible = False
                    ddlPillar.Visible = False
                    txtPillar.Visible = True
                    ddlBusinessArea.Visible = False
                    txtBusinessArea.Visible = True
                    ddlBusinessUnit.Visible = False
                    txtBusinessUnit.Visible = True
                    ddlSavingsCategory.Visible = False
                    txtSavingsCategory.Visible = True
                    cbActive.Enabled = False
                Case "EditRow"
                    ddlPillar.Visible = False
                    txtPillar.Visible = True
                    ddlBusinessArea.Visible = False
                    txtBusinessArea.Visible = True
                    ddlBusinessUnit.Visible = False
                    txtBusinessUnit.Visible = True
                    ddlSavingsCategory.Visible = False
                    txtSavingsCategory.Visible = True
                Case "DeleteRow"
                    pnlExit.Visible = False
                    pnlOKCancel.Visible = True
                    ddlPillar.Visible = False
                    txtPillar.Visible = True
                    ddlBusinessArea.Visible = False
                    txtBusinessArea.Visible = True
                    ddlBusinessUnit.Visible = False
                    txtBusinessUnit.Visible = True
                    ddlSavingsCategory.Visible = False
                    txtSavingsCategory.Visible = True
                    cbActive.Enabled = False
            End Select
        End Sub
        Private Function InsertTrackerPlan() As Boolean
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
                Dim strPillarAbbrev As String = ""
                Dim iBusinessUnitID As Integer = -1
                Dim iSavingsCategoryID As Integer = -1

                If ddlPillar.SelectedItem IsNot Nothing AndAlso ddlPillar.SelectedItem.Value.ToString.Trim.Length > 0 Then
                    strPillarAbbrev = ddlPillar.SelectedItem.Value.ToString.Trim
                End If
                If ddlBusinessUnit.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlBusinessUnit.SelectedItem.Value) Then
                    iBusinessUnitID = Convert.ToInt32(ddlBusinessUnit.SelectedItem.Value)
                End If
                If ddlSavingsCategory.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlSavingsCategory.SelectedItem.Value) Then
                    iSavingsCategoryID = Convert.ToInt32(ddlSavingsCategory.SelectedItem.Value)
                End If

                SessionManager.SelectedValueTrackerPlanID = TrackerPlanMaster.InsertTrackerPlan(SessionManager.WorkingSiteID, strPillarAbbrev, ddlBusinessArea.SelectedItem.Value, iBusinessUnitID, iSavingsCategoryID, cbActive.Checked)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueTrackerPlanID.ToString, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertTrackerPlan", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateTrackerPlan() As Boolean
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
                Dim strPillarAbbrev As String = ""
                Dim iBusinessUnitID As Integer = -1
                Dim iSavingsCategoryID As Integer = -1

                If ddlPillar.SelectedItem IsNot Nothing AndAlso ddlPillar.SelectedItem.Value.ToString.Trim.Length > 0 Then
                    strPillarAbbrev = ddlPillar.SelectedItem.Value.ToString.Trim
                End If
                If ddlBusinessUnit.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlBusinessUnit.SelectedItem.Value) Then
                    iBusinessUnitID = Convert.ToInt32(ddlBusinessUnit.SelectedItem.Value)
                End If
                If ddlSavingsCategory.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlSavingsCategory.SelectedItem.Value) Then
                    iSavingsCategoryID = Convert.ToInt32(ddlSavingsCategory.SelectedItem.Value)
                End If

                TrackerPlanMaster.UpdateTrackerPlan(SessionManager.SelectedValueTrackerPlanID, SessionManager.WorkingSiteID, strPillarAbbrev, ddlBusinessArea.SelectedItem.Value, iBusinessUnitID, iSavingsCategoryID, cbActive.Checked)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueTrackerPlanID.ToString, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateTrackerPlan", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function DeleteTrackerPlan() As Boolean
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
                TrackerPlanMaster.DeleteTrackerPlan(SessionManager.SelectedValueTrackerPlanID)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueTrackerPlanID.ToString, "Tracker Plan Deleted", SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteTrackerPlan", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
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
            objDic.Add("Site", txtSite.Text.Trim)
            If ddlPillar.SelectedItem IsNot Nothing Then
                objDic.Add("Pillar", ddlPillar.SelectedItem.Text.Trim)
            Else
                objDic.Add("Pillar", "")
            End If
            If ddlBusinessArea.SelectedItem IsNot Nothing Then
                objDic.Add("BusinessArea", ddlBusinessArea.SelectedItem.Text.Trim)
            Else
                objDic.Add("BusinessArea", "")
            End If
            If ddlBusinessUnit.SelectedItem IsNot Nothing Then
                objDic.Add("BusinessUnit", ddlBusinessUnit.SelectedItem.Text.Trim)
            Else
                objDic.Add("BusinessUnit", "")
            End If
            If ddlSavingsCategory.SelectedItem IsNot Nothing Then
                objDic.Add("SavingsCategory", ddlSavingsCategory.SelectedItem.Text.Trim)
            Else
                objDic.Add("SavingsCategory", "")
            End If
            objDic.Add("Active", cbActive.Checked.ToString)

            Return objDic
        End Function
#End Region

    End Class
End Namespace
