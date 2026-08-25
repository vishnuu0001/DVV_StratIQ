#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports System.Web.Security
Imports System.DirectoryServices
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.UI.CustomControls
Imports System.Collections.Generic

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class UserMaster6
        Inherits ApplicationBase

#Region " Constants"
        Private Shared ReadOnly FormName As String = "User Master"
        Private Shared ReadOnly ProgramName As String = "UserMaster6"
        Private Shared ReadOnly DBTableName As String = "UserMaster"
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel"}
            Dim OutMessageArr() As String = {"", ""}
            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event)")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
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

            Master.IconImage = Request.ApplicationPath + "/images/user1_preferences.gif"
            Master.HeaderMessage = FormName & " - " & SessionManager.UserADMode.Replace("Row", "") & " User"
            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                If SessionManager.UserADMode = "EditRow" Then
                    BindSite()
                    LoadSelectedRecord()
                Else
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserMaster5"), False)
                End If
            End If
        End Sub

        Private Sub btnCancel_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnCancel.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.UserADMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserMaster5"), False)
        End Sub

        Private Sub btnOK_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim blnSuccess As Boolean = UpdateUser()
            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.UserADMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserMaster5"), False)
            End If
        End Sub
#End Region

#Region " Bind Site"
        Private Sub BindSite()
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
                SiteMaster.SelectSiteMasterList(ddlSite)
                ddlSite.Items.Insert(0, " ")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindSite", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

#Region " Custom Functions"
        Private Function UpdateUser() As Boolean
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
                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.CompareDictionaryValues(SessionManager.RecordTransactionCurrentValues, objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                UserMaster.UpdateADUserMaster(txtUserID.Text.ToUpper.Trim(), ddlSite.SelectedItem.Value, txtLastName.Text.Trim(), txtFirstName.Text.Trim(), txtMiddleInitial.Text.Trim(), txtTitle.Text.Trim(), txtEmailAddress.Text.Trim(), ckActive.Checked)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, txtUserID.Text.ToUpper.Trim(), strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateADUser", Exc, SessionManager.UserID, ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function

        Private Sub LoadSelectedRecord()
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
                Dim dt As DataTable = UserMaster.SelectUserMaster(SessionManager.SelectedValue)
                If SessionManager.RecordTransactionCurrentValues IsNot Nothing Then
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RecordTransactionCurrentValues)
                End If
                If dt.Rows.Count <> 0 Then
                    Dim dr As DataRow = dt.Rows(0)
                    txtUserID.Text = dr.Item("UserID").ToString.Trim()
                    txtFirstName.Text = dr.Item("FirstName").ToString.Trim()
                    txtLastName.Text = dr.Item("LastName").ToString.Trim()
                    txtMiddleInitial.Text = dr.Item("MiddleInitial").ToString
                    txtTitle.Text = dr.Item("Title").ToString
                    txtEmailAddress.Text = dr.Item("EmailAddress").ToString

                    If dr.Item("Site").ToString.Trim.Length = 0 Then
                        ddlSite.SelectedIndex = -1
                    Else
                        Dim objItem As ListItem = ddlSite.Items.FindByValue(dr.Item("SiteID").ToString.Trim)
                        If Not objItem Is Nothing Then
                            objItem.Selected = True
                        End If
                    End If

                    ckActive.Checked = dr("Active")

                    Dim objDic As New Dictionary(Of String, String)
                    objDic.Add("FirstName", txtFirstName.Text.Trim())
                    objDic.Add("LastName", txtLastName.Text.Trim())
                    objDic.Add("MiddleInitial", txtMiddleInitial.Text.Trim())
                    objDic.Add("Site", ddlSite.SelectedItem.Text.Trim())
                    objDic.Add("Title", txtTitle.Text.Trim())
                    objDic.Add("EmailAddress", txtEmailAddress.Text.Trim())
                    objDic.Add("Active", ckActive.Checked)
                    SessionManager.RecordTransactionCurrentValues = objDic
                End If

                'now, fill in the AD information
                Dim objEntry As DirectoryEntry
                objEntry = ADAccess.GetADUser(txtUserID.Text)
                If Not IsNothing(objEntry) Then
                    Dim objProps As System.DirectoryServices.PropertyCollection
                    objProps = objEntry.Properties

                    If IsNothing(objProps("samaccountname").Value) Then
                        txtADUserID.Text = String.Empty
                    Else
                        txtADUserID.Text = objProps("samaccountname").Value.ToString()
                    End If
                    If IsNothing(objProps("givenname").Value) Then
                        txtADFirstName.Text = String.Empty
                    Else
                        txtADFirstName.Text = objProps("givenname").Value.ToString()
                    End If
                    If IsNothing(objProps("sn").Value) Then
                        txtADLastName.Text = String.Empty
                    Else
                        txtADLastName.Text = objProps("sn").Value.ToString()
                    End If
                    If IsNothing(objProps("initials").Value) Then
                        txtADMiddle.Text = String.Empty
                    Else
                        txtADMiddle.Text = objProps("initials").Value.ToString()
                    End If
                    If IsNothing(objProps("distinguishedname").Value) Then
                        txtADSite.Text = String.Empty
                    Else
                        Dim strholder As String = ADAccess.GetADSite(objProps("distinguishedname").Value.ToString())
                        If strholder.Trim.Length > 0 Then
                            txtADSite.Text = SiteMaster.GetSiteNameFromADSite(strholder)
                        Else
                            txtADSite.Text = String.Empty
                        End If
                    End If
                    If IsNothing(objProps("description").Value) Then
                        txtADTitle.Text = String.Empty
                    Else
                        txtADTitle.Text = objProps("description").Value.ToString()
                    End If
                    If IsNothing(objProps("userprincipalname").Value) Then
                        txtADEmail.Text = String.Empty
                    Else
                        txtADEmail.Text = objProps("userprincipalname").Value.ToString()
                    End If
                    Try
                        If Not IsNothing(objEntry.NativeObject.AccountDisabled) Then
                            ckADActive.Checked = Not objEntry.NativeObject.AccountDisabled
                        End If
                    Catch
                        ckADActive.Checked = True
                    End Try
                End If

                If txtFirstName.Text.ToUpper <> txtADFirstName.Text.ToUpper Then
                    lblDifFirstName.Visible = True
                End If
                If txtLastName.Text.ToUpper <> txtADLastName.Text.ToUpper Then
                    lblDifLastName.Visible = True
                End If
                If txtMiddleInitial.Text.ToUpper <> txtADMiddle.Text.ToUpper Then
                    lblDifMiddle.Visible = True
                End If
                If ddlSite.SelectedItem.Text.ToUpper <> txtADSite.Text.ToUpper Then
                    lblDifSite.Visible = True
                End If
                If txtEmailAddress.Text.ToUpper <> txtADEmail.Text.ToUpper Then
                    lblDifEmail.Visible = True
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord", Exc, SessionManager.UserID, ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

#Region " GetUpdatedValues"
        Private Function GetUpdatedValues() As Dictionary(Of String, String)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim objDic As New Dictionary(Of String, String)
            Try
                objDic.Add("FirstName", txtFirstName.Text.Trim())
                objDic.Add("LastName", txtLastName.Text.Trim())
                objDic.Add("MiddleInitial", txtMiddleInitial.Text.Trim())
                objDic.Add("Site", ddlSite.SelectedItem.Text.Trim())
                objDic.Add("Title", txtTitle.Text.Trim())
                objDic.Add("EmailAddress", txtEmailAddress.Text.Trim())
                objDic.Add("Active", ckActive.Checked)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - GetUpdatedValues", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
            Return objDic
        End Function
#End Region

    End Class
End Namespace
