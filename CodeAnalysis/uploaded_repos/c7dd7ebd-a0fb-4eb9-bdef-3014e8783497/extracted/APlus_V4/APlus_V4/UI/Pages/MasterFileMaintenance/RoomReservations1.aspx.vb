#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports System.Web.Security
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.DataAccess.Custom
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class RoomReservations1
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Room Scheduling"
        Private Shared ReadOnly ProgramName As String = "RoomReservations1"
        Private bReBind As Boolean = True
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

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnExit.UniqueID + "'),window.event)")

            If SessionManager.WorkingSite.ToString.Length = 0 Then
                Master.DisplayError(GetTranslationString("mustselectsite", "You must have a Working Site selected"))
                pnlCalendar.Visible = False

                Return
            End If

            If SessionManager.RoomReservations <> "" AndAlso SessionManager.RoomReservations.ToString = "Y" Then
                Master.HideAPlusIcon = True
                Master.MinimalIcons = True
            End If

            If Not Page.IsPostBack Then
                If SessionManager.SelectedValueDate <> "" AndAlso IsDate(SessionManager.SelectedValueDate) Then
                    calReserve.SelectedDate = SessionManager.SelectedValueDate
                    calReserve.VisibleDate = calReserve.SelectedDate
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueDate)
                Else
                    calReserve.SelectedDate = Now.Date
                End If
            End If

            LoadRoomReservations()
        End Sub
        Private Sub lbToday_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles lbToday.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            calReserve.SelectedDate = Now().Date
            calReserve.VisibleDate = calReserve.SelectedDate
            LoadRoomReservations()
        End Sub
        Private Sub calReserve_VisibleMonthChanged(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.MonthChangedEventArgs) Handles calReserve.VisibleMonthChanged
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            calReserve.SelectedDate = e.NewDate
            LoadRoomReservations()
        End Sub
        Private Sub calReserve_SelectionChanged(ByVal sender As Object, ByVal e As System.EventArgs) Handles calReserve.SelectionChanged
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            LoadRoomReservations()
        End Sub
        Private Sub calReserve_PreRender(ByVal sender As Object, ByVal e As System.EventArgs) Handles calReserve.PreRender
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If bReBind = True Then
                LoadRoomReservations()
            End If
        End Sub
        Private Sub btnReserveRoom_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnReserveRoom.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.RoomReservationsMode = "AddRow"
            SessionManager.SelectedValueDate = RegionalConversion.FormatSQLDate(calReserve.SelectedDate.ToShortDateString)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RoomReservations2"), False)
        End Sub
        Private Sub LinkButton_Click(ByVal sender As System.Object, ByVal e As System.EventArgs)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim strIDHolder As String = CType(sender, LinkButton).CommandArgument
            SessionManager.SelectedValueReservationID = strIDHolder
            SessionManager.SelectedValueDate = RegionalConversion.FormatSQLDate(calReserve.SelectedDate.ToShortDateString)
            SessionManager.RoomReservationsMode = "EditRow"
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RoomReservations2"), False)
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

            If Not SessionManager.RoomReservations = "Y" Then
                If SessionManager.MasterControlExitProgram <> "" AndAlso SessionManager.MasterControlExitProgram.ToString.Trim.Length > 0 Then
                    Dim strHolder As String = SessionManager.MasterControlExitProgram
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.MasterControlExitProgram)

                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strHolder))
                Else
                    RemoveCurrentProgramandGoBack()
                End If
            Else
                Session.Abandon()

                Dim sScript As New System.Text.StringBuilder
                sScript.Append("<SCRIPT language=""javascript"">" & vbCrLf)
                sScript.Append("window.close();" & vbCrLf)
                sScript.Append("</SCRIPT>" & vbCrLf)
                ClientScript.RegisterStartupScript(Me.GetType, "ForceDefaultToScript", sScript.ToString)
            End If
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadRoomReservations()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            LoadRooms()
            LoadReservations()

            bReBind = False
        End Sub
        Private Sub LoadRooms()
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
                tblSchedule.Rows.Clear()

                Dim objDT As DataTable = RoomMaster.SelectRoomsBySite(SessionManager.WorkingSiteID)

                If objDT.Rows.Count = 0 Then
                    Master.DisplayError(GetTranslationString("noroomattheinn", "No Conference Rooms exist for ") & SessionManager.WorkingSite)
                    pnlCalendar.Visible = False
                End If

                Dim objRow As TableRow
                Dim objCell As TableCell
                Dim iRowCount As Integer = 0
                'Dim strColWidth As String
                'If objDS.Tables(0).Rows.Count > 8 Then
                '    strColWidth = "500"
                'Else
                '    strColWidth = (99 / objDS.Tables(0).Rows.Count).ToString & "%"
                'End If

                'Header Columns
                objRow = New TableRow
                objCell = New TableCell
                objCell.ColumnSpan = objDT.Rows.Count + 1
                objCell.Text = calReserve.SelectedDate.ToShortDateString
                objCell.HorizontalAlign = HorizontalAlign.Center
                objCell.BorderColor = Drawing.Color.DarkGray
                objCell.BorderStyle = BorderStyle.Solid
                objCell.BorderWidth = New Unit(1)
                objCell.Height = New Unit(15)
                objCell.CssClass = "webPlannerCaption"
                objRow.Cells.Add(objCell)
                tblSchedule.Rows.Add(objRow)

                objRow = New TableRow
                objCell = New TableCell
                objCell.Text = "&nbsp;&nbsp;"
                objCell.Width = New Unit(50)
                objCell.HorizontalAlign = HorizontalAlign.Left
                objCell.BorderColor = Drawing.Color.DarkGray
                objCell.BorderStyle = BorderStyle.Solid
                objCell.BorderWidth = New Unit(1)
                objCell.Height = New Unit(15)
                objCell.CssClass = "webPlannerCaption"
                objRow.Cells.Add(objCell)

                For Each dtRow As DataRow In objDT.Rows
                    'Just plug in time with conference rooms
                    objCell = New TableCell
                    objCell.Text = dtRow("Room").ToString
                    objCell.Width = New Unit((100 / objDT.Rows.Count).ToString & "%")
                    objCell.HorizontalAlign = HorizontalAlign.Center
                    objCell.BorderColor = Drawing.Color.DarkGray
                    objCell.BorderStyle = BorderStyle.Solid
                    objCell.BorderWidth = New Unit(1)
                    objCell.Height = New Unit(15)
                    objCell.CssClass = "webPlannerCaption"
                    objRow.Cells.Add(objCell)
                Next

                tblSchedule.Rows.Add(objRow)

                For iHour As Integer = 0 To 23
                    'Hour
                    objRow = New TableRow
                    objCell = New TableCell
                    objCell.Text = "&nbsp;" & iHour.ToString("00") & ":00&nbsp;"
                    objCell.Width = New Unit(50)
                    objCell.BorderColor = Drawing.Color.DarkGray
                    objCell.BorderStyle = BorderStyle.Solid
                    objCell.BorderWidth = New Unit(1)
                    objCell.Height = New Unit(15)
                    objCell.CssClass = "webPlannerSB"
                    objRow.Cells.Add(objCell)

                    For Each dtRow As DataRow In objDT.Rows
                        'Just plug in time with conference rooms
                        objCell = New TableCell
                        objCell.Text = "&nbsp;"
                        objCell.Width = New Unit((100 / objDT.Rows.Count).ToString & "%")
                        objCell.BackColor = Drawing.Color.LightGray
                        objCell.BorderColor = Drawing.Color.DarkGray
                        objCell.BorderStyle = BorderStyle.Solid
                        objCell.BorderWidth = New Unit(1)
                        objCell.Height = New Unit(15)

                        objCell.ID = "R" & iRowCount.ToString & "C" & dtRow("RoomID").ToString

                        objRow.Cells.Add(objCell)
                    Next

                    tblSchedule.Rows.Add(objRow)

                    If iHour < 24 Then
                        iRowCount += 1

                        '1/2 Hour
                        objRow = New TableRow
                        objCell = New TableCell
                        objCell.Text = "&nbsp;" & iHour.ToString("00") & ":30&nbsp;"
                        objCell.Width = New Unit(50)
                        objCell.BorderColor = Drawing.Color.DarkGray
                        objCell.BorderStyle = BorderStyle.Solid
                        objCell.BorderWidth = New Unit(1)
                        objCell.Height = New Unit(15)
                        objCell.CssClass = "webPlannerSB"
                        objRow.Cells.Add(objCell)

                        For Each dtRow As DataRow In objDT.Rows
                            'Just plug in time with conference rooms
                            objCell = New TableCell
                            objCell.Text = "&nbsp;"
                            objCell.Width = New Unit((100 / objDT.Rows.Count).ToString & "%")
                            objCell.BackColor = Drawing.Color.LightGray
                            objCell.BorderColor = Drawing.Color.DarkGray
                            objCell.BorderStyle = BorderStyle.Solid
                            objCell.BorderWidth = New Unit(1)
                            objCell.Height = New Unit(15)

                            objCell.ID = "R" & iRowCount.ToString & "C" & dtRow("RoomID").ToString

                            objRow.Cells.Add(objCell)
                        Next

                        tblSchedule.Rows.Add(objRow)
                    End If

                    iRowCount += 1
                Next
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadRooms ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub LoadReservations()
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
                Dim objDT As DataTable = RoomReservationsMaster.SelectRoomReservationsByDate(SessionManager.WorkingSiteID, RegionalConversion.FormatSQLDate(calReserve.SelectedDate))
                Dim bShowIcons As Boolean = True
                If SessionManager.RoomReservations <> "" AndAlso SessionManager.RoomReservations = "Y" Then
                    bShowIcons = False
                End If

                If objDT.Rows.Count > 0 Then
                    Dim rCell As TableCell
                    Dim strRoomID As String
                    Dim dtStartTime As DateTime
                    Dim iDuration As Integer
                    Dim iStartRow As Integer
                    Dim objLinkButton As LinkButton
                    Dim ctlImage As System.Web.UI.WebControls.Image
                    Dim bAddReturn As Boolean = False
                    Dim strReturn As String

                    For Each dtRow As DataRow In objDT.Rows
                        'first, get the roomid
                        strRoomID = dtRow("RoomID").ToString

                        'get the starting time
                        dtStartTime = dtRow("StartTime")
                        iDuration = DateDiff(DateInterval.Minute, dtRow("StartTime"), dtRow("EndTime")) / 30

                        'find the start row
                        'REMEMBER - 6:00 AM is row 0
                        'Just get the hour and subtract 6
                        iStartRow = (dtStartTime.TimeOfDay.Hours) * 2
                        If dtStartTime.TimeOfDay.Minutes = 30 Then
                            iStartRow += 1
                        End If

                        For iCounter As Integer = iStartRow To iStartRow + iDuration - 1
                            If iCounter > 48 Then
                                'ignore this row as it goes beyond the last visible time
                            Else
                                Try
                                    rCell = DirectCast(Master.FindControl("ContentPlaceholder1").FindControl("R" & iCounter.ToString & "C" & strRoomID), TableCell)
                                Catch ex As Exception
                                    rCell = Nothing
                                End Try

                                If rCell IsNot Nothing Then
                                    rCell.VerticalAlign = VerticalAlign.Top
                                    rCell.HorizontalAlign = HorizontalAlign.Center

                                    rCell.BackColor = Drawing.Color.LightBlue

                                    If iCounter = iStartRow Then
                                        rCell.RowSpan = iDuration

                                        If bShowIcons Then
                                            'if this required catering, add the cater icon
                                            If dtRow("Catering").ToString.Trim.Length > 0 Then
                                                Select Case dtRow("Catering").ToString.ToUpper
                                                    Case "L"
                                                        ctlImage = New System.Web.UI.WebControls.Image
                                                        ctlImage.ImageUrl = Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar + "\images\lunch.gif"
                                                        ctlImage.Width = New Unit(20)
                                                        ctlImage.Height = New Unit(16)
                                                        rCell.Controls.Add(ctlImage)

                                                        bAddReturn = True
                                                    Case "T"
                                                        ctlImage = New System.Web.UI.WebControls.Image
                                                        ctlImage.ImageUrl = Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar + "\images\Tea.gif"
                                                        ctlImage.Width = New Unit(16)
                                                        ctlImage.Height = New Unit(16)
                                                        rCell.Controls.Add(ctlImage)

                                                        bAddReturn = True
                                                    Case "D"
                                                        ctlImage = New System.Web.UI.WebControls.Image
                                                        ctlImage.ImageUrl = Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar + "\images\dinner.gif"
                                                        ctlImage.Width = New Unit(24)
                                                        ctlImage.Height = New Unit(16)
                                                        rCell.Controls.Add(ctlImage)

                                                        bAddReturn = True
                                                    Case "A"
                                                        'add all three icons
                                                        ctlImage = New System.Web.UI.WebControls.Image
                                                        ctlImage.ImageUrl = Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar + "\images\lunch.gif"
                                                        ctlImage.Width = New Unit(20)
                                                        ctlImage.Height = New Unit(16)
                                                        rCell.Controls.Add(ctlImage)

                                                        ctlImage = New System.Web.UI.WebControls.Image
                                                        ctlImage.ImageUrl = Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar + "\images\Tea.gif"
                                                        ctlImage.Width = New Unit(16)
                                                        ctlImage.Height = New Unit(16)
                                                        rCell.Controls.Add(ctlImage)

                                                        ctlImage = New System.Web.UI.WebControls.Image
                                                        ctlImage.ImageUrl = Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar + "\images\dinner.gif"
                                                        ctlImage.Width = New Unit(24)
                                                        ctlImage.Height = New Unit(16)
                                                        rCell.Controls.Add(ctlImage)

                                                        bAddReturn = True
                                                    Case "X"
                                                        ctlImage = New System.Web.UI.WebControls.Image
                                                        ctlImage.ImageUrl = Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar + "\images\lunch.gif"
                                                        ctlImage.Width = New Unit(20)
                                                        ctlImage.Height = New Unit(16)
                                                        rCell.Controls.Add(ctlImage)

                                                        ctlImage = New System.Web.UI.WebControls.Image
                                                        ctlImage.ImageUrl = Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar + "\images\Tea.gif"
                                                        ctlImage.Width = New Unit(16)
                                                        ctlImage.Height = New Unit(16)
                                                        rCell.Controls.Add(ctlImage)

                                                        bAddReturn = True
                                                    Case "Y"
                                                        ctlImage = New System.Web.UI.WebControls.Image
                                                        ctlImage.ImageUrl = Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar + "\images\Tea.gif"
                                                        ctlImage.Width = New Unit(16)
                                                        ctlImage.Height = New Unit(16)
                                                        rCell.Controls.Add(ctlImage)

                                                        ctlImage = New System.Web.UI.WebControls.Image
                                                        ctlImage.ImageUrl = Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar + "\images\dinner.gif"
                                                        ctlImage.Width = New Unit(24)
                                                        ctlImage.Height = New Unit(16)
                                                        rCell.Controls.Add(ctlImage)

                                                        bAddReturn = True
                                                    Case "Z"
                                                        ctlImage = New System.Web.UI.WebControls.Image
                                                        ctlImage.ImageUrl = Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar + "\images\lunch.gif"
                                                        ctlImage.Width = New Unit(20)
                                                        ctlImage.Height = New Unit(16)
                                                        rCell.Controls.Add(ctlImage)

                                                        ctlImage = New System.Web.UI.WebControls.Image
                                                        ctlImage.ImageUrl = Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar + "\images\dinner.gif"
                                                        ctlImage.Width = New Unit(24)
                                                        ctlImage.Height = New Unit(16)
                                                        rCell.Controls.Add(ctlImage)

                                                        bAddReturn = True
                                                End Select
                                            End If

                                            'if this is a video conference, add the video icon
                                            If dtRow("VideoConferencing") = True Then
                                                ctlImage = New System.Web.UI.WebControls.Image
                                                ctlImage.ImageUrl = Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar + "\images\Video.gif"
                                                ctlImage.Width = New Unit(12)
                                                ctlImage.Height = New Unit(12)
                                                rCell.Controls.Add(ctlImage)

                                                bAddReturn = True
                                            End If
                                        End If

                                        If bAddReturn Then
                                            strReturn = "<BR>"
                                        Else
                                            strReturn = ""
                                        End If

                                        objLinkButton = New LinkButton
                                        objLinkButton.ID = "lnk" & dtRow("RoomReservationID")
                                        objLinkButton.CommandArgument = dtRow("RoomReservationID")
                                        If dtRow("Description").ToString.Length > 15 Then
                                            objLinkButton.Text = strReturn & Left(dtRow("Description").ToString, 12) & "..."
                                        Else
                                            objLinkButton.Text = strReturn & Left(dtRow("Description").ToString, 15)
                                        End If
                                        AddHandler objLinkButton.Click, AddressOf LinkButton_Click

                                        rCell.Controls.Add(objLinkButton)
                                        rCell.ToolTip = dtRow("Description").ToString & " -- " & CDate(dtRow("StartTime")).ToShortTimeString & " - " & CDate(dtRow("EndTime")).ToShortTimeString
                                    Else
                                        tblSchedule.Rows(iCounter + 2).Cells.Remove(rCell)
                                    End If
                                End If
                            End If
                        Next
                    Next
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadReservations ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

    End Class
End Namespace
