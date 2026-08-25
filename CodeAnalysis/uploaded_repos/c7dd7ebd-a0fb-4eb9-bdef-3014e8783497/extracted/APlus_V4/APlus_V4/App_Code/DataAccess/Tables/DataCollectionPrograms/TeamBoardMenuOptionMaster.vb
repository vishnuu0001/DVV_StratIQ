#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class TeamBoardMenuOptionMaster

#Region " Select Methods"
        Public Shared Function SelectTeamBoardMenuOptionMasterByTeam(ByVal passTeamID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTeamBoardMenuOptionMasterByTeam", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TeamID", passTeamID)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectTeamBoardMenuOptionMasterNextSequence(ByVal passTeamID As Integer, _
                                                                           ByVal passBoardRow As Integer, _
                                                                           ByVal passBoardColumn As Integer, _
                                                                           Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelTeamBoardMenuOptionMasterNextSequence", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@TeamID", passTeamID)
                cmSelect.Parameters.AddWithValue("@BoardRow", passBoardRow)
                cmSelect.Parameters.AddWithValue("@BoardColumn", passBoardColumn)
                Return cmSelect.ExecuteScalar
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectTeamBoardMenuOptionMasterByID(ByVal passMenuOptionID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passMenuOptionID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTeamBoardMenuOptionMasterByID", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@MenuOptionID", passMenuOptionID)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectTeamBoardMenuOptionMaster(ByVal passTeamID As Integer, _
                                                               ByVal passBoardColumn As String, _
                                                               ByVal passBoardRow As String, _
                                                               ByVal passRCSequence As String, _
                                                               Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passTeamID, _
                                                                                     passBoardColumn, _
                                                                                     passBoardRow, _
                                                                                     passRCSequence, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTeamBoardMenuOptionMaster", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TeamID", passTeamID)
                da.SelectCommand.Parameters.AddWithValue("@BoardRow", passBoardRow)
                da.SelectCommand.Parameters.AddWithValue("@BoardColumn", passBoardColumn)
                da.SelectCommand.Parameters.AddWithValue("@RCSequence", passRCSequence)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function TeamBoardMenuOptionMasterByTeamExist(ByVal passTeamID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spSelTeamBoardMenuOptionMasterByTeamExist", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim bReturn As Boolean = False

            Try
                With cmAdd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@TeamID", passTeamID)
                    bReturn = .ExecuteScalar
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try

            Return bReturn
        End Function
#End Region

#Region " Action Methods"
        Public Shared Function AddTeamBoardMenuOptionMaster(ByVal passTeamID As Integer, ByVal passBoardColumn As Integer, ByVal passBoardRow As Integer, _
                                                            ByVal passRCSequence As Integer, ByVal passBoardDescription As String, ByVal passLinkType As String, _
                                                            ByVal passProgram As String, ByVal passLinkFileURL As String, _
                                                            Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passTeamID, _
                                                                                     passBoardColumn, _
                                                                                     passBoardRow, _
                                                                                     passRCSequence, _
                                                                                     passBoardDescription, _
                                                                                     passLinkType, _
                                                                                     passProgram, _
                                                                                     passLinkFileURL, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsTeamBoardMenuOptionMaster", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmAdd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@TeamID", passTeamID)
                    .Parameters.AddWithValue("@BoardColumn", passBoardColumn)
                    .Parameters.AddWithValue("@BoardRow", passBoardRow)
                    .Parameters.AddWithValue("@RCSequence", passRCSequence)
                    .Parameters.AddWithValue("@BoardDescription", passBoardDescription)
                    .Parameters.AddWithValue("@LinkType", passLinkType)
                    If Not String.IsNullOrEmpty(passProgram.Trim()) Then .Parameters.AddWithValue("@Program", passProgram)
                    If Not String.IsNullOrEmpty(passLinkFileURL.Trim()) Then .Parameters.AddWithValue("@LinkFileURL", passLinkFileURL)
                    Return .ExecuteScalar
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Sub UpdateTeamBoardMenuOptionMaster(ByVal passMenuOptionID As Integer, ByVal passTeamID As Integer, _
                                                          ByVal passBoardColumn As String, ByVal passOldBoardColumn As String, _
                                                          ByVal passBoardRow As String, ByVal passOldBoardRow As String, _
                                                          ByVal passRCSequence As String, ByVal passOldRCSequence As String, _
                                                          ByVal passBoardDescription As String, ByVal passLinkType As String, _
                                                          ByVal passProgram As String, ByVal passLinkFileURL As String, _
                                                          Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passMenuOptionID, _
                                                                                     passTeamID, _
                                                                                     passBoardColumn, _
                                                                                     passOldBoardColumn, _
                                                                                     passBoardRow, _
                                                                                     passOldBoardRow, _
                                                                                     passRCSequence, _
                                                                                     passOldRCSequence, _
                                                                                     passBoardDescription, _
                                                                                     passLinkType, _
                                                                                     passProgram, _
                                                                                     passLinkFileURL, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdTeamBoardMenuOptionMaster", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@MenuOptionID", passMenuOptionID)
                    .Parameters.AddWithValue("@TeamID", passTeamID)
                    .Parameters.AddWithValue("@BoardColumn", passBoardColumn)
                    .Parameters.AddWithValue("@OldBoardColumn", passOldBoardColumn)
                    .Parameters.AddWithValue("@BoardRow", passBoardRow)
                    .Parameters.AddWithValue("@OldBoardRow", passOldBoardRow)
                    .Parameters.AddWithValue("@RCSequence", passRCSequence)
                    .Parameters.AddWithValue("@OldRCSequence", passOldRCSequence)
                    .Parameters.AddWithValue("@BoardDescription", passBoardDescription)
                    .Parameters.AddWithValue("@LinkType", passLinkType)
                    If Not String.IsNullOrEmpty(passProgram.Trim()) Then .Parameters.AddWithValue("@Program", passProgram)
                    If Not String.IsNullOrEmpty(passLinkFileURL.Trim()) Then .Parameters.AddWithValue("@LinkFileURL", passLinkFileURL)
                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub MoveTeamBoardMenuOptionMaster(ByVal itemId As Integer, ByVal destinationRow As Integer, ByVal destinationCol As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, itemId, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmd As New SqlCommand("spMoveTeamBoardMenuOptionMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@TeamId", SessionManager.SelectedTeamID)
                    .Parameters.AddWithValue("@ItemId", itemId)
                    .Parameters.AddWithValue("@Row", destinationRow)
                    .Parameters.AddWithValue("@Column", destinationCol)
                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub

        Public Shared Sub DeleteTeamBoardMenuOptionMaster(ByVal passMenuOptionID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passMenuOptionID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelTeamBoardMenuOptionMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmDelete
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@MenuOptionID", passMenuOptionID)
                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmDelete.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub InsertTeamBoardMenuDefaultsToTeamBoardMenuOptionMaster(ByVal passTeamID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsTeamBoardMenuDefaultsToTeamBoardMenuOptionMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmAdd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@TeamID", passTeamID)
                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub DeleteTeamBoardMenuOptionMasterByTeam(ByVal passTeamID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spDelTeamBoardMenuOptionMasterByTeam", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmAdd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@TeamID", passTeamID)
                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Function SelectNextAvailableSequenceNumber(ByVal teamId As Integer, ByVal rowNumber As Integer, ByVal columnNumber As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As String
            Dim cnSubConnection As New ApplicationConnection
            Dim cmd As New SqlCommand("spSelNextAvailableSequenceNumber", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim myParm As SqlParameter
            Try
                With cmd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@TeamId", teamId)
                    .Parameters.AddWithValue("@RowNumber", rowNumber)
                    .Parameters.AddWithValue("@ColumnNumber", columnNumber)
                    myParm = .Parameters.AddWithValue("@SequenceNumberNext", SqlDbType.Int)
                    myParm.Direction = ParameterDirection.Output
                    .ExecuteNonQuery()

                End With
                Return Trim(cmd.Parameters("@SequenceNumberNext").Value()).ToString()
            Catch Exc As Exception
                Throw
            Finally
                cmd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

    End Class
End Namespace
