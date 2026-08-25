#Region " Imports"
Imports WebApp.APlus.DataAccess.Connections
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.UI.CustomControls
Imports System.IO
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class PrinterFriendly
        Inherits System.Web.UI.MasterPage

#Region "Error Control Methods"
        Public Sub DisplayError(ByVal passErrorMessage As String)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passErrorMessage)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            ErrorControl.DisplayError(passErrorMessage)
        End Sub
        Public Sub DisplayErrors(ByVal passEventName As String, ByVal passException As Exception, ByVal passUserID As String, ByVal passErrorType As ApplicationErrorControl.ApplicationErrorMessages)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passEventName, _
                                                                                     passException.ToString, _
                                                                                     passUserID, _
                                                                                     passErrorType)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            ErrorControl.DisplayErrors(passEventName, passException, passUserID, passErrorType)
        End Sub
        Public Sub WriteErrors(ByVal passEventName As String, ByVal passException As Exception, ByVal passUserID As String)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passEventName, _
                                                                                     passException.ToString, _
                                                                                     passUserID)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            ErrorControl.WriteErrors(passEventName, passException, passUserID)
        End Sub
        Public Sub AddBodyAttribute(ByVal passEvent As String, ByVal passAction As String)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passEvent, passAction)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try
            If Body1.Attributes.Item(passEvent) Is Nothing Then
                Body1.Attributes.Add(passEvent, passAction)
            ElseIf Body1.Attributes.Item(passEvent).Trim.Length > 0 Then
                If Body1.Attributes.Item(passEvent).ToString.Contains(passAction) = False Then
                    passAction = Body1.Attributes.Item(passEvent).ToString + ";" + passAction
                    Body1.Attributes.Add(passEvent, passAction)
                End If
            Else
                Body1.Attributes.Add(passEvent, passAction)
            End If
        End Sub
        Public Sub RemoveBodyAttribute(ByVal passEvent As String, ByVal passAction As String)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passEvent, passAction)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try
            If Body1.Attributes.Item(passEvent).Trim.Length > 0 Then
                If Body1.Attributes.Item(passEvent).Contains(passAction) Then
                    Dim iFunctionStart As Integer = Body1.Attributes.Item(passEvent).IndexOf(passAction)
                    Dim iFunctionEnd As Integer = Body1.Attributes.Item(passEvent).IndexOf(";", iFunctionStart)
                    If iFunctionEnd = -1 Then
                        iFunctionEnd = Body1.Attributes.Item(passEvent).Length
                    End If
                    Dim strEvent As String = Body1.Attributes.Item(passEvent).Substring(0, iFunctionStart - 1).Trim
                    strEvent += Body1.Attributes.Item(passEvent).Substring(iFunctionEnd, Body1.Attributes.Item(passEvent).Length - iFunctionEnd).Trim

                    Body1.Attributes.Item(passEvent) = strEvent
                End If
            End If
        End Sub
#End Region

#Region "Event Handlers"
        Protected Sub Page_Init(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.Init
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim js As New HtmlGenericControl("script")
            js.Attributes("type") = "text/javascript"
            js.Attributes("src") = ResolveUrl("~/Scripts/CommonFunctions.js")
            Page.Header.Controls.Add(js)
        End Sub
#End Region

    End Class
End Namespace

