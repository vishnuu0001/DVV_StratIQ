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
    Partial Class TrackerPlanSavings2
        Inherits ApplicationBase

#Region " Private Variables"
        Private Shared ReadOnly FormName As String = "Master Plan Maintenance"
        Private Shared ReadOnly ProgramName As String = "TrackerPlanSavings2"
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
                lblPeriod.Text = GetTranslationString("team", lblPeriod.Text.Replace(":", "")) & ":"
                lblSavings.Text = GetTranslationString("plansavings", lblSavings.Text.Replace(":", "")) & ":"
                lblStretch.Text = GetTranslationString("stretchsavings", lblStretch.Text.Replace(":", "")) & ":"
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
            Dim myTabArray() As Object = {txtPeriod, _
                                          txtPlanSavings, _
                                          txtStretchSavings}

            Dim TabKeyDownArr() As String = {Tab(txtPlanSavings, txtStretchSavings, "No"), _
                                             Tab(txtStretchSavings, txtPeriod, "Yes"), _
                                             Tab(txtPeriod, txtPlanSavings, "Yes")}

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

            Master.HeaderMessage = GetTranslationString(FormName, FormName) & " - " & GetTranslationString(SessionManager.TrackerPlanMode.Replace("Row", ""), SessionManager.TrackerPlanMode.Replace("Row", ""))
            Master.IconImage = Request.ApplicationPath + "/images/boss.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/" & SessionManager.CulturePref & "/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                LoadCultureTranslations()

                Select Case SessionManager.TrackerPlanSavingsMode
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        pnlOKCancel.Visible = True
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Plan Savings.');")
                        TransactionHistory1.LockControl = True
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        LoadAddEditModeJavaScripts()
                        txtPeriod.Focus()
                    Case "EditRow"
                        LoadAddEditModeJavaScripts()
                        LoadSelectedRecord()
                        UnEnableRecords()
                        txtPlanSavings.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TrackerPlanSavings1"), False)
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
            Select Case SessionManager.TrackerPlanSavingsMode
                Case "AddRow"
                    blnSuccess = InsertPlanSavings()
                Case "EditRow"
                    blnSuccess = UpdatePlanSavings()
                Case "DeleteRow"
                    blnSuccess = DeletePlanSavings()
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueTrackerPlanSavingsID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TrackerPlanSavingsMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TrackerPlanSavings1"), False)
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueTrackerPlanSavingsID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TrackerPlanSavingsMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TrackerPlanSavings1"), False)
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

            If SessionManager.RecordTransactionCurrentValues IsNot Nothing Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RecordTransactionCurrentValues)
            End If

            Dim objDT As DataTable = TrackerPlanSavings.SelectTrackerPlanSavingsByID(SessionManager.SelectedValueTrackerPlanSavingsID)
            If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                Dim dtRow As DataRow = objDT.Rows(0)

                txtPeriod.Text = dtRow("TrackerPeriod").ToString
                txtPlanSavings.Text = dtRow("TrackerPlanSavings").ToString
                txtStretchSavings.Text = dtRow("TrackerStretchSavings").ToString

                TransactionHistory1.TableName = DBTableName
                TransactionHistory1.RecordID = SessionManager.SelectedValueTrackerID.ToString

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("Period", txtPeriod.Text.Trim())
                objDic.Add("Savings", txtPlanSavings.Text.Trim)
                objDic.Add("Stretch", txtStretchSavings.Text.Trim)

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

            Select Case SessionManager.TrackerPlanSavingsMode
                Case "ViewRow", "DeleteRow"
                    pnlOKCancel.Visible = False
                    txtPeriod.ReadOnly = True
                    txtPeriod.CssClass = "Textbox_Display"
                    txtPlanSavings.ReadOnly = True
                    txtPlanSavings.CssClass = "Textbox_Display"
                    txtStretchSavings.ReadOnly = True
                    txtStretchSavings.CssClass = "Textbox_Display"
            End Select
        End Sub
        Private Function InsertPlanSavings() As Boolean
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
                If String.IsNullOrEmpty(txtPlanSavings.Text.Trim) And Not String.IsNullOrEmpty(txtStretchSavings.Text.Trim) _
                OrElse String.IsNullOrEmpty(txtPlanSavings.Text.Trim) And Not String.IsNullOrEmpty(txtStretchSavings.Text.Trim) Then
                    Master.DisplayError("Enter both plan values.")
                    Return False
                End If

                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                TrackerPlanSavings.InsertPlanSavings(SessionManager.SelectedValueTrackerPlanID, RegionalConversion.FormatSQLDate(txtPeriod.Text, False), txtPlanSavings.Text.Trim, txtStretchSavings.Text.Trim)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueTrackerPlanID.ToString, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertTrackerPlan", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdatePlanSavings() As Boolean
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
                If String.IsNullOrEmpty(txtPlanSavings.Text.Trim) And Not String.IsNullOrEmpty(txtStretchSavings.Text.Trim) _
                OrElse String.IsNullOrEmpty(txtPlanSavings.Text.Trim) And Not String.IsNullOrEmpty(txtStretchSavings.Text.Trim) Then
                    Master.DisplayError("Enter both plan values or clear both values to delete the plan entry.")
                    Return False
                End If

                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.CompareDictionaryValues(SessionManager.RecordTransactionCurrentValues, objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                TrackerPlanSavings.UpdatePlanSavings(SessionManager.SelectedValueTrackerPlanSavingsID, RegionalConversion.FormatSQLDate(txtPeriod.Text.Trim, False), txtPlanSavings.Text.Trim, txtStretchSavings.Text.Trim)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueTrackerPlanID.ToString, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateTrackerPlan", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function DeletePlanSavings() As Boolean
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
                TrackerPlanSavings.DeletePlanSavings(SessionManager.SelectedValueTrackerPlanSavingsID)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueTrackerPlanID.ToString, "Tracker Plan Savings Deleted", SessionManager.UserID)

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

            objDic.Add("Period", txtPeriod.Text.Trim)
            objDic.Add("Savings", txtPlanSavings.Text.Trim)
            objDic.Add("Stretch", txtStretchSavings.Text.Trim)

            Return objDic
        End Function
#End Region

    End Class
End Namespace
