#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports System.Resources
Imports System.Globalization
Imports System.Web.Security
Imports System.IO
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus
    Public Module CultureTranslation
        Public strTranslationApplicationName As String = ConfigurationManager.AppSettings("ApplicationNameRef")

#Region " Translation Methods"
        Public Function GetTranslationString(ByVal passKey As String) As String
            Return GetTranslationString(passKey, passKey)
        End Function
        Public Function GetTranslationString(ByVal passKey As String, ByVal passDefault As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As String
            Return GetTranslationString(SessionManager.CulturePref, passKey, passDefault, cnMasterConnection)
        End Function
        Public Function GetTranslationString(ByVal passCulture As String, ByVal passKey As String, ByVal passDefault As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passKey, passDefault, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If passCulture = String.Empty Then
                Return passDefault
            ElseIf passKey.Trim.Length = 0 Then
                Return passDefault
            End If

            'Check to see if the culture requires localization
            'If not, return original value
            Dim strCulture As String = passCulture.ToLower
            'Do not bother getting a value if the web config settings says not to.
            If ConfigurationManager.AppSettings(strCulture) Is Nothing OrElse ConfigurationManager.AppSettings(strCulture).ToString.Trim.ToUpper <> "ON" Then
                Return passDefault
            End If

            Dim cnSubConnection As New CultureTranslationConnection

            Try
                'Store the original string without any translation
                Dim strOriginal As String = passKey
                Dim strKey As String = String.Empty  ' Resource Key
                Dim strValue As String = String.Empty ' Resource Value

                'Remove : - and &nbsp; before translating
                strKey = Replace(passKey, ":", "", 1, , CompareMethod.Text)
                strKey = Replace(strKey, "-", "", 1, , CompareMethod.Text)
                strKey = Replace(strKey, "&nbsp;", "", 1, , CompareMethod.Text)

                ' ************************************************************************
                '
                ' Resource Values are stored in a two tier hashtable application variable
                ' Top level hashtable, culture code is the key, the value is a hashtable
                ' Bottom level hashtable contains the resource key value pairs
                '
                ' ************************************************************************

                Dim htCultureHash As Hashtable
                Dim htResourceHash As Hashtable

                ' Top Level Hash
                If HttpContext.Current.Application("CultureCache") IsNot Nothing AndAlso _
                TypeOf HttpContext.Current.Application("CultureCache") Is Hashtable Then
                    htCultureHash = DirectCast(HttpContext.Current.Application("CultureCache"), Hashtable)
                Else
                    htCultureHash = New Hashtable()
                End If

                ' Bottom Level Hash
                If htCultureHash.ContainsKey(strCulture) Then
                    htResourceHash = htCultureHash(strCulture)
                Else
                    htResourceHash = New Hashtable()
                End If

                If strKey.Trim.Length = 0 Then
                    Return passDefault
                End If

                ' If the hash already contains the key use it
                ' or go to the database to get it
                If htResourceHash.ContainsKey(strKey) Then
                    strValue = htResourceHash(strKey).ToString
                Else
                    Dim objDT As DataTable = SelectCultureTranslationByKey(strCulture, strKey, passDefault)
                    If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                        strValue = objDT.Rows(0)("ResourceValue").ToString
                    End If

                    If strValue.Trim.Length = 0 Then
                        strValue = passDefault
                    End If

                    If htResourceHash.ContainsKey(strKey) Then
                        htResourceHash.Remove(strKey)
                    End If
                    htResourceHash.Add(strKey, strValue)

                    If htCultureHash.ContainsKey(strCulture) Then
                        htCultureHash.Remove(strCulture)
                    End If
                    htCultureHash.Add(strCulture, htResourceHash)
                    HttpContext.Current.Application("CultureCache") = htCultureHash
                End If

                Return strValue
            Catch Exc As Exception
                Throw
            Finally
                cnSubConnection.CloseCultureTranslationConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " Select Methods"
        Public Function SelectCultureTranslationByKey(ByVal passCultureCode As String, _
                                                      ByVal passResourceKey As String, _
                                                      Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Return SelectCultureTranslationByKey(strTranslationApplicationName, passCultureCode, passResourceKey, "", cnMasterConnection)
        End Function
        Public Function SelectCultureTranslationByKey(ByVal passCultureCode As String, _
                                                      ByVal passResourceKey As String, _
                                                      ByVal passDefaultValue As String, _
                                                      Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Return SelectCultureTranslationByKey(strTranslationApplicationName, passCultureCode, passResourceKey, passDefaultValue, cnMasterConnection)
        End Function
        Public Function SelectCultureTranslationByKey(ByVal passResourceType As String, _
                                                      ByVal passCultureCode As String, _
                                                      ByVal passResourceKey As String, _
                                                      ByVal passDefaultValue As String, _
                                                      Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passResourceType, passCultureCode, passResourceKey, passDefaultValue, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New CultureTranslationConnection
            Dim cmSelect As New SqlCommand("spSelResourceValueByKey", cnSubConnection.OpenCultureTranslationConnection(cnMasterConnection))
            Dim daSelect As New SqlDataAdapter(cmSelect)
            Dim ds As New DataTable

            Try
                With cmSelect
                    .CommandType = CommandType.StoredProcedure

                    .Parameters.AddWithValue("@ResourceType", passResourceType)
                    .Parameters.AddWithValue("@CultureCode", passCultureCode)
                    .Parameters.AddWithValue("@ResourceKey", passResourceKey)
                    .Parameters.AddWithValue("@DefaultValue", passDefaultValue)

                    daSelect.Fill(ds)

                    Return ds
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                cnSubConnection.CloseCultureTranslationConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " DB Table Methods"
        Public Sub InsertResourceValue(ByVal passCultureCode As String, _
                                       ByVal passResourceKey As String, _
                                       ByVal passDefaultValue As String, _
                                       Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passCultureCode, passResourceKey, passDefaultValue, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            InsertResourceValue(strTranslationApplicationName, passCultureCode, passResourceKey, passDefaultValue, "", cnMasterConnection)
        End Sub
        Public Sub InsertResourceValue(ByVal passCultureCode As String, _
                                       ByVal passResourceKey As String, _
                                       ByVal passDefaultValue As String, _
                                       ByVal passResourceValue As String, _
                                       Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passCultureCode, passResourceKey, passDefaultValue, passResourceValue, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            InsertResourceValue(strTranslationApplicationName, passCultureCode, passResourceKey, passDefaultValue, passResourceValue, cnMasterConnection)
        End Sub
        Public Sub InsertResourceValue(ByVal passResourceType As String, _
                                       ByVal passCultureCode As String, _
                                       ByVal passResourceKey As String, _
                                       ByVal passDefaultValue As String, _
                                       ByVal passResourceValue As String, _
                                       Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passResourceType, _
                                                                                     passCultureCode, _
                                                                                     passResourceKey, _
                                                                                     passDefaultValue, _
                                                                                     passResourceValue, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New CultureTranslationConnection
            Dim cmAdd As New SqlCommand("spInsResourceValue", cnSubConnection.OpenCultureTranslationConnection(cnMasterConnection))

            Try
                With cmAdd
                    .CommandType = CommandType.StoredProcedure

                    .Parameters.AddWithValue("@ResourceType", passResourceType)
                    .Parameters.AddWithValue("@CultureCode", passCultureCode)
                    .Parameters.AddWithValue("@ResourceKey", passResourceKey)
                    .Parameters.AddWithValue("@DefaultValue", passDefaultValue)
                    If passResourceValue.Trim.Length > 0 Then
                        .Parameters.AddWithValue("@ResourceValue", passResourceValue)
                    End If

                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseCultureTranslationConnection(cnMasterConnection)
            End Try
        End Sub

        Public Sub UpdateResourceValue(ByVal passCultureCode As String, _
                                       ByVal passResourceKey As String, _
                                       ByVal passDefaultValue As String, _
                                       Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            UpdateResourceValue(strTranslationApplicationName, passCultureCode, passResourceKey, passDefaultValue, "", cnMasterConnection)
        End Sub

        Public Sub UpdateResourceValue(ByVal passCultureCode As String, _
                                       ByVal passResourceKey As String, _
                                       ByVal passDefaultValue As String, _
                                       ByVal passResourceValue As String, _
                                       Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            UpdateResourceValue(strTranslationApplicationName, passCultureCode, passResourceKey, passDefaultValue, passResourceValue, cnMasterConnection)
        End Sub
        Public Sub UpdateResourceValue(ByVal passResourceType As String, _
                                       ByVal passCulture As String, _
                                       ByVal passResourceKey As String, _
                                       ByVal passDefaultValue As String, _
                                       ByVal passResourceValue As String, _
                                       Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passResourceType, _
                                                                                     passCulture, _
                                                                                     passResourceKey, _
                                                                                     passDefaultValue, _
                                                                                     passResourceValue, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New CultureTranslationConnection
            Dim cmUpdate As New SqlCommand("spUpdResourceValue", cnSubConnection.OpenCultureTranslationConnection(cnMasterConnection))

            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure

                    .Parameters.AddWithValue("@ResourceType", passResourceType)
                    .Parameters.AddWithValue("@CultureCode", passCulture)
                    .Parameters.AddWithValue("@ResourceKey", passResourceKey)
                    .Parameters.AddWithValue("@DefaultValue", passDefaultValue)
                    If passResourceValue.Trim.Length > 0 Then
                        .Parameters.AddWithValue("@ResourceValue", passResourceValue)
                    End If

                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseCultureTranslationConnection(cnMasterConnection)
            End Try
        End Sub

        Public Sub DeleteResourceValue(ByVal passCultureCode As String, _
                                       ByVal passResourceKey As String, _
                                       Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            DeleteResourceValue(strTranslationApplicationName, passCultureCode, passResourceKey, cnMasterConnection)
        End Sub
        Public Sub DeleteResourceValue(ByVal passResourceType As String, _
                                       ByVal passCultureCode As String, _
                                       ByVal passResourceKey As String, _
                                       Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passResourceType, _
                                                                                     passCultureCode, _
                                                                                     passResourceKey, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try
            Dim cnSubConnection As New CultureTranslationConnection
            Dim cmDelete As New SqlCommand("spDelResourceValue", cnSubConnection.OpenCultureTranslationConnection(cnMasterConnection))

            Try
                With cmDelete
                    .CommandType = CommandType.StoredProcedure

                    .Parameters.AddWithValue("@ResourceType", passResourceType)
                    .Parameters.AddWithValue("@CultureCode", passCultureCode)
                    .Parameters.AddWithValue("@ResourceKey", passResourceKey)

                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmDelete.Dispose()
                cnSubConnection.CloseCultureTranslationConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " Select CultureMaster and Return Dropdownlist values"
        Public Sub SelectCultureMasterCodeList(ByRef ddlList As System.Web.UI.WebControls.DropDownList, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelCultureMasterList", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    ddlList.Items.Add(New ListItem(drList.GetString(2), drList.GetString(1)))
                End While
                ddlList.Items.Insert(0, (New ListItem("", "")))
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Sub SelectDefaultSiteCultureListShowDescription(ByRef ddlList As System.Web.UI.WebControls.DropDownList, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelDefaultSiteCultureList", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    ddlList.Items.Add(New ListItem(drList.GetString(1), drList.GetInt32(0)))
                End While
                ddlList.Items.Insert(0, New ListItem("", 0))
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

    End Module
End Namespace
