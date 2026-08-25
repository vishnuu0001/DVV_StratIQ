#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class JobSkillMaster

#Region " Select Job Skill"
        Public Shared Function SelectJobSkill(ByVal passJobSkillID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passJobSkillID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelJobSkillbyID", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@JobSKillID", passJobSkillID)
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

#Region " Select Job Skills By Job"
        Public Shared Function SelectJobSkillsByJob(ByVal passJobID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
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
            Dim da As New SqlDataAdapter(New SqlCommand("spSelJobSkillsbyJob", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@JobID", passJobID)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " Get Next Job Skill Sequence Number"
        Public Shared Function GetNextJobSkillSequenceNumber(ByVal passJobID As Integer) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passJobID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim iReturn As Integer = 0
            Try
                Dim objDT As DataTable = SelectJobSkillsByJob(passJobID)
                If objDT.Rows.Count > 0 Then
                    iReturn = Val(objDT.Rows(objDT.Rows.Count - 1).Item("Sequence").ToString)
                    iReturn += 1
                End If
                If iReturn < 1 Then
                    iReturn = 1
                End If
            Catch Exc As Exception
                iReturn = 1
            End Try
            Return iReturn
        End Function
#End Region

#Region " Insert Job Skill"
        Public Shared Function InsertJobSkill(ByVal passJobID As Integer, _
                                              ByVal passCategoryID As Integer, _
                                              ByVal passSkill As String, _
                                              ByVal passCriteria As String, _
                                              ByVal passSequence As Integer, _
                                              ByVal passRequired As String, _
                                              ByVal passDesired As String, _
                                              Optional ByRef cnMasterConnection As SqlConnection = Nothing, _
                                              Optional ByRef trans As SqlTransaction = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passJobID, _
                                                                                     passCategoryID, _
                                                                                     passSkill, _
                                                                                     passCriteria, _
                                                                                     passSequence, _
                                                                                     passRequired, _
                                                                                     passDesired, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cm As New SqlClient.SqlCommand("spInsJobSkill", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                If Not trans Is Nothing Then
                    cm.Transaction = trans
                End If

                With cm
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@JobID", passJobID)
                    .Parameters.AddWithValue("@SkillCategoryID", passCategoryID)
                    .Parameters.AddWithValue("@Skill", passSkill)
                    If Not String.IsNullOrEmpty(passCriteria.Trim()) Then .Parameters.AddWithValue("@AssessmentCriteria", passCriteria)
                    .Parameters.AddWithValue("@Sequence", passSequence)
                    .Parameters.AddWithValue("@RequiredRating", passRequired)
                    .Parameters.AddWithValue("@DesiredRating", passDesired)
                    Return .ExecuteScalar
                End With
            Catch Exc As Exception
                Throw
            Finally
                cm.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function

        'Public Shared Function InsertJobSkillReturn(ByVal passJobID As Integer, _
        '                                            ByVal passCategoryID As Integer, _
        '                                            ByVal passSkill As String, _
        '                                            ByVal passCriteria As String, _
        '                                            ByVal passSequence As Integer, _
        '                                            ByVal passRequired As String, _
        '                                            ByVal passDesired As String, _
        '                                            Optional ByRef cnMasterConnection As SqlConnection = Nothing, _
        '                                            Optional ByRef trans As SqlTransaction = Nothing) As Integer
        '    Try
        '        If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATraining) Then
        '            Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
        '            Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
        '                                                                             passJobID, _
        '                                                                             passCategoryID, _
        '                                                                             passSkill, _
        '                                                                             passCriteria, _
        '                                                                             passSequence, _
        '                                                                             passRequired, _
        '                                                                             passDesired, "", "")
        '            EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
        '        End If
        '    Catch Exc As Exception
        '        'Nothing
        '    End Try

        '    Dim cnSubConnection As New ApplicationConnection
        '    Dim cm As New SqlClient.SqlCommand("spInsJobSkillReturn", cnSubConnection.OpenConnection(cnMasterConnection))
        '    Dim iReturn As Integer = -1
        '    Try
        '        If Not trans Is Nothing Then
        '            cm.Transaction = trans
        '        End If

        '        With cm
        '            .CommandType = CommandType.StoredProcedure
        '            .Parameters.AddWithValue("@JobID", passJobID)
        '            .Parameters.AddWithValue("@SkillCategoryID", passCategoryID)
        '            .Parameters.AddWithValue("@Skill", passSkill)
        '            If Not String.IsNullOrEmpty(passCriteria.Trim()) Then .Parameters.AddWithValue("@AssessmentCriteria", passCriteria)
        '            .Parameters.AddWithValue("@Sequence", passSequence)
        '            .Parameters.AddWithValue("@RequiredRating", passRequired)
        '            .Parameters.AddWithValue("@DesiredRating", passDesired)
        '            .ExecuteNonQuery()
        '        End With
        '        iReturn = cm.Parameters("@RETURN_VALUE").Value()
        '    Catch Exc As Exception
        '        Throw
        '    Finally
        '        cm.Dispose()
        '        cnSubConnection.CloseConnection(cnMasterConnection)
        '    End Try
        '    Return iReturn
        'End Function
#End Region

#Region " Update"
        Public Shared Sub UpdateJobSkill(ByVal passJobSkillID As Integer, _
                                         ByVal passCategoryID As Integer, _
                                         ByVal passSkill As String, _
                                         ByVal passCriteria As String, _
                                         ByVal passSequence As Integer, _
                                         ByVal passRequiredRating As String, _
                                         ByVal passDesiredRating As String, _
                                         Optional ByRef cnMasterConnection As SqlConnection = Nothing)

            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passJobSkillID, _
                                                                                     passCategoryID, _
                                                                                     passSkill, _
                                                                                     passCriteria, _
                                                                                     passSequence, _
                                                                                     passRequiredRating, _
                                                                                     passDesiredRating, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdJobSkill", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@JobSkillID", passJobSkillID)
                    .Parameters.AddWithValue("@SkillCategoryID", passCategoryID)
                    .Parameters.AddWithValue("@Skill", passSkill)
                    If Not String.IsNullOrEmpty(passCriteria.Trim()) Then .Parameters.AddWithValue("@AssessmentCriteria", passCriteria)
                    .Parameters.AddWithValue("@Sequence", passSequence)
                    .Parameters.AddWithValue("@RequiredRating", passRequiredRating)
                    .Parameters.AddWithValue("@DesiredRating", passDesiredRating)
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

#Region " Delete"
        Public Shared Sub DeleteJobSkill(ByVal passJobSkillID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passJobSkillID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelJobSkill", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmDelete.CommandType = CommandType.StoredProcedure
                cmDelete.Parameters.AddWithValue("@JobSkillID", passJobSkillID)
                cmDelete.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmDelete.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " ChangeJobSkillSequence"
        Public Shared Sub MoveSkillJob(ByVal passOldSkill As Integer, ByVal passNewSkill As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passOldSkill, passNewSkill, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmProcessFeedback As New SqlCommand("spUpdJobSkillMove", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmProcessFeedback
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@oldSkill", passOldSkill)
                    .Parameters.AddWithValue("@newSkill", passNewSkill)
                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmProcessFeedback.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " - Insert Job Skills Import"
        Public Shared Sub InsertJobSkillsImport(ByVal passJobID As Integer, ByVal passUser As String, ByRef passDataTable As DataTable)
            Dim cnMasterConnection As SqlConnection = ApplicationConnection.OpenMasterConnection
            Dim trans As SqlTransaction = cnMasterConnection.BeginTransaction(IsolationLevel.ReadUncommitted)
            Dim iSkillCategoryID As Integer
            Dim iRet As Integer
            Dim bError As Boolean = False
            Try
                'loop through table rows and insert
                For Each objRow As DataRow In passDataTable.Rows
                    iSkillCategoryID = SkillCategoryMaster.SelectSkillCategoryID(objRow("SkillCategory").ToString)
                    If iSkillCategoryID > 0 Then
                        iRet = InsertJobSkill(passJobID, iSkillCategoryID, objRow("Skill").ToString, objRow("AssessmentCriteria").ToString, objRow("Sequence"), objRow("RequiredRating").ToString, objRow("DesiredRating").ToString, cnMasterConnection, trans)
                    Else
                        bError = True
                        objRow("Errors") = "Invalid Skill Category"
                    End If
                Next objRow
                trans.Commit()
            Catch Exc As Exception
                trans.Rollback()
                Throw
            Finally
                ApplicationConnection.CloseMasterConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

    End Class
End Namespace
