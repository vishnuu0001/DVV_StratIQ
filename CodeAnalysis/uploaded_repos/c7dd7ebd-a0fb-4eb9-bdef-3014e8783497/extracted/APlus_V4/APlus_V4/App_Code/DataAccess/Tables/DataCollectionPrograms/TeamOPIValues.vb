#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class TeamOPIValues

#Region " Select TeamOPI Value"
        Public Shared Function SelectTeamOPIValue(ByVal passTeamOPIValueID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable

            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamOPIValueID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTeamOPIValue", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TeamOPIValueID", passTeamOPIValueID)
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

#Region " Select Team OPI Report Detail ByDate"
        Public Shared Function SelectTeamOPIReportDetailByDate(ByVal passTeamID As Integer, ByVal passOPI As String, ByVal passDate As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, passOPI, passDate, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTeamOPIReportDetail", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TeamID", passTeamID)
                da.SelectCommand.Parameters.AddWithValue("@OPI", passOPI)
                If Not String.IsNullOrEmpty(passDate.Trim()) Then da.SelectCommand.Parameters.AddWithValue("@StartDate", passDate)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " Select Team OPI Report All Detail "
        Public Shared Function SelectTeamOPIReportAllDetail(ByVal passTeamID As Integer, ByVal passOPI As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, passOPI, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTeamOPIReportDetail", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TeamID", passTeamID)
                da.SelectCommand.Parameters.AddWithValue("@OPI", passOPI)
                da.SelectCommand.Parameters.AddWithValue("@Top", True)
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

#Region " Select Team OPI Attribute Defaults"
        Public Shared Function SelectTeamOPIAttributeDefaults(ByVal passTeamID As Integer, ByVal passOPI As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, passOPI, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try


            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTeamOPIAttributeDefaults", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TeamID", passTeamID)
                da.SelectCommand.Parameters.AddWithValue("@OPI", passOPI)
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

#Region " - Select Team OPI Values Report Summary"
        Public Shared Function SelectTeamOPIValuesReportSummary(ByVal passTeamID As Integer, ByVal passOPI As String, Optional ByVal bSortAscending As Boolean = False, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, passOPI, bSortAscending, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTeamOPIValueReportSummary", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TeamID", passTeamID)
                da.SelectCommand.Parameters.AddWithValue("@OPI", passOPI)
                If bSortAscending = True Then da.SelectCommand.Parameters.AddWithValue("@Chart", 1)
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

#Region " Select Team OPI History And Benefit"
        Public Shared Function SelectTeamOPIHistoryAndBenefit(ByVal passTeamID As Integer, ByVal passOPI As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, passOPI, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTeamOPIHistoryAndBenefit", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TeamID", passTeamID)
                da.SelectCommand.Parameters.AddWithValue("@OPI", passOPI)
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

#Region " Insert Team OPI Value"
        Public Shared Function InsertTeamOPIValue(ByVal passTeamID As Integer, ByVal passOPI As String, ByVal passOPIDateTime As String, _
                                                  ByVal passOPIValue As String, ByVal passCost As String, ByVal passNotes As String, _
                                                  ByVal passA1 As String, ByVal passA2 As String, ByVal passA3 As String, ByVal passA4 As String, _
                                                  ByVal passA5 As String, ByVal passA6 As String, ByVal passMaintenanceUserID As String, _
                                                  Optional ByRef cnMasterConnection As SqlConnection = Nothing, Optional ByRef trans As SqlTransaction = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passTeamID, _
                                                                                     passOPI, _
                                                                                     passOPIDateTime, _
                                                                                     passOPIValue, _
                                                                                     passCost, _
                                                                                     passNotes, _
                                                                                     passA1, _
                                                                                     passA2, _
                                                                                     passA3, _
                                                                                     passA4, _
                                                                                     passA5, _
                                                                                     passA6, _
                                                                                     passMaintenanceUserID, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spInsTeamOPIValue", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                If Not trans Is Nothing Then
                    cmSelect.Transaction = trans
                End If
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@TeamID", passTeamID)
                cmSelect.Parameters.AddWithValue("@OPI", passOPI)
                cmSelect.Parameters.AddWithValue("@OPIValueDateTime", passOPIDateTime)
                If Not String.IsNullOrEmpty(passA1.Trim()) Then cmSelect.Parameters.AddWithValue("@Attribute1Value", passA1.Trim)
                If Not String.IsNullOrEmpty(passA2.Trim()) Then cmSelect.Parameters.AddWithValue("@Attribute2Value", passA2.Trim)
                If Not String.IsNullOrEmpty(passA3.Trim()) Then cmSelect.Parameters.AddWithValue("@Attribute3Value", passA3.Trim)
                If Not String.IsNullOrEmpty(passA4.Trim()) Then cmSelect.Parameters.AddWithValue("@Attribute4Value", passA4.Trim)
                If Not String.IsNullOrEmpty(passA5.Trim()) Then cmSelect.Parameters.AddWithValue("@Attribute5Value", passA5.Trim)
                If Not String.IsNullOrEmpty(passA6.Trim()) Then cmSelect.Parameters.AddWithValue("@Attribute6Value", passA6.Trim)
                cmSelect.Parameters.AddWithValue("@OPIValue", passOPIValue)
                cmSelect.Parameters.AddWithValue("@Cost", passCost)
                cmSelect.Parameters.AddWithValue("@Notes", passNotes)
                cmSelect.Parameters.AddWithValue("@MaintenanceUserID", passMaintenanceUserID)
                Return cmSelect.ExecuteScalar
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " Update Team OPI Value"
        Public Shared Sub UpdateTeamOPIValue(ByVal passTeamOPIValueID As Integer, _
                                             ByVal passOPIValue As String, _
                                             ByVal passCost As String, _
                                             ByVal passNotes As String, _
                                             ByVal passA1 As String, _
                                             ByVal passA2 As String, _
                                             ByVal passA3 As String, _
                                             ByVal passA4 As String, _
                                             ByVal passA5 As String, _
                                             ByVal passA6 As String, _
                                             ByVal passOldA1 As String, _
                                             ByVal passOldA2 As String, _
                                             ByVal passOldA3 As String, _
                                             ByVal passOldA4 As String, _
                                             ByVal passOldA5 As String, _
                                             ByVal passOldA6 As String, _
                                             ByVal passUserID As String, _
                                             Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passTeamOPIValueID, _
                                                                                     passOPIValue, _
                                                                                     passCost, _
                                                                                     passNotes, _
                                                                                     passA1, _
                                                                                     passA2, _
                                                                                     passA3, _
                                                                                     passA4, _
                                                                                     passA5, _
                                                                                     passA6, _
                                                                                     passOldA1, _
                                                                                     passOldA2, _
                                                                                     passOldA3, _
                                                                                     passOldA4, _
                                                                                     passOldA5, _
                                                                                     passOldA6, _
                                                                                     passUserID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spUpdTeamOPIValue", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@TeamOPIValueID", passTeamOPIValueID)
                cmSelect.Parameters.AddWithValue("@OPIValue", passOPIValue)
                cmSelect.Parameters.AddWithValue("@Cost", passCost)
                cmSelect.Parameters.AddWithValue("@Notes", passNotes)
                cmSelect.Parameters.AddWithValue("@MaintenanceUserID", passUserID)
                If Not String.IsNullOrEmpty(passA1.Trim()) Then cmSelect.Parameters.AddWithValue("@Attribute1Value", passA1.Trim)
                If Not String.IsNullOrEmpty(passA2.Trim()) Then cmSelect.Parameters.AddWithValue("@Attribute2Value", passA2.Trim)
                If Not String.IsNullOrEmpty(passA3.Trim()) Then cmSelect.Parameters.AddWithValue("@Attribute3Value", passA3.Trim)
                If Not String.IsNullOrEmpty(passA4.Trim()) Then cmSelect.Parameters.AddWithValue("@Attribute4Value", passA4.Trim)
                If Not String.IsNullOrEmpty(passA5.Trim()) Then cmSelect.Parameters.AddWithValue("@Attribute5Value", passA5.Trim)
                If Not String.IsNullOrEmpty(passA6.Trim()) Then cmSelect.Parameters.AddWithValue("@Attribute6Value", passA6.Trim)
                cmSelect.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " Delete TeamOPIValue"
        Public Shared Sub DeleteTeamOPIValue(ByVal passTeamOPIValueID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamOPIValueID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spDelTeamOPIValue", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@TeamOPIValueID", passTeamOPIValueID)
                cmSelect.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

    End Class
End Namespace
