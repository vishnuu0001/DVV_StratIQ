#Region "Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports Microsoft.VisualBasic
Imports WebApp.APlus.DataAccess.Connections
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.DataAccess.SLICETables
    Public Class SLICEResultMaster

#Region " Select SLICEResult Master List"
        Public Shared Sub SelectSLICEResultMasterList(ByRef ddlList As System.Web.UI.WebControls.DropDownList, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
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
            Dim cmSelect As New SqlCommand("spSelSLICEResultMasterList", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    ddlList.Items.Add(New ListItem(drList.GetString(0), drList.GetString(0)))
                End While
                ddlList.Items.Insert(0, New ListItem("", ""))
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " Select SLICEResult Master"
        Public Shared Function SelectSLICEResultMaster(ByVal passSLICEResultID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSLICEResultID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelSLICEResultMaster", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@SLICEResultID", passSLICEResultID)
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

#Region " Select SLICEResult Master By ID"
        Public Shared Function SelectSLICEResultMasterByID(ByVal passSLICEResultID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSLICEResultID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelSLICEResultMasterByResultID", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@intID", passSLICEResultID)
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

#Region " Add SLICEResult Master"
        Public Shared Function AddSLICEResultMaster(ByVal passSLICEResultText As String, _
                                               ByVal passPass As Boolean, _
                                               ByVal passPresentationSequence As Integer, _
                                               Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSLICEResultText, passPass, passPresentationSequence, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spInsSLICEResultMaster", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@SLICEResultText", passSLICEResultText)
                    .Parameters.AddWithValue("@Pass", passPass)
                    .Parameters.AddWithValue("@PresentationSequence", passPresentationSequence)
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

#Region " Update SLICEResult Master"
        Public Shared Sub UpdateSLICEResultMaster(ByVal passSLICEResultID As Integer, _
                                                  ByVal passSLICEResultText As String, _
                                                  ByVal passPass As Boolean, _
                                                  ByVal passPresentationSequence As Integer, _
                                                  Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSLICEResultID, passSLICEResultText, passPass, passPresentationSequence, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdSLICEResultMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@SLICEResultID", passSLICEResultID)
                    .Parameters.AddWithValue("@SLICEResultText", passSLICEResultText)
                    .Parameters.AddWithValue("@Pass", passPass)
                    .Parameters.AddWithValue("@PresentationSequence", passPresentationSequence)
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


#Region " Delete SLICEResult Master"
        Public Shared Sub DeleteSLICEResultMaster(ByVal passSLICEResultID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSLICEResultID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelSLICEResultMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmDelete
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@SLICEResultID", passSLICEResultID)
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

