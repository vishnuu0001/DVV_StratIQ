#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.UI.CustomControls
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class QueryMaster4
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Query Master"
        Private Shared ReadOnly ProgramName As String = "QueryMaster4"
        Private colControls As New Collection
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
        Private Sub LoadEditModeJavaScripts()
            Dim iCounter As Integer
            Dim strNext As String
            Dim strPrevious As String

            If colControls.Count > 1 Then
                For iCounter = 1 To colControls.Count
                    If iCounter = 1 Then
                        strNext = CType(colControls.Item(iCounter + 1), Control).UniqueID
                        strPrevious = CType(colControls.Item(colControls.Count), Control).UniqueID
                    ElseIf iCounter = colControls.Count Then
                        strNext = CType(colControls.Item(1), Control).UniqueID
                        strPrevious = CType(colControls.Item(iCounter - 1), Control).UniqueID
                    Else
                        strNext = CType(colControls.Item(iCounter + 1), Control).UniqueID
                        strPrevious = CType(colControls.Item(iCounter - 1), Control).UniqueID
                    End If

                    colControls.Item(iCounter).Attributes.Add("onkeydown", "Tab(" + strNext + ", " + strPrevious + ", window.event, 'No');")
                Next

                CType(colControls(1), Control).Focus()
            End If
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

            Master.HeaderMessage = FormName & " - " & SessionManager.QueryMasterMode.Replace("Row", "")
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            Select Case SessionManager.QueryMasterMode
                Case "EditRow"
                    Master.IconImage = Request.ApplicationPath + "/images/data_preferences.gif"
                Case "ViewRow"
                    Master.IconImage = Request.ApplicationPath + "/images/data_information.gif"
                Case "DeleteRow"
                    Master.IconImage = Request.ApplicationPath + "/images/data_delete.gif"
                Case "AddRow"
                    Master.IconImage = Request.ApplicationPath + "/images/data_add.gif"
            End Select

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                Select Case SessionManager.QueryParameterMasterMode
                    Case "EditRow"
                        LoadSelectedRecord()
                        UnEnableControls()
                        txtParameterPrompt.Focus()
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableControls()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableControls()
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Parameter.');")
                    Case "AddRow"
                        lblQueryID.Text = SessionManager.SelectedValueQueryID
                        txtQueryParameter.Focus()
                        colControls.Add(txtQueryParameter, txtQueryParameter.ID)
                        colControls.Add(txtParameterPrompt, txtParameterPrompt.ID)
                        LoadEditModeJavaScripts()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("QueryMaster3"), False)
                End Select
            Else
                ValidatePage()
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

            If rblParameterType.SelectedItem Is Nothing Then
                Master.DisplayError("You must selecte a Parameter Type")
                Return
            End If

            Select Case SessionManager.QueryParameterMasterMode
                Case "EditRow"
                    blnSuccess = UpdateParameter()
                Case "DeleteRow"
                    blnSuccess = DeleteParameter()
                Case "AddRow"
                    blnSuccess = InsertParameter()
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.QueryParameterMasterMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("QueryMaster3"), False)
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.QueryParameterMasterMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("QueryMaster3"), False)
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.QueryParameterMasterMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("QueryMaster3"), False)
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub ValidatePage()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.QueryParameterMasterMode = "AddRow" Then
                colControls.Add(txtQueryParameter, txtQueryParameter.ID)
            End If
            colControls.Add(txtParameterPrompt, txtParameterPrompt.ID)

            If Not rblParameterType.SelectedItem Is Nothing Then
                Select Case rblParameterType.SelectedItem.Value
                    Case "DATE"
                        AddDateEntryControl()
                    Case "SITE"
                        AddSiteEntryControl()
                    Case "TEXT"
                        AddTextEntryControl()
                    Case "TEAM"
                        AddTeamEntryControl()
                    Case "MYTEAMS"
                        AddMyTeamsEntryControl()
                End Select

                LoadEditModeJavaScripts()
            End If
        End Sub
        Private Sub LoadSelectedRecord()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim objDT As DataTable = QueryParametersMaster.SelectQueryParameter(SessionManager.SelectedValueQueryID, SessionManager.SelectedValue1)

                If objDT.Rows.Count > 0 Then
                    Dim objDR As DataRow = objDT.Rows(0)
                    Dim objItem As ListItem

                    lblQueryID.Text = objDR("QueryID")
                    txtQueryParameter.Text = objDR("QueryParameter").ToString
                    txtParameterPrompt.Text = objDR("ParameterPrompt").ToString
                    objItem = rblParameterType.Items.FindByValue(objDR("ParameterType").ToString.ToUpper)

                    If Not IsNothing(objItem) Then
                        colControls.Add(txtParameterPrompt, txtParameterPrompt.ID)
                        objItem.Selected = True

                        Select Case objDR("ParameterType").ToString.Trim.ToUpper
                            Case "DATE"
                                AddDateEntryControl()

                                If objDR("ParameterDefaultValue").ToString.Trim.ToUpper = "NOW" Then
                                    Dim objCheck As CheckBox = Page.FindControl("ctl00$ContentPlaceHolder1$chkNow")
                                    If Not IsNothing(objCheck) Then
                                        objCheck.Checked = True
                                    End If
                                End If
                            Case "SITE"
                                AddSiteEntryControl()

                                If Convert.ToBoolean(objDR("ShowInputPrompt")) Then
                                    Dim objCheck As CheckBox = Page.FindControl("ctl00$ContentPlaceHolder1$chkShowPrompt")
                                    If Not IsNothing(objCheck) Then
                                        objCheck.Checked = True
                                    End If
                                End If
                            Case "TEAM"
                                AddTeamEntryControl()

                                If objDR("ParameterDefaultValue").ToString.Trim.Length > 0 Then
                                    If objDR("ParameterDefaultValue").ToString.Trim.ToUpper = "SELECTEDTEAM" Then
                                        Dim objCheck As CheckBox = Page.FindControl("ctl00$ContentPlaceHolder1$chkSelectedTeam")
                                        If Not IsNothing(objCheck) Then
                                            objCheck.Checked = True
                                        End If
                                    Else
                                        CType(Page.FindControl("txtTeam"), TextBox).Text = objDR("ParameterDefaultValue").ToString
                                    End If
                                End If
                            Case "MYTEAMS"
                                AddMyTeamsEntryControl()

                                If objDR("ParameterDefaultValue").ToString.Trim.Length > 0 Then
                                    If objDR("ParameterDefaultValue").ToString.Trim.ToUpper = "SELECTEDTEAM" Then
                                        Dim objCheck As CheckBox = Page.FindControl("ctl00$ContentPlaceHolder1$chkSelectedTeam")
                                        If Not IsNothing(objCheck) Then
                                            objCheck.Checked = True
                                        End If
                                    ElseIf objDR("ParameterDefaultValue").ToString.Trim.ToUpper = "MYTEAMS" Then
                                        Dim objCheck As CheckBox = Page.FindControl("ctl00$ContentPlaceHolder1$chkMyTeams")
                                        If Not IsNothing(objCheck) Then
                                            objCheck.Checked = True
                                        End If
                                    Else
                                        CType(Page.FindControl("txtTeam"), TextBox).Text = objDR("ParameterDefaultValue").ToString
                                    End If
                                End If
                            Case "TEXT"
                                AddTextEntryControl()

                                If objDR("ParameterDefaultValue").ToString.Trim.Length > 0 Then
                                    Dim objTextBox As TextBox = Page.FindControl("ctl00$ContentPlaceHolder1$txtText")
                                    If Not IsNothing(objTextBox) Then
                                        objTextBox.Text = objDR("ParameterDefaultValue")
                                    End If
                                End If
                        End Select

                        LoadEditModeJavaScripts()
                    Else
                        Master.DisplayError("Invalide Parameter Type")
                        Return
                    End If
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub UnEnableControls()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Select Case SessionManager.QueryParameterMasterMode
                Case "EditRow"
                    txtQueryParameter.CssClass = "Textbox_Display"
                    txtQueryParameter.ReadOnly = True
                    rblParameterType.Enabled = True
                    pnlExit.Visible = False
                Case "ViewRow"
                    txtQueryParameter.CssClass = "Textbox_Display"
                    txtQueryParameter.ReadOnly = True
                    txtParameterPrompt.CssClass = "Textbox_Display"
                    txtParameterPrompt.ReadOnly = True
                    rblParameterType.Enabled = False
                    pnlOKCancel.Visible = False
                Case "DeleteRow"
                    txtQueryParameter.CssClass = "Textbox_Display"
                    txtQueryParameter.ReadOnly = True
                    txtParameterPrompt.CssClass = "Textbox_Display"
                    txtParameterPrompt.ReadOnly = True
                    rblParameterType.Enabled = False
                    pnlExit.Visible = False
            End Select
        End Sub
        Private Sub AddSiteEntryControl()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim objRow As HtmlTableRow
                Dim objCell As HtmlTableCell

                objRow = New HtmlTableRow
                objCell = New HtmlTableCell
                objCell.InnerText = "Show Prompt:"
                objRow.Cells.Add(objCell)

                objCell = New HtmlTableCell

                Dim objCheck As New CheckBox
                objCheck.Text = ""
                objCheck.ID = "chkShowPrompt"
                objCheck.CssClass = ""
                objCell.Controls.Add(objCheck)

                objRow.Cells.Add(objCell)
                tblParameter.Rows.Add(objRow)

                colControls.Add(objCheck, objCheck.ID)

                Select Case SessionManager.QueryParameterMasterMode
                    Case "EditRow", "AddRow"
                        objCheck.Enabled = True
                    Case "ViewRow", "DeleteRow"
                        objCheck.Enabled = False
                End Select
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - AddSiteEntryControl", Exc, SessionManager.UserID, ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub AddTextEntryControl()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim objRow As HtmlTableRow
                Dim objCell As HtmlTableCell

                objRow = New HtmlTableRow
                objCell = New HtmlTableCell
                objCell.InnerText = "Default Text :"
                objRow.Cells.Add(objCell)

                objCell = New HtmlTableCell

                Dim objTextBox As New TextBox
                objTextBox.Text = ""
                objTextBox.ID = "txtText"
                objCell.Controls.Add(objTextBox)

                objRow.Cells.Add(objCell)
                tblParameter.Rows.Add(objRow)

                colControls.Add(objTextBox, objTextBox.ID)

                Select Case SessionManager.QueryParameterMasterMode
                    Case "EditRow", "AddRow"
                        objTextBox.ReadOnly = False
                        objTextBox.CssClass = "Textbox_Entry"
                    Case "ViewRow", "DeleteRow"
                        objTextBox.ReadOnly = True
                        objTextBox.CssClass = "Textbox_Display"
                End Select
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - AddTextEntryControl", Exc, SessionManager.UserID, ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub AddDateEntryControl()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim objRow As HtmlTableRow
                Dim objCell As HtmlTableCell

                objRow = New HtmlTableRow
                objCell = New HtmlTableCell
                objCell.InnerText = "Use Current Date as Default :"
                objRow.Cells.Add(objCell)

                objCell = New HtmlTableCell

                Dim objCheck As New CheckBox
                objCheck.Checked = False
                objCheck.Text = ""
                objCheck.ID = "chkNow"
                objCheck.CssClass = ""
                objCell.Controls.Add(objCheck)

                objRow.Cells.Add(objCell)
                tblParameter.Rows.Add(objRow)

                colControls.Add(objCheck, objCheck.ID)

                Select Case SessionManager.QueryParameterMasterMode
                    Case "EditRow", "AddRow"
                        objCheck.Enabled = True
                    Case "ViewRow", "DeleteRow"
                        objCheck.Enabled = False
                End Select
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - AddDateEntryControl", Exc, SessionManager.UserID, ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub AddTeamEntryControl()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim objRow As HtmlTableRow
            Dim objCell As HtmlTableCell

            objRow = New HtmlTableRow
            objCell = New HtmlTableCell
            objCell.InnerText = "Default Team :"
            objRow.Cells.Add(objCell)

            objCell = New HtmlTableCell

            Dim objTextBox As New TextBox
            objTextBox.Text = ""
            objTextBox.ID = "txtTeam"
            objCell.Controls.Add(objTextBox)

            Dim objLabel As New Label
            objLabel.Text = " or "
            objCell.Controls.Add(objLabel)

            Dim objCheckBox As New CheckBox
            objCheckBox.Text = "Use Selected Team"
            objCheckBox.ID = "chkSelectedTeam"
            objCell.Controls.Add(objCheckBox)

            objRow.Cells.Add(objCell)
            tblParameter.Rows.Add(objRow)

            colControls.Add(objTextBox, objTextBox.ID)
            colControls.Add(objCheckBox, objCheckBox.ID)

            Select Case SessionManager.QueryParameterMasterMode
                Case "EditRow", "AddRow"
                    objTextBox.ReadOnly = False
                    objTextBox.CssClass = "Textbox_Entry"
                    objCheckBox.Enabled = True
                Case "ViewRow", "DeleteRow"
                    objTextBox.ReadOnly = True
                    objTextBox.CssClass = "Textbox_Display"
                    objCheckBox.Enabled = False
            End Select
        End Sub
        Private Sub AddMyTeamsEntryControl()
            Dim objRow As HtmlTableRow
            Dim objCell As HtmlTableCell

            objRow = New HtmlTableRow
            objCell = New HtmlTableCell
            objCell.InnerText = "Default Team :"
            objRow.Cells.Add(objCell)

            objCell = New HtmlTableCell

            Dim objTextBox As New TextBox
            objTextBox.Text = ""
            objTextBox.ID = "txtTeam"
            objCell.Controls.Add(objTextBox)

            Dim objLabel As New Label
            objLabel.Text = " or "
            objCell.Controls.Add(objLabel)

            Dim objCheck As New CheckBox
            objCheck.ID = "chkSelectedTeam"
            objCheck.Text = "Use Selected Team"
            objCell.Controls.Add(objCheck)

            objLabel = New Label
            objLabel.Text = " or "
            objCell.Controls.Add(objLabel)

            Dim objCheck2 As New CheckBox
            objCheck2.ID = "chkMyTeams"
            objCheck2.Text = "Use All My Teams"
            objCell.Controls.Add(objCheck2)

            objRow.Cells.Add(objCell)
            tblParameter.Rows.Add(objRow)

            colControls.Add(objTextBox, objTextBox.ID)
            colControls.Add(objCheck, objCheck.ID)
            colControls.Add(objCheck2, objCheck2.ID)

            Select Case SessionManager.QueryParameterMasterMode
                Case "EditRow", "AddRow"
                    objTextBox.ReadOnly = False
                    objTextBox.CssClass = "Textbox_Entry"
                    objCheck.Enabled = True
                    objCheck2.Enabled = True
                Case "ViewRow", "DeleteRow"
                    objTextBox.ReadOnly = True
                    objTextBox.CssClass = "Textbox_Display"
                    objCheck.Enabled = False
                    objCheck2.Enabled = False
            End Select
        End Sub
        Private Function UpdateParameter() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If Page.IsValid Then
                Try
                    Dim lQueryID As Long = lblQueryID.Text
                    Dim strParameter As String = txtQueryParameter.Text
                    Dim strParameterPrompt As String = txtParameterPrompt.Text
                    Dim strParameterType As String = rblParameterType.SelectedItem.Value.ToUpper
                    Dim strDefaultValue As String = ""
                    Dim bShowInputPrompt As Boolean

                    If GetParameterValues(strParameterType, strDefaultValue, bShowInputPrompt) = True Then
                        If bShowInputPrompt = True AndAlso strParameterPrompt.Trim.Length = 0 Then
                            Master.DisplayError("Parameter Prompt is required")
                            Return False
                        End If
                        QueryParametersMaster.UpdateQueryParametersMaster(lQueryID, strParameter, strParameterPrompt, strParameterType, strDefaultValue, bShowInputPrompt)
                        Return True
                    Else
                        Return False
                    End If
                Catch Exc As Exception
                    Master.DisplayErrors(ProgramName & " - UpdateParameter", Exc, SessionManager.UserID, ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                    Return False
                End Try
            End If
        End Function
        Private Function InsertParameter() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If Page.IsValid Then
                Try
                    Dim lQueryID As Long = lblQueryID.Text
                    Dim strParameter As String = txtQueryParameter.Text
                    Dim strParameterPrompt As String = txtParameterPrompt.Text
                    Dim strParameterType As String = rblParameterType.SelectedItem.Value.ToUpper
                    Dim strDefaultValue As String = ""
                    Dim bShowInputPrompt As Boolean

                    If GetParameterValues(strParameterType, strDefaultValue, bShowInputPrompt) = True Then
                        If bShowInputPrompt = True And strParameterPrompt.Trim.Length = 0 Then
                            Master.DisplayError("Parameter Prompt is required")
                            Return False
                        End If
                        QueryParametersMaster.InsertQueryParametersMaster(lQueryID, strParameter, strParameterPrompt, strParameterType, strDefaultValue, bShowInputPrompt)
                        Return True
                    Else
                        Return False
                    End If
                Catch Exc As Exception
                    Master.DisplayErrors(ProgramName & " - InsertParameter", Exc, SessionManager.UserID, ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                    Return False
                End Try
            End If
        End Function
        Private Function DeleteParameter() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                QueryParametersMaster.DeleteQueryParametersMaster(lblQueryID.Text, txtQueryParameter.Text)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteParameter", Exc, SessionManager.UserID, ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
        End Function
        Private Function GetParameterValues(ByRef strParameterType As String, ByRef strDefaultValue As String, ByRef bShowInputPrompt As Boolean) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Select Case strParameterType
                    Case "DATE"
                        If CType(Page.FindControl("ctl00$ContentPlaceHolder1$chkNow"), CheckBox).Checked = True Then
                            strDefaultValue = "NOW"
                            bShowInputPrompt = True
                        End If
                    Case "SITE"
                        strDefaultValue = "WORKINGSITE"
                        If CType(Page.FindControl("ctl00$ContentPlaceHolder1$chkShowPrompt"), CheckBox).Checked = True Then
                            bShowInputPrompt = True
                        Else
                            bShowInputPrompt = False
                        End If
                    Case "TEAM"
                        Dim objTextBox As TextBox = CType(Page.FindControl("ctl00$ContentPlaceHolder1$txtTeam"), TextBox)

                        If CType(Page.FindControl("ctl00$ContentPlaceHolder1$chkSelectedTeam"), CheckBox).Checked = True Then
                            strDefaultValue = "SELECTEDTEAM"
                            bShowInputPrompt = False
                        Else
                            If objTextBox.Text.Trim.Length > 0 Then
                                strDefaultValue = objTextBox.Text.Trim
                            End If

                            bShowInputPrompt = True
                        End If

                        If strDefaultValue = "SELECTEDTEAM" And objTextBox.Text.Trim.Length > 0 Then
                            Master.DisplayError("You have selected too many Team Default options.  Please enter a Team or select 'Selected Team'")
                            Return False
                        End If
                    Case "MYTEAMS"
                        Dim objTextBox As TextBox = CType(Page.FindControl("ctl00$ContentPlaceHolder1$txtTeam"), TextBox)

                        If CType(Page.FindControl("ctl00$ContentPlaceHolder1$chkSelectedTeam"), CheckBox).Checked = True Then
                            strDefaultValue = "SELECTEDTEAM"
                        ElseIf CType(Page.FindControl("ctl00$ContentPlaceHolder1$chkMyTeams"), CheckBox).Checked = True Then
                            strDefaultValue = "MYTEAMS"
                        Else
                            If objTextBox.Text.Trim.Length > 0 Then
                                strDefaultValue = objTextBox.Text.Trim
                            End If
                        End If

                        If CType(Page.FindControl("ctl00$ContentPlaceHolder1$chkSelectedTeam"), CheckBox).Checked = True And CType(Page.FindControl("ctl00$ContentPlaceHolder1$chkMyTeams"), CheckBox).Checked = True Then
                            Master.DisplayError("Select 'Selected Team' or 'All My Teams'")
                            Return False
                        ElseIf (strDefaultValue = "MYTEAMS" Or strDefaultValue = "SELECTEDTEAM") And objTextBox.Text.Trim.Length > 0 Then
                            Master.DisplayError("You have selected too many Team Default options.  Please enter a Team or select one of the check boxes.")
                            Return False
                        End If

                        bShowInputPrompt = True




                    Case "TEXT"
                        Dim objTextBox As TextBox = CType(Page.FindControl("ctl00$ContentPlaceHolder1$txtText"), TextBox)
                        If objTextBox.Text.Trim.Length > 0 Then
                            strDefaultValue = objTextBox.Text.Trim
                        End If
                        bShowInputPrompt = True
                End Select
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - GetParameterValues", Exc, SessionManager.UserID, ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                Return False
            End Try
        End Function
#End Region

    End Class
End Namespace
