#Region "Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports Microsoft.VisualBasic
Imports WebApp.APlus.DataAccess.Connections
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.DataAccess.SLICETables
    Public Class SLICEActivityResultMaster

#Region " - Select "
        Public Shared Function SelectSLICEResultTextAndPassAsDataTable(Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelSLICEResultMasterData", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function

        Public Shared Function SelectSLICEActivityResultsBasedOnSLICEActivityID(ByRef passActivityID As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passActivityID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelSLICEResultsBySLICEActivityID", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@ActivityID", passActivityID)
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

#Region " - Delete "
        Public Shared Sub DeleteSLICEActivityResultByActivityId(ByVal passSLICEActivityID As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSLICEActivityID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelSLICEActivityResultMasterByActivityID", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmDelete
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@intActivityID", passSLICEActivityID)
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

#Region " - Insert "
        Public Shared Sub InsertSLICEActivityResultMaster(ByVal passSLICEActivityID As Integer, _
                                                            ByVal passSLICEResultTextList As String, _
                                                            Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSLICEActivityID, passSLICEResultTextList, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spInsSLICEActivityResultMasterWrapper", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@intActivityID", passSLICEActivityID)
                    .Parameters.AddWithValue("@vchResultTextList", passSLICEResultTextList)
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

    End Class
End Namespace

