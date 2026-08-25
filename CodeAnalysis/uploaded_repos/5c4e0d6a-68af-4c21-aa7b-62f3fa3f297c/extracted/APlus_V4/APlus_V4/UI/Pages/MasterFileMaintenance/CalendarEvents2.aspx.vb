#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports System.Collections.Generic

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class CalendarEvents2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Calendar Events"
        Private Shared ReadOnly ProgramName As String = "CalendarEvents2"
        Private Shared ReadOnly DBTableName As String = "CalendarEvents"
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel, btnExit}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel", "Exit"}
            Dim OutMessageArr() As String = {"", "", ""}

            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)

            'load the javascripts for the date controls
            Dim strDateFormat As String = SessionManager.DateFormat
            txtDate_CalendarExtender.Format = strDateFormat

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnExit.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
        End Sub
        Private Sub LoadAddModeJavaScripts()
            Dim myTabArray() As Object = {ddlSite, _
                                          ddlEventTypes, _
                                          txtEvent, _
                                          txtDate, _
                                          txtTime, _
                                          txtExpandDescription}
            Dim TabKeyDownArr() As String = {Tab(ddlEventTypes, txtExpandDescription, "No"), _
                                             Tab(txtEvent, ddlSite, "No"), _
                                             Tab(txtDate, ddlEventTypes, "No"), _
                                             Tab(txtTime, txtEvent, "No"), _
                                             Tab(txtExpandDescription, txtDate, "No"), _
                                             Tab(ddlSite, txtTime, "No")}

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

            Master.HeaderMessage = FormName & " - " & SessionManager.CalendarEventsMode.Replace("Row", "") & " Calendar Event"
            Master.IconImage = Request.ApplicationPath + "/images/Scheduled Tasks.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()
            lnkPrintPage.NavigateUrl = Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("CalendarEvents3")
            lnkPrintPage.NavigateUrl += "?CalendarEventID=" + SessionManager.CalendarEventsSelectedID.ToString.Trim()
            lnkPrintPage.Target = "_blank"

            If Not Page.IsPostBack Then
                Select Case SessionManager.CalendarEventsMode.ToString
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                        lnkPrintPage.Visible = True
                    Case "EditRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        txtExpandDescription.Focus()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        pnlOKCancel.Visible = True
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Calendar Event.');")
                        TransactionHistory1.LockControl = True
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        LoadAddModeJavaScripts()
                        LoadDropDownLists()
                        UnEnableRecords()
                        ddlSite.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("CalendarEvents1"), False)
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

            Dim blnSuccess As Boolean

            Select Case SessionManager.CalendarEventsMode.ToString
                Case "AddRow"
                    blnSuccess = InsertCalendarEvent()
                Case "DeleteRow"
                    blnSuccess = DeleteCalendarEvent()
                Case "EditRow"
                    blnSuccess = UpdateCalendarEvent()
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CalendarEventsSelectedID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CalendarEventsMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("CalendarEvents1"), False)
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
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CalendarEventsSelectedID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CalendarEventsMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("CalendarEvents1"), False)
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
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CalendarEventsSelectedID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CalendarEventsMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("CalendarEvents1"), False)
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadDropDownLists()
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
                ddlSite.Items.Clear()
                ddlSite.Items.Add("")
                SiteMaster.SelectSiteMasterActiveList(ddlSite)

                ddlEventTypes.Items.Clear()
                ddlEventTypes.Items.Add("")
                CalendarEventTypes.SelectCalendarEventTypesList(ddlEventTypes)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadDropDownLists", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
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

            Try
                LoadDropDownLists()

                Dim dt As DataTable = CalendarEvents.SelectCalendarEventByID(SessionManager.CalendarEventsSelectedID)
                If dt IsNot Nothing AndAlso dt.Rows.Count > 0 Then
                    Dim objItem As ListItem
                    Dim dr As DataRow = dt.Rows(0)

                    objItem = ddlSite.Items.FindByValue(dr("SiteID").ToString)
                    If Not objItem Is Nothing Then
                        objItem.Selected = True
                        txtSite.Text = objItem.Text
                    ElseIf IsNumeric(dr("SiteID").ToString) Then
                        Dim dtSite As DataTable = SiteMaster.GetSiteMasterBySite(dr("SiteID").ToString)
                        If dtSite IsNot Nothing AndAlso dtSite.Rows.Count = 1 Then
                            objItem = New ListItem(dtSite.Rows(0)("Site").ToString, dtSite.Rows(0)("SiteID").ToString)
                            objItem.Selected = True
                            txtSite.Text = objItem.Text
                        End If
                    End If

                    objItem = ddlEventTypes.Items.FindByValue(dr("EventTypeID").ToString)
                    If Not objItem Is Nothing Then
                        objItem.Selected = True
                        txtEventType.Text = objItem.Text
                    End If

                    txtEvent.Text = dr("Event").ToString
                    If IsDate(dr("EventDate")) Then
                        txtDate.Text = Convert.ToDateTime("" + dr("EventDate")).ToShortDateString
                    Else
                        txtDate.Text = ""
                    End If
                    txtTime.Text = dr("EventTime").ToString
                    txtExpandDescription.Text = dr("EventDescription").ToString

                    TransactionHistory1.TableName = DBTableName
                    TransactionHistory1.RecordID = SessionManager.CalendarEventsSelectedID

                    Dim objDic As New Dictionary(Of String, String)
                    objDic.Add("Site", ddlSite.SelectedItem.Text.Trim())
                    objDic.Add("EventType", ddlEventTypes.SelectedItem.Text.Trim())
                    objDic.Add("Event", txtEvent.Text.Trim())
                    objDic.Add("EventDate", txtDate.Text.Trim())
                    objDic.Add("EventTime", txtTime.Text.Trim())
                    objDic.Add("EventDescription", txtExpandDescription.Text.Trim())
                    SessionManager.RecordTransactionCurrentValues = objDic
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
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

            Select Case SessionManager.CalendarEventsMode.ToString
                Case "ViewRow", "DeleteRow"
                    pnlOKCancel.Visible = False
                    ddlSite.Visible = False
                    txtSite.Visible = True
                    ddlEventTypes.Visible = False
                    txtEventType.Visible = True
                    imgDate.Visible = False
                    txtDate_CalendarExtender.Enabled = False
                    txtEvent.ReadOnly = True
                    txtEvent.CssClass = "Textbox_Display"
                    txtDate.ReadOnly = True
                    txtDate.CssClass = "Textbox_Display"
                    txtTime.ReadOnly = True
                    txtTime.CssClass = "Textbox_Display"
                    txtExpandDescription.ReadOnly = True
                    txtExpandDescription.CssClass = "Textbox_Display"
                Case "EditRow"
                    ddlSite.Visible = False
                    txtSite.Visible = True
                    ddlEventTypes.Visible = False
                    txtEventType.Visible = True
                    imgDate.Visible = False
                    txtDate_CalendarExtender.Enabled = False
                    txtEvent.ReadOnly = True
                    txtEvent.CssClass = "Textbox_Display"
                    txtDate.ReadOnly = True
                    txtDate.CssClass = "Textbox_Display"
                    txtTime.ReadOnly = True
                    txtTime.CssClass = "Textbox_Display"
            End Select
        End Sub
        Private Function UpdateCalendarEvent() As Boolean
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
                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.CompareDictionaryValues(SessionManager.RecordTransactionCurrentValues, objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If
                CalendarEvents.UpdateCalendarEvent(SessionManager.CalendarEventsSelectedID, txtExpandDescription.Text.Trim())
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.CalendarEventsSelectedID, strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateCalendarEvent", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function InsertCalendarEvent() As Boolean
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
                Dim strDate As String = RegionalConversion.FormatSQLDate(txtDate.Text)
                If ddlEventTypes.SelectedItem.Text.Length = 0 Then
                    Master.DisplayError("Select Event Type")
                    Return False
                End If

                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                Dim intResult As Integer = CalendarEvents.AddCalendarEvent(ddlSite.SelectedItem.Value, ddlEventTypes.SelectedItem.Value, txtEvent.Text, strDate, txtTime.Text, txtExpandDescription.Text)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, intResult.ToString.Trim(), strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertCalendarEvent", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function DeleteCalendarEvent() As Boolean
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
                CalendarEvents.DeleteCalendarEvent(SessionManager.CalendarEventsSelectedID)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.CalendarEventsSelectedID, "Calendar Event Deleted", SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteCalendarEvent", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
        End Function
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
            objDic.Add("Site", ddlSite.SelectedItem.Text.Trim())
            objDic.Add("EventType", ddlEventTypes.SelectedItem.Text.Trim())
            objDic.Add("Event", txtEvent.Text.Trim())
            objDic.Add("EventDate", txtDate.Text.Trim())
            objDic.Add("EventTime", txtTime.Text.Trim())
            objDic.Add("EventDescription", txtExpandDescription.Text.Trim())
            Return objDic
        End Function
#End Region

    End Class
End Namespace