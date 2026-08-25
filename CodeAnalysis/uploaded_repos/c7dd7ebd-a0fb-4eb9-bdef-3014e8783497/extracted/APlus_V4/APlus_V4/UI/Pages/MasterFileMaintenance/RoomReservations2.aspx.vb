#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports System.Web.Security
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.DataAccess.Custom
Imports System.Collections.Generic

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class RoomReservations2
        Inherits ApplicationBase

#Region " Constants"
        Private Shared ReadOnly FormName As String = "Room Reservations"
        Private Shared ReadOnly ProgramName As String = "RoomReservations2"
        Private Shared ReadOnly DBTableName As String = "RoomReservationsMaster"
        Private strSite As String = ""
        Private iSiteID As Integer
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
        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {ddlRoom, _
                                          ddlStartTime, _
                                          ddlStartTimeMinutes, _
                                          ddlEndTime, _
                                          ddlEndTimeMinutes, _
                                          txtExpandDescription, _
                                          ddlTeam}
            Dim TabKeyDownArr() As String = { _
                                            Tab(ddlStartTime, ddlTeam, "No"), _
                                            Tab(ddlStartTimeMinutes, ddlRoom, "No"), _
                                            Tab(ddlEndTime, ddlStartTime, "No"), _
                                            Tab(ddlEndTimeMinutes, ddlStartTimeMinutes, "No"), _
                                            Tab(txtExpandDescription, ddlEndTime, "No"), _
                                            Tab(ddlTeam, ddlEndTimeMinutes, "No"), _
                                            Tab(ddlRoom, txtExpandDescription, "No")}

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

            Master.HeaderMessage = FormName
            Master.IconImage = Request.ApplicationPath + "/images/RoomReservation.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            'initialize the print friendly page
            lnkPrintPage.NavigateUrl = Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RoomReservations3")
            lnkPrintPage.NavigateUrl += "?RoomReservationID=" + SessionManager.SelectedValueReservationID
            lnkPrintPage.Target = "_blank"

            If SessionManager.SelectedValueTeamSiteID > 0 Then
                iSiteID = SessionManager.SelectedValueTeamSiteID
                strSite = SiteMaster.GetSiteNameBySiteID(SessionManager.SelectedValueTeamSiteID)
            Else
                strSite = SessionManager.WorkingSite
                iSiteID = SessionManager.WorkingSiteID
            End If

            LoadCommonJavaScripts()

            If SessionManager.RoomReservations.ToString = "Y" Then
                Master.HideAPlusIcon = True
                Master.MinimalIcons = True
                pnlTeam.Visible = False
            End If

            If Not Page.IsPostBack Then
                LoadDropDownLists()

                Select Case SessionManager.RoomReservationsMode
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                        lnkPrintPage.Visible = True
                    Case "EditRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        If SessionManager.RoomReservationsMode = "ViewRow" Then
                            pnlExit.Visible = True
                            lnkPrintPage.Visible = True
                        Else
                            LoadEditModeJavaScripts()
                            txtDate.Focus()
                            btnDelete.Visible = True
                            btnDelete.CausesValidation = False
                            btnDelete.Attributes.Add("onclick", "return confirm('Click OK to Delete this Room Reservation.');")
                        End If
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        LoadEditModeJavaScripts()
                        txtRoomReservationID.Text = "New"
                        txtUserID.Text = SessionManager.UserID
                        pnlMaintenance.Visible = False
                        If IsDate(SessionManager.SelectedValueDate) Then
                            txtDate.Text = CDate(SessionManager.SelectedValueDate).ToShortDateString
                        Else
                            txtDate.Text = ""
                            Master.DisplayError("Invalid Date Passed to Page")
                            Return
                        End If
                        UnEnableRecords()

                        ddlRoom.Focus()
                    Case "AddTeamMeeting"
                        TransactionHistory1.Visible = False

                        LoadEditModeJavaScripts()
                        txtRoomReservationID.Text = "New"
                        txtUserID.Text = SessionManager.UserID
                        pnlMaintenance.Visible = False
                        If IsDate(SessionManager.SelectedValueDate) Then
                            txtDate.Text = CDate(SessionManager.SelectedValueDate).ToShortDateString
                        Else
                            txtDate.Text = ""
                            Master.DisplayError(GetTranslationString("invaliddate", "Invalid Date Passed to Page"))
                            Return
                        End If
                        Dim objItem As ListItem
                        objItem = ddlTeam.Items.FindByValue(SessionManager.SelectedTeamID)
                        If Not objItem Is Nothing Then
                            objItem.Selected = True
                        End If
                        txtExpandDescription.Text = UserMaster.GetUserFullName(SessionManager.UserID) & " - " & SessionManager.SelectedTeam & " - " & SessionManager.SelectedTeamName
                        UnEnableRecords()

                        Dim strStart As String = Left(SessionManager.SelectedValueDateTime, 2)
                        Dim strStartMinutes As String = Right(SessionManager.SelectedValueDateTime, 2)
                        If Val(strStartMinutes) < 30 Then
                            strStartMinutes = "00"
                        Else
                            strStartMinutes = "30"
                        End If

                        objItem = ddlStartTime.Items.FindByValue(strStart)
                        If Not objItem Is Nothing Then
                            objItem.Selected = True
                        End If
                        objItem = ddlStartTimeMinutes.Items.FindByValue(strStartMinutes)
                        If Not objItem Is Nothing Then
                            objItem.Selected = True
                        End If

                        objItem = ddlRoom.Items.FindByText(SessionManager.SelectedValueLocation)
                        If Not objItem Is Nothing Then
                            objItem.Selected = True
                        End If

                        ddlRoom.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RoomReservations1"), False)
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

            Select Case SessionManager.RoomReservationsMode
                Case "AddRow", "AddTeamMeeting"
                    blnSuccess = InsertRoomReservation()
                Case "EditRow"
                    blnSuccess = UpdateRoomReservation()
            End Select

            If blnSuccess Then
                Select Case SessionManager.RoomReservationsMode
                    Case "AddTeamMeeting"
                        SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueReservationID)
                        SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RoomReservationsMode)
                        SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueDate)
                        SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueDateTime)
                        SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueTeamSiteID)
                        SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueLocation)
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamMeetings2"), False)
                    Case Else
                        SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueReservationID)
                        SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RoomReservationsMode)
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RoomReservations1"), False)
                End Select
            End If
        End Sub
        Private Sub btnDelete_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnDelete.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim blnSuccess As Boolean = DeleteRoomReservation()
            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueReservationID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RoomReservationsMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RoomReservations1"), False)
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

            Select Case SessionManager.RoomReservationsMode
                Case "AddTeamMeeting"
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueReservationID)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RoomReservationsMode)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueDate)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueDateTime)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueTeamSiteID)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueLocation)
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamMeetings2"), False)
                Case Else
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueReservationID)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RoomReservationsMode)
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RoomReservations1"), False)
            End Select
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueReservationID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RoomReservationsMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RoomReservations1"), False)
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
                ddlRoom.Items.Clear()
                ddlRoom.Items.Add("")
                RoomMaster.FillRoomDropDownList(iSiteID, ddlRoom)

                ddlTeam.Items.Clear()
                ddlTeam.Items.Add("")
                Teams.FillTeamSelectionList(ddlTeam, SessionManager.UserID, iSiteID, False)
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
                If SessionManager.RecordTransactionCurrentValues IsNot Nothing Then
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RecordTransactionCurrentValues)
                End If
                TransactionHistory1.TableName = DBTableName
                TransactionHistory1.RecordID = SessionManager.SelectedValueReservationID

                Dim dt As DataTable = RoomReservationsMaster.SelectRoomReservation(SessionManager.SelectedValueReservationID)
                Dim objItem As ListItem

                If dt.Rows.Count > 0 Then
                    Dim dr As DataRow = dt.Rows(0)
                    objItem = ddlRoom.Items.FindByValue(dr("RoomID"))
                    If Not objItem Is Nothing Then
                        objItem.Selected = True
                        txtRoom.Text = objItem.Text
                    End If

                    Dim dtStart As DateTime = dr("StartTime")
                    Dim dtEnd As DateTime = dr("EndTime")

                    txtRoomReservationID.Text = SessionManager.SelectedValueReservationID
                    txtDate.Text = dtStart.ToShortDateString

                    objItem = ddlStartTime.Items.FindByValue(dtStart.ToString("HH"))
                    If Not objItem Is Nothing Then
                        objItem.Selected = True
                    End If
                    objItem = ddlStartTimeMinutes.Items.FindByValue(dtStart.ToString("mm"))
                    If Not objItem Is Nothing Then
                        objItem.Selected = True
                    End If
                    txtStartTime.Text = dtStart.ToShortTimeString

                    objItem = ddlEndTime.Items.FindByValue(dtEnd.ToString("HH"))
                    If Not objItem Is Nothing Then
                        objItem.Selected = True
                    End If
                    objItem = ddlEndTimeMinutes.Items.FindByValue(dtEnd.ToString("mm"))
                    If Not objItem Is Nothing Then
                        objItem.Selected = True
                    End If
                    txtEndTime.Text = dtEnd.ToShortTimeString

                    txtExpandDescription.Text = dr("Description").ToString
                    txtExpandNotes.Text = dr("Notes").ToString

                    Select Case dr("Catering").ToString.ToUpper
                        Case "L"
                            ckLunch.Checked = True
                            ckCoffee.Checked = False
                            ckDinner.Checked = False
                        Case "T"
                            ckLunch.Checked = False
                            ckCoffee.Checked = True
                            ckDinner.Checked = False
                        Case "D"
                            ckLunch.Checked = False
                            ckCoffee.Checked = False
                            ckDinner.Checked = True
                        Case "A"
                            'denotes All
                            ckLunch.Checked = True
                            ckCoffee.Checked = True
                            ckDinner.Checked = True
                        Case "X"
                            'denotes Lunch and Coffee
                            ckLunch.Checked = True
                            ckCoffee.Checked = True
                            ckDinner.Checked = False
                        Case "Y"
                            'denotes Coffee and Dinner
                            ckLunch.Checked = False
                            ckCoffee.Checked = True
                            ckDinner.Checked = True
                        Case "Z"
                            'denotes Lunch and Dinner only
                            ckLunch.Checked = True
                            ckCoffee.Checked = False
                            ckDinner.Checked = True
                        Case Else
                            ckLunch.Checked = False
                            ckCoffee.Checked = False
                            ckDinner.Checked = False
                    End Select
                    ckVideoConferencing.Checked = dr("VideoConferencing")

                    objItem = ddlTeam.Items.FindByValue(dr("TeamID").ToString)
                    If Not objItem Is Nothing Then
                        objItem.Selected = True
                        txtTeam.Text = objItem.Text
                    End If

                    txtUserID.Text = UserMaster.GetUserFullName(dr("UserID").ToString)
                    txtMaintUserID.Text = UserMaster.GetUserFullName(dr("MaintenanceUserID").ToString)
                    txtMaintDate.Text = dr("MaintenanceDate").ToString

                    'lets determine if this user actually has edit capability
                    If dr("UserID").ToString.ToUpper = SessionManager.UserID.ToString.ToUpper Then
                        'edit mode
                        pnlNotes.Visible = True
                    Else
                        SessionManager.RoomReservationsMode = "ViewRow"

                        Dim dtMode As DataTable = ProgramSecurity.ProgramModeFromProgram(SessionManager.UserID, "RoomReservations1")
                        If dtMode.Rows.Count > 0 Then
                            If CType(dtMode.Rows(0).Item("AllowEdit"), Boolean) = True Then
                                SessionManager.RoomReservationsMode = "EditRow"
                            ElseIf IsNumeric(dr("TeamID").ToString) Then
                                If Teams.UserHasAccessToTeam(SessionManager.UserID, dr("TeamID"), iSiteID) Then
                                    SessionManager.RoomReservationsMode = "EditRow"
                                End If
                            End If
                        ElseIf IsNumeric(dr("TeamID").ToString) Then
                            If Teams.UserHasAccessToTeam(SessionManager.UserID, dr("TeamID"), iSiteID) Then
                                SessionManager.RoomReservationsMode = "EditRow"
                            End If
                        End If

                        If SessionManager.RoomReservationsMode = "EditRow" Then
                            pnlNotes.Visible = True
                        End If
                    End If

                    Dim objDic As New Dictionary(Of String, String)
                    objDic.Add("Room", txtRoom.Text)
                    objDic.Add("StartTime", txtStartTime.Text.Trim())
                    objDic.Add("EndTime", txtEndTime.Text.Trim())
                    objDic.Add("Description", txtExpandDescription.Text.Trim())
                    objDic.Add("Catering", dr("Catering").ToString.ToUpper.Trim())
                    objDic.Add("VideoConferencing", ckVideoConferencing.Checked)
                    objDic.Add("UserID", txtUserID.Text.Trim())
                    objDic.Add("Team", txtTeam.Text.Trim())
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

            Select Case SessionManager.RoomReservationsMode
                Case "ViewRow", "DeleteRow"
                    pnlOKCancel.Visible = False

                    ddlRoom.Visible = False
                    txtRoom.Visible = True

                    ddlStartTime.Visible = False
                    ddlStartTimeMinutes.Visible = False
                    txtStartTime.Visible = True

                    ddlEndTime.Visible = False
                    ddlEndTimeMinutes.Visible = False
                    txtEndTime.Visible = True

                    txtExpandDescription.ReadOnly = True
                    txtExpandDescription.CssClass = "Textbox_Display"
                    txtExpandNotes.ReadOnly = True
                    txtExpandNotes.CssClass = "Textbox_Display"

                    ddlTeam.Visible = False
                    txtTeam.Visible = True

                    imgDate.Visible = False
                    txtDate_CalendarExtender.Enabled = False
                    reqDate.Enabled = False
                Case "AddRow", "AddTeamMeeting"
                    imgDate.Visible = False
                    txtDate_CalendarExtender.Enabled = False
                    reqDate.Enabled = False
                    pnlNotes.Visible = True
                Case "EditRow"
                    txtDate.ReadOnly = False
                    txtDate.CssClass = "Textbox_Entry"
                    imgDate.Visible = True
                    reqDate.Enabled = True
            End Select
        End Sub
        Private Function InsertRoomReservation() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If ValidateReservation() = False Then
                Return False
            End If

            Dim strCatering As String = ""
            Dim strStart As String = RegionalConversion.FormatSQLDate(SessionManager.SelectedValueDate & " " & ddlStartTime.SelectedItem.Value & ":" & ddlStartTimeMinutes.SelectedItem.Value, True)
            Dim strEnd As String = ""
            If IsDate(txtDate.Text) AndAlso ddlEndTime.SelectedItem.Value.ToString = "24" Then
                strEnd = RegionalConversion.FormatSQLDate(Convert.ToDateTime(txtDate.Text).AddDays(1) & " 00:00", True)
            Else
                strEnd = RegionalConversion.FormatSQLDate(txtDate.Text & " " & ddlEndTime.SelectedItem.Value & ":" & ddlEndTimeMinutes.SelectedItem.Value, True)
            End If
            Dim strTeam As String = ddlTeam.SelectedItem.Value

            If ckLunch.Checked Then
                'check to see if any other checkboxes are checked
                If ckCoffee.Checked = True And ckDinner.Checked = True Then
                    'all
                    strCatering = "A"
                ElseIf ckCoffee.Checked = True And ckDinner.Checked = False Then
                    strCatering = "X"
                ElseIf ckCoffee.Checked = False And ckDinner.Checked = True Then
                    strCatering = "Z"
                Else
                    strCatering = "L"
                End If
            Else
                If ckCoffee.Checked Then
                    If ckDinner.Checked = True Then
                        strCatering = "Y"
                    Else
                        strCatering = "T"
                    End If
                Else
                    If ckDinner.Checked Then
                        strCatering = "D"
                    End If
                End If
            End If

            Try
                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If
                Dim intResult As Integer = RoomReservationsMaster.AddRoomReservation(ddlRoom.SelectedItem.Value, strStart, strEnd, txtExpandDescription.Text, txtExpandNotes.Text.Trim, strTeam, SessionManager.UserID, strCatering, ckVideoConferencing.Checked)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, intResult, strChangeLog, SessionManager.UserID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertRoomReservation", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try

            Return True
        End Function
        Private Function UpdateRoomReservation() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If ValidateReservation() = False Then
                Return False
            End If

            Dim strCatering As String = String.Empty
            Dim strStart As String = RegionalConversion.FormatSQLDate(txtDate.Text & " " & ddlStartTime.SelectedItem.Value & ":" & ddlStartTimeMinutes.SelectedItem.Value, True)
            Dim strEnd As String = ""
            If IsDate(txtDate.Text) AndAlso ddlEndTime.SelectedItem.Value.ToString = "24" Then
                strEnd = RegionalConversion.FormatSQLDate(Convert.ToDateTime(txtDate.Text).AddDays(1) & " 00:00", True)
            Else
                strEnd = RegionalConversion.FormatSQLDate(txtDate.Text & " " & ddlEndTime.SelectedItem.Value & ":" & ddlEndTimeMinutes.SelectedItem.Value, True)
            End If
            Dim strTeam As String = ddlTeam.SelectedItem.Value

            If ckLunch.Checked Then
                If ckCoffee.Checked = True And ckDinner.Checked = True Then
                    strCatering = "A"
                ElseIf ckCoffee.Checked = True And ckDinner.Checked = False Then
                    strCatering = "X"
                ElseIf ckCoffee.Checked = False And ckDinner.Checked = True Then
                    strCatering = "Z"
                Else
                    strCatering = "L"
                End If
            Else
                If ckCoffee.Checked Then
                    If ckDinner.Checked = True Then
                        strCatering = "Y"
                    Else
                        strCatering = "T"
                    End If
                Else
                    If ckDinner.Checked Then
                        strCatering = "D"
                    End If
                End If
            End If

            Try
                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.CompareDictionaryValues(SessionManager.RecordTransactionCurrentValues, objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If
                RoomReservationsMaster.UpdateRoomReservation(SessionManager.SelectedValueReservationID, ddlRoom.SelectedItem.Value, strStart, strEnd, txtExpandDescription.Text, txtExpandNotes.Text.Trim, strTeam, SessionManager.UserID, strCatering, ckVideoConferencing.Checked)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueReservationID, strChangeLog, SessionManager.UserID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateRoomReservation", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
            Return True
        End Function
        Private Function DeleteRoomReservation() As Boolean
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
                RoomReservationsMaster.DeleteRoomReservation(txtRoomReservationID.Text)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueReservationID, "Room Reservation Deleted", SessionManager.UserID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteRoomReservation", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
            Return True
        End Function
        Private Function ValidateReservation() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            'first, verify that we have times selected
            If ddlStartTime.SelectedItem.Value.Trim.Length = 0 Then
                Master.DisplayError(GetTranslationString("selectstarthours", "Select Start Time Hours"))
                Return False
            End If
            If ddlStartTimeMinutes.SelectedItem.Value.Trim.Length = 0 Then
                Master.DisplayError(GetTranslationString("selectstartmin", "Select Start Time Minutes"))
                Return False
            End If
            If ddlEndTime.SelectedItem.Value.Trim.Length = 0 Then
                Master.DisplayError(GetTranslationString("selectendhours", "Select End Time Hours"))
                Return False
            End If
            If ddlEndTimeMinutes.SelectedItem.Value.Trim.Length = 0 Then
                Master.DisplayError(GetTranslationString("selectendmin", "Select End Time Minutes"))
                Return False
            End If

            'verify that the selected Time is open for the selected room
            Dim strStart As String = RegionalConversion.FormatSQLDate(txtDate.Text & " " & ddlStartTime.SelectedItem.Value & ":" & ddlStartTimeMinutes.SelectedItem.Value, True)
            Dim strEnd As String = ""
            If IsDate(txtDate.Text) AndAlso ddlEndTime.SelectedItem.Value.ToString = "24" Then
                strEnd = RegionalConversion.FormatSQLDate(Convert.ToDateTime(txtDate.Text).AddDays(1) & " 00:00", True)
            Else
                strEnd = RegionalConversion.FormatSQLDate(txtDate.Text & " " & ddlEndTime.SelectedItem.Value & ":" & ddlEndTimeMinutes.SelectedItem.Value, True)
            End If

            'End Time must be greater than Start Time
            If DateDiff(DateInterval.Minute, CDate(strStart), CDate(strEnd)) < 30 Then
                Master.DisplayError(GetTranslationString("endtoosoon", "End Time must be at least 30 minutes after Start Time"))
                Return False
            End If

            Dim iReservationID As Integer
            If IsNumeric(txtRoomReservationID.Text) Then
                iReservationID = Integer.Parse(txtRoomReservationID.Text)
            Else
                iReservationID = 0
            End If
            If RoomReservationsMaster.TimeSlotIsOpen(iReservationID, ddlRoom.SelectedItem.Value, strStart, strEnd) = False Then
                Master.DisplayError(GetTranslationString("roomnotavailable", "Selected Room is not available for specified time range"))
                Return False
            End If

            Return True
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

            Dim strCatering As String = String.Empty
            If ckLunch.Checked Then
                If ckCoffee.Checked = True And ckDinner.Checked = True Then
                    strCatering = "A"
                ElseIf ckCoffee.Checked = True And ckDinner.Checked = False Then
                    strCatering = "X"
                ElseIf ckCoffee.Checked = False And ckDinner.Checked = True Then
                    strCatering = "Z"
                Else
                    strCatering = "L"
                End If
            Else
                If ckCoffee.Checked Then
                    If ckDinner.Checked = True Then
                        strCatering = "Y"
                    Else
                        strCatering = "T"
                    End If
                Else
                    If ckDinner.Checked Then
                        strCatering = "D"
                    End If
                End If
            End If

            Dim strStart As String = RegionalConversion.FormatSQLDate(SessionManager.SelectedValueDate & " " & ddlStartTime.SelectedItem.Value & ":" & ddlStartTimeMinutes.SelectedItem.Value, True)
            Dim strEnd As String = RegionalConversion.FormatSQLDate(SessionManager.SelectedValueDate & " " & ddlEndTime.SelectedItem.Value & ":" & ddlEndTimeMinutes.SelectedItem.Value, True)
            Dim objDic As New Dictionary(Of String, String)
            objDic.Add("Room", ddlRoom.SelectedItem.Text)
            objDic.Add("StartTime", strStart.Trim())
            objDic.Add("EndTime", strEnd.Trim())
            objDic.Add("Description", txtExpandDescription.Text.Trim())
            objDic.Add("Catering", strCatering.Trim())
            objDic.Add("VideoConferencing", ckVideoConferencing.Checked)
            objDic.Add("UserID", SessionManager.UserID)
            objDic.Add("Team", ddlTeam.SelectedItem.Text)
            Return objDic
        End Function
#End Region

    End Class
End Namespace
