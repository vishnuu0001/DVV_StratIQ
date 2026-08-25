Imports AjaxControlToolkit
Imports System.Data
Imports System.Web
Imports System.Web.Services
Imports System.Web.Services.Protocols
Imports WebApp.APlus.DataAccess.Tables

Namespace WebApp.APlus.WebServices
    <System.Web.Script.Services.ScriptService()> _
    <WebService(Namespace:="http://tempuri.org/")> _
    <WebServiceBinding(ConformsTo:=WsiProfiles.BasicProfile1_1)> _
    Public Class AJAXMethods
        Inherits System.Web.Services.WebService

#Region " Anomaly Methods"
        <WebMethod(True)> _
        Public Function GetAnomlyTypeMaster(ByVal knownCategoryValues As String, ByVal category As String) As CascadingDropDownNameValue()
            Dim objDT As DataTable = AnomalyTypeMaster.SelectAnomalyTypeMaster()
            Dim values As New Generic.List(Of CascadingDropDownNameValue)

            For Each dtRow As DataRow In objDT.Rows
                values.Add(New CascadingDropDownNameValue(dtRow("AnomalyType").ToString, dtRow("AnomalyTypeID").ToString))
            Next
            Return values.ToArray
        End Function
        <WebMethod(True)> _
        Public Function GetKPISelectionList(ByVal knownCategoryValues As String, ByVal category As String) As CascadingDropDownNameValue()
            Dim sd As StringDictionary = CascadingDropDown.ParseKnownCategoryValuesString(knownCategoryValues)
            Dim iAnomalyTypeID As Integer = 0
            If (Not sd.ContainsKey("AnomalyType") OrElse Not Int32.TryParse(sd("AnomalyType"), iAnomalyTypeID)) Then
                Return Nothing
            End If

            Dim objDT As DataTable = AnomalyTypeMaster.SelectAnomalyTypeMasterByID(iAnomalyTypeID)
            Dim values As New Generic.List(Of CascadingDropDownNameValue)
            If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                Select Case objDT.Rows(0)("AnomalyType").ToString.ToUpper
                    Case "KPI DEVIATION"
                        objDT = KPIMaster.SelectKPISelectionList(SessionManager.UserID, SessionManager.WorkingSiteID)

                        For Each dtRow As DataRow In objDT.Rows
                            values.Add(New CascadingDropDownNameValue(dtRow("KPI").ToString, dtRow("KPIID").ToString))
                        Next
                    Case Else
                        'do nothing here
                End Select
            End If

            Return values.ToArray
        End Function
#End Region

#Region " Area Methods"
        <WebMethod(True)> _
        Public Function GetSiteMasterList(ByVal knownCategoryValues As String, ByVal category As String) As CascadingDropDownNameValue()
            Dim objDT As DataTable = SiteMaster.GetSiteMasterList
            Dim values As New Generic.List(Of CascadingDropDownNameValue)

            For Each dtRow As DataRow In objDT.Rows
                values.Add(New CascadingDropDownNameValue(dtRow("Site").ToString, dtRow("SiteID").ToString))
            Next
            Return values.ToArray
        End Function
        <WebMethod(True)> _
         Public Function GetAreaList(ByVal knownCategoryValues As String, ByVal category As String) As CascadingDropDownNameValue()
            Dim sd As StringDictionary = CascadingDropDown.ParseKnownCategoryValuesString(knownCategoryValues)
            Dim iSiteID As Integer = 0
            If (Not sd.ContainsKey("Site") OrElse Not Int32.TryParse(sd("Site"), iSiteID)) Then
                Return Nothing
            End If

            Dim values As New Generic.List(Of CascadingDropDownNameValue)
            If iSiteID > 0 Then
                Dim objDT As DataTable = AreaMaster.SelectAreaMasterList(iSiteID)
                If objDT IsNot Nothing AndAlso objDT.Rows.Count > 0 Then
                    For Each dtRow As DataRow In objDT.Rows
                        values.Add(New CascadingDropDownNameValue(dtRow("Area").ToString, dtRow("AreaID").ToString))
                    Next
                End If
            End If

            Return values.ToArray
        End Function
#End Region

    End Class
End Namespace