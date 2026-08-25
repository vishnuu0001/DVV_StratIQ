#Region "Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports Microsoft.VisualBasic
Imports WebApp.APlus.DataAccess.Connections
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.DataAccess.SLICETables
    Public Class SLICEActivityMaster

#Region " Select and Fill DDL"
        Public Shared Sub SelectSLICEActivityMasterList(ByRef ddlList As System.Web.UI.WebControls.DropDownList, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
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
            Dim cmSelect As New SqlCommand("spSelSLICEActivityMaster", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    ddlList.Items.Add(New ListItem(drList.GetString(1), drList.GetInt16(0)))
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
        Public Shared Function SelectSLICEActivityMaster(ByVal passSLICEActivityID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataSet
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
            Dim da As New SqlDataAdapter(New SqlCommand("spSelSLICEActivityMaster", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim ds As New DataSet

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@SLICEActivityID", passSLICEActivityID)
                da.Fill(ds)
                Return ds
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " - Select  "
        Public Shared Function SelectSLICEActivityMasterAsDataTable(ByVal passSLICEActivityID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
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
            Dim da As New SqlDataAdapter(New SqlCommand("spSelSLICEActivityMaster", cnSubConnection.OpenConnection(cnMasterConnection)))
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

        Public Shared Function SelectSLICEActivityMasterDataAsDataTable(ByVal passSLICEActivityID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
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
            Dim da As New SqlDataAdapter(New SqlCommand("spSelSLICEDataForPrintFriendlyPage", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@ActivityGroupMaster", passSLICEActivityID)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function

        Public Shared Function SelectSLICEActivityIDBySLICEGroupID(ByVal passSLICEActivityGroupID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
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
            Dim da As New SqlDataAdapter(New SqlCommand("spSelSLICEActivityMasterIDbyGroupID", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@intActivityID", passSLICEActivityGroupID)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function

        Public Shared Function CheckSLICEActivityInformation(ByVal passWorkCenterID As Integer, _
                                                             ByVal passActivityGrp As String, _
                                                             ByVal passEntity As String, _
                                                             ByVal passPosition As String, _
                                                             ByVal passSLICEType As String, _
                                                             ByVal passSLICEFreq As String, _
                                                             ByVal passSLICEResults As String, _
                                                            Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passWorkCenterID, _
                                                                                     passActivityGrp, _
                                                                                     passEntity, _
                                                                                     passPosition, _
                                                                                     passSLICEType, _
                                                                                     passSLICEFreq, _
                                                                                     passSLICEResults, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim myParm As SqlParameter
            Dim cmdCheck As New SqlCommand("spCheckSLICEActivityInformation", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmdCheck
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@intWorkCenterID", passWorkCenterID)
                    .Parameters.AddWithValue("@vchActivityGroup", passActivityGrp)
                    .Parameters.AddWithValue("@vchEntityInput", passEntity)
                    .Parameters.AddWithValue("@vchPositionInput", passPosition)
                    .Parameters.AddWithValue("@vchSLICEType", passSLICEType)
                    .Parameters.AddWithValue("@vchSLICEFrequency", passSLICEFreq)
                    .Parameters.AddWithValue("@vchSLICEResults", passSLICEResults)
                    myParm = .Parameters.Add("@RETURN_VALUE", SqlDbType.Int)
                    myParm.Direction = ParameterDirection.ReturnValue
                    .ExecuteNonQuery()
                End With
                Return cmdCheck.Parameters("@RETURN_VALUE").Value()
            Catch Exc As Exception
                Throw
            Finally
                cmdCheck.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function

        Public Shared Function CheckSLICEActivityGrpForUniqPresSeqNum(ByVal passActivityGrp As String, _
                                                                      ByVal passPresSeqNum As Integer, _
                                                                      Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passActivityGrp, passPresSeqNum, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim myParm As SqlParameter
            Dim cmdCheck As New SqlCommand("spCheckSLICEActivityGrpForUniqPresSeq", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmdCheck
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@vchSLICEActivityGrp", passActivityGrp)
                    .Parameters.AddWithValue("@intPresSeqNum", passPresSeqNum)
                    myParm = .Parameters.Add("@RETURN_VALUE", SqlDbType.Int)
                    myParm.Direction = ParameterDirection.ReturnValue
                    .ExecuteNonQuery()
                End With
                Return cmdCheck.Parameters("@RETURN_VALUE").Value()
            Catch Exc As Exception
                Throw
            Finally
                cmdCheck.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function

        Public Shared Function SelectSLICEActivityMasterDataByActivityGroupID(ByVal passActivityGroupID As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passActivityGroupID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelSLICEActivityMasterByActivityGroupMasterID", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@ActivityGroupMaster", passActivityGroupID)
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
        Public Shared Function AddSLICEActivityMaster(ByVal passSLICEActivityGroupID As Integer, _
                                                 ByVal passEntityID As Integer, _
                                                 ByVal passPositionID As Integer, _
                                                 ByVal passPresentationSequence As String, _
                                                 ByVal passSLICEFrequencyID As Integer, _
                                                 ByVal passMeasurement As String, _
                                                 ByVal passDesiredCondition As String, _
                                                 ByVal passTargetTime As Integer, _
                                                 Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passSLICEActivityGroupID, _
                                                                                     passEntityID, _
                                                                                     passPositionID, _
                                                                                     passPresentationSequence, _
                                                                                     passSLICEFrequencyID, _
                                                                                     passMeasurement, _
                                                                                     passDesiredCondition, _
                                                                                     passTargetTime, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsSLICEActivityMaster", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmAdd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@SLICEActivityGroupID", passSLICEActivityGroupID)
                    .Parameters.AddWithValue("@EntityID", passEntityID)
                    .Parameters.AddWithValue("@PositionID", passPositionID)
                    .Parameters.AddWithValue("@SLICEFrequencyID", passSLICEFrequencyID)
                    .Parameters.AddWithValue("@PresentationSequence", passPresentationSequence)
                    .Parameters.AddWithValue("@Measurement", passMeasurement)
                    .Parameters.AddWithValue("@DesiredCondition", passDesiredCondition)
                    .Parameters.AddWithValue("@TargetTime", passTargetTime)
                    Return .ExecuteScalar()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Sub AddSLICEActivityExcelImportData(ByVal passWorkCenterID As Integer, _
                                                          ByVal passSLICEActivityGroup As String, _
                                                          ByVal passEntity As String, _
                                                          ByVal passPosition As String, _
                                                          ByVal passSLICETypes As String, _
                                                          ByVal passPresentationSeqNum As Integer, _
                                                          ByVal passSLICEFrequency As String, _
                                                          ByVal passMeasurement As String, _
                                                          ByVal passDesiredCondition As String, _
                                                          ByVal passSLICEResults As String, _
                                                          ByVal passTargetTime As Integer, _
                                                          Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passWorkCenterID, _
                                                                                     passSLICEActivityGroup, _
                                                                                     passEntity, _
                                                                                     passPosition, _
                                                                                     passSLICETypes, _
                                                                                     passPresentationSeqNum, _
                                                                                     passSLICEFrequency, _
                                                                                     passMeasurement, _
                                                                                     passDesiredCondition, _
                                                                                     passSLICEResults, _
                                                                                     passTargetTime, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsSLICEActivityExcelImportData", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmAdd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@intWorkCenterID", passWorkCenterID)
                    .Parameters.AddWithValue("@vchActivityGrpDesc", passSLICEActivityGroup)
                    .Parameters.AddWithValue("@vchEntity", passEntity)
                    .Parameters.AddWithValue("@vchPosition", passPosition)
                    .Parameters.AddWithValue("@vchSLICEType", passSLICETypes)
                    .Parameters.AddWithValue("@vchSLICEFrequency", passSLICEFrequency)
                    .Parameters.AddWithValue("@intPresentationSeqNum", passPresentationSeqNum)
                    .Parameters.AddWithValue("@vchMeasurement", passMeasurement)
                    .Parameters.AddWithValue("@vchDesiredCondition", passDesiredCondition)
                    .Parameters.AddWithValue("@vchSLICEResults", passSLICEResults)
                    .Parameters.AddWithValue("@intTargetTime", passTargetTime)
                    .ExecuteNonQuery()
                End With
            Catch exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " Update"
        Public Shared Sub UpdateSLICEActivityMaster(ByVal passSLICEActivityID As String, _
                                                         ByVal passSLICEActivityGroupID As String, _
                                                         ByVal passEntityID As String, _
                                                         ByVal passPositionID As String, _
                                                         ByVal passSLICEFrequencyID As String, _
                                                         ByVal passPresentationSequence As String, _
                                                         ByVal passMeasurement As String, _
                                                         ByVal passDesiredCondition As String, _
                                                         ByVal passTargetTime As String, _
                                                         Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passSLICEActivityID, _
                                                                                     passSLICEActivityGroupID, _
                                                                                     passEntityID, _
                                                                                     passPositionID, _
                                                                                     passSLICEFrequencyID, _
                                                                                     passPresentationSequence, _
                                                                                     passMeasurement, _
                                                                                     passDesiredCondition, _
                                                                                     passTargetTime, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdSLICEActivityMaster", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@SLICEActivityID", passSLICEActivityID)
                    .Parameters.AddWithValue("@SLICEActivityGroupID", passSLICEActivityGroupID)
                    .Parameters.AddWithValue("@EntityID", passEntityID)
                    .Parameters.AddWithValue("@PositionID", passPositionID)
                    .Parameters.AddWithValue("@SLICEFrequencyID", passSLICEFrequencyID)
                    .Parameters.AddWithValue("@PresentationSequence", passPresentationSequence)
                    .Parameters.AddWithValue("@Measurement", passMeasurement)
                    .Parameters.AddWithValue("@DesiredCondition", passDesiredCondition)
                    .Parameters.AddWithValue("@TargetTime", passTargetTime)
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
        Public Shared Sub DeleteSLICEActivityMaster(ByVal passSLICEActivityID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
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
            Dim cmDelete As New SqlCommand("spDelSLICEActivityMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmDelete
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@SLICEActivityID", passSLICEActivityID)
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

