#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports System.Web.Security
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.DataAccess.Custom
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class RoomReservations3
        Inherits PrinterFriendlyBase

#Region " Private Variables"
        Private iRoomReservationID As Integer = 0
#End Region

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "RoomReservations3", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            iRoomReservationID = Request.Params("RoomReservationID")
            LoadSelectedRecord()
            lblPrintDate.Text = "Printed : " + Now.ToString(SessionManager.DateTimeFormat)
        End Sub
#End Region

#Region " Custom Methods"
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
                Dim dt As DataTable = RoomReservationsMaster.SelectRoomReservation(iRoomReservationID)

                If dt.Rows.Count > 0 Then
                    Dim dr As DataRow = dt.Rows(0)
                    Dim dtStart As DateTime
                    Dim dtEnd As DateTime
                    Dim dtMaintenance As DateTime

                    txtRoomReservationID.Text = iRoomReservationID.ToString
                    txtSite.Text = dr("Site").ToString
                    txtRoom.Text = dr("Room").ToString

                    dtStart = dr("StartTime")
                    dtEnd = dr("EndTime")

                    txtStartTime.Text = dtStart.ToString(SessionManager.DateTimeFormat)
                    txtEndTime.Text = dtEnd.ToString(SessionManager.DateTimeFormat)
                    txtExpandDescription.Text = dr("Description").ToString

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

                    txtTeam.Text = dr("Team").ToString
                    txtUserID.Text = UserMaster.GetUserFullName(dr("UserID").ToString)
                    txtMaintenanceUserID.Text = UserMaster.GetUserFullName(dr("MaintenanceUserID").ToString)
                    dtMaintenance = dr("MaintenanceDate")
                    txtMaintenanceDate.Text = dtMaintenance.ToString(SessionManager.DateTimeFormat)
                End If
            Catch Exc As Exception
                Master.DisplayErrors("RoomReservations3 - LoadSelectedRecord ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

    End Class
End Namespace
