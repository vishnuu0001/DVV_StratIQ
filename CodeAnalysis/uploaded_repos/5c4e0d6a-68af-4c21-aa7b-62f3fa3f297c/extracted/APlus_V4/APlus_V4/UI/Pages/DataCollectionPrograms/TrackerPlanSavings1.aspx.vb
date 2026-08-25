#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports System.IO
Imports System.Threading
Imports WebApp.APlus.DataAccess.Connections
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class TrackerPlanSavings1
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Master Plan Maintenance"
        Private Shared ReadOnly ProgramName As String = "TrackerPlanSavings1"
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

            Master.IconImage = Request.ApplicationPath & "/images/boss.gif"
            Master.HeaderMessage = FormName
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

            If SessionManager.AllowMaintenanceAdd OrElse SessionManager.AllowMaintenanceEdit Then
                SessionManager.TrackerPlanSavingsMode = "EditRow"
            Else
                SessionManager.TrackerPlanSavingsMode = "ViewRow"
            End If

            mcTrackerPlan.StoredProcedureParams.Add("@TrackerPlanID", SessionManager.SelectedValueTrackerPlanID)
            mcTrackerPlan.StoredProcedureParams.Add("@Year", SessionManager.TrackerSelNavYear)

            BindGrid()

            TransactionHistory1.TableName = "TrackerPlanMaster"
            TransactionHistory1.RecordID = SessionManager.SelectedValueTrackerPlanID.ToString

            LoadEditModeJavaScripts()
        End Sub
        Protected Sub mcTrackerPlan_onRowCommand(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewCommandEventArgs) Handles mcTrackerPlan.onRowCommand
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", e.CommandName)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Select Case e.CommandName
                Case "ViewRow", "EditRow", "DeleteRow"
                    SessionManager.TrackerPlanMode = e.CommandName

                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TrackerPlanMaster2"), False)
            End Select
        End Sub
        Private Sub Button_Click(ByVal sender As System.Object, ByVal e As WebControls.CommandEventArgs)
            Dim strTarget() As String
            strTarget = (CType(sender, LinkButton).ID).ToString.Split("~")
            Dim strProgram As String = ""

            Select Case strTarget(0).ToUpper
                Case "EDIT"
                    SessionManager.TrackerSelEditMode = "Month"
                    SessionManager.TrackerSelEditMonth = strTarget(1)
                Case "NAV"
                    SessionManager.TrackerSelNavYear = strTarget(1)
                    SessionManager.TrackerSelEditMode = ""
                    SessionManager.TrackerSelEditMonth = 0
                Case "PLAN"
                    SessionManager.TrackerSelEditMode = "Plan"
                    SessionManager.TrackerSelEditMonth = 0
                Case "STRETCH"
                    SessionManager.TrackerSelEditMode = "Stretch"
                    SessionManager.TrackerSelEditMonth = 0
            End Select

            If SessionManager.TrackerSelEditMode = "" Then
                pnlOKCancel.Visible = False
                pnlExit.Visible = True
                Master.EnableTeamLink = True
            Else
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
            If Not SaveSavingsPlan() Then
                pnlOKCancel.Visible = False

                Return
            Else
                SessionManager.TrackerSelEditMode = ""
                SessionManager.TrackerSelEditMonth = 0
                pnlOKCancel.Visible = False
                pnlExit.Visible = True
                Master.EnableTeamLink = True

                BindGrid()
            End If
        End Sub
        Private Sub btnCancel_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnCancel.Click
            SessionManager.TrackerSelEditMode = ""
            SessionManager.TrackerSelEditMonth = 0
            pnlOKCancel.Visible = False
            pnlExit.Visible = True
            Master.EnableTeamLink = True

            BindGrid()
        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TrackerSelEditMode)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TrackerSelEditMonth)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TrackerPlanSavingsMode)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueTrackerPlanID)

            Dim strProgram = "TrackerPlanMaster1"
            If SessionManager.CallingProgram.Trim.Length > 0 Then
                strProgram = SessionManager.CallingProgram
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CallingProgram)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueTrackerPlanID)
            End If
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strProgram), False)
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub BindGrid()
            'determine if VIEW or EDIT mode
            Dim blnVIEWMode As Boolean = True
            If SessionManager.TrackerPlanSavingsMode = "EditRow" Then
                blnVIEWMode = False
            End If

            tblMasterPlan.Rows.Clear()

            If mcTrackerPlan.StoredProcedureParams.ContainsKey("@Year") Then
                mcTrackerPlan.StoredProcedureParams.Remove("@Year")
            End If
            mcTrackerPlan.StoredProcedureParams.Add("@Year", SessionManager.TrackerSelNavYear)
            mcTrackerPlan.DataBind(True)

            Dim objDT As DataTable = TrackerPlanSavings.SelectTrackerPlanSavingsByYear(SessionManager.SelectedValueTrackerPlanID, SessionManager.TrackerSelNavYear)
            If objDT Is Nothing OrElse objDT.Rows.Count <> 2 Then
                Return
            End If

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
            tblMasterPlan.Rows.Add(objRow)

            'add Month columns
            'add header columns
            objRow = New TableRow
            objRow.Cells.Add(GenerateTableCell("", New Unit("16%"), New Unit(15), "#FFFFFF", "#FFFFFF", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.Solid, ""))

            For i As Integer = 1 To 12
                If SessionManager.TrackerSelEditMode.Trim.Length > 0 OrElse blnVIEWMode Then
                    objCell = GenerateTableCell(objDT.Columns(i).ColumnName, New Unit("7%"), New Unit(15), "#FFFFFF", "#000000", HorizontalAlign.Center, VerticalAlign.Top, 1, BorderStyle.Solid, "")
                Else
                    objCell = GenerateTableCell("", New Unit("7%"), New Unit(15), "#FFFFFF", "#000000", HorizontalAlign.Center, VerticalAlign.Top, 1, BorderStyle.Solid, "", GenerateTableLink(objDT.Columns(i).ColumnName, "#3333FF", "Edit~" & (i).ToString, ""))
                End If

                objRow.Cells.Add(objCell)
            Next

            tblMasterPlan.Rows.Add(objRow)

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

                If intRowIndex Mod 2 = 0 Then
                    If SessionManager.TrackerSelEditMode = "" AndAlso Not blnVIEWMode Then
                        lnkValue = GenerateTableLink("Stretch", "#3333FF", "STRETCH", "Edit Year")
                        objRow.Cells.Add(GenerateTableCell("Stretch", New Unit("16%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, "", lnkValue))
                    Else
                        objRow.Cells.Add(GenerateTableCell("Stretch", New Unit("16%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                    End If
                Else
                    If SessionManager.TrackerSelEditMode = "" AndAlso Not blnVIEWMode Then
                        lnkValue = GenerateTableLink("Plan", "#3333FF", "PLAN", "Edit Year")
                        objRow.Cells.Add(GenerateTableCell("Plan", New Unit("16%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, "", lnkValue))
                    Else
                        objRow.Cells.Add(GenerateTableCell("Plan", New Unit("16%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                    End If
                End If

                ' Values
                For i As Integer = 1 To 12
                    objCell = New TableCell
                    objCell.Width = New Unit("7%")
                    objCell.Height = New Unit(15)
                    objCell.HorizontalAlign = HorizontalAlign.Center
                    If intRowIndex Mod 2 = 0 Then
                        objCell.BackColor = System.Drawing.ColorTranslator.FromHtml("#CCCCCC")
                    Else
                        objCell.BackColor = System.Drawing.ColorTranslator.FromHtml("#FFFFFF")
                    End If

                    If SessionManager.TrackerSelEditMode = "Month" AndAlso SessionManager.TrackerSelEditMonth = (i) AndAlso Not blnVIEWMode Then
                        blnEditMode = True
                        objCell.HorizontalAlign = HorizontalAlign.Center
                        objCell.BorderStyle = BorderStyle.Solid
                        objTextBox = New TextBox
                        objTextBox.CssClass = "Textbox_Entry_Center"
                        objTextBox.Width = New Unit("85%")
                        objTextBox.Height = New Unit("85%")
                        objTextBox.ID = "txt" & objDT.Columns(i).ColumnName & dtRow("PlanType").ToString
                        objTextBox.MaxLength = 12
                        objTextBox.BorderStyle = BorderStyle.Solid
                        objTextBox.BorderWidth = New Unit(1)
                        objTextBox.Attributes.Add("onFocus", "document.all.ctl00_ContentPlaceHolder1_" & objTextBox.ClientID & ".select();")
                        If IsNumeric(dtRow(i).ToString) Then
                            objTextBox.Text = Convert.ToDouble(dtRow(i)).ToString("0.####")
                        Else
                            objTextBox.Text = ""
                        End If
                        colControls.Add(objTextBox, objTextBox.ID)

                        objRegValid = New RegularExpressionValidator
                        objRegValid.ID = "Reg" & objTextBox.ID
                        objRegValid.ControlToValidate = objTextBox.ID
                        objRegValid.Display = ValidatorDisplay.None
                        objRegValid.ValidationExpression = "(-?\d{0,7}\" & Thread.CurrentThread.CurrentCulture.NumberFormat.NumberDecimalSeparator & "{1}\d{0,4})|(-?\d{0,10})"
                        objRegValid.ErrorMessage = "Invalid Plan Value"
                        objCell.Controls.Add(objRegValid)

                        objCell.Controls.Add(objTextBox)
                    ElseIf SessionManager.TrackerSelEditMode.Trim.ToUpper = dtRow("PlanType").ToString.ToUpper Then
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

                    objRow.Cells.Add(objCell)
                Next

                tblMasterPlan.Rows.Add(objRow)
            Next

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
        End Sub
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
        Private Function SaveSavingsPlan() As Boolean
            Dim objTextBox As TextBox
            Dim iEditMonth As Integer = 0
            Dim strPlanValue As String = String.Empty
            Dim strStretchValue As String = String.Empty
            Dim strDate As String = String.Empty

            Try
                Select Case SessionManager.TrackerSelEditMode.ToUpper
                    Case "MONTH"
                        iEditMonth = SessionManager.TrackerSelEditMonth
                        strDate = RegionalConversion.FormatSQLDate(SessionManager.TrackerSelNavYear.ToString & "/" & iEditMonth.ToString & "/01")

                        'Plan
                        objTextBox = CType(colControls(1), TextBox)
                        If IsNumeric(objTextBox.Text) Then
                            strPlanValue = RegionalConversion.FormatSQLSingle(objTextBox.Text.Trim)
                        Else
                            strPlanValue = ""
                        End If

                        'Stretch
                        objTextBox = CType(colControls(2), TextBox)
                        If IsNumeric(objTextBox.Text) Then
                            strStretchValue = RegionalConversion.FormatSQLSingle(objTextBox.Text.Trim)
                        Else
                            strStretchValue = ""
                        End If

                        If IsNumeric(strPlanValue) And Not IsNumeric(strStretchValue) Then
                            strStretchValue = strPlanValue
                        ElseIf IsNumeric(strStretchValue) And Not IsNumeric(strPlanValue) Then
                            strPlanValue = "0"
                        End If

                        TrackerPlanSavings.UpdatePlanByPeriod(SessionManager.SelectedValueTrackerPlanID, strDate, strPlanValue, strStretchValue)
                        RecordTransactionHistory.InsertRecordTransactionHistory("TrackerPlanMaster", SessionManager.SelectedValueTrackerPlanID.ToString, "Master Plan Savings Modified for " & strDate, SessionManager.UserID)
                    Case "PLAN"
                        iEditMonth = 0
                        For Each objTextBox In colControls
                            iEditMonth += 1
                            strDate = RegionalConversion.FormatSQLDate(SessionManager.TrackerSelNavYear.ToString & "/" & iEditMonth.ToString & "/01")

                            If IsNumeric(objTextBox.Text) Then
                                strPlanValue = RegionalConversion.FormatSQLSingle(objTextBox.Text.Trim)
                            Else
                                strPlanValue = ""
                            End If

                            TrackerPlanSavings.UpdatePlanSavingsByPeriod(SessionManager.SelectedValueTrackerPlanID, strDate, strPlanValue)
                            RecordTransactionHistory.InsertRecordTransactionHistory("TrackerPlanMaster", SessionManager.SelectedValueTrackerPlanID.ToString, "Plan Savings Modified for " & strDate, SessionManager.UserID)
                        Next
                    Case "STRETCH"
                        iEditMonth = 0
                        For Each objTextBox In colControls
                            iEditMonth += 1
                            strDate = RegionalConversion.FormatSQLDate(SessionManager.TrackerSelNavYear.ToString & "/" & iEditMonth.ToString & "/01")

                            If IsNumeric(objTextBox.Text) Then
                                strStretchValue = RegionalConversion.FormatSQLSingle(objTextBox.Text.Trim)
                            Else
                                strStretchValue = ""
                            End If

                            TrackerPlanSavings.UpdateStretchSavingsByPeriod(SessionManager.SelectedValueTrackerPlanID, strDate, strStretchValue)
                            RecordTransactionHistory.InsertRecordTransactionHistory("TrackerPlanMaster", SessionManager.SelectedValueTrackerPlanID.ToString, "Stretch Savings Modified for " & strDate, SessionManager.UserID)
                        Next
                End Select
            Catch ex As Exception

            End Try

            Return True
        End Function
#End Region

    End Class
End Namespace
