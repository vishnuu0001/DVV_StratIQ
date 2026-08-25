#Region " Imports"

Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper
Imports WebApp.APlus.UI.CustomControls
Imports WebApp.APlus.DataAccess.SLICETables
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports System.Collections.Generic

#End Region

Namespace WebApp.APlus.UI.SLICE
    Partial Class SLICEFrequencyMaster2
        Inherits ApplicationBase

#Region " Private Variables"
        Private intResult As Integer
#End Region

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "SLICE Frequency"
        Private Shared ReadOnly ProgramName As String = "SLICEFrequencyMaster2"
        Private Shared ReadOnly DBTableName As String = "SLICEFrequencyMaster"
#End Region

#Region "Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel, btnExit}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel", "Exit"}
            Dim OutMessageArr() As String = {"", "", ""}
            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)
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

            Master.HeaderMessage = FormName & " - " & SessionManager.SLICEFrequencyMasterMode.Replace("Row", "")
            Master.IconImage = Request.ApplicationPath + "/images/clipboard.png"
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + Me.btnOK.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:IgnoreTab(window.event)")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event")
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                If SessionManager.SLICEFrequencyMasterMode = "ViewRow" Then
                    pnlExit.Visible = True
                    LoadSelectedRecord()
                    UnEnableRecords()
                ElseIf SessionManager.SLICEFrequencyMasterMode = "EditRow" Then
                    LoadSelectedRecord()
                    UnEnableRecords()
                    txtSLICEFrequency.Focus()
                ElseIf SessionManager.SLICEFrequencyMasterMode = "DeleteRow" Then
                    LoadSelectedRecord()
                    UnEnableRecords()
                    btnOK.CausesValidation = False
                    btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this SLICE Frequency.');")
                    TransactionHistory1.LockControl = True
                ElseIf SessionManager.SLICEFrequencyMasterMode = "AddRow" Then
                    TransactionHistory1.Visible = False
                    UnEnableRecords()
                    txtSLICEFrequencyID.Focus()
                Else
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEFrequencyMaster1"), False)
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

            If SessionManager.SLICEFrequencyMasterMode = "DeleteRow" Then
                blnSuccess = DeleteSLICEFrequency()
            ElseIf SessionManager.SLICEFrequencyMasterMode = "AddRow" Then
                blnSuccess = InsertSLICEFrequency()
            ElseIf SessionManager.SLICEFrequencyMasterMode = "EditRow" Then
                blnSuccess = UpdateSLICEFrequency()
            End If

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueSLICEFrequency)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueSLICEFrequencyID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SLICEFrequencyMasterMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEFrequencyMaster1"), False)
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

            If SessionManager.SLICEFrequencyMasterMode = "EditRow" Or SessionManager.SLICEFrequencyMasterMode = "ViewRow" _
                                                Or SessionManager.SLICEFrequencyMasterMode = "DeleteRow" _
                                                Or SessionManager.SLICEFrequencyMasterMode = "AddRow" Then

                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueSLICEFrequency)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueSLICEFrequencyID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SLICEFrequencyMasterMode)
            End If
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEFrequencyMaster1"), False)
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueSLICEFrequency)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueSLICEFrequencyID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SLICEFrequencyMasterMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEFrequencyMaster1"), False)
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

            txtSLICEFrequencyID.Text = SessionManager.SelectedValueSLICEFrequencyID
            txtSLICEFrequency.Text = SessionManager.SelectedValueSLICEFrequency

            TransactionHistory1.TableName = DBTableName
            TransactionHistory1.RecordID = SessionManager.SelectedValueSLICEFrequencyID

            Dim objDic As New Dictionary(Of String, String)
            objDic.Add("SLICEFrequency", txtSLICEFrequency.Text.Trim())
            SessionManager.RecordTransactionCurrentValues = objDic
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

            If SessionManager.SLICEFrequencyMasterMode = "ViewRow" Then
                pnlOKCancel.Visible = False
                txtSLICEFrequency.ReadOnly = True
                txtSLICEFrequency.CssClass = "Textbox_Display"
            ElseIf SessionManager.SLICEFrequencyMasterMode = "AddRow" Then
                txtSLICEFrequencyID.ReadOnly = True
                txtSLICEFrequencyID.Text = "New"
                txtSLICEFrequency.Focus()
            ElseIf SessionManager.SLICEFrequencyMasterMode = "DeleteRow" Then
                txtSLICEFrequency.ReadOnly = True
                txtSLICEFrequency.CssClass = "Textbox_Display"
            End If
        End Sub

        Private Function InsertSLICEFrequency() As Boolean
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

                Dim intResult As Integer = SLICEFrequencyMaster.AddSLICEFrequencyMaster(txtSLICEFrequency.Text.Trim)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, intResult, strChangeLog, SessionManager.UserID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertSLICEFrequency", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
            Return True
        End Function

        Private Function UpdateSLICEFrequency() As Boolean
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

                SLICEFrequencyMaster.UpdateSLICEFrequencyMaster(SessionManager.SelectedValueSLICEFrequencyID, txtSLICEFrequency.Text.Trim)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueSLICEFrequencyID, strChangeLog, SessionManager.UserID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateSLICEFrequency", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
            Return True
        End Function

        Private Function DeleteSLICEFrequency() As Boolean
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
                SLICEFrequencyMaster.DeleteSLICEFrequencyMaster(SessionManager.SelectedValueSLICEFrequencyID)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueSLICEFrequencyID, "SLICE Frequency Deleted", SessionManager.UserID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteSLICEFrequency", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
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
            objDic.Add("SLICEFrequency", txtSLICEFrequency.Text.Trim())
            Return objDic
        End Function
#End Region

    End Class
End Namespace

