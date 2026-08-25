#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class TrackerPlanMaster

#Region " Select Methods"
        Public Shared Function SelectTrackerPlanHeader(ByVal passSiteID As Integer, ByVal passTrackerPlanID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTrackerPlanID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim strReturn As String = ""

            Try
                Dim objDT As DataTable = SelectTrackerPlan(passTrackerPlanID)
                If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                    Dim dtRow As DataRow = objDT.Rows(0)

                    strReturn = dtRow("SiteAbbrev").ToString.Trim & ":"
                    strReturn += dtRow("PillarAbbrev").ToString.Trim & ":"
                    strReturn += dtRow("BusinessAreaAbbrev").ToString.Trim & ":"
                    strReturn += dtRow("BusinessUnitAbbrev").ToString.Trim & ":"
                    strReturn += dtRow("SavingsCategory").ToString.Trim
                Else
                    If passSiteID > 0 Then
                        objDT = SiteMaster.GetSiteMasterBySite(passSiteID)
                        If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                            strReturn = objDT.Rows(0)("SiteAbbrev").ToString.Trim
                        End If
                    End If
                End If
            Catch ex As Exception

            End Try

            Return strReturn
        End Function
        Public Shared Function SelectTrackerPlan(ByVal passTrackerPlanID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTrackerPlanID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTrackerPlanByID", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
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
        Public Shared Function SelectTrackerPlanMasterSavings(ByVal passSiteID As Integer, ByVal passYear As Integer, ByVal passShowInactive As Boolean, _
                                                              ByVal passShowPlan As Boolean, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSiteID, passYear, passShowInactive, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTrackerPlanMasterSavings", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@SiteID", passSiteID)
                da.SelectCommand.Parameters.AddWithValue("@Year", passYear)
                da.SelectCommand.Parameters.AddWithValue("@ShowInactive", passShowInactive)
                da.SelectCommand.Parameters.AddWithValue("@ShowPlan", passShowPlan)
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
        Public Shared Function InsertTrackerPlan(ByVal passSiteID As Integer, ByVal passPillarAbbrev As String, ByVal passBusinessAreaID As Integer, _
                                                 ByVal passBusinessUnitID As Integer, ByVal passSavingsCategoryID As Integer, ByVal passActive As Boolean, _
                                                 Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSiteID, passPillarAbbrev, passBusinessAreaID, passBusinessUnitID, _
                                                                                     passSavingsCategoryID, passActive, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsTrackerPlan", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmAdd.CommandType = CommandType.StoredProcedure

                cmAdd.Parameters.AddWithValue("@SiteID", passSiteID)
                If passPillarAbbrev.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@PillarAbbrev", passPillarAbbrev)
                End If
                cmAdd.Parameters.AddWithValue("@BusinessAreaID", passBusinessAreaID)
                If passBusinessUnitID > 0 Then
                    cmAdd.Parameters.AddWithValue("@BusinessUnitID", passBusinessUnitID)
                End If
                If passSavingsCategoryID > 0 Then
                    cmAdd.Parameters.AddWithValue("@SavingsCategoryID", passSavingsCategoryID)
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
        Public Shared Sub UpdateTrackerPlan(ByVal passTrackerPlanID As Integer, ByVal passSiteID As Integer, ByVal passPillarAbbrev As String, _
                                            ByVal passBusinessAreaID As Integer, ByVal passBusinessUnitID As Integer, ByVal passSavingsCategoryID As Integer, _
                                            ByVal passActive As Boolean, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTrackerPlanID, passSiteID, passPillarAbbrev, passBusinessAreaID, _
                                                                                     passBusinessUnitID, passSavingsCategoryID, passActive, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdTrackerPlan", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmUpdate.CommandType = CommandType.StoredProcedure

                cmUpdate.Parameters.AddWithValue("@TrackerPlanID", passTrackerPlanID)
                cmUpdate.Parameters.AddWithValue("@SiteID", passSiteID)
                If passPillarAbbrev.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@PillarAbbrev", passPillarAbbrev)
                End If
                cmUpdate.Parameters.AddWithValue("@BusinessAreaID", passBusinessAreaID)
                If passBusinessUnitID > 0 Then
                    cmUpdate.Parameters.AddWithValue("@BusinessUnitID", passBusinessUnitID)
                End If
                If passSavingsCategoryID > 0 Then
                    cmUpdate.Parameters.AddWithValue("@SavingsCategoryID", passSavingsCategoryID)
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
        Public Shared Sub DeleteTrackerPlan(ByVal passTrackerPlanID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTrackerPlanID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelTrackerPlan", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmDelete.CommandType = CommandType.StoredProcedure
                cmDelete.Parameters.AddWithValue("@TrackerPlanID", passTrackerPlanID)
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

