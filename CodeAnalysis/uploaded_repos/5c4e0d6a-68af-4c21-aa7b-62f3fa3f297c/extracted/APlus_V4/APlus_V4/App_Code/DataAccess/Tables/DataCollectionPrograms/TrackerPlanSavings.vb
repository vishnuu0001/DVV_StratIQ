#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class TrackerPlanSavings

#Region " Select Methods"
        Public Shared Function SelectTrackerPlanSavingsByID(ByVal passTrackerPlanSavingsID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTrackerPlanSavingsID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTrackerPlanSavingsByID", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TrackerPlanSavingsID", passTrackerPlanSavingsID)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectTrackerPlanSavingsByYear(ByVal passTrackerPlanID As Integer, ByVal passYear As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTrackerPlanID, passYear, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTrackerPlanSavingsByYear", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TrackerPlanID", passTrackerPlanID)
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
        Public Shared Function SelectTrackerPlanSavingsOverview(ByVal passYear As Integer, ByVal passSiteID As Integer, ByVal passPillarAbbrev As String, _
                                                                ByVal passBusinessAreaID As Integer, ByVal passBusinessUnitID As Integer, ByVal passShowProjected As Boolean, _
                                                                Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passYear, passSiteID, passPillarAbbrev, passBusinessAreaID, passBusinessUnitID, passShowProjected, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelMasterPlanSavingsOverview", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@Year", passYear)
                If passSiteID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@SiteID", passSiteID)
                End If
                If Not String.IsNullOrEmpty(passPillarAbbrev) Then
                    da.SelectCommand.Parameters.AddWithValue("@PillarAbbrev", passPillarAbbrev)
                End If
                If passBusinessAreaID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@BusinessAreaID", passBusinessAreaID)
                End If
                If passBusinessUnitID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@BusinessUnitID", passBusinessUnitID)
                End If
                da.SelectCommand.Parameters.AddWithValue("@ShowProjected", passShowProjected)

                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectTrackerPlanSavingsOverview2(ByVal passYear As Integer, ByVal passSiteID As Integer, ByVal passPillarAbbrev As String, _
                                                                ByVal passBusinessAreaID As Integer, ByVal passBusinessUnitID As Integer, ByVal passShowProjected As Boolean, _
                                                                Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passYear, passSiteID, passPillarAbbrev, passBusinessAreaID, passBusinessUnitID, passShowProjected, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelMasterPlanSavingsOverview2", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@Year", passYear)
                If passSiteID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@SiteID", passSiteID)
                End If
                If Not String.IsNullOrEmpty(passPillarAbbrev) Then
                    da.SelectCommand.Parameters.AddWithValue("@PillarAbbrev", passPillarAbbrev)
                End If
                If passBusinessAreaID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@BusinessAreaID", passBusinessAreaID)
                End If
                If passBusinessUnitID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@BusinessUnitID", passBusinessUnitID)
                End If
                da.SelectCommand.Parameters.AddWithValue("@ShowProjected", passShowProjected)

                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectTrackerPlanSavingsOverview3(ByVal passYear As Integer, ByVal passSiteID As Integer, ByVal passPillarAbbrev As String, _
                                                                ByVal passBusinessAreaID As Integer, ByVal passBusinessUnitID As Integer, ByVal passShowProjected As Boolean, _
                                                                Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passYear, passSiteID, passPillarAbbrev, passBusinessAreaID, passBusinessUnitID, passShowProjected, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelMasterPlanSavingsOverview3", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@Year", passYear)
                If passSiteID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@SiteID", passSiteID)
                End If
                If Not String.IsNullOrEmpty(passPillarAbbrev) Then
                    da.SelectCommand.Parameters.AddWithValue("@PillarAbbrev", passPillarAbbrev)
                End If
                If passBusinessAreaID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@BusinessAreaID", passBusinessAreaID)
                End If
                If passBusinessUnitID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@BusinessUnitID", passBusinessUnitID)
                End If
                da.SelectCommand.Parameters.AddWithValue("@ShowProjected", passShowProjected)

                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectTrackerPlanSavingsOverviewEUR(ByVal passYear As Integer, ByVal passSiteID As Integer, ByVal passBusinessAreaID As Integer, _
                                                                   ByVal passShowProjected As Boolean, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passYear, passSiteID, passBusinessAreaID, passShowProjected, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelMasterPlanSavingsOverviewEUR", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@Year", passYear)
                If passSiteID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@SiteID", passSiteID)
                End If
                If passBusinessAreaID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@BusinessAreaID", passBusinessAreaID)
                End If
                da.SelectCommand.Parameters.AddWithValue("@ShowProjected", passShowProjected)

                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectTrackerPlanSavingsOverviewEUR2(ByVal passYear As Integer, ByVal passSiteID As Integer, ByVal passBusinessAreaID As Integer, _
                                                                   ByVal passShowProjected As Boolean, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passYear, passSiteID, passBusinessAreaID, passShowProjected, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelMasterPlanSavingsOverviewEUR2", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@Year", passYear)
                If passSiteID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@SiteID", passSiteID)
                End If
                If passBusinessAreaID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@BusinessAreaID", passBusinessAreaID)
                End If
                da.SelectCommand.Parameters.AddWithValue("@ShowProjected", passShowProjected)

                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectTrackerPlanSavingsOverviewEUR3(ByVal passYear As Integer, ByVal passSiteID As Integer, ByVal passBusinessAreaID As Integer, _
                                                                   ByVal passShowProjected As Boolean, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passYear, passSiteID, passBusinessAreaID, passShowProjected, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelMasterPlanSavingsOverviewEUR3", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@Year", passYear)
                If passSiteID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@SiteID", passSiteID)
                End If
                If passBusinessAreaID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@BusinessAreaID", passBusinessAreaID)
                End If
                da.SelectCommand.Parameters.AddWithValue("@ShowProjected", passShowProjected)

                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectTrackerPlanSavingsCollection(ByVal passSiteID As Integer, ByVal passYear As Integer, ByVal passShowProjected As Boolean, _
                                                                  Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSiteID, passYear, passShowProjected, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelMasterPlanSavingsCollection", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@SiteID", passSiteID)
                da.SelectCommand.Parameters.AddWithValue("@Year", passYear)
                da.SelectCommand.Parameters.AddWithValue("@ShowProjected", passShowProjected)

                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectTrackerPlanBASavingsCollection(ByVal passSiteID As Integer, ByVal passYear As Integer, ByVal passShowProjected As Boolean, _
                                                                    Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSiteID, passYear, passShowProjected, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelMasterPlanBASavings", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@SiteID", passSiteID)
                da.SelectCommand.Parameters.AddWithValue("@Year", passYear)
                da.SelectCommand.Parameters.AddWithValue("@ShowProjected", passShowProjected)

                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectTrackerPlanSavingsTotalsBySite(ByVal passSiteID As Integer, ByVal passYear As Integer, ByVal passTrackerPlanID As Integer, _
                                                                    Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSiteID, passYear, passTrackerPlanID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelMasterPlanSavingsCollectionBySite", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@SiteID", passSiteID)
                da.SelectCommand.Parameters.AddWithValue("@Year", passYear)
                If passTrackerPlanID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@TrackerPlanID", passTrackerPlanID)
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
        Public Shared Function SelectTrackerPlanSavingsTotalsYTDBySite(ByVal passSiteID As Integer, ByVal passYear As Integer, ByVal passTrackerPlanID As Integer, _
                                                                       ByVal passShowProjected As Boolean, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSiteID, passYear, passTrackerPlanID, passShowProjected, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelMasterPlanSavingsCollectionYTDBySite", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@SiteID", passSiteID)
                da.SelectCommand.Parameters.AddWithValue("@Year", passYear)
                If passTrackerPlanID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@TrackerPlanID", passTrackerPlanID)
                End If
                da.SelectCommand.Parameters.AddWithValue("@ShowProjected", passShowProjected)

                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectTrackerPlanTeams(ByVal passUserID As String, ByVal passWorkingSiteID As Integer, ByVal passTrackerPlanID As Integer, _
                                                      Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, passTrackerPlanID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelMasterPlanTeams", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@UserID", passUserID)
                da.SelectCommand.Parameters.AddWithValue("@SiteID", passWorkingSiteID)
                da.SelectCommand.Parameters.AddWithValue("@TrackerPlanID", passTrackerPlanID)

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

#Region " Action Methods"
        Public Shared Function InsertPlanSavings(ByVal passTrackerPlanID As Integer, ByVal passTrackerPeriod As String, ByVal passTrackerPlanSavings As String, _
                                                 ByVal passTrackerStretchSavings As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTrackerPlanID, passTrackerPeriod, passTrackerPlanSavings, passTrackerStretchSavings, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsTrackerPlanSavings", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmAdd.CommandType = CommandType.StoredProcedure

                cmAdd.Parameters.AddWithValue("@TrackerPlanID", passTrackerPlanID)
                cmAdd.Parameters.AddWithValue("@TrackerPeriod", passTrackerPeriod)
                cmAdd.Parameters.AddWithValue("@TrackerPlanSavings", passTrackerPlanSavings)
                cmAdd.Parameters.AddWithValue("@TrackerStretchSavings", passTrackerStretchSavings)

                Return cmAdd.ExecuteScalar
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Sub UpdatePlanSavings(ByVal passTrackerPlanSavingsID As Integer, ByVal passTrackerPeriod As String, ByVal passTrackerPlanSavings As String, _
                                            ByVal passTrackerStretchSavings As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTrackerPlanSavingsID, passTrackerPeriod, passTrackerPlanSavings, passTrackerStretchSavings, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdTrackerPlanSavings", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmUpdate.CommandType = CommandType.StoredProcedure

                cmUpdate.Parameters.AddWithValue("@TrackerPlanSavingsID", passTrackerPlanSavingsID)
                cmUpdate.Parameters.AddWithValue("@TrackerPeriod", passTrackerPeriod)
                cmUpdate.Parameters.AddWithValue("@TrackerPlanSavings", passTrackerPlanSavings)
                cmUpdate.Parameters.AddWithValue("@TrackerStretchSavings", passTrackerStretchSavings)

                cmUpdate.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub UpdatePlanByPeriod(ByVal passTrackerPlanID As Integer, ByVal passTrackerPeriod As String, ByVal passTrackerPlanSavings As String, _
                                             ByVal passTrackerStretchSavings As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTrackerPlanID, passTrackerPeriod, passTrackerPlanSavings, passTrackerStretchSavings, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdTrackerPlanByPeriod", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmUpdate.CommandType = CommandType.StoredProcedure

                cmUpdate.Parameters.AddWithValue("@TrackerPlanID", passTrackerPlanID)
                cmUpdate.Parameters.AddWithValue("@TrackerPeriod", passTrackerPeriod)
                If passTrackerPlanSavings.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@TrackerPlanSavings", passTrackerPlanSavings)
                End If
                If passTrackerStretchSavings.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@TrackerStretchSavings", passTrackerStretchSavings)
                End If

                cmUpdate.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub UpdatePlanSavingsByPeriod(ByVal passTrackerPlanID As Integer, ByVal passTrackerPeriod As String, ByVal passTrackerPlanSavings As String, _
                                            Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTrackerPlanID, passTrackerPeriod, passTrackerPlanSavings, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdTrackerPlanSavingsByPeriod", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmUpdate.CommandType = CommandType.StoredProcedure

                cmUpdate.Parameters.AddWithValue("@TrackerPlanID", passTrackerPlanID)
                cmUpdate.Parameters.AddWithValue("@TrackerPeriod", passTrackerPeriod)
                If passTrackerPlanSavings.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@TrackerPlanSavings", passTrackerPlanSavings)
                End If

                cmUpdate.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub UpdateStretchSavingsByPeriod(ByVal passTrackerPlanID As Integer, ByVal passTrackerPeriod As String, ByVal passTrackerStretchSavings As String, _
                                                       Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTrackerPlanID, passTrackerPeriod, passTrackerStretchSavings, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdTrackerStretchSavingsByPeriod", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmUpdate.CommandType = CommandType.StoredProcedure

                cmUpdate.Parameters.AddWithValue("@TrackerPlanID", passTrackerPlanID)
                cmUpdate.Parameters.AddWithValue("@TrackerPeriod", passTrackerPeriod)
                If passTrackerStretchSavings.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@TrackerStretchSavings", passTrackerStretchSavings)
                End If

                cmUpdate.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub DeletePlanSavings(ByVal passTrackerPlanSavingsID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTrackerPlanSavingsID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelTrackerPlanSavings", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmDelete.CommandType = CommandType.StoredProcedure
                cmDelete.Parameters.AddWithValue("@TrackerPlanSavingsID", passTrackerPlanSavingsID)
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

