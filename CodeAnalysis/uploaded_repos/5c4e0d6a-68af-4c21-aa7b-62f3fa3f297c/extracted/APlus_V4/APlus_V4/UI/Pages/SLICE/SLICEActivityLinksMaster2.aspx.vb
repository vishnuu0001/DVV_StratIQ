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
    Partial Class SLICEActivityLinksMaster2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "SLICE Activity Maintenance"
        Private Shared ReadOnly ProgramName As String = "SLICEActivityLinksMaster2"
        Private Shared ReadOnly DBTableName As String = "SLICEActivityLinksMaster"
#End Region

#Region " JavaScript Functions "
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel, btnExit}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel", "Exit"}
            Dim OutMessageArr() As String = {"", "", ""}
            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnExit.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
        End Sub
        Private Sub LoadAddModeJavaScripts()
            Dim myTabArray() As Object = {ddlSLICEActivityLinkTypeID, _
                                          txtExpandLinkDescription, _
                                          txtExpandLinkURL}

            Dim TabKeyDownArr() As String = {Tab(txtExpandLinkDescription, txtExpandLinkURL, "No"), _
                                             Tab(txtExpandLinkURL, ddlSLICEActivityLinkTypeID, "No"), _
                                             Tab(ddlSLICEActivityLinkTypeID, txtExpandLinkDescription, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {ddlSLICEActivityLinkTypeID, _
                                          txtExpandLinkDescription, _
                                          txtExpandLinkURL}

            Dim TabKeyDownArr() As String = {Tab(txtExpandLinkDescription, txtExpandLinkURL, "No"), _
                                             Tab(txtExpandLinkURL, ddlSLICEActivityLinkTypeID, "No"), _
                                             Tab(ddlSLICEActivityLinkTypeID, txtExpandLinkDescription, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
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

            Master.HeaderMessage = FormName & " - " & SessionManager.SLICEActivityLinkMasterMode.Replace("Row", "")
            Master.IconImage = Request.ApplicationPath + "/images/clipboard.png"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                Select Case SessionManager.SLICEActivityLinkMasterMode.ToString()
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        DisableControls()
                    Case "EditRow"
                        LoadSelectedRecord()
                        DisableControls()
                        LoadEditModeJavaScripts()
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        LoadSLICEActivityForAddOperation()
                        BindSliceActivityTypesToDropDown()
                        DisableControls()
                        LoadAddModeJavaScripts()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        DisableControls()
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Activity Link.');")
                        TransactionHistory1.LockControl = True
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEActivityMaster1"), False)
                End Select
            End If
            lblSLICEActivityLinkID.Visible = False
            txtSLICEActivityLinkID.Visible = False
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

            SessionManager.MasterControlExitProgram = "SLICEActivityMaster2"
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEActivityLinksMaster1"), False)
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedSLICEActivityLinksID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SLICEActivityLinkMasterMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEActivityLinksMaster1"), False)
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

            If SessionManager.SLICEActivityLinkMasterMode.ToString.Trim() = "EditRow" Then
                blnSuccess = UpdateSLICEActivityLink()
            ElseIf SessionManager.SLICEActivityLinkMasterMode.ToString.Trim() = "AddRow" Then
                blnSuccess = InsertSLICEActivityLink()
            ElseIf SessionManager.SLICEActivityLinkMasterMode.ToString.Trim() = "DeleteRow" Then
                blnSuccess = DeleteSLICEActivityLink()
            End If

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedSLICEActivityLinksID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SLICEActivityLinkMasterMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEActivityLinksMaster1"), False)
            End If
        End Sub
#End Region

#Region " Custom Methods "
        Public Sub LoadSLICEActivityForAddOperation()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim strTemp As String = String.Empty
            Try
                Dim dt As DataTable = SLICEActivityLinks.SelectActivityLinkDataAsDataTable(SessionManager.SelectedValueSLICEActivityID)
                If dt.Rows.Count > 0 Then
                    txtSLICEActivityID.Text = dt.Rows(0)("SLICEType").ToString().Trim()
                Else
                    If SessionManager.SLICEActivityMasterMode.ToString().Trim().ToUpper() = "EDITROW" Then
                        dt = SLICEActivityLinks.SelectSLICETypeAsDataTable(SessionManager.SelectedValueSLICEActivityID)
                        If dt.Rows.Count > 0 Then
                            strTemp = dt.Rows(0)("SLICEType").ToString().Trim()
                            strTemp = strTemp.Replace(vbCr, "")
                            strTemp = strTemp.Replace(vbLf, " ")
                            txtSLICEActivityID.Text = strTemp
                        End If
                    End If
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub

        Public Sub LoadSelectedRecord()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim objItem As ListItem = Nothing
            Dim strTemp As String = ""

            Try
                Dim dt As DataTable = SLICEActivityLinks.SelectActivityLinkDataAsDataTableByActivityLinkID(SessionManager.SelectedSLICEActivityLinksID)
                If dt.Rows.Count > 0 Then
                    txtExpandLinkDescription.Text = dt.Rows(0)("LinkDescription").ToString().Trim()
                    txtExpandLinkURL.Text = dt.Rows(0)("LinkURL").ToString().Trim()
                    strTemp = dt.Rows(0)("SLICEType").ToString().Trim()
                    strTemp = strTemp.Replace(vbCr, " ")
                    strTemp = strTemp.Replace(vbLf, "")
                    txtSLICEActivityID.Text = strTemp
                    txtSLICEActivityLinkID.Text = dt.Rows(0)("SLICEActivityLinkID").ToString().Trim()
                    txtSLICEActivityLinkTypeID.Text = dt.Rows(0)("SLICEActivityLinkType").ToString().Trim()
                    hdnSLICEActivityID.Text = dt.Rows(0)("SLICEActivityID").ToString().Trim()
                    hdnSLICEActivityLinkTypeID.Text = dt.Rows(0)("SLICEActivityLinkTypeID").ToString.Trim()
                Else
                    txtExpandLinkDescription.Text = ""
                    txtExpandLinkURL.Text = ""
                    txtSLICEActivityID.Text = ""
                    txtSLICEActivityLinkID.Text = ""
                    txtSLICEActivityLinkTypeID.Text = ""
                    hdnSLICEActivityID.Text = ""
                    hdnSLICEActivityLinkTypeID.Text = ""
                End If

                BindSliceActivityTypesToDropDown()
                If dt.Rows.Count > 0 Then
                    objItem = ddlSLICEActivityLinkTypeID.Items.FindByValue(dt.Rows(0)("SLICEActivityLinkTypeID").ToString().Trim())
                End If

                If Not objItem Is Nothing Then
                    objItem.Selected = True
                End If
                TransactionHistory1.TableName = DBTableName
                TransactionHistory1.RecordID = SessionManager.SelectedSLICEActivityLinksID

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("SLICEActivityID", txtSLICEActivityID.Text.Trim())
                objDic.Add("SLICEActivityLinkTypeID", ddlSLICEActivityLinkTypeID.SelectedItem.Text.Trim())
                objDic.Add("LinkDescription", txtExpandLinkDescription.Text.Trim())
                objDic.Add("LinkURL", txtExpandLinkURL.Text.Trim())
                SessionManager.RecordTransactionCurrentValues = objDic
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
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

            Select Case SessionManager.SLICEActivityLinkMasterMode.ToString()
                Case "ViewRow", "DeleteRow"
                    If SessionManager.SLICEActivityLinkMasterMode.ToString() = "ViewRow" Then pnlOKCancel.Visible = False
                    txtSLICEActivityLinkID.CssClass = "Textbox_Display"
                    txtExpandLinkDescription.ReadOnly = True
                    txtExpandLinkDescription.CssClass = "Textbox_Display"
                    txtExpandLinkURL.ReadOnly = True
                    txtExpandLinkURL.CssClass = "Textbox_Display"
                    txtSLICEActivityLinkTypeID.ReadOnly = True
                    txtSLICEActivityLinkTypeID.CssClass = "Textbox_Display"
                    txtSLICEActivityID.ReadOnly = True
                    txtSLICEActivityID.CssClass = "Textbox_Display"
                    ddlSLICEActivityLinkTypeID.Visible = False
                Case "EditRow"
                    ddlSLICEActivityLinkTypeID.Visible = True
                    txtSLICEActivityLinkTypeID.Visible = False
                    txtSLICEActivityID.ReadOnly = True
                    txtSLICEActivityID.CssClass = "Textbox_Display"
                Case "AddRow"
                    txtSLICEActivityID.ReadOnly = True
                    txtSLICEActivityID.CssClass = "Textbox_Display"
                    txtSLICEActivityLinkTypeID.Visible = False
                    ddlSLICEActivityLinkTypeID.Visible = True
                    txtSLICEActivityLinkID.ReadOnly = False
                    txtSLICEActivityLinkID.Text = "New"
                    txtSLICEActivityLinkID.ReadOnly = True
                    reqActivityLinkTypeID.ControlToValidate = "ddlSLICEActivityLinkTypeID"
                    txtExpandLinkURL.Text = ""
                    txtExpandLinkDescription.Text = ""
            End Select
        End Sub
        Private Sub BindSliceActivityTypesToDropDown()
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
                SLICEActivityLinks.SelectActivityLinksTypes(ddlSLICEActivityLinkTypeID)
                ddlSLICEActivityLinkTypeID.Items.Insert(0, " ")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Function InsertSLICEActivityLink() As Boolean
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

                Dim intResult As Integer = SLICEActivityLinks.InsertSLICEActivityLinksMaster(SessionManager.SelectedValueSLICEActivityID, ddlSLICEActivityLinkTypeID.SelectedValue.ToString().Trim(), txtExpandLinkDescription.Text.Trim(), txtExpandLinkURL.Text.Trim())
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, intResult, strChangeLog, SessionManager.UserID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertSLICEActivityLink", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try

            Return True
        End Function
        Private Function UpdateSLICEActivityLink() As Boolean
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

                SLICEActivityLinks.UpdateSLICEActivityLinksMaster(txtSLICEActivityLinkID.Text.Trim(), hdnSLICEActivityID.Text.Trim(), ddlSLICEActivityLinkTypeID.SelectedValue.ToString().Trim(), txtExpandLinkDescription.Text.Trim(), txtExpandLinkURL.Text.Trim())
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedSLICEActivityLinksID, strChangeLog, SessionManager.UserID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateSLICEActivityLinksMaster", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try

            Return True
        End Function
        Private Function DeleteSLICEActivityLink() As Boolean
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
                SLICEActivityLinks.DeleteSLICEActivityLink(SessionManager.SelectedSLICEActivityLinksID)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedSLICEActivityLinksID, "SLICE Activity Link Deleted", SessionManager.UserID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteSLICEActivityLinksMaster", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
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
            objDic.Add("SLICEActivityID", txtSLICEActivityID.Text.Trim())
            objDic.Add("SLICEActivityLinkTypeID", ddlSLICEActivityLinkTypeID.SelectedItem.Text.Trim())
            objDic.Add("LinkDescription", txtExpandLinkDescription.Text.Trim())
            objDic.Add("LinkURL", txtExpandLinkURL.Text.Trim())
            Return objDic
        End Function
#End Region

    End Class
End Namespace

