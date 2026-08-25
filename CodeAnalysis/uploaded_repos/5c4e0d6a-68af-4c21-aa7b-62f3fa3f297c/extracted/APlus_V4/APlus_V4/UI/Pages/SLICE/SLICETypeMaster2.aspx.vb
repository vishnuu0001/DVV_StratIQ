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
    Partial Class SLICETypeMaster2
        Inherits ApplicationBase

#Region " Private Constants "
        Private Shared ReadOnly FormName As String = "SLICE Type"
        Private Shared ReadOnly ProgramName As String = "SLICETypeMaster2"
        Private Shared ReadOnly DBTableName As String = "SLICETypeMaster"
#End Region

#Region "Load JavaScripts "
        Private Sub LoadCommonJavaScripts()

            Dim StatusArr() As WebControl = {btnOK, btnCancel, btnExit}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel", "Exit"}
            Dim OutMessageArr() As String = {"", "", ""}
            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)

        End Sub

        Private Sub LoadAddModeJavaScripts()
            Dim myTabArray() As Object = {txtSLICETypeID, _
                                          txtSLICEType}
            Dim TabKeyDownArr() As String = {Tab(txtSLICEType, txtSLICEType, "YES"), _
                                                      Tab(txtSLICETypeID, txtSLICETypeID, "No")}
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

            Master.HeaderMessage = FormName & " - " & SessionManager.SLICETypeMasterMode.Replace("Row", "")
            Master.IconImage = Request.ApplicationPath + "/images/clipboard.png"
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + Me.btnOK.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:IgnoreTab(window.event)")
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                If SessionManager.SLICETypeMasterMode = "ViewRow" Then
                    pnlExit.Visible = True
                    LoadSelectedRecord()
                    UnEnableRecords()
                ElseIf SessionManager.SLICETypeMasterMode = "EditRow" Then
                    LoadSelectedRecord()
                    UnEnableRecords()
                    txtSLICEType.Focus()
                ElseIf SessionManager.SLICETypeMasterMode = "DeleteRow" Then
                    LoadSelectedRecord()
                    UnEnableRecords()
                    btnOK.CausesValidation = False
                    btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this SLICE Type.');")
                    TransactionHistory1.LockControl = True
                ElseIf SessionManager.SLICETypeMasterMode = "AddRow" Then
                    TransactionHistory1.Visible = False
                    LoadAddModeJavaScripts()
                    UnEnableRecords()
                    txtSLICETypeID.Focus()
                Else
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICETypeMaster1"), False)
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
            If SessionManager.SLICETypeMasterMode = "DeleteRow" Then
                blnSuccess = DeleteSLICEType()
            ElseIf SessionManager.SLICETypeMasterMode = "AddRow" Then
                blnSuccess = InsertSLICEType()
            ElseIf SessionManager.SLICETypeMasterMode = "EditRow" Then
                blnSuccess = UpdateSLICEType()
            End If

            If blnSuccess Then
                Master.WriteErrors(FormName, SessionManager.SLICETypeMasterMode & " SLICEType " & txtSLICEType.Text, SessionManager.UserID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueSLICEType)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueSLICETypeID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SLICETypeMasterMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICETypeMaster1"), False)
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

            If SessionManager.SLICETypeMasterMode = "EditRow" Or SessionManager.SLICETypeMasterMode = "ViewRow" Or SessionManager.SLICETypeMasterMode = "DeleteRow" Or SessionManager.SLICETypeMasterMode = "AddRow" Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueSLICEType)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueSLICETypeID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SLICETypeMasterMode)
            End If
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICETypeMaster1"), False)
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueSLICEType)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueSLICETypeID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SLICETypeMasterMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICETypeMaster1"), False)
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

            txtSLICETypeID.Text = SessionManager.SelectedValueSLICETypeID
            txtSLICEType.Text = SessionManager.SelectedValueSLICEType

            TransactionHistory1.TableName = DBTableName
            TransactionHistory1.RecordID = SessionManager.SelectedValueSLICETypeID

            Dim objDic As New Dictionary(Of String, String)
            objDic.Add("SLICEType", txtSLICEType.Text.Trim())
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

            If SessionManager.SLICETypeMasterMode = "ViewRow" Then
                pnlOKCancel.Visible = False
                txtSLICEType.ReadOnly = True
                txtSLICEType.CssClass = "Textbox_Display"
            ElseIf SessionManager.SLICETypeMasterMode = "AddRow" Then
                txtSLICETypeID.ReadOnly = True
                txtSLICETypeID.Text = "New"
                txtSLICEType.Focus()
            ElseIf SessionManager.SLICETypeMasterMode = "DeleteRow" Then
                txtSLICEType.ReadOnly = True
                txtSLICEType.CssClass = "Textbox_Display"
            End If
        End Sub

        Private Function InsertSLICEType() As Boolean
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
                Dim intResult As Integer = SLICETypeMaster.AddSLICETypeMaster(txtSLICEType.Text.Trim)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, intResult, strChangeLog, SessionManager.UserID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertSLICEType", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
            Return True
        End Function

        Private Function UpdateSLICEType() As Boolean
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

                SLICETypeMaster.UpdateSLICETypeMaster(SessionManager.SelectedValueSLICETypeID, txtSLICEType.Text.Trim)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueSLICETypeID, strChangeLog, SessionManager.UserID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateSLICEType", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
            Return True
        End Function

        Private Function DeleteSLICEType() As Boolean
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
                SLICETypeMaster.DeleteSLICETypeMaster(SessionManager.SelectedValueSLICETypeID)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueSLICETypeID, "SLICE Type Deleted", SessionManager.UserID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteSLICEType", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
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
            objDic.Add("SLICEType", txtSLICEType.Text.Trim())
            Return objDic
        End Function
#End Region

    End Class
End Namespace

