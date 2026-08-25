#Region " Imports"
Imports System.Reflection
Imports System.Data
Imports System.Data.SqlClient
Imports System.Net.Mail
Imports System.Diagnostics
Imports System.Text
Imports WebApp.APlus.DataAccess.Connections
Imports System.IO
Imports System.Web
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class EventTracker

#Region " Add"
        Public Shared Sub Add(ByVal passEventName As String, ByVal passMessage As String, ByVal passUserID As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Dim cnSubConnection As New ApplicationConnection
            cnSubConnection.OpenConnection(cnMasterConnection)

            Try
                AddNoEmail(passEventName, passMessage, passUserID, cnMasterConnection)

                Dim strTo As String = String.Empty
                Dim strFrom As String = ConfigurationManager.AppSettings("SendEmailFrom")
                Dim dtEmailAddress As DataTable = GetEventLogEmailAddressList()

                If dtEmailAddress IsNot Nothing AndAlso dtEmailAddress.Rows.Count > 0 Then
                    For Each dr As DataRow In dtEmailAddress.Rows
                        If Not Convert.ToBoolean(dr.Item("EmailInactive")) Then
                            strTo &= dr.Item("EmailAddress").ToString & ","
                        End If
                    Next

                    'Remove the last extra comma
                    If strTo.Trim.Length > 0 AndAlso strTo.EndsWith(",") Then
                        strTo = strTo.Remove(strTo.Length - 1, 1)
                    End If

                    If strTo.Length > 0 Then
                        'Construct the Email message
                        Dim strMessage As String = String.Format("Program Name:  {1} {0}" _
                                                               & "User ID:       {2} {0}" _
                                                               & "Event Time:    {3} {0}{0}{4}", vbCrLf, passEventName, passUserID, Now.ToString(), passMessage)

                        Dim MailClient As New SmtpClient
                        MailClient.Host = ConfigurationManager.AppSettings("SMTPServer")
                        MailClient.Send(strFrom, strTo, "Event Notification", strMessage.Trim())
                    End If
                End If
            Catch Sxc As HttpException
                'if we didn't send an email, don't worry - just write another line in the event log
                If InStr(Sxc.Message, "CDO.Message") > 0 Then
                    AddNoEmail(passEventName, passMessage, passUserID, cnMasterConnection)
                Else
                    EventLog.WriteEntry(ConfigurationManager.AppSettings("EventLogSource"), Sxc.ToString, Diagnostics.EventLogEntryType.Error)
                End If
            Catch Exc As Exception
                Try
                    EventLog.WriteEntry(ConfigurationManager.AppSettings("EventLogSource"), Exc.ToString, Diagnostics.EventLogEntryType.Error)
                Catch ex As Exception
                    'do nothing here
                End Try
            Finally
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        <Obsolete("This method is deprecated, use Add with No EventLogType instead.")> _
        Public Shared Sub Add(ByVal EventName As String, ByVal EventLogType As String, _
                              ByVal Message As String, ByVal UserID As String, _
                              Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Add(EventName, Message, UserID, cnMasterConnection)
        End Sub
        Public Shared Sub AddNoEmail(ByVal passEventName As String, ByVal passMessage As String, _
                                     ByVal passUserID As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Dim cnSubConnection As New ApplicationConnection
            Dim cmEventLog As New SqlCommand("spInsEventLog", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmEventLog
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@EventName", passEventName.Trim())
                    .Parameters.AddWithValue("@Message", passMessage.Trim())
                    .Parameters.AddWithValue("@UserID", passUserID.Trim())
                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Try
                    EventLog.WriteEntry(ConfigurationManager.AppSettings("EventLogSource"), Exc.ToString, Diagnostics.EventLogEntryType.Error)
                Catch ex As Exception
                    'do nothing here
                End Try
            Finally
                cmEventLog.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " Get EventLog EmailAddress"
        Public Shared Function GetEventLogEmailAddressList(Optional ByRef cnMasterConnection As SqlConnection = Nothing, _
                                                           Optional ByRef trans As SqlTransaction = Nothing) As DataTable

            Dim cnSubConnection As New ApplicationConnection
            Try
                Dim ds As New DataTable
                Dim da As New SqlDataAdapter(New SqlCommand("spSelEventLogEmailAddressMaster", cnSubConnection.OpenConnection(cnMasterConnection)))
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                If Not trans Is Nothing Then
                    da.SelectCommand.Transaction = trans
                End If

                da.Fill(ds)

                Return ds
            Finally
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " Get Function Information"
        Public Overloads Shared Function GetFunctionInformation(ByVal passFunction As MethodBase, ByVal ParamArray passParValues As String()) As String
            Dim strReturn As String = String.Empty
            Dim parmInfo As ParameterInfo() = passFunction.GetParameters
            Dim i As Integer = parmInfo.Length - 1
            For x As Integer = 0 To parmInfo.Length - 1
                If parmInfo(x).IsOptional = False Or Not String.IsNullOrEmpty(passParValues(x)) Then
                    If x = i Then
                        strReturn += parmInfo(x).Name.Trim() & ":=" & passParValues(x).ToString.Trim()
                    Else
                        strReturn += parmInfo(x).Name.Trim() & ":=" & passParValues(x).ToString.Trim() & ", "
                    End If
                Else
                    If x = i Then
                        strReturn += parmInfo(x).Name.Trim() & ":="
                    Else
                        strReturn += parmInfo(x).Name.Trim() & ":=, "
                    End If
                End If
            Next
            Return passFunction.Name & "(" & strReturn.Trim() & ")"
        End Function
#End Region

    End Class
End Namespace