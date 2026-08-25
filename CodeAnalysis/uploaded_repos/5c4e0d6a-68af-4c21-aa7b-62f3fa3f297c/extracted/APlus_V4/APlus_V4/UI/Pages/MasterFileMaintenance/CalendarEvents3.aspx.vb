#Region " Imports"
Imports System.Data
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class CalendarEvents3
        Inherits PrinterFriendlyBase

#Region " Private Variables"
        Private intCalendarEventID As Integer = 0
#End Region

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "CalendarEvents3", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            intCalendarEventID = Request.Params("CalendarEventID")
            LoadSelectedRecord()
            lblPrintDate.Text = "Printed : " + Now.ToShortDateString + " " + Now.ToShortTimeString
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
                Dim dt As DataTable = CalendarEvents.SelectCalendarEventByID(intCalendarEventID)
                If dt IsNot Nothing AndAlso dt.Rows.Count <> 0 Then
                    Dim dr As DataRow = dt.Rows(0)
                    txtSite.Text = dr("Site").ToString
                    txtEventType.Text = dr("EventType").ToString
                    txtEvent.Text = dr("Event").ToString
                    If IsDate(dr("EventDate")) Then
                        txtDate.Text = Convert.ToDateTime("" + dr("EventDate")).ToShortDateString
                    Else
                        txtDate.Text = String.Empty
                    End If
                    txtTime.Text = dr("EventTime").ToString
                    txtDescription.Text = dr("EventDescription").ToString
                End If
            Catch
                'can't do too much here!
            End Try
        End Sub
#End Region

    End Class
End Namespace

