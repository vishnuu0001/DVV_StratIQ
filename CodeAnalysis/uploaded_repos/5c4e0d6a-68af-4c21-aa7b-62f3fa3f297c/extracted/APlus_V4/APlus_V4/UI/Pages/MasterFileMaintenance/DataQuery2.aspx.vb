#Region " Imports"
Imports System.IO
Imports System.Data
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.DataAccess.Custom
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class DataQuery2
        Inherits ApplicationBase

#Region " Constants and Local Variabls"
        Private Shared ReadOnly FormName As String = "Database Query"
        Private Shared ReadOnly ProgramName As String = "DataQuery2"
        Private colControls As New Collection
        Private strSQL As String = String.Empty
        Private dsParametersDataSet As DataTable
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnRunQuery, btnExit}
            Dim OverMessageArr() As String = {"Run Query - Enter", "Exit"}
            Dim OutMessageArr() As String = {"", ""}

            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnExit.UniqueID + "'),window.event)")
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
            ElseIf colControls.Count = 1 Then
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

            Master.HeaderMessage = FormName
            Master.IconImage = Request.ApplicationPath + "/images/data_scroll.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            If SessionManager.SelectedQuery <> "" Then
                lblQueryID.Text = SessionManager.SelectedQuery
                lblQuery.Text = SessionManager.SelectedQueryName
            End If

            LoadCommonJavaScripts()
            strSQL = BuildQueryString()
            If LoadParameters() Then
                If Not Page.IsPostBack Then
                    btnRunQuery_Click(Nothing, Nothing)
                End If
            End If
            LoadEditModeJavaScripts()
        End Sub
        Private Sub btnRunQuery_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnRunQuery.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            grdQueryResults.DataSource = Nothing
            grdQueryResults.DataBind()

            If strSQL.Length > 0 Then
                If GetParameterValues(strSQL) Then
                    BindQueryGrid()
                End If
            End If
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedQuery)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedQueryName)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("QueryMaster1"), False)
        End Sub
        Private Sub btnExport_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExport.Click
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
                If GetParameterValues(strSQL) Then
                    BindQueryGrid()
                End If
                Dim stringWrite As New System.IO.StringWriter
                Dim htmlWrite As New System.Web.UI.HtmlTextWriter(stringWrite)
                Dim dv As DataTable = CType(grdQueryResults.DataSource, DataTable)
                Dim dg As New DataGrid
                dg.HeaderStyle.HorizontalAlign = HorizontalAlign.Left
                dg.HeaderStyle.VerticalAlign = VerticalAlign.Top
                dg.HeaderStyle.Font.Bold = True
                dg.ItemStyle.VerticalAlign = VerticalAlign.Top
                dg.ItemStyle.HorizontalAlign = HorizontalAlign.Left
                If dv.Rows.Count < 1 Then Exit Sub

                dg.DataSource = dv
                dg.DataBind()
                dg.RenderControl(htmlWrite)

                SessionManager.ExportString = stringWrite.ToString
                HttpContext.Current.Response.Redirect(HttpContext.Current.Request.ApplicationPath.ToString & "/UI/UserControls/Export.aspx", False)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - btnExport_Click", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub TeamCheckChanged(ByVal sender As Object, ByVal e As System.EventArgs)
            Dim objCheck As CheckBox = CType(sender, CheckBox)
            Dim objDDL As DropDownList

            Select Case objCheck.ID
                Case "chkClosedTeams"
                    objDDL = CType(Page.FindControl(objCheck.ToolTip), DropDownList)
                    If Not IsNothing(objDDL) Then
                        objDDL.Items.Clear()

                        If objCheck.Checked = True Then
                            Teams.TeamSelectionList(objDDL, SessionManager.UserID, SessionManager.WorkingSiteID, True)
                            objDDL.Items.Insert(0, "")
                        Else
                            Teams.TeamSelectionList(objDDL, SessionManager.UserID, SessionManager.WorkingSiteID, False)
                            objDDL.Items.Insert(0, "")
                        End If
                    End If
                Case "chkClosedMyTeams"
                    objDDL = CType(Page.FindControl(objCheck.ToolTip), DropDownList)
                    If Not IsNothing(objDDL) Then
                        objDDL.Items.Clear()

                        If objCheck.Checked = True Then
                            Teams.SelectMyTeamList(objDDL, SessionManager.UserID, SessionManager.WorkingSiteID, True)
                        Else
                            Teams.SelectMyTeamList(objDDL, SessionManager.UserID, SessionManager.WorkingSiteID)
                        End If
                    End If
            End Select
        End Sub
#End Region

#Region " Custom Methods"
        Private Function GetParameterValues(ByRef passSQLString As String) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim strControlID As String = String.Empty

                For Each objDR As DataRow In dsParametersDataSet.Rows
                    Select Case objDR("ParameterType").ToString.Trim.ToUpper
                        Case "DATE"
                            strControlID = CType(colControls(objDR("QueryParameter").ToString), TextBox).UniqueID
                            Dim objTextBox As TextBox = Page.FindControl(strControlID)

                            If Not IsNothing(objTextBox) Then
                                If IsDate(objTextBox.Text) Then
                                    passSQLString = passSQLString.Replace("<<" & objDR("QueryParameter") & ">>", "'" & RegionalConversion.FormatSQLDate(objTextBox.Text) & "'")
                                Else
                                    Master.DisplayError("Invalid Date")
                                    objTextBox.Focus()

                                    Return False
                                End If
                            End If
                        Case "SITE", "TEAM"
                            If Convert.ToBoolean(objDR("ShowInputPrompt")) Then
                                strControlID = CType(colControls(objDR("QueryParameter").ToString), DropDownList).UniqueID
                                Dim objcontrol As DropDownList = Page.FindControl(strControlID)

                                If Not IsNothing(objcontrol) Then
                                    If objcontrol.SelectedItem.Text.Trim.Length > 0 Then
                                        passSQLString = passSQLString.Replace("<<" & objDR("QueryParameter") & ">>", "'" & objcontrol.SelectedItem.Value & "'")
                                    Else
                                        Master.DisplayError("Select a value for " & objDR("QueryParameter"))
                                        objcontrol.Focus()

                                        Return False
                                    End If
                                End If
                            End If
                        Case "MYTEAMS"
                            strControlID = CType(colControls(objDR("QueryParameter").ToString), DropDownList).UniqueID
                            Dim objcontrol As DropDownList = Page.FindControl(strControlID)

                            If Not IsNothing(objcontrol) Then
                                If objcontrol.SelectedItem.Value = "MYTEAMS" Then
                                    Dim strHolder As String = ""

                                    For Each objItem As ListItem In objcontrol.Items
                                        If objItem.Value <> "MYTEAMS" And objItem.Value <> "" Then
                                            If strHolder.Trim.Length > 0 Then
                                                strHolder += ", "
                                            End If

                                            strHolder += "'" & objItem.Value & "'"
                                        End If
                                    Next

                                    passSQLString = passSQLString.Replace("<<" & objDR("QueryParameter") & ">>", strHolder)
                                ElseIf objcontrol.SelectedItem.Value <> "" Then
                                    passSQLString = passSQLString.Replace("<<" & objDR("QueryParameter") & ">>", "'" & objcontrol.SelectedItem.Value & "'")
                                Else
                                    Master.DisplayError(GetTranslationString("selectvaluefor", "Select a value for ") & objDR("QueryParameter"))
                                    objcontrol.Focus()

                                    Return False
                                End If
                            End If
                        Case "TEXT"
                            strControlID = CType(colControls(objDR("QueryParameter").ToString), TextBox).UniqueID
                            Dim objTextBox As TextBox = Page.FindControl(strControlID)

                            If Not IsNothing(objTextBox) Then
                                If objTextBox.Text.Trim.Length > 0 Then
                                    passSQLString = passSQLString.Replace("<<" & objDR("QueryParameter") & ">>", objTextBox.Text)
                                Else
                                    Master.DisplayError("Enter value for " & objDR("QueryParameter"))
                                    objTextBox.Focus()

                                    Return False
                                End If
                            End If
                        Case Else
                            'no good!
                            Return False
                    End Select
                Next
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - GetParameterValues", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Function
        Private Function LoadParameters() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim bRunQuery As Boolean = True
            Try
                dsParametersDataSet = QueryParametersMaster.SelectQueryParametersMaster(lblQueryID.Text)

                If dsParametersDataSet.Rows.Count > 0 Then
                    For Each objDR As DataRow In dsParametersDataSet.Rows
                        If objDR("ParameterDefaultValue").ToString.Trim.Length > 0 Then
                            If objDR("ShowInputPrompt") = True Then
                                AddParameterControl(objDR("QueryParameter"), objDR("ParameterPrompt"), objDR("ParameterType"), objDR("ParameterDefaultValue").ToString)
                                bRunQuery = False
                            Else
                                ProcessQueryParameter(objDR("QueryParameter"), objDR("ParameterType"), objDR("ParameterDefaultValue").ToString)
                            End If
                        Else
                            AddParameterControl(objDR("QueryParameter"), objDR("ParameterPrompt"), objDR("ParameterType"), objDR("ParameterDefaultValue").ToString)
                            bRunQuery = False
                        End If
                    Next
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadParameters", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try

            Return bRunQuery
        End Function
        Private Function BuildQueryString() As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim strHolder As String = String.Empty

            Try
                Dim objDS As DataSet = QueryMaster.SelectQuery(lblQueryID.Text)

                If objDS.Tables.Count > 0 Then
                    If objDS.Tables(0).Rows.Count > 0 Then
                        Dim objDR As DataRow = objDS.Tables(0).Rows(0)
                        strHolder = "Select " + Replace(objDR("QuerySelect").ToString.Trim, """", """""")
                        strHolder += " From " + Replace(objDR("QueryFrom").ToString.Trim, """", """""")

                        If objDR("QueryWhere").ToString.Trim.Length > 0 Then
                            strHolder += " where " + Replace(objDR("QueryWhere").ToString.Trim, """", """""")
                        End If

                        If objDR("QueryGroupBy").ToString.Trim.Length > 0 Then
                            strHolder += " group by " + Replace(objDR("QueryGroupBy").ToString.Trim, """", """""")
                        End If

                        If objDR("QueryOrderBy").ToString.Trim.Length > 0 Then
                            strHolder += " order by " + Replace(objDR("QueryOrderBy").ToString.Trim, """", """""")
                        End If
                    End If
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BuildQueryString", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try

            Return strHolder
        End Function
        Private Function ProcessQueryParameter(ByVal passParam As String, ByVal passParamType As String, ByVal passDefault As String) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Select Case passParamType.ToUpper
                    Case "DATE"
                        If passDefault.Trim.ToUpper = "NOW" Then
                            strSQL = strSQL.Replace("<<" & passParam & ">>", "'" & Now.ToString(SessionManager.DateFormat) & "'")
                        End If
                    Case "SITE"
                        If passDefault.Trim.ToUpper = "WORKINGSITE" Then
                            strSQL = strSQL.Replace("<<" & passParam & ">>", SessionManager.WorkingSiteID)
                        End If
                    Case "TEXT"
                        If passDefault.Trim.Length > 0 Then
                            strSQL = strSQL.Replace("<<" & passParam & ">>", passDefault)
                        Else
                            Return False
                        End If
                    Case Else
                        Return False
                End Select
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - ProcessQueryParameter", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
            Return True
        End Function
        Private Sub AddParameterControl(ByVal passParam As String, ByVal passPrompt As String, ByVal passParamType As String, ByVal passDefault As String)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "", "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim objRow As TableRow
                Dim objCell As TableCell

                Select Case passParamType.ToUpper
                    Case "DATE"
                        objRow = New TableRow

                        objCell = New TableCell
                        objCell.Text = passPrompt
                        objCell.Width = New Unit(objCell.Text.Length * 6)
                        objRow.Cells.Add(objCell)

                        objCell = New TableCell

                        Dim objTextBox As New TextBox
                        objTextBox.ID = passParam
                        objTextBox.CssClass = "Textbox_Entry"
                        objTextBox.MaxLength = 12
                        objCell.Controls.Add(objTextBox)

                        Dim objDateButton As New ImageButton
                        objDateButton.ID = "img" & passParam
                        objDateButton.ImageUrl = "~/images/date-time_select.gif"
                        objDateButton.CausesValidation = False
                        objDateButton.ToolTip = "Click to Select Date..."
                        objCell.Controls.Add(objDateButton)

                        Dim strDateFormat As String = SessionManager.DateFormat

                        Dim objDJ As New AjaxControlToolkit.CalendarExtender
                        objDJ.ID = objTextBox.ID & "_CalendarExtender"
                        objDJ.EnabledOnClient = True
                        objDJ.Enabled = True
                        objDJ.CssClass = "APlus_Calendar"
                        objDJ.TargetControlID = objTextBox.ID
                        objDJ.PopupButtonID = objDateButton.ID
                        objDJ.Format = strDateFormat
                        objCell.Controls.Add(objDJ)

                        objRow.Cells.Add(objCell)
                        tblQuery.Rows.Add(objRow)

                        colControls.Add(objTextBox, objTextBox.ID)

                        If passDefault.Trim.Length > 0 Then
                            If passDefault.Trim.ToUpper = "NOW" Then
                                objTextBox.Text = Now.ToString(strDateFormat)
                            End If
                        End If
                    Case "SITE"
                        objRow = New TableRow

                        objCell = New TableCell
                        objCell.Text = passPrompt
                        objRow.Cells.Add(objCell)

                        objCell = New TableCell
                        Dim objControl As New DropDownList
                        objControl.ID = passParam
                        objControl.CssClass = "DropdownList_Entry"
                        SiteMaster.SelectSiteMasterList(objControl)
                        objControl.Items.Insert(0, "")
                        objCell.Controls.Add(objControl)
                        objRow.Cells.Add(objCell)

                        tblQuery.Rows.Add(objRow)

                        colControls.Add(objControl, objControl.ID)

                        If passDefault.Trim.Length > 0 Then
                            Dim objItem As ListItem

                            If passDefault.Trim.ToUpper = "WORKINGSITE" Then
                                objItem = objControl.Items.FindByValue(SessionManager.WorkingSiteID)
                            Else
                                objItem = objControl.Items.FindByValue(passDefault.Trim)
                            End If

                            If Not IsNothing(objItem) Then
                                objItem.Selected = True
                            End If
                        End If
                    Case "MYTEAMS"
                        objRow = New TableRow

                        objCell = New TableCell
                        objCell.Text = passPrompt
                        objRow.Cells.Add(objCell)

                        objCell = New TableCell
                        Dim objControl As New DropDownList
                        objControl.Width = New Unit(425)
                        objControl.ID = passParam
                        objControl.CssClass = "DropdownList_Entry"
                        objCell.Controls.Add(objControl)

                        Teams.SelectMyTeamList(objControl, SessionManager.UserID, SessionManager.WorkingSiteID)

                        Dim objCheckBox As New CheckBox
                        objCheckBox.Text = "Show Closed Teams"
                        objCheckBox.ToolTip = passParam
                        objCheckBox.ID = "chkClosedMyTeams"
                        objCheckBox.AutoPostBack = True
                        AddHandler objCheckBox.CheckedChanged, AddressOf TeamCheckChanged

                        objCell.Controls.Add(objCheckBox)

                        objRow.Cells.Add(objCell)

                        tblQuery.Rows.Add(objRow)

                        colControls.Add(objControl, objControl.ID)
                        colControls.Add(objCheckBox, objCheckBox.ID)

                        If passDefault.Trim.Length > 0 Then
                            Dim objItem As ListItem

                            If passDefault.Trim.ToUpper = "SELECTEDTEAM" Then
                                objItem = objControl.Items.FindByValue(SessionManager.SelectedTeamID)
                            ElseIf passDefault.Trim.ToUpper = "MYTEAMS" Then
                                objItem = objControl.Items.FindByValue("MYTEAMS")
                            Else
                                objItem = objControl.Items.FindByValue(passDefault.ToUpper)
                            End If

                            If Not IsNothing(objItem) Then
                                objItem.Selected = True
                            End If
                        End If
                    Case "TEAM"
                        objRow = New TableRow

                        objCell = New TableCell
                        objCell.Text = passPrompt
                        objRow.Cells.Add(objCell)

                        objCell = New TableCell
                        Dim objControl As New DropDownList
                        objControl.Width = New Unit(425)
                        objControl.ID = passParam
                        objControl.CssClass = "DropdownList_Entry"
                        objCell.Controls.Add(objControl)

                        Teams.TeamSelectionList(objControl, SessionManager.UserID, SessionManager.WorkingSiteID, True)
                        objControl.Items.Insert(0, "")

                        Dim objCheckBox As New CheckBox
                        objCheckBox.Text = "Show Closed Teams"
                        objCheckBox.ID = "chkClosedTeams"
                        objCheckBox.ToolTip = passParam
                        objCheckBox.AutoPostBack = True
                        AddHandler objCheckBox.CheckedChanged, AddressOf TeamCheckChanged
                        objCell.Controls.Add(objCheckBox)

                        objRow.Cells.Add(objCell)

                        tblQuery.Rows.Add(objRow)

                        colControls.Add(objControl, objControl.ID)
                        colControls.Add(objCheckBox, objCheckBox.ID)

                        If passDefault.Trim.Length > 0 Then
                            Dim objItem As ListItem

                            If passDefault.Trim.ToUpper = "SELECTEDTEAM" Then
                                objItem = objControl.Items.FindByValue(SessionManager.SelectedTeamID)
                            Else
                                objItem = objControl.Items.FindByValue(passDefault.ToUpper)
                            End If

                            If Not IsNothing(objItem) Then
                                objItem.Selected = True
                            End If
                        End If
                    Case "TEXT"
                        objRow = New TableRow

                        objCell = New TableCell
                        objCell.Text = passPrompt
                        objRow.Cells.Add(objCell)

                        objCell = New TableCell

                        Dim objTextBox As New TextBox
                        objTextBox.ID = passParam
                        objTextBox.CssClass = "Textbox_Entry"
                        objTextBox.MaxLength = 50
                        objCell.Controls.Add(objTextBox)

                        objRow.Cells.Add(objCell)
                        tblQuery.Rows.Add(objRow)

                        colControls.Add(objTextBox, objTextBox.ID)

                        If passDefault.Trim.Length > 0 Then
                            objTextBox.Text = passDefault
                        End If
                    Case "PASSWORD"
                        objRow = New TableRow

                        objCell = New TableCell
                        objCell.Text = passPrompt
                        objRow.Cells.Add(objCell)

                        objCell = New TableCell

                        Dim objTextBox As New TextBox
                        objTextBox.ID = passParam
                        objTextBox.CssClass = "Textbox_Entry"
                        objTextBox.MaxLength = 25
                        objTextBox.TextMode = TextBoxMode.Password
                        objCell.Controls.Add(objTextBox)

                        objRow.Cells.Add(objCell)
                        tblQuery.Rows.Add(objRow)

                        colControls.Add(objTextBox, objTextBox.ID)

                        If passDefault.Trim.Length > 0 Then
                            objTextBox.Text = passDefault
                        End If
                    Case Else
                        'no good!
                End Select
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - AddParameterControl", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindQueryGrid()
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
                Dim dsHolder As DataTable = GeneralDataAccess.DatabaseQuery(strSQL)
                If Not IsNothing(dsHolder) Then
                    grdQueryResults.DataSource = dsHolder
                    grdQueryResults.DataBind()
                End If
                btnExport.Visible = True
            Catch Exc As Exception
                btnExport.Visible = False
                Master.DisplayError(Exc.Message)
            End Try
        End Sub
#End Region

    End Class
End Namespace
