#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports System.Threading
Imports WebApp.APlus.DataAccess.Connections
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class SavingsTracker1
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Savings Tracker"
        Private Shared ReadOnly ProgramName As String = "SavingsTracker1"
        Private colControls As Collection
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
        Private Sub LoadEditModeJavaScripts()
            Dim objTextBox As TextBox
            Dim iCounter As Integer
            Dim strNext As String
            Dim strPrevious As String

            Try
                If colControls.Count > 1 Then
                    For iCounter = 1 To colControls.Count
                        objTextBox = colControls.Item(iCounter)
                        If iCounter = 1 Then
                            strNext = CType(colControls.Item(iCounter + 1), TextBox).UniqueID
                            strPrevious = CType(colControls.Item(colControls.Count), TextBox).UniqueID
                        ElseIf iCounter = colControls.Count Then
                            strNext = CType(colControls.Item(1), TextBox).UniqueID
                            strPrevious = CType(colControls.Item(iCounter - 1), TextBox).UniqueID
                        Else
                            strNext = CType(colControls.Item(iCounter + 1), TextBox).UniqueID
                            strPrevious = CType(colControls.Item(iCounter - 1), TextBox).UniqueID
                        End If
                        If Not objTextBox.ID.Contains("Historic") AndAlso Not objTextBox.ID.Contains("Target") Then
                            objTextBox.Attributes.Add("onkeydown", "javascript:Tab(document.all." + strNext + ", document.all." + strPrevious + ", window.event, 'Neg');")
                        Else
                            objTextBox.Attributes.Add("onkeydown", "javascript:Tab(document.all." + strNext + ", document.all." + strPrevious + ", window.event, 'Yes');")
                        End If
                    Next
                ElseIf colControls.Count = 1 Then
                    objTextBox = colControls.Item(1)
                    objTextBox.Attributes.Add("onkeydown", "javascript:Tab(document.all." + objTextBox.UniqueID + ", document.all." + objTextBox.UniqueID + ", window.event, 'Yes');")
                End If
            Catch ex As Exception
                EventTracker.AddNoEmail("SavingsTracker1:LoadEditModeJavaScripts", ex.Message, SessionManager.UserID)
            End Try
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
                btnOK.Text = GetTranslationString("ok", btnOK.Text)
                btnCancel.Text = GetTranslationString("cancel", btnCancel.Text)
                btnExit.Text = GetTranslationString("exit", btnExit.Text)
                btnCancelConfirm.Text = GetTranslationString("cancel", btnCancelConfirm.Text)
                btnExisting.Text = GetTranslationString("existingformula", btnExisting.Text)
                btnCurrent.Text = GetTranslationString("currentformula", btnCurrent.Text)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadCultureTranslations", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, ProgramName, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Master.IconImage = Request.ApplicationPath & "/images/TeamAction.gif"
            Master.HeaderMessage = GetTranslationString(FormName, FormName)
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/" & SessionManager.CulturePref & "/DataEntry.js")

            LoadCommonJavaScripts()
            LoadCultureTranslations()

            If SessionManager.TrackerSelNavYear = 0 Then
                SessionManager.TrackerSelNavYear = Now.Year
                SessionManager.TrackerSelEditMonth = 0
            End If

            If SessionManager.TrackerSelEditMonth = 0 Then
                pnlOKCancel.Visible = False
                pnlExit.Visible = True
                Master.EnableTeamLink = True
            Else
                pnlOKCancel.Visible = True
                pnlExit.Visible = False
            End If

            If SessionManager.SavingsTrackerMode.Trim.Length = 0 Then
                If SessionManager.SelectedTeamID > 0 Then
                    If SessionManager.SelectedTeamAllowEdit Then
                        SessionManager.SavingsTrackerMode = "EditRow"
                    End If
                Else
                    If Trackers.SelectTrackerEditMode(SessionManager.SelectedValueTrackerID, SessionManager.UserID) Then
                        SessionManager.SavingsTrackerMode = "EditRow"
                    Else
                        SessionManager.SavingsTrackerMode = "ViewRow"
                    End If
                End If
            End If

            MasterControl1.StoredProcedureParams.Add("@TrackerID", SessionManager.SelectedValueTrackerID)
            Dim strLanguage As String = New System.Globalization.CultureInfo(SessionManager.CulturePref).TwoLetterISOLanguageName.ToUpper
            If strLanguage = "EN" Then
                MasterControl1.GridColumns(1).DataField = "TrackerOther"
            Else
                MasterControl1.GridColumns(1).DataField = "Tracker"
            End If

            mcTotals.StoredProcedureParams.Add("@TrackerID", SessionManager.SelectedValueTrackerID)

            mcVariables.StoredProcedureParams.Add("@TrackerID", SessionManager.SelectedValueTrackerID)
            mcVariables.GridColumns(4).DataFormatString = "{0:" + SessionManager.DateFormat + "}"

            BindGrid()

            LoadEditModeJavaScripts()
        End Sub
        Private Sub Button_Click(ByVal sender As System.Object, ByVal e As WebControls.CommandEventArgs)
            Dim strTarget() As String
            strTarget = (CType(sender, LinkButton).ID).ToString.Split("~")
            Dim strProgram As String = ""

            Select Case strTarget(0)
                Case "Edit"
                    SessionManager.TrackerSelEditMode = "Month"
                    SessionManager.TrackerSelEditMonth = strTarget(1)
                Case "Nav"
                    SessionManager.TrackerSelNavYear = strTarget(1)
                    SessionManager.TrackerSelEditMode = ""
                    SessionManager.TrackerSelEditMonth = 0
                Case "Value"
                    SessionManager.TrackerSelEditMode = "Value"
                    SessionManager.TrackerSelEditMonth = 0
                Case "Target"
                    SessionManager.TrackerSelEditMode = "Target"
                    SessionManager.TrackerSelEditMonth = 0
                Case "Historic"
                    SessionManager.TrackerSelEditMode = "Historic"
                    SessionManager.TrackerSelEditMonth = 0
                Case "TargetSavings"
                    SessionManager.TrackerSelEditMode = "TargetSavings"
                    SessionManager.TrackerSelEditMonth = 0
            End Select

            If SessionManager.TrackerSelEditMode = "" Then
                TransactionHistory1.Visible = True

                pnlOKCancel.Visible = False
                pnlExit.Visible = True
                Master.EnableTeamLink = True
            Else
                TransactionHistory1.Visible = False

                pnlOKCancel.Visible = True
                pnlExit.Visible = False
                Master.EnableTeamLink = False
            End If

            BindGrid()
            LoadEditModeJavaScripts()

            If Not colControls Is Nothing AndAlso colControls.Count > 0 Then
                CType(colControls(1), Control).Focus()
            End If
        End Sub
        Private Sub btnOK_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnOK.Click
            If Not SaveSavingsTracker(0) Then
                pnlOKCancel.Visible = False
                pnlConfirm.Visible = True

                Return
            Else
                SessionManager.TrackerSelEditMode = ""
                SessionManager.TrackerSelEditMonth = 0
                pnlOKCancel.Visible = False
                pnlConfirm.Visible = False
                pnlExit.Visible = True
                Master.EnableTeamLink = True

                TransactionHistory1.CollapseAll()
                TransactionHistory1.Visible = True

                BindGrid()
            End If
        End Sub
        Private Sub btnCancel_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnCancel.Click, btnCancelConfirm.Click
            SessionManager.TrackerSelEditMode = ""
            SessionManager.TrackerSelEditMonth = 0
            pnlOKCancel.Visible = False
            pnlConfirm.Visible = False
            pnlExit.Visible = True
            Master.EnableTeamLink = True

            TransactionHistory1.CollapseAll()
            TransactionHistory1.Visible = True

            BindGrid()
        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click
            'SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TrackerSelNavYear)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TrackerSelEditMode)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TrackerSelEditMonth)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SavingsTrackerMode)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueTrackerID)

            Dim strProgram = "MyTrackers"
            If SessionManager.CallingProgram.Trim.Length > 0 Then
                strProgram = SessionManager.CallingProgram
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CallingProgram)
            End If
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strProgram), False)
        End Sub
        Protected Sub btnExisting_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnExisting.Click
            If Not SaveSavingsTracker(2) Then
                pnlOKCancel.Visible = False
                pnlConfirm.Visible = True

                Return
            Else
                SessionManager.TrackerSelEditMode = ""
                SessionManager.TrackerSelEditMonth = 0
                pnlOKCancel.Visible = False
                pnlConfirm.Visible = False
                pnlExit.Visible = True
                Master.EnableTeamLink = True

                TransactionHistory1.CollapseAll()
                TransactionHistory1.Visible = True

                BindGrid()
            End If
        End Sub
        Protected Sub btnCurrent_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnCurrent.Click
            If Not SaveSavingsTracker(1) Then
                pnlOKCancel.Visible = False
                pnlConfirm.Visible = True

                Return
            Else
                SessionManager.TrackerSelEditMode = ""
                SessionManager.TrackerSelEditMonth = 0
                pnlOKCancel.Visible = False
                pnlConfirm.Visible = False
                pnlExit.Visible = True
                Master.EnableTeamLink = True

                TransactionHistory1.CollapseAll()
                TransactionHistory1.Visible = True

                BindGrid()
            End If
        End Sub
        Protected Sub mcVariables_FunctionButtonOneClick(ByVal sender As Object, ByVal e As System.EventArgs) Handles mcVariables.FunctionButtonOneClick
            SessionManager.MasterControlExitProgram = "SavingsTracker1"
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TrackerVariables1"), False)
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub BindGrid()
            'determine if VIEW or EDIT mode
            Dim blnVIEWMode As Boolean = True
            If SessionManager.SavingsTrackerMode = "EditRow" Then
                blnVIEWMode = False
            End If

            TransactionHistory1.TableName = "Trackers"
            TransactionHistory1.RecordID = SessionManager.SelectedValueTrackerID.ToString

            tblSavingsTracker.Rows.Clear()

            MasterControl1.DataBind(True)
            If mcTotals.StoredProcedureParams.ContainsKey("@Year") Then
                mcTotals.StoredProcedureParams.Remove("@Year")
            End If
            mcTotals.StoredProcedureParams.Add("@Year", SessionManager.TrackerSelNavYear)
            mcTotals.DataBind(True)
            If Not SessionManager.SelectedTeamAllowEdit OrElse (SessionManager.TrackerSelEditMode.Trim.Length > 0 AndAlso Not blnVIEWMode) Then
                mcVariables.ShowFunctionButtonOne = False
            Else
                mcVariables.ShowFunctionButtonOne = True
            End If
            mcVariables.DataBind(True)

            Dim dStartDate As DateTime = Nothing
            Dim dEndDate As DateTime = Nothing
            Dim dEvalDate As DateTime = Nothing
            Dim objDT As DataTable = Trackers.SelectTracker(SessionManager.SelectedValueTrackerID)
            If objDT Is Nothing OrElse objDT.Rows.Count <> 1 Then
                Return
            End If
            dStartDate = objDT.Rows(0)("BeginPeriod")
            dEndDate = objDT.Rows(0)("EndPeriod")

            Dim cnMasterConnection As SqlConnection = ApplicationConnection.OpenMasterConnection()
            objDT = SavingsTracker.SelectSavingsTrackerValuesList(SessionManager.SelectedValueTrackerID, SessionManager.TrackerSelNavYear, cnMasterConnection)

            Dim objRow As TableRow
            Dim objCell As TableCell
            Dim objTextBox As TextBox
            Dim lnkValue As LinkButton = Nothing
            Dim lnkHistoric As LinkButton = Nothing
            Dim lnkTarget As LinkButton = Nothing
            Dim lnkOther As LinkButton = Nothing

            colControls = New Collection

            'add top for year and nav buttons
            objRow = New TableRow
            If SessionManager.TrackerSelEditMode.Trim.Length > 0 AndAlso Not blnVIEWMode Then
                objRow.Cells.Add(GenerateTableCell("", New Unit((100 / 15).ToString & "%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.None, ""))
                objRow.Cells.Add(GenerateTableCell(SessionManager.TrackerSelNavYear.ToString, New Unit((0).ToString & "%"), New Unit(0), "#41519A", "#ffffff", HorizontalAlign.Center, VerticalAlign.NotSet, 11, BorderStyle.None, ""))
                objRow.Cells.Add(GenerateTableCell("", New Unit((100 / 15).ToString & "%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.None, ""))
            Else
                objRow.Cells.Add(GenerateTableCell("", New Unit((100 / 15).ToString & "%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.None, "", GenerateTableLink("<", "#E7E7FF", "Nav~" & (SessionManager.TrackerSelNavYear - 1).ToString, "Previous Year")))
                objRow.Cells.Add(GenerateTableCell(SessionManager.TrackerSelNavYear.ToString, New Unit((0).ToString & "%"), New Unit(0), "#41519A", "#ffffff", HorizontalAlign.Center, VerticalAlign.NotSet, 11, BorderStyle.None, ""))
                objRow.Cells.Add(GenerateTableCell("", New Unit((100 / 15).ToString & "%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.None, "", GenerateTableLink(">", "#E7E7FF", "Nav~" & (SessionManager.TrackerSelNavYear + 1).ToString, "Next Year")))
            End If
            tblSavingsTracker.Rows.Add(objRow)

            'add Month columns
            'add header columns
            objRow = New TableRow
            objRow.Cells.Add(GenerateTableCell("", New Unit("16%"), New Unit(15), "#FFFFFF", "#FFFFFF", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.Solid, ""))

            For i As Integer = 4 To 15
                If SessionManager.TrackerSelEditMode.Trim.Length > 0 OrElse blnVIEWMode Then
                    objCell = GenerateTableCell(objDT.Columns(i).ColumnName, New Unit("7%"), New Unit(15), "#FFFFFF", "#000000", HorizontalAlign.Center, VerticalAlign.Top, 1, BorderStyle.Solid, "")
                Else
                    objCell = GenerateTableCell("", New Unit("7%"), New Unit(15), "#FFFFFF", "#000000", HorizontalAlign.Center, VerticalAlign.Top, 1, BorderStyle.Solid, "", GenerateTableLink(objDT.Columns(i).ColumnName, "#3333FF", "Edit~" & (i - 3).ToString, ""))
                End If

                dEvalDate = Convert.ToDateTime(SessionManager.TrackerSelNavYear.ToString & "/" & (i - 3).ToString & "/01")
                If dEvalDate = dStartDate OrElse dEvalDate = dEndDate _
                OrElse (dEvalDate > dStartDate AndAlso dEvalDate < dEndDate) Then
                    objCell.BackColor = Drawing.Color.LightGreen
                End If

                objRow.Cells.Add(objCell)
            Next

            tblSavingsTracker.Rows.Add(objRow)

            Dim intRowIndex As Int16 = 0
            Dim strAlternatingRowColor As String
            Dim blnEditMode As Boolean = False
            Dim objRegValid As RegularExpressionValidator
            Dim bFormulaDif As Boolean = False
            Dim bAllNull As Boolean = True

            For Each dtRow As DataRow In objDT.Rows
                intRowIndex += 1
                'values for this year
                objRow = New TableRow

                'alternating row color code
                If intRowIndex Mod 2 = 0 Then
                    strAlternatingRowColor = "#CCCCCC"
                Else
                    strAlternatingRowColor = "#FFFFFF"
                End If

                Select Case dtRow("ValueType").ToString.Trim.ToUpper
                    Case "VALUE"
                        If SessionManager.TrackerSelEditMode = "" AndAlso Not blnVIEWMode Then
                            lnkValue = GenerateTableLink("Value - " & dtRow("TrackerValueUOM").ToString(), "#3333FF", "Value", "Value")
                            objRow.Cells.Add(GenerateTableCell("Value - " & dtRow("TrackerValueUOM").ToString(), New Unit("16%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, "", lnkValue))
                        Else
                            objRow.Cells.Add(GenerateTableCell("Value - " & dtRow("TrackerValueUOM").ToString(), New Unit("16%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, dtRow("TrackerValueUOM").ToString()))
                        End If
                    Case "HISTORIC"
                        If SessionManager.TrackerSelEditMode = "" AndAlso Not blnVIEWMode Then
                            lnkHistoric = GenerateTableLink("Historic", "#3333FF", dtRow("ValueType").ToString(), "")
                            objRow.Cells.Add(GenerateTableCell(dtRow("ValueType").ToString(), New Unit("16%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.Middle, 1, BorderStyle.Solid, "", lnkHistoric))
                        Else
                            objRow.Cells.Add(GenerateTableCell("Historic", New Unit("16%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.Middle, 1, BorderStyle.Solid, dtRow("ValueType").ToString()))
                        End If
                    Case "TARGET"
                        If SessionManager.TrackerSelEditMode = "" AndAlso Not blnVIEWMode Then
                            lnkTarget = GenerateTableLink(dtRow("ValueType").ToString(), "#3333FF", dtRow("ValueType").ToString(), "")
                            objRow.Cells.Add(GenerateTableCell(dtRow("ValueType").ToString(), New Unit("16%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.Middle, 1, BorderStyle.Solid, "", lnkTarget))
                        Else
                            objRow.Cells.Add(GenerateTableCell(dtRow("ValueType").ToString(), New Unit("16%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.Middle, 1, BorderStyle.Solid, dtRow("ValueType").ToString()))
                        End If
                    Case "TARGETSAVINGS"
                        If SessionManager.TrackerSelEditMode = "" AndAlso Not blnVIEWMode Then
                            lnkOther = GenerateTableLink("Target Savings", "#3333FF", dtRow("ValueType").ToString(), "")
                            objRow.Cells.Add(GenerateTableCell(dtRow("ValueType").ToString(), New Unit("16%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.Middle, 1, BorderStyle.Solid, "", lnkOther))
                        Else
                            objRow.Cells.Add(GenerateTableCell("Target Savings", New Unit("16%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.Middle, 1, BorderStyle.Solid, dtRow("ValueType").ToString()))
                        End If
                End Select

                ' Values
                For i As Integer = 4 To 15
                    objCell = New TableCell
                    objCell.Width = New Unit("7%")
                    objCell.Height = New Unit(15)
                    objCell.HorizontalAlign = HorizontalAlign.Center
                    If intRowIndex Mod 2 = 0 Then
                        objCell.BackColor = System.Drawing.ColorTranslator.FromHtml("#CCCCCC")
                    Else
                        objCell.BackColor = System.Drawing.ColorTranslator.FromHtml("#FFFFFF")
                    End If

                    'if edit year = this row year and this is the 'Value' row
                    Select Case dtRow("ValueType").ToString.Trim.ToUpper
                        Case "VALUE"
                            If SessionManager.TrackerSelEditMode = "Month" AndAlso SessionManager.TrackerSelEditMonth = (i - 3) AndAlso Not blnVIEWMode Then
                                blnEditMode = True
                                objCell.HorizontalAlign = HorizontalAlign.Center
                                objCell.BorderStyle = BorderStyle.Solid
                                objTextBox = New TextBox
                                objTextBox.CssClass = "Textbox_Entry_Center"
                                objTextBox.Width = New Unit("85%")
                                objTextBox.Height = New Unit("85%")
                                objTextBox.ID = "txt" & objDT.Columns(i).ColumnName & "Value"
                                objTextBox.MaxLength = 12
                                objTextBox.BorderStyle = BorderStyle.Solid
                                objTextBox.BorderWidth = New Unit(1)
                                objTextBox.Attributes.Add("onFocus", "document.all.ctl00_ContentPlaceHolder1_" & objTextBox.ClientID & ".select();")
                                If dtRow(i) Is DBNull.Value OrElse Not IsNumeric(dtRow(i)) Then
                                    objTextBox.Text = ""
                                Else
                                    objTextBox.Text = CDbl(dtRow(i)).ToString("0.####")
                                End If

                                colControls.Add(objTextBox, objTextBox.ID)

                                objRegValid = New RegularExpressionValidator
                                objRegValid.ID = "Reg" & objTextBox.ID
                                objRegValid.ControlToValidate = objTextBox.ID
                                objRegValid.Display = ValidatorDisplay.None
                                objRegValid.ValidationExpression = "(-?\d{0,7}\" & Thread.CurrentThread.CurrentCulture.NumberFormat.NumberDecimalSeparator & "{1}\d{0,4})|(-?\d{0,10})"
                                objRegValid.ErrorMessage = "Invalid Tracker Value"
                                objCell.Controls.Add(objRegValid)

                                objCell.Controls.Add(objTextBox)
                            ElseIf SessionManager.TrackerSelEditMode = "Value" Then
                                blnEditMode = True
                                objCell.HorizontalAlign = HorizontalAlign.Center
                                objCell.BorderStyle = BorderStyle.Solid
                                objTextBox = New TextBox
                                objTextBox.CssClass = "Textbox_Entry_Center"
                                objTextBox.Width = New Unit("90%")
                                objTextBox.Height = New Unit("90%")
                                objTextBox.ID = "txt" & objDT.Columns(i).ColumnName
                                objTextBox.MaxLength = 12
                                objTextBox.BorderStyle = BorderStyle.Solid
                                objTextBox.BorderWidth = New Unit(1)
                                objTextBox.Attributes.Add("onFocus", "document.all.ctl00_ContentPlaceHolder1_" & objTextBox.ClientID & ".select();")
                                If dtRow(i) Is DBNull.Value OrElse Not IsNumeric(dtRow(i)) Then
                                    objTextBox.Text = ""
                                Else
                                    objTextBox.Text = CDbl(dtRow(i)).ToString("0.####")
                                End If

                                colControls.Add(objTextBox, objTextBox.ID)

                                objRegValid = New RegularExpressionValidator
                                objRegValid.ID = "Reg" & objTextBox.ID
                                objRegValid.ControlToValidate = objTextBox.ID
                                objRegValid.Display = ValidatorDisplay.None
                                objRegValid.ValidationExpression = "(-?\d{0,7}\" & Thread.CurrentThread.CurrentCulture.NumberFormat.NumberDecimalSeparator & "{1}\d{0,4})|(-?\d{0,10})"
                                objRegValid.ErrorMessage = "Invalid Tracker Value"
                                objCell.Controls.Add(objRegValid)

                                objCell.Controls.Add(objTextBox)
                            Else
                                objCell.BorderStyle = BorderStyle.Solid
                                If Not dtRow(i) Is DBNull.Value AndAlso IsNumeric(dtRow(i)) Then
                                    objCell.Text = CDbl(dtRow(i)).ToString("0.####")
                                End If
                                'objCell.ID = "td" & objDT.Columns(i).ColumnName
                            End If
                        Case Else
                            If SessionManager.TrackerSelEditMode = "Month" AndAlso SessionManager.TrackerSelEditMonth = (i - 3) AndAlso Not blnVIEWMode Then
                                blnEditMode = True
                                objCell.HorizontalAlign = HorizontalAlign.Center
                                objCell.BorderStyle = BorderStyle.Solid
                                objTextBox = New TextBox
                                objTextBox.CssClass = "Textbox_Entry_Center"
                                objTextBox.Width = New Unit("85%")
                                objTextBox.Height = New Unit("85%")
                                objTextBox.ID = "txt" & objDT.Columns(i).ColumnName & dtRow("ValueType").ToString
                                objTextBox.MaxLength = 12
                                objTextBox.BorderStyle = BorderStyle.Solid
                                objTextBox.BorderWidth = New Unit(1)
                                objTextBox.Attributes.Add("onFocus", "document.all.ctl00_ContentPlaceHolder1_" & objTextBox.ClientID & ".select();")
                                If dtRow(i) Is DBNull.Value OrElse Not IsNumeric(dtRow(i)) Then
                                    If MasterControl1.MasterControlGrid.Rows.Count = 1 AndAlso IsNumeric(MasterControl1.MasterControlGrid.DataKeys(0)(dtRow("ValueType").ToString)) Then
                                        objTextBox.Text = Convert.ToDouble(MasterControl1.MasterControlGrid.DataKeys(0)(dtRow("ValueType").ToString)).ToString("0.####")
                                    Else
                                        objTextBox.Text = ""
                                    End If
                                Else
                                    objTextBox.Text = Convert.ToDouble(dtRow(i)).ToString("0.####")
                                End If

                                colControls.Add(objTextBox, objTextBox.ID)

                                objRegValid = New RegularExpressionValidator
                                objRegValid.ID = "Reg" & objTextBox.ID
                                objRegValid.ControlToValidate = objTextBox.ID
                                objRegValid.Display = ValidatorDisplay.None
                                objRegValid.ValidationExpression = "(-?\d{0,7}\" & Thread.CurrentThread.CurrentCulture.NumberFormat.NumberDecimalSeparator & "{1}\d{0,4})|(-?\d{0,10})"
                                objRegValid.ErrorMessage = "Invalid " & dtRow("ValueType").ToString & " Value"
                                objCell.Controls.Add(objRegValid)

                                objCell.Controls.Add(objTextBox)
                            ElseIf SessionManager.TrackerSelEditMode.Trim.ToUpper = dtRow("ValueType").ToString.Trim.ToUpper Then
                                blnEditMode = True
                                objCell.HorizontalAlign = HorizontalAlign.Center
                                objCell.BorderStyle = BorderStyle.Solid
                                objTextBox = New TextBox
                                objTextBox.CssClass = "Textbox_Entry_Center"
                                objTextBox.Width = New Unit("90%")
                                objTextBox.Height = New Unit("90%")
                                objTextBox.ID = "txt" & objDT.Columns(i).ColumnName
                                objTextBox.MaxLength = 12
                                objTextBox.BorderStyle = BorderStyle.Solid
                                objTextBox.BorderWidth = New Unit(1)
                                objTextBox.Attributes.Add("onFocus", "document.all.ctl00_ContentPlaceHolder1_" & objTextBox.ClientID & ".select();")
                                If dtRow(i) Is DBNull.Value OrElse Not IsNumeric(dtRow(i)) Then
                                    objTextBox.Text = ""
                                Else
                                    bAllNull = False
                                    objTextBox.Text = CDbl(dtRow(i)).ToString("0.####")
                                End If

                                colControls.Add(objTextBox, objTextBox.ID)

                                objRegValid = New RegularExpressionValidator
                                objRegValid.ID = "Reg" & objTextBox.ID
                                objRegValid.ControlToValidate = objTextBox.ID
                                objRegValid.Display = ValidatorDisplay.None
                                objRegValid.ValidationExpression = "(-?\d{0,7}\" & Thread.CurrentThread.CurrentCulture.NumberFormat.NumberDecimalSeparator & "{1}\d{0,4})|(-?\d{0,10})"
                                objRegValid.ErrorMessage = "Invalid Tracker Value"
                                objCell.Controls.Add(objRegValid)

                                objCell.Controls.Add(objTextBox)
                            Else
                                objCell.BorderStyle = BorderStyle.Solid
                                If Not dtRow(i) Is DBNull.Value AndAlso IsNumeric(dtRow(i)) Then
                                    objCell.Text = CDbl(dtRow(i)).ToString("0.####")
                                End If
                            End If
                    End Select

                    objRow.Cells.Add(objCell)
                Next

                tblSavingsTracker.Rows.Add(objRow)
            Next

            objRow = New TableRow
            objRow.Cells.Add(GenerateTableCell("", New Unit("100%"), New Unit(5), "#FFFFFF", "#FFFFFF", HorizontalAlign.Center, VerticalAlign.NotSet, 13, BorderStyle.None, ""))
            tblSavingsTracker.Rows.Add(objRow)

            If bAllNull AndAlso SessionManager.TrackerSelEditMode.Trim.Length > 0 AndAlso SessionManager.TrackerSelEditMode <> "Month" AndAlso SessionManager.TrackerSelEditMode <> "Value" _
            AndAlso SessionManager.TrackerSelEditMode <> "TargetSavings" Then
                For Each objTextBox In colControls
                    If IsNumeric(MasterControl1.MasterControlGrid.DataKeys(0)(SessionManager.TrackerSelEditMode).ToString) Then
                        objTextBox.Text = Convert.ToDouble(MasterControl1.MasterControlGrid.DataKeys(0)(SessionManager.TrackerSelEditMode).ToString).ToString("0.####")
                    Else
                        objTextBox.Text = MasterControl1.MasterControlGrid.DataKeys(0)(SessionManager.TrackerSelEditMode).ToString
                    End If
                Next
            End If

            ' Savings
            Dim strTrackerPeriod As String = ""
            objDT = SavingsTracker.SelectSavingsTrackerSavingsList(SessionManager.SelectedValueTrackerID, SessionManager.TrackerSelNavYear, cnMasterConnection)
            If objDT IsNot Nothing AndAlso objDT.Rows.Count > 0 Then
                Dim tCell As TableCell
                Dim strFormulaVariables As String = ""
                Dim strFormulaTooltip As String = ""
                Dim bEnterSavings As Boolean = False

                For Each dtRow As DataRow In objDT.Rows
                    intRowIndex += 1
                    'values for this year
                    objRow = New TableRow

                    'alternating row color code
                    If intRowIndex Mod 2 = 0 Then
                        strAlternatingRowColor = "#CCCCCC"
                    Else
                        strAlternatingRowColor = "#FFFFFF"
                    End If

                    strFormulaVariables = ProcessFormulaTrackerVariables(dtRow("Formula").ToString)
                    strFormulaTooltip = dtRow("Formula").ToString
                    If strFormulaVariables.Trim.Length > 0 Then
                        strFormulaTooltip += vbCrLf & strFormulaVariables
                    End If
                    If strFormulaTooltip.Trim.Length = 0 Then
                        strFormulaTooltip = "[Entered Manually]"
                    End If

                    tCell = GenerateTableCell(dtRow("TrackerType").ToString() & " - " & dtRow("SavingsType").ToString, New Unit("16%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, strFormulaTooltip)
                    tCell.Attributes.Add("Tag", dtRow("TrackerCollectionID").ToString & "~" & dtRow("Formula").ToString)
                    objRow.Cells.Add(tCell)

                    For i As Integer = 5 To 16
                        objCell = New TableCell
                        objCell.Width = New Unit("7%")
                        objCell.Height = New Unit(15)
                        objCell.HorizontalAlign = HorizontalAlign.Center
                        If intRowIndex Mod 2 = 0 Then
                            objCell.BackColor = System.Drawing.ColorTranslator.FromHtml("#CCCCCC")
                        Else
                            objCell.BackColor = System.Drawing.ColorTranslator.FromHtml("#FFFFFF")
                        End If

                        If dtRow("Formula").ToString.Trim.Length = 0 AndAlso _
                        SessionManager.TrackerSelEditMode = "Month" AndAlso SessionManager.TrackerSelEditMonth = (i - 4) AndAlso Not blnVIEWMode Then
                            bEnterSavings = True
                        Else
                            bEnterSavings = False
                        End If

                        If bEnterSavings Then
                            blnEditMode = True
                            objCell.HorizontalAlign = HorizontalAlign.Center
                            objCell.BorderStyle = BorderStyle.Solid
                            objTextBox = New TextBox
                            objTextBox.CssClass = "Textbox_Entry_Center"
                            objTextBox.Width = New Unit("85%")
                            objTextBox.Height = New Unit("85%")
                            objTextBox.ID = "txtRow" & (intRowIndex + 2).ToString & "Savings"
                            objTextBox.MaxLength = 12
                            objTextBox.BorderStyle = BorderStyle.Solid
                            objTextBox.BorderWidth = New Unit(1)
                            objTextBox.Attributes.Add("onFocus", "document.all.ctl00_ContentPlaceHolder1_" & objTextBox.ClientID & ".select();")
                            If dtRow(i) Is DBNull.Value OrElse Not IsNumeric(dtRow(i)) Then
                                objTextBox.Text = ""
                            Else
                                objTextBox.Text = CDbl(dtRow(i)).ToString("0.##")
                            End If

                            colControls.Add(objTextBox, objTextBox.ID)

                            objRegValid = New RegularExpressionValidator
                            objRegValid.ID = "Reg" & objTextBox.ID
                            objRegValid.ControlToValidate = objTextBox.ID
                            objRegValid.Display = ValidatorDisplay.None
                            objRegValid.ValidationExpression = "(-?\d{0,7}\" & Thread.CurrentThread.CurrentCulture.NumberFormat.NumberDecimalSeparator & "{1}\d{0,4})|(-?\d{0,10})"
                            objRegValid.ErrorMessage = "Invalid Savings Value"
                            objCell.Controls.Add(objRegValid)

                            objCell.Controls.Add(objTextBox)
                        Else
                            objCell.BorderStyle = BorderStyle.Solid
                            If Not dtRow(i) Is DBNull.Value AndAlso IsNumeric(dtRow(i)) Then
                                objCell.Text = CDbl(dtRow(i)).ToString("0.##")
                            Else
                                objCell.Text = "&nbsp;"
                            End If
                        End If

                        If dtRow(i).ToString.Trim.Length > 0 Then
                            objCell.Attributes.Add("Tag", dtRow(i + 12).ToString)
                            strFormulaTooltip = dtRow(i + 12).ToString
                            strTrackerPeriod = SessionManager.TrackerSelNavYear.ToString & "/" & (i - 4).ToString & "/01"
                            strFormulaTooltip += vbCrLf & ProcessSavingsTrackerVariables(dtRow(i + 12).ToString, dtRow("TrackerCollectionID"), strTrackerPeriod)

                            If strFormulaTooltip.Trim.Length = 0 Then
                                strFormulaTooltip = "[Entered Manually]"
                            End If

                            If strFormulaTooltip <> objRow.Cells(0).ToolTip Then
                                objCell.BackColor = Drawing.Color.Yellow
                                bFormulaDif = True
                            End If

                            objCell.ToolTip = strFormulaTooltip
                        End If

                        objRow.Cells.Add(objCell)
                    Next

                    tblSavingsTracker.Rows.Add(objRow)
                Next
            End If

            If bFormulaDif AndAlso SessionManager.TrackerSelEditMode.Trim.Length = 0 AndAlso Not blnVIEWMode Then
                If lnkValue IsNot Nothing Then
                    lnkValue.ToolTip = "Unable to edit, formulas may have been modified"
                    lnkValue.Enabled = False
                End If
                If lnkHistoric IsNot Nothing Then
                    lnkHistoric.ToolTip = "Unable to edit, formulas may have been modified"
                    lnkHistoric.Enabled = False
                End If
                If lnkTarget IsNot Nothing Then
                    lnkTarget.ToolTip = "Unable to edit, formulas may have been modified"
                    lnkTarget.Enabled = False
                End If
            End If

            cnMasterConnection.Close()
        End Sub
        Private Function ProcessFormulaTrackerVariables(ByVal passFormula As String) As String
            Try
                Dim objDT As DataTable = GetFormulaTrackerVariables(passFormula)
                If objDT IsNot Nothing AndAlso objDT.Rows.Count > 0 Then
                    For Each dtRow As DataRow In objDT.Rows
                        passFormula = Replace(passFormula, dtRow("TrackerVariable").ToString, dtRow("VariableValue").ToString, 1, , CompareMethod.Text)
                    Next
                End If

                Return passFormula
            Catch ex As Exception
                Return ""
            End Try
        End Function
        Private Function GetFormulaTrackerVariables(ByVal passFormula As String) As DataTable
            Try
                Dim strVariables As String = ParseFormulaForVariables(passFormula)
                If strVariables.Trim.Length > 0 Then
                    Dim objDT As DataTable = TrackerVariables.SelectFormulaTrackerVariables(strVariables)
                    Return objDT
                End If
            Catch ex As Exception
                Return Nothing
            End Try

            Return Nothing
        End Function
        Private Function ProcessSavingsTrackerVariables(ByVal passFormula As String, ByVal passTrackerCollectionID As Integer, ByVal passTrackerPeriod As String) As String
            Try
                Dim objDT As DataTable = GetSavingsTrackerVariables(passFormula, passTrackerCollectionID, passTrackerPeriod)
                If objDT IsNot Nothing AndAlso objDT.Rows.Count > 0 Then
                    For Each dtRow As DataRow In objDT.Rows
                        passFormula = Replace(passFormula, dtRow("TrackerVariable").ToString, dtRow("VariableValue").ToString, 1, , CompareMethod.Text)
                    Next
                End If

                Return passFormula
            Catch ex As Exception
                Return ""
            End Try
        End Function
        Private Function GetSavingsTrackerVariables(ByVal passFormula As String, ByVal passTrackerCollectionID As Integer, ByVal passTrackerPeriod As String) As DataTable
            Try
                Dim strVariables As String = ParseFormulaForVariables(passFormula)
                If strVariables.Trim.Length > 0 Then
                    Dim objDT As DataTable = TrackerVariables.SelectSavingsTrackerVariables(strVariables, passTrackerCollectionID, passTrackerPeriod)

                    Return objDT
                End If
            Catch ex As Exception
                Return Nothing
            End Try

            Return Nothing
        End Function
        Private Function ParseFormulaForVariables(ByVal passFormula As String) As String
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
                Dim strCheckFormula As String = passFormula.Trim.Replace("[Value]", "").Replace("[Target]", "").Replace("[Historic]", "")
                If strCheckFormula.Contains("[") Then
                    Dim strVariables As String = ""
                    Dim strVariableHolder As String = ""

                    Do Until Not strCheckFormula.Contains("[")
                        If strCheckFormula.Contains("]") Then
                            strVariableHolder = strCheckFormula.Substring(strCheckFormula.IndexOf("["), strCheckFormula.IndexOf("]") - strCheckFormula.IndexOf("[") + 1)
                            strCheckFormula = Replace(strCheckFormula, strVariableHolder, "", 1, , CompareMethod.Text)

                            If strVariables.Trim.Length > 0 Then strVariables += ","
                            strVariables += strVariableHolder
                        End If
                    Loop

                    Return strVariables
                Else
                    Return ""
                End If
            Catch ex As Exception
                Return ""
            End Try
        End Function
        Private Function GenerateTableCell(ByVal strText As String, ByVal strCellWidth As Unit, ByVal intCellHeight As Unit, ByVal strBackColor As String, ByVal strForeColor As String, ByVal intHorizontalCellAlign As Integer, ByVal intVerticalCellAlign As Integer, ByVal intColSpan As Integer, ByVal intBorderStyle As Integer, ByVal strToolTip As String, Optional ByVal objLink As LinkButton = Nothing) As TableCell
            Dim objCell = New TableCell
            objCell.HorizontalAlign = intHorizontalCellAlign
            objCell.VerticalAlign = intVerticalCellAlign
            objCell.Width = strCellWidth
            objCell.Height = intCellHeight
            objCell.BackColor = System.Drawing.ColorTranslator.FromHtml(strBackColor)
            objCell.ForeColor = System.Drawing.ColorTranslator.FromHtml(strForeColor)
            objCell.ColumnSpan = intColSpan
            objCell.Text = strText
            objCell.BorderStyle = intBorderStyle
            objCell.ToolTip = strToolTip

            If objLink IsNot Nothing Then
                objCell.Controls.Add(objLink)
            End If

            Return objCell
        End Function
        Private Function GenerateTableLink(ByVal strText As String, ByVal strForeColor As String, ByVal strElementID As String, ByVal strToolTip As String) As LinkButton
            Dim objLink As New LinkButton
            AddHandler objLink.Command, AddressOf Button_Click
            objLink.Text = strText
            objLink.ID = strElementID
            objLink.ToolTip = strToolTip
            objLink.ForeColor = System.Drawing.ColorTranslator.FromHtml(strForeColor)

            Return objLink
        End Function
        Private Function SaveSavingsTracker(ByVal iProcessType As Integer) As Boolean
            ' 0 - First Time Through, check formulas
            ' 1 - Use Current Formulas
            ' 2 - Use Existing Formulas

            Dim objTextBox As TextBox
            Dim iSavingsStartRow As Integer = 7
            Dim strHolder As String()
            Dim iTrackerCollectionID As Integer = 0
            Dim strTrackerFormula As String = ""
            Dim strFormula As String = ""
            Dim dValue As Double = 0
            Dim strValue As String = ""
            Dim iEditMonth As Integer = 0
            Dim bValidFormula As Boolean = False
            Dim strDate As String = ""
            Dim strTrackerValue As String = ""
            Dim strHistoric As String = ""
            Dim strTarget As String = ""
            Dim strTargetSavings As String = ""

            Try
                Select Case SessionManager.TrackerSelEditMode
                    Case "Month"
                        iEditMonth = SessionManager.TrackerSelEditMonth
                        strDate = RegionalConversion.FormatSQLDate(SessionManager.TrackerSelNavYear.ToString & "/" & iEditMonth.ToString & "/01")

                        'Value
                        objTextBox = CType(colControls(1), TextBox)
                        If IsNumeric(objTextBox.Text) Then
                            strTrackerValue = RegionalConversion.FormatSQLSingle(objTextBox.Text.Trim)
                        Else
                            strTrackerValue = ""
                        End If
                        'Historic
                        objTextBox = CType(colControls(2), TextBox)
                        If IsNumeric(objTextBox.Text) Then
                            strHistoric = RegionalConversion.FormatSQLSingle(objTextBox.Text)
                        Else
                            strHistoric = ""
                        End If
                        'Target
                        objTextBox = CType(colControls(3), TextBox)
                        If IsNumeric(objTextBox.Text) Then
                            strTarget = RegionalConversion.FormatSQLSingle(objTextBox.Text)
                        Else
                            strTarget = ""
                        End If
                        'TargetSavings
                        objTextBox = CType(colControls(4), TextBox)
                        If IsNumeric(objTextBox.Text) Then
                            strTargetSavings = RegionalConversion.FormatSQLSingle(objTextBox.Text)
                        Else
                            strTargetSavings = ""
                        End If

                        If iProcessType = 0 Then
                            'check formulas first
                            For iRow = iSavingsStartRow To tblSavingsTracker.Rows.Count - 1
                                strFormula = ""
                                strTrackerFormula = ""

                                If tblSavingsTracker.Rows(iRow).Cells(0).ToolTip.Trim.Length > 0 Then
                                    strFormula = tblSavingsTracker.Rows(iRow).Cells(0).ToolTip.Trim
                                End If

                                If tblSavingsTracker.Rows(iRow).Cells(iEditMonth).ToolTip.Trim.Length > 0 Then
                                    strTrackerFormula = tblSavingsTracker.Rows(iRow).Cells(iEditMonth).ToolTip.Trim
                                End If

                                If strTrackerFormula.Trim.Length > 0 AndAlso strFormula <> strTrackerFormula Then
                                    Master.DisplayError("Some savings values have been calculated using formula different than the current formula." & vbCrLf & "Please specify whether you want to use the Exising formula, Current formula or cancel")
                                    Return False
                                End If
                            Next
                        End If

                        SavingsTracker.UpdateTrackerValue(SessionManager.SelectedValueTrackerID, strDate, strTrackerValue.Trim, strHistoric.Trim, strTarget.Trim, strTargetSavings, "")
                        RecordTransactionHistory.InsertRecordTransactionHistory("Trackers", SessionManager.SelectedValueTrackerID.ToString, "Tracker Values Modified for " & strDate & vbCrLf & "Value: " & strTrackerValue & vbCrLf & "Historic:" & strHistoric & vbCrLf & "Target: " & strTarget, SessionManager.UserID)

                        For iRow = iSavingsStartRow To tblSavingsTracker.Rows.Count - 1
                            bValidFormula = True
                            strHolder = tblSavingsTracker.Rows(iRow).Cells(0).Attributes("Tag").ToString.Split("~")
                            iTrackerCollectionID = strHolder(0)
                            strTrackerFormula = strHolder(1)
                            strFormula = strHolder(1)

                            Select Case iProcessType
                                Case 2
                                    If tblSavingsTracker.Rows(iRow).Cells(iEditMonth).Attributes.Count > 0 AndAlso _
                                    tblSavingsTracker.Rows(iRow).Cells(iEditMonth).Attributes("Tag") IsNot Nothing AndAlso _
                                    tblSavingsTracker.Rows(iRow).Cells(iEditMonth).Attributes("Tag").ToString.Trim.Length > 0 Then
                                        strTrackerFormula = tblSavingsTracker.Rows(iRow).Cells(iEditMonth).Attributes("Tag").ToString
                                        strFormula = strTrackerFormula
                                    End If
                            End Select

                            If InStr(strFormula, "[Value]") > 0 Then
                                If IsNumeric(RegionalConversion.FormatLocalSingle(strTrackerValue)) Then
                                    strFormula = strFormula.Replace("[Value]", strTrackerValue)
                                Else
                                    bValidFormula = False
                                End If
                            End If
                            If InStr(strFormula, "[Historic]") > 0 Then
                                If IsNumeric(RegionalConversion.FormatLocalSingle(strHistoric)) Then
                                    strFormula = strFormula.Replace("[Historic]", strHistoric)
                                Else
                                    bValidFormula = False
                                End If
                            End If
                            If InStr(strFormula, "[Target]") > 0 Then
                                If IsNumeric(RegionalConversion.FormatLocalSingle(strTarget)) Then
                                    strFormula = strFormula.Replace("[Target]", strTarget)
                                Else
                                    bValidFormula = False
                                End If
                            End If

                            Dim objDTVariables As DataTable = Nothing

                            If iProcessType = 2 Then
                                objDTVariables = GetSavingsTrackerVariables(strFormula, iTrackerCollectionID, strDate)
                            Else
                                objDTVariables = GetFormulaTrackerVariables(strFormula)
                            End If

                            If objDTVariables IsNot Nothing AndAlso objDTVariables.Rows.Count > 0 Then
                                For Each dtRow As DataRow In objDTVariables.Rows
                                    If strFormula.ToUpper.Contains(dtRow("TrackerVariable").ToString.ToUpper) Then
                                        If IsNumeric(dtRow("VariableValue").ToString) Then
                                            strFormula = Replace(strFormula, dtRow("TrackerVariable").ToString, RegionalConversion.FormatSQLSingle(dtRow("VariableValue").ToString), 1, , CompareMethod.Text)
                                        Else
                                            bValidFormula = False
                                        End If
                                    End If
                                Next
                            End If

                            If strFormula.Trim.Length = 0 AndAlso colControls.Contains("txtRow" & iRow.ToString & "Savings") Then
                                strValue = RegionalConversion.FormatSQLSingle(CType(colControls("txtRow" & iRow.ToString & "Savings"), TextBox).Text)
                            ElseIf bValidFormula Then
                                Try
                                    dValue = WebApp.APlus.UI.CustomControls.Evaluator.EvaluateToDouble(strFormula)
                                    strValue = RegionalConversion.FormatSQLSingle(dValue.ToString)
                                Catch ex As Exception
                                    strValue = ""
                                    'Master.DisplayError("Error calculating formula<br />" & strFormula)
                                    'Return False
                                End Try
                            Else
                                strValue = ""
                            End If

                            SavingsTracker.UpdateTrackerSavings(iTrackerCollectionID, strDate, strValue, strTrackerFormula)
                            RecordTransactionHistory.InsertRecordTransactionHistory("Trackers", SessionManager.SelectedValueTrackerID.ToString, "Tracker Savings Modified for " & strDate & vbCrLf & tblSavingsTracker.Rows(iRow).Cells(0).Text & ": " & strValue, SessionManager.UserID)

                            'update the TrackerSavingsVariables table
                            If objDTVariables IsNot Nothing AndAlso objDTVariables.Rows.Count > 0 Then
                                For Each dtRow As DataRow In objDTVariables.Rows
                                    If InStr(strTrackerFormula, dtRow("TrackerVariable").ToString) > 0 Then
                                        If IsNumeric(dtRow("VariableValue").ToString) Then
                                            SavingsTracker.UpdateTrackerSavingsVariableValues(iTrackerCollectionID, strDate, dtRow("TrackerVariableID"), RegionalConversion.FormatSQLSingle(dtRow("VariableValue").ToString))
                                        End If
                                    End If
                                Next
                            End If
                        Next
                    Case "Value"
                        iEditMonth = 0
                        For Each objTextBox In colControls
                            iEditMonth += 1
                            strDate = RegionalConversion.FormatSQLDate(SessionManager.TrackerSelNavYear.ToString & "/" & iEditMonth.ToString & "/01")

                            If IsNumeric(objTextBox.Text) Then
                                strTrackerValue = RegionalConversion.FormatSQLSingle(objTextBox.Text.Trim)
                            Else
                                strTrackerValue = ""
                            End If
                            If IsNumeric(tblSavingsTracker.Rows(3).Cells(iEditMonth).Text) Then
                                strHistoric = RegionalConversion.FormatSQLSingle(tblSavingsTracker.Rows(3).Cells(iEditMonth).Text)
                            Else
                                strHistoric = ""
                            End If
                            If IsNumeric(tblSavingsTracker.Rows(4).Cells(iEditMonth).Text) Then
                                strTarget = RegionalConversion.FormatSQLSingle(tblSavingsTracker.Rows(4).Cells(iEditMonth).Text)
                            Else
                                strTarget = ""
                            End If
                            If IsNumeric(tblSavingsTracker.Rows(5).Cells(iEditMonth).Text) Then
                                strTargetSavings = RegionalConversion.FormatSQLSingle(tblSavingsTracker.Rows(5).Cells(iEditMonth).Text)
                            Else
                                strTargetSavings = ""
                            End If

                            SavingsTracker.UpdateTrackerValue(SessionManager.SelectedValueTrackerID, strDate, strTrackerValue.Trim, strHistoric.Trim, strTarget.Trim, strTargetSavings, "")
                            RecordTransactionHistory.InsertRecordTransactionHistory("Trackers", SessionManager.SelectedValueTrackerID.ToString, "Tracker Values Modified for " & strDate & vbCrLf & "Value: " & strTrackerValue, SessionManager.UserID)

                            For iRow = iSavingsStartRow To tblSavingsTracker.Rows.Count - 1
                                bValidFormula = True
                                strHolder = tblSavingsTracker.Rows(iRow).Cells(0).Attributes("Tag").ToString.Split("~")
                                iTrackerCollectionID = strHolder(0)
                                strTrackerFormula = strHolder(1)
                                strFormula = strHolder(1)

                                If InStr(strFormula, "[Value]") > 0 Then
                                    If IsNumeric(RegionalConversion.FormatLocalSingle(strTrackerValue)) Then
                                        strFormula = Replace(strFormula, "[Value]", strTrackerValue, 1, , CompareMethod.Text)
                                    Else
                                        bValidFormula = False
                                    End If
                                End If
                                If InStr(strFormula, "[Historic]") > 0 Then
                                    If IsNumeric(RegionalConversion.FormatLocalSingle(strHistoric)) Then
                                        strFormula = Replace(strFormula, "[Historic]", strHistoric, 1, , CompareMethod.Text)
                                    Else
                                        bValidFormula = False
                                    End If
                                End If
                                If InStr(strFormula, "[Target]") > 0 Then
                                    If IsNumeric(RegionalConversion.FormatLocalSingle(strTarget)) Then
                                        strFormula = Replace(strFormula, "[Target]", strTarget, 1, , CompareMethod.Text)
                                    Else
                                        bValidFormula = False
                                    End If
                                End If

                                Dim objDTVariables As DataTable = GetFormulaTrackerVariables(strFormula)
                                If objDTVariables IsNot Nothing AndAlso objDTVariables.Rows.Count > 0 Then
                                    For Each dtRow As DataRow In objDTVariables.Rows
                                        If InStr(strFormula, dtRow("TrackerVariable").ToString) > 0 Then
                                            If IsNumeric(dtRow("VariableValue").ToString) Then
                                                strFormula = Replace(strFormula, dtRow("TrackerVariable").ToString, RegionalConversion.FormatSQLSingle(dtRow("VariableValue").ToString), 1, , CompareMethod.Text)
                                            Else
                                                bValidFormula = False
                                            End If
                                        End If
                                    Next
                                End If

                                If bValidFormula AndAlso strFormula.Trim.Length > 0 AndAlso IsNumeric(objTextBox.Text) Then
                                    Try
                                        dValue = WebApp.APlus.UI.CustomControls.Evaluator.EvaluateToDouble(strFormula)
                                        strValue = RegionalConversion.FormatSQLSingle(dValue.ToString)
                                    Catch ex As Exception
                                        Master.DisplayError("Error calculating formula<br />" & strFormula)
                                        Return False
                                    End Try
                                ElseIf strFormula.Trim.Length = 0 AndAlso IsNumeric(tblSavingsTracker.Rows(iRow).Cells(iEditMonth).Text) Then
                                    strValue = RegionalConversion.FormatSQLSingle(tblSavingsTracker.Rows(iRow).Cells(iEditMonth).Text)
                                Else
                                    strValue = ""
                                End If

                                SavingsTracker.UpdateTrackerSavings(iTrackerCollectionID, strDate, strValue, strTrackerFormula)
                                RecordTransactionHistory.InsertRecordTransactionHistory("Trackers", SessionManager.SelectedValueTrackerID.ToString, "Tracker Savings Modified for " & strDate & vbCrLf & tblSavingsTracker.Rows(iRow).Cells(0).Text & ": " & strValue, SessionManager.UserID)

                                'update the TrackerSavingsVariables table
                                If objDTVariables IsNot Nothing AndAlso objDTVariables.Rows.Count > 0 Then
                                    For Each dtRow As DataRow In objDTVariables.Rows
                                        If InStr(strTrackerFormula, dtRow("TrackerVariable").ToString) > 0 Then
                                            If IsNumeric(dtRow("VariableValue").ToString) Then
                                                SavingsTracker.UpdateTrackerSavingsVariableValues(iTrackerCollectionID, strDate, dtRow("TrackerVariableID"), RegionalConversion.FormatSQLSingle(dtRow("VariableValue").ToString))
                                            End If
                                        End If
                                    Next
                                End If
                            Next
                        Next
                    Case "Historic"
                        iEditMonth = 0
                        For Each objTextBox In colControls
                            iEditMonth += 1
                            strDate = RegionalConversion.FormatSQLDate(SessionManager.TrackerSelNavYear.ToString & "/" & iEditMonth.ToString & "/01")

                            If IsNumeric(tblSavingsTracker.Rows(2).Cells(iEditMonth).Text) Then
                                strTrackerValue = RegionalConversion.FormatSQLSingle(tblSavingsTracker.Rows(2).Cells(iEditMonth).Text)
                            Else
                                strTrackerValue = ""
                            End If
                            If IsNumeric(objTextBox.Text) Then
                                strHistoric = RegionalConversion.FormatSQLSingle(objTextBox.Text.Trim)
                            Else
                                strHistoric = ""
                            End If
                            If IsNumeric(tblSavingsTracker.Rows(4).Cells(iEditMonth).Text) Then
                                strTarget = RegionalConversion.FormatSQLSingle(tblSavingsTracker.Rows(4).Cells(iEditMonth).Text)
                            Else
                                strTarget = ""
                            End If
                            If IsNumeric(tblSavingsTracker.Rows(5).Cells(iEditMonth).Text) Then
                                strTargetSavings = RegionalConversion.FormatSQLSingle(tblSavingsTracker.Rows(5).Cells(iEditMonth).Text)
                            Else
                                strTargetSavings = ""
                            End If

                            SavingsTracker.UpdateTrackerValue(SessionManager.SelectedValueTrackerID, strDate, strTrackerValue.Trim, strHistoric.Trim, strTarget.Trim, strTargetSavings, "")
                            RecordTransactionHistory.InsertRecordTransactionHistory("Trackers", SessionManager.SelectedValueTrackerID.ToString, "Tracker Values Modified for " & strDate & vbCrLf & "Historic: " & strHistoric, SessionManager.UserID)

                            For iRow = iSavingsStartRow To tblSavingsTracker.Rows.Count - 1
                                bValidFormula = True
                                strHolder = tblSavingsTracker.Rows(iRow).Cells(0).Attributes("Tag").ToString.Split("~")
                                iTrackerCollectionID = strHolder(0)
                                strTrackerFormula = strHolder(1)
                                strFormula = strHolder(1)

                                If InStr(strFormula, "[Value]") > 0 Then
                                    If IsNumeric(RegionalConversion.FormatLocalSingle(strTrackerValue)) Then
                                        strFormula = Replace(strFormula, "[Value]", strTrackerValue, 1, , CompareMethod.Text)
                                    Else
                                        bValidFormula = False
                                    End If
                                End If
                                If InStr(strFormula, "[Historic]") > 0 Then
                                    If IsNumeric(RegionalConversion.FormatLocalSingle(strHistoric)) Then
                                        strFormula = Replace(strFormula, "[Historic]", strHistoric, 1, , CompareMethod.Text)
                                    Else
                                        bValidFormula = False
                                    End If
                                End If
                                If InStr(strFormula, "[Target]") > 0 Then
                                    If IsNumeric(RegionalConversion.FormatLocalSingle(strTarget)) Then
                                        strFormula = Replace(strFormula, "[Target]", strTarget, 1, , CompareMethod.Text)
                                    Else
                                        bValidFormula = False
                                    End If
                                End If

                                Dim objDTVariables As DataTable = GetFormulaTrackerVariables(strFormula)
                                If objDTVariables IsNot Nothing AndAlso objDTVariables.Rows.Count > 0 Then
                                    For Each dtRow As DataRow In objDTVariables.Rows
                                        If strFormula.ToUpper.Contains(dtRow("TrackerVariable").ToString.ToUpper) Then
                                            If IsNumeric(dtRow("VariableValue").ToString) Then
                                                strFormula = Replace(strFormula, dtRow("TrackerVariable").ToString, RegionalConversion.FormatSQLSingle(dtRow("VariableValue").ToString), 1, , CompareMethod.Text)
                                            Else
                                                bValidFormula = False
                                            End If
                                        End If
                                    Next
                                End If

                                If bValidFormula AndAlso strFormula.Trim.Length > 0 Then
                                    Try
                                        dValue = WebApp.APlus.UI.CustomControls.Evaluator.EvaluateToDouble(strFormula)
                                        strValue = RegionalConversion.FormatSQLSingle(dValue.ToString)
                                    Catch ex As Exception
                                        Master.DisplayError("Error calculating formula<br />" & strFormula)
                                        Return False
                                    End Try
                                ElseIf strFormula.Trim.Length = 0 AndAlso IsNumeric(tblSavingsTracker.Rows(iRow).Cells(iEditMonth).Text) Then
                                    strValue = RegionalConversion.FormatSQLSingle(tblSavingsTracker.Rows(iRow).Cells(iEditMonth).Text)
                                Else
                                    strValue = ""
                                End If

                                SavingsTracker.UpdateTrackerSavings(iTrackerCollectionID, strDate, strValue, strTrackerFormula)
                                RecordTransactionHistory.InsertRecordTransactionHistory("Trackers", SessionManager.SelectedValueTrackerID.ToString, "Tracker Savings Modified for " & strDate & vbCrLf & tblSavingsTracker.Rows(iRow).Cells(0).Text & ": " & strValue, SessionManager.UserID)

                                'update the TrackerSavingsVariables table
                                If objDTVariables IsNot Nothing AndAlso objDTVariables.Rows.Count > 0 Then
                                    For Each dtRow As DataRow In objDTVariables.Rows
                                        If InStr(strTrackerFormula, dtRow("TrackerVariable").ToString) > 0 Then
                                            If IsNumeric(dtRow("VariableValue").ToString) Then
                                                SavingsTracker.UpdateTrackerSavingsVariableValues(iTrackerCollectionID, strDate, dtRow("TrackerVariableID"), RegionalConversion.FormatSQLSingle(dtRow("VariableValue").ToString))
                                            End If
                                        End If
                                    Next
                                End If
                            Next
                        Next
                    Case "Target"
                        iEditMonth = 0
                        For Each objTextBox In colControls
                            iEditMonth += 1
                            strDate = RegionalConversion.FormatSQLDate(SessionManager.TrackerSelNavYear.ToString & "/" & iEditMonth.ToString & "/01")

                            If IsNumeric(tblSavingsTracker.Rows(2).Cells(iEditMonth).Text) Then
                                strTrackerValue = RegionalConversion.FormatSQLSingle(tblSavingsTracker.Rows(2).Cells(iEditMonth).Text)
                            Else
                                strTrackerValue = ""
                            End If
                            If IsNumeric(tblSavingsTracker.Rows(3).Cells(iEditMonth).Text) Then
                                strHistoric = RegionalConversion.FormatSQLSingle(tblSavingsTracker.Rows(3).Cells(iEditMonth).Text)
                            Else
                                strHistoric = ""
                            End If
                            If IsNumeric(objTextBox.Text) Then
                                strTarget = RegionalConversion.FormatSQLSingle(objTextBox.Text.Trim)
                            Else
                                strTarget = ""
                            End If
                            If IsNumeric(tblSavingsTracker.Rows(5).Cells(iEditMonth).Text) Then
                                strTargetSavings = RegionalConversion.FormatSQLSingle(tblSavingsTracker.Rows(5).Cells(iEditMonth).Text)
                            Else
                                strTargetSavings = ""
                            End If

                            SavingsTracker.UpdateTrackerValue(SessionManager.SelectedValueTrackerID, strDate, strTrackerValue.Trim, strHistoric.Trim, strTarget.Trim, strTargetSavings, "")
                            RecordTransactionHistory.InsertRecordTransactionHistory("Trackers", SessionManager.SelectedValueTrackerID.ToString, "Tracker Values Modified for " & strDate & vbCrLf & "Target: " & strTarget, SessionManager.UserID)

                            For iRow = iSavingsStartRow To tblSavingsTracker.Rows.Count - 1
                                bValidFormula = True
                                strHolder = tblSavingsTracker.Rows(iRow).Cells(0).Attributes("Tag").ToString.Split("~")
                                iTrackerCollectionID = strHolder(0)
                                strTrackerFormula = strHolder(1)
                                strFormula = strHolder(1)

                                If InStr(strFormula, "[Value]") > 0 Then
                                    If IsNumeric(RegionalConversion.FormatLocalSingle(strTrackerValue)) Then
                                        strFormula = strFormula.Replace("[Value]", strTrackerValue)
                                    Else
                                        bValidFormula = False
                                    End If
                                End If
                                If InStr(strFormula, "[Historic]") > 0 Then
                                    If IsNumeric(RegionalConversion.FormatLocalSingle(strHistoric)) Then
                                        strFormula = strFormula.Replace("[Historic]", strHistoric)
                                    Else
                                        bValidFormula = False
                                    End If
                                End If
                                If InStr(strFormula, "[Target]") > 0 Then
                                    If IsNumeric(RegionalConversion.FormatLocalSingle(strTarget)) Then
                                        strFormula = strFormula.Replace("[Target]", strTarget)
                                    Else
                                        bValidFormula = False
                                    End If
                                End If

                                Dim objDTVariables As DataTable = GetFormulaTrackerVariables(strFormula)
                                If objDTVariables IsNot Nothing AndAlso objDTVariables.Rows.Count > 0 Then
                                    For Each dtRow As DataRow In objDTVariables.Rows
                                        If strFormula.ToUpper.Contains(dtRow("TrackerVariable").ToString.ToUpper) Then
                                            If IsNumeric(dtRow("VariableValue").ToString) Then
                                                strFormula = Replace(strFormula, dtRow("TrackerVariable").ToString, RegionalConversion.FormatSQLSingle(dtRow("VariableValue").ToString), 1, , CompareMethod.Text)
                                            Else
                                                bValidFormula = False
                                            End If
                                        End If
                                    Next
                                End If

                                If bValidFormula AndAlso strFormula.Trim.Length > 0 Then
                                    Try
                                        dValue = WebApp.APlus.UI.CustomControls.Evaluator.EvaluateToDouble(strFormula)
                                        strValue = RegionalConversion.FormatSQLSingle(dValue.ToString)
                                    Catch ex As Exception
                                        Master.DisplayError("Error calculating formula<br />" & strFormula)
                                        Return False
                                    End Try
                                ElseIf strFormula.Trim.Length = 0 AndAlso IsNumeric(tblSavingsTracker.Rows(iRow).Cells(iEditMonth).Text) Then
                                    strValue = RegionalConversion.FormatSQLSingle(tblSavingsTracker.Rows(iRow).Cells(iEditMonth).Text)
                                Else
                                    strValue = ""
                                End If

                                SavingsTracker.UpdateTrackerSavings(iTrackerCollectionID, strDate, strValue, strTrackerFormula)
                                RecordTransactionHistory.InsertRecordTransactionHistory("Trackers", SessionManager.SelectedValueTrackerID.ToString, "Tracker Savings Modified for " & strDate & vbCrLf & tblSavingsTracker.Rows(iRow).Cells(0).Text & ": " & strValue, SessionManager.UserID)

                                'update the TrackerSavingsVariables table
                                If objDTVariables IsNot Nothing AndAlso objDTVariables.Rows.Count > 0 Then
                                    For Each dtRow As DataRow In objDTVariables.Rows
                                        If InStr(strTrackerFormula, dtRow("TrackerVariable").ToString) > 0 Then
                                            If IsNumeric(dtRow("VariableValue").ToString) Then
                                                SavingsTracker.UpdateTrackerSavingsVariableValues(iTrackerCollectionID, strDate, dtRow("TrackerVariableID"), RegionalConversion.FormatSQLSingle(dtRow("VariableValue").ToString))
                                            End If
                                        End If
                                    Next
                                End If
                            Next
                        Next
                    Case "TargetSavings"
                        iEditMonth = 0
                        For Each objTextBox In colControls
                            iEditMonth += 1
                            strDate = RegionalConversion.FormatSQLDate(SessionManager.TrackerSelNavYear.ToString & "/" & iEditMonth.ToString & "/01")

                            If IsNumeric(tblSavingsTracker.Rows(2).Cells(iEditMonth).Text) Then
                                strTrackerValue = RegionalConversion.FormatSQLSingle(tblSavingsTracker.Rows(2).Cells(iEditMonth).Text)
                            Else
                                strTrackerValue = ""
                            End If
                            If IsNumeric(tblSavingsTracker.Rows(3).Cells(iEditMonth).Text) Then
                                strHistoric = RegionalConversion.FormatSQLSingle(tblSavingsTracker.Rows(3).Cells(iEditMonth).Text)
                            Else
                                strHistoric = ""
                            End If
                            If IsNumeric(tblSavingsTracker.Rows(4).Cells(iEditMonth).Text) Then
                                strTarget = RegionalConversion.FormatSQLSingle(tblSavingsTracker.Rows(4).Cells(iEditMonth).Text)
                            Else
                                strTarget = ""
                            End If
                            If IsNumeric(objTextBox.Text) Then
                                strTargetSavings = RegionalConversion.FormatSQLSingle(objTextBox.Text.Trim)
                            Else
                                strTargetSavings = ""
                            End If

                            SavingsTracker.UpdateTrackerValue(SessionManager.SelectedValueTrackerID, strDate, strTrackerValue.Trim, strHistoric.Trim, strTarget.Trim, strTargetSavings, "")
                            RecordTransactionHistory.InsertRecordTransactionHistory("Trackers", SessionManager.SelectedValueTrackerID.ToString, "Tracker Values Modified for " & strDate & vbCrLf & "Target: " & strTarget, SessionManager.UserID)
                        Next
                End Select

                Return True
            Catch ex As Exception

            End Try
        End Function
#End Region

    End Class
End Namespace
