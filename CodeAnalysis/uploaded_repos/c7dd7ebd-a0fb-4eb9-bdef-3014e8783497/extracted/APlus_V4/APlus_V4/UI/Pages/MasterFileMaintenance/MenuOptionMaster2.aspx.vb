#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports System.Collections.Generic

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class MenuOptionMaster2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Menu Option Master"
        Private Shared ReadOnly ProgramName As String = "MenuOptionMaster2"
#End Region

#Region " Load JavaScripts"
        Private Sub LoadJavaScript()
            Dim StatusArr() As WebControl = {btnOK, btnCancel, btnExit}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel", "Exit"}
            Dim OutMessageArr() As String = {"", "", ""}

            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnExit.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
        End Sub
        Private Sub LoadAddModeJavaScript()
            Dim myTabArray() As Object = {ddlMenu, _
                                          txtOption, _
                                          txtDescription, _
                                          ddlProgram, _
                                          txtLinkURL, _
                                          ddlProgramGroup}

            Dim TabKeyDownArr() As String = {Tab(txtOption, ddlProgramGroup, "No"), _
                                             Tab(txtDescription, ddlMenu, "Yes"), _
                                             Tab(ddlProgram, txtOption, "No"), _
                                             Tab(txtLinkURL, txtDescription, "No"), _
                                             Tab(ddlProgramGroup, ddlProgram, "No"), _
                                             Tab(ddlMenu, txtLinkURL, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
        Private Sub LoadEditModeJavaScript()
            Dim myTabArray() As Object = {txtDescription, _
                                          ddlProgram, _
                                          txtLinkURL, _
                                          ddlProgramGroup}

            Dim TabKeyDownArr() As String = {Tab(ddlProgram, ddlProgramGroup, "No"), _
                                             Tab(txtLinkURL, txtDescription, "No"), _
                                             Tab(ddlProgramGroup, ddlProgram, "No"), _
                                             Tab(txtDescription, txtLinkURL, "No")}

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
            Master.HeaderMessage = FormName & " - " & SessionManager.MenuOptionMode.Replace("Row", "")
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadJavaScript()

            If Page.IsPostBack Then
                Select Case SessionManager.MenuOptionMode
                    Case "AddRow"
                        LoadAddModeJavaScript()
                        ddlMenu.Focus()
                End Select
            Else
                LoadDropDownLists()

                Select Case SessionManager.MenuOptionMode
                    Case "ViewRow"
                        pnlOKCancel.Visible = False
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        SetControls()
                    Case "EditRow"
                        LoadSelectedRecord()
                        SetControls()
                        LoadEditModeJavaScript()
                        txtDescription.Focus()
                    Case "AddRow"
                        TransactionHistory.Visible = False
                        SetControls()
                        LoadAddModeJavaScript()
                        ddlMenu.Focus()

                        'if we have a selected menu, use it
                        If SessionManager.SelectedValueOptionMenu <> "" OrElse SessionManager.SelectedValueMenu <> "" Then
                            Dim strMenu As String = ""
                            If SessionManager.SelectedValueOptionMenu.Trim.Length > 0 Then
                                strMenu = SessionManager.SelectedValueOptionMenu.Trim
                            ElseIf SessionManager.SelectedValueMenu.Trim.Length > 0 Then
                                strMenu = SessionManager.SelectedValueMenu.Trim
                            End If

                            If strMenu.Trim.Length > 0 Then
                                Dim objItem As ListItem = ddlMenu.Items.FindByValue(strMenu)
                                If objItem IsNot Nothing Then
                                    objItem.Selected = True
                                    txtMenu.Text = objItem.Text

                                    ddlMenu.Visible = False
                                    txtMenu.Visible = True

                                    BindProgramGroups()
                                End If
                            End If
                        End If
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        SetControls()
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Menu Option.');")
                        TransactionHistory.LockControl = True
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("MenuOptionMaster1"), False)
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
            Select Case SessionManager.MenuOptionMode
                Case "DeleteRow"
                    blnSuccess = DeleteMenuOption()
                Case "EditRow"
                    blnSuccess = UpdateMenuOption()
                Case "AddRow"
                    blnSuccess = InsertMenuOption()
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueOptionMenu)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueOption)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.MenuOptionMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("MenuOptionMaster1"), False)
            End If
        End Sub
        Private Sub btnCancel_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnCancel.Click, btnExit.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueOptionMenu)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueOption)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.MenuOptionMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("MenuOptionMaster1"), False)
        End Sub
        Private Sub ddlMenu_SelectedIndexChanged(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles ddlMenu.SelectedIndexChanged
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            txtMenu.Text = ddlMenu.SelectedItem.Value
            BindProgramGroups()
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadDropDownLists()
            Try
                BindMenu()
                BindProgram()
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadDropDownLists", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindMenu()
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
                ProgramMaster.GetMenuList(ddlMenu)
                ddlMenu.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindMenu", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindProgram()
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
                ProgramMaster.GetProgramList(ddlProgram)
                ddlProgram.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindProgram", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindProgramGroups()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            ddlProgramGroup.Items.Clear()
            Try
                If txtMenu.Text.Trim.Length > 0 Then
                    MenuProgramGroupMaster.SelectProgramGroupsListByMenu(ddlProgramGroup, txtMenu.Text.Trim)
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindProgramGroups", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
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
                If SessionManager.RecordTransactionCurrentValues IsNot Nothing Then
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RecordTransactionCurrentValues)
                End If
                TransactionHistory.RecordID = SessionManager.SelectedValueOptionMenu.Trim() & "," & SessionManager.SelectedValueOption

                Dim objDT As DataTable = MenuOptionMaster.SelectMenuOptionMasterByKey(SessionManager.SelectedValueOptionMenu, SessionManager.SelectedValueOption)
                If objDT IsNot Nothing AndAlso objDT.Rows.Count > 0 Then
                    Dim dtRow As DataRow = objDT.Rows(0)
                    Dim objItem As ListItem

                    objItem = ddlMenu.Items.FindByValue(SessionManager.SelectedValueOptionMenu)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                        txtMenu.Text = objItem.Text
                    End If
                    txtOption.Text = SessionManager.SelectedValueOption
                    txtDescription.Text = dtRow("OptionDescription").ToString.Trim
                    objItem = ddlProgram.Items.FindByValue(dtRow("Program").ToString)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                        txtProgram.Text = objItem.Text
                    End If
                    txtLinkURL.Text = dtRow("LinkURL").ToString.Trim
                    BindProgramGroups()
                    objItem = ddlProgramGroup.Items.FindByValue(dtRow("ProgramGroup").ToString)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                        txtProgramGroup.Text = objItem.Text
                    End If
                End If

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("Menu", txtMenu.Text.Trim())
                objDic.Add("OptionValue", txtOption.Text.Trim())
                objDic.Add("OptionDescription", txtDescription.Text.Trim())
                objDic.Add("Program", ddlProgram.SelectedItem.Value.Trim())
                objDic.Add("LinkURL", txtLinkURL.Text.Trim())
                objDic.Add("ProgramGroup", ddlProgramGroup.SelectedItem.Value.Trim())
                SessionManager.RecordTransactionCurrentValues = objDic
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub SetControls()
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
                Select Case SessionManager.MenuOptionMode
                    Case "EditRow"
                        txtMenu.Visible = True
                        ddlMenu.Visible = False
                        txtOption.ReadOnly = True
                        txtOption.CssClass = "Textbox_Display"
                        txtProgram.Visible = False
                        ddlProgram.Visible = True
                    Case "AddRow"
                        txtOption.Text = ""
                        txtDescription.Text = ""
                        txtProgram.Visible = False
                        ddlProgram.Visible = True
                        txtMenu.Visible = False
                        ddlMenu.Visible = True
                        txtOption.ReadOnly = False
                        txtOption.CssClass = "Textbox_Entry"
                    Case Else
                        txtMenu.Visible = True
                        ddlMenu.Visible = False
                        txtOption.ReadOnly = True
                        txtOption.CssClass = "Textbox_Display"
                        txtDescription.ReadOnly = True
                        txtDescription.CssClass = "Textbox_Display"
                        txtProgram.Visible = True
                        ddlProgram.Visible = False
                        txtLinkURL.ReadOnly = True
                        txtLinkURL.CssClass = "Textbox_Display"
                        txtProgramGroup.Visible = True
                        ddlProgramGroup.Visible = False
                End Select
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - SetControls", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Function InsertMenuOption() As Boolean
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
                If (ddlProgram.SelectedValue.ToString.Trim.Length > 0 AndAlso txtLinkURL.Text.Trim.Length > 0) _
                OrElse (ddlProgram.SelectedValue.ToString.Trim.Length = 0 AndAlso txtLinkURL.Text.Trim.Length = 0) Then
                    Master.DisplayError("You must select either a program or a link URL")
                    Return False
                End If

                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                MenuOptionMaster.InsertMenuOption(ddlMenu.SelectedItem.Text.Trim, txtOption.Text.Trim, txtDescription.Text.Trim, ddlProgram.SelectedItem.Text.Trim, txtLinkURL.Text.Trim, ddlProgramGroup.SelectedItem.Value)
                RecordTransactionHistory.InsertRecordTransactionHistory("MenuOptionMaster", ddlMenu.SelectedItem.Value & "," & txtOption.Text.Trim, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertMenuOption", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateMenuOption() As Boolean
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
                If (ddlProgram.SelectedValue.ToString.Trim.Length > 0 AndAlso txtLinkURL.Text.Trim.Length > 0) _
                OrElse (ddlProgram.SelectedValue.ToString.Trim.Length = 0 AndAlso txtLinkURL.Text.Trim.Length = 0) Then
                    Master.DisplayError("You must select either a program or a link URL")
                    Return False
                End If

                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.CompareDictionaryValues(SessionManager.RecordTransactionCurrentValues, objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                MenuOptionMaster.UpdateMenuOption(txtMenu.Text, txtOption.Text.Trim, txtDescription.Text.Trim, ddlProgram.SelectedItem.Text.Trim, txtLinkURL.Text.Trim, ddlProgramGroup.SelectedItem.Value)
                RecordTransactionHistory.InsertRecordTransactionHistory("MenuOptionMaster", txtMenu.Text.Trim() & "," & txtOption.Text.Trim, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateMenuOption", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function DeleteMenuOption() As Boolean
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
                MenuOptionMaster.DeleteMenuOption(Trim(txtMenu.Text), txtOption.Text)
                RecordTransactionHistory.InsertRecordTransactionHistory("MenuOptionMaster", txtMenu.Text.Trim() & "," & txtOption.Text.Trim, "Menu Option Deleted", SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteMenuOption", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
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
                If ddlMenu.SelectedItem IsNot Nothing Then
                    objDic.Add("Menu", ddlMenu.SelectedItem.Value)
                End If
                objDic.Add("OptionValue", txtOption.Text.Trim())
                objDic.Add("OptionDescription", txtDescription.Text.Trim())
                If ddlProgram.SelectedItem IsNot Nothing Then
                    objDic.Add("Program", ddlProgram.SelectedItem.Text.Trim.Trim())
                End If
                objDic.Add("LinkURL", txtLinkURL.Text.Trim())
                If ddlProgramGroup.SelectedItem IsNot Nothing Then
                    objDic.Add("ProgramGroup", ddlProgramGroup.SelectedItem.Value)
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - GetUpdatedValues", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
            Return objDic
        End Function
#End Region

    End Class
End Namespace