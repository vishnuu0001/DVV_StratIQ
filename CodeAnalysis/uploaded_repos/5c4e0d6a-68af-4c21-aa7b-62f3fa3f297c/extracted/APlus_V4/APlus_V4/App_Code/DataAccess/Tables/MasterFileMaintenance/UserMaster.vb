#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports System.DirectoryServices
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Enum InsertADUserError As Integer
        NoError = 0
        NotValidADUser = 1
        UserExistsInAPlus = 2
        UnknownError = 3
        SQLError = 4
        InActiveUser = 5
        InvalidSite = 6
    End Enum

    Public Class UserMaster

#Region " Verify User Access"
        Public Shared Function VerifyUserAccess(ByVal passUserID As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection()
            Dim da As New SqlDataAdapter(New SqlCommand("spSelUserAccess", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@UserID", passUserID)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " Select User Master"
        Public Shared Function SelectUserMaster(ByVal passUserID As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelUser", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim ds As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@UserID", passUserID)
                da.Fill(ds)
                Return ds
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectUsersBySite(ByVal passSiteID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSiteID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelUsersBySite", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@SiteID", passSiteID)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Sub SelectUserIDList(ByRef ddlList As System.Web.UI.WebControls.DropDownList, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelUserIDList", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    ddlList.Items.Add(New ListItem(drList.GetString(2) + ", " + drList.GetString(1) + " (" + drList.GetString(0) + ")", drList.GetString(0)))
                End While
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub SelectUserNameList(ByVal passSiteID As Integer, ByRef ddlList As System.Web.UI.WebControls.DropDownList, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            SelectUserNameList(passSiteID, False, ddlList, cnMasterConnection)
        End Sub
        Public Shared Sub SelectUserNameList(ByVal passSiteID As Integer, ByVal passActiveOnly As Boolean, ByRef ddlList As System.Web.UI.WebControls.DropDownList, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSiteID, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelUserNameList", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@SiteID", passSiteID)
                cmSelect.Parameters.AddWithValue("@ShowActiveOnly", passActiveOnly)
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    ddlList.Items.Add(New ListItem(drList.GetString(2) & ", " & drList.GetString(1) & " " & "(" & drList.GetString(0) & ")", drList.GetString(0)))
                End While
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Function GetUserFullName(ByVal passUserID As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelUser", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim ds As New DataSet
            Dim strHolder As String = String.Empty
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@UserID", passUserID)
                da.Fill(ds)
                da.Dispose()
                If ds.Tables(0).Rows.Count > 0 Then
                    If ds.Tables(0).Rows(0)("FirstName").ToString.Length > 0 Then
                        strHolder = ds.Tables(0).Rows(0)("FirstName").ToString
                    End If
                    If ds.Tables(0).Rows(0)("LastName").ToString.Length > 0 Then
                        If strHolder.Trim.Length > 0 Then
                            strHolder += " "
                        End If
                        strHolder += ds.Tables(0).Rows(0)("LastName").ToString
                    End If
                End If
            Catch Exc As Exception
                Throw
            Finally
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try

            Return strHolder
        End Function
        Public Shared Function GetUserFullNameLastNameFirst(ByVal passUser As String) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUser)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim strHolder As String = String.Empty
            Try
                Dim ds As DataTable = SelectUserMaster(passUser)
                If ds.Rows.Count > 0 Then
                    If ds.Rows(0)("LastName").ToString.Length > 0 Then
                        strHolder = ds.Rows(0)("LastName").ToString
                    End If
                    If ds.Rows(0)("FirstName").ToString.Length > 0 Then
                        If strHolder.Trim.Length > 0 Then
                            strHolder += ", "
                        End If
                        strHolder += ds.Rows(0)("FirstName").ToString
                    End If
                End If
            Catch Exc As Exception
                Throw
            End Try

            Return strHolder
        End Function
        Public Shared Function GetUserSite(ByVal passUserID As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelSiteByUser", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim ds As New DataSet
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@UserID", passUserID)
                da.Fill(ds)
                da.Dispose()
                If ds.Tables(0).Rows.Count > 0 Then
                    Return CInt(ds.Tables(0).Rows(0)(0))
                End If
            Catch Exc As Exception
                Throw
            Finally
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try

            Return 0
        End Function
        Public Shared Function GetUserCulture(ByVal passUserID As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim strHolder As String = String.Empty
            If IsNothing(passUserID) Then
                Return strHolder
            ElseIf passUserID.Trim.Length = 0 Then
                Return strHolder
            End If

            Try
                Dim da As New SqlDataAdapter(New SqlCommand("spSelCultureByUser", cnSubConnection.OpenConnection(cnMasterConnection)))
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                Dim ds As New DataSet
                da.SelectCommand.Parameters.AddWithValue("@UserID", passUserID)
                da.Fill(ds)
                da.Dispose()
                If ds.Tables(0).Rows.Count > 0 Then
                    strHolder = "" + ds.Tables(0).Rows(0)(0).ToString
                End If
            Catch Exc As Exception
                Throw
            Finally
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try

            Return strHolder
        End Function
        Public Shared Function GetUserEmail(ByVal passUserID As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelEmailByUser", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim ds As New DataSet
            Dim strHolder As String = String.Empty
            Try

                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@UserID", passUserID)
                da.Fill(ds)
                da.Dispose()
                If ds.Tables(0).Rows.Count > 0 Then
                    strHolder = "" + ds.Tables(0).Rows(0)(0).ToString
                End If
            Catch Exc As Exception
                Throw
            Finally
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try

            Return strHolder
        End Function
        Public Shared Function UserExists(ByVal passUserID As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelUser", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim ds As New DataSet
            Dim retValue As Boolean = False
            Try

                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@UserID", passUserID)
                da.Fill(ds)
                da.Dispose()
                If ds.Tables(0).Rows.Count > 0 Then
                    retValue = True
                End If
            Catch Exc As Exception
                Throw
            Finally
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
            Return retValue
        End Function
#End Region

#Region " Add UserMaster"
        Public Shared Function AddUserMaster(ByVal passUserID As String, ByVal passSiteID As Integer, _
                                        ByVal passPassword As String, ByVal passInitialProgram As String, _
                                        ByVal passIsAdministrator As Boolean, ByVal passLastName As String, _
                                        ByVal passFirstName As String, ByVal passMiddleInitial As String, _
                                        ByVal passSuffix As String, ByVal passTitle As String, _
                                        ByVal passDeptNumber As String, ByVal passActive As Boolean, _
                                        ByVal passEmailAddress As String, ByVal passRegTemp As Boolean, _
                                        ByVal passCultureID As Integer, ByVal passShowMenuOptionNumbers As Boolean, _
                                        Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Boolean

            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passUserID, passSiteID, _
                                                                                     passPassword, passInitialProgram, _
                                                                                     passIsAdministrator, passLastName, _
                                                                                     passFirstName, passMiddleInitial, _
                                                                                     passSuffix, passTitle, _
                                                                                     passDeptNumber, passActive, _
                                                                                     passEmailAddress, passRegTemp, _
                                                                                     passCultureID, passShowMenuOptionNumbers, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsUserMaster", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim blnValid As Boolean = False
            Try
                With cmAdd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@UserID", passUserID)
                    .Parameters.AddWithValue("@SiteID", passSiteID)
                    .Parameters.AddWithValue("@Password", passPassword)
                    .Parameters.AddWithValue("@InitialProgram", passInitialProgram)
                    .Parameters.AddWithValue("@IsAdministrator", passIsAdministrator)
                    .Parameters.AddWithValue("@LastName", passLastName)
                    .Parameters.AddWithValue("@FirstName", passFirstName)
                    .Parameters.AddWithValue("@MiddleInitial", passMiddleInitial)
                    .Parameters.AddWithValue("@Suffix", passSuffix)
                    .Parameters.AddWithValue("@Title", passTitle)
                    .Parameters.AddWithValue("@DeptNumber", passDeptNumber)
                    .Parameters.AddWithValue("@EmailAddress", passEmailAddress)
                    .Parameters.AddWithValue("@CultureID", passCultureID)
                    If passRegTemp Then
                        .Parameters.AddWithValue("@RegTemp", "TMP")
                    Else
                        .Parameters.AddWithValue("@RegTemp", "REG")
                    End If
                    .Parameters.AddWithValue("@Active", passActive)
                    .Parameters.AddWithValue("@ShowMenuOptionNumbers", passShowMenuOptionNumbers)
                    .ExecuteNonQuery()
                End With
                blnValid = True
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
            Return blnValid
        End Function
#End Region

#Region " Update UserMaster"
        Public Shared Sub UpdateUserMaster(ByVal passUserID As String, _
                                           ByVal passSiteID As Integer, _
                                           ByVal passInitialProgram As String, _
                                           ByVal passIsAdministrator As Boolean, _
                                           ByVal passLastName As String, _
                                           ByVal passFirstName As String, _
                                           ByVal passMiddleInitial As String, _
                                           ByVal passSuffix As String, _
                                           ByVal passTitle As String, _
                                           ByVal passDeptNumber As String, _
                                           ByVal passActive As Boolean, _
                                           ByVal passEmailAddress As String, _
                                           ByVal passRegTemp As Boolean, _
                                           ByVal passCultureID As Integer, _
                                           Optional ByRef cnMasterConnection As SqlConnection = Nothing)

            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passUserID, _
                                                                                     passSiteID, _
                                                                                     passInitialProgram, _
                                                                                     passIsAdministrator, _
                                                                                     passLastName, _
                                                                                     passFirstName, _
                                                                                     passMiddleInitial, _
                                                                                     passSuffix, _
                                                                                     passTitle, _
                                                                                     passDeptNumber, _
                                                                                     passActive, _
                                                                                     passEmailAddress, _
                                                                                     passRegTemp, _
                                                                                     passCultureID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdUserMaster", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@UserID", passUserID)
                    .Parameters.AddWithValue("@SiteID", passSiteID)
                    .Parameters.AddWithValue("@InitialProgram", passInitialProgram)
                    .Parameters.AddWithValue("@IsAdministrator", passIsAdministrator)
                    .Parameters.AddWithValue("@LastName", passLastName)
                    .Parameters.AddWithValue("@FirstName", passFirstName)
                    .Parameters.AddWithValue("@MiddleInitial", passMiddleInitial)
                    .Parameters.AddWithValue("@Suffix", passSuffix)
                    .Parameters.AddWithValue("@Title", passTitle)
                    .Parameters.AddWithValue("@DeptNumber", passDeptNumber)
                    .Parameters.AddWithValue("@EmailAddress", passEmailAddress)
                    .Parameters.AddWithValue("@CultureID", passCultureID)
                    If passRegTemp Then
                        .Parameters.AddWithValue("@RegTemp", "TMP")
                    Else
                        .Parameters.AddWithValue("@RegTemp", "REG")
                    End If
                    .Parameters.AddWithValue("@Active", passActive)
                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub

        Public Shared Sub UpdateADUserMaster(ByVal passUserID As String, _
                                                  ByVal passSiteID As Integer, _
                                                  ByVal passLastName As String, _
                                                  ByVal passFirstName As String, _
                                                  ByVal passMiddleInitial As String, _
                                                  ByVal passTitle As String, _
                                                  ByVal passEmailAddress As String, _
                                                  ByVal passActive As Boolean, _
                                                  Optional ByRef cnMasterConnection As SqlConnection = Nothing)

            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passUserID, _
                                                                                     passSiteID, _
                                                                                     passLastName, _
                                                                                     passFirstName, _
                                                                                     passMiddleInitial, _
                                                                                     passTitle, _
                                                                                     passEmailAddress, _
                                                                                     passActive, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdADUserMaster", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@UserID", passUserID)
                    .Parameters.AddWithValue("@SiteID", passSiteID)
                    .Parameters.AddWithValue("@LastName", passLastName)
                    .Parameters.AddWithValue("@FirstName", passFirstName)
                    .Parameters.AddWithValue("@MiddleInitial", passMiddleInitial)
                    .Parameters.AddWithValue("@Title", passTitle)
                    .Parameters.AddWithValue("@EmailAddress", passEmailAddress)
                    .Parameters.AddWithValue("@Active", passActive)
                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " Delete UserMaster"
        Public Shared Sub DeleteUserMaster(ByVal passUserID As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelUserMaster", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmDelete
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@UserID", passUserID)
                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmDelete.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " Insert User Master FromAD "
        Public Shared Function InsertUserMasterFromAD(ByVal passUser As String, ByVal passCulture As String, Optional ByVal passPassword As String = "") As InsertADUserError
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUser, passCulture, passPassword, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim strPwd As String
                If passPassword.Trim.Length > 0 Then
                    strPwd = FormsAuthentication.HashPasswordForStoringInConfigFile(passPassword.Trim.ToUpper & passUser.Trim.ToUpper, "sha1")
                Else
                    strPwd = FormsAuthentication.HashPasswordForStoringInConfigFile("XXXX" & passUser.Trim.ToUpper, "sha1")
                End If

                Dim iSiteID As Integer = 0
                Dim strFirstName As String = String.Empty
                Dim strLastName As String = String.Empty
                Dim strMiddle As String = String.Empty
                Dim strEmail As String = String.Empty
                Dim iCultureID As Integer = 0

                Dim objEntry As DirectoryEntry
                objEntry = ADAccess.GetADUser(passUser)
                If Not IsNothing(objEntry) Then
                    Dim objProps As System.DirectoryServices.PropertyCollection
                    objProps = objEntry.Properties

                    '**************
                    'Site
                    Dim strholder As String = ADAccess.GetADSite(objProps("distinguishedname").Value.ToString())
                    Dim dtSite As DataTable = SiteMaster.GetSiteFromADSite(strholder)
                    If dtSite.Rows.Count = 0 OrElse Not Convert.ToBoolean(dtSite.Rows(0)("Active")) Then
                        Return InsertADUserError.InvalidSite
                    End If

                    iSiteID = Convert.ToInt32(dtSite.Rows(0)("SiteID"))

                    'default if no valid site is found
                    If iSiteID = 0 Then
                        Return InsertADUserError.UnknownError
                    End If

                    '*****************
                    'First Name
                    If IsNothing(objProps("givenname").Value) Then
                        strFirstName = String.Empty
                    Else
                        strFirstName = objProps("givenname").Value.ToString()
                    End If

                    '*******************
                    'Last Name
                    If IsNothing(objProps("sn").Value) Then
                        strLastName = String.Empty
                    Else
                        strLastName = objProps("sn").Value.ToString()
                    End If

                    '*******************
                    'Middle
                    If IsNothing(objProps("initials").Value) Then
                        strMiddle = String.Empty
                    Else
                        strMiddle = objProps("initials").Value.ToString()
                    End If

                    '***************
                    'Email
                    If IsNothing(objProps("userprincipalname").Value) Then
                        strEmail = String.Empty
                    Else
                        strEmail = objProps("userprincipalname").Value.ToString()
                    End If

                    '*********************
                    ' Culture
                    iCultureID = CultureMaster.GetCultureIDByCode(passCulture)
                    If iCultureID = 0 Then
                        Return InsertADUserError.UnknownError
                    End If

                    'Only add what should be VALID USER accounts
                    If strFirstName.Trim.Length = 0 OrElse strLastName.Trim.Length = 0 OrElse _
                    strFirstName.Contains(strholder) OrElse strLastName.Contains(strholder) Then
                        Return InsertADUserError.NotValidADUser
                    End If
                Else
                    Return InsertADUserError.NotValidADUser
                End If

                If AddUserMaster(passUser.ToUpper, iSiteID, strPwd, "MainMenu", False, strLastName, strFirstName, strMiddle, "", "-", "", True, strEmail, False, iCultureID, False) Then
                    UserSecurityGroupMaster.AddUserSecurityGroupMaster(passUser.ToUpper, 4)
                    Return InsertADUserError.NoError
                Else
                    Return InsertADUserError.UserExistsInAPlus
                End If
            Catch Exc As Exception
                Return InsertADUserError.UnknownError
            End Try
            Return InsertADUserError.NoError
        End Function
#End Region

#Region " Table Methods"
        Public Shared Sub AddNewPassword(ByVal passUserID As String, ByVal passPassword As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, passPassword, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spUpdNewPassword", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmAdd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@UserID", passUserID)
                    .Parameters.AddWithValue("@Password", passPassword)
                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub UpdateUserCulture(ByVal passUserID As String, ByVal passNewCultureCode As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, passNewCultureCode, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spUpdUserCultureCode", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmAdd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@UserID", passUserID)
                    .Parameters.AddWithValue("@CultureCode", passNewCultureCode)
                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub UpdateUserCultureByID(ByVal passUserID As String, ByVal passNewCultureID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, passNewCultureID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spUpdUserCulture", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmAdd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@UserID", passUserID)
                    .Parameters.AddWithValue("@CultureID", passNewCultureID)
                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub UpdateMenuOption(ByVal passUserID As String, ByVal passShowMenuOptionNumbers As Boolean, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, passShowMenuOptionNumbers, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spUpdUserShowMenuOptionNumbers", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmAdd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@UserID", passUserID)
                    .Parameters.AddWithValue("@ShowMenuOptionNumbers", passShowMenuOptionNumbers)
                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub UpdateDepartment(ByVal passUserID As String, _
                                                ByVal passNewDepartment As String, _
                                                Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, passNewDepartment, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spUpdUserMasterDepartment", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmAdd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@UserID", passUserID)
                    If passNewDepartment.Trim.Length > 0 Then
                        .Parameters.AddWithValue("@DeptNumber", passNewDepartment)
                    End If
                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub UpdateTitle(ByVal passUserID As String, ByVal passNewTitle As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, passNewTitle, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spUpdUserMasterTitle", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmAdd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@UserID", passUserID)
                    If passNewTitle.Trim.Length = 0 Then
                        passNewTitle = "-"
                    End If
                    .Parameters.AddWithValue("@Title", passNewTitle)
                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

    End Class
End Namespace
