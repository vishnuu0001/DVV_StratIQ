#Region " Imports"
Imports System.Text
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class MenuOptionMaster

#Region " Select Methods"
        Public Shared Function GetMenuOptions(ByVal passUserID As String, ByVal passIsAdministrator As Integer, ByVal passMenu As String, _
                                              ByVal passGroupPrograms As Boolean, ByVal passAllowUserSpecifiedColumns As Boolean, _
                                              ByVal passShowAllMenuOptions As Boolean, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataSet
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passUserID, _
                                                                                     passIsAdministrator, _
                                                                                     passMenu, _
                                                                                     passGroupPrograms, _
                                                                                     passAllowUserSpecifiedColumns, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelProgramForMenu", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim ds As New DataSet
            Try
                With da
                    .SelectCommand.CommandType = CommandType.StoredProcedure
                    .SelectCommand.Parameters.AddWithValue("@UserID", passUserID)
                    .SelectCommand.Parameters.AddWithValue("@IsAdministrator", passIsAdministrator)
                    .SelectCommand.Parameters.AddWithValue("@Menu", passMenu)
                    .SelectCommand.Parameters.AddWithValue("@GroupPrograms", passGroupPrograms)
                    .SelectCommand.Parameters.AddWithValue("@AllowUserSpecifiedColumns", passAllowUserSpecifiedColumns)
                    .SelectCommand.Parameters.AddWithValue("@ShowAllMenuOptions", passShowAllMenuOptions)
                    .Fill(ds)
                End With
                Return ds
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectMenuOptionMasterByKey(ByVal passMenu As String, ByVal passMenuOption As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelMenuOptionMasterByKey", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim ds As New DataTable
            Try
                With da
                    .SelectCommand.CommandType = CommandType.StoredProcedure

                    .SelectCommand.Parameters.AddWithValue("@Menu", passMenu)
                    .SelectCommand.Parameters.AddWithValue("@MenuOption", passMenuOption)
                    .Fill(ds)
                End With

                Return ds
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " Action Methods"
        Public Shared Sub InsertMenuOption(ByVal passMenu As String, ByVal passOptionValue As Integer, ByVal passOptionDescription As String, _
                                           ByVal passProgram As String, ByVal passLinkURL As String, ByVal passProgramGroup As String, _
                                           Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passMenu, passOptionValue, _
                                                                                     passOptionDescription, passProgram, passLinkURL, passProgramGroup, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmInsertMenuOption As New SqlCommand("spInsMenuOptionMaster", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmInsertMenuOption
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@Menu", passMenu)
                    .Parameters.AddWithValue("@OptionValue", passOptionValue)
                    .Parameters.AddWithValue("@OptionDescription", passOptionDescription)
                    If passProgram.Trim.Length > 0 Then
                        .Parameters.AddWithValue("@Program", passProgram)
                    End If
                    If passLinkURL.Trim.Length > 0 Then
                        .Parameters.AddWithValue("@LinkURL", passLinkURL)
                    End If
                    If passProgramGroup.Trim.Length > 0 Then
                        .Parameters.AddWithValue("@ProgramGroup", passProgramGroup)
                    End If

                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmInsertMenuOption.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub UpdateMenuOption(ByVal passMenu As String, ByVal passOptionValue As Integer, ByVal passOptionDescription As String, _
                                           ByVal passProgram As String, ByVal passLinkURL As String, ByVal passProgramGroup As String, _
                                           Optional ByRef cnMasterConnection As SqlConnection = Nothing)

            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passMenu, passOptionValue, passOptionDescription, _
                                                                                     passProgram, passLinkURL, passProgramGroup, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdateMenuOption As New SqlCommand("spUpdMenuOptionMaster", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmUpdateMenuOption
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@Menu", passMenu)
                    .Parameters.AddWithValue("@OptionValue", passOptionValue)
                    .Parameters.AddWithValue("@OptionDescription", passOptionDescription)
                    If passProgram.Trim.Length > 0 Then
                        .Parameters.AddWithValue("@Program", passProgram)
                    End If
                    If passLinkURL.Trim.Length > 0 Then
                        .Parameters.AddWithValue("@LinkURL", passLinkURL)
                    End If
                    If passProgramGroup.Trim.Length > 0 Then
                        .Parameters.AddWithValue("@ProgramGroup", passProgramGroup)
                    End If

                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmUpdateMenuOption.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub DeleteMenuOption(ByVal passMenu As String, _
                                           ByVal passOptionValue As Integer, _
                                           Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passMenu, passOptionValue, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDeleteMenuOption As New SqlCommand("spDelMenuOptionMaster", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmDeleteMenuOption
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@Menu", passMenu)
                    .Parameters.AddWithValue("@OptionValue", passOptionValue)
                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmDeleteMenuOption.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

    End Class
End Namespace