#Region " Imports "

Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.DataAccess.SLICETables
Imports WebApp.APlus.UI.CustomControls
Imports System.Collections.Generic

#End Region

Namespace WebApp.APlus.UI.SLICE
    Partial Class WorkcenterMaster2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Workcenter Master"
        Private Shared ReadOnly ProgramName As String = "WorkcenterMaster2"
        Private Shared ReadOnly DBTableName As String = "WorkcenterMaster"
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel, btnExit}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel", "Exit"}
            Dim OutMessageArr() As String = {"", "", ""}
            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)
        End Sub

        Private Sub LoadAddModeJavaScripts()
            Dim myTabArray() As Object = {ddlSite, _
                                          txtWorkcenter, _
                                          txtWorkcenterDescription}
            Dim TabKeyDownArr() As String = {Tab(txtWorkcenter, txtWorkcenterDescription, "No"), _
                                            Tab(txtWorkcenterDescription, ddlSite, "No"), _
                                             Tab(ddlSite, txtWorkcenter, "No")}
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

            Master.HeaderMessage = FormName & " - " & SessionManager.WorkcenterMasterMode.Replace("Row", "")
            Master.IconImage = Request.ApplicationPath + "/images/WorkCenter.gif"
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnOK.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event")
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                Select Case SessionManager.WorkcenterMasterMode
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "EditRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        ddlSite.Focus()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Workcenter Master.');")
                        TransactionHistory1.LockControl = True
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        LoadAddModeJavaScripts()
                        BindSite()
                        UnEnableRecords()
                        txtWorkcenter.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("WorkcenterMaster1"), False)
                End Select
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

            If SessionManager.WorkcenterMasterMode = "DeleteRow" Then
                blnSuccess = DeleteWorkcenterMaster()
            ElseIf SessionManager.WorkcenterMasterMode = "AddRow" Then
                blnSuccess = InsertWorkcenterMaster()
            ElseIf SessionManager.WorkcenterMasterMode = "EditRow" Then
                blnSuccess = UpdateWorkcenterMaster()
            End If

            If blnSuccess Then
                Master.WriteErrors(FormName, SessionManager.WorkcenterMasterMode & " WorkcenterMaster " & txtWorkcenterID.Text, SessionManager.UserID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueWorkcenterID)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("WorkcenterMaster1"), False)
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

            Select Case SessionManager.WorkcenterMasterMode
                Case "EditRow", "ViewRow", "AddRow", "DeleteRow"
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueWorkcenterID)
            End Select
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("WorkcenterMaster1"), False)
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

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("WorkcenterMaster1"), False)
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadSelectedRecord()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim dt As DataTable = WorkcenterMaster.SelectWorkcenterMasterByIDAsDataTable(SessionManager.SelectedValueWorkcenterID)
                Dim objItem As ListItem = Nothing

                If dt.Rows.Count > 0 Then
                    txtSite.Text = dt.Rows(0)("Site").ToString().Trim()
                    txtWorkcenter.Text = dt.Rows(0)("Workcenter").ToString().Trim()
                    txtWorkcenterDescription.Text = dt.Rows(0)("WorkcenterDescription").ToString().Trim()
                    txtWorkcenterID.Text = dt.Rows(0)("WorkcenterID").ToString().Trim()
                Else
                    txtWorkcenter.Text = ""
                    txtWorkcenterID.Text = ""
                    txtWorkcenterDescription.Text = ""
                    txtSite.Text = ""
                End If
                BindSite()

                If dt.Rows.Count > 0 Then
                    objItem = ddlSite.Items.FindByValue(dt.Rows(0)("SiteID").ToString().Trim())
                End If

                If Not objItem Is Nothing Then
                    objItem.Selected = True
                    txtSite.Text = objItem.Text
                End If

                TransactionHistory1.TableName = DBTableName
                TransactionHistory1.RecordID = SessionManager.SelectedValueWorkcenterID

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("Site", ddlSite.SelectedItem.Text.Trim())
                objDic.Add("Workcenter", txtWorkcenter.Text.Trim())
                objDic.Add("WorkcenterDescription", txtWorkcenterDescription.Text.Trim())
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

            If SessionManager.WorkcenterMasterMode = "ViewRow" Then
                pnlOKCancel.Visible = False
                ddlSite.Visible = False
                txtSite.ReadOnly = True
                txtWorkcenter.CssClass = "Textbox_Display"
                txtWorkcenterDescription.ReadOnly = True
                txtWorkcenterDescription.CssClass = "Textbox_Display"
            ElseIf SessionManager.WorkcenterMasterMode = "AddRow" Then
                txtWorkcenterID.ReadOnly = True
                txtWorkcenterID.Text = "New"
                txtWorkcenter.Visible = True
                txtSite.Visible = False
                ddlSite.Focus()
            ElseIf SessionManager.WorkcenterMasterMode = "DeleteRow" Then
                ddlSite.Visible = False
                txtWorkcenter.ReadOnly = True
                txtWorkcenter.CssClass = "Textbox_Display"
                txtWorkcenterDescription.ReadOnly = True
                txtWorkcenterDescription.CssClass = "Textbox_Display"
            ElseIf SessionManager.WorkcenterMasterMode = "EditRow" Then
                txtWorkcenter.Visible = True
                txtSite.Visible = False
            End If
        End Sub
        Private Sub BindSite()
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
                SiteMaster.SelectSiteMasterActiveList(ddlSite)

                If SessionManager.WorkcenterMasterMode = "AddRow" Then
                    If SessionManager.WorkingSite.Trim.Length > 0 Then
                        Dim objItem As ListItem = ddlSite.Items.FindByValue(SessionManager.WorkingSiteID)
                        If objItem IsNot Nothing Then
                            objItem.Selected = True
                        End If
                    End If
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindSite", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Function InsertWorkcenterMaster() As Boolean
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

                Dim intResult As Integer = WorkcenterMaster.AddWorkcenterMaster(CInt(ddlSite.SelectedValue), txtWorkcenter.Text.Trim, txtWorkcenterDescription.Text.Trim)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, intResult, strChangeLog, SessionManager.UserID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertWorkcenterMaster", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
            Return True
        End Function
        Private Function UpdateWorkcenterMaster() As Boolean
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

                WorkcenterMaster.UpdateWorkcenterMaster(CInt(txtWorkcenterID.Text.Trim()), CInt(ddlSite.SelectedValue.Trim()), txtWorkcenter.Text.Trim, txtWorkcenterDescription.Text.Trim)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueWorkcenterID, strChangeLog, SessionManager.UserID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateWorkcenterMaster", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
            Return True
        End Function
        Private Function DeleteWorkcenterMaster() As Boolean
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
                WorkcenterMaster.DeleteWorkcenterMaster(CInt(txtWorkcenterID.Text.Trim))
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueWorkcenterID, "Work Center Deleted", SessionManager.UserID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteWorkcenterMaster", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
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
            objDic.Add("Site", ddlSite.SelectedItem.Text.Trim())
            objDic.Add("Workcenter", txtWorkcenter.Text.Trim())
            objDic.Add("WorkcenterDescription", txtWorkcenterDescription.Text.Trim())
            Return objDic
        End Function
#End Region

    End Class
End Namespace

