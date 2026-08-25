#Region " Imports "
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper

Imports WebApp.APlus.DataAccess.SLICETables
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.UI.CustomControls
Imports WebApp.APlus.DataAccess.Tables
Imports System.Collections.Generic

#End Region

Namespace WebApp.APlus.UI.SLICE
    Partial Class SLICEActivityGroupMaster2
        Inherits ApplicationBase

#Region " Private Constants "
        Private Shared ReadOnly FormName As String = "Checksheet Template Master"
        Private Shared ReadOnly ProgramName As String = "SLICEActivityGroupMaster2"
        Private Shared ReadOnly DBTableName As String = "SLICEActivityGroupMaster"
#End Region

#Region "Load JavaScripts "
        Private Sub LoadCommonJavaScripts()
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnExit.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
        End Sub
        Private Sub LoadAddModeJavaScripts()
            Dim myTabArray() As Object = {txtSLICEActivityGroup, _
                                          txtSLICEActivityGroupDescription, _
                                          ddlWorkcenter, _
                                          txtTargetDeviation}
            Dim TabKeyDownArr() As String = {Tab(txtSLICEActivityGroupDescription, txtTargetDeviation, "No"), _
                                             Tab(ddlWorkcenter, txtSLICEActivityGroup, "No"), _
                                             Tab(txtTargetDeviation, txtSLICEActivityGroupDescription, "No"), _
                                             Tab(txtSLICEActivityGroup, ddlWorkcenter, "Yes")}
            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub

#End Region

#Region " Event Handlers "
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, ProgramName, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Master.HeaderMessage = FormName & " - " & SessionManager.SLICEActivityGroupMasterMode.Replace("Row", "")
            Master.IconImage = Request.ApplicationPath + "/images/clipboard.png"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                Select Case SessionManager.SLICEActivityGroupMasterMode
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "EditRow"
                        LoadAddModeJavaScripts()
                        LoadSelectedRecord()
                        UnEnableRecords()
                        txtSLICEActivityGroup.Focus()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this SLICEActivityGroup Master.');")
                        TransactionHistory1.LockControl = True
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        LoadAddModeJavaScripts()
                        BindWorkcenter()
                        UnEnableRecords()
                        txtSLICEActivityGroupID.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEActivityGroupMaster1"), False)
                End Select
            End If
        End Sub
        Private Sub btnOK_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim blnSuccess As Boolean
            If SessionManager.SLICEActivityGroupMasterMode = "DeleteRow" Then
                blnSuccess = DeleteSLICEActivityGroupMaster()
            ElseIf SessionManager.SLICEActivityGroupMasterMode = "AddRow" Then
                blnSuccess = InsertSLICEActivityGroupMaster()
            ElseIf SessionManager.SLICEActivityGroupMasterMode = "EditRow" Then
                blnSuccess = UpdateSLICEActivityGroupMaster()
            End If

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueSliceActivityGroupID)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEActivityGroupMaster1"), False)
            End If
        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.SLICEActivityGroupMasterMode = "EditRow" Or SessionManager.SLICEActivityGroupMasterMode = "ViewRow" Or SessionManager.SLICEActivityGroupMasterMode = "DeleteRow" Or SessionManager.SLICEActivityGroupMasterMode = "AddRow" Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueSliceActivityGroupID)
            End If
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEActivityGroupMaster1"), False)
        End Sub
        Private Sub btnCancel_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnCancel.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueSliceActivityGroupID)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEActivityGroupMaster1"), False)
        End Sub
#End Region

#Region " Custom Methods "
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
                Dim objItem As ListItem = Nothing
                Dim dt As DataTable = SLICEActivityGroupMaster.SelectSLICEActivityGroupMasterByID(SessionManager.SelectedValueSliceActivityGroupID)
                If dt.Rows.Count > 0 Then
                    txtSLICEActivityGroupID.Text = dt.Rows(0)("SLICEActivityGroupID").ToString().Trim()
                    txtSLICEActivityGroupDescription.Text = dt.Rows(0)("SLICEActivityGroupDescription").ToString().Trim()
                    txtSLICEActivityGroup.Text = dt.Rows(0)("SLICEActivityGroup").ToString().Trim()
                    txtTargetDeviation.Text = dt.Rows(0)("TargetDeviation").ToString().Trim()
                    txtWorkcenter.Text = dt.Rows(0)("Workcenter").ToString().Trim()
                Else
                    txtSLICEActivityGroupID.Text = ""
                    txtSLICEActivityGroup.Text = ""
                    txtSLICEActivityGroupDescription.Text = ""
                    txtTargetDeviation.Text = ""
                    txtWorkcenter.Text = ""
                End If
                BindWorkcenter()
                If dt.Rows.Count > 0 Then
                    objItem = ddlWorkcenter.Items.FindByValue(dt.Rows(0)("WorkcenterID").ToString().Trim())
                End If
                If Not objItem Is Nothing Then
                    objItem.Selected = True
                    txtWorkcenter.Text = objItem.Text
                End If

                TransactionHistory1.TableName = DBTableName
                TransactionHistory1.RecordID = SessionManager.SelectedValueSliceActivityGroupID

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("SLICEActivityGroup", txtSLICEActivityGroup.Text.Trim())
                objDic.Add("SLICEActivityGroupDescription", txtSLICEActivityGroupDescription.Text.Trim())
                objDic.Add("Workcenter", ddlWorkcenter.SelectedItem.Text.Trim())
                objDic.Add("TargetDeviation", txtTargetDeviation.Text.Trim())
                SessionManager.RecordTransactionCurrentValues = objDic
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
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

            If SessionManager.SLICEActivityGroupMasterMode = "ViewRow" Then
                pnlOKCancel.Visible = False
                ddlWorkcenter.Visible = False
                txtWorkcenter.Visible = True
                txtSLICEActivityGroup.ReadOnly = True
                txtSLICEActivityGroup.CssClass = "Textbox_Display"
                txtSLICEActivityGroupDescription.ReadOnly = True
                txtSLICEActivityGroupDescription.CssClass = "Textbox_Display"
                txtTargetDeviation.ReadOnly = True
                txtTargetDeviation.CssClass = "Textbox_Display"
            ElseIf SessionManager.SLICEActivityGroupMasterMode = "AddRow" Then
                txtSLICEActivityGroupID.ReadOnly = True
                txtSLICEActivityGroupID.Text = "New"
                txtWorkcenter.Visible = False
                txtSLICEActivityGroup.Focus()
            ElseIf SessionManager.SLICEActivityGroupMasterMode = "DeleteRow" Then
                ddlWorkcenter.Visible = False
                txtSLICEActivityGroup.ReadOnly = True
                txtSLICEActivityGroup.CssClass = "Textbox_Display"
                txtSLICEActivityGroupDescription.ReadOnly = True
                txtSLICEActivityGroupDescription.CssClass = "Textbox_Display"
                txtTargetDeviation.ReadOnly = True
                txtTargetDeviation.CssClass = "Textbox_Display"
            ElseIf SessionManager.SLICEActivityGroupMasterMode = "EditRow" Then
                txtWorkcenter.Visible = False
                txtSLICEActivityGroup.Focus()
            End If
        End Sub
        Private Sub BindWorkcenter()
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
                WorkcenterMaster.SelectWorkcenterMasterList(ddlWorkcenter, SessionManager.WorkingSiteID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindWorkcenter", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Function InsertSLICEActivityGroupMaster() As Boolean
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

                Dim intResult As Integer = SLICEActivityGroupMaster.AddSLICEActivityGroupMaster(txtSLICEActivityGroup.Text.Trim, txtSLICEActivityGroupDescription.Text.Trim, ddlWorkcenter.SelectedValue.Trim, txtTargetDeviation.Text.Trim)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, intResult, strChangeLog, SessionManager.UserID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertSLICEActivityGroupMaster", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
            Return True
        End Function
        Private Function UpdateSLICEActivityGroupMaster() As Boolean
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

                SLICEActivityGroupMaster.UpdateSLICEActivityGroupMaster(SessionManager.SelectedValueSliceActivityGroupID, txtSLICEActivityGroup.Text.Trim, txtSLICEActivityGroupDescription.Text.Trim, ddlWorkcenter.SelectedValue.Trim, txtTargetDeviation.Text.Trim)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueSliceActivityGroupID, strChangeLog, SessionManager.UserID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateSLICEActivityGroupMaster", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
            Return True
        End Function
        Private Function DeleteSLICEActivityGroupMaster() As Boolean
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
                SLICEActivityGroupMaster.DeleteSLICEActivityGroupMaster(SessionManager.SelectedValueSliceActivityGroupID, ddlWorkcenter.SelectedValue.Trim())
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueSliceActivityGroupID, "SLICE Activity Group Deleted", SessionManager.UserID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteSLICEActivityGroupMaster", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
            Return True
        End Function
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
            objDic.Add("SLICEActivityGroup", txtSLICEActivityGroup.Text.Trim())
            objDic.Add("SLICEActivityGroupDescription", txtSLICEActivityGroupDescription.Text.Trim())
            objDic.Add("Workcenter", ddlWorkcenter.SelectedItem.Text.Trim())
            objDic.Add("TargetDeviation", txtTargetDeviation.Text.Trim())
            Return objDic
        End Function
#End Region

    End Class
End Namespace

