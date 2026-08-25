Imports System.Data

Namespace WebApp.APlus.UI.UserControls
    Partial Class TeamMeetingCalendarEvent
        Inherits System.Web.UI.Page

        Protected Sub Page_Load(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.Load
            Try
                If Request.Params("TeamMeetingID") IsNot Nothing AndAlso IsNumeric(Request.Params("TeamMeetingID").ToString) Then
                    Dim objDT As DataTable = DataAccess.Tables.TeamMeetings.SelectTeamMeeting(Convert.ToInt32(Request.Params("TeamMeetingID").ToString))
                    If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                        Dim dtRow As DataRow = objDT.Rows(0)
                        Dim dtDate As DateTime
                        Dim strDate As String
                        Dim strLength As String()
                        Dim strAgenda As String
                        Dim sScript As New System.Text.StringBuilder

                        sScript.Append("BEGIN:VCALENDAR" & Environment.NewLine)
                        sScript.Append("VERSION:2.0" & Environment.NewLine)
                        sScript.Append("METHOD:PUBLISH" & Environment.NewLine)
                        sScript.Append("BEGIN:VEVENT" & Environment.NewLine)

                        dtDate = Convert.ToDateTime(Convert.ToDateTime(dtRow("MeetingDate")).ToString("yyyy/MM/dd") & " " & dtRow("MeetingTime").ToString)
                        strDate = dtDate.ToString("yyyyMMddTHHmmss")
                        sScript.Append("DTSTART:" & strDate & Environment.NewLine)

                        strLength = dtRow("MeetingLength").ToString.Split(" ")
                        If IsNumeric(strLength(0)) Then
                            If Convert.ToDecimal(strLength(0)) > 10 Then
                                dtDate = dtDate.AddMinutes(Convert.ToDecimal(strLength(0)))
                            Else
                                dtDate = dtDate.AddHours(Convert.ToDecimal(strLength(0)))
                            End If
                        End If
                        strDate = dtDate.ToString("yyyyMMddTHHmmss")
                        sScript.Append("DTEND:" & strDate & Environment.NewLine)

                        sScript.Append("SUMMARY:" & dtRow("Team").ToString.Trim & " : " & dtRow("TeamName").ToString.Trim & " Team Meeting" & Environment.NewLine)

                        strAgenda = "<!doctype html public><html><body>Agenda:" & "<br />"
                        strAgenda += dtRow("Agenda").ToString.Trim & "<br /><br />"

                        Dim strURL As String = "http://" & ConfigurationManager.AppSettings("ApplicationServerDNS").ToString & "/aplus/UI/Pages/DataCollectionPrograms/TeamMeetings3.aspx?MeetingID=" & Request.Params("TeamMeetingID").ToString
                        strAgenda += "<a href=" & strURL & ">" & GetTranslationString("Click Here to view Team Meeting") & "</a><br /><br />"

                        strURL = "http://" & ConfigurationManager.AppSettings("ApplicationServerDNS").ToString & "/aplus/login.aspx"
                        strURL += "?auto=y&team=" & dtRow("TeamID").ToString
                        strAgenda += "<a href=" & strURL & ">" & GetTranslationString("Click Here to link to Team Status") & "</a><br />"
                        strAgenda += "</body></html>"

                        sScript.Append("X-ALT-DESC;FMTTYPE=text/html:" & strAgenda & Environment.NewLine)
                        sScript.Append("LOCATION:" & dtRow("MeetingLocation").ToString.Trim & Environment.NewLine)

                        sScript.Append("END:VEVENT" & Environment.NewLine)
                        sScript.Append("END:VCALENDAR" & Environment.NewLine)

                        Response.Clear()
                        Response.ContentType = "text/calendar"
                        Response.ContentEncoding = Encoding.UTF8
                        Response.Charset = "utf-8"
                        Response.AddHeader("Content-Disposition", "attachment;filename=TeamMeeting" & Request.Params("TeamMeetingID").ToString & ".ics")
                        Response.Buffer = True
                        Response.Write(sScript.ToString)
                        Response.End()
                    End If
                End If
            Catch ex As Exception
                Return
            End Try
        End Sub
    End Class
End Namespace
