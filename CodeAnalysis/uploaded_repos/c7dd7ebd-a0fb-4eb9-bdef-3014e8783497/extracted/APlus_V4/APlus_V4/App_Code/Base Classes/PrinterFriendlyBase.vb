#Region "Imports"
Imports System.Threading
Imports System.Globalization
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus
    Public Class PrinterFriendlyBase
        Inherits System.Web.UI.Page

#Region " Page Load"
        Private Sub Page_Load(ByVal sender As Object, ByVal e As System.EventArgs) Handles MyBase.Load
            DisablePageCaching()

            ValidateRegionalSettings()
        End Sub
#End Region

#Region " Regional Functions"
        Private Sub ValidateRegionalSettings()
            Dim strCulturePref As String

            If SessionManager.CulturePref = String.Empty OrElse SessionManager.CulturePref = "" Then
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
#End Region

    End Class
End Namespace
