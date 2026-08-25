#Region "Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports Microsoft.VisualBasic
Imports WebApp.APlus.DataAccess.Connections
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.DataAccess.SLICETables
    Public Class SLICEChecksheetMaster

#Region " Select Checksheet Data As DataTable"
        Public Shared Function SelectChecksheetDataAsDataTable(ByVal passSLICEChecksheetID As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSLICEChecksheetID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelSLICEChecksheetByChecksheetID", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@intCheckSheetID", passSLICEChecksheetID)
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

#Region " Select Checksheet Status As DataTable"
        Public Shared Function SelectChecksheetStatusAsDataTable(Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
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
            Dim da As New SqlDataAdapter(New SqlCommand("spSelSLICEChecksheetStatusMaster", cnSubConnection.OpenConnection(cnMasterConnection)))
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
#End Region

#Region " Select Checksheet Data For Input Screen"
        Public Shared Function SelectChecksheetDataForInputScreen(ByVal passReportID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passReportID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelSLICEChecksheetDataForInputScreen", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@intCheckSheetID", passReportID)
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

#Region " Select Data For Checksheet Report"
        Public Shared Function SelectDataForChecksheetReport(ByVal passReportID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passReportID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelSLICEChecksheetReportData", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@intCheckSheetID", passReportID)
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

#Region " Select Checksheet Row Data For Edit"
        Public Shared Function SelectChecksheetRowDataForEdit(ByVal passSliceActivityID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSliceActivityID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelSLICEChecksheetRowDataForEdit", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@intSLICEChecksheetActivityID", passSliceActivityID)
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

#Region " Select Checksheet Data By WorkcenterID"
        Public Shared Function SelectChecksheetDataByWorkcenterID(ByVal passWorkCenterID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passWorkCenterID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelSLICEChecksheetTemplatesByWorkcenterID", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@intWorkCenterID", passWorkCenterID)
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

#Region " Update SLICEChecksheet Master"
        Public Shared Sub UpdateSLICEChecksheetMaster(ByVal passSLICEChecksheetID As Integer, _
                                                      ByVal passSLICEActivityGroupID As Integer, _
                                                      ByVal passReleaseDate As String, _
                                                      ByVal passDueDate As String, _
                                                      ByVal passStatusID As Integer, _
                                                      ByVal passCreateUserID As String, _
                                                      ByVal passCreateDate As String, _
                                                      ByVal passNumPrinted As Integer, _
                                                      ByVal passLastPrintDate As String, _
                                                      ByVal passLastPrintUserID As String, _
                                                      Optional ByRef cnMasterConnection As SqlConnection = Nothing)

            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passSLICEChecksheetID, _
                                                                                     passSLICEActivityGroupID, _
                                                                                     passReleaseDate, _
                                                                                     passDueDate, _
                                                                                     passStatusID, _
                                                                                     passCreateUserID, _
                                                                                     passCreateDate, _
                                                                                     passNumPrinted, _
                                                                                     passLastPrintDate, _
                                                                                     passLastPrintUserID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdSLICEChecksheetMaster", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@SLICEChecksheetID", passSLICEChecksheetID)
                    .Parameters.AddWithValue("@SLICEActivityGroupID", passSLICEActivityGroupID)
                    .Parameters.AddWithValue("@SLICEChecksheetReleaseDate", passReleaseDate)
                    .Parameters.AddWithValue("@SLICEChecksheetDueDate", passDueDate)
                    .Parameters.AddWithValue("@SLICEChecksheetStatusID", passStatusID)
                    .Parameters.AddWithValue("@CreateUserID", passCreateUserID)
                    .Parameters.AddWithValue("@CreatedDateTime", passCreateDate)
                    .Parameters.AddWithValue("@NumberPrinted", passNumPrinted)
                    .Parameters.AddWithValue("@LastPrintedDateTime", passLastPrintDate)
                    .Parameters.AddWithValue("@LastPrintedUserID", passLastPrintUserID)
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

#Region " Update SLICEChecksheet Master StatusID"
        Public Shared Sub UpdateSLICEChecksheetMasterStatusID(ByVal passSLICEChecksheetID As String, ByVal passStatusDesc As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSLICEChecksheetID, passStatusDesc, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdSLICEChecksheetStatus", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@intCheckSheetID", CInt(passSLICEChecksheetID))
                    .Parameters.AddWithValue("@vchChecksheetStatusDesc", passStatusDesc)
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

#Region " Update SLICEActivity Results Row"
        Public Shared Sub UpdateSLICEActivityResultsRow(ByVal passSLICEChecksheetID As Integer, _
                                                                    ByVal passElapsedTime As String, _
                                                                    ByVal passComments As String, _
                                                                    ByVal passWorkOrdNum As String, _
                                                                    ByVal passUserID As String, _
                                                                    ByVal passSLICEResultID As Integer, _
                                                                    Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passSLICEChecksheetID, _
                                                                                     passElapsedTime, _
                                                                                     passComments, _
                                                                                     passWorkOrdNum, _
                                                                                     passUserID, _
                                                                                     passSLICEResultID.ToString, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdSLICEActivityResultData", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@SLICEChecksheetActivityID", CInt(passSLICEChecksheetID))
                    If IsNumeric(passElapsedTime) Then
                        .Parameters.AddWithValue("@ElapsedTime", passElapsedTime)
                    End If
                    If passComments.Trim.Length > 0 Then
                        .Parameters.AddWithValue("@Comments", passComments)
                    End If
                    If passWorkOrdNum > 0 Then
                        .Parameters.AddWithValue("@WorkOrdNum", passWorkOrdNum)
                    End If
                    .Parameters.AddWithValue("@UserID", passUserID)
                    If passSLICEResultID > -1 Then
                        .Parameters.AddWithValue("@SLICEResultID", passSLICEResultID)
                    End If
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

#Region " Add SLICEChecksheet Master"
        Public Shared Function AddSLICEChecksheetMaster(ByVal passSLICEActivityGroupID As Integer, _
                                                            ByVal passReleaseDate As String, _
                                                            ByVal passDueDate As String, _
                                                            ByVal passStatusID As Integer, _
                                                            ByVal passCreateUserID As String, _
                                                            ByVal passCreateDate As String, _
                                                            ByVal passNumPrinted As Integer, _
                                                            ByVal passLastPrintDate As String, _
                                                            ByVal passLastPrintUserID As String, _
                                                            Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passSLICEActivityGroupID, _
                                                                                     passReleaseDate, _
                                                                                     passDueDate, _
                                                                                     passStatusID, _
                                                                                     passCreateUserID, _
                                                                                     passCreateDate, _
                                                                                     passNumPrinted, _
                                                                                     passLastPrintDate, _
                                                                                     passLastPrintUserID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmdAdd As New SqlCommand("spInsSLICEChecksheetMaster", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmdAdd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@SLICEActivityGroupID", passSLICEActivityGroupID)
                    .Parameters.AddWithValue("@SLICEChecksheetReleaseDate", passReleaseDate)
                    .Parameters.AddWithValue("@SLICEChecksheetDueDate", passDueDate)
                    .Parameters.AddWithValue("@SLICEChecksheetStatusID", passStatusID)
                    .Parameters.AddWithValue("@CreateUserID", passCreateUserID)
                    .Parameters.AddWithValue("@CreatedDateTime", passCreateDate)
                    .Parameters.AddWithValue("@NumberPrinted", passNumPrinted)
                    .Parameters.AddWithValue("@LastPrintedDateTime", passLastPrintDate)
                    .Parameters.AddWithValue("@LastPrintedUserID", passLastPrintUserID)
                    Return .ExecuteScalar()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmdAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " Add SLICEChecksheet Activity Master"
        Public Shared Sub AddSLICEChecksheetActivityMaster(ByVal passSLICEChecksheetID As String, _
                                                           ByVal passSLICEActivityID As String, _
                                                           Optional ByRef cnMasterConnection As SqlConnection = Nothing, _
                                                           Optional ByRef Trans As SqlTransaction = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passSLICEChecksheetID, _
                                                                                     passSLICEActivityID, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmdAdd As New SqlCommand("spInsSLICEChecksheetActivityMaster", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                If Trans IsNot Nothing Then
                    cmdAdd.Transaction = Trans
                End If
                With cmdAdd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@CheckSheetID", passSLICEChecksheetID)
                    .Parameters.AddWithValue("@SLICEActivityID", passSLICEActivityID)
                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmdAdd.Dispose()
                If Trans IsNot Nothing Then

                End If
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " Insert Values To SLICEChecksheet Activity Master"
        Public Shared Sub InsertValuesToSLICEChecksheetActivityMaster(ByVal passCheckSheetID As String, ByVal passSLICEActivityGrpID As String)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passCheckSheetID, passSLICEActivityGrpID)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnMasterConnection As SqlConnection = ApplicationConnection.OpenMasterConnection
            Dim trans As SqlTransaction = cnMasterConnection.BeginTransaction(IsolationLevel.ReadUncommitted)
            Try
                Dim dt As DataTable = SLICEActivityMaster.SelectSLICEActivityMasterDataByActivityGroupID(passSLICEActivityGrpID)
                If dt.Rows.Count > 0 Then
                    For x As Integer = 0 To dt.Rows.Count - 1
                        SLICEChecksheetMaster.AddSLICEChecksheetActivityMaster(passCheckSheetID, dt.Rows(x)("SLICEActivityID").ToString().Trim(), cnMasterConnection, trans)
                    Next
                End If
                trans.Commit()
            Catch Exc As Exception
                trans.Rollback()
                Throw
            Finally
                ApplicationConnection.CloseMasterConnection(cnMasterConnection, trans)
            End Try
        End Sub
#End Region

#Region " Insert SLICEChecksheet Results Comments Data"
        Public Shared Function InsertSLICEChecksheetResultsCommentsData(ByVal passSLICEActivityID As Integer, _
                                                            ByVal passElapsedTime As Integer, _
                                                            ByVal passUserID As String, _
                                                            ByVal passWorkOrderNumber As Integer, _
                                                            ByVal passSLICEResultID As Integer, _
                                                            ByVal passComments As String, _
                                                            ByVal passTransactionUserID As String, _
                                                            ByVal passSLICECheckSheetActivityID As Integer, _
                                                            Optional ByRef cnMasterConnection As SqlConnection = Nothing, _
                                                            Optional ByRef trans As SqlTransaction = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passSLICEActivityID, _
                                                                                     passElapsedTime, _
                                                                                     passUserID, _
                                                                                     passWorkOrderNumber, _
                                                                                     passSLICEResultID, _
                                                                                     passComments, _
                                                                                     passTransactionUserID, _
                                                                                     passSLICECheckSheetActivityID, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmdAdd As New SqlCommand("spInsSLICEChecksheetResultsAndComments", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmdAdd
                    If trans IsNot Nothing Then
                        .Transaction = trans
                    End If
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@SLICEActivityID", passSLICEActivityID)
                    .Parameters.AddWithValue("@ElapsedTime", passElapsedTime)
                    .Parameters.AddWithValue("@UserID", passUserID)
                    .Parameters.AddWithValue("@WorkOrderNumber", passWorkOrderNumber)
                    .Parameters.AddWithValue("@SLICEResultID", passSLICEResultID)
                    .Parameters.AddWithValue("@Comments", passComments)
                    .Parameters.AddWithValue("@TransactionUserID", passTransactionUserID)
                    .Parameters.AddWithValue("@SLICECheckSheetActivityID", passSLICECheckSheetActivityID)
                    Return .ExecuteScalar()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmdAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " Delete SLICEChecksheet Master"
        Public Shared Sub DeleteSLICEChecksheetMaster(ByVal passSLICEChecksheetID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DASlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSLICEChecksheetID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmdDelete As New SqlCommand("spDelSLICEChecksheetMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmdDelete
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@SLICEChecksheetID", passSLICEChecksheetID)
                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmdDelete.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

    End Class
End Namespace

