#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.DataAccess.Custom
    Public Class TeamOPIEvents

#Region " Select Team OPI Event"
        Public Shared Function SelectTeamOPIEvent(ByVal passTeamID As Integer, ByVal passOPI As String, ByVal passEventDate As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, passOPI, passEventDate, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTeamOPIEvent", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TeamID", passTeamID)
                da.SelectCommand.Parameters.AddWithValue("@OPI", passOPI)
                da.SelectCommand.Parameters.AddWithValue("@EventDate", passEventDate)
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

#Region " Insert Team OPI Event"
        Public Shared Sub InsertTeamOPIEvent(ByVal passTeamID As Integer, _
                                             ByVal passOPI As String, _
                                             ByVal passEventDate As String, _
                                             ByVal passEventDescription As String, _
                                             ByVal passShortDescription As String, _
                                             ByVal passLineWidth As Integer, _
                                             ByVal passLineStyle As Integer, _
                                             ByVal passLineColor As String, _
                                             Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passTeamID, _
                                                                                     passOPI, _
                                                                                     passEventDate, _
                                                                                     passEventDescription, _
                                                                                     passShortDescription, _
                                                                                     passLineWidth, _
                                                                                     passLineStyle, _
                                                                                     passLineColor, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spInsTeamOPIEvent", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@TeamID", passTeamID)
                cmSelect.Parameters.AddWithValue("@OPI", passOPI)
                cmSelect.Parameters.AddWithValue("@EventDate", passEventDate)
                cmSelect.Parameters.AddWithValue("@EventDescription", passEventDescription)
                cmSelect.Parameters.AddWithValue("@ShortDescription", passShortDescription)
                cmSelect.Parameters.AddWithValue("@EventLineWidth", passLineWidth)
                cmSelect.Parameters.AddWithValue("@EventLineStyle", passLineStyle)
                cmSelect.Parameters.AddWithValue("@EventLineColor", passLineColor)
                cmSelect.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " Update Team OPI Event"
        Public Shared Sub UpdateTeamOPIEvent(ByVal passTeamID As Integer, _
                                             ByVal passOPI As String, _
                                             ByVal passEventDate As String, _
                                             ByVal passEventDescription As String, _
                                             ByVal passShortDescription As String, _
                                             ByVal passLineWidth As Integer, _
                                             ByVal passLineStyle As Integer, _
                                             ByVal passLineColor As String, _
                                             Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passTeamID, _
                                                                                     passOPI, _
                                                                                     passEventDate, _
                                                                                     passEventDescription, _
                                                                                     passShortDescription, _
                                                                                     passLineWidth, _
                                                                                     passLineStyle, _
                                                                                     passLineColor, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spUpdTeamOPIEvent", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@TeamID", passTeamID)
                cmSelect.Parameters.AddWithValue("@OPI", passOPI)
                cmSelect.Parameters.AddWithValue("@EventDate", passEventDate)
                cmSelect.Parameters.AddWithValue("@EventDescription", passEventDescription)
                cmSelect.Parameters.AddWithValue("@ShortDescription", passShortDescription)
                cmSelect.Parameters.AddWithValue("@EventLineWidth", passLineWidth)
                cmSelect.Parameters.AddWithValue("@EventLineStyle", passLineStyle)
                cmSelect.Parameters.AddWithValue("@EventLineColor", passLineColor)
                cmSelect.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " Delete Team OPI Event"
        Public Shared Sub DeleteTeamOPIEvent(ByVal passTeamID As Integer, _
                                             ByVal passOPI As String, _
                                             ByVal passEventDate As String, _
                                             Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passTeamID, _
                                                                                     passOPI, _
                                                                                     passEventDate, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spDelTeamOPIEvent", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@TeamID", passTeamID)
                cmSelect.Parameters.AddWithValue("@OPI", passOPI)
                cmSelect.Parameters.AddWithValue("@EventDate", passEventDate)
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
