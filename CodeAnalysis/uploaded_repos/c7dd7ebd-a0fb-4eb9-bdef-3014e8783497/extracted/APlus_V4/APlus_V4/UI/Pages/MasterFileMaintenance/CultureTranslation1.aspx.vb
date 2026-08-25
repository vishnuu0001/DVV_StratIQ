#Region " Imports"
Imports System.IO
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class CultureTranslation1
        Inherits ApplicationBase

#Region " Constants"
        Private Shared ReadOnly FormName As String = "Culture Translation"
        Private Shared ReadOnly ProgramName As String = "CultureTranslation11"
#End Region

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, ProgramName, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Master.IconImage = Request.ApplicationPath & "/images/earth_location.gif"
            Master.HeaderMessage = GetTranslationString(FormName, FormName)
            Master.ProgramName = ProgramName
            Master.AddBodyAttribute("onkeydown", "TrapEscKey(document.getElementById('" + MasterControl1.ExitButtonID + "'),window.event)")
            Master.AddBodyAttribute("onkeydown", "TrapEnterKey(document.getElementById('" + MasterControl1.AddButtonID + "'),window.event)")

            MasterControl1.ConnectionString = ConfigurationManager.AppSettings("CultureTranslationConnectionString").ToString
            MasterControl1.StoredProcedureParams.Add("@ResourceType", strTranslationApplicationName)
            MasterControl1.StoredProcedureParams.Add("@CultureCode", SessionManager.CulturePref)
        End Sub
        Protected Sub Timer1_Tick(ByVal sender As Object, ByVal e As System.EventArgs) Handles Timer1.Tick
            Timer1.Enabled = False
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            MasterControl1.DataBind()
            Master.MasterScriptManager.RegisterPostBackControl(MasterControl1.ExportButton)
        End Sub
        Protected Sub MasterControl1_FunctionButtonOneClick(ByVal sender As Object, ByVal e As System.EventArgs) Handles MasterControl1.FunctionButtonOneClick
            If HttpContext.Current.Application("CultureCache") IsNot Nothing Then
                Try
                    For Each de As DictionaryEntry In CType(HttpContext.Current.Application("CultureCache"), Hashtable)
                        If de.Key.ToString.ToUpper = SessionManager.CulturePref.ToUpper Then
                            CType(HttpContext.Current.Application("CultureCache"), Hashtable).Remove(de.Key)

                            Exit For
                        End If
                    Next
                Catch ex As Exception
                    Master.DisplayError(ex.Message)
                End Try
            End If
        End Sub
        Protected Sub MasterControl1_onRowCommand(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewCommandEventArgs) Handles MasterControl1.onRowCommand
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", e.CommandName)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Select Case e.CommandName
                Case "ViewRow", "EditRow", "DeleteRow"
                    SessionManager.SelectedCultureCode = MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("CultureCode").ToString
                    SessionManager.SelectedCultureValue = MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("ResourceKey").ToString
                    SessionManager.CultureTranslationMode = e.CommandName
                    LastPixelPositionUpdate(ProgramName, Master.CurrentPixelPosition)
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("CultureTranslation2"), False)
            End Select
        End Sub
#End Region

    End Class
End Namespace

