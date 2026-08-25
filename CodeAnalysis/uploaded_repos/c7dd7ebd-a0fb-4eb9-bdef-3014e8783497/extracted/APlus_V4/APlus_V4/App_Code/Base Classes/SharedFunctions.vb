#Region "Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports System.IO
Imports WebApp.APlus
Imports WebApp.APlus.DataAccess.Connections
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Module SharedFunctions

#Region " Program Security Methods"
    Public Sub ProgramSecurityFromProgramURL(Optional ByRef cnMasterConnection As SqlConnection = Nothing)
        If SessionManager.IsAdministrator Then
            SessionManager.AllowMaintenanceAdd = True
            SessionManager.AllowMaintenanceEdit = True
            SessionManager.AllowMaintenanceDelete = True

            Return
        End If

        Dim strProgram As String = HttpContext.Current.Request.Path.Substring(HttpContext.Current.Request.ApplicationPath.Length + 1)
        Dim objDT As DataTable = ProgramSecurity.ProgramModeFromURL(SessionManager.UserID, strProgram, cnMasterConnection)

        SessionManager.AllowMaintenanceAdd = False
        SessionManager.AllowMaintenanceEdit = False
        SessionManager.AllowMaintenanceDelete = False

        If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
            Dim dtRow As DataRow = objDT.Rows(0)

            SessionManager.AllowMaintenanceAdd = Convert.ToBoolean(dtRow("AllowAdd"))
            SessionManager.AllowMaintenanceEdit = Convert.ToBoolean(dtRow("AllowEdit"))
            SessionManager.AllowMaintenanceDelete = Convert.ToBoolean(dtRow("AllowDelete"))
        End If
    End Sub
    Public Sub ProgramSecurityFromProgram(Optional ByRef cnMasterConnection As SqlConnection = Nothing)
       If SessionManager.IsAdministrator Then
            SessionManager.AllowMaintenanceAdd = True
            SessionManager.AllowMaintenanceEdit = True
            SessionManager.AllowMaintenanceDelete = True

            Return
        End If

        Dim objDT As DataTable = ProgramSecurity.ProgramModeFromProgram(SessionManager.UserID, SessionManager.CurrentMenuProgram, cnMasterConnection)

        If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
            Dim dtRow As DataRow = objDT.Rows(0)

            SessionManager.AllowMaintenanceAdd = Convert.ToBoolean(dtRow("AllowAdd"))
            SessionManager.AllowMaintenanceEdit = Convert.ToBoolean(dtRow("AllowEdit"))
            SessionManager.AllowMaintenanceDelete = Convert.ToBoolean(dtRow("AllowDelete"))
        End If
    End Sub
#End Region

End Module
