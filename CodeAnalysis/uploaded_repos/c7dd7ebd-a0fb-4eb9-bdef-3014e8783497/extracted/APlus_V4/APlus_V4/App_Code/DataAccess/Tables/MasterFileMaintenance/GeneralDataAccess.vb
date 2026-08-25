#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class GeneralDataAccess

#Region " Execute Methods"
        Public Shared Function DatabaseQuery(ByVal passSQL As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSQL, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New DataQueryConnection
            Try
                Dim cmSelect As New SqlCommand(passSQL, cnSubConnection.OpenConnection(cnMasterConnection))
                Dim da As New SqlDataAdapter(cmSelect)
                Dim ds As New DataTable
                da.Fill(ds)
                Return ds
            Catch Exc As Exception
                Throw
            Finally
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function ExecuteDatabaseQuery(ByVal passSQL As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSQL, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New DataQueryConnection
            Try
                Dim cmSelect As New SqlCommand(passSQL, cnSubConnection.OpenConnection(cnMasterConnection))
                cmSelect.ExecuteNonQuery()
                Return True
            Catch Exc As Exception
                Throw
                Return False
            Finally
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function ExecuteDatabaseQuery(ByVal passCommandText As String, ByVal passParams As Hashtable, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passCommandText, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New DataQueryConnection
            Dim da As New SqlDataAdapter(New SqlCommand(passCommandText, cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                If passParams IsNot Nothing AndAlso passParams.Count > 0 Then
                    Dim param As SqlParameter
                    Dim myEnumerator As IDictionaryEnumerator = passParams.GetEnumerator()

                    While myEnumerator.MoveNext
                        param = New SqlParameter(myEnumerator.Key.ToString, myEnumerator.Value)
                        If Not da.SelectCommand.Parameters.Contains(param) Then
                            da.SelectCommand.Parameters.Add(param)
                        End If
                    End While
                End If
                da.Fill(dt)

                Return dt
            Catch Exc As Exception
                Throw
            Finally
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

    End Class
End Namespace

