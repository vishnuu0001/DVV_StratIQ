#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.UI.CustomControls
Imports System.Collections.Generic

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class ProgramMaster2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Program Master"
        Private Shared ReadOnly ProgramName As String = "ProgramMaster2"
        Private Shared ReadOnly DBTableName As String = "ProgramMaster"
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel"}
            Dim OutMessageArr() As String = {"", ""}
            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnExit.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
        End Sub
        Private Sub LoadAddModeJavaScripts()
            Dim myTabArray() As Object = {txtProgram, _
                                          txtProgramURL, _
                                          txtHelpFile, _
                                          txtProgramShortcut, _
                                          chkMenu, _
                                          chkInitialProgram, _
                                          ckTeamSelectionRequired, _
                                          ckTeamBoardSelection, _
                                          txtDescription, _
                                          ddlLinkTypes}

            Dim TabKeyDownArr() As String = {Tab(txtProgramURL, ddlLinkTypes, "No"), _
                                             Tab(txtHelpFile, txtProgram, "No"), _
                                             Tab(txtProgramShortcut, txtProgramURL, "No"), _
                                             Tab(chkMenu, txtHelpFile, "No"), _
                                             Tab(chkInitialProgram, txtProgramShortcut, "No"), _
                                             Tab(ckTeamSelectionRequired, chkMenu, "No"), _
                                             Tab(ckTeamBoardSelection, chkInitialProgram, "No"), _
                                             Tab(txtDescription, ckTeamSelectionRequired, "No"), _
                                             Tab(ddlLinkTypes, ckTeamBoardSelection, "No"), _
                                             Tab(txtProgram, txtDescription, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {txtProgramURL, _
                                          txtHelpFile, _
                                          txtProgramShortcut, _
                                          chkMenu, _
                                          chkInitialProgram, _
                                          ckTeamSelectionRequired, _
                                          ckTeamBoardSelection, _
                                          txtDescription, _
                                          ddlLinkTypes}

            Dim TabKeyDownArr() As String = {Tab(txtHelpFile, ddlLinkTypes, "No"), _
                                             Tab(txtProgramShortcut, txtProgramURL, "No"), _
                                             Tab(chkMenu, txtHelpFile, "No"), _
                                             Tab(chkInitialProgram, txtProgramShortcut, "No"), _
                                             Tab(ckTeamSelectionRequired, chkMenu, "No"), _
                                             Tab(ckTeamBoardSelection, chkInitialProgram, "No"), _
                                             Tab(txtDescription, ckTeamSelectionRequired, "No"), _
                                             Tab(ddlLinkTypes, ckTeamBoardSelection, "No"), _
                                             Tab(txtProgramURL, txtDescription, "No")}

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

            Master.IconImage = Request.ApplicationPath + "/images/form_blue.gif"
            Master.HeaderMessage = FormName & " - " & SessionManager.ProgramMasterMode.Replace("Row", "") & " Program"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                Select Case SessionManager.ProgramMasterMode
                    Case "EditRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        LoadEditModeJavaScripts()
                        txtProgramURL.Focus()
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Program.');")
                        TransactionHistory1.LockControl = True
                        UnEnableRecords()
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        LoadAddModeJavaScripts()
                        txtProgram.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("ProgramMaster1"), False)
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

            Dim blnSuccess As Boolean = False
            Select Case SessionManager.ProgramMasterMode
                Case "EditRow"
                    blnSuccess = UpdateProgram()
                Case "DeleteRow"
                    blnSuccess = DeleteProgram()
                Case "AddRow"
                    blnSuccess = InsertProgram()
            End Select
            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.ProgramMasterMode)
                Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar + (ProgramSecurity.GetProgramURL("ProgramMaster1")), False)
            End If
        End Sub
        Private Sub btnCancel_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnCancel.Click, btnExit.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.ProgramMasterMode)
            Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar + (ProgramSecurity.GetProgramURL("ProgramMaster1")), False)
        End Sub
#End Region

#Region " Custom Methods"
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

            Select Case SessionManager.ProgramMasterMode
                Case "ViewRow", "DeleteRow"
                    If SessionManager.ProgramMasterMode = "ViewRow" Then
                        pnlOKCancel.Visible = False
                    End If
                    txtProgram.ReadOnly = True
                    txtProgramURL.ReadOnly = True
                    txtHelpFile.ReadOnly = True
                    txtProgram.CssClass = "Textbox_Display"
                    txtProgramURL.CssClass = "Textbox_Display"
                    txtHelpFile.CssClass = "Textbox_Display"
                    txtProgramShortcut.ReadOnly = True
                    txtProgramShortcut.CssClass = "Textbox_Display"
                    chkMenu.Enabled = False
                    chkInitialProgram.Enabled = False
                    ckTeamSelectionRequired.Enabled = False
                    ckTeamBoardSelection.Enabled = False
                    txtDescription.ReadOnly = True
                    txtDescription.CssClass = "Textbox_Display"
                    ddlLinkTypes.Visible = False
                    txtLinkType.Visible = True
                Case "EditRow"
                    txtProgram.ReadOnly = True
                    txtProgram.CssClass = "Textbox_Display"
            End Select
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

            If SessionManager.RecordTransactionCurrentValues IsNot Nothing Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RecordTransactionCurrentValues)
            End If
            TransactionHistory1.TableName = DBTableName
            TransactionHistory1.RecordID = SessionManager.SelectedValue

            Try
                Dim ds As DataTable = ProgramMaster.SelectProgramMaster(SessionManager.SelectedValue)
                Dim dr As DataRow = ds.Rows(0)
                txtProgram.Text = dr("Program").ToString.Trim()
                txtProgramURL.Text = dr("ProgramURL").ToString.Trim()
                txtHelpFile.Text = dr.Item("HelpFile").ToString.Trim()
                chkMenu.Checked = CType(dr("MenuYN"), Boolean)
                chkInitialProgram.Checked = CType(dr.Item("InitialProgramYN"), Boolean)
                txtProgramShortcut.Text = dr("ProgramShortcut").ToString
                ckTeamSelectionRequired.Checked = CType(dr.Item("TeamSelectionRequired"), Boolean)
                ckTeamBoardSelection.Checked = CType(dr.Item("AllowTeamBoardMenuOptionMasterSelection"), Boolean)
                txtDescription.Text = dr.Item("TeamBoardMenuOptionMasterDescription").ToString
                txtLinkType.Text = dr.Item("LinkType").ToString

                If dr.Item("LinkType") IsNot DBNull.Value Then
                    Dim objItems As ListItem = ddlLinkTypes.Items.FindByValue(dr.Item("LinkType"))
                    If objItems IsNot Nothing Then
                        objItems.Selected = True
                    End If
                End If

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("ProgramURL", txtProgramURL.Text.Trim())
                objDic.Add("HelpFile", txtHelpFile.Text.Trim())
                objDic.Add("ProgramShortcut", txtProgramShortcut.Text.Trim())
                objDic.Add("MenuYN", chkMenu.Checked)
                objDic.Add("InitialProgramYN", chkInitialProgram.Checked)
                objDic.Add("TeamSelectionRequired", ckTeamSelectionRequired.Checked)
                objDic.Add("AllowTeamBoardMenuOptionMasterSelection", ckTeamBoardSelection.Checked)
                objDic.Add("TeamBoardMenuOptionMasterDescription", txtDescription.Text.Trim())
                objDic.Add("LinkType", ddlLinkTypes.SelectedItem.Value.Trim())
                SessionManager.RecordTransactionCurrentValues = objDic
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Function DeleteProgram() As Boolean
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
                ProgramMaster.DeleteProgramMaster(txtProgram.Text.Trim)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, txtProgram.Text.Trim, "Program Deleted", SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteProgram", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
        End Function
        Private Function UpdateProgram() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If ckTeamBoardSelection.Checked = True Then
                If txtDescription.Text.Trim.Length = 0 Or ddlLinkTypes.SelectedItem.Text.Trim.Length = 0 Then
                    Master.DisplayError(GetTranslationString("needtbdandlink", "You must have Both a Team Board Description AND a Link Type"))
                    Return False
                End If
            End If

            Try
                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.CompareDictionaryValues(SessionManager.RecordTransactionCurrentValues, objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                ProgramMaster.UpdateProgramMaster(txtProgram.Text.Trim, txtProgramURL.Text.Trim, chkMenu.Checked, chkInitialProgram.Checked, txtHelpFile.Text.Trim, ckTeamSelectionRequired.Checked, ckTeamBoardSelection.Checked, txtDescription.Text.Trim, ddlLinkTypes.SelectedItem.Value.Trim(), txtProgramShortcut.Text)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, txtProgram.Text.Trim, strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateProgram", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function InsertProgram() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If ckTeamBoardSelection.Checked = True Then
                If txtDescription.Text.Trim.Length = 0 Or ddlLinkTypes.SelectedItem.Text.Trim.Length = 0 Then
                    Master.DisplayError(GetTranslationString("needtbdandlink", "You must have Both a Team Board Description AND a Link Type"))
                    Return False
                End If
            End If

            Try
                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If
                ProgramMaster.AddProgramMaster(txtProgram.Text.Trim, txtProgramURL.Text.Trim, chkMenu.Checked, chkInitialProgram.Checked, txtHelpFile.Text, ckTeamSelectionRequired.Checked, ckTeamBoardSelection.Checked, txtDescription.Text, ddlLinkTypes.SelectedItem.Value.Trim(), txtProgramShortcut.Text)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, txtProgram.Text.Trim, strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertProgram", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
#End Region

#Region " Get Updated Values"
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
            objDic.Add("ProgramURL", txtProgramURL.Text.Trim())
            objDic.Add("HelpFile", txtHelpFile.Text.Trim())
            objDic.Add("ProgramShortcut", txtProgramShortcut.Text.Trim())
            objDic.Add("MenuYN", chkMenu.Checked.ToString)
            objDic.Add("InitialProgramYN", chkInitialProgram.Checked.ToString)
            objDic.Add("TeamSelectionRequired", ckTeamSelectionRequired.Checked.ToString)
            objDic.Add("AllowTeamBoardMenuOptionMasterSelection", ckTeamBoardSelection.Checked.ToString)
            objDic.Add("TeamBoardMenuOptionMasterDescription", txtDescription.Text.Trim())
            objDic.Add("LinkType", ddlLinkTypes.SelectedItem.Value.Trim())
            Return objDic
        End Function
#End Region

    End Class
End Namespace
