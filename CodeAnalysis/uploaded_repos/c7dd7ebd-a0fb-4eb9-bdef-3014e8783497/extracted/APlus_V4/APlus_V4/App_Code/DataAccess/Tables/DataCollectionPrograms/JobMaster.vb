#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class JobMaster

#Region " Select Job"
        Public Shared Function SelectJob(ByVal passJobID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passJobID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelJob", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@JobID", passJobID)
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

#Region " Select Job Name From JobID"
        Public Shared Function SelectJobNameFromJobID(ByVal passJobID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passJobID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim dtHolder As DataTable = SelectJob(passJobID, cnMasterConnection)

                If Not dtHolder Is Nothing AndAlso dtHolder.Rows.Count > 0 Then
                    Return dtHolder.Rows(0)("Job").ToString
                Else
                    Return ""
                End If
            Catch Exc As Exception
                Return ""
            End Try
        End Function
#End Region

#Region " Select Team From JobID"
        Public Shared Function SelectTeamFromJobID(ByVal passJobID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passJobID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim dtHolder As DataTable = SelectJob(passJobID, cnMasterConnection)
                If Not dtHolder Is Nothing AndAlso dtHolder.Rows.Count > 0 AndAlso IsNumeric(dtHolder.Rows(0)("TeamID").ToString) Then
                    Return dtHolder.Rows(0)("TeamID")
                Else
                    Return 0
                End If
            Catch Exc As Exception
                Return ""
            End Try
        End Function
#End Region

#Region " Select Job Detail"
        Public Shared Function SelectJobDetail(ByVal passJobID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passJobID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelJobMasterDetail", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@JobID", passJobID)
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

#Region " Get Job List For Team Board"
        Public Shared Sub GetJobListForTeamBoard(ByRef ddlList As System.Web.UI.WebControls.DropDownList, ByVal passSiteID As Integer, ByVal passTeamID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, ddlList.ID, passSiteID, passTeamID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelJobMasterListTeamBoard", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@SiteID", passSiteID)
                cmSelect.Parameters.AddWithValue("@TeamID", passTeamID)
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    ddlList.Items.Add(New ListItem(drList.GetString(1), drList.GetInt32(0)))
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

#Region " Insert Job"
        Public Shared Function InsertJob(ByVal passJob As String, ByVal passSiteID As Integer, _
                                         ByVal passRatingType As String, ByVal passTeamID As Integer, _
                                         Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passJob, passSiteID, passRatingType, passTeamID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cm As New SqlClient.SqlCommand("spInsJobMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cm
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@Job", passJob)
                    .Parameters.AddWithValue("@SiteID", passSiteID)
                    .Parameters.AddWithValue("@RatingType", passRatingType)
                    If passTeamID > 0 Then
                        .Parameters.AddWithValue("@TeamID", passTeamID)
                    End If

                    Return .ExecuteScalar
                End With
            Catch Exc As Exception
                Throw
            Finally
                cm.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " Insert Team Job"
        Public Shared Function InsertTeamJob(ByVal passTeamID As Integer, ByVal passTeam As String, ByVal passSiteID As Integer, ByVal passRouteAbbrev As String) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, passTeam, passSiteID, passRouteAbbrev)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnMasterConnection As SqlConnection = ApplicationConnection.OpenMasterConnection
            Dim trans As SqlTransaction = cnMasterConnection.BeginTransaction(IsolationLevel.ReadUncommitted)

            Dim cnSubConnection As New ApplicationConnection
            Dim cm As New SqlClient.SqlCommand("spInsJobMasterReturn", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim iJobID As Integer = -1
            Dim bError As Boolean = False

            Try
                With cm
                    If Not trans Is Nothing Then
                        cm.Transaction = trans
                    End If
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@Job", passTeam + " Internal Training Matrix")
                    .Parameters.AddWithValue("@SiteID", passSiteID)
                    .Parameters.AddWithValue("@RatingType", "Standard")
                    .Parameters.AddWithValue("@TeamID", passTeamID)

                    iJobID = .ExecuteScalar
                End With

                If iJobID < 0 Then
                    'bad
                    bError = True
                Else
                    Dim iJobSkillID As Integer
                    Dim iCounter As Integer = 0

                    'now we need to add the job skills!
                    Dim dtTools As DataTable = RouteStepsKeyActionsTools.SelectRouteStepsKeyActionsToolsByRouteAbbrev(passRouteAbbrev)
                    If dtTools Is Nothing OrElse dtTools.Rows.Count = 0 Then
                        bError = True
                    End If

                    If bError = False Then
                        Dim iCategoryID As Integer = SkillCategoryMaster.SelectSkillCategoryID("Tool")
                        Dim strRootDir As String = ""
                        If iCategoryID > 0 Then
                            For Each dtRow As DataRow In dtTools.Rows
                                iCounter += 1
                                iJobSkillID = JobSkillMaster.InsertJobSkill(iJobID, iCategoryID, dtRow("Tool").ToString, "", iCounter, 3, 4, cnMasterConnection, trans)
                                If iJobSkillID = -1 Then
                                    bError = True
                                ElseIf iJobSkillID = -2 Then
                                    'duplicate, keep going without generating an error
                                Else
                                    'good
                                    'based on what data we have then modify the document attachment
                                    'document must include the fully qualified URL

                                    Dim dsAttachment As DataTable
                                    Dim strURL As String = ""

                                    If IsNumeric(dtRow("AttachmentID").ToString) AndAlso Convert.ToInt16(dtRow("AttachmentID").ToString) > 0 AndAlso _
                                    dtRow("AttachmentType").ToString.Trim.Length > 0 Then
                                        dsAttachment = AttachmentsMaster.SelectAttachmentsMasterByID(dtRow("AttachmentID"))
                                        If dsAttachment IsNot Nothing AndAlso dsAttachment.Rows.Count > 0 Then
                                            strRootDir = ConfigurationManager.AppSettings(dtRow("AttachmentType").ToString.Trim & "AttachmentsVirtualRootDirectory").ToString

                                            strURL = "http://" & ConfigurationManager.AppSettings("ApplicationServerDNS").ToString
                                            strURL += strRootDir & "en/" & dsAttachment.Rows(0)("Attachment").ToString
                                        End If
                                    ElseIf dtRow("URLLink").ToString.Trim.Length > 0 Then
                                        strURL = dtRow("URLLink").ToString.Trim
                                    Else
                                        strURL = ""
                                    End If

                                    'only insert the attachment if we have a url
                                    If strURL.Trim.Length > 0 Then
                                        JobSkillAttachments.InsertJobSkillAttachment(iJobSkillID, dtRow("Tool").ToString, strURL, cnMasterConnection, trans)
                                    End If
                                End If
                            Next
                        Else
                            bError = True
                        End If
                    End If
                End If

                If bError Then
                    trans.Rollback()
                    Return -1
                Else
                    trans.Commit()
                    Return iJobID
                End If
            Catch Exc As Exception
                trans.Rollback()
                Return -1
                Throw
            Finally
                cm.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " Update Job"
        Public Shared Sub UpdateJob(ByVal passJobID As Integer, ByVal passJob As String, ByVal passRatingType As String, _
                                    ByVal passTeamID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passJobID, _
                                                                                     passJob, _
                                                                                     passRatingType, _
                                                                                     passTeamID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdJobMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@JobID", passJobID)
                    .Parameters.AddWithValue("@Job", passJob.Trim)
                    .Parameters.AddWithValue("@RatingType", passRatingType)
                    If passTeamID > 0 Then
                        .Parameters.AddWithValue("@TeamID", passTeamID)
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

#Region " Delete Team Job By Team"
        Public Shared Sub DeleteTeamJobByTeam(ByVal passTeamID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelTeamJobByTeam", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmDelete.CommandType = CommandType.StoredProcedure
                cmDelete.Parameters.AddWithValue("@TeamID", passTeamID)
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
