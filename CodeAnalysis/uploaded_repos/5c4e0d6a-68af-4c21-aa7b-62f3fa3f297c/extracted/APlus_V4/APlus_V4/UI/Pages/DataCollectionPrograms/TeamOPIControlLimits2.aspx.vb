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
    Partial Class TeamOPIControlLimits2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Team OPI Control Limits"
        Private Shared ReadOnly ProgramName As String = "TeamOPIControlLimits2"
        Private Shared ReadOnly DBTableName As String = "TeamOPIControlLimits"
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel, btnExit}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel", "Exit"}
            Dim OutMessageArr() As String = {"", "", ""}
            Dim strDateFormat As String = SessionManager.DateFormat

            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)
            txtStartDate_CalendarExtender.Format = strDateFormat

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnExit.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
        End Sub
        Private Sub LoadAddModeJavaScripts()
            Dim myTabArray() As Object = {txtStartDate, _
                                         txtUpperValue, _
                                         txtLowerValue, _
                                         txtExpandDescription}
            Dim TabKeyDownArr() As String = {Tab(txtUpperValue, txtExpandDescription, "No"), _
                                             Tab(txtLowerValue, txtStartDate, "Neg"), _
                                             Tab(txtExpandDescription, txtUpperValue, "Neg"), _
                                             Tab(txtStartDate, txtLowerValue, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {txtUpperValue, _
                                          txtLowerValue, _
                                          txtExpandDescription}
            Dim TabKeyDownArr() As String = {Tab(txtLowerValue, txtExpandDescription, "Neg"), _
                                             Tab(txtExpandDescription, txtUpperValue, "Neg"), _
                                             Tab(txtUpperValue, txtLowerValue, "No")}

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
                lblRouteAbbrev.Text = GetTranslationString("team", lblRouteAbbrev.Text.Replace(":", "")) & ":"
                lblRoute.Text = GetTranslationString("opi", lblRoute.Text.Replace(":", "")) & ":"
                lblStartDate.Text = GetTranslationString("start date", lblStartDate.Text.Replace(":", "")) & ":"
                lblUpperValue.Text = GetTranslationString("upper value", lblUpperValue.Text.Replace(":", "")) & ":"
                lblLowerValue.Text = GetTranslationString("lower value", lblLowerValue.Text.Replace(":", "")) & ":"
                lblDescription.Text = GetTranslationString("description", lblDescription.Text.Replace(":", "")) & ":"
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

            If Not Page.IsPostBack Then
                LoadCultureTranslations()
            End If

            Master.HeaderMessage = GetTranslationString(FormName, FormName) & " - " & GetTranslationString(SessionManager.TeamOPIControlLimitsMode.Replace("Row", ""), SessionManager.TeamOPIControlLimitsMode.Replace("Row", ""))
            Master.IconImage = Request.ApplicationPath + "/images/TeamOPI.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                Select Case SessionManager.TeamOPIControlLimitsMode
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        pnlOKCancel.Visible = True
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Team OPI Control Limit.');")
                        TransactionHistory1.LockControl = True
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        LoadAddModeJavaScripts()
                        txtTeam.Text = SessionManager.SelectedTeam
                        txtOPI.Text = SessionManager.SelectedOPI
                        LoadPageValidation()
                        txtStartDate.Focus()
                    Case "EditRow"
                        LoadEditModeJavaScripts()
                        LoadSelectedRecord()
                        UnEnableRecords()
                        LoadPageValidation()
                        txtUpperValue.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamOPIControlLimits1"), False)
                End Select
            End If
        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.TeamOPIControlLimitsMode = "EditRow" Or SessionManager.TeamOPIControlLimitsMode = "ViewRow" Or SessionManager.TeamOPIControlLimitsMode = "DeleteRow" Or SessionManager.TeamOPIControlLimitsMode = "AddRow" Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue2)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamOPIControlLimitsMode)
            End If
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamOPIControlLimits1"), False)
        End Sub
        Private Sub btnCancel_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnCancel.Click
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
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue2)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamOPIControlLimitsMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamOPIControlLimits1"), False)
        End Sub
        Private Sub btnOK_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnOK.Click
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

            If SessionManager.TeamOPIControlLimitsMode = "DeleteRow" Then
                blnSuccess = DeleteTeamOPIControlLimit()
            ElseIf SessionManager.TeamOPIControlLimitsMode = "AddRow" Then
                blnSuccess = InsertTeamOPIControlLimit()
            ElseIf SessionManager.TeamOPIControlLimitsMode = "EditRow" Then
                blnSuccess = UpdateTeamOPIControlLimit()
            End If

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue2)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamOPIControlLimitsMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamOPIControlLimits1"), False)
            End If
        End Sub
#End Region

#Region " Custom Methods"
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

            Try
                Dim dt As DataTable = TeamOPIControlLimits.SelectTeamOPIControlLimit(SessionManager.SelectedValue, SessionManager.SelectedValue1, SessionManager.SelectedValue2)
                If dt.Rows.Count <> 0 Then
                    Dim dr As DataRow = dt.Rows(0)
                    txtTeam.Text = dr.Item("Team").ToString.Trim()
                    txtOPI.Text = dr("OPI")
                    If Not (dr("UpperValue") Is DBNull.Value) Then
                        txtUpperValue.Text = Format(dr("UpperValue"), "0.####")
                    End If
                    If Not (dr("LowerValue") Is DBNull.Value) Then
                        txtLowerValue.Text = Format(dr("LowerValue"), "0.####")
                    End If
                    txtExpandDescription.Text = "" + dr("Description").ToString.Trim()
                    If IsDate(dr("StartDate")) Then
                        txtStartDate.Text = Convert.ToDateTime("" + dr("StartDate")).ToShortDateString
                    Else
                        txtStartDate.Text = ""
                    End If
                    If SessionManager.TeamOPIControlLimitsMode = "EditRow" Then
                        imgStartDate.Visible = True
                    Else
                        imgStartDate.Visible = False
                        txtStartDate_CalendarExtender.Enabled = False
                    End If

                    TransactionHistory1.TableName = DBTableName
                    TransactionHistory1.RecordID = SessionManager.SelectedValue & "," & SessionManager.SelectedValue1 & "," & SessionManager.SelectedValue2

                    Dim objDic As New Dictionary(Of String, String)
                    objDic.Add("Team", txtTeam.Text.Trim())
                    objDic.Add("OPI", txtOPI.Text.Trim())
                    objDic.Add("StartDate", txtStartDate.Text.Trim())
                    objDic.Add("Description", txtExpandDescription.Text.Trim())
                    objDic.Add("UpperValue", txtUpperValue.Text.Trim())
                    objDic.Add("LowerValue", txtLowerValue.Text.Trim())
                    SessionManager.RecordTransactionCurrentValues = objDic
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
            End Try
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

            Select Case SessionManager.TeamOPIControlLimitsMode
                Case "ViewRow", "DeleteRow"
                    If SessionManager.TeamOPIControlLimitsMode = "ViewRow" Then pnlOKCancel.Visible = False
                    txtStartDate.ReadOnly = True
                    txtStartDate.CssClass = "Textbox_Display"
                    imgStartDate.Visible = False
                    txtStartDate_CalendarExtender.Enabled = False
                    txtLowerValue.ReadOnly = True
                    txtLowerValue.CssClass = "Textbox_Display"
                    txtUpperValue.ReadOnly = True
                    txtUpperValue.CssClass = "Textbox_Display"
                    txtExpandDescription.ReadOnly = True
                    txtExpandDescription.CssClass = "Textbox_Display"
                Case "EditRow"
                    txtStartDate.ReadOnly = True
                    txtStartDate.CssClass = "Textbox_Display"
                    imgStartDate.Visible = False
                    txtStartDate_CalendarExtender.Enabled = False
                    txtUpperValue.Focus()
            End Select
        End Sub
        Private Sub LoadPageValidation()
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
                Dim strOPIHolder As String = "" + txtOPI.Text
                If String.IsNullOrEmpty(strOPIHolder.Trim()) Then Exit Sub

                Dim dsHolder As DataTable = TeamOPI.SelectTeamOPI(SessionManager.SelectedTeamID, strOPIHolder)
                Dim dr As DataRow = dsHolder.Rows(0)

                Dim _OPISize As Integer = CInt(dr("OPISize"))
                Dim _NegativeEntryAllowed As Boolean = CBool(dr("NegativeEntryAllowed"))

                Select Case dr.Item("OPIEntryType").ToString.ToUpper
                    Case "N"
                        txtUpperValue.Width = New Unit(_OPISize * 12)
                        txtLowerValue.Width = New Unit(_OPISize * 12)

                        If _NegativeEntryAllowed Then
                            txtUpperValue.MaxLength = 1 + _OPISize
                            txtLowerValue.MaxLength = 1 + _OPISize

                            reqUpperValueValid.ValidationExpression = "-?\d{1," + _OPISize.ToString + "}"
                            reqLowerValueValid.ValidationExpression = "-?\d{1," + _OPISize.ToString + "}"
                        Else
                            txtUpperValue.MaxLength = _OPISize
                            txtLowerValue.MaxLength = _OPISize
                            reqUpperValueValid.ValidationExpression = "\d{1," + _OPISize.ToString + "}"
                            reqLowerValueValid.ValidationExpression = "\d{1," + _OPISize.ToString + "}"
                        End If

                        reqUpperValueValid.ErrorMessage = "Upper Value must be a numeric value with no more than " + _OPISize.ToString + " digits"
                        reqLowerValueValid.ErrorMessage = "Lower Value must be a numeric value with no more than " + _OPISize.ToString + " digits"
                    Case "D"
                        txtUpperValue.Width = New Unit((8 + _OPISize) * 12)
                        txtLowerValue.Width = New Unit((8 + _OPISize) * 12)

                        If _NegativeEntryAllowed Then
                            txtUpperValue.MaxLength = 9 + _OPISize
                            txtLowerValue.MaxLength = 9 + _OPISize

                            reqUpperValueValid.ValidationExpression = "(-?\d{0,7}\.{1}\d{0," + _OPISize.ToString + "})|(-?\d{0,7})"
                            reqLowerValueValid.ValidationExpression = "(-?\d{0,7}\.{1}\d{0," + _OPISize.ToString + "})|(-?\d{0,7})"
                        Else
                            txtUpperValue.MaxLength = 8 + _OPISize
                            txtLowerValue.MaxLength = 8 + _OPISize

                            reqUpperValueValid.ValidationExpression = "(\d{0,7}\.{1}\d{0," + _OPISize.ToString + "})|(\d{0,7})"
                            reqLowerValueValid.ValidationExpression = "(\d{0,7}\.{1}\d{0," + _OPISize.ToString + "})|(\d{0,7})"
                        End If

                        reqUpperValueValid.ErrorMessage = "Upper Value must be decimal value with no more than " + _OPISize.ToString + " decimal places"
                        reqLowerValueValid.ErrorMessage = "Lower Value must be decimal value with no more than " + _OPISize.ToString + " decimal places"
                End Select
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
            End Try
        End Sub
        Private Function InsertTeamOPIControlLimit() As Boolean
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
                Dim strDateHolder As String = RegionalConversion.FormatSQLDate(txtStartDate.Text)
                If Not IsDate(strDateHolder) Then
                    Master.DisplayError("Invalid Start Date")
                    Return False
                End If

                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                TeamOPIControlLimits.InsertTeamOPIControlLimit(SessionManager.SelectedTeamID, txtOPI.Text, strDateHolder, txtUpperValue.Text, txtLowerValue.Text, txtExpandDescription.Text.Trim)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValue & "," & txtOPI.Text & "," & strDateHolder, strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertTeamOPIControlLimit", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateTeamOPIControlLimit() As Boolean
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
                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.CompareDictionaryValues(SessionManager.RecordTransactionCurrentValues, objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                TeamOPIControlLimits.UpdateTeamOPIControlLimit(SessionManager.SelectedValue, SessionManager.SelectedValue1, SessionManager.SelectedValue2, txtUpperValue.Text, txtLowerValue.Text, txtExpandDescription.Text.Trim)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValue & "," & SessionManager.SelectedValue1 & "," & SessionManager.SelectedValue2, strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateTeamOPIControlLimits", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function DeleteTeamOPIControlLimit() As Boolean
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
                TeamOPIControlLimits.DeleteTeamOPIControlLimit(SessionManager.SelectedValue, SessionManager.SelectedValue1, RegionalConversion.FormatSQLDate(txtStartDate.Text))
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValue & "," & SessionManager.SelectedValue1 & "," & SessionManager.SelectedValue2, "Team OPI Control Limits Deleted", SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteTeamOPIControlLimit", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
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
            objDic.Add("Team", txtTeam.Text.Trim())
            objDic.Add("OPI", txtOPI.Text.Trim())
            objDic.Add("StartDate", txtStartDate.Text.Trim())
            objDic.Add("Description", txtExpandDescription.Text.Trim())
            objDic.Add("UpperValue", txtUpperValue.Text.Trim())
            objDic.Add("LowerValue", txtLowerValue.Text.Trim())
            Return objDic
        End Function
#End Region

    End Class
End Namespace