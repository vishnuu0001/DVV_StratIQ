#Region " Imports "

Imports System.IO
Imports System.Data
Imports System.Text
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.SLICETables
Imports WebApp.APlus.UI.CustomControls
Imports WebApp.APlus.DataAccess.Tables
Imports System.Collections.Generic

#End Region

Namespace WebApp.APlus.UI.SLICE
    Partial Class SLICECheckSheetMaster2
        Inherits ApplicationBase

#Region " Private Constants "
        Private Shared ReadOnly FormName As String = "SLICE Checksheet"
        Private Shared ReadOnly ProgramName As String = "SLICEChecksheetMaster2"
        Private Shared ReadOnly DBTableName As String = "SLICEChecksheetMaster"
        Private Shared ReadOnly DATE_FORMAT As String = "yyyy/MM/dd"
        Private bClosed As Boolean = False
#End Region

#Region " Load JavaScripts "
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel, btnExit}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel", "Exit"}
            Dim OutMessageArr() As String = {"", "", ""}
            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)
            txtNumPrinted.Attributes.Add("onkeydown", "javascript:AllowIntegers(window.event);")
            txtReleaseDate_CalendarExtender.Format = DATE_FORMAT
            txtDueDate_CalendarExtender.Format = DATE_FORMAT

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnExit.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
        End Sub
        Private Sub LoadAddModeJavaScripts()
            Dim myTabArray() As Object = {ddlCheckSheetTemplates, _
                                          txtReleaseDate, _
                                          txtDueDate}

            Dim TabKeyDownArr() As String = {Tab(txtReleaseDate, txtDueDate, "No"), _
                                             Tab(txtDueDate, ddlCheckSheetTemplates, "No"), _
                                             Tab(ddlCheckSheetTemplates, txtReleaseDate, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
        Private Sub LoadEditModeJavaScripts()
            If bClosed Then
                Dim myTabArray() As Object = {ddlCheckSheetStatus}

                Dim TabKeyDownArr() As String = {Tab(ddlCheckSheetStatus, ddlCheckSheetStatus, "No")}

                AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
            Else
                Dim myTabArray() As Object = {txtReleaseDate, _
                                              txtDueDate, _
                                              ddlCheckSheetStatus}

                Dim TabKeyDownArr() As String = {Tab(txtDueDate, ddlCheckSheetStatus, "No"), _
                                                 Tab(ddlCheckSheetStatus, txtReleaseDate, "No"), _
                                                 Tab(txtReleaseDate, txtDueDate, "No")}

                AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
            End If
        End Sub
#End Region

#Region " Event Handlers "
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Master.IconImage = Request.ApplicationPath & "/images/clipboard.png"
            Master.HeaderMessage = FormName & " - " & SessionManager.SLICEChecksheetMasterMode.ToString
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                LoadChecksheetDropDownList()
                LoadStatusDropDownList()

                Select Case SessionManager.SLICEChecksheetMasterMode.ToString()
                    Case "ViewRow"
                        LoadSelectedRecord()
                        DisableControls()
                    Case "EditRow"
                        LoadSelectedRecord()
                        DisableControls()
                        LoadEditModeJavaScripts()

                        If bClosed Then
                            ddlCheckSheetStatus.Focus()
                        Else
                            txtReleaseDate.Focus()
                        End If
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        DisplayAddControls()
                        DisableControls()
                        LoadAddModeJavaScripts()
                        ddlCheckSheetTemplates.Focus()
                    Case "DeleteRow"
                        TransactionHistory1.LockControl = True
                        reqTemplateSelection.Enabled = False
                        LoadSelectedRecord()
                        DisableControls()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEChecksheetMaster1"), False)
                End Select
            End If
        End Sub
        Private Sub btnExit_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnExit.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.MasterControlExitProgram = "SLICEChecksheetMaster2"
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEChecksheetMaster1"), False)
        End Sub
        Private Sub btnOK_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim bResult As Boolean = False
            Select Case SessionManager.SLICEChecksheetMasterMode.ToString()
                Case "EditRow"
                    bResult = UpdateSLICEChecksheetMaster()
                Case "AddRow"
                    bResult = InsertSLICEChecksheetMasterData()
                Case "DeleteRow"
                    bResult = DeleteSLICEChecksheetMaster()
            End Select

            If bResult Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueCheckSheetID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SLICEChecksheetMasterMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEChecksheetMaster1"), False)
            End If
        End Sub
        Private Sub btnCancel_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnCancel.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueCheckSheetID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SLICEChecksheetMasterMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEChecksheetMaster1"), False)
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
                Dim dt As DataTable = SLICEChecksheetMaster.SelectChecksheetDataAsDataTable(SessionManager.SelectedValueCheckSheetID.ToString())
                If dt.Rows.Count > 0 Then
                    Dim dtRow As DataRow = dt.Rows(0)
                    Dim objItem As ListItem = Nothing

                    txtSLICEChecksheetID.Text = dtRow("SLICEChecksheetID").ToString().Trim()
                    objItem = ddlCheckSheetTemplates.Items.FindByValue(dtRow("SLICEActivityGroupID").ToString)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                        txtSLICEActivityGroup.Text = objItem.Text
                    End If
                    If IsDate(dtRow("SLICEChecksheetReleaseDate").ToString) Then
                        txtReleaseDate.Text = Convert.ToDateTime(dtRow("SLICEChecksheetReleaseDate").ToString).ToString("yyyy/MM/dd")
                    End If
                    If IsDate(dtRow("SLICEChecksheetDueDate").ToString) Then
                        txtDueDate.Text = Convert.ToDateTime(dtRow("SLICEChecksheetDueDate").ToString).ToString("yyyy/MM/dd")
                    End If
                    objItem = ddlCheckSheetStatus.Items.FindByValue(dtRow("SLICEChecksheetStatusID").ToString)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                        txtSheetStatus.Text = objItem.Text
                        If objItem.Text.ToUpper = "CLOSED" Then
                            bClosed = True
                        End If
                    End If
                    txtCreatedUserId.Text = dtRow("CreateUserID").ToString()
                    If IsDate(dtRow("CreatedDateTime").ToString) Then
                        txtCreateDate.Text = Convert.ToDateTime(dtRow("CreatedDateTime").ToString).ToString("yyyy/MM/dd")
                    End If
                    txtNumPrinted.Text = dtRow("NumberPrinted").ToString()
                    If IsDate(dtRow("LastPrintedDateTime").ToString) Then
                        txtLastPrintDate.Text = Convert.ToDateTime(dtRow("LastPrintedDateTime").ToString).ToString("yyyy/MM/dd")
                    End If
                    txtLastUserToPrint.Text = dtRow("LastPrintedUserID").ToString

                    TransactionHistory1.TableName = DBTableName
                    TransactionHistory1.RecordID = SessionManager.SelectedValueCheckSheetID

                    Dim objDic As New Dictionary(Of String, String)
                    objDic.Add("SLICEActivityGroup", txtSLICEActivityGroup.Text.Trim())
                    objDic.Add("SLICEChecksheetReleaseDate", txtReleaseDate.Text.Trim())
                    objDic.Add("SLICEChecksheetDueDate", txtDueDate.Text.Trim())
                    objDic.Add("SLICEChecksheetStatus", txtSheetStatus.Text)
                    objDic.Add("CreateUserID", txtCreatedUserId.Text.Trim())
                    objDic.Add("CreatedDateTime", txtCreateDate.Text.Trim())
                    objDic.Add("NumberPrinted", txtNumPrinted.Text.Trim())
                    objDic.Add("LastPrintedDateTime", txtLastPrintDate.Text.Trim())
                    objDic.Add("LastPrintedUserID", txtLastUserToPrint.Text.Trim())
                    SessionManager.RecordTransactionCurrentValues = objDic
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord() ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub DisplayAddControls()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            txtSLICEChecksheetID.Text = "New"
            Dim objitem As ListItem = ddlCheckSheetTemplates.Items.FindByValue(SessionManager.SLICEActivityGroupMasterID.ToString())
            If objitem IsNot Nothing Then
                objitem.Selected = True
                txtSLICEActivityGroup.Text = objitem.Text
            End If
            txtReleaseDate.Text = Now.ToString("yyyy/MM/dd")
            txtDueDate.Text = Now.ToString("yyyy/MM/dd")
            txtCreatedUserId.Text = SessionManager.UserID.ToString().Trim.ToUpper()
            txtCreateDate.Text = Now.ToString("yyyy/MM/dd")
            txtNumPrinted.Text = "0"
            txtLastPrintDate.Text = Now.ToString("yyyy/MM/dd")
            txtLastUserToPrint.Text = SessionManager.UserID.ToString().Trim.ToUpper()
            objitem = ddlCheckSheetStatus.Items.FindByText("Planned")
            If objitem IsNot Nothing Then
                objitem.Selected = True
                txtSheetStatus.Text = objitem.Text
            End If
        End Sub
        Private Sub DisableControls()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Select Case SessionManager.SLICEChecksheetMasterMode.ToString()
                Case "ViewRow"
                    pnlOKCancel.Visible = False
                    btnExit.Visible = True

                    txtSLICEActivityGroup.Visible = True
                    ddlCheckSheetTemplates.Visible = False
                    txtReleaseDate.ReadOnly = True
                    txtReleaseDate.CssClass = "Textbox_Display"
                    imgReleaseDate.Visible = False
                    txtReleaseDate_CalendarExtender.Enabled = False
                    txtDueDate.ReadOnly = True
                    txtDueDate.CssClass = "Textbox_Display"
                    imgDueDate.Visible = False
                    txtDueDate_CalendarExtender.Enabled = False
                    ddlCheckSheetStatus.Visible = False
                    txtSheetStatus.Visible = True
                Case "AddRow"
                    txtSLICEActivityGroup.Visible = False
                    ddlCheckSheetTemplates.Visible = True
                    ddlCheckSheetStatus.Visible = False
                    txtSheetStatus.Visible = True

                    pnlExit.Visible = False
                    pnlOKCancel.Visible = True
                Case "EditRow"
                    pnlExit.Visible = False
                    pnlOKCancel.Visible = True

                    If bClosed Then
                        txtReleaseDate.ReadOnly = True
                        txtReleaseDate.CssClass = "Textbox_Display"
                        imgReleaseDate.Visible = False
                        txtReleaseDate_CalendarExtender.Enabled = False
                        txtDueDate.ReadOnly = True
                        txtDueDate.CssClass = "Textbox_Display"
                        imgDueDate.Visible = False
                        txtDueDate_CalendarExtender.Enabled = False
                    End If
                Case "DeleteRow"
                    pnlOKCancel.Visible = True
                    btnExit.Visible = False

                    txtSLICEActivityGroup.Visible = True
                    ddlCheckSheetTemplates.Visible = False
                    txtReleaseDate.ReadOnly = True
                    txtReleaseDate.CssClass = "Textbox_Display"
                    imgReleaseDate.Visible = False
                    txtReleaseDate_CalendarExtender.Enabled = False
                    txtDueDate.ReadOnly = True
                    txtDueDate.CssClass = "Textbox_Display"
                    imgDueDate.Visible = False
                    txtDueDate_CalendarExtender.Enabled = False
                    ddlCheckSheetStatus.Visible = False
                    txtSheetStatus.Visible = True
            End Select
        End Sub
        Private Sub LoadStatusDropDownList()
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
                Dim dt As DataTable = SLICEChecksheetMaster.SelectChecksheetStatusAsDataTable()
                If dt.Rows.Count > 0 Then
                    ddlCheckSheetStatus.Items.Insert(0, " ")
                    For i As Integer = 0 To dt.Rows.Count - 1
                        Dim objList As New ListItem
                        objList.Text = dt.Rows(i)("SLICECheckSheetDesc").ToString().Trim()
                        objList.Value = dt.Rows(i)("SLICECheckSheetStatusID").ToString().Trim()
                        ddlCheckSheetStatus.Items.Add(objList)
                    Next
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadStatusDropDownList() ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub LoadChecksheetDropDownList()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim iCnt As Integer = 0
            Try
                Dim dt As DataTable = SLICEChecksheetMaster.SelectChecksheetDataByWorkcenterID(SessionManager.SelectedWorkCenterID)
                If dt.Rows.Count > 0 Then
                    Dim objList As ListItem
                    objList = New ListItem
                    objList.Text = ""
                    objList.Value = ""

                    ddlCheckSheetTemplates.Items.Add(objList)
                    While iCnt < dt.Rows.Count
                        objList = New ListItem
                        objList.Text = dt.Rows(iCnt)("TemplateDesc").ToString()
                        objList.Value = dt.Rows(iCnt)("SLICEActivityGroupID").ToString()
                        ddlCheckSheetTemplates.Items.Add(objList)
                        iCnt += 1
                    End While
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadChecksheetDropDownList()", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Function InsertSLICEChecksheetMasterData() As Boolean
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

                Dim intResult As Integer = SLICEChecksheetMaster.AddSLICEChecksheetMaster(ddlCheckSheetTemplates.SelectedValue.ToString().Trim(), _
                                                                txtReleaseDate.Text.Trim(), _
                                                                txtDueDate.Text.Trim(), _
                                                                0, _
                                                                txtCreatedUserId.Text.Trim(), _
                                                                txtCreateDate.Text.Trim(), _
                                                                txtNumPrinted.Text.Trim(), _
                                                                txtLastPrintDate.Text.Trim(), _
                                                                txtLastUserToPrint.Text.Trim())
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, intResult, strChangeLog, SessionManager.UserID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertSLICEChecksheetMasterData()", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
            Return True
        End Function
        Private Function UpdateSLICEChecksheetMaster() As Boolean
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

                SLICEChecksheetMaster.UpdateSLICEChecksheetMaster(txtSLICEChecksheetID.Text.Trim(), _
                                                                  ddlCheckSheetTemplates.SelectedItem.Value, _
                                                                  txtReleaseDate.Text.Trim(), _
                                                                  txtDueDate.Text.Trim(), _
                                                                  ddlCheckSheetStatus.SelectedValue.ToString(), _
                                                                  txtCreatedUserId.Text.Trim(), _
                                                                  txtCreateDate.Text.Trim(), _
                                                                  txtNumPrinted.Text.Trim(), _
                                                                  txtLastPrintDate.Text.Trim(), _
                                                                  txtLastUserToPrint.Text.Trim())
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueCheckSheetID, strChangeLog, SessionManager.UserID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateSLICEChecksheetMaster() ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
            Return True
        End Function
        Private Function DeleteSLICEChecksheetMaster() As Boolean
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
                SLICEChecksheetMaster.DeleteSLICEChecksheetMaster(CInt(txtSLICEChecksheetID.Text.Trim()))
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueCheckSheetID, "SLICE Checksheet Deleted", SessionManager.UserID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertSLICEChecksheetMasterData()", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
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
            objDic.Add("SLICEChecksheetReleaseDate", txtReleaseDate.Text.Trim())
            objDic.Add("SLICEChecksheetDueDate", txtDueDate.Text.Trim())
            If ddlCheckSheetStatus.SelectedItem IsNot Nothing Then
                objDic.Add("SLICEChecksheetStatus", ddlCheckSheetStatus.SelectedItem.Text)
            End If
            objDic.Add("CreateUserID", txtCreatedUserId.Text.Trim())
            objDic.Add("CreatedDateTime", txtCreateDate.Text.Trim())
            objDic.Add("NumberPrinted", txtNumPrinted.Text.Trim())
            objDic.Add("LastPrintedDateTime", txtLastPrintDate.Text.Trim())
            objDic.Add("LastPrintedUserID", txtLastUserToPrint.Text.Trim())
            Return objDic
        End Function
#End Region

    End Class
End Namespace

