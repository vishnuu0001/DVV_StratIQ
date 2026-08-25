#Region "Imports"
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.DataAccess.Custom
Imports System.Threading
Imports System.Globalization
Imports System.IO
Imports System.Web.Mail
Imports System.Web.UI.Page
Imports System.Data
Imports System.Reflection
#End Region

Namespace WebApp.APlus
    Public Module Helper

#Region " Enums"
        Public Enum DataGridStatus
            Show
            Hide
        End Enum
        Public Enum WorkcenterStatus
            Unlock
            Lock
        End Enum

        Public Enum RollStatus
            InUseByWorkcenter
            NotInUse
            Used
        End Enum

        Public Enum WIPPalletStatus
            InUseByWorkcenter
            NotInUse
            Used
        End Enum

        Public Enum NextCustomerPallettNumberStatus
            Unlock
            Lock
        End Enum

        Public Enum LabelFormatType
            Pallet
            Roll
        End Enum

        Public Enum StickMasterDisplayStatus
            Hide
            Show
        End Enum

        Public Enum StagPallet
            Yes
            OK
            Cancel
        End Enum

        Public Enum FunctionKeys
            Show
            Hide
        End Enum

        Public Enum PanelStatus
            Show
            Hide
        End Enum

        Public Enum ValidationStatus
            Enabled
            Disabled
        End Enum

        Public Enum TextboxStatus
            Enabled
            Disabled
        End Enum

        Public Enum ProductionRecordType
            StickWeight
            RollWeight
        End Enum

        Public Enum PanelEnabled
            Enable
            Disable
        End Enum

        Public Enum InventoryType
            FinishedGoodsLimbo
            DextendedFinishedGoods
            Rough
            Rework
            OffSpec
            Broke
            Invalid
        End Enum

        Public Enum HoldFlag
            Hold
            NotOnHold
        End Enum

        Public Enum TransactionID
            AR
            DR
            RR
            SR
        End Enum
        Public Enum LinkType
            L
            P
            T
        End Enum
#End Region

#Region " Assembly & Version Methods"
        Public Function GetVersionNumber() As String
            Dim strVersion As String = String.Empty

            Try
                Dim objAssembly As Assembly = Assembly.GetExecutingAssembly()
                strVersion = objAssembly.GetName().Version.ToString()
            Catch ex As Exception
                strVersion = String.Empty
            End Try

            Return strVersion
        End Function
#End Region

#Region " Functions associated with JavaScripts"

        Public Function ServerSideCloseString() As String
            Dim sScript As New System.Text.StringBuilder

            sScript.Append("<SCRIPT language=""javascript"">" & vbCrLf)
            sScript.Append("window.close();" & vbCrLf)
            sScript.Append("</SCRIPT>" & vbCrLf)

            Return sScript.ToString
        End Function

        Public Sub AllowNumeric(ByVal ParamArray txtArr() As System.Web.UI.WebControls.TextBox)
            Dim txt As System.Web.UI.WebControls.TextBox
            For Each txt In txtArr
                txt.Attributes.Add("onkeydown", "javascript:AllowNumbers(window.event);")
            Next
        End Sub

        Public Function AllowNumeric() As String
            Return "javascript:AllowNumbers(window.event);"
        End Function

        Public Sub AllowIntegers(ByVal ParamArray txtArr() As System.Web.UI.WebControls.TextBox)
            Dim txt As System.Web.UI.WebControls.TextBox
            For Each txt In txtArr
                txt.Attributes.Add("onkeydown", "javascript:AllowIntegers(window.event);")
            Next
        End Sub

        Public Function AllowIntegers() As String
            Return "javascript:AllowIntegers(window.event);"
        End Function

        Public Function TabNextDown(ByVal Num As Integer) As String
            Return "javascript:TabNext(this,'down'," & Num.ToString() & ");"
        End Function

        Public Function TabNextUp(ByVal Num As Integer, ByVal ctl As TextBox) As String
            Return "javascript:TabNext(this,'up'," & Num.ToString() & ",document.all." & ctl.ClientID & ");"
        End Function

        Public Function NextField(ByVal ctl As TextBox) As String
            Return "javascript:NextField(document.all." & ctl.ClientID & ");"
        End Function

        Public Function Tab(ByVal ctlNext As Object, ByVal ctlPrev As Object, ByVal AllowNumbers As String) As String
            Return "javascript:Tab(document.all." & ctlNext.UniqueID & ", document.all." & ctlPrev.UniqueID & ", window.event, '" & AllowNumbers.Trim() & "');"
        End Function

        Public Sub AssociateJavascriptEventHandler(ByVal EventName As String, ByVal ctlArr() As TextBox, ByVal ValueArr() As String)
            For i As Integer = 0 To ctlArr.Length - 1
                ctlArr(i).Attributes.Add(EventName, ValueArr(i).ToString())
            Next
        End Sub

        Public Sub AssociateTabJavascriptEventHandler(ByVal ctlArr() As Object, ByVal ValueArr() As String)
            For i As Integer = 0 To ctlArr.Length - 1
                ctlArr(i).Attributes.Add("onkeydown", ValueArr(i).ToString())
            Next
        End Sub

        Public Sub ShowStatusBar(ByVal ctlArr() As WebControl, ByVal MouseOverMessage() As String, ByVal MouseOutMessage() As String)
            Dim len As Int16 = ctlArr.Length - 1
            Dim i As Int16

            For i = 0 To len
                If i = len Then
                    Exit Sub
                End If
                ctlArr(i).Attributes.Add("onmouseover", "javascript:window.status='" & MouseOverMessage(i) & "';return true")
                ctlArr(i).Attributes.Add("onmouseout", "javascript:window.status='" & MouseOutMessage(i) & "';return true")
            Next

        End Sub

        Public Sub ShowStatusBar(ByVal ctlArr() As HtmlControl, ByVal MouseOverMessage() As String, ByVal MouseOutMessage() As String)
            Dim len As Int16 = ctlArr.Length - 1
            Dim i As Int16

            For i = 0 To len
                If i = len Then
                    Exit Sub
                End If
                ctlArr(i).Attributes.Add("onmouseover", "javascript:window.status='" & MouseOverMessage(i) & "';return true")
                ctlArr(i).Attributes.Add("onmouseout", "javascript:window.status='" & MouseOutMessage(i) & "';return true")
            Next
        End Sub

#End Region

#Region " Prevent Page Caching and Check the Session Timeout"
        'Redirects user to login page if Session timed out
        Public Sub CheckSessionTimeout()
            If Not HttpContext.Current.Request.FilePath.Contains("/Login.aspx") Then
                If SessionManager.UserID = "" Then
                    System.Web.Security.FormsAuthentication.SignOut()
                    HttpContext.Current.Response.Redirect(HttpContext.Current.Request.ApplicationPath)
                End If
            End If
        End Sub

        'This prevents IE from caching the page
        Public Sub DisablePageCaching()
            HttpContext.Current.Response.Expires = -1000
            HttpContext.Current.Response.AddHeader("Pragma", "No-Cache")
            HttpContext.Current.Response.CacheControl = "no-cache"
        End Sub
#End Region

#Region " Remove CurrentProgram and GoBack"
        Public Sub RemoveCurrentProgramandGoBack()
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CurrentProgram)
            If ProgramSecurity.CanUserAccessProgram(SessionManager.UserID, SessionManager.CurrentMenuProgram) Then
                HttpContext.Current.Response.Redirect(HttpContext.Current.Request.ApplicationPath & Path.AltDirectorySeparatorChar & (ProgramSecurity.GetProgramURL(SessionManager.CurrentMenuProgram)), False)
            Else
                Dim strMenuProgram As String = ProgramSecurity.VerifyInitialMenu(SessionManager.UserID)
                If ProgramSecurity.CanUserAccessProgram(SessionManager.UserID, strMenuProgram) Then
                    HttpContext.Current.Response.Redirect(HttpContext.Current.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strMenuProgram), False)
                Else
                    HttpContext.Current.Session.Abandon()
                    HttpContext.Current.Response.Redirect(HttpContext.Current.Request.ApplicationPath & "\Login.aspx", False)
                End If
            End If
        End Sub
#End Region

#Region " Status of Function Keys"
        Public Sub ChangeFunctionKeysStatus(ByVal Status As FunctionKeys, ByVal ParamArray Keys() As Control)
            Dim blnStatus As Boolean
            Select Case Status
                Case FunctionKeys.Show
                    blnStatus = True
                Case FunctionKeys.Hide
                    blnStatus = False
            End Select
            For i As Integer = 0 To Keys.Length - 1
                Keys(i).Visible = blnStatus
            Next i
        End Sub
#End Region

#Region " Send Email Methods"
        Public Function SendEmail(ByVal strTo As String, ByVal strFrom As String, ByVal strSubject As String, ByVal strBody As String) As Boolean
            Dim mmToSend As System.Net.Mail.MailMessage
            Dim mmClient As New Net.Mail.SmtpClient

            Try
                mmToSend = New Net.Mail.MailMessage(strFrom, strTo, strSubject, strBody)
                mmToSend.IsBodyHtml = True

                mmClient.Host = ConfigurationManager.AppSettings("SMTPServer")
                mmClient.Send(mmToSend)
            Catch ex As Exception
                Return False
            End Try

            Return True
        End Function
#End Region

#Region " RowFocus Methods"
        Public Function LastPixelPositionUpdate(ByVal pageName As String, ByVal rowNum As Integer) As Boolean
            Dim lastPixelPositionHash As Hashtable = SessionManager.LastPixelPosition
            If lastPixelPositionHash Is Nothing Then
                lastPixelPositionHash = New Hashtable
            End If

            If Not lastPixelPositionHash.ContainsKey(pageName) Then
                lastPixelPositionHash.Add(pageName, rowNum)
            Else
                lastPixelPositionHash(pageName) = rowNum
            End If

            SessionManager.LastPixelPosition = lastPixelPositionHash
            Return True
        End Function
        Public Function LastPixelPositionGet(ByVal pageName As String) As Integer
            Dim iReturn As Integer = 0
            If SessionManager.LastPixelPosition IsNot Nothing AndAlso SessionManager.LastPixelPosition.ContainsKey(pageName) Then
                iReturn = SessionManager.LastPixelPosition(pageName)
                SessionManager.LastPixelPosition.Remove(pageName)
            End If

            Return iReturn
        End Function
        Public Sub LastPixelPositionClear(ByVal pageName As String)
            If SessionManager.LastPixelPosition IsNot Nothing AndAlso SessionManager.LastPixelPosition.ContainsKey(pageName) Then
                SessionManager.LastPixelPosition.Remove(pageName)
            End If
        End Sub
#End Region

    End Module
End Namespace
