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
    Partial Class TeamOPIEvents2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Team OPI Events"
        Private Shared ReadOnly ProgramName As String = "TeamOPIEvents2"
        Private Shared ReadOnly DBTableName As String = "TeamOPIEvents"
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel, btnExit}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel", "Exit"}
            Dim OutMessageArr() As String = {"", "", ""}
            Dim strDateFormat As String = SessionManager.DateFormat

            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)
            txtEventDate_CalendarExtender.Format = strDateFormat

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnExit.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
        End Sub
        Private Sub LoadAddModeJavaScripts()
            Dim myTabArray() As Object = {txtEventDate, _
                                          txtDescription, _
                                          txtShortDescription, _
                                          ddlLineWidth, _
                                          ddlLineStyle, _
                                          ddlLineColor}
            Dim TabKeyDownArr() As String = {Tab(txtDescription, ddlLineColor, "No"), _
                                             Tab(txtShortDescription, txtEventDate, "No"), _
                                             Tab(ddlLineWidth, txtDescription, "No"), _
                                             Tab(ddlLineStyle, txtShortDescription, "No"), _
                                             Tab(ddlLineColor, ddlLineWidth, "No"), _
                                             Tab(txtEventDate, ddlLineStyle, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {txtDescription, _
                                          txtShortDescription, _
                                          ddlLineWidth, _
                                          ddlLineStyle, _
                                          ddlLineColor}
            Dim TabKeyDownArr() As String = {Tab(txtShortDescription, ddlLineColor, "No"), _
                                             Tab(ddlLineWidth, txtDescription, "No"), _
                                             Tab(ddlLineStyle, txtShortDescription, "No"), _
                                             Tab(ddlLineColor, ddlLineWidth, "No"), _
                                             Tab(txtDescription, ddlLineStyle, "No")}

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
                lblEventDate.Text = GetTranslationString("event date", lblEventDate.Text.Replace(":", "")) & ":"
                lblDescription.Text = GetTranslationString("description", lblDescription.Text.Replace(":", "")) & ":"
                lblShortDescription.Text = GetTranslationString("short description", lblShortDescription.Text.Replace(":", "")) & ":"
                lblLineWidth.Text = GetTranslationString("linewidth", lblLineWidth.Text.Replace(":", "")) & ":"
                lblLineStyle.Text = GetTranslationString("linestyle", lblLineStyle.Text.Replace(":", "")) & ":"
                lblLineColor.Text = GetTranslationString("linecolor", lblLineColor.Text.Replace(":", "")) & ":"
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

            Master.HeaderMessage = GetTranslationString(FormName, FormName) & " - " & GetTranslationString(SessionManager.TeamOPIEventMode.Replace("Row", ""), SessionManager.TeamOPIEventMode.Replace("Row", "")) & " " & GetTranslationString("team opi event", "Team OPI Event")
            Master.IconImage = Request.ApplicationPath + "/images/TeamOPI.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                Select Case SessionManager.TeamOPIEventMode
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        pnlOKCancel.Visible = True
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Team OPI Event.');")
                        TransactionHistory1.LockControl = True
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        LoadAddModeJavaScripts()
                        txtTeam.Text = SessionManager.SelectedTeam
                        txtOPI.Text = SessionManager.SelectedOPI
                        txtEventDate.Focus()
                    Case "EditRow"
                        LoadEditModeJavaScripts()
                        LoadSelectedRecord()
                        UnEnableRecords()
                        txtDescription.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamOPIEvents1"), False)
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueEventDate)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamOPIEventMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamOPIEvents1"), False)
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueEventDate)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamOPIEventMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamOPIEvents1"), False)
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

            Select Case SessionManager.TeamOPIEventMode
                Case "DeleteRow"
                    blnSuccess = DeleteTeamOPIEvent()
                Case "AddRow"
                    blnSuccess = InsertTeamOPIEvent()
                Case "EditRow"
                    blnSuccess = UpdateTeamOPIEvent()
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueEventDate)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamOPIEventMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamOPIEvents1"), False)
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
                Dim dt As DataTable = TeamOPIEvents.SelectTeamOPIEvent(SessionManager.SelectedTeamID, SessionManager.SelectedOPI, SessionManager.SelectedValueEventDate)
                Dim objItem As ListItem
                If dt.Rows.Count <> 0 Then
                    Dim dr As DataRow = dt.Rows(0)
                    txtTeam.Text = dr("Team")
                    txtOPI.Text = dr("OPI")
                    If IsDate(dr("EventDate")) Then
                        txtEventDate.Text = Convert.ToDateTime("" + dr("EventDate")).ToShortDateString
                    Else
                        txtEventDate.Text = ""
                    End If
                    txtDescription.Text = dr("EventDescription").ToString
                    txtShortDescription.Text = dr("ShortDescription").ToString

                    objItem = ddlLineWidth.Items.FindByValue(dr("EventLineWidth"))
                    If Not objItem Is Nothing Then
                        objItem.Selected = True
                        txtLineWidth.Text = objItem.Text
                    End If

                    objItem = ddlLineStyle.Items.FindByValue(dr("EventLineStyle"))
                    If Not objItem Is Nothing Then
                        objItem.Selected = True
                        txtLineStyle.Text = objItem.Text
                    End If

                    objItem = ddlLineColor.Items.FindByValue(dr("EventLineColor"))
                    If Not objItem Is Nothing Then
                        objItem.Selected = True
                        txtLineColor.Text = objItem.Text
                    End If

                    TransactionHistory1.TableName = DBTableName
                    TransactionHistory1.RecordID = SessionManager.SelectedTeamID.ToString & "," & SessionManager.SelectedOPI & "," & SessionManager.SelectedValueEventDate

                    Dim objDic As New Dictionary(Of String, String)
                    objDic.Add("Team", txtTeam.Text.Trim())
                    objDic.Add("OPI", txtOPI.Text.Trim())
                    objDic.Add("EventDate", txtEventDate.Text.Trim())
                    objDic.Add("EventDescription", txtDescription.Text.Trim())
                    objDic.Add("ShortDescription", txtShortDescription.Text.Trim())
                    objDic.Add("EventLineWidth", ddlLineWidth.SelectedItem.Text.Trim())
                    objDic.Add("EventLineStyle", ddlLineStyle.SelectedItem.Text.Trim())
                    objDic.Add("EventLineColor", ddlLineColor.SelectedItem.Text.Trim())
                    SessionManager.RecordTransactionCurrentValues = objDic
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
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

            Select Case SessionManager.TeamOPIEventMode
                Case "ViewRow", "DeleteRow"
                    If SessionManager.TeamOPIEventMode = "ViewRow" Then pnlOKCancel.Visible = False
                    txtEventDate.ReadOnly = True
                    txtEventDate.CssClass = "Textbox_Display"
                    imgEventDate.Visible = False
                    txtEventDate_CalendarExtender.Enabled = False
                    txtDescription.ReadOnly = True
                    txtDescription.CssClass = "Textbox_Display"
                    txtShortDescription.ReadOnly = True
                    txtShortDescription.CssClass = "Textbox_Display"
                    ddlLineWidth.Visible = False
                    txtLineWidth.Visible = True
                    ddlLineStyle.Visible = False
                    txtLineStyle.Visible = True
                    ddlLineColor.Visible = False
                    txtLineColor.Visible = True
                Case "EditRow"
                    txtEventDate.ReadOnly = True
                    txtEventDate.CssClass = "Textbox_Display"
                    imgEventDate.Visible = False
                    txtEventDate_CalendarExtender.Enabled = False
            End Select
        End Sub
        Private Function InsertTeamOPIEvent() As Boolean
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
                Dim strDateHolder As String = RegionalConversion.FormatSQLDate(txtEventDate.Text)
                If Not IsDate(strDateHolder) Then
                    Master.DisplayError("Invalid Date")
                    Return False
                End If

                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                TeamOPIEvents.InsertTeamOPIEvent(SessionManager.SelectedTeamID, txtOPI.Text, strDateHolder, txtDescription.Text, txtShortDescription.Text, CInt(ddlLineWidth.SelectedItem.Value), CInt(ddlLineStyle.SelectedItem.Value), ddlLineColor.SelectedItem.Value)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, txtTeam.Text.Trim() & "," & txtOPI.Text.Trim() & "," & txtEventDate.Text.Trim(), strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertTeamOPIEvent ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateTeamOPIEvent() As Boolean
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

                TeamOPIEvents.UpdateTeamOPIEvent(SessionManager.SelectedTeamID, txtOPI.Text, RegionalConversion.FormatSQLDate(txtEventDate.Text), txtDescription.Text, txtShortDescription.Text, CInt(ddlLineWidth.SelectedItem.Value), CInt(ddlLineStyle.SelectedItem.Value), ddlLineColor.SelectedItem.Value)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedTeamID & "," & SessionManager.SelectedOPI & "," & SessionManager.SelectedValueEventDate, strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateTeamOPIEvent ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function DeleteTeamOPIEvent() As Boolean
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
                TeamOPIEvents.DeleteTeamOPIEvent(SessionManager.SelectedTeamID, txtOPI.Text, RegionalConversion.FormatSQLDate(txtEventDate.Text))
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedTeamID & "," & SessionManager.SelectedOPI & "," & SessionManager.SelectedValueEventDate, "Team OPI Event Deleted", SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteTeamOPIEvent", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
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
            objDic.Add("EventDate", txtEventDate.Text.Trim())
            objDic.Add("EventDescription", txtDescription.Text.Trim())
            objDic.Add("ShortDescription", txtShortDescription.Text.Trim())
            objDic.Add("EventLineWidth", ddlLineWidth.SelectedItem.Text.Trim())
            objDic.Add("EventLineStyle", ddlLineStyle.SelectedItem.Text.Trim())
            objDic.Add("EventLineColor", ddlLineColor.SelectedItem.Text.Trim())
            Return objDic
        End Function
#End Region

    End Class
End Namespace