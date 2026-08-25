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
    Partial Class FXRates3
        Inherits ApplicationBase

#Region " Private Variables"
        Private Shared ReadOnly FormName As String = "FX Rates"
        Private Shared ReadOnly ProgramName As String = "FXRates3"
        Private Shared ReadOnly DBTableName As String = "FXRates"
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
            Dim myTabArray() As Object = {txtPeriod, _
                                          txtRate}

            Dim TabKeyDownArr() As String = {Tab(txtRate, txtRate, "No"), _
                                             Tab(txtPeriod, txtPeriod, "Yes")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {txtRate}

            Dim TabKeyDownArr() As String = {Tab(txtRate, txtRate, "Yes")}

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

            Master.HeaderMessage = FormName & " - " & SessionManager.AreaMaintenanceMode.Replace("Row", "")
            Master.IconImage = Request.ApplicationPath + "/images/boss.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                mcFXRateElement.StoredProcedureParams.Add("@FXRateID", SessionManager.SelectedValueFXRateID)
                mcFXRateElement.DataBind()

                Select Case SessionManager.FXRateMode
                    Case "ViewRow"
                        pnlExit.Visible = True
                        pnlOKCancel.Visible = False
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        pnlOKCancel.Visible = True
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this FX Rate.');")
                        TransactionHistory1.LockControl = True
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        LoadAddModeJavaScripts()
                        txtPeriod.Focus()
                    Case "EditRow"
                        LoadEditModeJavaScripts()
                        LoadSelectedRecord()
                        UnEnableRecords()
                        txtRate.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("FXRates2"), False)
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
            Select Case SessionManager.FXRateMode
                Case "AddRow"
                    blnSuccess = InsertRate()
                Case "EditRow"
                    blnSuccess = UpdateRate()
                Case "DeleteRow"
                    blnSuccess = DeleteRate()
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.FXRateMode)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.AreaMaintenanceMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("FXRates2"), False)
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.AreaMaintenanceMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("FXRates2"), False)
        End Sub
#End Region

#Region " Custom Methods"
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

            Dim objDT As DataTable = FXRates.SelectFXRateByID(SessionManager.SelectedValueFXRateID, SessionManager.SelectedValueFXRatePeriod)
            If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                Dim dtRow As DataRow = objDT.Rows(0)

                If IsDate(dtRow("FXRatePeriod").ToString) Then
                    txtPeriod.Text = Convert.ToDateTime(dtRow("FXRatePeriod").ToString).ToString("yyyy/MM/dd")
                Else
                    txtPeriod.Text = dtRow("FXRatePeriod").ToString
                End If
                txtRate.Text = dtRow("FXRate").ToString
                If IsDate(dtRow("LastUpdated").ToString) Then
                    txtLastUpdated.Text = Convert.ToDateTime(dtRow("LastUpdated").ToString).ToString("yyyy/MM/dd hh:mm")
                Else
                    txtLastUpdated.Text = dtRow("LastUpdated").ToString
                End If

                TransactionHistory1.TableName = DBTableName
                TransactionHistory1.RecordID = SessionManager.SelectedValueFXRateID.ToString & "," & SessionManager.SelectedValueFXRatePeriod

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("Period", txtPeriod.Text.Trim())
                objDic.Add("Rate", txtRate.Text.Trim())
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

            Select Case SessionManager.FXRateMode
                Case "ViewRow", "DeleteRow"
                    pnlOKCancel.Visible = False
                    txtPeriod.ReadOnly = True
                    txtPeriod.CssClass = "Textbox_Display"
                    txtRate.ReadOnly = True
                    txtRate.CssClass = "Textbox_Display"
                Case "EditRow"
                    txtPeriod.ReadOnly = True
                    txtPeriod.CssClass = "Textbox_Display"
            End Select
        End Sub
        Private Function InsertRate() As Boolean
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

                FXRates.InsertFXRate(SessionManager.SelectedValueFXRateID, txtPeriod.Text, Convert.ToDouble(txtRate.Text))
                Dim strPeriod As String = Convert.ToDateTime(txtPeriod.Text).ToString("yyyy/MM/dd")

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueFXRateID.ToString & "," & strPeriod, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertArea", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateRate() As Boolean
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

                FXRates.UpdateFXRate(SessionManager.SelectedValueFXRateID, SessionManager.SelectedValueFXRatePeriod, Convert.ToDouble(txtRate.Text))

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueFXRateID.ToString & "," & SessionManager.SelectedValueFXRatePeriod, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateArea", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function DeleteRate() As Boolean
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
                FXRates.DeleteFXRate(SessionManager.SelectedValueFXRateID, SessionManager.SelectedValueFXRatePeriod)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueFXRateID.ToString & "," & SessionManager.SelectedValueFXRatePeriod, "FX Rate Deleted", SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteArea", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
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
            objDic.Add("Period", txtPeriod.Text.Trim())
            objDic.Add("Rate", txtRate.Text.Trim())

            Return objDic
        End Function
#End Region

    End Class
End Namespace
