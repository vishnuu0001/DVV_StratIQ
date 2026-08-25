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
    Partial Class KPIDailyValues1
        Inherits ApplicationBase

#Region " Members / Variables"
        Private strDecSeperator As String = ""
        Private Shared ReadOnly FormName As String = "KPI Daily Values"
        Private Shared ReadOnly ProgramName As String = "KPIDailyValues1"
        Private colControls As Collection
        Private strSummaryType As String = "N"
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnExit}
            Dim OverMessageArr() As String = {"Exit"}
            Dim OutMessageArr() As String = {""}

            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnExit.UniqueID + "'),window.event)")
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
                btnExit.Text = GetTranslationString("exit", btnExit.Text)
                btnExport.Text = GetTranslationString("export", btnExport.Text)
                btnRunReport1.Text = GetTranslationString("kpireport1", btnRunReport1.Text)
                btnRunReport2.Text = GetTranslationString("kpireport2", btnRunReport2.Text)
                btnKPIDaily.Text = GetTranslationString("kpishowmonth", btnKPIDaily.Text)
                lblComments.Text = GetTranslationString("kpivaluecomments", lblComments.Text)
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

            If Not Page.IsPostBack Then
                If Not SessionManager.KPIDataEntryDaily OrElse Not KPIMaster.IsKPIDaily(SessionManager.SelectedValueKPIID) Then
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPIValues1"), False)
                    Return
                End If
            End If

            Master.IconImage = Request.ApplicationPath & "/images/TeamAction.gif"
            Master.HeaderMessage = GetTranslationString(FormName, FormName)
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/" & SessionManager.CulturePref & "/DataEntry.js")

            LoadCommonJavaScripts()
            LoadCultureTranslations()

            If SessionManager.KPISelNavYear = 0 Then
                SessionManager.KPISelNavYear = Now.Year
            End If

            If SessionManager.KPISelEditMode.Trim.Length = 0 Then
                pnlOKCancel.Visible = False
                pnlExit.Visible = True
                Master.EnableTeamLink = True
            Else
                pnlOKCancel.Visible = True
                pnlExit.Visible = False
            End If

            If Not Page.IsPostBack Then
                TransactionHistory1.TableName = "KPIDailyValues"
                TransactionHistory1.RecordID = SessionManager.SelectedValueKPIID.ToString

                If SessionManager.AllowMaintenanceEdit Then
                    Dim dtKPI As DataTable = KPIMaster.SelectKPIAccess(SessionManager.UserID, SessionManager.SelectedValueKPIID)
                    If dtKPI IsNot Nothing AndAlso dtKPI.Rows.Count = 1 Then
                        If Convert.ToBoolean(dtKPI.Rows(0)("AllowEdit")) Then
                            SessionManager.KPIMasterMode = "EditRow"
                            btnKPIMaintenance.Visible = True
                        End If
                    End If
                End If
            End If

            MasterControl1.StoredProcedureParams.Add("@KPIID", SessionManager.SelectedValueKPIID)

            BindData()
        End Sub
        Private Sub Button_Click(ByVal sender As System.Object, ByVal e As WebControls.CommandEventArgs)
            Dim strTarget() As String
            strTarget = (CType(sender, LinkButton).ID).ToString.Split("~")
            Dim strProgram As String = ""

            Select Case strTarget(0)
                Case "Nav"
                    If Convert.ToInt16(strTarget(1)) = 12 AndAlso SessionManager.KPISelNavMonth = 1 Then
                        SessionManager.KPISelNavYear -= 1
                    ElseIf Convert.ToInt16(strTarget(1)) = 1 AndAlso SessionManager.KPISelNavMonth = 12 Then
                        SessionManager.KPISelNavYear += 1
                    End If

                    SessionManager.KPISelNavMonth = strTarget(1)
                Case "Daily"
                    SessionManager.KPISelEditMode = "Daily"
                Case "MTD"
                    SessionManager.KPISelEditMode = "MTD"
            End Select

            If SessionManager.KPISelEditMode = "" Then
                TransactionHistory1.Visible = True

                pnlOKCancel.Visible = False
                pnlExit.Visible = True
                Master.EnableTeamLink = True
            Else
                TransactionHistory1.Visible = False

                txtExpandComments.ReadOnly = False
                txtExpandComments.CssClass = "Textbox_Entry"

                pnlOKCancel.Visible = True
                pnlExit.Visible = False

                Master.EnableTeamLink = False
            End If

            BindData()
            LoadEditModeJavaScripts()

            If Not colControls Is Nothing AndAlso colControls.Count > 0 Then
                CType(colControls(1), Control).Focus()
            End If
        End Sub
        Private Sub TeamButton_Click(ByVal sender As System.Object, ByVal e As WebControls.CommandEventArgs)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim strTarget() As String
            strTarget = (CType(sender, LinkButton).CommandArgument).ToString.Split("~")
            Dim strProgram As String = ""

            PushTeamOntoStack(SessionManager.SelectedTeamID, SessionManager.SelectedTeam, SessionManager.SelectedOPI, "KPIDailyValues1", SessionManager.CurrentMenuProgram)
            SessionManager.SelectedTeamID = strTarget(1)
            SessionManager.SelectedTeam = strTarget(2)
            SessionManager.SelectedTeamName = Teams.GetTeamName(SessionManager.SelectedTeamID)
            SessionManager.SelectedTeamAllowEdit = UserSiteMaster.SelectTeamAllowEdit(SessionManager.SelectedTeamID, SessionManager.UserID)
            Select Case strTarget(0)
                Case "Team"
                    SessionManager.SelectedOPI = ""
                    SessionManager.CurrentMenuProgram = "TeamBoardMenu"
                    strProgram = "TeamBoardMenu"
                Case "OPI"
                    SessionManager.SelectedOPI = strTarget(3)
                    strProgram = "TeamOPIReports2"
            End Select

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strProgram), False)
        End Sub
        Protected Sub btnOK_Click(sender As Object, e As System.EventArgs) Handles btnOK.Click
            If Not SaveKPIValues() Then

                Return
            Else
                SessionManager.KPISelEditMode = ""

                txtExpandComments.ReadOnly = True
                txtExpandComments.CssClass = "Textbox_Display"

                pnlOKCancel.Visible = False
                pnlExit.Visible = True
                Master.EnableTeamLink = True
                TransactionHistory1.CollapseAll()
                TransactionHistory1.Visible = True

                BindData()
            End If
        End Sub
        Protected Sub btnCancel_Click(sender As Object, e As System.EventArgs) Handles btnCancel.Click
            SessionManager.KPISelEditMode = ""

            txtExpandComments.ReadOnly = True
            txtExpandComments.CssClass = "Textbox_Display"

            pnlOKCancel.Visible = False
            pnlExit.Visible = True
            Master.EnableTeamLink = True
            TransactionHistory1.CollapseAll()
            TransactionHistory1.Visible = True

            BindData()
        End Sub
        Protected Sub btnRunReport1_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnRunReport1.Click
            Try
                Dim strURL As String = Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & "UI/Pages/DataCollectionPrograms/WebReportPrintPreview.aspx"
                strURL += "?ReportKey=KPIReportSummary"
                strURL += "&ReportParams="
                strURL += "KPIID=" & SessionManager.SelectedValueKPIID.ToString
                strURL += "|KPIYear=" & SessionManager.KPISelNavYear.ToString

                ClientScript.RegisterStartupScript(Me.GetType, "ReportScript", "<script language='javascript'>window.open('" & strURL & "', '_blank')</script>")
            Catch ex As Exception

            End Try
        End Sub
        Protected Sub btnRunReport2_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnRunReport2.Click
            Try
                Dim strURL As String = Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & "UI/Pages/DataCollectionPrograms/WebReportPrintPreview.aspx"
                strURL += "?ReportKey=KPIReportSummaryBar"
                strURL += "&ReportParams="
                strURL += "KPIID=" & SessionManager.SelectedValueKPIID.ToString
                strURL += "|KPIYear=" & SessionManager.KPISelNavYear.ToString

                ClientScript.RegisterStartupScript(Me.GetType, "ReportScript", "<script language='javascript'>window.open('" & strURL & "', '_blank')</script>")
            Catch ex As Exception

            End Try
        End Sub
        Protected Sub btnRunReport3_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnRunReport3.Click
            Try
                Dim strURL As String = Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & "UI/Pages/DataCollectionPrograms/WebReportPrintPreview.aspx"
                strURL += "?ReportKey=KPIReportSummaryBar2"
                strURL += "&ReportParams="
                strURL += "KPIID=" & SessionManager.SelectedValueKPIID.ToString
                strURL += "|KPIPeriod=" & Format(Now, "yyyy/MM/01")

                ClientScript.RegisterStartupScript(Me.GetType, "ReportScript", "<script language='javascript'>window.open('" & strURL & "', '_blank')</script>")
            Catch ex As Exception

            End Try
        End Sub
        Protected Sub btnExport_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnExport.Click
            Dim stringWrite As New System.IO.StringWriter
            Dim htmlWrite As New System.Web.UI.HtmlTextWriter(stringWrite)
            Dim dg As New DataGrid
            dg.DataSource = KPIValues.SelectKPIValuesByIDYear(SessionManager.SelectedValueKPIID, SessionManager.KPISelNavYear)
            dg.DataBind()
            dg.RenderControl(htmlWrite)

            SessionManager.ExportString = stringWrite.ToString

            HttpContext.Current.Response.Redirect(HttpContext.Current.Request.ApplicationPath.ToString + "/UI/UserControls/Export.aspx")
        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueKPIID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.KPIMasterMode)

            Dim strProgram = "KPIMaster1"
            If SessionManager.CallingProgram.Trim.Length > 0 Then
                strProgram = SessionManager.CallingProgram
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CallingProgram)
            End If
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strProgram), False)
        End Sub
        Protected Sub btnKPIDaily_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnKPIDaily.Click
            SessionManager.KPIDataEntryDaily = False
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPIValues1"), False)
        End Sub
        Protected Sub btnKPIMaintenance_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnKPIMaintenance.Click
            SessionManager.CallingProgram = "KPIDailyValues1"
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPIMaster2"), False)
        End Sub
        Protected Sub mcAnomaly_onRowCommand(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewCommandEventArgs) Handles mcAnomaly.onRowCommand
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
                Case "ViewRow"
                    SessionManager.SelectedValueAnomalyID = mcAnomaly.MasterControlGrid.DataKeys(e.CommandArgument)("AnomalyID").ToString
                    If IsDate(mcAnomaly.MasterControlGrid.DataKeys(e.CommandArgument)("ClosedDateTime").ToString) Then
                        SessionManager.AnomalyMode = "ViewRow"
                    Else
                        SessionManager.AnomalyMode = "EditRow"
                    End If
                    SessionManager.MasterControlExitProgram = "KPIDailyValues1"

                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyActions1"), False)
            End Select
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub BindData()
            MasterControl1.DataBind(True)

            tblKPIValues.Rows.Clear()
            tblKPIDailyValues.Rows.Clear()

            Dim cnMasterConnection As SqlConnection = ApplicationConnection.OpenMasterConnection()

            BindValuesGrid(cnMasterConnection)
            BindDailyValuesGrid(cnMasterConnection)

            cnMasterConnection.Close()

            If SessionManager.KPISelEditMode.Trim.Length = 0 Then
                pnlTeamOPI.Visible = True
                BindTeamGrid()

                mcTrackers.StoredProcedureParams.Clear()
                mcTrackers.StoredProcedureParams.Add("@KPIID", SessionManager.SelectedValueKPIID)
                mcTrackers.DataBind(True)

                mcAnomaly.GridColumns(7).DataFormatString = "{0:yyyy/MM/dd}"
                mcAnomaly.GridColumns(9).DataFormatString = "{0:yyyy/MM/dd}"
                mcAnomaly.StoredProcedureParams.Clear()
                mcAnomaly.StoredProcedureParams.Add("@KPIID", SessionManager.SelectedValueKPIID)
                mcAnomaly.DataBind(True)
            Else
                pnlTeamOPI.Visible = False
            End If

        End Sub
        Private Sub BindValuesGrid(ByVal passConnection As SqlConnection)
            Dim objDT As DataTable = Nothing

            objDT = KPIValues.SelectKPIValuesByIDYear(SessionManager.SelectedValueKPIID, SessionManager.KPISelNavYear, passConnection)
            If objDT Is Nothing OrElse objDT.Rows.Count = 0 Then
                Return
            End If

            Dim objRow As TableRow
            Dim objCell As TableCell

            'add top for year and nav buttons
            objRow = New TableRow
            objRow.Cells.Add(GenerateTableCell("", New Unit("5%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.None, ""))
            objRow.Cells.Add(GenerateTableCell(SessionManager.KPISelNavYear.ToString, New Unit((0).ToString & "%"), New Unit(0), "#41519A", "#ffffff", HorizontalAlign.Center, VerticalAlign.NotSet, 17, BorderStyle.None, ""))
            objRow.Cells.Add(GenerateTableCell("", New Unit(0), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.None, ""))
            tblKPIValues.Rows.Add(objRow)

            'add Month columns
            'add header columns
            objRow = New TableRow
            objRow.Cells.Add(GenerateTableCell("", New Unit("5%"), New Unit(15), "#FFFFFF", "#FFFFFF", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            objRow.Cells.Add(GenerateTableCell("Prev", New Unit("5%"), New Unit(15), "#FFFFFF", "#000000", HorizontalAlign.Center, VerticalAlign.Top, 1, BorderStyle.Solid, ""))

            For i As Integer = 2 To 18
                objRow.Cells.Add(GenerateTableCell(objDT.Columns(i).ColumnName, New Unit("5%"), New Unit(15), "#FFFFFF", "#000000", HorizontalAlign.Center, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            Next

            tblKPIValues.Rows.Add(objRow)

            Dim strCategoryDisplayName As String = ""
            Dim intRowIndex As Int16 = 0
            Dim strAlternatingRowColor As String
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

                objRow.Cells.Add(GenerateTableCell(dtRow("KPIType").ToString(), New Unit("10%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, dtRow("KPIType").ToString()))

                If dtRow("Prev") Is DBNull.Value OrElse Not IsNumeric(dtRow("Prev").ToString) Then
                    objRow.Cells.Add(GenerateTableCell("", New Unit("5%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Center, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                Else
                    objRow.Cells.Add(GenerateTableCell(CDbl(dtRow("Prev")).ToString("0.##"), New Unit("5%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Center, VerticalAlign.NotSet, 1, BorderStyle.Solid, ""))
                End If

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

                    objCell.BorderStyle = BorderStyle.Solid
                    If Not dtRow(i) Is DBNull.Value AndAlso IsNumeric(dtRow(i)) Then
                        objCell.Text = CDbl(dtRow(i)).ToString("0.##")
                    End If

                    ' Business logic to override standard cell backcolor
                    ' only processed on the value row
                    If intRowIndex Mod 2 <> 0 Then
                        If IsNumeric(dtRow(i).ToString) Then
                            If IsNumeric(dtRow(i).ToString) AndAlso IsNumeric(objDT.Rows(intRowIndex)(i).ToString) AndAlso IsNumeric(dtRow("Prev").ToString) Then
                                If bTargetUp Then
                                    If CDbl(dtRow(i).ToString) >= CDbl(objDT.Rows(intRowIndex)(i).ToString) Then
                                        objCell.BackColor = Drawing.Color.LightGreen
                                    ElseIf CDbl(dtRow(i).ToString) > CDbl(dtRow("Prev").ToString) Then
                                        objCell.BackColor = Drawing.Color.Yellow
                                    Else
                                        objCell.BackColor = Drawing.Color.Salmon
                                    End If
                                Else
                                    If CDbl(dtRow(i).ToString) <= CDbl(objDT.Rows(intRowIndex)(i).ToString) Then
                                        objCell.BackColor = Drawing.Color.LightGreen
                                    ElseIf CDbl(dtRow(i).ToString) < CDbl(dtRow("Prev").ToString) Then
                                        objCell.BackColor = Drawing.Color.Yellow
                                    Else
                                        objCell.BackColor = Drawing.Color.Salmon
                                    End If
                                End If
                            ElseIf IsNumeric(dtRow(i).ToString) AndAlso IsNumeric(objDT.Rows(intRowIndex)(i).ToString) Then
                                If bTargetUp Then
                                    If CDbl(dtRow(i).ToString) >= CDbl(objDT.Rows(intRowIndex)(i).ToString) Then
                                        objCell.BackColor = Drawing.Color.LightGreen
                                    Else
                                        objCell.BackColor = Drawing.Color.Salmon
                                    End If
                                Else
                                    If CDbl(dtRow(i).ToString) <= CDbl(objDT.Rows(intRowIndex)(i).ToString) Then
                                        objCell.BackColor = Drawing.Color.LightGreen
                                    Else
                                        objCell.BackColor = Drawing.Color.Salmon
                                    End If
                                End If
                            ElseIf IsNumeric(dtRow(i).ToString) AndAlso IsNumeric(dtRow("Prev").ToString) Then
                                If bTargetUp Then
                                    If CDbl(dtRow(i).ToString) > CDbl(dtRow("Prev").ToString) Then
                                        objCell.BackColor = Drawing.Color.Yellow
                                    Else
                                        objCell.BackColor = Drawing.Color.Salmon
                                    End If
                                Else
                                    If CDbl(dtRow(i).ToString) < CDbl(dtRow("Prev").ToString) Then
                                        objCell.BackColor = Drawing.Color.Yellow
                                    Else
                                        objCell.BackColor = Drawing.Color.Salmon
                                    End If
                                End If
                            End If
                        End If
                    End If

                    objRow.Cells.Add(objCell)
                Next

                tblKPIValues.Rows.Add(objRow)
            Next
        End Sub
        Private Sub BindDailyValuesGrid(ByVal passConnection As SqlConnection)
            Dim objDT As DataTable = Nothing

            If SessionManager.KPISelNavMonth = 0 Then
                SessionManager.KPISelNavMonth = DateTime.Now.Month
            End If

            objDT = KPIValues.SelectKPIDailyValuesByDate(SessionManager.SelectedValueKPIID, SessionManager.KPISelNavYear, SessionManager.KPISelNavMonth, passConnection)
            If objDT Is Nothing OrElse objDT.Rows.Count = 0 Then
                Return
            End If

            Dim objRow As TableRow
            Dim objCell As TableCell
            Dim objTextBox As TextBox = Nothing
            Dim lnkValue As LinkButton = Nothing

            'determine if VIEW or EDIT mode
            Dim blnVIEWMode As Boolean = True
            If SessionManager.KPIMasterMode = "EditRow" Then
                Dim dtKPI As DataTable = KPIMaster.SelectKPIAccess(SessionManager.UserID, SessionManager.SelectedValueKPIID, passConnection)
                If dtKPI IsNot Nothing AndAlso dtKPI.Rows.Count = 1 Then
                    If Convert.ToBoolean(dtKPI.Rows(0)("AllowEdit")) Then
                        blnVIEWMode = False
                    End If
                End If
            End If

            colControls = New Collection

            Dim strMonth As String = Convert.ToDateTime(SessionManager.KPISelNavYear.ToString + "/" + SessionManager.KPISelNavMonth.ToString + "/01").ToString("MMM")
            Dim iPrevMonth As Integer = SessionManager.KPISelNavMonth - 1
            Dim iNextMonth As Integer = SessionManager.KPISelNavMonth + 1
            If SessionManager.KPISelNavMonth = 1 Then
                iPrevMonth = 12
            ElseIf SessionManager.KPISelNavMonth = 12 Then
                iNextMonth = 1
            End If

            If SessionManager.KPISelEditMode.Trim.Length > 0 AndAlso Not blnVIEWMode Then
            Else
                txtExpandComments.Text = KPIValues.SelectKPIValueComments(SessionManager.SelectedValueKPIID, SessionManager.KPISelNavYear.ToString + "/" + SessionManager.KPISelNavMonth.ToString + "/01", passConnection)
                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("Comments", txtExpandComments.Text.Trim())
                SessionManager.RecordTransactionCurrentValues = objDic
            End If

            'add top for year and nav buttons
            objRow = New TableRow
            If SessionManager.KPISelEditMode.Trim.Length > 0 AndAlso Not blnVIEWMode Then
                objRow.Cells.Add(GenerateTableCell("", New Unit("7%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.None, ""))
                objRow.Cells.Add(GenerateTableCell(strMonth, New Unit("100%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Center, VerticalAlign.NotSet, 30, BorderStyle.None, ""))
                objRow.Cells.Add(GenerateTableCell("", New Unit((90 / 31).ToString & "%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.None, ""))
            Else
                objRow.Cells.Add(GenerateTableCell("", New Unit("7%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.None, "", GenerateTableLink("<", "#E7E7FF", "Nav~" & iPrevMonth.ToString, "Previous Month")))
                objRow.Cells.Add(GenerateTableCell(strMonth, New Unit("100%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Center, VerticalAlign.NotSet, 30, BorderStyle.None, ""))
                objRow.Cells.Add(GenerateTableCell("", New Unit((90 / 31).ToString & "%"), New Unit(15), "#41519A", "#ffffff", HorizontalAlign.Right, VerticalAlign.Top, 1, BorderStyle.None, "", GenerateTableLink(" > ", "#E7E7FF", "Nav~" & iNextMonth.ToString, "Next Month")))
            End If
            tblKPIDailyValues.Rows.Add(objRow)

            'add header columns
            Dim dtHolder As DateTime = Nothing
            Dim strBackColor As String = String.Empty
            objRow = New TableRow
            objRow.Cells.Add(GenerateTableCell("", New Unit("7%"), New Unit(15), "#FFFFFF", "#FFFFFF", HorizontalAlign.Left, VerticalAlign.Top, 1, BorderStyle.Solid, ""))

            For i As Integer = 2 To 32
                If IsDate(SessionManager.KPISelNavYear.ToString + "/" + SessionManager.KPISelNavMonth.ToString + "/" + objDT.Columns(i).ColumnName.ToString) Then
                    dtHolder = Convert.ToDateTime(SessionManager.KPISelNavYear.ToString + "/" + SessionManager.KPISelNavMonth.ToString + "/" + objDT.Columns(i).ColumnName.ToString)
                    If dtHolder.DayOfWeek = DayOfWeek.Sunday Then
                        strBackColor = "#B0C4DE"
                    Else
                        strBackColor = "#FFFFFF"
                    End If
                Else
                    strBackColor = "#FFFFFF"
                End If

                objRow.Cells.Add(GenerateTableCell(objDT.Columns(i).ColumnName, New Unit((90 / 31).ToString & "%"), New Unit(15), strBackColor, "#000000", HorizontalAlign.Center, VerticalAlign.Top, 1, BorderStyle.Solid, ""))
            Next

            tblKPIDailyValues.Rows.Add(objRow)

            Dim intRowIndex As Int16 = 0
            Dim strAlternatingRowColor As String
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

                If SessionManager.KPISelEditMode = "" AndAlso Not blnVIEWMode Then
                    lnkValue = GenerateTableLink(dtRow("KPIType").ToString(), "#3333FF", dtRow("KPIType").ToString(), dtRow("KPIType").ToString())
                    objRow.Cells.Add(GenerateTableCell(dtRow("KPIType").ToString(), New Unit("7%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, "", lnkValue))
                Else
                    objRow.Cells.Add(GenerateTableCell(dtRow("KPIType").ToString(), New Unit("7%"), New Unit(5), strAlternatingRowColor, "#000000", HorizontalAlign.Left, VerticalAlign.NotSet, 1, BorderStyle.Solid, dtRow("KPIType").ToString()))
                End If

                For i As Integer = 2 To 32
                    objCell = New TableCell
                    objCell.Width = New Unit((90 / 31).ToString & "%")
                    objCell.Height = New Unit(15)
                    objCell.HorizontalAlign = HorizontalAlign.Center
                    If intRowIndex Mod 2 = 0 Then
                        objCell.BackColor = System.Drawing.ColorTranslator.FromHtml("#CCCCCC")
                    Else
                        objCell.BackColor = System.Drawing.ColorTranslator.FromHtml("#FFFFFF")
                    End If

                    If SessionManager.KPISelEditMode = dtRow("KPIType").ToString() Then
                        objCell.HorizontalAlign = HorizontalAlign.Center
                        objCell.BorderStyle = BorderStyle.Solid
                        objTextBox = New TextBox
                        objTextBox.Width = New Unit("87%")
                        objTextBox.Height = New Unit("90%")
                        objTextBox.ID = "txt" & objDT.Columns(i).ColumnName
                        objTextBox.MaxLength = 12
                        objTextBox.BorderStyle = BorderStyle.Solid
                        objTextBox.BorderWidth = New Unit(1)
                        If dtRow(i) Is DBNull.Value OrElse Not IsNumeric(dtRow(i)) Then
                            objTextBox.Text = ""
                        Else
                            objTextBox.Text = CDbl(dtRow(i)).ToString("0.##")
                        End If

                        objTextBox.CssClass = "Textbox_Entry_Center"
                        objTextBox.Attributes.Add("onFocus", "this.select();")

                        colControls.Add(objTextBox, objTextBox.ID)

                        objCell.Controls.Add(objTextBox)
                    Else
                        objCell.BorderStyle = BorderStyle.Solid
                        If Not dtRow(i) Is DBNull.Value AndAlso IsNumeric(dtRow(i)) Then
                            objCell.Text = CDbl(dtRow(i)).ToString("0.##")
                        Else
                            objCell.Text = "&nbsp;"
                        End If
                    End If

                    If SessionManager.KPISelEditMode <> "Value" Then
                        ' Business logic to override standard cell backcolor
                        If dtRow("DailyKPICompare") AndAlso IsNumeric(dtRow(i).ToString) AndAlso IsNumeric(dtRow("KPITarget").ToString) Then
                            If bTargetUp Then
                                If CDbl(dtRow(i).ToString) >= CDbl(dtRow("KPITarget").ToString) Then
                                    objCell.BackColor = Drawing.Color.LightGreen
                                Else
                                    objCell.BackColor = Drawing.Color.Salmon
                                End If
                            Else
                                If CDbl(dtRow(i).ToString) <= CDbl(dtRow("KPITarget").ToString) Then
                                    objCell.BackColor = Drawing.Color.LightGreen
                                Else
                                    objCell.BackColor = Drawing.Color.Salmon
                                End If
                            End If
                        End If
                    End If

                    objRow.Cells.Add(objCell)
                Next

                tblKPIDailyValues.Rows.Add(objRow)
            Next
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
        Private Sub BindTeamGrid()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                tblTeams.Rows.Clear()

                Dim objDS As DataTable = Teams.SelectKPITeamsOverview(SessionManager.UserID, SessionManager.SelectedValueKPIID)
                Dim objRow As TableRow
                Dim objCell As TableCell
                Dim objLink As LinkButton

                If objDS.Rows.Count > 0 Then
                    'create header
                    objRow = New TableRow

                    'fill in the cells
                    'Team
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objCell.Text = "Team"
                    objCell.Font.Bold = True
                    objRow.Cells.Add(objCell)

                    'Team Name
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objCell.Text = "Team Name"
                    objCell.Font.Bold = True
                    objRow.Cells.Add(objCell)

                    'Site
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objCell.Text = "Site"
                    objRow.Cells.Add(objCell)

                    'Pillar
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objCell.Text = "Pillar"
                    objRow.Cells.Add(objCell)

                    'Business Area
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objCell.Text = "BA"
                    objRow.Cells.Add(objCell)

                    'Business Unit
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objCell.Text = "BU"
                    objRow.Cells.Add(objCell)

                    'Route
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objCell.Text = "Route"
                    objRow.Cells.Add(objCell)

                    'Dept
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objCell.Text = "Dept"
                    objRow.Cells.Add(objCell)

                    'Start
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objCell.Text = "Start"
                    objRow.Cells.Add(objCell)

                    'Finish
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objCell.Text = "Finish"
                    objRow.Cells.Add(objCell)

                    'Duration
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objCell.Text = "Duration"
                    objRow.Cells.Add(objCell)

                    'Status
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objCell.Text = "Status"
                    objRow.Cells.Add(objCell)

                    'Team Type
                    objCell = New TableCell
                    objCell.CssClass = "Table_Teams3_Cell"
                    objCell.Text = "Type"
                    objRow.Cells.Add(objCell)
                    tblTeams.Rows.Add(objRow)
                End If

                Dim _status As Boolean = True
                For Each objDR As DataRow In objDS.Rows
                    'create row
                    objRow = New TableRow

                    'fill in the cells
                    'Team
                    objCell = New TableCell
                    objCell.Width = New Unit(75)
                    RowStyle(_status, objCell)
                    objLink = New LinkButton
                    AddHandler objLink.Command, AddressOf TeamButton_Click
                    objLink.Text = objDR("Team").ToString
                    objLink.ID = "Team~" + objDR("TeamID").ToString & "~" & objDR("Team").ToString
                    objLink.CommandArgument = "Team~" + objDR("TeamID").ToString & "~" & objDR("Team").ToString
                    objCell.Controls.Add(objLink)
                    objRow.Cells.Add(objCell)

                    'Team Name
                    objCell = New TableCell
                    objCell.Width = New Unit(275)
                    RowStyle(_status, objCell)
                    objCell.Text = objDR("TeamName").ToString
                    objRow.Cells.Add(objCell)

                    'Site
                    objCell = New TableCell
                    RowStyle(_status, objCell)
                    objCell.Text = objDR("Site").ToString
                    objRow.Cells.Add(objCell)

                    'Pillar
                    objCell = New TableCell
                    RowStyle(_status, objCell)
                    objCell.Text = objDR("PillarAbbrev").ToString
                    objRow.Cells.Add(objCell)

                    'Business Area
                    objCell = New TableCell
                    RowStyle(_status, objCell)
                    objCell.Text = objDR("BusinessAreaAbbrev").ToString
                    objRow.Cells.Add(objCell)

                    'Business Unit
                    objCell = New TableCell
                    RowStyle(_status, objCell)
                    objCell.Text = objDR("BusinessUnitAbbrev").ToString
                    objRow.Cells.Add(objCell)

                    'Route
                    objCell = New TableCell
                    RowStyle(_status, objCell)
                    objCell.Text = objDR("Route").ToString
                    objRow.Cells.Add(objCell)

                    'Dept
                    objCell = New TableCell
                    RowStyle(_status, objCell)
                    objCell.Text = objDR("DeptNumber").ToString
                    objRow.Cells.Add(objCell)

                    'Start
                    objCell = New TableCell
                    RowStyle(_status, objCell)
                    objCell.Text = objDR("TeamStartDate").ToString
                    objRow.Cells.Add(objCell)

                    'Finish
                    objCell = New TableCell
                    RowStyle(_status, objCell)
                    objCell.Text = objDR("TeamFinishDate").ToString
                    objRow.Cells.Add(objCell)

                    'Duration
                    objCell = New TableCell
                    RowStyle(_status, objCell)
                    objCell.Text = objDR("Duration").ToString
                    objRow.Cells.Add(objCell)

                    'Status
                    objCell = New TableCell
                    RowStyle(_status, objCell)
                    objCell.Text = objDR("TeamStatusDescription").ToString
                    objRow.Cells.Add(objCell)

                    'Team Type
                    objCell = New TableCell
                    RowStyle(_status, objCell)
                    objCell.Text = objDR("TeamType").ToString
                    objRow.Cells.Add(objCell)

                    tblTeams.Rows.Add(objRow)
                    Dim xCell As TableCell = objCell
                    If IsNumeric(objDR("OPICount").ToString) AndAlso Convert.ToInt16(objDR("OPICount")) > 0 Then
                        Dim dsOPI As DataTable = TeamOPI.SelectOPIsByTeam(objDR("TeamID"))
                        Dim OPITable As Table
                        Dim OPIRow As TableRow
                        Dim OPICell As TableCell
                        Dim strHolder As String

                        objRow = New TableRow
                        objCell = New TableCell
                        objCell.ColumnSpan = 13

                        OPITable = New Table
                        OPITable.Width = New Unit("100%")
                        OPITable.CellPadding = 0
                        OPITable.CellSpacing = 0

                        Dim _default As Boolean = False
                        For Each drOPI As DataRow In dsOPI.Rows
                            If xCell.CssClass = "Table_Teams3_DefaultRowStyle" Then
                                _default = True
                            End If
                            OPIRow = New TableRow

                            OPICell = New TableCell
                            OPICell.Width = New Unit(115)
                            RowStyle(_default, OPICell)
                            OPIRow.Cells.Add(OPICell)

                            OPICell = New TableCell
                            RowStyle(_default, OPICell)
                            OPICell.Width = New Unit(200)

                            objLink = New LinkButton
                            AddHandler objLink.Command, AddressOf TeamButton_Click
                            objLink.Text = drOPI("OPI").ToString
                            objLink.ID = "OPI~" & objDR("TeamID").ToString & "~" & objDR("Team").ToString & "~" & drOPI("OPI").ToString
                            objLink.CommandArgument = "OPI~" & objDR("TeamID").ToString & "~" & objDR("Team").ToString & "~" & drOPI("OPI").ToString
                            OPICell.Controls.Add(objLink)
                            OPIRow.Cells.Add(OPICell)

                            OPICell = New TableCell
                            RowStyle(_default, OPICell)
                            strHolder = UserMaster.GetUserFullNameLastNameFirst(drOPI("ResponsibleUser").ToString)
                            If strHolder.Trim.Length = 0 Then
                                strHolder = drOPI("ResponsibleUser").ToString
                            End If
                            If strHolder.Trim.Length = 0 Then
                                strHolder = "&nbsp;"
                            End If
                            OPICell.Text = strHolder
                            OPIRow.Cells.Add(OPICell)
                            OPITable.Rows.Add(OPIRow)
                        Next drOPI

                        objCell.Controls.Add(OPITable)
                        objRow.Cells.Add(objCell)
                        tblTeams.Rows.Add(objRow)
                    End If
                    If _status = True Then
                        _status = False
                    Else
                        _status = True
                    End If
                Next objDR
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindGrid", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
            End Try
        End Sub
        Private Sub RowStyle(ByVal passDefault As Boolean, ByRef passObj As TableCell)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If passDefault Then
                passObj.CssClass = "Table_Teams3_DefaultRowStyle"
            Else
                passObj.CssClass = "Table_Teams3_AlternatingRowStyle"
            End If
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

                'KPI Comments
                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("Comments", txtExpandComments.Text.Trim())
                Dim strChangeLog As String = TransactionProcessing.CompareDictionaryValues(SessionManager.RecordTransactionCurrentValues, objDic)

                If Not String.IsNullOrEmpty(strChangeLog) Then
                    KPIValues.UpdateKPIValueComments(SessionManager.SelectedValueKPIID, RegionalConversion.FormatSQLDate(SessionManager.KPISelNavYear.ToString & "/" & SessionManager.KPISelNavMonth.ToString & "/01"), txtExpandComments.Text.Trim, cnMasterConnection)
                    RecordTransactionHistory.InsertRecordTransactionHistory("KPIDailyValues", SessionManager.SelectedValueKPIID.ToString, SessionManager.KPISelNavYear.ToString & "/" & SessionManager.KPISelNavMonth.ToString & Environment.NewLine & strChangeLog, SessionManager.UserID, cnMasterConnection)
                End If

                For Each objTextBox In colControls
                    iColIndex += 1

                    strDate = RegionalConversion.FormatSQLDate(SessionManager.KPISelNavYear.ToString & "/" & SessionManager.KPISelNavMonth.ToString & "/" & iColIndex.ToString)

                    If IsNumeric(objTextBox.Text) Then
                        strValue = RegionalConversion.FormatSQLSingle(objTextBox.Text.Trim)
                    Else
                        strValue = ""
                    End If

                    If iColIndex > 1 Then
                        strLogValue += "|"
                    End If
                    strLogValue += strValue.Trim

                    If SessionManager.KPISelEditMode = "Daily" Then
                        KPIValues.UpdateKPIDailyValue(SessionManager.SelectedValueKPIID, strDate, strValue, cnMasterConnection)
                    Else
                        KPIValues.UpdateKPIDailyValueMTD(SessionManager.SelectedValueKPIID, strDate, strValue, cnMasterConnection)
                    End If
                Next

                If strLogValue.Trim.Length > 0 Then
                    RecordTransactionHistory.InsertRecordTransactionHistory("KPIDailyValues", SessionManager.SelectedValueKPIID.ToString, SessionManager.KPISelEditMode & " " & SessionManager.KPISelNavYear.ToString & "/" & SessionManager.KPISelNavMonth.ToString & ": " & strLogValue, SessionManager.UserID, cnMasterConnection)
                End If
            Catch ex As Exception
                Return False
            Finally
                If cnMasterConnection IsNot Nothing AndAlso cnMasterConnection.State <> ConnectionState.Closed Then
                    cnMasterConnection.Close()
                End If
            End Try

            Return True
        End Function
#End Region

    End Class
End Namespace
