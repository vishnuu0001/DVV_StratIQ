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
    Partial Class OEEReports2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "OEEReports"
        Private Shared ReadOnly ProgramName As String = "OEEReports2"
        Private Shared ReadOnly DBTableName As String = "OEEReports"
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
            Dim myTabArray() As Object = {txtWorkcenter, txtReport, txtURL}

            Dim TabKeyDownArr() As String = {Tab(txtReport, txtURL, "No"), _
                                                Tab(txtURL, txtWorkcenter, "No"), _
                                                Tab(txtWorkcenter, txtReport, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {txtWorkcenter, txtReport, txtURL}

            Dim TabKeyDownArr() As String = {Tab(txtReport, txtURL, "No"), _
             Tab(txtURL, txtWorkcenter, "No"), _
             Tab(txtWorkcenter, txtReport, "No")}

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

            Master.HeaderMessage = FormName & " - " & SessionManager.OEEReportsMode.Replace("Row", "")
            Master.IconImage = Request.ApplicationPath + "/images/padlock.gif"

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                If SessionManager.OEEReportsMode = "DeleteRow" Then
                    LoadSelectedRecord()
                    UnEnableRecords()
                    pnlOKCancel.Visible = True
                    btnOK.CausesValidation = False
                    btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this OEEReports record.');")
                    TransactionHistory1.LockControl = True
                ElseIf SessionManager.OEEReportsMode = "EditRow" Then
                    LoadSelectedRecord()
                    UnEnableRecords()
                    LoadAddModeJavaScripts()
                    txtURL.Focus()
                ElseIf SessionManager.OEEReportsMode = "AddRow" Then
                    TransactionHistory1.Visible = False
                    LoadAddModeJavaScripts()
                    txtWorkcenter.Focus()
                Else
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("CultureMaster1"), False)
                End If
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

            If SessionManager.OEEReportsMode = "DeleteRow" Then
                blnSuccess = DeleteOEEReports()
            ElseIf SessionManager.OEEReportsMode = "EditRow" Then
                blnSuccess = UpdateOEEReports()
            ElseIf SessionManager.OEEReportsMode = "AddRow" Then
                blnSuccess = InsertOEEReports()
            End If

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.OEEReportsMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("OEEReports1"), False)
            End If
        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.OEEReportsMode = "View" Or SessionManager.OEEReportsMode = "Delete" Or SessionManager.OEEReportsMode = "AddRow" Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.OEEReportsMode)
            End If
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("OEEReports1"), False)
        End Sub

        Private Sub btnCancel_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnCancel.Click
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
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.OEEReportsMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("OEEReports1"), False)
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

            txtWorkcenter.Text = SessionManager.SelectedValue
            txtReport.Text = SessionManager.SelectedValue1
            txtURL.Text = SessionManager.SelectedValue2

            TransactionHistory1.TableName = DBTableName
            TransactionHistory1.RecordID = SessionManager.WorkingSiteID & "," & txtWorkcenter.Text.Trim() & "," & txtReport.Text.Trim()

            Dim objDic As New Dictionary(Of String, String)
            objDic.Add("WorkCenter", txtWorkcenter.Text.Trim())
            objDic.Add("Report", txtReport.Text.Trim())
            objDic.Add("URL", txtURL.Text.Trim())
            SessionManager.RecordTransactionCurrentValues = objDic
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

            If SessionManager.OEEReportsMode = "DeleteRow" Then
                pnlOKCancel.Visible = True
                txtWorkcenter.ReadOnly = True
                txtWorkcenter.CssClass = "Textbox_Display"
                txtReport.ReadOnly = True
                txtReport.CssClass = "Textbox_Display"
                txtURL.ReadOnly = True
                txtURL.CssClass = "Textbox_Display"
            ElseIf SessionManager.OEEReportsMode = "EditRow" Then
                pnlOKCancel.Visible = True
                txtWorkcenter.ReadOnly = True
                txtWorkcenter.CssClass = "Textbox_Display"
                txtReport.ReadOnly = True
                txtReport.CssClass = "Textbox_Display"
            End If
        End Sub
        Private Function InsertOEEReports() As Boolean
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

                OEEReports.AddOEEREPORTS(SessionManager.WorkingSiteID, txtWorkcenter.Text, txtReport.Text, txtURL.Text)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.WorkingSiteID & "," & txtWorkcenter.Text.Trim() & "," & txtReport.Text.Trim(), strChangeLog, SessionManager.UserID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertOEEReports", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
            Return True
        End Function
        Private Function UpdateOEEReports() As Boolean
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

                OEEReports.UpdateOEEREPORTS(SessionManager.WorkingSiteID, txtWorkcenter.Text, txtReport.Text, txtURL.Text)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.WorkingSiteID & "," & txtWorkcenter.Text.Trim() & "," & txtReport.Text.Trim(), strChangeLog, SessionManager.UserID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateOEEReports", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
            Return True
        End Function

        Private Function DeleteOEEReports() As Boolean
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
                OEEReports.DeleteOEEREPORTS(SessionManager.WorkingSiteID, txtWorkcenter.Text, txtReport.Text)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.WorkingSiteID & "," & txtWorkcenter.Text.Trim() & "," & txtReport.Text.Trim(), "OEE Report Deleted", SessionManager.UserID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteOEEReports", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
            Return True
        End Function
        Private Function GetUpdatedValues() As Dictionary(Of String, String)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim objDic As New Dictionary(Of String, String)
            objDic.Add("WorkCenter", txtWorkcenter.Text.Trim())
            objDic.Add("Report", txtReport.Text.Trim())
            objDic.Add("URL", txtURL.Text.Trim())
            Return objDic
        End Function
#End Region

    End Class
End Namespace