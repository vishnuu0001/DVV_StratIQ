#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class AnomalyMaster

#Region " Select Methods"
        Public Shared Function SelectAnomalyMasterByID(ByVal passAnomalyID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passAnomalyID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelAnomalyMasterByID", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@AnomalyID", passAnomalyID)
                da.SelectCommand.Parameters.AddWithValue("@UserID", SessionManager.UserID)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function AnomalyActionRequiresCause(ByVal passAnomalyID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passAnomalyID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelAnomalyTypeByAnomalyID", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Dim bReturn As Boolean = False

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@AnomalyID", passAnomalyID)
                da.Fill(dt)

                If dt IsNot Nothing AndAlso dt.Rows.Count = 1 Then
                    If Convert.ToBoolean(dt.Rows(0)("CauseRequired")) Then
                        bReturn = True
                    End If
                End If
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try

            Return bReturn
        End Function
        Public Shared Function AnomalyIsClosed(ByVal passAnomalyID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passAnomalyID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim bReturn As Boolean = False

            Dim objDT As DataTable = SelectAnomalyMasterByID(passAnomalyID, cnMasterConnection)
            If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                If objDT.Rows(0)("ClosedDateTime").ToString.Trim.Length > 0 Then
                    bReturn = True
                End If
            End If

            Return bReturn
        End Function
        Public Shared Function SelectAnomalyEditAuthority(ByVal passAnomalyID As Integer, ByVal passUserID As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passAnomalyID, passUserID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelAnomalyEditAuthority", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@AnomalyID", passAnomalyID)
                da.SelectCommand.Parameters.AddWithValue("@UserID", passUserID)
                da.Fill(dt)

                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectAnomalyMasterByKPI(ByVal passKPIID As Integer, ByVal passKPIPeriod As String, ByVal passKPIValueType As String, _
                                                        Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelAnomalyMasterByKPI", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@KPIID", passKPIID)
                da.SelectCommand.Parameters.AddWithValue("@KPIPeriod", passKPIPeriod)
                da.SelectCommand.Parameters.AddWithValue("@KPIValueType", passKPIValueType)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectAnomalyMasterByUserSite(ByVal passUserID As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelAnomalyMasterByUserSite", cnSubConnection.OpenConnection(cnMasterConnection)))

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@UserID", passUserID)

                Return da.SelectCommand.ExecuteScalar
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectMyDashboardAnomalies(ByVal passUserID As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelMyDashboardAnomalies", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@UserID", passUserID)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Sub SelectAnomalyUserNameList(ByVal passSiteID As Integer, ByRef ddlList As System.Web.UI.WebControls.DropDownList, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSiteID, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelAnomalyUserNameList", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@SiteID", passSiteID)
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    ddlList.Items.Add(New ListItem(drList.GetString(1) & " (" & drList.GetString(0) & ")", drList.GetString(0)))
                End While
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " Table Methods"
        Public Shared Function AddAnomaly(ByVal passAnomaly As String, ByVal passAnomalyTypeID As Integer, ByVal passSiteID As Integer, ByVal passAreaID As Integer, _
                                          ByVal passSubject As String, ByVal passKPIID As Integer, ByVal passKPIPeriod As String, ByVal passKPIValueType As String, _
                                          ByVal passCreatedDate As String, ByVal passCreatedUserID As String, ByVal passResponsibleUserID As String, _
                                          ByVal passAnomalyOrigin1ID As Integer, ByVal passAnomalyOrigin2ID As Integer, ByVal passAnomalyOrigin3ID As Integer, _
                                          ByVal passObservations As String, ByVal passClosedDate As String, ByVal passCancelled As Boolean, _
                                          ByVal passEvaluation As String, ByVal passEvaluatedDate As String, ByVal passIneffective As Boolean, _
                                          ByVal passAutoGenerated As Boolean, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Return AddAnomaly(passAnomaly, passAnomalyTypeID, passSiteID, passAreaID, passSubject, passKPIID, passKPIPeriod, passKPIValueType, passCreatedDate, _
                              passCreatedUserID, passResponsibleUserID, passAnomalyOrigin1ID, passAnomalyOrigin2ID, passAnomalyOrigin3ID, passObservations, passClosedDate, _
                              passCancelled, passEvaluation, passEvaluatedDate, passIneffective, passAutoGenerated, -1, -1, String.Empty, String.Empty, -1, String.Empty, _
                              False, False, False, String.Empty, String.Empty, cnMasterConnection)
        End Function
        Public Shared Function AddAnomaly(ByVal passAnomaly As String, ByVal passAnomalyTypeID As Integer, ByVal passSiteID As Integer, ByVal passAreaID As Integer, _
                                          ByVal passSubject As String, ByVal passKPIID As Integer, ByVal passKPIPeriod As String, ByVal passKPIValueType As String, _
                                          ByVal passCreatedDate As String, ByVal passCreatedUserID As String, ByVal passResponsibleUserID As String, _
                                          ByVal passAnomalyOrigin1ID As Integer, ByVal passAnomalyOrigin2ID As Integer, ByVal passAnomalyOrigin3ID As Integer, _
                                          ByVal passObservations As String, ByVal passClosedDate As String, ByVal passCancelled As Boolean, _
                                          ByVal passEvaluation As String, ByVal passEvaluatedDate As String, ByVal passIneffective As Boolean, _
                                          ByVal passAutoGenerated As Boolean, ByVal passSGI As Integer, ByVal passChangeFEMEA As Integer, ByVal passFEMEADescription As String, _
                                          ByVal passFEMEAJustification As String, ByVal passRiskAnalysis As Integer, ByVal passRiskJustification As String, _
                                          ByVal passRiskResult1 As Boolean, ByVal passRiskResult2 As Boolean, ByVal passRiskResult3 As Boolean, _
                                          ByVal passRiskResultJustification As String, ByVal passSystemAgainstError As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passAnomaly, passAnomalyTypeID, passSiteID, passAreaID, passSubject, passKPIID, passKPIPeriod, _
                                                                                     passCreatedDate, passCreatedUserID, passResponsibleUserID, passAnomalyOrigin1ID, passAnomalyOrigin2ID, passAnomalyOrigin3ID, _
                                                                                     passObservations, passClosedDate, passCancelled, passEvaluation, passEvaluatedDate, passIneffective, passAutoGenerated, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsAnomalyMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmAdd.CommandType = CommandType.StoredProcedure

                cmAdd.Parameters.AddWithValue("@Anomaly", passAnomaly)
                cmAdd.Parameters.AddWithValue("@AnomalyTypeID", passAnomalyTypeID)
                cmAdd.Parameters.AddWithValue("@SiteID", passSiteID)
                cmAdd.Parameters.AddWithValue("@AreaID", passAreaID)
                If passSubject.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@Subject", passSubject)
                End If
                If passKPIID > 0 Then
                    cmAdd.Parameters.AddWithValue("@KPIID", passKPIID)
                    If passKPIPeriod.Trim.Length > 0 Then
                        cmAdd.Parameters.AddWithValue("@KPIPeriod", passKPIPeriod)
                    End If
                    If passKPIValueType.Trim.Length > 0 Then
                        cmAdd.Parameters.AddWithValue("@KPIValueType", passKPIValueType)
                    End If
                End If
                If passSGI >= 0 Then
                    cmAdd.Parameters.AddWithValue("@SGI", passSGI = 1)
                End If
                If passChangeFEMEA >= 0 Then
                    cmAdd.Parameters.AddWithValue("@ChangeFEMEA", passChangeFEMEA = 1)
                End If
                If Not String.IsNullOrEmpty(passFEMEADescription) Then
                    cmAdd.Parameters.AddWithValue("@FEMEADescription", passFEMEADescription.Trim)
                End If
                If Not String.IsNullOrEmpty(passFEMEAJustification) Then
                    cmAdd.Parameters.AddWithValue("@FEMEAJustification", passFEMEAJustification.Trim)
                End If
                If passRiskAnalysis >= 0 Then
                    cmAdd.Parameters.AddWithValue("@RiskAnalysis", passRiskAnalysis = 1)
                End If
                If Not String.IsNullOrEmpty(passRiskJustification) Then
                    cmAdd.Parameters.AddWithValue("@RiskJustification", passRiskJustification.Trim)
                End If
                cmAdd.Parameters.AddWithValue("@RiskResult1", passRiskResult1)
                cmAdd.Parameters.AddWithValue("@RiskResult2", passRiskResult2)
                cmAdd.Parameters.AddWithValue("@RiskResult3", passRiskResult3)
                If Not String.IsNullOrEmpty(passRiskResultJustification) Then
                    cmAdd.Parameters.AddWithValue("@RiskResultJustification", passRiskResultJustification.Trim)
                End If
                If Not String.IsNullOrEmpty(passSystemAgainstError) Then
                    cmAdd.Parameters.AddWithValue("@SystemAgainstError", passSystemAgainstError.Trim)
                End If
                cmAdd.Parameters.AddWithValue("@CreatedDateTime", passCreatedDate)
                cmAdd.Parameters.AddWithValue("@CreatedUserID", passCreatedUserID)
                cmAdd.Parameters.AddWithValue("@ResponsibleUserID", passResponsibleUserID)
                If passAnomalyOrigin1ID > 0 Then
                    cmAdd.Parameters.AddWithValue("@AnomalyOrigin1ID", passAnomalyOrigin1ID)
                End If
                If passAnomalyOrigin2ID > 0 Then
                    cmAdd.Parameters.AddWithValue("@AnomalyOrigin2ID", passAnomalyOrigin2ID)
                End If
                If passAnomalyOrigin3ID > 0 Then
                    cmAdd.Parameters.AddWithValue("@AnomalyOrigin3ID", passAnomalyOrigin3ID)
                End If
                If passObservations.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@Observations", passObservations.Trim)
                End If
                If passClosedDate.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@ClosedDateTime", passClosedDate)
                    cmAdd.Parameters.AddWithValue("@Cancelled", passCancelled)
                End If
                If passEvaluatedDate.Trim.Length > 0 Then
                    If passEvaluation.Trim.Length > 0 Then
                        cmAdd.Parameters.AddWithValue("@Evaluation", passEvaluation.Trim)
                    End If
                    cmAdd.Parameters.AddWithValue("@EvaluatedDateTime", passEvaluatedDate)
                    cmAdd.Parameters.AddWithValue("@Ineffective", passIneffective)
                End If
                cmAdd.Parameters.AddWithValue("@AutoGenerated", passAutoGenerated)

                Return cmAdd.ExecuteScalar
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Sub UpdateAnomaly(ByVal passAnomalyID As Integer, ByVal passAnomaly As String, ByVal passAnomalyTypeID As Integer, ByVal passSiteID As Integer, _
                                        ByVal passAreaID As Integer, ByVal passSubject As String, ByVal passKPIID As Integer, ByVal passResponsibleUserID As String, _
                                        ByVal passAnomalyOrigin1ID As Integer, ByVal passAnomalyOrigin2ID As Integer, ByVal passAnomalyOrigin3ID As Integer, _
                                        ByVal passObservations As String, ByVal passClosedDate As String, ByVal passCancelled As Boolean, _
                                        ByVal passEvaluation As String, ByVal passEvaluatedDate As String, ByVal passIneffective As Boolean, _
                                        ByVal passAutoGenerated As Boolean, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            UpdateAnomaly(passAnomaly, passAnomaly, passAnomalyTypeID, passSiteID, passAreaID, passSubject, passKPIID, passResponsibleUserID, passAnomalyOrigin1ID, passAnomalyOrigin2ID, passAnomalyOrigin3ID, _
                          passObservations, passClosedDate, passCancelled, passEvaluation, passEvaluatedDate, passIneffective, passAutoGenerated, -1, -1, String.Empty, String.Empty, -1, _
                          String.Empty, False, False, False, String.Empty, String.Empty, cnMasterConnection)
        End Sub
        Public Shared Sub UpdateAnomaly(ByVal passAnomalyID As Integer, ByVal passAnomaly As String, ByVal passAnomalyTypeID As Integer, ByVal passSiteID As Integer, _
                                        ByVal passAreaID As Integer, ByVal passSubject As String, ByVal passKPIID As Integer, ByVal passResponsibleUserID As String, _
                                        ByVal passAnomalyOrigin1ID As Integer, ByVal passAnomalyOrigin2ID As Integer, ByVal passAnomalyOrigin3ID As Integer, _
                                        ByVal passObservations As String, ByVal passClosedDate As String, ByVal passCancelled As Boolean, _
                                        ByVal passEvaluation As String, ByVal passEvaluatedDate As String, ByVal passIneffective As Boolean, _
                                        ByVal passAutoGenerated As Boolean, ByVal passSGI As Integer, ByVal passChangeFEMEA As Integer, ByVal passFEMEADescription As String, _
                                        ByVal passFEMEAJustification As String, ByVal passRiskAnalysis As Integer, ByVal passRiskJustification As String, _
                                        ByVal passRiskResult1 As Boolean, ByVal passRiskResult2 As Boolean, ByVal passRiskResult3 As Boolean, ByVal passRiskResultJustification As String, _
                                        ByVal passSystemAgainstError As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passAnomalyID, passAnomaly, passAnomalyTypeID, passSiteID, passAreaID, passSubject, passKPIID, _
                                                                                     passResponsibleUserID, passAnomalyOrigin1ID, passAnomalyOrigin2ID, passAnomalyOrigin3ID, passObservations, _
                                                                                     passClosedDate, passCancelled, passEvaluation, passEvaluatedDate, passIneffective, passAutoGenerated, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdAnomalyMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmUpdate.CommandType = CommandType.StoredProcedure

                cmUpdate.Parameters.AddWithValue("@AnomalyID", passAnomalyID)
                cmUpdate.Parameters.AddWithValue("@Anomaly", passAnomaly)
                cmUpdate.Parameters.AddWithValue("@AnomalyTypeID", passAnomalyTypeID)
                cmUpdate.Parameters.AddWithValue("@SiteID", passSiteID)
                cmUpdate.Parameters.AddWithValue("@AreaID", passAreaID)
                If passSubject.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@Subject", passSubject)
                End If
                If passKPIID > 0 Then
                    cmUpdate.Parameters.AddWithValue("@KPIID", passKPIID)
                End If
                If passSGI >= 0 Then
                    cmUpdate.Parameters.AddWithValue("@SGI", passSGI = 1)
                End If
                If passChangeFEMEA >= 0 Then
                    cmUpdate.Parameters.AddWithValue("@ChangeFEMEA", passChangeFEMEA = 1)
                End If
                If Not String.IsNullOrEmpty(passFEMEADescription) Then
                    cmUpdate.Parameters.AddWithValue("@FEMEADescription", passFEMEADescription.Trim)
                End If
                If Not String.IsNullOrEmpty(passFEMEAJustification) Then
                    cmUpdate.Parameters.AddWithValue("@FEMEAJustification", passFEMEAJustification.Trim)
                End If
                If passRiskAnalysis >= 0 Then
                    cmUpdate.Parameters.AddWithValue("@RiskAnalysis", passRiskAnalysis = 1)
                End If
                If Not String.IsNullOrEmpty(passRiskJustification) Then
                    cmUpdate.Parameters.AddWithValue("@RiskJustification", passRiskJustification.Trim)
                End If
                cmUpdate.Parameters.AddWithValue("@RiskResult1", passRiskResult1)
                cmUpdate.Parameters.AddWithValue("@RiskResult2", passRiskResult2)
                cmUpdate.Parameters.AddWithValue("@RiskResult3", passRiskResult3)
                If Not String.IsNullOrEmpty(passRiskResultJustification) Then
                    cmUpdate.Parameters.AddWithValue("@RiskResultJustification", passRiskResultJustification.Trim)
                End If
                If Not String.IsNullOrEmpty(passSystemAgainstError) Then
                    cmUpdate.Parameters.AddWithValue("@SystemAgainstError", passSystemAgainstError.Trim)
                End If
                cmUpdate.Parameters.AddWithValue("@ResponsibleUserID", passResponsibleUserID)
                If passAnomalyOrigin1ID > 0 Then
                    cmUpdate.Parameters.AddWithValue("@AnomalyOrigin1ID", passAnomalyOrigin1ID)
                End If
                If passAnomalyOrigin2ID > 0 Then
                    cmUpdate.Parameters.AddWithValue("@AnomalyOrigin2ID", passAnomalyOrigin2ID)
                End If
                If passAnomalyOrigin3ID > 0 Then
                    cmUpdate.Parameters.AddWithValue("@AnomalyOrigin3ID", passAnomalyOrigin3ID)
                End If
                If passObservations.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@Observations", passObservations.Trim)
                End If
                If passClosedDate.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@ClosedDateTime", passClosedDate)
                    cmUpdate.Parameters.AddWithValue("@Cancelled", passCancelled)
                End If
                If passEvaluatedDate.Trim.Length > 0 Then
                    If passEvaluation.Trim.Length > 0 Then
                        cmUpdate.Parameters.AddWithValue("@Evaluation", passEvaluation.Trim)
                    End If
                    cmUpdate.Parameters.AddWithValue("@EvaluatedDateTime", passEvaluatedDate)
                    cmUpdate.Parameters.AddWithValue("@Ineffective", passIneffective)
                End If
                cmUpdate.Parameters.AddWithValue("@AutoGenerated", passAutoGenerated)

                cmUpdate.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub UpdateAnomalyReOpen(ByVal passAnomalyID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passAnomalyID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdAnomalyMasterReOpen", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmUpdate.CommandType = CommandType.StoredProcedure

                cmUpdate.Parameters.AddWithValue("@AnomalyID", passAnomalyID)

                cmUpdate.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub DeleteAnomaly(ByVal passAnomalyID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passAnomalyID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelAnomalyMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmDelete.CommandType = CommandType.StoredProcedure
                cmDelete.Parameters.AddWithValue("@AnomalyID", passAnomalyID)
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

