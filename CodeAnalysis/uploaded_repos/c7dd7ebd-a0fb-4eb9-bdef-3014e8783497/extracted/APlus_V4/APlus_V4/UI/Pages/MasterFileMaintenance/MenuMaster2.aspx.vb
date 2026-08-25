#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports System.Collections.Generic

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class MenuMaster2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Menu Master"
        Private Shared ReadOnly ProgramName As String = "MenuMaster2"
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
            Dim myTabArray() As Object = {ddlMenu, _
                                          txtMenuText, _
                                          ddlMenuType, _
                                          ckShowProgramGroups, _
                                          ckAllowProgramShortcuts, _
                                          ckShowProgramShortcuts, _
                                          chkHideOptionNumbers, _
                                          ckAllowUserSpecifiedColumns, _
                                          txtMaxColumns}
            Dim TabKeyDownArr() As String = {Tab(txtMenuText, txtMaxColumns, "No"), _
                                             Tab(ddlMenuType, ddlMenu, "No"), _
                                             Tab(ckShowProgramGroups, txtMenuText, "No"), _
                                             Tab(ckAllowProgramShortcuts, ddlMenuType, "No"), _
                                             Tab(ckShowProgramShortcuts, ckShowProgramGroups, "No"), _
                                             Tab(chkHideOptionNumbers, ckAllowProgramShortcuts, "No"), _
                                             Tab(ckAllowUserSpecifiedColumns, ckShowProgramShortcuts, "No"), _
                                             Tab(txtMaxColumns, chkHideOptionNumbers, "No"), _
                                             Tab(ddlMenu, ckAllowUserSpecifiedColumns, "Yes")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {txtMenuText, _
                                          ddlMenuType, _
                                          ckShowProgramGroups, _
                                          ckAllowProgramShortcuts, _
                                          ckShowProgramShortcuts, _
                                          chkHideOptionNumbers, _
                                          ckAllowUserSpecifiedColumns, _
                                          txtMaxColumns}
            Dim TabKeyDownArr() As String = {Tab(ddlMenuType, txtMaxColumns, "No"), _
                                             Tab(ckShowProgramGroups, txtMenuText, "No"), _
                                             Tab(ckAllowProgramShortcuts, ddlMenuType, "No"), _
                                             Tab(ckShowProgramShortcuts, ckShowProgramGroups, "No"), _
                                             Tab(chkHideOptionNumbers, ckAllowProgramShortcuts, "No"), _
                                             Tab(ckAllowUserSpecifiedColumns, ckShowProgramShortcuts, "No"), _
                                             Tab(txtMaxColumns, chkHideOptionNumbers, "No"), _
                                             Tab(txtMenuText, ckAllowUserSpecifiedColumns, "Yes")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
#End Region

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, ProgramName, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Master.IconImage = Request.ApplicationPath + "/images/signpost.gif"
            Master.HeaderMessage = FormName & " - " & SessionManager.MenuMode.Replace("Row", "") & " Menu"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                LoadDropDownLists()

                Select Case SessionManager.MenuMode
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "EditRow"
                        LoadSelectedRecord()
                        LoadEditModeJavaScripts()
                        UnEnableRecords()
                        txtMenuText.Focus()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        pnlOKCancel.Visible = True
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Menu.');")
                        TransactionHistory.LockControl = True
                    Case "AddRow"
                        TransactionHistory.Visible = False
                        LoadMenus()
                        LoadAddModeJavaScripts()
                        UnEnableRecords()
                        ddlMenu.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("MenuMaster1"), False)
                End Select
            End If
        End Sub
        Private Sub btnOK_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim blnSuccess As Boolean

            Select Case SessionManager.MenuMode
                Case "DeleteRow"
                    blnSuccess = DeleteMenu()
                Case "EditRow"
                    blnSuccess = UpdateMenu()
                Case "AddRow"
                    blnSuccess = InsertMenu()
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueMenu)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.MenuMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("MenuMaster1"), False)
            End If
        End Sub
        Private Sub btnCancel_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnCancel.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueMenu)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.MenuMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("MenuMaster1"), False)
        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueMenu)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.MenuMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("MenuMaster1"), False)
        End Sub
        Private Sub btnProgramGroups_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnProgramGroups.Click, btnProgramGroups2.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Page.Validate()
            If UpdateMenu() Then
                SessionManager.MasterControlExitProgram = ProgramName
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("MenuProgramGroupMaster1"), False)
            End If
        End Sub
        Private Sub btnMenuOptionMaster_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnMenuOptionMaster.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Page.Validate()
            If UpdateMenu() Then
                SessionManager.SelectedValueOptionMenu = SessionManager.SelectedValueMenu
                SessionManager.MasterControlExitProgram = ProgramName
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("MenuOptionMaster1"), False)
            End If
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadMenus()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                ddlMenu.Items.Clear()
                ProgramMaster.GetMenuProgramList(ddlMenu)
                If ddlMenu.Items.Count = 1 Then
                    Master.DisplayError("There are NO Program that can be used as a Menu.")
                    SessionManager.MenuMode = "ViewRow"
                    UnEnableRecords()
                    btnProgramGroups2.Visible = False
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadMenus", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
            End Try
        End Sub

        Private Sub LoadDropDownLists()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                ddlMenuType.Items.Clear()
                MenuTypeMaster.SelectMenuTypeList(ddlMenuType)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadDropDownLists", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
            End Try
        End Sub

        Private Sub LoadSelectedRecord()


            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim dt As DataTable = MenuMaster.SelectMenuMasterByKey(SessionManager.SelectedValueMenu)
                Dim lstitem As ListItem
                If SessionManager.RecordTransactionCurrentValues IsNot Nothing Then
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RecordTransactionCurrentValues)
                End If
                TransactionHistory.RecordID = SessionManager.SelectedValueMenu.Trim()

                If dt.Rows.Count <> 0 Then
                    Dim dr As DataRow = dt.Rows(0)
                    txtMenu.Text = dr("Menu").ToString
                    txtMenuText.Text = dr("MenuText").ToString
                    txtMenuType.Text = dr("MenuType").ToString
                    lstitem = ddlMenuType.Items.FindByValue(txtMenuType.Text)
                    If Not IsNothing(lstitem) Then
                        lstitem.Selected = True
                    End If
                    ckShowProgramGroups.Checked = dr("ShowProgramGroups")
                    ckAllowProgramShortcuts.Checked = dr("AllowProgramShortcuts")
                    ckShowProgramShortcuts.Checked = dr("ShowProgramShortcuts")
                    ckAllowUserSpecifiedColumns.Checked = dr("AllowUserSpecifiedColumns")
                    txtMaxColumns.Text = dr("MaxColumns").ToString
                    chkHideOptionNumbers.Checked = dr("HideOptionNumbers")

                    Dim objDic As New Dictionary(Of String, String)
                    objDic.Add("Menu", txtMenu.Text.Trim())
                    objDic.Add("MenuText", txtMenuText.Text.Trim())
                    objDic.Add("MenuType", ddlMenuType.SelectedItem.Value.Trim())
                    objDic.Add("ShowProgramGroups", ckShowProgramGroups.Checked)
                    objDic.Add("AllowProgramShortcuts", ckAllowProgramShortcuts.Checked)
                    objDic.Add("ShowProgramShortcuts", ckShowProgramShortcuts.Checked)
                    objDic.Add("HideOptionNumbers", chkHideOptionNumbers.Checked)
                    objDic.Add("AllowUserSpecifiedColumns", ckAllowUserSpecifiedColumns.Checked)
                    objDic.Add("MaxColumns", txtMaxColumns.Text.Trim())
                    SessionManager.RecordTransactionCurrentValues = objDic
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
            End Try
        End Sub

        Private Sub UnEnableRecords()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Select Case SessionManager.MenuMode
                Case "ViewRow", "DeleteRow"
                    If SessionManager.MenuMode = "DeleteRow" Then
                        pnlOKCancel.Visible = True
                        pnlExit.Visible = False
                    Else
                        pnlOKCancel.Visible = False
                        pnlExit.Visible = True
                    End If
                    txtMenu.Visible = True
                    ddlMenu.Visible = False
                    txtMenuText.ReadOnly = True
                    txtMenuText.CssClass = "Textbox_Display"
                    ddlMenuType.Visible = False
                    txtMenuType.Visible = True
                    ckShowProgramGroups.Enabled = False
                    ckAllowProgramShortcuts.Enabled = False
                    ckShowProgramShortcuts.Enabled = False
                    ckAllowUserSpecifiedColumns.Enabled = False
                    chkHideOptionNumbers.Enabled = False
                    txtMaxColumns.ReadOnly = True
                    txtMaxColumns.CssClass = "Textbox_Display"
                Case "EditRow"
                    reqMenu.Enabled = False
                    txtMenu.Visible = True
                    ddlMenu.Visible = False
                Case "AddRow"
                    txtMenu.Visible = False
                    ddlMenu.Visible = True
            End Select
        End Sub

        Private Function InsertMenu() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
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

                MenuMaster.InsertMenu(ddlMenu.SelectedItem.Value, txtMenuText.Text, ddlMenuType.SelectedItem.Value, ckShowProgramGroups.Checked, ckAllowProgramShortcuts.Checked, ckShowProgramShortcuts.Checked, txtMaxColumns.Text, ckAllowUserSpecifiedColumns.Checked, chkHideOptionNumbers.Checked)
                RecordTransactionHistory.InsertRecordTransactionHistory("MenuMaster", ddlMenu.SelectedItem.Value, strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertMenu", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function

        Private Function UpdateMenu() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
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
                MenuMaster.UpdateMenu(txtMenu.Text, txtMenuText.Text, ddlMenuType.SelectedItem.Value, ckShowProgramGroups.Checked, ckAllowProgramShortcuts.Checked, ckShowProgramShortcuts.Checked, txtMaxColumns.Text, ckAllowUserSpecifiedColumns.Checked, chkHideOptionNumbers.Checked)
                RecordTransactionHistory.InsertRecordTransactionHistory("MenuMaster", txtMenu.Text, strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateMenu", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function

        Private Function DeleteMenu() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                MenuMaster.DeleteMenu(txtMenu.Text)
                RecordTransactionHistory.InsertRecordTransactionHistory("MenuMaster", txtMenu.Text, "Menu Deleted", SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteMenu", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
        End Function

        Private Function GetUpdatedValues() As Dictionary(Of String, String)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try
            Dim objDic As New Dictionary(Of String, String)
            Try
                If SessionManager.MenuMode = "AddRow" Then
                    objDic.Add("Menu", ddlMenu.SelectedItem.Value)
                Else
                    objDic.Add("Menu", txtMenu.Text.Trim())
                End If
                objDic.Add("MenuText", txtMenuText.Text.Trim())
                objDic.Add("MenuType", ddlMenuType.SelectedItem.Value)
                objDic.Add("ShowProgramGroups", ckShowProgramGroups.Checked)
                objDic.Add("AllowProgramShortcuts", ckAllowProgramShortcuts.Checked)
                objDic.Add("ShowProgramShortcuts", ckShowProgramShortcuts.Checked)
                objDic.Add("AllowUserSpecifiedColumns", ckAllowUserSpecifiedColumns.Checked)
                objDic.Add("MaxColumns", txtMaxColumns.Text.Trim())
                objDic.Add("HideOptionNumbers", chkHideOptionNumbers.Checked)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - GetUpdatedValues", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
            Return objDic
        End Function
#End Region

    End Class
End Namespace