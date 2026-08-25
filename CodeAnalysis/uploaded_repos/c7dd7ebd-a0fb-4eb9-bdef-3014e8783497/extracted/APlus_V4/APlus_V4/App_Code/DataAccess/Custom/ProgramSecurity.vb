#Region " Imports"
Imports System.Text
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.DataAccess.Custom
    Public Class ProgramSecurity

#Region " Program Verification"
        Public Shared Function ProgramVerification(ByVal passUserID As String, ByVal passProfile As Boolean) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, passProfile, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnMasterConnection As SqlConnection = ApplicationConnection.OpenMasterConnection()
            Try
                Dim myInitialMenu As String = VerifyInitialMenu(passUserID, cnMasterConnection)
                Dim myProgramURL As String = ProgramSecurity(passUserID, passProfile, myInitialMenu, cnMasterConnection)
                Return myProgramURL
            Catch Exc As Exception
                Throw
            Finally
                ApplicationConnection.CloseMasterConnection(cnMasterConnection)
            End Try
        End Function

        Public Shared Function ProgramVerification(ByVal passUserID As String, ByVal passProfile As Boolean, ByRef passInitialMenu As String) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, passProfile, passInitialMenu, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnMasterConnection As SqlConnection = ApplicationConnection.OpenMasterConnection()
            Try
                Dim myInitialMenu As String = VerifyInitialMenu(passUserID, cnMasterConnection)
                Dim myProgramURL As String = ProgramSecurity(passUserID, passProfile, myInitialMenu, cnMasterConnection)
                If myProgramURL.Trim.Length > 0 Then
                    passInitialMenu = myInitialMenu
                End If
                Return myProgramURL
            Catch Exc As Exception
                Throw
            Finally
                ApplicationConnection.CloseMasterConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " Get Program"
        Public Shared Sub GetProgram(ByVal passUserID As String, _
                                     ByVal passProfile As Boolean, _
                                     ByVal passMenu As String, _
                                     ByVal passMenuOption As Integer, _
                                     ByRef passProgram As String, _
                                     ByRef passProgramURL As String, _
                                     Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passUserID, _
                                                                                     passProfile, _
                                                                                     passMenu, _
                                                                                     passMenuOption, _
                                                                                     passProgram, _
                                                                                     passProgramURL, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim myParm As SqlParameter
            Dim cmMenuOption As New SqlCommand("spSelProgram", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmMenuOption
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@UserID", passUserID)
                    .Parameters.AddWithValue("@Menu", passMenu)
                    .Parameters.AddWithValue("@Optionvalue", passMenuOption)
                    .Parameters.AddWithValue("@IsAdministrator", passProfile)
                    myParm = .Parameters.Add("@Program", SqlDbType.VarChar, 50)
                    myParm.Direction = ParameterDirection.Output
                    myParm = .Parameters.Add("@ProgramURL", SqlDbType.VarChar, 100)
                    myParm.Direction = ParameterDirection.Output
                    .ExecuteNonQuery()
                    .Dispose()
                    passProgram = cmMenuOption.Parameters("@Program").Value.ToString.Trim()
                    passProgramURL = cmMenuOption.Parameters("@ProgramURL").Value.ToString.Trim()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub

        Public Shared Sub GetProgramFromShortcut(ByVal passUserID As String, _
                                                 ByVal passProfile As Boolean, _
                                                 ByVal passProgramShortcut As String, _
                                                 ByRef passProgram As String, _
                                                 ByRef passProgramURL As String, _
                                                 Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passUserID, _
                                                                                     passProfile, _
                                                                                     passProgramShortcut, _
                                                                                     passProgram, _
                                                                                     passProgramURL, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim myParm As SqlParameter
            Dim cmMenuOption As New SqlCommand("spSelProgramFromShortcut", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmMenuOption
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@UserID", passUserID)
                    .Parameters.AddWithValue("@IsAdministrator", passProfile)
                    .Parameters.AddWithValue("@ProgramShortcut", passProgramShortcut)
                    myParm = .Parameters.Add("@Program", SqlDbType.VarChar, 50)
                    myParm.Direction = ParameterDirection.Output
                    myParm = .Parameters.Add("@ProgramURL", SqlDbType.VarChar, 100)
                    myParm.Direction = ParameterDirection.Output
                    .ExecuteNonQuery()
                    .Dispose()
                    passProgram = cmMenuOption.Parameters("@Program").Value.ToString.Trim()
                    passProgramURL = cmMenuOption.Parameters("@ProgramURL").Value.ToString.Trim()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " Get Program URL"
        Public Shared Function GetProgramURL(ByVal passMenu As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passMenu, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmGetProgramURL As New SqlCommand("spSelProgramURL", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim strURL As String = ""

            Try
                cmGetProgramURL.CommandType = CommandType.StoredProcedure
                cmGetProgramURL.Parameters.AddWithValue("@Program", passMenu)
                strURL = Convert.ToString(cmGetProgramURL.ExecuteScalar).Trim
            Catch Exc As Exception
                Throw
            Finally
                cmGetProgramURL.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
            Return strURL
        End Function
#End Region

#Region " Program URL"
        Public Shared Function ProgramURL(ByVal passUserID As String, _
                                          ByVal passProfile As Boolean, _
                                          ByVal passProgram As String, _
                                          Optional ByRef cnMasterConnection As SqlConnection = Nothing) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, passProfile, passProgram, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim strReturn As String = String.Empty
            Dim intAdminValue As Integer
            Dim cnSubConnection As New ApplicationConnection
            Dim myParm As SqlParameter
            Dim cmProgramURL As New SqlCommand("spSelProgramURLSecurity", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmProgramURL
                    .CommandType = CommandType.StoredProcedure
                    If passProfile Then
                        intAdminValue = 1
                    Else
                        intAdminValue = 0
                    End If
                    .Parameters.AddWithValue("@UserID", passUserID)
                    .Parameters.AddWithValue("@IsAdministrator", intAdminValue)
                    .Parameters.AddWithValue("@Program", passProgram)
                    myParm = .Parameters.Add("@ProgramURL", SqlDbType.VarChar, 100)
                    myParm.Direction = ParameterDirection.Output
                    .ExecuteNonQuery()
                    .Dispose()
                End With
                strReturn = cmProgramURL.Parameters("@ProgramURL").Value.ToString.Trim()
            Catch Exc As Exception
                Throw
            Finally
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
            Return strReturn
        End Function
#End Region

#Region " Verify Initial Menu"
        Public Shared Function VerifyInitialMenu(ByVal passUserID As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim strReturn As String = String.Empty
            Dim cnSubConnection As New ApplicationConnection
            Dim myParm As SqlParameter
            Dim cmInitialMenu As New SqlCommand("spSelInitialMenu", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmInitialMenu
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@UserID", passUserID)
                    myParm = .Parameters.Add("@InitialProgram", SqlDbType.VarChar, 50)
                    myParm.Direction = ParameterDirection.Output
                    .ExecuteNonQuery()
                    .Dispose()
                End With
                strReturn = cmInitialMenu.Parameters("@InitialProgram").Value.ToString.Trim()
            Catch Exc As Exception
                Throw
            Finally
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
            Return strReturn
        End Function

#End Region

#Region " Program Security"
        Private Shared Function ProgramSecurity(ByVal passUserID As String, _
                                                ByVal passProfile As Boolean, _
                                                ByVal passProgram As String, _
                                                Optional ByRef cnMasterConnection As SqlConnection = Nothing) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, passProfile, passProgram, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim strReturn As String = String.Empty
            Dim myParm As SqlParameter
            Dim intAdminValue As Integer
            Dim cmProgramSecurity As New SqlCommand("spSelProgramSecurityUrl", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmProgramSecurity
                    .CommandType = CommandType.StoredProcedure
                    If passProfile Then
                        intAdminValue = 1
                    Else
                        intAdminValue = 0
                    End If
                    .Parameters.AddWithValue("@Program", passProgram)
                    .Parameters.AddWithValue("@UserID", passUserID)
                    .Parameters.AddWithValue("@IsAdministrator", intAdminValue)
                    myParm = .Parameters.Add("@ProgramURL", SqlDbType.VarChar, 50)
                    myParm.Direction = ParameterDirection.Output
                    .ExecuteNonQuery()
                    .Dispose()
                End With
                strReturn = cmProgramSecurity.Parameters("@ProgramURL").Value.ToString.Trim()
            Catch Exc As Exception
                Throw
            Finally
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
            Return strReturn
        End Function
#End Region

#Region " Program Mode"
        Public Shared Function ProgramModeFromProgram(ByVal passUserID As String, _
                                                      ByVal passProgram As String, _
                                                      Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, passProgram, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelAllowMaintenance", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@UserID", passUserID)
                da.SelectCommand.Parameters.AddWithValue("@Program", passProgram)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function

        Public Shared Function ProgramModeFromURL(ByVal passUserID As String, _
                                                  ByVal passProgramURL As String, _
                                                  Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, passProgramURL, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelAllowMaintenancefromURL", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@UserID", passUserID)
                da.SelectCommand.Parameters.AddWithValue("@ProgramURL", passProgramURL)
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

#Region " Define URL Path"
        Public Function DefineURLPath(ByVal myProgramURL As String) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, myProgramURL)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim iLeftValue As Integer = myProgramURL.IndexOf("=") + 2
            Dim iRightValue As Integer = myProgramURL.IndexOf(">") - 1
            Dim iLength As Integer = ((iRightValue) - (iLeftValue))
            Dim sProgramURL As String = myProgramURL.Substring(iLeftValue, iLength)
            DefineURLPath = sProgramURL
        End Function

        Public Function DefineProgramName(ByVal myProgramURL As String) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, myProgramURL)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim iLength As Integer = InStr(myProgramURL, ".")
            Dim sProgramURL As String = Mid(myProgramURL, 1, iLength - 1)
            DefineProgramName = sProgramURL
        End Function
#End Region

#Region " CanUserAccessThisProgram"
        Public Shared Function CanUserAccessCurrentProgramURL(Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim blnAccess As Boolean = False

            If SessionManager.UserID <> "" Then
                If SessionManager.IsAdministrator Then
                    Return True
                End If

                Dim cnSubConnection As New ApplicationConnection
                Dim myParm As SqlParameter
                Dim cmUserAccessForProgram As New SqlCommand("spSelCanUserAccessThisProgram", cnSubConnection.OpenConnection(cnMasterConnection))
                Try
                    With cmUserAccessForProgram
                        .CommandType = CommandType.StoredProcedure
                        .Parameters.AddWithValue("@UserID", SessionManager.UserID)
                        .Parameters.AddWithValue("@ProgramURL", HttpContext.Current.Request.Path.Substring(HttpContext.Current.Request.ApplicationPath.Length + 1))
                        myParm = .Parameters.Add("@Access", SqlDbType.Bit)
                        myParm.Direction = ParameterDirection.Output
                        .ExecuteNonQuery()
                        blnAccess = Convert.ToBoolean(.Parameters("@Access").Value)
                    End With
                Catch Exc As Exception
                    Throw
                Finally
                    cmUserAccessForProgram.Dispose()
                    cnSubConnection.CloseConnection(cnMasterConnection)
                End Try
            End If

            Return blnAccess
        End Function
        Public Shared Function CanUserAccessThisProgramURL(ByVal passUser As String, ByVal passProgramURL As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUser, passProgramURL, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim blnAccess As Boolean = False
            If SessionManager.UserID <> "" Then
                If SessionManager.IsAdministrator Then
                    Return True
                End If

                Dim cnSubConnection As New ApplicationConnection
                Dim myParm As SqlParameter
                Dim cmUserAccessForProgram As New SqlCommand("spSelCanUserAccessProgramURL", cnSubConnection.OpenConnection(cnMasterConnection))
                Try
                    With cmUserAccessForProgram
                        .CommandType = CommandType.StoredProcedure
                        .Parameters.AddWithValue("@UserID", passUser)
                        .Parameters.AddWithValue("@ProgramURL", passProgramURL)
                        myParm = .Parameters.Add("@Access", SqlDbType.Bit)
                        myParm.Direction = ParameterDirection.Output
                        .ExecuteNonQuery()
                        blnAccess = Convert.ToBoolean(.Parameters("@Access").Value)
                        cmUserAccessForProgram.Dispose()
                    End With
                Catch Exc As Exception
                    Throw
                Finally
                    cnSubConnection.CloseConnection(cnMasterConnection)
                End Try
            End If

            Return blnAccess
        End Function
        Public Shared Function CanUserAccessProgram(ByVal passUser As String, ByVal passProgram As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUser, passProgram, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim blnAccess As Boolean = False
            If SessionManager.UserID <> "" Then
                If SessionManager.IsAdministrator Then
                    Return True
                ElseIf passProgram.Trim.Length = 0 Then
                    Return False
                End If

                Dim cnSubConnection As New ApplicationConnection
                Dim myParm As SqlParameter
                Dim cmUserAccessForProgram As New SqlCommand("spSelCanUserAccessProgram", cnSubConnection.OpenConnection(cnMasterConnection))
                Try
                    With cmUserAccessForProgram
                        .CommandType = CommandType.StoredProcedure
                        .Parameters.AddWithValue("@UserID", passUser)
                        .Parameters.AddWithValue("@Program", passProgram)
                        myParm = .Parameters.Add("@Access", SqlDbType.Bit)
                        myParm.Direction = ParameterDirection.Output
                        .ExecuteNonQuery()
                        blnAccess = Convert.ToBoolean(.Parameters("@Access").Value)
                        cmUserAccessForProgram.Dispose()
                    End With
                Catch Exc As Exception
                    Throw
                Finally
                    cnSubConnection.CloseConnection(cnMasterConnection)
                End Try
            End If

            Return blnAccess
        End Function
#End Region

    End Class
End Namespace
