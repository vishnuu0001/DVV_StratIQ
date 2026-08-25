#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class TeamOPIControlLimits

#Region " Select Team OPI Control Limits"
        Public Shared Function SelectTeamOPIControlLimit(ByVal passTeamID As Integer, ByVal passOPI As String, ByVal passStartDate As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, passOPI, passStartDate, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTeamOPIControlLimit", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TeamID", passTeamID)
                da.SelectCommand.Parameters.AddWithValue("@OPI", passOPI)
                da.SelectCommand.Parameters.AddWithValue("@StartDate", passStartDate)
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

#Region " Insert Team OPI Control Limit"
        Public Shared Sub InsertTeamOPIControlLimit(ByVal passTeamID As Integer, _
                                                    ByVal passOPI As String, _
                                                    ByVal passStartDate As String, _
                                                    ByVal passUpperValue As String, _
                                                    ByVal passLowerValue As String, _
                                                    ByVal passDescription As String, _
                                                    Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passTeamID, _
                                                                                     passOPI, _
                                                                                     passStartDate, _
                                                                                     passUpperValue, _
                                                                                     passLowerValue, _
                                                                                     passDescription, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spInsTeamOPIControlLimit", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@TeamID", passTeamID)
                cmSelect.Parameters.AddWithValue("@OPI", passOPI)
                cmSelect.Parameters.AddWithValue("@StartDate", passStartDate)
                If passUpperValue.Trim.Length > 0 Then
                    cmSelect.Parameters.AddWithValue("@UpperValue", passUpperValue)
                End If
                If passLowerValue.Trim.Length > 0 Then
                    cmSelect.Parameters.AddWithValue("@LowerValue", passLowerValue)
                End If
                If passDescription.Trim.Length > 0 Then
                    cmSelect.Parameters.AddWithValue("@Description", passDescription)
                End If
                cmSelect.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " Update Team OPI Control Limit"
        Public Shared Sub UpdateTeamOPIControlLimit(ByVal passTeamID As Integer, _
                                                    ByVal passOPI As String, _
                                                    ByVal passStartDate As String, _
                                                    ByVal passUpperValue As String, _
                                                    ByVal passLowerValue As String, _
                                                    ByVal passDescription As String, _
                                                    Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passTeamID, _
                                                                                     passOPI, _
                                                                                     passStartDate, _
                                                                                     passUpperValue, _
                                                                                     passLowerValue, _
                                                                                     passDescription, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spUpdTeamOPIControlLimit", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@TeamID", passTeamID)
                cmSelect.Parameters.AddWithValue("@OPI", passOPI)
                cmSelect.Parameters.AddWithValue("@StartDate", passStartDate)
                If passUpperValue.Trim.Length > 0 Then
                    cmSelect.Parameters.AddWithValue("@UpperValue", passUpperValue)
                End If
                If passLowerValue.Trim.Length > 0 Then
                    cmSelect.Parameters.AddWithValue("@LowerValue", passLowerValue)
                End If
                If passDescription.Trim.Length > 0 Then
                    cmSelect.Parameters.AddWithValue("@Description", passDescription)
                End If
                cmSelect.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " Delete Team OPI Control Limit"
        Public Shared Sub DeleteTeamOPIControlLimit(ByVal passTeamID As Integer, ByVal passOPI As String, ByVal passStartDate As String, _
                                                    Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, passOPI, passStartDate, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spDelTeamOPIControlLimit", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@TeamID", passTeamID)
                cmSelect.Parameters.AddWithValue("@OPI", passOPI)
                cmSelect.Parameters.AddWithValue("@StartDate", passStartDate)
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
