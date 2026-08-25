#Region "Imports"
Imports System.Threading
Imports System.Globalization
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus
    Public Class RegionalConversion
        Public Shared Sub ValidateRegionalSettings()
            Dim strCulturePref As String

            If SessionManager.CulturePref = "" OrElse SessionManager.CulturePref = String.Empty Then
                strCulturePref = UserMaster.GetUserCulture(SessionManager.UserID)

                SessionManager.CulturePref = strCulturePref
            Else
                strCulturePref = SessionManager.CulturePref
            End If

            If strCulturePref.Trim.Length > 0 Then
                Try
                    Thread.CurrentThread.CurrentCulture = CultureInfo.CreateSpecificCulture(strCulturePref)
                Catch ex As Exception
                    Thread.CurrentThread.CurrentCulture = New CultureInfo(strCulturePref)
                End Try

                SessionManager.DateFormat = Thread.CurrentThread.CurrentCulture.DateTimeFormat().ShortDatePattern
                SessionManager.DateTimeFormat = SessionManager.DateFormat + " HH:mm:ss"
                Thread.CurrentThread.CurrentUICulture = Thread.CurrentThread.CurrentCulture
            Else
                SessionManager.DateFormat = "yyyy/MM/dd"
                SessionManager.DateTimeFormat = "yyyy/MM/dd HH:mm:ss"
            End If
        End Sub
        Public Shared Function FormatSQLTime(ByVal passTime As String) As String
            'Currently working under the assumption that the formation function will
            'always use the thread culture.
            Dim strHolder As String = ""

            If SessionManager.CulturePref = String.Empty Or SessionManager.CulturePref = "" Then
                'just return the date as it should already be formmated yyyy/mm/dd
                strHolder = passTime
            Else
                If IsDate(passTime) Then
                    strHolder += Format(Convert.ToDateTime(passTime), "HH:mm:ss").Replace(".", ":")
                End If
            End If

            Return strHolder
        End Function
        Public Shared Function FormatSQLDate(ByVal passDate As String) As String
            Return FormatSQLDate(passDate, False)
        End Function
        Public Shared Function FormatSQLDate(ByVal passDate As String, ByVal blnFormatTime As Boolean) As String
            'Currently working under the assumption that the formation function will
            'always use the thread culture.
            Dim strHolder As String = ""

            If SessionManager.CulturePref = String.Empty Or SessionManager.CulturePref = "" Then
                'just return the date as it should already be formmated yyyy/mm/dd
                strHolder = passDate
            Else
                If IsDate(passDate) Then
                    If CDate(passDate) < New Date(1990, 1, 1) Then
                        Return ""
                    End If

                    If blnFormatTime Then
                        If Thread.CurrentThread.CurrentUICulture.DateTimeFormat.TimeSeparator <> ":" Then
                            strHolder = Format(Convert.ToDateTime(passDate), "yyyy/MM/dd")
                            strHolder += " "
                            strHolder += Format(Convert.ToDateTime(passDate), "HH:mm:ss").Replace(Thread.CurrentThread.CurrentUICulture.DateTimeFormat.TimeSeparator, ":")
                        Else
                            strHolder = Format(Convert.ToDateTime(passDate), "yyyy/MM/dd HH:mm:ss")
                        End If
                    Else
                        strHolder = Format(Convert.ToDateTime(passDate), "yyyy/MM/dd")
                    End If
                End If
            End If

            Return strHolder
        End Function
        Public Shared Function FormatSQLSingle(ByVal passNumber As String) As String
            Return FormatSQLSingle(passNumber, "")
        End Function
        Public Shared Function FormatSQLSingle(ByVal passNumber As String, ByVal passFormatString As String) As String
            'number begin passed in is assumed to be in US format
            'verify that the number is formatted for the current culture for conversion to single
            If Thread.CurrentThread.CurrentCulture.NumberFormat.NumberDecimalSeparator <> "." Then
                passNumber = passNumber.Replace(".", Thread.CurrentThread.CurrentCulture.NumberFormat.NumberDecimalSeparator)
            End If

            If passNumber.Trim.Length = 0 Then
                Return ""
            End If

            'convert the numeric string value to a single
            Dim sHolder As Double = CType(passNumber, Double)
            Dim strReturn As String

            'perform any passed in formatting on the number
            If passFormatString.Trim.Length > 0 Then
                strReturn = Format(sHolder, passFormatString)
            Else
                strReturn = sHolder.ToString
            End If

            'change any culture specific characters back to en-US so value can be written to the database
            If Thread.CurrentThread.CurrentCulture.NumberFormat.NumberDecimalSeparator <> "." Then
                strReturn = strReturn.Replace(Thread.CurrentThread.CurrentCulture.NumberFormat.NumberDecimalSeparator, ".")
            End If

            Return strReturn
        End Function
        Public Shared Function FormatLocalSingle(ByVal passNumber As String) As String
            Return FormatLocalSingle(passNumber, "")
        End Function
        Public Shared Function FormatLocalSingle(ByVal passNumber As String, ByVal passFormatString As String) As String
            'number begin passed in is assumed to be in US format
            'verify that the number is formatted for the current culture for conversion to single
            If Thread.CurrentThread.CurrentCulture.NumberFormat.NumberDecimalSeparator <> "." Then
                passNumber = passNumber.Replace(".", Thread.CurrentThread.CurrentCulture.NumberFormat.NumberDecimalSeparator)
            End If

            If Not IsNumeric(passNumber) Then
                Return ""
            End If

            'convert the numeric string value to a single
            Dim sHolder As Double = CType(passNumber, Double)
            Dim strReturn As String

            'perform any passed in formatting on the number
            If passFormatString.Trim.Length > 0 Then
                strReturn = Format(sHolder, passFormatString)
            Else
                strReturn = sHolder.ToString
            End If

            Return strReturn
        End Function
    End Class
End Namespace
