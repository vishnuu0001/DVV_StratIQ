#Region "Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports Microsoft.VisualBasic
Imports WebApp.APlus.DataAccess.Connections
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.DataAccess.SLICETables
    Public Class SLICEActivityGroupMaster

#Region " - Select SLICEActivityGroupMaster and Return Dropdownlist values"
        Public Shared Sub SelectSLICEActivityGroupMasterList(ByRef ddlList As System.Web.UI.WebControls.DropDownList, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, ddlList.ID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelSLICEActivityGroupMasterList", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    ddlList.Items.Add(New ListItem(drList.GetString(1), drList.GetInt32(0).ToString()))
                End While
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " - Select"
        Public Shared Function SelectSLICEActivityGroupMaster(ByVal passSLICEActivityGroup As String, ByVal passSLICEActivityGroupDescription As String, ByVal passWorkcenterID As Integer, ByVal passTargetDeviation As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSLICEActivityGroup, passSLICEActivityGroupDescription, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelSLICEActivityGroupMaster", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@SLICEActivityGroup", passSLICEActivityGroup)
                da.SelectCommand.Parameters.AddWithValue("@SLICEActivityGroupDescription", passSLICEActivityGroupDescription)
                da.SelectCommand.Parameters.AddWithValue("@WorkcenterID", passWorkcenterID)
                da.SelectCommand.Parameters.AddWithValue("@TargetDeviation", passTargetDeviation)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function

        Public Shared Function SelectSLICEActivityGroupMasterByID(ByVal passSLICEActivityGroupID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSLICEActivityGroupID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelSLICEActivityGroupMasterListByID", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@intID", passSLICEActivityGroupID)
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

#Region " - Add "
        Public Shared Function AddSLICEActivityGroupMaster(ByVal passSLICEActivityGroup As String, _
                                                      ByVal passSLICEActivityGroupDescription As String, _
                                                      ByVal passWorkcenterID As Integer, _
                                                      ByVal passTargetDeviation As Integer, _
                                                      Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passSLICEActivityGroup, _
                                                                                     passSLICEActivityGroupDescription, _
                                                                                     passWorkcenterID, _
                                                                                     passTargetDeviation, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spInsSLICEActivityGroupMaster", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    If passWorkcenterID <> -1 Then
                        .Parameters.AddWithValue("@WorkcenterID", passWorkcenterID)
                    End If
                    .Parameters.AddWithValue("@SLICEActivityGroup", passSLICEActivityGroup)
                    .Parameters.AddWithValue("@SLICEActivityGroupDescription", passSLICEActivityGroupDescription)
                    .Parameters.AddWithValue("@TargetDeviation", passTargetDeviation)
                    Return .ExecuteScalar()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " Update"
        Public Shared Sub UpdateSLICEActivityGroupMaster(ByVal passActivityGroupID As String, _
                                                         ByVal passSLICEActivityGroup As String, _
                                                         ByVal passSLICEActivityGroupDescription As String, _
                                                         ByVal passWorkcenterID As Integer, _
                                                         ByVal passTargetDeviation As Integer, _
                                                         Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passActivityGroupID, _
                                                                                     passSLICEActivityGroup, _
                                                                                     passSLICEActivityGroupDescription, _
                                                                                     passWorkcenterID, _
                                                                                     passTargetDeviation, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdSLICEActivityGroupMaster", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@SLICEActivityGroup", passSLICEActivityGroup)
                    .Parameters.AddWithValue("@SLICEActivityGroupDescription", passSLICEActivityGroupDescription)
                    .Parameters.AddWithValue("@TargetDeviation", passTargetDeviation)
                    If passWorkcenterID <> -1 Then
                        .Parameters.AddWithValue("@WorkcenterID", passWorkcenterID)
                    End If
                    .Parameters.AddWithValue("@SLICEActivityGroupID", passActivityGroupID)
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

#Region " - Delete"
        Public Shared Sub DeleteSLICEActivityGroupMaster(ByVal passSLICEActivityGroupID As Integer, ByVal passWorkcenterID As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSLICEActivityGroupID, passWorkcenterID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelSLICEActivityGroupMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmDelete
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@SLICEActivityGroupID", passSLICEActivityGroupID)
                    .Parameters.AddWithValue("@WorkcenterID", passWorkcenterID)
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

    End Class
End Namespace

