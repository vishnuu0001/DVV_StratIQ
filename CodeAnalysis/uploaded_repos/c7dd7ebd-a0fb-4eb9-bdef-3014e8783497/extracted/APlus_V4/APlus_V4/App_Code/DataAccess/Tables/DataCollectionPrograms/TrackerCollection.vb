#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class TrackerCollection

#Region " Select Methods"
        Public Shared Function SelectTrackerCollection(ByVal passTrackerCollectionID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTrackerCollectionID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTrackerCollection", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TrackerCollectionID", passTrackerCollectionID)
                da.Fill(dt)

                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectTrackerTypesByTracker(ByVal passTrackerID As Integer, _
                                                       Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTrackerID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTrackerTypesByTracker", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TrackerID", passTrackerID)
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

#Region " Table Methods"
        Public Shared Function AddTrackerCollection(ByVal passTrackerID As Integer, ByVal passTrackerTypeID As Integer, ByVal passSavingsTypeID As Integer, _
        ByVal passFormula As String, ByVal passTrackerVariables As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTrackerID, passTrackerTypeID, passSavingsTypeID, passFormula, passTrackerVariables, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsTrackerCollection", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmAdd.CommandType = CommandType.StoredProcedure
                cmAdd.Parameters.AddWithValue("@TrackerID", passTrackerID)
                cmAdd.Parameters.AddWithValue("@TrackerTypeID", passTrackerTypeID)
                cmAdd.Parameters.AddWithValue("@SavingsTypeID", passSavingsTypeID)
                If passFormula.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@Formula", passFormula)
                End If
                If passTrackerVariables.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@TrackerVariables", passTrackerVariables.Trim)
                End If

                Return Convert.ToInt16(cmAdd.ExecuteScalar)
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Sub UpdateTrackerCollection(ByVal passTrackerCollectionID As Integer, ByVal passFormula As String, ByVal passTrackerVariables As String, _
                                                  Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTrackerCollectionID, passFormula, passTrackerVariables, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdTrackerCollection", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmUpdate.CommandType = CommandType.StoredProcedure
                cmUpdate.Parameters.AddWithValue("@TrackerCollectionID", passTrackerCollectionID)
                If passFormula.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@Formula", passFormula)
                End If
                If passTrackerVariables.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@TrackerVariables", passTrackerVariables.Trim)
                End If

                cmUpdate.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub DeleteTrackerCollection(ByVal passTrackerCollectionID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTrackerCollectionID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelTrackerCollection", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmDelete.CommandType = CommandType.StoredProcedure
                cmDelete.Parameters.AddWithValue("@TrackerCollectionID", passTrackerCollectionID)
                cmDelete.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmDelete.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

    End Class
End Namespace

