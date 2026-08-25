#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class KPIValues

#Region " Select Methods"
        Public Shared Function SelectKPICollection(ByVal passYear As Integer, ByVal passSiteID As Integer, ByVal passPillarAbbrev As String, _
                                                   ByVal passBusinessAreaID As Integer, ByVal passBusinessUnitID As Integer, _
                                                   ByVal passTeamCategoryID As Integer, ByVal passReportingLevelID As Integer, _
                                                   ByVal passResponsibleUserID As String, ByVal passUserID As String, ByVal passShowSupportingKPIs As Boolean, _
                                                   ByVal passAreaGroupID As Integer, ByVal passAllAreas As Boolean, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
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
            Dim da As New SqlDataAdapter(New SqlCommand("spSelKPICollection", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure

                da.SelectCommand.Parameters.AddWithValue("@Year", passYear)
                If passSiteID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@SiteID", passSiteID)
                End If
                If passPillarAbbrev.Trim.Length > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@PillarAbbrev", passPillarAbbrev)
                End If
                If passBusinessAreaID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@BusinessAreaID", passBusinessAreaID)
                End If
                If passBusinessUnitID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@BusinessUnitID", passBusinessUnitID)
                End If
                If passTeamCategoryID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@TeamCategoryID", passTeamCategoryID)
                End If
                If passReportingLevelID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@ReportingLevelID", passReportingLevelID)
                End If
                If passResponsibleUserID.Trim.Length > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@ResponsibleUserID", passResponsibleUserID)
                End If
                da.SelectCommand.Parameters.AddWithValue("@UserID", passUserID)
                da.SelectCommand.Parameters.AddWithValue("@ShowSupportingKPI", passShowSupportingKPIs)
                If passAreaGroupID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@AreaGroupID", passAreaGroupID)
                    da.SelectCommand.Parameters.AddWithValue("@AllAreas", passAllAreas)
                End If
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectKPICollectionNoTarget(ByVal passYear As Integer, ByVal passSiteID As Integer, ByVal passPillarAbbrev As String, _
                                                   ByVal passBusinessAreaID As Integer, ByVal passBusinessUnitID As Integer, _
                                                   ByVal passTeamCategoryID As Integer, ByVal passReportingLevelID As Integer, _
                                                   ByVal passResponsibleUserID As String, ByVal passUserID As String, ByVal passShowSupportingKPIs As Boolean, _
                                                   ByVal passAreaGroupID As Integer, ByVal passAllAreas As Boolean, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
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
            Dim da As New SqlDataAdapter(New SqlCommand("spSelKPICollectionNoTarget", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure

                da.SelectCommand.Parameters.AddWithValue("@Year", passYear)
                If passSiteID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@SiteID", passSiteID)
                End If
                If passPillarAbbrev.Trim.Length > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@PillarAbbrev", passPillarAbbrev)
                End If
                If passBusinessAreaID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@BusinessAreaID", passBusinessAreaID)
                End If
                If passBusinessUnitID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@BusinessUnitID", passBusinessUnitID)
                End If
                If passTeamCategoryID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@TeamCategoryID", passTeamCategoryID)
                End If
                If passReportingLevelID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@ReportingLevelID", passReportingLevelID)
                End If
                If passResponsibleUserID.Trim.Length > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@ResponsibleUserID", passResponsibleUserID)
                End If
                da.SelectCommand.Parameters.AddWithValue("@UserID", passUserID)
                da.SelectCommand.Parameters.AddWithValue("@ShowSupportingKPI", passShowSupportingKPIs)
                If passAreaGroupID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@AreaGroupID", passAreaGroupID)
                    da.SelectCommand.Parameters.AddWithValue("@AllAreas", passAllAreas)
                End If

                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectKPIReport1Collection(ByVal passYear As Integer, ByVal passKPIReportCategory As String, _
                                                          ByVal passKPIReportGroupID As Integer, ByVal passBusinessAreaID As Integer, _
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
            Dim da As New SqlDataAdapter(New SqlCommand("spSelKPIReport1Collection", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure

                da.SelectCommand.Parameters.AddWithValue("@Year", passYear)
                If Not String.IsNullOrEmpty(passKPIReportCategory.Trim) Then
                    da.SelectCommand.Parameters.AddWithValue("@KPIReportCategory", passKPIReportCategory)
                End If
                If passKPIReportGroupID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@KPIReportGroupID", passKPIReportGroupID)
                End If
                If passBusinessAreaID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@BusinessAreaID", passBusinessAreaID)
                End If

                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectKPIReport2Collection(ByVal passYear As Integer, ByVal passKPIReportGroupID As Integer, ByVal passBusinessAreaID As Integer, _
                                                          ByVal passSiteID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
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
            Dim da As New SqlDataAdapter(New SqlCommand("spSelKPIReport2Collection", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure

                da.SelectCommand.Parameters.AddWithValue("@Year", passYear)
                If passKPIReportGroupID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@KPIReportGroupID", passKPIReportGroupID)
                End If
                If passBusinessAreaID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@BusinessAreaID", passBusinessAreaID)
                End If
                If passSiteID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@SiteID", passSiteID)
                End If

                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectKPIReport3Collection(ByVal passYear As Integer, ByVal passKPIReportCategory As String, ByVal passKPIReportGroupID As Integer, _
                                                          ByVal passBusinessAreaID As Integer, ByVal passSiteID As Integer, _
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
            Dim da As New SqlDataAdapter(New SqlCommand("spSelKPIReport3Collection", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure

                da.SelectCommand.Parameters.AddWithValue("@Year", passYear)
                If Not String.IsNullOrEmpty(passKPIReportCategory.Trim) Then
                    da.SelectCommand.Parameters.AddWithValue("@KPIReportCategory", passKPIReportCategory)
                End If
                If passKPIReportGroupID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@KPIReportGroupID", passKPIReportGroupID)
                End If
                If passBusinessAreaID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@BusinessAreaID", passBusinessAreaID)
                End If
                If passSiteID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@SiteID", passSiteID)
                End If

                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectKPIReport4Collection(ByVal passYear As Integer, ByVal passKPIReportGroupID As Integer, ByVal passBusinessAreaID As Integer, _
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
            Dim da As New SqlDataAdapter(New SqlCommand("spSelKPIReport4Collection", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure

                da.SelectCommand.Parameters.AddWithValue("@Year", passYear)
                If passKPIReportGroupID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@KPIReportGroupID", passKPIReportGroupID)
                End If
                If passBusinessAreaID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@BusinessAreaID", passBusinessAreaID)
                End If

                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectKPIReport5Collection(ByVal passYear As Integer, ByVal passKPIReportGroupID As Integer, ByVal passBusinessAreaID As Integer, _
                                                          ByVal passSiteID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
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
            Dim da As New SqlDataAdapter(New SqlCommand("spSelKPIReport5Collection", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure

                da.SelectCommand.Parameters.AddWithValue("@Year", passYear)
                If passKPIReportGroupID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@KPIReportGroupID", passKPIReportGroupID)
                End If
                If passBusinessAreaID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@BusinessAreaID", passBusinessAreaID)
                End If
                If passSiteID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@SiteID", passSiteID)
                End If

                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectKPIReport5CollectionNoTargets(ByVal passYear As Integer, ByVal passKPIReportGroupID As Integer, ByVal passBusinessAreaID As Integer, _
                                                          ByVal passSiteID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
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
            Dim da As New SqlDataAdapter(New SqlCommand("spSelKPIReport5CollectionNoTargets", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure

                da.SelectCommand.Parameters.AddWithValue("@Year", passYear)
                If passKPIReportGroupID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@KPIReportGroupID", passKPIReportGroupID)
                End If
                If passBusinessAreaID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@BusinessAreaID", passBusinessAreaID)
                End If
                If passSiteID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@SiteID", passSiteID)
                End If

                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectKPIReport8Collection(ByVal passYear As Integer, ByVal passKPIReportGroupID As Integer, ByVal passBusinessAreaID As Integer, _
                                                          ByVal passSiteID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
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
            Dim da As New SqlDataAdapter(New SqlCommand("spSelKPIReport8Collection", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure

                da.SelectCommand.Parameters.AddWithValue("@Year", passYear)
                If passKPIReportGroupID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@KPIReportGroupID", passKPIReportGroupID)
                End If
                If passBusinessAreaID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@BusinessAreaID", passBusinessAreaID)
                End If
                If passSiteID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@SiteID", passSiteID)
                End If

                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectKPIReport9Collection(ByVal passYear As Integer, ByVal passKPIReportGroupID As Integer, ByVal passBusinessAreaID As Integer, _
                                                                  ByVal passSiteID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
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
            Dim da As New SqlDataAdapter(New SqlCommand("spSelKPIReport9Collection", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure

                da.SelectCommand.Parameters.AddWithValue("@Year", passYear)
                If passKPIReportGroupID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@KPIReportGroupID", passKPIReportGroupID)
                End If
                If passBusinessAreaID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@BusinessAreaID", passBusinessAreaID)
                End If
                If passSiteID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@SiteID", passSiteID)
                End If

                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectKPIValuesByIDYear(ByVal passKPIID As Integer, ByVal passYear As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passKPIID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelKPIValues", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@KPIID", passKPIID)
                da.SelectCommand.Parameters.AddWithValue("@Year", passYear)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectKPIDailyValuesByDate(ByVal passKPIID As Integer, ByVal passYear As Integer, ByVal passMonth As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passKPIID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelKPIDailyValues", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@KPIID", passKPIID)
                da.SelectCommand.Parameters.AddWithValue("@Year", passYear)
                da.SelectCommand.Parameters.AddWithValue("@Month", passMonth)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectKPIValuesByDate(ByVal passKPIID As Integer, ByVal passKPIPeriod As String, ByVal passValueType As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passKPIID, passKPIPeriod, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelKPIValuesByDate", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@KPIID", passKPIID)
                da.SelectCommand.Parameters.AddWithValue("@KPIPeriod", passKPIPeriod)
                da.SelectCommand.Parameters.AddWithValue("@ValueType", passValueType)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectKPIValueComments(ByVal passKPIID As Integer, ByVal passKPIPeriod As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passKPIID, passKPIPeriod, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim dc As New SqlCommand("spSelKPIValueComments", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim dt As New DataTable
            Dim strReturn As String = String.Empty

            Try
                dc.CommandType = CommandType.StoredProcedure
                dc.Parameters.AddWithValue("@KPIID", passKPIID)
                dc.Parameters.AddWithValue("@KPIPeriod", passKPIPeriod)

                strReturn =  dc.ExecuteScalar()
            Catch Exc As Exception
                Throw
            Finally
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try

            Return strReturn
        End Function
#End Region

#Region " Table Methods"
        Public Shared Sub UpdateKPIValues(ByVal passKPIID As Integer, ByVal passKPIPeriod As String, ByVal passValueType As String, _
                                          ByVal passKPIValue As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passKPIID, passKPIPeriod, passValueType, passKPIValue, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdKPIValues", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmUpdate.CommandType = CommandType.StoredProcedure
                cmUpdate.Parameters.AddWithValue("@KPIID", passKPIID)
                cmUpdate.Parameters.AddWithValue("@KPIPeriod", passKPIPeriod)
                cmUpdate.Parameters.AddWithValue("@ValueType", passValueType)
                If passKPIValue.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@KPIValue", passKPIValue)
                End If

                cmUpdate.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub UpdateKPITargets(ByVal passKPIID As Integer, ByVal passKPIPeriod As String, ByVal passValueType As String, _
                                          ByVal passKPITarget As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passKPIID, passKPIPeriod, passValueType, passKPITarget, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdKPITarget", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmUpdate.CommandType = CommandType.StoredProcedure
                cmUpdate.Parameters.AddWithValue("@KPIID", passKPIID)
                cmUpdate.Parameters.AddWithValue("@KPIPeriod", passKPIPeriod)
                cmUpdate.Parameters.AddWithValue("@ValueType", passValueType)
                If passKPITarget.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@KPITarget", passKPITarget)
                End If

                cmUpdate.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub UpdateKPITargetYTD(ByVal passKPIID As Integer, ByVal passKPIPeriod As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passKPIID, passKPIPeriod, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdKPITargetYTD", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmUpdate.CommandType = CommandType.StoredProcedure
                cmUpdate.Parameters.AddWithValue("@KPIID", passKPIID)
                cmUpdate.Parameters.AddWithValue("@KPIPeriod", passKPIPeriod)

                cmUpdate.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub UpdateKPIDailyValue(ByVal passKPIID As Integer, ByVal passKPIPeriod As String, _
                                          ByVal passDailyValue As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passKPIID, passKPIPeriod, passDailyValue, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdKPIDailyValue", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmUpdate.CommandType = CommandType.StoredProcedure
                cmUpdate.Parameters.AddWithValue("@KPIID", passKPIID)
                cmUpdate.Parameters.AddWithValue("@KPIPeriod", passKPIPeriod)
                If passDailyValue.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@KPIDailyValue", passDailyValue)
                End If

                cmUpdate.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub UpdateKPIDailyValueMTD(ByVal passKPIID As Integer, ByVal passKPIPeriod As String, _
                                          ByVal passMTDValue As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passKPIID, passKPIPeriod, passMTDValue, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdKPIDailyValueMTD", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmUpdate.CommandType = CommandType.StoredProcedure
                cmUpdate.Parameters.AddWithValue("@KPIID", passKPIID)
                cmUpdate.Parameters.AddWithValue("@KPIPeriod", passKPIPeriod)
                If passMTDValue.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@KPIMTDValue", passMTDValue)
                End If

                cmUpdate.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub UpdateKPIValueComments(ByVal passKPIID As Integer, ByVal passKPIPeriod As String, _
                                          ByVal passComments As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passKPIID, passKPIPeriod, passComments, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdKPIValueComments", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmUpdate.CommandType = CommandType.StoredProcedure
                cmUpdate.Parameters.AddWithValue("@KPIID", passKPIID)
                cmUpdate.Parameters.AddWithValue("@KPIPeriod", passKPIPeriod)
                If Not String.IsNullOrEmpty(passComments) Then
                    cmUpdate.Parameters.AddWithValue("@Comments", passComments)
                End If

                cmUpdate.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub DeleteKPIValueComments(ByVal passKPIID As Integer, ByVal passKPIPeriod As String, _
                                          Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passKPIID, passKPIPeriod, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spDelKPIValueComments", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmUpdate.CommandType = CommandType.StoredProcedure
                cmUpdate.Parameters.AddWithValue("@KPIID", passKPIID)
                cmUpdate.Parameters.AddWithValue("@KPIPeriod", passKPIPeriod)

                cmUpdate.ExecuteNonQuery()
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

