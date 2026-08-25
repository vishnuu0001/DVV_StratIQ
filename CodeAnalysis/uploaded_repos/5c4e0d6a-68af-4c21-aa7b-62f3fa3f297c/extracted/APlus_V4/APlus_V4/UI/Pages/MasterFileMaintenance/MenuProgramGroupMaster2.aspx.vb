#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports System.Collections.Generic

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class MenuProgramGroupMaster2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Menu Program Group Master"
        Private Shared ReadOnly ProgramName As String = "MenuProgramGroupMaster2"
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
            Dim myTabArray() As Object = {txtProgramGroup, _
                                          txtColumn, _
                                          txtSortOrder}
            Dim TabKeyDownArr() As String = {Tab(txtColumn, txtSortOrder, "No"), _
                                             Tab(txtSortOrder, txtProgramGroup, "Yes"), _
                                             Tab(txtProgramGroup, txtColumn, "Yes")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {txtColumn, _
                                          txtSortOrder}
            Dim TabKeyDownArr() As String = {Tab(txtSortOrder, txtSortOrder, "Yes"), _
                                             Tab(txtColumn, txtColumn, "Yes")}

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
            Master.HeaderMessage = FormName & " - " & SessionManager.MenuProgramGroupMode.Replace("Row", "") & " Menu"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                Select Case SessionManager.MenuProgramGroupMode
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "EditRow"
                        LoadSelectedRecord()
                        LoadEditModeJavaScripts()
                        UnEnableRecords()
                        txtColumn.Focus()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        pnlOKCancel.Visible = True
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Menu Program Group.');")
                        TransactionHistory.LockControl = True
                    Case "AddRow"
                        TransactionHistory.Visible = False
                        LoadAddModeJavaScripts()
                        txtMenu.Text = SessionManager.SelectedValueMenu
                        UnEnableRecords()
                        txtProgramGroup.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("MenuProgramGroupMaster1"), False)
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

            Select Case SessionManager.MenuProgramGroupMode
                Case "DeleteRow"
                    blnSuccess = DeleteMenuProgramGroup()
                Case "EditRow"
                    blnSuccess = UpdateMenuProgramGroup()
                Case "AddRow"
                    blnSuccess = InsertMenuProgramGroup()
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueProgramGroupMenu)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueProgramGroup)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.MenuProgramGroupMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("MenuProgramGroupMaster1"), False)
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueProgramGroupMenu)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueProgramGroup)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.MenuProgramGroupMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("MenuProgramGroupMaster1"), False)
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueProgramGroupMenu)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueProgramGroup)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.MenuProgramGroupMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("MenuProgramGroupMaster1"), False)
        End Sub
#End Region

#Region " Custom Methods"
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

                TransactionHistory.RecordID = SessionManager.SelectedValueMenu.Trim() & "," & SessionManager.SelectedValueProgramGroup

                Dim dt As DataTable = MenuProgramGroupMaster.SelectMenuProgramGroup(SessionManager.SelectedValueMenu, SessionManager.SelectedValueProgramGroup)
                If dt.Rows.Count <> 0 Then
                    Dim dr As DataRow = dt.Rows(0)
                    txtMenu.Text = dr("Menu").ToString
                    txtProgramGroup.Text = dr("ProgramGroup").ToString
                    txtColumn.Text = dr("MenuColumn").ToString
                    txtSortOrder.Text = dr("SortOrder").ToString

                    Dim objDic As New Dictionary(Of String, String)
                    objDic.Add("Menu", txtMenu.Text.Trim())
                    objDic.Add("ProgramGroup", txtProgramGroup.Text.Trim())
                    objDic.Add("MenuColumn", txtColumn.Text.Trim())
                    objDic.Add("SortOrder", txtSortOrder.Text.Trim())
                    SessionManager.RecordTransactionCurrentValues = objDic
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
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

            Select Case SessionManager.MenuProgramGroupMode
                Case "ViewRow", "DeleteRow"
                    pnlOKCancel.Visible = False
                    txtProgramGroup.Visible = True
                    txtProgramGroup.ReadOnly = True
                    txtProgramGroup.CssClass = "Textbox_Display"
                    txtColumn.ReadOnly = True
                    txtColumn.CssClass = "Textbox_Display"
                    txtSortOrder.ReadOnly = True
                    txtSortOrder.CssClass = "Textbox_Display"
                Case "EditRow"
                    txtProgramGroup.Visible = True
                Case "AddRow"
                    txtProgramGroup.Visible = True
                    txtProgramGroup.ReadOnly = False
                    txtProgramGroup.CssClass = "Textbox_Entry"
            End Select
        End Sub

        Private Function InsertMenuProgramGroup() As Boolean
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
                MenuProgramGroupMaster.InsertMenuProgramGroup(txtMenu.Text, txtProgramGroup.Text.Trim, txtColumn.Text, txtSortOrder.Text)
                RecordTransactionHistory.InsertRecordTransactionHistory("MenuProgramGroupMaster", txtMenu.Text.Trim() & "," & txtProgramGroup.Text.Trim, strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertMenu", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function

        Private Function UpdateMenuProgramGroup() As Boolean
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
                MenuProgramGroupMaster.UpdateMenuProgramGroup(txtMenu.Text, txtProgramGroup.Text, txtColumn.Text, txtSortOrder.Text)
                RecordTransactionHistory.InsertRecordTransactionHistory("MenuProgramGroupMaster", txtMenu.Text.Trim() & "," & txtProgramGroup.Text.Trim, strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateMenuProgramGroup", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function

        Private Function DeleteMenuProgramGroup() As Boolean
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
                MenuProgramGroupMaster.DeleteMenuProgramGroup(txtMenu.Text, txtProgramGroup.Text)
                RecordTransactionHistory.InsertRecordTransactionHistory("MenuProgramGroupMaster", txtMenu.Text.Trim() & "," & txtProgramGroup.Text.Trim, "Menu Program Group Deleted", SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteMenuProgramGroup", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
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
                objDic.Add("Menu", txtMenu.Text.Trim())
                objDic.Add("ProgramGroup", txtProgramGroup.Text.Trim())
                objDic.Add("MenuColumn", txtColumn.Text.Trim())
                objDic.Add("SortOrder", txtSortOrder.Text.Trim())
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - GetUpdatedValues", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
            Return objDic
        End Function
#End Region

    End Class
End Namespace