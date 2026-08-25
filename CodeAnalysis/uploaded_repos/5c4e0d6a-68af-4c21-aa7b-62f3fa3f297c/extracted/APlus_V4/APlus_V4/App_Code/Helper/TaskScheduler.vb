#Region " Imports "
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.DataAccess.Custom
Imports System.Threading
Imports System.Globalization
Imports System.IO
Imports System.Web.Mail
#End Region

Namespace WebApp.APlus
    Public Class TaskScheduler

#Region " Calculate Next Run Time "
        Public Shared Function GetScheduleRegularExpression() As String
            'Reg Ex Validation Code
            '
            '(([1-9]|[1-2][0-9]|[3][0-1]){1}(,([1-9]|[1-2][0-9]|[3][0-1]){1}){0,8})?
            '   1,3,15 - The 1st, 3rd and 15th of the month

            Return "^(([1-9]|[1-2][0-9]|[3][0-1]){1}(,([1-9]|[1-2][0-9]|[3][0-1]){1}){0,8})?$"
        End Function
        Public Shared Function CalculateNextExecution(ByVal passScheduleCode As String, ByVal passScheduleTime As String) As String
            Try
                If passScheduleCode.Trim.Length = 0 Then
                    Return ""
                Else
                    Dim dtNextRun As Date = TaskScheduler.CalculateNextRunTime(passScheduleCode, passScheduleTime)
                    If dtNextRun <> Nothing Then
                        Return RegionalConversion.FormatSQLDate(dtNextRun.ToString, True)
                    Else
                        Return ""
                    End If
                End If
            Catch ex As Exception
                Return ""
            End Try
        End Function
        Public Shared Function CalculateNextRunTime(ByVal passScheduleCode As String) As DateTime
            Return CalculateNextRunTime(passScheduleCode, "")
        End Function
        Public Shared Function CalculateNextRunTime(ByVal passScheduleCode As String, ByVal passTime As String) As DateTime
            Dim dtNewDate As Date = Nothing

            Try
                If passTime.Length = 4 Then
                    passTime = passTime.Insert(2, ":")
                End If

                dtNewDate = CType(Now.Date + " 00:00", Date)
                Dim iHolder As Integer = 0

                If passScheduleCode.Length > 0 Then
                    Dim iCurrentDay As Integer = Now.Day

                    If Not passScheduleCode.Contains(",") AndAlso IsNumeric(passScheduleCode) Then
                        iHolder = CInt(passScheduleCode)

                        If iHolder > iCurrentDay Then
                            dtNewDate = dtNewDate.AddDays(iHolder - iCurrentDay)
                        Else
                            dtNewDate = dtNewDate.AddMonths(1)
                            dtNewDate = dtNewDate.AddDays(iHolder - iCurrentDay)
                        End If
                    Else
                        If passScheduleCode.Contains(",") Then
                            Dim strDays() As String = passScheduleCode.Split(",")
                            Dim iDay As Integer
                            Dim bMonthForward As Boolean = False

                            For Each strDay As String In strDays
                                iDay = CInt(strDay)

                                If iDay >= dtNewDate.Day Then
                                    dtNewDate = dtNewDate.AddDays(iDay - dtNewDate.Day)

                                    bMonthForward = True
                                    Exit For
                                End If
                            Next

                            If Not bMonthForward Then
                                For Each strDay As String In strDays
                                    iDay = CInt(strDay)

                                    dtNewDate = dtNewDate.AddMonths(1)
                                    dtNewDate = dtNewDate.AddDays(iDay - dtNewDate.Day)

                                    Exit For
                                Next
                            End If
                        End If
                    End If

                    If passTime.Trim.Length > 0 AndAlso IsDate(dtNewDate.Date + " " + passTime) Then
                        dtNewDate = dtNewDate.Date + " " + passTime
                    End If
                Else
                    dtNewDate = Nothing
                End If
            Catch ex As Exception
                dtNewDate = Nothing
            End Try

            Return dtNewDate
        End Function
#End Region

    End Class
End Namespace
