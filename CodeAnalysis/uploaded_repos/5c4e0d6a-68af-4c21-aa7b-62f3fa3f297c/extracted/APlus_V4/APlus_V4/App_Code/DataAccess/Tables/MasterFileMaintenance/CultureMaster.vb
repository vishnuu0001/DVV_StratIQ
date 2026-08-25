#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class CultureMaster

#Region " Select CultureMaster and Return Dropdownlist values"
        Public Shared Sub SelectCultureMasterList(ByRef ddlList As System.Web.UI.WebControls.DropDownList, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, ddlList.ID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelCultureMasterList", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
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

        Public Shared Sub SelectCultureMasterCodeList(ByRef ddlList As System.Web.UI.WebControls.DropDownList, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelCultureMasterList", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    ddlList.Items.Add(New ListItem(drList.GetString(2), drList.GetString(1)))
                End While
                ddlList.Items.Insert(0, (New ListItem("", "")))
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " Select Methods"
        Public Shared Function SelectCultureMaster(ByVal passCultureID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Dim cnSubConnection As New ApplicationConnection

            Try
                Dim da As New SqlDataAdapter(New SqlCommand("spSelCultureMasterByID", cnSubConnection.OpenConnection(cnMasterConnection)))
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                Dim ds As New DataTable

                da.SelectCommand.Parameters.AddWithValue("@CultureID", passCultureID)
                da.Fill(ds)
                da.Dispose()

                Return ds
            Catch Exc As Exception
                Throw
            Finally
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function GetCultureIDByCode(ByVal passCultureCode As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Dim cnSubConnection As New ApplicationConnection

            Try
                Dim da As New SqlDataAdapter(New SqlCommand("spSelCultureMaster", cnSubConnection.OpenConnection(cnMasterConnection)))
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                Dim objDT As New DataTable
                Dim iCultureID As Integer = 0

                da.Fill(objDT)
                da.Dispose()

                For Each dtRow As DataRow In objDT.Rows
                    If dtRow("CultureCode").ToString = passCultureCode Then
                        iCultureID = dtRow("CultureID")
                    End If
                Next

                Return iCultureID
            Catch Exc As Exception
                Throw
            Finally
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " Add Culture"
        Public Shared Function AddCulture(ByVal passCulture As String, ByVal passDescription As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passCulture, passDescription, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsCultureMaster", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                cmAdd.CommandType = CommandType.StoredProcedure
                cmAdd.Parameters.AddWithValue("@CultureCode", passCulture)
                cmAdd.Parameters.AddWithValue("@CultureDescription", passDescription)
                Return cmAdd.ExecuteScalar
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " Update Culture"
        Public Shared Sub UpdateCulture(ByVal passCultureID As Integer, _
                                        ByVal passCultureCode As String, _
                                        ByVal passDescription As String, _
                                        Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spUpdCultureMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmAdd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@CultureID", passCultureID)
                    .Parameters.AddWithValue("@CultureCode", passCultureCode)
                    .Parameters.AddWithValue("@CultureDescription", passDescription)
                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " Delete Culture"
        Public Shared Sub DeleteCulture(ByVal passCultureID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passCultureID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelCultureMaster", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                cmDelete.CommandType = CommandType.StoredProcedure
                cmDelete.Parameters.AddWithValue("@CultureID", passCultureID)
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
