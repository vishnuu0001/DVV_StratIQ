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
    Partial Class TeamBoardMenuDefaults2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Team Board Menu Defaults"
        Private Shared ReadOnly ProgramName As String = "TeamBoardMenuDefaults2"
        Private Shared ReadOnly DBTableName As String = "TeamBoardMenuDefaults"
        Private strLinkType As String = ""
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
        Private Sub LoadAddEditModeJavaScripts()
            Dim myTabArray() As Object = {txtBoardColumn, _
                                          txtBoardRow, _
                                          txtRCSequence, _
                                          txtDescription, _
                                          ddlProgram, _
                                          txtLinkFileURL, _
                                          ckDefault, _
                                          ckTeamFolderDocument}

            Dim TabKeyDownArr() As String = {Tab(txtBoardRow, ckTeamFolderDocument, "Int"), _
                                             Tab(txtRCSequence, txtBoardColumn, "Int"), _
                                             Tab(txtDescription, txtBoardRow, "Int"), _
                                             Tab(ddlProgram, txtRCSequence, "No"), _
                                             Tab(txtLinkFileURL, txtDescription, "No"), _
                                             Tab(ckDefault, ddlProgram, "No"), _
                                             Tab(ckTeamFolderDocument, txtLinkFileURL, "No"), _
                                             Tab(txtBoardColumn, ckDefault, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
#End Region

#Region " Load Culture Translations"
        Private Sub LoadCultureTranslations()
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
                lblSite.Text = GetTranslationString("site", lblSite.Text.Replace(":", "")) & ":"
                lblBoardColumn.Text = GetTranslationString("boardcolumn", lblBoardColumn.Text.Replace(":", "")) & ":"
                lblBoardRow.Text = GetTranslationString("boardrow", lblBoardRow.Text.Replace(":", "")) & ":"
                lblRCSequence.Text = GetTranslationString("rcsequence", lblRCSequence.Text.Replace(":", "")) & ":"
                lblDescription.Text = GetTranslationString("boarddescription", lblDescription.Text.Replace(":", "")) & ":"
                lblProgram.Text = GetTranslationString("program", lblProgram.Text.Replace(":", "")) & ":"
                lblLinkFileURL.Text = GetTranslationString("LinkFileURL", lblLinkFileURL.Text.Replace(":", "")) & ":"
                ckDefault.Text = GetTranslationString("default", ckDefault.Text)
                btnOK.Text = GetTranslationString("ok", btnOK.Text)
                btnCancel.Text = GetTranslationString("cancel", btnCancel.Text)
                btnExit.Text = GetTranslationString("exit", btnExit.Text)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadCultureTranslations", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
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

            Master.HeaderMessage = GetTranslationString(FormName, FormName) & " - " & GetTranslationString(SessionManager.TeamUsersMode.Replace("Row", ""), SessionManager.TeamUsersMode.Replace("Row", ""))
            Master.IconImage = Request.ApplicationPath + "/images/usergroup.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                LoadCultureTranslations()

                BindProgram()

                Select Case SessionManager.TeamBoardMenuDefaultsMode.ToString()
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        pnlOKCancel.Visible = True
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete these defaults.');")
                        TransactionHistory1.LockControl = True
                    Case "EditRow"
                        LoadAddEditModeJavaScripts()
                        LoadSelectedRecord()
                        UnEnableRecords()
                        txtBoardColumn.Focus()
                    Case "AddRow"
                        If SessionManager.WorkingSiteID = 0 Then
                            RemoveCurrentProgramandGoBack()
                        End If

                        txtTeamBoardMenuDefault.Text = "New"
                        txtSite.Text = SessionManager.WorkingSite

                        LoadAddEditModeJavaScripts()
                        TransactionHistory1.Visible = False
                        UnEnableRecords()
                        txtBoardColumn.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamBoardMenuDefaults1"), False)
                End Select
            End If
        End Sub
        Protected Sub ddlProgram_SelectedIndexChanged(ByVal sender As Object, ByVal e As System.EventArgs) Handles ddlProgram.SelectedIndexChanged
            If ddlProgram.SelectedItem.Text.Trim.Length > 0 Then
                txtDescription.Text = ddlProgram.SelectedItem.Text
            Else
                txtDescription.Text = String.Empty
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
            Select Case SessionManager.TeamBoardMenuDefaultsMode
                Case "AddRow"
                    blnSuccess = InsertTeamBoardMenuDefaults()
                Case "EditRow"
                    blnSuccess = UpdateTeamBoardMenuDefaults()
                Case "DeleteRow"
                    blnSuccess = DeleteTeamBoardMenuDefaults()
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.AreaMaintenanceMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamBoardMenuDefaults1"), False)
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.AreaMaintenanceMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamBoardMenuDefaults1"), False)
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub BindProgram()
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
                ProgramMaster.GetTeamBoardProgramList(ddlProgram)
                ddlProgram.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindProgram", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
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

            Dim objDT As DataTable = TeamBoardMenuDefaults.SelectTeamBoardMenuDefaultsByID(Convert.ToInt16(SessionManager.SelectedValue))
            If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                Dim dtRow As DataRow = objDT.Rows(0)
                Dim objItem As ListItem = Nothing

                txtTeamBoardMenuDefault.Text = SessionManager.SelectedValue
                txtSite.Text = SessionManager.WorkingSite
                txtBoardColumn.Text = dtRow("BoardColumn").ToString
                txtBoardRow.Text = dtRow("BoardRow").ToString
                txtRCSequence.Text = dtRow("RCSequence").ToString
                txtDescription.Text = dtRow("BoardDescription").ToString()
                strLinkType = dtRow("LinkType").ToString()

                objItem = ddlProgram.Items.FindByValue(dtRow("LinkType").ToString.Trim + "-" + dtRow("Program").ToString.Trim)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                    txtProgram.Text = objItem.Text
                End If

                txtLinkFileURL.Text = dtRow("LinkFileURL").ToString()
                ckDefault.Checked = Convert.ToBoolean(dtRow("BoardDefault"))

                If dtRow("LinkType").ToString() = "L" Then
                    ckTeamFolderDocument.Checked = True
                End If

                TransactionHistory1.TableName = DBTableName
                TransactionHistory1.RecordID = SessionManager.SelectedValue.Trim()

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("Site", txtSite.Text.Trim())
                objDic.Add("BoardColumn", txtBoardColumn.Text.Trim())
                objDic.Add("BoardRow", txtBoardRow.Text.Trim())
                objDic.Add("RCSequence", txtRCSequence.Text.Trim())
                objDic.Add("BoardDescription", txtDescription.Text.Trim())
                objDic.Add("LinkType", strLinkType)
                objDic.Add("Program", txtProgram.Text.Trim())
                objDic.Add("LinkFileURL", txtLinkFileURL.Text.Trim())
                objDic.Add("BoardDefault", ckDefault.Checked.ToString)
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

            Select Case SessionManager.TeamBoardMenuDefaultsMode.ToString()
                Case "ViewRow", "DeleteRow"
                    pnlOKCancel.Visible = False
                    txtBoardColumn.ReadOnly = True
                    txtBoardColumn.CssClass = "Textbox_Display"
                    txtBoardRow.ReadOnly = True
                    txtBoardRow.CssClass = "Textbox_Display"
                    txtRCSequence.ReadOnly = True
                    txtRCSequence.CssClass = "Textbox_Display"
                    txtDescription.ReadOnly = True
                    txtDescription.CssClass = "Textbox_Display"
                    ddlProgram.Visible = False
                    'txtProgram.Text = ParseProgram()
                    txtProgram.Visible = True
                    txtProgram.ReadOnly = True
                    txtLinkFileURL.ReadOnly = True
                    txtLinkFileURL.CssClass = "Textbox_Display"
                    ckDefault.Enabled = False
                    ckTeamFolderDocument.Enabled = False
                Case "EditRow"
                    ddlProgram.Visible = True
                    txtProgram.Visible = False
                Case "AddRow"
                    ddlProgram.Visible = True
                    txtProgram.Visible = False
            End Select
        End Sub
        Private Function InsertTeamBoardMenuDefaults() As Boolean
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
                If Not ValidateLinkType() Then
                    Return False
                End If

                Dim strProgram As String = ParseProgram()
                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                Dim iTeamBoardMenuDefault As Integer = TeamBoardMenuDefaults.InsertTeamBoardMenuDefaults(SessionManager.WorkingSiteID, txtBoardColumn.Text.Trim, _
                                                     txtBoardRow.Text.Trim, txtRCSequence.Text.Trim, txtDescription.Text.Trim, strLinkType, _
                                                     strProgram, txtLinkFileURL.Text.Trim, ckDefault.Checked)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, iTeamBoardMenuDefault.ToString, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertTeamBoardMenuDefaults", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateTeamBoardMenuDefaults() As Boolean
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
                If Not ValidateLinkType() Then
                    Return False
                End If

                Dim strProgram As String = ParseProgram()
                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.CompareDictionaryValues(SessionManager.RecordTransactionCurrentValues, objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                TeamBoardMenuDefaults.UpdateTeamBoardMenuDefaults(SessionManager.SelectedValue, _
                                      SessionManager.WorkingSiteID, txtBoardColumn.Text.Trim, txtBoardRow.Text.Trim, _
                                      txtRCSequence.Text.Trim, txtDescription.Text.Trim, strLinkType, _
                                      strProgram, txtLinkFileURL.Text.Trim, _
                                      ckDefault.Checked)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValue.Trim(), strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateTeamBoardMenuDefaults", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function DeleteTeamBoardMenuDefaults() As Boolean
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
                TeamBoardMenuDefaults.DeleteTeamBoardMenuDefaults(SessionManager.SelectedValue)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValue.Trim(), "Savings Type Deleted", SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteTeamBoardMenuDefaults", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
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
            objDic.Add("BoardColumn", txtBoardColumn.Text.Trim())
            objDic.Add("BoardRow", txtBoardRow.Text.Trim())
            objDic.Add("RCSequence", txtRCSequence.Text.Trim())
            objDic.Add("BoardDescription", txtDescription.Text.Trim())
            objDic.Add("LinkType", strLinkType)
            objDic.Add("Program", txtProgram.Text.Trim())
            objDic.Add("txtLinkFileURL", txtLinkFileURL.Text.Trim())
            objDic.Add("BoardDefault", ckDefault.Checked.ToString)

            Return objDic
        End Function
        Private Function ParseProgram() As String
            Dim strProgram As String = ""

            If ddlProgram.SelectedItem IsNot Nothing AndAlso ddlProgram.SelectedItem.Text.Trim.Length > 0 Then
                strProgram = ddlProgram.SelectedItem.Value.ToString.Substring(2)
                txtProgram.Text = ddlProgram.SelectedItem.Text
            End If

            Return strProgram
        End Function
        Private Function ValidateLinkType() As Boolean
            If ddlProgram.SelectedValue.Trim.Length > 0 Then
                If txtDescription.Text.Trim.Length = 0 Then
                    Master.DisplayError("This is a Program, you must enter Board Description")
                    txtDescription.Focus()
                    Return False
                End If

                If txtLinkFileURL.Text.Trim.Length > 0 Then
                    Master.DisplayError("Select either Program or LinkFileURL, not both")
                    ddlProgram.Focus()
                    Return False
                End If

                ckTeamFolderDocument.Checked = False
                strLinkType = ddlProgram.SelectedItem.Value.Substring(0, 1)
            ElseIf txtLinkFileURL.Text.Trim.Length > 0 Then
                If txtDescription.Text.Trim.Length = 0 Then
                    Master.DisplayError("This is a Link, you must enter Board Description")
                    txtDescription.Focus()
                    Return False
                End If
                If ckTeamFolderDocument.Checked Then
                    strLinkType = "L"
                Else
                    'if we have anything that looks like an A+ URL, reject it
                    If txtLinkFileURL.Text.Contains("UI/Pages") Then
                        Master.DisplayError("URL Link not allowed")
                        txtLinkFileURL.Focus()
                        Return False
                    End If

                    strLinkType = "U"
                End If
            Else
                'we must have at LEAST the board description
                If txtDescription.Text.Trim.Length = 0 Then
                    Master.DisplayError("Must have a Board Description")
                    txtDescription.Focus()
                    Return False
                End If
                strLinkType = "D"
            End If

            Return True
        End Function
#End Region

    End Class
End Namespace