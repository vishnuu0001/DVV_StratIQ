#Region " Imports "

Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper

Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.SLICETables
Imports WebApp.APlus.UI.CustomControls
Imports WebApp.APlus.DataAccess.Tables
Imports System.Collections.Generic

#End Region

Namespace WebApp.APlus.UI.SLICE
    Partial Class SLICEResultMaster2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "SLICE Result"
        Private Shared ReadOnly ProgramName As String = "SLICEResultMaster2"
        Private Shared ReadOnly DBTableName As String = "SLICEResultMaster"
#End Region

#Region "Load JavaScripts"
        Private Sub LoadCommonJavaScripts()

            Dim StatusArr() As WebControl = {btnOK, btnCancel, btnExit}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel", "Exit"}
            Dim OutMessageArr() As String = {"", "", ""}
            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)
            txtPresentationSequence.Attributes.Add("onkeydown", "javascript:AllowIntegers(window.event);")

        End Sub

        Private Sub LoadAddModeJavaScripts()
            Dim myTabArray() As Object = {txtSLICEResultID, _
                                          txtSLICEResultText, _
                                          chkPass}
            Dim TabKeyDownArr() As String = {Tab(txtSLICEResultText, chkPass, "YES"), _
                                             Tab(chkPass, txtSLICEResultID, "No"), _
                                             Tab(txtSLICEResultID, txtSLICEResultText, "No")}
            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
#End Region

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Master.HeaderMessage = FormName & " - " & SessionManager.SLICEResultMasterMode & " SLICE Result Master"
            Master.IconImage = Request.ApplicationPath + "/images/clipboard.png"
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnOK.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:IgnoreTab(window.event)")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event")
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                If SessionManager.SLICEResultMasterMode = "ViewRow" Then
                    pnlExit.Visible = True
                    LoadSelectedRecord()
                    UnEnableRecords()
                ElseIf SessionManager.SLICEResultMasterMode = "EditRow" Then
                    LoadSelectedRecord()
                    UnEnableRecords()
                    txtSLICEResultText.Focus()
                ElseIf SessionManager.SLICEResultMasterMode = "DeleteRow" Then
                    LoadSelectedRecord()
                    UnEnableRecords()
                    btnOK.CausesValidation = False
                    btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this SLICE Result.');")
                    TransactionHistory1.LockControl = True
                ElseIf SessionManager.SLICEResultMasterMode = "AddRow" Then
                    TransactionHistory1.Visible = False
                    LoadAddModeJavaScripts()
                    UnEnableRecords()
                    txtSLICEResultID.Focus()
                Else
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEResultMaster1"), False)
                End If
            End If
        End Sub
        Private Sub btnOK_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim blnSuccess As Boolean

            If SessionManager.SLICEResultMasterMode = "DeleteRow" Then
                blnSuccess = DeleteSLICEResult()
            ElseIf SessionManager.SLICEResultMasterMode = "AddRow" Then
                blnSuccess = InsertSLICEResult()
            ElseIf SessionManager.SLICEResultMasterMode = "EditRow" Then
                blnSuccess = UpdateSLICEResult()
            End If

            If blnSuccess Then
                Master.WriteErrors(FormName, SessionManager.SLICEResultMasterMode & " SLICEResult " & txtSLICEResultText.Text, SessionManager.UserID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueSLICEResultID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SLICEResultMasterMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEResultMaster1"), False)
            End If
        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.SLICEResultMasterMode = "EditRow" Or SessionManager.SLICEResultMasterMode = "ViewRow" Or SessionManager.SLICEResultMasterMode = "DeleteRow" Or SessionManager.SLICEResultMasterMode = "AddRow" Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueSLICEResultID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SLICEResultMasterMode)
            End If
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEResultMaster1"), False)
        End Sub
        Private Sub btnCancel_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnCancel.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueSLICEResultID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SLICEResultMasterMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEResultMaster1"), False)
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadSelectedRecord()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim dt As DataTable = SLICEResultMaster.SelectSLICEResultMasterByID(SessionManager.SelectedValueSLICEResultID)
                If dt.Rows.Count > 0 Then
                    txtSLICEResultID.Text = dt.Rows(0)("SLICEResultID").ToString().Trim()
                    txtSLICEResultText.Text = dt.Rows(0)("SLICEResultText").ToString().Trim()
                    txtPresentationSequence.Text = dt.Rows(0)("PresentationSequence").ToString().Trim()
                    chkPass.Checked = dt.Rows(0)("Pass").ToString().Trim()
                Else
                    txtSLICEResultID.Text = ""
                    txtSLICEResultText.Text = ""
                    txtPresentationSequence.Text = ""
                    chkPass.Checked = False
                End If
                TransactionHistory1.TableName = DBTableName
                TransactionHistory1.RecordID = SessionManager.SelectedValueSLICEResultID

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("SLICEResultText", txtSLICEResultText.Text.Trim())
                objDic.Add("Pass", chkPass.Checked)
                objDic.Add("PresentationSequence", txtPresentationSequence.Text.Trim())
                SessionManager.RecordTransactionCurrentValues = objDic

            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
            End Try
        End Sub

        Private Sub UnEnableRecords()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.SLICEResultMasterMode = "ViewRow" Then
                pnlOKCancel.Visible = False
                txtSLICEResultText.ReadOnly = True
                txtSLICEResultText.CssClass = "Textbox_Display"
                chkPass.Enabled = False
                txtPresentationSequence.ReadOnly = True
                txtPresentationSequence.CssClass = "Textbox_Display"
            ElseIf SessionManager.SLICEResultMasterMode = "AddRow" Then
                txtSLICEResultID.ReadOnly = True
                txtSLICEResultID.Text = "New"
                txtSLICEResultText.Focus()
            ElseIf SessionManager.SLICEResultMasterMode = "DeleteRow" Then
                txtSLICEResultText.ReadOnly = True
                txtSLICEResultText.CssClass = "Textbox_Display"
                chkPass.Enabled = False
                txtPresentationSequence.ReadOnly = True
                txtPresentationSequence.CssClass = "Textbox_Display"
            End If
        End Sub

        Private Function InsertSLICEResult() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
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
                Dim intResult As Integer = SLICEResultMaster.AddSLICEResultMaster(txtSLICEResultText.Text.Trim, chkPass.Checked, txtPresentationSequence.Text.Trim)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, intResult, strChangeLog, SessionManager.UserID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertSLICEResult", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
            Return True
        End Function

        Private Function UpdateSLICEResult() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
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

                SLICEResultMaster.UpdateSLICEResultMaster(SessionManager.SelectedValueSLICEResultID, txtSLICEResultText.Text.Trim, chkPass.Checked, txtPresentationSequence.Text.Trim)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueSLICEResultID, strChangeLog, SessionManager.UserID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateSLICEResult", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
            Return True
        End Function

        Private Function DeleteSLICEResult() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                SLICEResultMaster.DeleteSLICEResultMaster(SessionManager.SelectedValueSLICEResultID)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueSLICEResultID, "SLICE Result Deleted", SessionManager.UserID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteSLICEResult", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
            Return True
        End Function
#End Region

#Region " Get Updated Values"
        Private Function GetUpdatedValues() As Dictionary(Of String, String)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim objDic As New Dictionary(Of String, String)
            objDic.Add("SLICEResultText", txtSLICEResultText.Text.Trim())
            objDic.Add("Pass", chkPass.Checked)
            objDic.Add("PresentationSequence", txtPresentationSequence.Text.Trim())
            Return objDic
        End Function
#End Region

    End Class
End Namespace

