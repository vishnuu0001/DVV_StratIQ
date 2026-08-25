#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class FeedbackMaster

#Region " Process Feedback"
        Public Shared Sub ProcessFeedback(ByVal passID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmProcessFeedback As New SqlCommand("spUpdFeedbackMaster", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                cmProcessFeedback.CommandType = CommandType.StoredProcedure
                cmProcessFeedback.Parameters.AddWithValue("@ID", passID)
                cmProcessFeedback.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmProcessFeedback.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " Add Feedback"
        Public Shared Sub AddFeedbackMaster(ByVal passFeedback As String, _
                                            ByVal passUserID As String, _
                                            ByVal passProgram As String, _
                                            Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passFeedback, passUserID, passProgram, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cm As New SqlClient.SqlCommand("spInsFeedbackMaster", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                cm.CommandType = CommandType.StoredProcedure
                cm.Parameters.AddWithValue("@Feedback", passFeedback)
                cm.Parameters.AddWithValue("@UserID", passUserID)
                cm.Parameters.AddWithValue("@Program", passProgram)
                cm.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cm.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " Select Feedback"
        Public Shared Function SelectFeedback(ByVal passFeedbackID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passFeedbackID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelFeedbackMasterByID", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@ID", passFeedbackID)
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

#Region " Update Feedback"
        Public Shared Sub UpdateFeedback(ByVal passFeedbackID As Integer, _
                                         ByVal passProcessed As Integer, _
                                         ByVal passComments As String, _
                                         ByVal passFeedbackType As Integer, _
                                         ByVal passFeedbackPriority As Integer, _
                                         ByVal passDevComments As String, _
                                         Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passFeedbackID, _
                                                                                     passProcessed, _
                                                                                     passComments, _
                                                                                     passFeedbackType, _
                                                                                     passFeedbackPriority, _
                                                                                     passDevComments, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdFeedbackMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@ID", passFeedbackID)
                    .Parameters.AddWithValue("@Processed", passProcessed)
                    If Not String.IsNullOrEmpty(passComments.Trim()) Then .Parameters.AddWithValue("@Comments", passComments)
                    If passFeedbackType > -1 Then .Parameters.AddWithValue("@FeedbackTypeID", passFeedbackType)
                    If passFeedbackPriority > -1 Then .Parameters.AddWithValue("@FeedbackPriorityID", passFeedbackPriority)
                    If Not String.IsNullOrEmpty(passDevComments.Trim()) Then .Parameters.AddWithValue("@DevComments", passDevComments)
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

    End Class
End Namespace