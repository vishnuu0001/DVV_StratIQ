#Region " Imports"
Imports System.Text
Imports System.Data
Imports System.Data.SqlClient
Imports System.DirectoryServices
Imports WebApp.APlus.DataAccess.Connections
Imports WebApp.APlus.DataAccess.Tables

#End Region

Namespace WebApp.APlus.DataAccess.Custom
    Public Class ADAccess
        Public Shared Function GetADUser(ByVal passUser As String) As DirectoryEntry
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUser)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If Not String.IsNullOrEmpty(passUser) Then
                Try
                    Dim ds As DirectorySearcher = New DirectorySearcher
                    Dim strADDomain As String = ConfigurationManager.AppSettings("ADDomain")

                    ds.SearchRoot = New DirectoryEntry("LDAP://" & strADDomain, ConfigurationManager.AppSettings("ADUserID"), ConfigurationManager.AppSettings("ADPassword"))
                    ds.Filter = "(&(objectCategory=person)(samaccountname=" + passUser + "))"
                    ds.SearchScope = SearchScope.Subtree

                    Dim src As SearchResultCollection
                    src = ds.FindAll

                    'we should have ONLY one
                    If src.Count = 1 Then
                        For Each sr As SearchResult In src
                            Return sr.GetDirectoryEntry
                        Next sr
                    Else
                        DataAccess.Tables.EventTracker.AddNoEmail("ADAccess.GetADUser", src.Count.ToString & " user records returned", passUser)
                    End If
                Catch ex As Exception
                    DataAccess.Tables.EventTracker.AddNoEmail("ADAccess.GetADUser", ex.ToString & Environment.NewLine & "SearchScope returned NULL", passUser)
                    Return Nothing
                End Try
            End If

            Return Nothing
        End Function
        Public Shared Function GetADSite(ByVal passADSPath As String) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passADSPath)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim strAR() As String = passADSPath.Split(",")

            'we want the fourth from the last
            strAR = strAR(UBound(strAR) - 3).Split("=")

            'if we have two then return the second one
            If UBound(strAR) = 1 Then
                Return strAR(1)
            Else
                Return ""
            End If
        End Function
    End Class
End Namespace
