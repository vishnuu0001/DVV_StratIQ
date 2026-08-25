#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class Trackers

#Region " Select Methods"
        Public Shared Function SelectTracker(ByVal passTrackerID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTrackerID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTracker", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TrackerID", passTrackerID)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectMyTrackers(ByVal passUserID As String, ByVal passSiteID As Integer, ByVal passPillarAbbrev As String, _
                                                ByVal passBusinessUnitID As Integer, ByVal passBusinessArea As Integer, _
                                                ByVal passSavingsCategoryID As Integer, ByVal passSavingsTypeID As Integer, _
                                                Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, passSiteID, passPillarAbbrev, passBusinessUnitID, passBusinessArea, passSavingsCategoryID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelMyTrackers", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure

                da.SelectCommand.Parameters.AddWithValue("@UserID", passUserID)
                da.SelectCommand.Parameters.AddWithValue("@SiteID", passSiteID)
                If passPillarAbbrev.Trim.Length > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@PillarAbbrev", passPillarAbbrev)
                End If
                da.SelectCommand.Parameters.AddWithValue("@BusinessUnitID", passBusinessUnitID)
                da.SelectCommand.Parameters.AddWithValue("@BusinessAreaID", passBusinessArea)
                da.SelectCommand.Parameters.AddWithValue("@SavingsCategoryID", passSavingsCategoryID)
                da.SelectCommand.Parameters.AddWithValue("@SavingsTypeID", passSavingsTypeID)

                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectMyTrackersPlan(ByVal passUserID As String, ByVal passSiteID As Integer, ByVal passPillarAbbrev As String, _
                                                ByVal passBusinessUnitID As Integer, ByVal passBusinessArea As Integer, _
                                                ByVal passSavingsCategoryID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, passSiteID, passPillarAbbrev, passBusinessUnitID, passBusinessArea, passSavingsCategoryID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelMyTrackersPlan", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure

                da.SelectCommand.Parameters.AddWithValue("@UserID", passUserID)
                da.SelectCommand.Parameters.AddWithValue("@SiteID", passSiteID)
                If passPillarAbbrev.Trim.Length > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@PillarAbbrev", passPillarAbbrev)
                End If
                da.SelectCommand.Parameters.AddWithValue("@BusinessUnitID", passBusinessUnitID)
                da.SelectCommand.Parameters.AddWithValue("@BusinessAreaID", passBusinessArea)
                da.SelectCommand.Parameters.AddWithValue("@SavingsCategoryID", passSavingsCategoryID)

                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Sub GetTrackerList(ByRef ddlList As System.Web.UI.WebControls.DropDownList, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelTrackersList", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    If (New System.Globalization.CultureInfo(SessionManager.CulturePref).TwoLetterISOLanguageName.ToUpper = "EN") Then
                        ddlList.Items.Add(New ListItem(drList.Item("TrackerOther").ToString.Trim, drList.Item("TrackerID").ToString.Trim))
                    Else
                        ddlList.Items.Add(New ListItem(drList.Item("Tracker").ToString.Trim, drList.Item("TrackerID").ToString.Trim))
                    End If
                End While
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub GetMyTrackerList(ByRef ddlList As System.Web.UI.WebControls.DropDownList, ByVal passUserID As String, _
                                           ByVal passSiteID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelMyTrackersList", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@UserID", passUserID)
                If passSiteID > 0 Then
                    cmSelect.Parameters.AddWithValue("@SiteID", passSiteID)
                End If
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    Dim myListIteam As ListItem = New ListItem
                    myListIteam.Text = drList.GetString(1)
                    myListIteam.Value = drList.GetInt32(0)

                    ddlList.Items.Add(myListIteam)
                End While
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Function SelectTrackerEditMode(ByVal passTrackerID As Integer, ByVal passUserID As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTrackerID, passUserID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTrackerEditMode", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TrackerID", passTrackerID)
                da.SelectCommand.Parameters.AddWithValue("@UserID", passUserID)
                da.Fill(dt)

                If dt IsNot Nothing AndAlso dt.Rows.Count = 1 Then
                    Return Convert.ToBoolean(dt.Rows(0)("AllowEdit"))
                Else
                    Return False
                End If
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectTeamTrackers(ByVal passTeamID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTrackersByTeam", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TeamID", passTeamID)
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

#Region " Table Methods"
        Public Shared Function AddTracker(ByVal passTracker As String, ByVal passTrackerOther As String, ByVal passTeamID As Integer, _
                                          ByVal passSavingsCategoryID As Integer, ByVal passTrackerUOM As String, ByVal passHistoric As String, _
                                          ByVal passTarget As String, ByVal passStartPeriod As String, ByVal passDescription As String, ByVal passInterface As Boolean, _
                                          ByVal passInterfaceFormula As String, ByVal passDataElements As String, ByVal passScheduleCode As String, _
                                          ByVal passScheduleTime As String, ByVal passNextExecute As String, ByVal passOnDemandExecute As String, _
                                          ByVal passActive As Boolean, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTracker, passTrackerOther, passTeamID, passSavingsCategoryID, passTrackerUOM, passHistoric, _
                                                                                     passTarget, passStartPeriod, passDescription, passInterface, passInterfaceFormula, _
                                                                                     passDataElements, passScheduleCode, passScheduleTime, passNextExecute, passOnDemandExecute, passActive, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsTracker", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmAdd.CommandType = CommandType.StoredProcedure
                cmAdd.Parameters.AddWithValue("@Tracker", passTracker)
                cmAdd.Parameters.AddWithValue("@TrackerOther", passTrackerOther)
                cmAdd.Parameters.AddWithValue("@TeamID", passTeamID)
                cmAdd.Parameters.AddWithValue("@SavingsCategoryID", passSavingsCategoryID)
                cmAdd.Parameters.AddWithValue("@TrackerValueUOM", passTrackerUOM)
                cmAdd.Parameters.AddWithValue("@Historic", passHistoric)
                cmAdd.Parameters.AddWithValue("@Target", passTarget)
                cmAdd.Parameters.AddWithValue("@StartPeriod", passStartPeriod)
                If passDescription.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@Description", passDescription)
                End If
                cmAdd.Parameters.AddWithValue("@Interface", passInterface)
                If passInterfaceFormula.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@InterfaceFormula", passInterfaceFormula.Trim)
                End If
                If passDataElements.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@DataElements", passDataElements.Trim)
                End If
                If passScheduleCode.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@ScheduleCode", passScheduleCode)
                End If
                If passScheduleTime.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@ScheduleTime", passScheduleTime)
                End If
                If passNextExecute.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@NextExecution", passNextExecute)
                End If
                If passOnDemandExecute.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@OnDemandExecute", passOnDemandExecute)
                End If
                cmAdd.Parameters.AddWithValue("@Active", passActive)

                Return cmAdd.ExecuteScalar
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Sub UpdateTracker(ByVal passTrackerID As Integer, ByVal passTracker As String, ByVal passTrackerOther As String, ByVal passTeamID As Integer, _
                                        ByVal passSavingsCategoryID As Integer, ByVal passTrackerUOM As String, ByVal passHistoric As String, _
                                        ByVal passTarget As String, ByVal passStartPeriod As String, ByVal passDescription As String, _
                                        ByVal passInterface As Boolean, ByVal passInterfaceFormula As String, ByVal passDataElements As String, _
                                        ByVal passScheduleCode As String, ByVal passScheduleTime As String, ByVal passNextExecute As String, _
                                        ByVal passOnDemandExecute As String, ByVal passActive As Boolean, _
                                        Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTrackerID, passTracker, passTrackerOther, passTeamID, _
                                                                                     passSavingsCategoryID, passTrackerUOM, passHistoric, passTarget, passStartPeriod, _
                                                                                     passDescription, passInterface, passInterfaceFormula, passDataElements, _
                                                                                     passScheduleCode, passScheduleTime, passNextExecute, passOnDemandExecute, passActive, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdTracker", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmUpdate.CommandType = CommandType.StoredProcedure
                cmUpdate.Parameters.AddWithValue("@TrackerID", passTrackerID)
                cmUpdate.Parameters.AddWithValue("@Tracker", passTracker)
                cmUpdate.Parameters.AddWithValue("@TrackerOther", passTrackerOther)
                cmUpdate.Parameters.AddWithValue("@TeamID", passTeamID)
                cmUpdate.Parameters.AddWithValue("@SavingsCategoryID", passSavingsCategoryID)
                cmUpdate.Parameters.AddWithValue("@TrackerValueUOM", passTrackerUOM)
                cmUpdate.Parameters.AddWithValue("@Historic", passHistoric)
                cmUpdate.Parameters.AddWithValue("@Target", passTarget)
                cmUpdate.Parameters.AddWithValue("@StartPeriod", passStartPeriod)
                cmUpdate.Parameters.AddWithValue("@Description", passDescription)
                cmUpdate.Parameters.AddWithValue("@Interface", passInterface)
                If passInterfaceFormula.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@InterfaceFormula", passInterfaceFormula.Trim)
                End If
                If passDataElements.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@DataElements", passDataElements.Trim)
                End If
                If passScheduleCode.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@ScheduleCode", passScheduleCode)
                End If
                If passScheduleTime.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@ScheduleTime", passScheduleTime)
                End If
                If passNextExecute.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@NextExecution", passNextExecute)
                End If
                If passOnDemandExecute.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@OnDemandExecute", passOnDemandExecute)
                End If
                cmUpdate.Parameters.AddWithValue("@Active", passActive)

                cmUpdate.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub DeleteTracker(ByVal passTrackerID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTrackerID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelTracker", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmDelete.CommandType = CommandType.StoredProcedure
                cmDelete.Parameters.AddWithValue("@TrackerID", passTrackerID)
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

