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
    Partial Class ReportingLevelMaster2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Reporting Level Master"
        Private Shared ReadOnly ProgramName As String = "ReportingLevelMaster2"
        Private Shared ReadOnly DBTableName As String = "ReportingLevelMaster"
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
        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {txtReportingLevelDescription, _
                                          txtReportingLevelAbbrev, _
                                          txtReportingLevel}

            Dim TabKeyDownArr() As String = {Tab(txtReportingLevelAbbrev, txtReportingLevel, "No"), _
                                             Tab(txtReportingLevel, txtReportingLevelDescription, "No"), _
                                             Tab(txtReportingLevelDescription, txtReportingLevelAbbrev, "No")}

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

            Master.HeaderMessage = FormName & " - " & SessionManager.Mode.Replace("Row", "")
            Master.IconImage = Request.ApplicationPath + "/images/community-users.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")
            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                Select Case SessionManager.Mode
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "EditRow"
                        LoadSelectedRecord()
                        LoadEditModeJavaScripts()
                        txtReportingLevelDescription.Focus()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Reporting Level.');")
                        TransactionHistory1.LockControl = True
                    Case "AddRow"
                        txtReportingLevelID.Text = "New"
                        TransactionHistory1.Visible = False
                        LoadEditModeJavaScripts()
                        txtReportingLevelDescription.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("ReportingLevelMaster1"), False)
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
                    blnSuccess = InsertReportingLevel()
                Case "EditRow"
                    blnSuccess = UpdateReportingLevel()
                Case "DeleteRow"
                    blnSuccess = DeleteReportingLevel()
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Mode)

                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("ReportingLevelMaster1"), False)
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
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Mode)

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("ReportingLevelMaster1"), False)
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

            Dim objDT As DataTable = ReportingLevelMaster.SelectReportingLevelMaster(SessionManager.SelectedValue)

            If objDT IsNot Nothing AndAlso objDT.Rows.Count > 0 Then
                Dim dtRow As DataRow = objDT.Rows(0)

                txtReportingLevelID.Text = SessionManager.SelectedValue
                txtReportingLevelDescription.Text = dtRow("ReportingLevelDescription").ToString
                txtReportingLevelAbbrev.Text = dtRow("ReportingLevelAbbrev").ToString
                txtReportingLevel.Text = dtRow("ReportingLevel").ToString
            End If

            TransactionHistory1.TableName = DBTableName
            TransactionHistory1.RecordID = SessionManager.SelectedValue

            Dim objDic As New Dictionary(Of String, String)
            objDic.Add("Description", txtReportingLevelDescription.Text.Trim)
            objDic.Add("Abbrev", txtReportingLevelAbbrev.Text.Trim)
            objDic.Add("Level", txtReportingLevel.Text)
            SessionManager.RecordTransactionCurrentValues = objDic
        End Sub
        Private Sub UnEnableRecords()
            If SessionManager.Mode = "ViewRow" Then
                pnlOKCancel.Visible = False
                txtReportingLevelDescription.ReadOnly = True
                txtReportingLevelDescription.CssClass = "Textbox_Display"
                txtReportingLevelAbbrev.ReadOnly = True
                txtReportingLevelAbbrev.CssClass = "Textbox_Display"
                txtReportingLevel.ReadOnly = True
                txtReportingLevel.CssClass = "Textbox_Display"
            ElseIf SessionManager.Mode = "DeleteRow" Then
                txtReportingLevelDescription.ReadOnly = True
                txtReportingLevelDescription.CssClass = "Textbox_Display"
                txtReportingLevelAbbrev.ReadOnly = True
                txtReportingLevelAbbrev.CssClass = "Textbox_Display"
                txtReportingLevel.ReadOnly = True
                txtReportingLevel.CssClass = "Textbox_Display"
            End If
        End Sub
        Private Function InsertReportingLevel() As Boolean
            Try
                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                Dim iReportingLevel As Integer = ReportingLevelMaster.AddReportingLevelMaster(txtReportingLevelDescription.Text.Trim, txtReportingLevelAbbrev.Text.Trim, Convert.ToInt16(txtReportingLevel.Text))
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, iReportingLevel.ToString, strChangeLog, SessionManager.UserID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertReportingLevel", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
            Return True
        End Function
        Private Function UpdateReportingLevel() As Boolean
            Try
                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.CompareDictionaryValues(SessionManager.RecordTransactionCurrentValues, objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                ReportingLevelMaster.UpdateReportingLevelMaster(SessionManager.SelectedValue, txtReportingLevelDescription.Text.Trim, txtReportingLevelAbbrev.Text.Trim, Convert.ToInt16(txtReportingLevel.Text))
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValue, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateReportingLevel", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function DeleteReportingLevel() As Boolean
            Try
                ReportingLevelMaster.DeleteReportingLevelMaster(SessionManager.SelectedValue)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValue, "Reporting Level Deleted", SessionManager.UserID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteRole", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try

            Return True
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
            objDic.Add("Description", txtReportingLevelDescription.Text.Trim)
            objDic.Add("Abbrev", txtReportingLevelAbbrev.Text.Trim)
            objDic.Add("Level", txtReportingLevel.Text)

            Return objDic
        End Function
#End Region

    End Class
End Namespace
