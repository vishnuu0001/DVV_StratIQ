#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper
Imports WebApp.APlus.DataAccess
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.DataAccess.Custom
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class ApplicationCacheMaster
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Application Cache Master"
        Private Shared ReadOnly ProgramName As String = "ApplicationCacheMaster"
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnExit}
            Dim OverMessageArr() As String = {"Exit"}
            Dim OutMessageArr() As String = {""}

            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnExit.UniqueID + "'),window.event)")
        End Sub
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

            Master.HeaderMessage = FormName & " - Edit Application Cache"
            Master.IconImage = Request.ApplicationPath + "/images/Cache.gif"

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                If Not IsNothing(HttpContext.Current.Application("CultureCache")) Then
                    Dim dt As New DataTable
                    dt.Columns.Add(New DataColumn("Language", GetType(String)))
                    dt.Columns.Add(New DataColumn("NumberOfItems", GetType(String)))

                    For Each de As DictionaryEntry In CType(HttpContext.Current.Application("CultureCache"), Hashtable)
                        Dim myHash As Hashtable = CType(de.Value, Hashtable)
                        Dim dr As DataRow = dt.NewRow
                        dr.Item("Language") = de.Key.ToString.Trim()
                        dr.Item("NumberOfItems") = myHash.Count.ToString.Trim()
                        dt.Rows.Add(dr)
                    Next
                    gvCach.DataSource = dt
                    gvCach.DataBind()
                    lblHashRows.Text = CType(HttpContext.Current.Application("CultureCache"), Hashtable).Keys.Count & " Items"
                Else
                    gvCach.DataSource = Nothing
                    gvCach.DataBind()
                    lblHashRows.Text = "0 Items"
                End If
            End If
        End Sub

        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try
            RemoveCurrentProgramandGoBack()
        End Sub

        Private Sub btnClearCultureCache_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnClearCultureCache.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                If Not IsNothing(HttpContext.Current.Application("CultureCache")) Then
                    HttpContext.Current.Application.Remove("CultureCache")
                End If

                If Not IsNothing(HttpContext.Current.Application("CultureCache")) Then
                    Dim dt As New DataTable
                    dt.Columns.Add(New DataColumn("Language", GetType(String)))
                    dt.Columns.Add(New DataColumn("NumberOfItems", GetType(String)))

                    For Each de As DictionaryEntry In CType(HttpContext.Current.Application("CultureCache"), Hashtable)
                        Dim myHash As Hashtable = CType(de.Value, Hashtable)
                        Dim dr As DataRow = dt.NewRow
                        dr.Item("Language") = de.Key.ToString.Trim()
                        dr.Item("NumberOfItems") = myHash.Count.ToString.Trim()
                        dt.Rows.Add(dr)
                    Next
                    gvCach.DataSource = dt
                    gvCach.DataBind()
                    lblHashRows.Text = CType(HttpContext.Current.Application("CultureCache"), Hashtable).Keys.Count & " Items"
                Else
                    gvCach.DataSource = Nothing
                    gvCach.DataBind()
                    lblHashRows.Text = "0 Items"
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - btnClearCultureCache_Click", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
            End Try
        End Sub
#End Region

    End Class
End Namespace