#Region "Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports Microsoft.VisualBasic
Imports WebApp.APlus.DataAccess.Connections
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.DataAccess.SLICETables
    Public Class SLICEActivityLinks

#Region " - Select "
        Public Shared Function SelectActivityLinkDataAsDataTable(ByVal passSLICEActivityID As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
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
            Dim da As New SqlDataAdapter(New SqlCommand("spSelSLICEActivityLinkDataByActivityID", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@SLICEActivityID", passSLICEActivityID)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function

        Public Shared Function SelectSLICETypeAsDataTable(ByVal passSLICEActivityLinkID As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSLICEActivityLinkID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelSLICETypeBasedOnActivityID", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@intActivityID", passSLICEActivityLinkID)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectActivityLinkDataAsDataTableByActivityLinkID(ByVal passSLICEActivityLinkID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSLICEActivityLinkID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelSLICEActivityLinkDataByActivityLinkID", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@SLICEActivityLinkID", passSLICEActivityLinkID)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function

        Public Shared Sub SelectActivityLinksTypes(ByRef ddlList As System.Web.UI.WebControls.DropDownList, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
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
            Dim drList As SqlDataReader = Nothing
            Dim cmSelect As New SqlCommand("spSelSLICEActivityLinkTypeMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    ddlList.Items.Add(New ListItem(drList.GetString(1), drList.GetInt32(0).ToString()))
                End While
                cmSelect.Dispose()
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " - Update "
        Public Shared Sub UpdateSLICEActivityLinksMaster(ByVal passSLICEActivityLinkID As String, _
                                                            ByVal passSLICEActivityID As String, _
                                                            ByVal passActivityLinkTypeID As String, _
                                                            ByVal passLinkDescriprion As String, _
                                                            ByVal passLinkURL As String, _
                                                            Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passSLICEActivityLinkID, _
                                                                                     passSLICEActivityID, _
                                                                                     passActivityLinkTypeID, _
                                                                                     passLinkDescriprion, _
                                                                                     passLinkURL, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdSLICEActivityLinks", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@SLICEActivityLinkID", passSLICEActivityLinkID)
                    .Parameters.AddWithValue("@SLICEActivityID", passSLICEActivityID)
                    .Parameters.AddWithValue("@SLICEActivityLinkTypeID", passActivityLinkTypeID)
                    .Parameters.AddWithValue("@LinkDescription", passLinkDescriprion)
                    .Parameters.AddWithValue("@LinkURL", passLinkURL)
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

#Region " Add "
        Public Shared Function InsertSLICEActivityLinksMaster(ByVal passSLICEActivityID As String, _
                                                         ByVal passActivityLinkTypeID As String, _
                                                         ByVal passLinkDescriprion As String, _
                                                         ByVal passLinkURL As String, _
                                                         Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passSLICEActivityID, _
                                                                                     passActivityLinkTypeID, _
                                                                                     passLinkDescriprion, _
                                                                                     passLinkURL, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spInsSLICEActivityLink", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure

                    .Parameters.AddWithValue("@SLICEActivityID", passSLICEActivityID)
                    .Parameters.AddWithValue("@SLICEActivityLinkTypeID", passActivityLinkTypeID)
                    .Parameters.AddWithValue("@LinkDescription", passLinkDescriprion)
                    .Parameters.AddWithValue("@LinkURL", passLinkURL)
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

#Region " - Delete"
        Public Shared Sub DeleteSLICEActivityLink(ByVal passSLICEActivityLinkID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSLICEActivityLinkID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelSLICEActivityLink", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmDelete
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@SLICEActivityLinkID", passSLICEActivityLinkID)
                    .ExecuteNonQuery()
                End With
            Catch exc As Exception
                Throw
            Finally
                cmDelete.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

    End Class
End Namespace

