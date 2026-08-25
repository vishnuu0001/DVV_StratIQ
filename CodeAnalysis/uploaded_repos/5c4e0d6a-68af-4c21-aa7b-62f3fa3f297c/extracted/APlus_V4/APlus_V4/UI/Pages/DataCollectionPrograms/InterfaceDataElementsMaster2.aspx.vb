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
    Partial Class InterfaceDataElementsMaster2
        Inherits ApplicationBase

#Region " Private Variables"
        Private Shared ReadOnly FormName As String = "Data Element Maintenance"
        Private Shared ReadOnly ProgramName As String = "InterfaceDataElementsMaster2"
        Private Shared ReadOnly DBTableName As String = "InterfaceDataElementsMaster"
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
            Dim myTabArray() As Object = {txtDataElement, _
                                          txtSource, _
                                          txtAppSource, _
                                          txtAppKPIKey, _
                                          txtAppMill, _
                                          txtAppIdentKey, _
                                          txtAppIdent, _
                                          txtUOM, _
                                          ckActive, _
                                          ckDailyValue}

            Dim TabKeyDownArr() As String = {Tab(txtSource, ckDailyValue, "No"), _
                                             Tab(txtAppSource, txtDataElement, "No"), _
                                             Tab(txtAppKPIKey, txtSource, "No"), _
                                             Tab(txtAppMill, txtAppSource, "No"), _
                                             Tab(txtAppIdentKey, txtAppKPIKey, "No"), _
                                             Tab(txtAppIdent, txtAppMill, "No"), _
                                             Tab(txtUOM, txtAppIdentKey, "No"), _
                                             Tab(ckActive, txtAppIdent, "No"), _
                                             Tab(ckDailyValue, txtUOM, "No"), _
                                             Tab(txtDataElement, ckActive, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {txtSource, _
                                          txtAppSource, _
                                          txtAppKPIKey, _
                                          txtAppMill, _
                                          txtAppIdentKey, _
                                          txtAppIdent, _
                                          txtUOM, _
                                          ckActive, _
                                          ckDailyValue}

            Dim TabKeyDownArr() As String = {Tab(txtAppSource, ckDailyValue, "No"), _
                                             Tab(txtAppKPIKey, txtSource, "No"), _
                                             Tab(txtAppMill, txtAppSource, "No"), _
                                             Tab(txtAppIdentKey, txtAppKPIKey, "No"), _
                                             Tab(txtAppIdent, txtAppMill, "No"), _
                                             Tab(txtUOM, txtAppIdentKey, "No"), _
                                             Tab(ckActive, txtAppIdent, "No"), _
                                             Tab(ckDailyValue, txtUOM, "No"), _
                                             Tab(txtSource, ckActive, "No")}

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

            Master.HeaderMessage = FormName & " - " & SessionManager.DataElementMode.Replace("Row", "")
            Master.IconImage = Request.ApplicationPath + "/images/boss.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                Select Case SessionManager.DataElementMode
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
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Data Element.');")
                        TransactionHistory1.LockControl = True
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        txtSite.Text = SessionManager.WorkingSite
                        LoadAddModeJavaScripts()
                        txtDataElement.Focus()
                    Case "EditRow"
                        LoadEditModeJavaScripts()
                        LoadSelectedRecord()
                        UnEnableRecords()
                        txtUOM.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("InterfaceDataElementsMaster1"), False)
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
            Select Case SessionManager.DataElementMode
                Case "AddRow"
                    blnSuccess = InsertDataElement()
                Case "EditRow"
                    blnSuccess = UpdateDataElement()
                Case "DeleteRow"
                    blnSuccess = DeleteDataElement()
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueDataElement)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.DataElementMode)

                Dim strProgram As String = "InterfaceDataElementsMaster1"
                If SessionManager.CallingProgram.Trim.Length > 0 Then
                    strProgram = SessionManager.CallingProgram
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CallingProgram)
                End If
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strProgram), False)
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueDataElement)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.DataElementMode)

            Dim strProgram As String = "InterfaceDataElementsMaster1"
            If SessionManager.CallingProgram.Trim.Length > 0 Then
                strProgram = SessionManager.CallingProgram
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CallingProgram)
            End If
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strProgram), False)
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

            Dim objDT As DataTable = InterfaceDataElements.SelectInterfaceDataElement(SessionManager.SelectedValueDataElement)
            If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                Dim dtRow As DataRow = objDT.Rows(0)

                txtDataElement.Text = dtRow("DataElement").ToString
                txtSite.Text = dtRow("Site").ToString
                txtSource.Text = dtRow("Source").ToString
                txtAppSource.Text = dtRow("APP_SOURCE").ToString
                txtAppKPIKey.Text = dtRow("APP_KPIKEY").ToString
                txtAppMill.Text = dtRow("APP_MILL").ToString
                txtAppIdentKey.Text = dtRow("APP_IDENTKEY").ToString
                txtAppIdent.Text = dtRow("APP_IDENT").ToString
                txtUOM.Text = dtRow("UOM").ToString
                ckActive.Checked = Convert.ToBoolean(dtRow("Active"))
                ckDailyValue.Checked = Convert.ToBoolean(dtRow("DailyValue"))

                TransactionHistory1.TableName = DBTableName
                TransactionHistory1.RecordID = SessionManager.SelectedValueDataElement.Trim()

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("Site", txtSite.Text.Trim())
                objDic.Add("Source", txtSource.Text.Trim())
                objDic.Add("AppSource", txtAppSource.Text.Trim)
                objDic.Add("AppKPIKey", txtAppKPIKey.Text.Trim)
                objDic.Add("AppMill", txtAppMill.Text.Trim)
                objDic.Add("AppIdentKey", txtAppIdentKey.Text.Trim)
                objDic.Add("AppIdent", txtAppIdent.Text.Trim)
                objDic.Add("UOM", txtUOM.Text.Trim)
                objDic.Add("Active", ckActive.Checked.ToString)
                objDic.Add("DailyValue", ckDailyValue.Checked.ToString)
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

            Select Case SessionManager.DataElementMode
                Case "ViewRow", "DeleteRow"
                    pnlOKCancel.Visible = False
                    txtDataElement.ReadOnly = True
                    txtDataElement.CssClass = "Textbox_Display"
                    txtSource.ReadOnly = True
                    txtSource.CssClass = "Textbox_Display"
                    txtAppSource.ReadOnly = True
                    txtAppSource.CssClass = "Textbox_Display"
                    txtAppKPIKey.ReadOnly = True
                    txtAppKPIKey.CssClass = "Textbox_Display"
                    txtAppMill.ReadOnly = True
                    txtAppMill.CssClass = "Textbox_Display"
                    txtAppIdentKey.ReadOnly = True
                    txtAppIdentKey.CssClass = "Textbox_Display"
                    txtAppIdent.ReadOnly = True
                    txtAppIdent.CssClass = "Textbox_Display"
                    txtUOM.ReadOnly = True
                    txtUOM.CssClass = "Textbox_Display"
                    ckActive.Enabled = False
                    ckDailyValue.Enabled = False
                Case "EditRow"
                    txtDataElement.ReadOnly = True
                    txtDataElement.CssClass = "Textbox_Display"
            End Select
        End Sub
        Private Function InsertDataElement() As Boolean
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

                InterfaceDataElements.InsertDataElement(txtDataElement.Text.Trim, SessionManager.WorkingSiteID, txtSource.Text.Trim, txtAppSource.Text.Trim, txtAppKPIKey.Text.Trim, txtAppMill.Text.Trim, txtAppIdentKey.Text.Trim, txtAppIdent.Text.Trim, txtUOM.Text.Trim, ckActive.Checked, ckDailyValue.Checked)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, txtDataElement.Text.Trim, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertDataElement", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateDataElement() As Boolean
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

                InterfaceDataElements.UpdateDataElement(SessionManager.SelectedValueDataElement, SessionManager.WorkingSiteID, txtSource.Text.Trim, txtAppSource.Text.Trim, txtAppKPIKey.Text.Trim, txtAppMill.Text.Trim, txtAppIdentKey.Text.Trim, txtAppIdent.Text.Trim, txtUOM.Text.Trim, ckActive.Checked, ckDailyValue.Checked)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueDataElement, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateDataElement", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function DeleteDataElement() As Boolean
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
                InterfaceDataElements.DeleteDataElement(SessionManager.SelectedValueDataElement)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueDataElement, "Data Element Deleted", SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteDataElement", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
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
            objDic.Add("Site", txtSite.Text.Trim())
            objDic.Add("Source", txtSource.Text.Trim())
            objDic.Add("AppSource", txtAppSource.Text.Trim)
            objDic.Add("AppKPIKey", txtAppKPIKey.Text.Trim)
            objDic.Add("AppMill", txtAppMill.Text.Trim)
            objDic.Add("AppIdentKey", txtAppIdentKey.Text.Trim)
            objDic.Add("AppIdent", txtAppIdent.Text.Trim)
            objDic.Add("UOM", txtUOM.Text.Trim)
            objDic.Add("Active", ckActive.Checked.ToString)
            objDic.Add("DailyValue", ckDailyValue.Checked.ToString)

            Return objDic
        End Function
#End Region

    End Class
End Namespace
