#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports System.Net.Mail
Imports WebApp.APlus.DataAccess.Connections
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class KPIValues2
        Inherits ApplicationBase

#Region " Private Constants"
        Private strDecSeperator As String = ""
        Private Shared ReadOnly FormName As String = "KPI Tracker"
        Private Shared ReadOnly ProgramName As String = "KPIValues2"
        Private colControls As New Collection
        Private colControlsCalcs As Collection
        Private Convert_to_Numeric_js As String = ""
        Private Convert_to_Numeric_Supress_Zero_js As String = ""
        Private Convert_to_String_js As String = ""
        Private Replace_Seperator_js As String = ""
        Private Truncate_to_2_Decimals_js As String = ""
        Private Calculate_Average_js As String = ""
        Private Calculate_Sum_js As String = ""
        Private Display_Value_js As String = ""
        Private strReCalcHeader_js As String = ""
        Private strReCalcBody_js As String = ""
        Private strReCalc_Calcs_js As String = ""
        Private strReCalcFooter_js As String = ""
        Private strSummaryType As String = "N"
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel"}
            Dim OutMessageArr() As String = {"", ""}

            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event)")
            Master.AddBodyAttribute("onkeydown", "javascript:EnterKeyScript(window.event, 'ReCalc()')")
        End Sub
        Private Sub LoadEditModeJavaScripts()
            Dim objTextBox As TextBox
            Dim iCounter As Integer
            Dim strNext As String
            Dim strPrevious As String

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

            LoadCalculationJavaScripts()
        End Sub
        Private Sub LoadCalculationJavaScripts()
            ClientScript.RegisterStartupScript(Me.GetType, "Convert_to_Numeric_js", Convert_to_Numeric_js)
            ClientScript.RegisterStartupScript(Me.GetType, "Convert_to_Numeric_Supress_Zero_js", Convert_to_Numeric_Supress_Zero_js)
            ClientScript.RegisterStartupScript(Me.GetType, "Convert_to_String_js", Convert_to_String_js)
            ClientScript.RegisterStartupScript(Me.GetType, "Truncate_to_2_Decimals_js", Truncate_to_2_Decimals_js)
            ClientScript.RegisterStartupScript(Me.GetType, "Display_Value_js", Display_Value_js)
            ClientScript.RegisterStartupScript(Me.GetType, "Calculate_Average_js", Calculate_Average_js)
            ClientScript.RegisterStartupScript(Me.GetType, "Calculate_Sum_js", Calculate_Sum_js)
            ClientScript.RegisterStartupScript(Me.GetType, "Replace_Seperator_js", Replace_Seperator_js)
            ClientScript.RegisterStartupScript(Me.GetType, "ReCalc", strReCalcHeader_js & strReCalcBody_js & vbCrLf & strReCalc_Calcs_js & strReCalcFooter_js & vbCrLf)
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
                ckDataEntryMode.Text = GetTranslationString("kpieditmode", ckDataEntryMode.Text)
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
            BuildJavaScripts()

            Master.EnableTeamLink = False

            If Not Page.IsPostBack Then
                If Not SessionManager.AllowMaintenanceEdit Then
                    btnCancel_Click(Nothing, Nothing)
                    Return
                End If

                Dim dtNow As DateTime = Now().AddMonths(-1)
                SessionManager.KPISelNavYear = dtNow.Year
                SessionManager.KPISelEditMode = dtNow.Month.ToString
                SessionManager.KPIMasterMode = "EditRow"

                ckDataEntryMode.Checked = SessionManager.KPIDataEntryMode
            End If

            MasterControl1.StoredProcedureParams.Add("@KPIID", SessionManager.SelectedValueKPIID)

            BindGrid()
            LoadEditModeJavaScripts()

            If Not colControls Is Nothing AndAlso colControls.Count > 0 Then
                CType(colControls(1), Control).Focus()
            End If
        End Sub
        Private Sub btnOK_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnOK.Click
            If Not SaveKPIValues() Then

                Return
            Else
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.KPISelEditMode)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueKPIID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.KPIMasterMode)

                Dim strProgram = "KPIMaster1"
                If SessionManager.CallingProgram.Trim.Length > 0 Then
                    strProgram = SessionManager.CallingProgram
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CallingProgram)
                End If

                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strProgram), False)
            End If
        End Sub
        Private Sub btnCancel_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnCancel.Click
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.KPISelEditMode)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueKPIID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.KPIMasterMode)

            Dim strProgram = "KPIMaster1"
            If SessionManager.CallingProgram.Trim.Length > 0 Then
                strProgram = SessionManager.CallingProgram
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CallingProgram)
            End If

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strProgram), False)
        End Sub
        Protected Sub ckDataEntryMode_CheckedChanged(ByVal sender As Object, ByVal e As System.EventArgs) Handles ckDataEntryMode.CheckedChanged
            SessionManager.KPIDataEntryMode = ckDataEntryMode.Checked

            If Not SessionManager.KPIDataEntryMode Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.KPISelEditMode)

                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPIValues1"), False)

                Return
            End If
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub BuildJavaScripts()
            strDecSeperator = System.Threading.Thread.CurrentThread.CurrentCulture.NumberFormat.NumberDecimalSeparator
            Dim cUserCulture As Globalization.CultureInfo
            cUserCulture = Globalization.CultureInfo.CreateSpecificCulture(Request.UserLanguages(0).ToString())
            Dim strClientSeperator As String = "."

            Convert_to_Numeric_js = "<SCRIPT LANGUAGE='JavaScript'>function Convert_to_Numeric(s) {if (s == '') {return 0} else {return Replace_Seperator(s) * 1};}</SCRIPT>" & vbCrLf
            Convert_to_Numeric_Supress_Zero_js = "<SCRIPT LANGUAGE='JavaScript'>function Convert_to_Numeric_Supress_Zero(s) {if (s == '') {return ''} else {return Replace_Seperator(s) * 1};}</SCRIPT>" & vbCrLf
            Replace_Seperator_js = "<SCRIPT LANGUAGE='JavaScript'>function Replace_Seperator(strValue) {var sVal; try {sVal = new String(strValue); if (sVal.length < 1) {return sVal;} sVal = sVal.replace('" & strDecSeperator & "','" & strClientSeperator & "'); } catch (exception) {}; return sVal;}" & "</SCRIPT>" & vbCrLf
            Convert_to_String_js = "<SCRIPT LANGUAGE='JavaScript'>function Convert_to_String(strValue) {strValue = strValue + ''; return strValue;}" & "</SCRIPT>" & vbCrLf
            Truncate_to_2_Decimals_js = "<SCRIPT LANGUAGE='JavaScript'>function Truncate_to_2_Decimals(strValue) {if (strValue.indexOf('.') != -1) {strValue = strValue.substring(0, strValue.indexOf('.') + 3)}; return strValue}" & "</SCRIPT>" & vbCrLf
            Calculate_Average_js = "<SCRIPT LANGUAGE='JavaScript'>function Avg() {var sum = 0;var count = 0;for(i = 0; i < arguments.length; i++) {var fField = arguments[i];if(!(isNaN(fField))){if(fField.toString() != '') {sum += Number(fField); count++;}}} if(count != 0) {return sum / count;} else {return '';}}" & "</SCRIPT>" & vbCrLf
            Calculate_Sum_js = "<SCRIPT LANGUAGE='JavaScript'>function CalcSum() {var sum = '';for(i = 0; i < arguments.length; i++) {var fField = arguments[i];if(!(isNaN(fField))){if(fField.toString() != '') {if(sum == ''){sum = Number(fField);} else{sum += Number(fField)}}}} return sum; }" & "</SCRIPT>" & vbCrLf
            Display_Value_js = "<SCRIPT LANGUAGE='JavaScript'>function Display_Value(strValue) {if (strValue == 'Infinity' || strValue == 'NaN' || strValue == 'undefined') {strValue = ''}; return strValue.replace('" & strClientSeperator & "','" & strDecSeperator & "');}" & "</SCRIPT>" & vbCrLf
            strReCalcHeader_js = "<SCRIPT LANGUAGE='JavaScript'>function ReCalc() { " & vbCrLf
            strReCalcFooter_js = "}</SCRIPT>"
        End Sub
        Private Sub BindGrid()
            MasterControl1.DataBind(True)

            tblKPIValues.Rows.Clear()

            Dim cnMasterConnection As SqlConnection = ApplicationConnection.OpenMasterConnection()
            Dim objDT As DataTable = Nothing

            objDT = KPIMaster.SelectKPIMasterByID(SessionManager.SelectedValueKPIID, cnMasterConnection)
            If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                strSummaryType = objDT.Rows(0)("SummaryType").ToString.ToUpper
            End If

            'determine if VIEW or EDIT mode
            Dim blnVIEWMode As Boolean = True
            If SessionManager.KPIMasterMode = "EditRow" Then
                Dim dtKPI As DataTable = KPIMaster.SelectKPIAccess(SessionManager.UserID, SessionManager.SelectedValueKPIID, cnMasterConnection)
                If dtKPI IsNot Nothing AndAlso dtKPI.Rows.Count = 1 Then
                    If Convert.ToBoolean(dtKPI.Rows(0)("AllowEdit")) Then
                        blnVIEWMode = False
                    End If
                End If
            End If

            If blnVIEWMode OrElse Not IsNumeric(SessionManager.KPISelEditMode) Then
                cnMasterConnection.Close()
                btnCancel_Click(Nothing, Nothing)
                Return
            End If

            objDT = KPIValues.SelectKPIValuesByIDYear(SessionManager.SelectedValueKPIID, SessionManager.KPISelNavYear, cnMasterConnection)
            If objDT Is Nothing OrElse objDT.Rows.Count = 0 Then
                cnMasterConnection.Close()
                Return
            End If

            Dim objRow As TableRow
            Dim objCell As TableCell
            Dim objTextBox As TextBox
            Dim lnkValue As LinkButton = Nothing
            Dim iMonth As Integer = Convert.ToInt16(SessionManager.KPISelEditMode)
            Dim iQuarter As Integer = 0
            Select Case iMonth
                Case 1, 2, 3
                    iQuarter = 1
                Case 4, 5, 6
                    iQuarter = 2
                Case 7, 8, 9
                    iQuarter = 3
                Case 10, 11, 12
                    iQuarter = 4
            End Select

            colControls = New Collection
            colControlsCalcs = New Collection

            'add top for year and nav buttons
            objRow = New TableRow
            objRow.Cells.Add(GenerateTableCell("", New Unit((100 / 15).ToString & "%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.None, ""))
            objRow.Cells.Add(GenerateTableCell(SessionManager.KPISelNavYear.ToString, New Unit((0).ToString & "%"), New Unit(0), "#41519A", "#ffffff", HorizontalAlign.Center, VerticalAlign.NotSet, 16, BorderStyle.None, ""))
            objRow.Cells.Add(GenerateTableCell("", New Unit((100 / 15).ToString & "%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.None, ""))
            tblKPIValues.Rows.Add(objRow)

            'add Month columns
            'add header columns
            objRow = New TableRow
            objRow.Cells.Add(GenerateTableCell("", New Unit("15%"), New Unit(15), "#FFFFFF", "#FFFFFF", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.Solid, ""))

            For i As Integer = 2 To 18
                objRow.Cells.Add(GenerateTableCell(objDT.Columns(i).ColumnName, New Unit("5%"), New Unit(15), "#FFFFFF", "#000000", HorizontalAlign.Center, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            Next

            tblKPIValues.Rows.Add(objRow)

            Dim strCategoryDisplayName As String = ""
            Dim intRowIndex As Int16 = 0
            Dim strAlternatingRowColor As String
            Dim objRegValid As RegularExpressionValidator
            Dim bTargetUp As Boolean = False

            For Each dtRow As DataRow In objDT.Rows
                bTargetUp = Convert.ToBoolean(dtRow("TargetUp"))

                intRowIndex += 1
                'values for this year
                objRow = New TableRow

                'alternating row color code
                If intRowIndex Mod 2 = 0 Then
                    strAlternatingRowColor = "#CCCCCC"
                Else
                    strAlternatingRowColor = "#FFFFFF"
                End If

                objRow.Cells.Add(GenerateTableCell(dtRow("KPIType").ToString(), New Unit("15%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, dtRow("KPIType").ToString()))

                For i As Integer = 2 To 18
                    objCell = New TableCell
                    objCell.Width = New Unit("5%")
                    objCell.Height = New Unit(15)
                    objCell.HorizontalAlign = HorizontalAlign.Center
                    If intRowIndex Mod 2 = 0 Then
                        objCell.BackColor = System.Drawing.ColorTranslator.FromHtml("#CCCCCC")
                    Else
                        objCell.BackColor = System.Drawing.ColorTranslator.FromHtml("#FFFFFF")
                    End If

                    If dtRow("KPIType").ToString() = "Value" Then
                        objCell.HorizontalAlign = HorizontalAlign.Center
                        objCell.BorderStyle = BorderStyle.Solid
                        objTextBox = New TextBox
                        objTextBox.Width = New Unit("90%")
                        objTextBox.Height = New Unit("90%")
                        objTextBox.ID = "txt" & objDT.Columns(i).ColumnName
                        objTextBox.Attributes.Add("tag", (i - 1).ToString)
                        objTextBox.MaxLength = 12
                        objTextBox.BorderStyle = BorderStyle.Solid
                        objTextBox.BorderWidth = New Unit(1)
                        If dtRow(i) Is DBNull.Value OrElse Not IsNumeric(dtRow(i)) Then
                            objTextBox.Text = ""
                        Else
                            objTextBox.Text = CDbl(dtRow(i)).ToString("0.##")
                        End If

                        If (i = (iMonth + 1) OrElse (strSummaryType = "N" AndAlso (i = (iQuarter + 13) OrElse i = 18))) Then
                            objTextBox.CssClass = "Textbox_Entry_Center"
                            objTextBox.Attributes.Add("onFocus", "this.select();")
                            objTextBox.Attributes.Add("onchange", "ReCalc();")

                            colControls.Add(objTextBox, objTextBox.ID)

                            objRegValid = New RegularExpressionValidator
                            objRegValid.ID = "Reg" & objTextBox.ID
                            objRegValid.ControlToValidate = objTextBox.ID
                            objRegValid.Display = ValidatorDisplay.None
                            objRegValid.ValidationExpression = "(-?\d{0,7}\" & strDecSeperator & "{1}\d{0,4})|(-?\d{0,10})"
                            objRegValid.ErrorMessage = "Invalid KPI " & dtRow("KPIType").ToString()
                            objCell.Controls.Add(objRegValid)
                        ElseIf strSummaryType = "S" AndAlso (i = (iQuarter + 13) OrElse i = 18) Then
                            objTextBox.CssClass = "Textbox_Display_Center"
                            objTextBox.Attributes.Add("readonly", "readonly")
                            GenerateSumCalcJavaScript(objDT.Columns(i).ColumnName, objTextBox.ID)
                            objTextBox.ToolTip += " (you may not change the value in this calculated cell)"
                            colControlsCalcs.Add(objTextBox, objTextBox.ID)
                        ElseIf strSummaryType = "A" AndAlso (i = (iQuarter + 13) OrElse i = 18) Then
                            objTextBox.CssClass = "Textbox_Display_Center"
                            objTextBox.Attributes.Add("readonly", "readonly")
                            GenerateAvgCalcJavaScript(objDT.Columns(i).ColumnName, objTextBox.ID)
                            objTextBox.ToolTip += " (you may not change the value in this calculated cell)"
                            colControlsCalcs.Add(objTextBox, objTextBox.ID)
                        Else
                            objTextBox.CssClass = "Textbox_Display_Center"
                            objTextBox.Attributes.Add("readonly", "readonly")
                            objTextBox.ToolTip += " (this cell is read only)"
                        End If

                        objCell.Controls.Add(objTextBox)
                    Else
                        objCell.BorderStyle = BorderStyle.Solid
                        If Not dtRow(i) Is DBNull.Value AndAlso IsNumeric(dtRow(i)) Then
                            objCell.Text = CDbl(dtRow(i)).ToString("0.##")
                        End If
                    End If

                    objRow.Cells.Add(objCell)
                Next

                tblKPIValues.Rows.Add(objRow)
            Next

            cnMasterConnection.Close()
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
        Private Sub GenerateAvgCalcJavaScript(ByRef strColumnName As String, ByVal strTextboxID As String)
            Try
                Dim strFormula As String = ""
                'all this JS code is to 
                '1) truncate the result to 2 decimal position. i.e. 3.777666 to 3.77
                '2) change the JS value 'NaN' (Not-a-Number) and 'Infinity' (result of division by 0) to 0 so the db doesn't complain
                strReCalc_Calcs_js += vbCrLf & vbTab & "//this is the calculation javascript for column '" & strColumnName & "'" & vbCrLf & vbTab & _
                "var " & strTextboxID & ";" & vbCrLf & vbTab & vbTab

                Select Case strColumnName
                    Case "Q1"
                        strFormula = "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtJan').value),"
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtFeb').value),"
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtMar').value)"
                    Case "Q2"
                        strFormula = "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtApr').value),"
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtMay').value),"
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtJun').value)"
                    Case "Q3"
                        strFormula = "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtJul').value),"
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtAug').value),"
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtSep').value)"
                    Case "Q4"
                        strFormula = "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtOct').value),"
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtNov').value),"
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtDec').value)"
                    Case "YTD"
                        strFormula = "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtJan').value),"
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtFeb').value),"
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtMar').value),"
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtApr').value),"
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtMay').value),"
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtJun').value),"
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtJul').value),"
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtAug').value),"
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtSep').value),"
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtOct').value),"
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtNov').value),"
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtDec').value)"
                End Select

                strReCalc_Calcs_js += strTextboxID & " = " & "Avg(" & strFormula & "); " & vbCrLf & vbTab & vbTab
                strReCalc_Calcs_js += strTextboxID & " = Convert_to_String(" & strTextboxID & "); " & vbCrLf & vbTab & vbTab & _
                strTextboxID & " = Truncate_to_2_Decimals(" & strTextboxID & "); " & vbCrLf & vbTab & vbTab & _
                strTextboxID & " = Display_Value(" & strTextboxID & ");" & vbCrLf & vbTab & vbTab
                strReCalc_Calcs_js += "document.getElementById('ctl00_ContentPlaceHolder1_" & strTextboxID & "').value = " & strTextboxID & ";" & vbCrLf & vbCrLf & vbTab
            Catch Exc As Exception
                Throw
            End Try
        End Sub
        Private Sub GenerateSumCalcJavaScript(ByRef strColumnName As String, ByVal strTextboxID As String)
            Try
                Dim strFormula As String = ""
                'all this JS code is to 
                '1) truncate the result to 2 decimal position. i.e. 3.777666 to 3.77
                '2) change the JS value 'NaN' (Not-a-Number) and 'Infinity' (result of division by 0) to 0 so the db doesn't complain
                strReCalc_Calcs_js += vbCrLf & vbTab & "//this is the calculation javascript for column '" & strColumnName & "'" & vbCrLf & vbTab & _
                "var " & strTextboxID & ";" & vbCrLf & vbTab & vbTab

                Select Case strColumnName
                    Case "Q1"
                        strFormula = "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtJan').value), "
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtFeb').value), "
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtMar').value)"
                    Case "Q2"
                        strFormula = "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtApr').value), "
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtMay').value), "
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtJun').value)"
                    Case "Q3"
                        strFormula = "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtJul').value), "
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtAug').value), "
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtSep').value)"
                    Case "Q4"
                        strFormula = "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtOct').value) + "
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtNov').value) + "
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtDec').value)"
                    Case "YTD"
                        strFormula = "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtJan').value), "
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtFeb').value), "
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtMar').value), "
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtApr').value), "
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtMay').value), "
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtJun').value), "
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtJul').value), "
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtAug').value), "
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtSep').value), "
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtOct').value), "
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtNov').value), "
                        strFormula += "Convert_to_Numeric_Supress_Zero(document.getElementById('ctl00_ContentPlaceHolder1_txtDec').value)"
                End Select
                strReCalc_Calcs_js += strTextboxID & " = " & "CalcSum(" & strFormula & "); " & vbCrLf & vbTab & vbTab
                strReCalc_Calcs_js += strTextboxID & " = Convert_to_String(" & strTextboxID & "); " & vbCrLf & vbTab & vbTab & _
                strTextboxID & " = Truncate_to_2_Decimals(" & strTextboxID & "); " & vbCrLf & vbTab & vbTab & _
                strTextboxID & " = Display_Value(" & strTextboxID & ");" & vbCrLf & vbTab & vbTab
                strReCalc_Calcs_js += "document.getElementById('ctl00_ContentPlaceHolder1_" & strTextboxID & "').value = " & strTextboxID & ";" & vbCrLf & vbCrLf & vbTab
            Catch Exc As Exception
                Throw
            End Try
        End Sub
        Private Function SaveKPIValues() As Boolean
            Dim objTextBox As TextBox
            Dim iColIndex As Integer
            Dim iEditMonth As Integer = 0
            Dim iMaxValueMonth As Integer = 0
            Dim strMaxValueDate As String = ""
            Dim strValueType As String = ""
            Dim strDate As String = ""
            Dim strValue As String = ""
            Dim strLogValue As String = ""
            Dim cnMasterConnection As SqlConnection = Nothing

            Try
                cnMasterConnection = ApplicationConnection.OpenMasterConnection()

                iColIndex = 0
                iEditMonth = 0

                If colControls.Count = 1 Then
                    For Each objTextBox In colControlsCalcs
                        colControls.Add(objTextBox)
                    Next
                End If

                For Each objTextBox In colControls
                    iColIndex += 1

                    If IsNumeric(objTextBox.Attributes("tag").ToString) Then
                        iEditMonth = Convert.ToInt16(objTextBox.Attributes("tag").ToString)
                    Else
                        Exit For
                    End If

                    Select Case iEditMonth
                        Case 13
                            iEditMonth = 3
                            strValueType = "Q"
                        Case 14
                            iEditMonth = 6
                            strValueType = "Q"
                        Case 15
                            iEditMonth = 9
                            strValueType = "Q"
                        Case 16
                            iEditMonth = 12
                            strValueType = "Q"
                        Case 17
                            iEditMonth = 12
                            strValueType = "Y"
                        Case Else
                            strValueType = "M"
                    End Select
                    strDate = RegionalConversion.FormatSQLDate(SessionManager.KPISelNavYear.ToString & "/" & iEditMonth.ToString & "/01")

                    If IsNumeric(objTextBox.Text) Then
                        strValue = RegionalConversion.FormatSQLSingle(objTextBox.Text.Trim)

                        If iEditMonth <= 12 AndAlso strValueType = "M" AndAlso SessionManager.KPISelNavYear = DateTime.Now.Year Then
                            iMaxValueMonth = iEditMonth
                            strMaxValueDate = strDate
                        End If
                    Else
                        strValue = ""
                    End If

                    If iColIndex > 1 Then
                        strLogValue += "|"
                    End If
                    strLogValue += strValue.Trim

                    CheckKPIDeviation(strDate, strValue, strValueType)

                    KPIValues.UpdateKPIValues(SessionManager.SelectedValueKPIID, strDate, strValueType, strValue, cnMasterConnection)
                Next

                If iMaxValueMonth > 0 AndAlso strSummaryType <> "N" Then
                    If iMaxValueMonth >= Now().AddMonths(-1).Month AndAlso Not String.IsNullOrEmpty(strMaxValueDate) Then
                        KPIValues.UpdateKPITargetYTD(SessionManager.SelectedValueKPIID, strMaxValueDate)
                    ElseIf iMaxValueMonth < Now().AddMonths(-1).Month AndAlso SessionManager.KPISelNavYear = DateTime.Now.Year Then
                        strMaxValueDate = RegionalConversion.FormatSQLDate(SessionManager.KPISelNavYear.ToString & "/" & Now().AddMonths(-1).Month.ToString & "/01")
                        KPIValues.UpdateKPITargetYTD(SessionManager.SelectedValueKPIID, strMaxValueDate)
                    End If
                End If

                If strLogValue.Trim.Length > 0 Then
                    RecordTransactionHistory.InsertRecordTransactionHistory("KPIValues", SessionManager.SelectedValueKPIID.ToString, SessionManager.KPISelEditMode & " " & SessionManager.KPISelNavYear.ToString & ": " & strLogValue, SessionManager.UserID, cnMasterConnection)
                End If

                Return True
            Catch ex As Exception
            Finally
                If cnMasterConnection IsNot Nothing AndAlso cnMasterConnection.State <> ConnectionState.Closed Then
                    cnMasterConnection.Close()
                End If
            End Try
        End Function
        Private Sub CheckKPIDeviation(ByVal passDate As String, ByVal passValue As String, ByVal passValueType As String)
            If IsDate(passDate) AndAlso IsNumeric(passValue) AndAlso (passValueType = "M" OrElse passValueType = "Y") Then
                'If Current or Previous Month
                If DateDiff(DateInterval.Month, CDate(passDate), CDate(DateTime.Now().Year & "/" & DateTime.Now().Month & "/01")) = 0 OrElse _
                DateDiff(DateInterval.Month, CDate(passDate), CDate(DateTime.Now().Year & "/" & DateTime.Now().Month & "/01").AddMonths(-1)) = 0 OrElse _
                passValueType = "Y" Then
                    Dim objDT As DataTable = KPIValues.SelectKPIValuesByDate(SessionManager.SelectedValueKPIID, passDate, passValueType)

                    If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 AndAlso objDT.Rows(0).Item("KPITarget") IsNot DBNull.Value Then
                        Dim dtRow As DataRow = objDT.Rows(0)
                        Dim sTarget As Single = dtRow("KPITarget")
                        Dim bCreateAnomaly As Boolean = False
                        Dim bTargetUp As Boolean = dtRow("TargetUp")
                        Dim sValue As Single = RegionalConversion.FormatLocalSingle(passValue)
                        Dim sCulture As String = dtRow("CultureCode").ToString.Trim.ToLower

                        If bTargetUp Then
                            If sValue < sTarget Then
                                bCreateAnomaly = True
                            End If
                        Else
                            If sValue > sTarget Then
                                bCreateAnomaly = True
                            End If
                        End If

                        If bCreateAnomaly Then
                            Dim strSubject As String = ""
                            Dim strBody As String = ""
                            Dim strURL As String = ""

                            'Only send deviation email for Monthly Value
                            If passValueType = "M" Then
                                strSubject = dtRow("KPI").ToString & ": " & CultureTranslation.GetTranslationString(sCulture, "targetnotmetmonth", "Monthly Value does not meet Target")
                                strBody = strSubject & "<br />" & CultureTranslation.GetTranslationString(sCulture, "value", "Value") & " = " & sValue
                                strBody += ", " & CultureTranslation.GetTranslationString(sCulture, "target", "Target") & " = " & sTarget
                                strBody += ", " & CultureTranslation.GetTranslationString(sCulture, "period", "Period") & " = " & passDate
                                strBody += "<br /><br />"

                                strURL = "http://" & ConfigurationManager.AppSettings("ApplicationServerDNS").ToString & "/aplus/login.aspx"
                                strURL += "?auto=y&kpi=" & SessionManager.SelectedValueKPIID.ToString
                                strBody += "<a href='" & strURL & "'>" & GetTranslationString("Click Here to view KPI") & ": " & dtRow("KPI").ToString & "</a>"

                                SendAnomalyEmail(strSubject, strBody, "")
                            Else
                                strSubject = dtRow("KPI").ToString & ": " & CultureTranslation.GetTranslationString(sCulture, "targetnotmetytd", "YTD Value does not meet Target")
                            End If

                            If (passValueType = "M" AndAlso dtRow("AutoGenerateAnomalyMonth")) _
                            OrElse (passValueType = "Y" AndAlso dtRow("AutoGenerateAnomalyYTD")) Then
                                strBody = strSubject & " " & CultureTranslation.GetTranslationString(sCulture, "value", "Value") & " = " & sValue
                                strBody += " " & CultureTranslation.GetTranslationString(sCulture, "target", "Target") & " = " & sTarget

                                If passValueType = "M" Then
                                    strBody += " " & CultureTranslation.GetTranslationString(sCulture, "period", "Period") & " = " & passDate
                                ElseIf passValueType = "Y" Then
                                    strBody += " " & CultureTranslation.GetTranslationString(sCulture, "period", "Period") & " = " & Convert.ToDateTime(passDate).Year.ToString
                                    passDate = DateTime.Now.Year.ToString & "/" & DateTime.Now.Month.ToString & "/01"
                                End If

                                Dim dtAnomaly As DataTable = AnomalyMaster.SelectAnomalyMasterByKPI(SessionManager.SelectedValueKPIID, passDate, passValueType)
                                If dtAnomaly IsNot Nothing AndAlso dtAnomaly.Rows.Count > 0 Then
                                    'Anomaly already exists for this period, skip out
                                    Return
                                End If

                                Dim iAnomalyID As Integer = AnomalyMaster.AddAnomaly(dtRow("KPI").ToString, 1, dtRow("SiteID"), dtRow("AreaID"), strBody, SessionManager.SelectedValueKPIID, passDate, passValueType, RegionalConversion.FormatSQLDate(Now(), True), SessionManager.UserID, dtRow("AnomalyResponsibleUserID").ToString, 0, 0, 0, "", "", False, "", "", False, True)
                                If iAnomalyID > 0 Then
                                    strBody += "<br /><br />"
                                    strURL = "http://" & ConfigurationManager.AppSettings("ApplicationServerDNS").ToString & "/aplus/login.aspx"
                                    strURL += "?auto=y&anomaly=" & iAnomalyID.ToString
                                    strBody += "<a href='" & strURL & "'>" & GetTranslationString("Click Here to view Anomaly") & ": " & dtRow("KPI").ToString & "</a>"

                                    SendAnomalyEmail(CultureTranslation.GetTranslationString(sCulture, "anomalycreated", "Anomaly Created") & " : " & strSubject, strBody, dtRow("AnomalyResponsibleUserID").ToString)
                                End If
                            End If
                        End If
                    End If
                End If
            End If
        End Sub
        Private Sub SendAnomalyEmail(ByVal passSubject As String, ByVal passBody As String, ByVal passResponsibleUserID As String)
            Try
                Dim strbTo As New System.Text.StringBuilder
                Dim hEmail As New Hashtable
                Dim strEmail As String = ""
                If passResponsibleUserID.Trim.Length > 0 Then
                    strEmail = UserMaster.GetUserEmail(passResponsibleUserID)
                    hEmail.Add(strEmail, strEmail)
                Else
                    Dim objDT As DataTable = KPIUserNotifications.SelectKPIUserNotificationDeviation(SessionManager.SelectedValueKPIID)
                    For Each dtrow As DataRow In objDT.Rows
                        Try
                            hEmail.Add(dtrow("EmailAddress").ToString.Trim, dtrow("EmailAddress").ToString.Trim)
                        Catch ex As Exception
                        End Try
                    Next
                End If

                Dim myEnumerator As IDictionaryEnumerator = hEmail.GetEnumerator()
                While myEnumerator.MoveNext
                    strEmail = myEnumerator.Key.ToString
                    strEmail.Replace(" ", "_")

                    If strbTo.Length > 0 Then
                        strbTo.Append(", " & strEmail)
                    Else
                        strbTo.Append(strEmail)
                    End If
                End While

                If strbTo.Length > 0 Then
                    Dim MailClient As New SmtpClient
                    Dim strSendEmailFrom As String = ConfigurationManager.AppSettings("SendEmailFrom")
                    Dim msg As New MailMessage(strSendEmailFrom, strbTo.ToString.Trim, passSubject, passBody)
                    MailClient.Host = ConfigurationManager.AppSettings("SMTPServer")
                    msg.IsBodyHtml = True

                    MailClient.Send(msg)
                End If
            Catch ex As Exception

            End Try
        End Sub
#End Region

    End Class
End Namespace
