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
    Partial Class TrackerTypes2
        Inherits ApplicationBase

#Region " Private Variables"
        Private Shared ReadOnly FormName As String = "Savings Types"
        Private Shared ReadOnly ProgramName As String = "TrackerTypes2"
        Private Shared ReadOnly DBTableName As String = "TrackerTypes"
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
            Dim myTabArray() As Object = {txtTrackerType}

            Dim TabKeyDownArr() As String = {Tab(txtTrackerType, txtTrackerType, "No")}

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

            Master.HeaderMessage = FormName & " - " & SessionManager.TrackerTypeMode.Replace("Row", "")
            Master.IconImage = Request.ApplicationPath + "/images/boss.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                Select Case SessionManager.TrackerTypeMode.ToString()
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        pnlOKCancel.Visible = True
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Savings Type.');")
                        TransactionHistory1.LockControl = True
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        txtTrackerTypeID.Text = "New"
                        LoadAddEditModeJavaScripts()
                        txtTrackerType.Focus()
                    Case "EditRow"
                        LoadAddEditModeJavaScripts()
                        LoadSelectedRecord()
                        UnEnableRecords()
                        txtTrackerType.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TrackerTypes1"), False)
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
            Select Case SessionManager.TrackerTypeMode.ToString()
                Case "AddRow"
                    blnSuccess = InsertTrackerType()
                Case "EditRow"
                    blnSuccess = UpdateTrackerType()
                Case "DeleteRow"
                    blnSuccess = DeleteTrackerType()
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TrackerTypeMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TrackerTypes1"), False)
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
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TrackerTypeMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TrackerTypes1"), False)
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

            Dim objDT As DataTable = TrackerTypes.SelectTrackerType(Convert.ToInt16(SessionManager.SelectedValue))
            If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                Dim dtRow As DataRow = objDT.Rows(0)

                txtTrackerTypeID.Text = SessionManager.SelectedValue
                txtTrackerType.Text = dtRow("TrackerType").ToString

                TransactionHistory1.TableName = DBTableName
                TransactionHistory1.RecordID = SessionManager.SelectedValue.Trim()

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("TrackerType", txtTrackerType.Text.Trim())
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

            Select Case SessionManager.TrackerTypeMode.ToString()
                Case "ViewRow", "DeleteRow"
                    pnlOKCancel.Visible = False
                    txtTrackerType.ReadOnly = True
                    txtTrackerType.CssClass = "Textbox_Display"
            End Select
        End Sub
        Private Function InsertTrackerType() As Boolean
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

                Dim iTrackerTypeID As Integer = TrackerTypes.AddTrackerType(txtTrackerType.Text.Trim)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, iTrackerTypeID.ToString, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertTrackerType", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateTrackerType() As Boolean
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

                TrackerTypes.UpdateTrackerType(SessionManager.SelectedValue.Trim(), txtTrackerType.Text.Trim)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValue.Trim(), strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateTrackerType", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function DeleteTrackerType() As Boolean
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
                TrackerTypes.DeleteTrackerType(SessionManager.SelectedValue.Trim())
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValue.Trim(), "Savings Type Deleted", SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteTrackerType", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
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
            objDic.Add("TrackerType", txtTrackerType.Text.Trim())
            Return objDic
        End Function
#End Region

    End Class
End Namespace
