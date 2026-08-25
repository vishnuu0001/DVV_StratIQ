#Region " Imports "
Imports System.ComponentModel
Imports System.Data
Imports System.Data.SqlClient
Imports System.IO
Imports System.Web
Imports System.Web.UI
Imports System.Web.UI.WebControls
Imports System.Web.UI.Design
Imports WebApp.APlus.DataAccess.Connections
Imports WebApp.APlus.DataAccess.Custom
#End Region

Namespace WebApp.APlus.UI.CustomControls

#Region " MasterControl Class "
    <ControlBuilder(GetType(MasterControlBuilder)), _
    ComponentModel.Designer(GetType(MasterControlDesigner))> Public Class MasterControl
        Inherits System.Web.UI.WebControls.WebControl

#Region " Members and Properties"

#Region " Private Members"
        Protected WithEvents _tblRows As Table
        Protected WithEvents _lblRows As New Label
        Protected WithEvents _grdInformation As New GridView
        Protected WithEvents _btnExit As New Button
        Protected WithEvents _btnAdd As New Button
        Protected WithEvents _btnExport As New Button
        Protected WithEvents _btnFunctionOne As New Button
        Protected WithEvents _ErrorControl As New ApplicationErrorControl
        Protected WithEvents _pnlButtons As New Panel

        Private _MaxRows As Integer = 0
        Private _AutoGenerateColumns As Boolean = False
        Private _BindData As Boolean = False
        Private _DataSource As DataView = Nothing
        Private _PrimaryControl As Boolean = True
        Private _CommandText As String
        Private _InitialSort As String = ""
        Private _InitialSortOrder As String = ""
        Private _FormName As String
        Private _ProgramName As String
        Private _RedirectProgramName As String = ""
        Private _ProgramMode As String = ""
        Private _NewLinkCaption As String
        Private _ShowView As Boolean = True
        Private _ShowEdit As Boolean = True
        Private _ShowDelete As Boolean = True
        Private _ShowAdd As Boolean = True
        Private _ShowExit As Boolean = True
        Private _ShowExport As Boolean = True
        Private _ShowFunctionButtonOne As Boolean = False
        Private _ViewLabel As String = "View"
        Private _EditLabel As String = "Edit"
        Private _DeleteLabel As String = "Delete"
        Private _FunctionButtonOneLabel As String = "Function Button One"
        Private _ExitURL As String
        Private _RaiseExitEvent As Boolean
        Private _RaiseExportEvent As Boolean
        Private _RaiseAddEvent As Boolean
        Private _StoredProcedureParams As New Hashtable
        Private _DataFilters As New ArrayList
        Private _Translate As Boolean
        Private _ConnectionString As String = ""
        Private _SaveSortOrder As Boolean = True
        Private _Fields As New MasterControlFields
        Private _AlternatingRows As Boolean = False
        Private _ShowRowCount As Boolean = False
        Private _UseScrollingColor As Boolean = True
        Private _ScrollingColor As System.Drawing.Color = Nothing
        Private _HideEmptyGrid As Boolean = False
#End Region

#Region " Public Properties"
        <PersistenceMode(PersistenceMode.InnerProperty), Browsable(False)> _
        Public ReadOnly Property GridColumns() As MasterControlFields
            Get
                Return _Fields
            End Get
        End Property
        Public Property MaxRows() As Integer
            Get
                Return _MaxRows
            End Get
            Set(ByVal value As Integer)
                _MaxRows = value
            End Set
        End Property
        Public Property DataSource() As DataView
            Get
                Return _DataSource
            End Get
            Set(ByVal value As DataView)
                _DataSource = value
            End Set
        End Property
        Public Property AlternatingRows() As Boolean
            Get
                Return _AlternatingRows
            End Get
            Set(ByVal value As Boolean)
                _AlternatingRows = value
            End Set
        End Property
        Public Property AutoGenerateColumns() As Boolean
            Get
                Return _AutoGenerateColumns
            End Get
            Set(ByVal value As Boolean)
                _AutoGenerateColumns = value
            End Set
        End Property
        Public Property ShowRowCount() As Boolean
            Get
                Return _ShowRowCount
            End Get
            Set(ByVal value As Boolean)
                _ShowRowCount = value
            End Set
        End Property
        Public Property SaveSortOrder() As Boolean
            Get
                Return _SaveSortOrder
            End Get
            Set(ByVal Value As Boolean)
                _SaveSortOrder = Value
            End Set
        End Property
        Public Property InitialSort() As String
            Get
                Return _InitialSort
            End Get
            Set(ByVal Value As String)
                _InitialSort = Value
            End Set
        End Property
        Public Property InitialSortOrder() As String
            Get
                Return _InitialSortOrder
            End Get
            Set(ByVal Value As String)
                _InitialSortOrder = Value
            End Set
        End Property
        Public Property Translate() As Boolean
            Get
                Return _Translate
            End Get
            Set(ByVal Value As Boolean)
                _Translate = Value
            End Set
        End Property
        Public Property ConnectionString() As String
            Get
                Return _ConnectionString
            End Get
            Set(ByVal Value As String)
                _ConnectionString = Value
            End Set
        End Property
        Public Property ShowView() As Boolean
            Get
                Return _ShowView
            End Get
            Set(ByVal Value As Boolean)
                _ShowView = Value
            End Set
        End Property
        Public Property ShowEdit() As Boolean
            Get
                Return _ShowEdit
            End Get
            Set(ByVal Value As Boolean)
                _ShowEdit = Value
            End Set
        End Property
        Public Property ShowDelete() As Boolean
            Get
                Return _ShowDelete
            End Get
            Set(ByVal Value As Boolean)
                _ShowDelete = Value
            End Set
        End Property
        Public Property ShowAdd() As Boolean
            Get
                Return _ShowAdd
            End Get
            Set(ByVal Value As Boolean)
                _ShowAdd = Value
            End Set
        End Property
        Public Property ShowExit() As Boolean
            Get
                Return _ShowExit
            End Get
            Set(ByVal Value As Boolean)
                _ShowExit = Value
            End Set
        End Property
        Public Property ShowExport() As Boolean
            Get
                Return _ShowExport
            End Get
            Set(ByVal Value As Boolean)
                _ShowExport = Value
            End Set
        End Property
        Public Property ShowFunctionButtonOne() As Boolean
            Get
                Return _ShowFunctionButtonOne
            End Get
            Set(ByVal value As Boolean)
                _ShowFunctionButtonOne = value
            End Set
        End Property
        Public Property FormName() As String
            Get
                Return _FormName
            End Get
            Set(ByVal Value As String)
                _FormName = Value
            End Set
        End Property
        Public Property ProgramName() As String
            Get
                Return _ProgramName
            End Get
            Set(ByVal Value As String)
                _ProgramName = Value
            End Set
        End Property
        Public Property ProgramMode() As String
            Get
                Return _ProgramMode
            End Get
            Set(ByVal Value As String)
                _ProgramMode = Value
            End Set
        End Property
        Public Property NewLinkCaption() As String
            Get
                Return _NewLinkCaption
            End Get
            Set(ByVal Value As String)
                _NewLinkCaption = Value
            End Set
        End Property
        Public Property RedirectProgramName() As String
            Get
                Return _RedirectProgramName
            End Get
            Set(ByVal Value As String)
                _RedirectProgramName = Value
            End Set
        End Property
        Public Property CommandText() As String
            Get
                Return _CommandText
            End Get
            Set(ByVal Value As String)
                _CommandText = Value
            End Set
        End Property
        Public Property ExitURL() As String
            Get
                Return _ExitURL
            End Get
            Set(ByVal Value As String)
                _ExitURL = Value
            End Set
        End Property
        Public Property ViewLabel() As String
            Get
                Return _ViewLabel
            End Get
            Set(ByVal Value As String)
                _ViewLabel = Value
            End Set
        End Property
        Public Property EditLabel() As String
            Get
                Return _EditLabel
            End Get
            Set(ByVal Value As String)
                _EditLabel = Value
            End Set
        End Property
        Public Property DeleteLabel() As String
            Get
                Return _DeleteLabel
            End Get
            Set(ByVal Value As String)
                _DeleteLabel = Value
            End Set
        End Property
        Public Property FunctionButtonOneLabel() As String
            Get
                Return _FunctionButtonOneLabel
            End Get
            Set(ByVal value As String)
                _FunctionButtonOneLabel = value
            End Set
        End Property
        Public Property RaiseExitEvent() As Boolean
            Get
                Return _RaiseExitEvent
            End Get
            Set(ByVal Value As Boolean)
                _RaiseExitEvent = Value
            End Set
        End Property
        Public Property RaiseExportEvent() As Boolean
            Get
                Return _RaiseExportEvent
            End Get
            Set(ByVal value As Boolean)
                _RaiseExportEvent = value
            End Set
        End Property
        Public Property RaiseAddEvent() As Boolean
            Get
                Return _RaiseAddEvent
            End Get
            Set(ByVal Value As Boolean)
                _RaiseAddEvent = Value
            End Set
        End Property
        Public ReadOnly Property StoredProcedureParams() As Hashtable
            Get
                Return _StoredProcedureParams
            End Get
        End Property
        Public ReadOnly Property DataFilters() As ArrayList
            Get
                Return _DataFilters
            End Get
        End Property
        Public ReadOnly Property ExitButtonID() As String
            Get
                Return _btnExit.UniqueID
            End Get
        End Property
        Public ReadOnly Property AddButton() As Button
            Get
                Return _btnAdd
            End Get
        End Property
        Public ReadOnly Property AddButtonID() As String
            Get
                Return _btnAdd.UniqueID
            End Get
        End Property
        Public ReadOnly Property FunctionButtonOne() As Button
            Get
                Return _btnFunctionOne
            End Get
        End Property
        Public ReadOnly Property FunctionButtonOneID() As String
            Get
                Return _btnFunctionOne.UniqueID
            End Get
        End Property
        Public ReadOnly Property Rows() As GridViewRowCollection
            Get
                Return _grdInformation.Rows
            End Get
        End Property
        Public ReadOnly Property MasterControlGrid() As GridView
            Get
                Return _grdInformation
            End Get
        End Property
        Public Property PrimaryControl() As Boolean
            Get
                Return _PrimaryControl
            End Get
            Set(ByVal value As Boolean)
                _PrimaryControl = value
            End Set
        End Property
        Public Property UseScrollingColor() As Boolean
            Get
                Return _UseScrollingColor
            End Get
            Set(ByVal value As Boolean)
                _UseScrollingColor = value
            End Set
        End Property
        Public Property ScrollingColor() As System.Drawing.Color
            Get
                If _ScrollingColor = Nothing Then
                    Return Drawing.Color.LightGray
                Else
                    Return _ScrollingColor
                End If
            End Get
            Set(ByVal value As System.Drawing.Color)
                _ScrollingColor = value
            End Set
        End Property
        Public ReadOnly Property ExportButton() As Button
            Get
                Return _btnExport
            End Get
        End Property
        Public ReadOnly Property ExportButtonID() As String
            Get
                Return _btnExport.UniqueID
            End Get
        End Property
        Public Property HideEmptyGrid() As Boolean
            Get
                Return _HideEmptyGrid
            End Get
            Set(ByVal value As Boolean)
                _HideEmptyGrid = value
            End Set
        End Property
#End Region

#End Region

#Region " Public Events"
        Public Event ExitClick(ByVal sender As System.Object, ByVal e As System.EventArgs)
        Public Event ExportClick(ByVal sender As System.Object, ByVal e As System.EventArgs)
        Public Event AddClick(ByVal sender As System.Object, ByVal e As System.EventArgs)
        Public Event FunctionButtonOneClick(ByVal sender As System.Object, ByVal e As System.EventArgs)
        Public Event onRowCommand(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewCommandEventArgs)
        Public Event onRowDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewRowEventArgs)
        Public Event Sorted(ByVal sender As Object, e As System.EventArgs)
#End Region

#Region " Event Handlers"
        Private Sub MasterControl_PreRender(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.PreRender
            Dim objLink As New HtmlLink()
            objLink.ID = "MasterControlCSS"
            objLink.Attributes.Add("type", "text/css")
            objLink.Attributes.Add("rel", "stylesheet")
            objLink.Attributes.Add("href", "~/Styles/MasterControlStyle.css")
            Dim CssLinkAlreadyExists As Boolean = False
            For Each headctrl As Control In Page.Header.Controls
                If (headctrl.ID = objLink.ID) Then
                    CssLinkAlreadyExists = True
                    Exit For
                End If
            Next
            If Not CssLinkAlreadyExists Then
                Page.Header.Controls.AddAt(0, objLink)
            End If
        End Sub
        Private Sub MasterControl_Init(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.Init
            Controls.Clear()

            BorderStyle = Web.UI.WebControls.BorderStyle.None
            Width = New Unit("100%")

            If _ShowRowCount Then
                _tblRows = New Table
                _tblRows.CssClass = "rowCount_table"

                Dim oRow As New TableRow
                Dim oCell As New TableCell

                _lblRows.ID = "lblRecords"
                oCell.Controls.Add(_lblRows)
                oRow.Cells.Add(oCell)

                oRow.CssClass = "rowCount_row"
                _tblRows.Rows.Add(oRow)
            End If

            If _PrimaryControl Then
                _pnlButtons = New Panel
                Dim objCTL As HtmlGenericControl

                objCTL = New HtmlGenericControl
                objCTL.InnerHtml = "<BR />"
                _pnlButtons.Controls.Add(objCTL)

                If _ShowExit Then
                    _btnExit.ID = "btnExit"
                    _btnExit.CssClass = "Button_Default"
                    _btnExit.Text = "Exit"
                    _btnExit.CausesValidation = False
                    _pnlButtons.Controls.Add(_btnExit)

                    objCTL = New HtmlGenericControl
                    objCTL.InnerHtml = "&nbsp;&nbsp;"
                    _pnlButtons.Controls.Add(objCTL)
                End If

                If _ShowAdd Then
                    _btnAdd.ID = "btnAdd"
                    _btnAdd.CssClass = "Button_Variable"
                    _btnAdd.Text = "New..."
                    _btnAdd.CausesValidation = False
                    _pnlButtons.Controls.Add(_btnAdd)

                    objCTL = New HtmlGenericControl
                    objCTL.InnerHtml = "&nbsp;&nbsp;"
                    _pnlButtons.Controls.Add(objCTL)
                End If

                If _ShowExport Then
                    _btnExport.ID = "btnExport"
                    _btnExport.CssClass = "Button_Default"
                    _btnExport.Text = "Export"
                    _btnExport.CausesValidation = False
                    _pnlButtons.Controls.Add(_btnExport)
                    _btnExport.Attributes.Add("onclick", "DisableWaitPanel()")

                    objCTL = New HtmlGenericControl
                    objCTL.InnerHtml = "&nbsp;&nbsp;"
                    _pnlButtons.Controls.Add(objCTL)
                End If

                If _ShowFunctionButtonOne Then
                    _btnFunctionOne.ID = "btnFunctionOne"
                    _btnFunctionOne.CssClass = "Button_Variable"
                    _btnFunctionOne.Text = "Function Button One"
                    _btnFunctionOne.CausesValidation = False
                    _pnlButtons.Controls.Add(_btnFunctionOne)
                End If

                objCTL = New HtmlGenericControl
                objCTL.InnerHtml = "<BR /><BR />"
                _pnlButtons.Controls.Add(objCTL)
            End If

            If _ShowRowCount Then
                _lblRows.Text = "Loading Data..."
                Controls.Add(_tblRows)
            End If

            Controls.Add(_grdInformation)
            If _PrimaryControl Then
                Controls.Add(_pnlButtons)
                Controls.Add(_ErrorControl)
            End If
        End Sub
        Protected Sub Page_Load(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.Load
            _grdInformation.EmptyDataRowStyle.CssClass = "emptyStyle"
            If _Translate Then
                _grdInformation.EmptyDataText = GetTranslationString("No records exist")
            Else
                _grdInformation.EmptyDataText = "No records exist"
            End If

            If Not Page.IsPostBack Then
                HttpContext.Current.Session.Remove("MasterControlDataTable")

                _grdInformation.Width = New Unit("100%")
                _grdInformation.GridLines = Web.UI.WebControls.GridLines.Vertical
                _grdInformation.AutoGenerateColumns = False
                _grdInformation.AllowSorting = True
                _grdInformation.CssClass = "tablestyle"
                _grdInformation.RowStyle.CssClass = "rowstyle"
                If _AlternatingRows Then
                    _grdInformation.AlternatingRowStyle.CssClass = "altrowstyle"
                End If
                _grdInformation.SelectedRowStyle.CssClass = "selectedRowStyle"
                _grdInformation.HeaderStyle.CssClass = "headerstyle"
                _grdInformation.EnableViewState = True

                Dim dkList As String = ""
                Dim strField As String = ""
                For Each bf As DataControlField In _Fields
                    strField = ""

                    Select Case bf.GetType.Name
                        Case "BoundField", "MasterControlField"
                            If CType(bf, BoundField).DataField.ToString.Trim.Length > 0 Then
                                strField = CType(bf, BoundField).DataField.ToString.Trim
                            End If
                        Case "ButtonField"
                            If CType(bf, ButtonField).DataTextField.ToString.Trim.Length > 0 Then
                                strField = CType(bf, ButtonField).DataTextField.ToString.Trim
                            End If
                    End Select

                    If strField.Trim.Length > 0 Then
                        If dkList.Trim.Length > 0 Then dkList += ","

                        dkList += strField
                    End If

                    If _Translate Then
                        bf.HeaderText = GetTranslationString(bf.HeaderText)
                    End If
                    _grdInformation.Columns.Add(CType(bf, DataControlField))
                Next
                _grdInformation.DataKeyNames = dkList.Split(",")

                If _RedirectProgramName.Trim.Length > 0 AndAlso ProgramSecurity.CanUserAccessProgram(SessionManager.UserID, _RedirectProgramName) Then
                    'good
                Else
                    _ShowView = False
                    _ShowEdit = False
                    _ShowDelete = False
                    _ShowAdd = False
                End If

                _ShowAdd = _ShowAdd AndAlso SessionManager.AllowMaintenanceAdd
                _ShowEdit = _ShowEdit AndAlso SessionManager.AllowMaintenanceEdit
                _ShowDelete = _ShowDelete AndAlso SessionManager.AllowMaintenanceDelete

                Dim objField As ButtonField

                If _ShowView Then
                    objField = New ButtonField
                    objField.CommandName = "ViewRow"
                    objField.ControlStyle.CssClass = "Link_Default"
                    objField.CausesValidation = False
                    objField.ItemStyle.HorizontalAlign = Web.UI.WebControls.HorizontalAlign.Left
                    objField.ItemStyle.ForeColor = Drawing.Color.Blue

                    If _Translate Then
                        _ViewLabel = GetTranslationString(_ViewLabel)
                    End If

                    objField.Text = _ViewLabel
                    _grdInformation.Columns.Add(objField)
                End If
                If _ShowEdit Then
                    objField = New ButtonField
                    objField.CommandName = "EditRow"
                    objField.ControlStyle.CssClass = "Link_Default"
                    objField.CausesValidation = False
                    objField.ItemStyle.HorizontalAlign = Web.UI.WebControls.HorizontalAlign.Left
                    objField.ItemStyle.ForeColor = Drawing.Color.Blue

                    If _Translate Then
                        _EditLabel = GetTranslationString(_EditLabel)
                    End If

                    objField.Text = _EditLabel
                    _grdInformation.Columns.Add(objField)
                End If
                If _ShowDelete Then
                    objField = New ButtonField
                    objField.CommandName = "DeleteRow"
                    objField.ControlStyle.CssClass = "Link_Default"
                    objField.CausesValidation = False
                    objField.ItemStyle.HorizontalAlign = Web.UI.WebControls.HorizontalAlign.Left
                    objField.ItemStyle.ForeColor = Drawing.Color.Blue

                    If _Translate Then
                        _DeleteLabel = GetTranslationString(_DeleteLabel)
                    End If

                    objField.Text = _DeleteLabel
                    _grdInformation.Columns.Add(objField)
                End If

                'Buttons
                If _ShowExit Then
                    If _Translate Then
                        _btnExit.Text = GetTranslationString(_btnExit.Text)
                    End If
                Else
                    _btnExit.Visible = False
                End If
                If _ShowAdd Then
                    _btnAdd.Visible = True

                    If _Translate Then
                        _btnAdd.Text = GetTranslationString("New") & " " & GetTranslationString(_NewLinkCaption)
                    Else
                        _btnAdd.Text = "New " & _NewLinkCaption
                    End If
                Else
                    _btnAdd.Visible = False
                End If
                If _ShowExport Then
                    If _Translate Then
                        _btnExport.Text = GetTranslationString(_btnExport.Text)
                    End If
                Else
                    _btnExport.Visible = False
                End If
                If _ShowFunctionButtonOne Then
                    _btnFunctionOne.Visible = True
                    _btnFunctionOne.Text = GetTranslationString(_FunctionButtonOneLabel)
                Else
                    _btnFunctionOne.Visible = False
                End If
            End If

            If _BindData Then
                BindDataGrid(True)

                _BindData = False
            End If
        End Sub
        Private Sub _grdInformation_RowDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewRowEventArgs) Handles _grdInformation.RowDataBound
            Try
                If e.Row.RowType = DataControlRowType.Header Then
                    If (ViewState("sortdirection") IsNot Nothing AndAlso Not String.IsNullOrEmpty(ViewState("sortdirection"))) AndAlso (ViewState("sortfield") IsNot Nothing AndAlso Not String.IsNullOrEmpty(ViewState("sortfield"))) Then
                        Dim cellIndex As Integer = -1
                        For Each field As DataControlField In _grdInformation.Columns
                            If field.SortExpression = ViewState("sortfield") Then
                                cellIndex = _grdInformation.Columns.IndexOf(field)

                                Exit For
                            End If
                        Next
                        If cellIndex > -1 Then
                            Dim strClass As String = ""

                            If ViewState("sortdirection").ToString.Trim.ToUpper = "ASC" Then
                                strClass = " sortascheader"
                            Else
                                strClass = " sortdescheader"
                            End If

                            e.Row.Cells(cellIndex).CssClass += strClass
                        End If
                    End If
                End If

                If e.Row.RowType = DataControlRowType.DataRow Then
                    If _UseScrollingColor = True Then
                        e.Row.Attributes.Add("onmouseover", "this.originalstyle=this.style.backgroundColor;this.style.backgroundColor='" & System.Drawing.ColorTranslator.ToHtml(Drawing.Color.FromArgb(ScrollingColor.ToArgb)) & "';")
                        e.Row.Attributes.Add("onmouseout", "this.style.backgroundColor=this.originalstyle;")
                    End If

                    Dim objField As MasterControlField = Nothing
                    For i As Integer = 0 To e.Row.Cells.Count - 1
                        If i <= _Fields.Count - 1 Then
                            objField = CType(_Fields(i), UI.CustomControls.MasterControlField)
                            If objField IsNot Nothing AndAlso objField.ShowReturns Then
                                e.Row.Cells(i).Text = e.Row.Cells(i).Text.Replace(vbCr, "<BR>")
                            End If
                        End If
                    Next
                End If
            Catch Exc As Exception
                'don't do anything here
            End Try

            RaiseEvent onRowDataBound(sender, e)
        End Sub
        Protected Sub Page_Unload(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.Unload
            MyBase.Dispose()
        End Sub
        Private Sub _btnAdd_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles _btnAdd.Click
            If SessionManager.UserID <> "" Then
                If _RaiseAddEvent Then
                    RaiseEvent AddClick(sender, e)
                Else
                    If _ProgramMode.Trim.Length > 0 Then
                        HttpContext.Current.Session(_ProgramMode) = "AddRow"
                    Else
                        SessionManager.Mode = "AddRow"
                    End If

                    HttpContext.Current.Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar + (ProgramSecurity.GetProgramURL(_RedirectProgramName)))
                End If
            End If
        End Sub
        Private Sub _btnExit_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles _btnExit.Click
            If _RaiseExitEvent Then
                RaiseEvent ExitClick(sender, e)
            Else
                ControlExit()
            End If
        End Sub
        Private Sub _btnExport_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles _btnExport.Click
            If _RaiseExportEvent Then
                RaiseEvent ExportClick(sender, e)
            Else
                Try
                    BindDataGrid(False)

                    Dim stringWrite As New System.IO.StringWriter
                    Dim htmlWrite As New System.Web.UI.HtmlTextWriter(stringWrite)
                    Dim dv As DataView = CType(_grdInformation.DataSource, DataView)
                    Dim dg As New DataGrid
                    dg.HeaderStyle.HorizontalAlign = HorizontalAlign.Left
                    dg.HeaderStyle.VerticalAlign = VerticalAlign.Top
                    dg.HeaderStyle.Font.Bold = True
                    dg.ItemStyle.VerticalAlign = VerticalAlign.Top
                    dg.ItemStyle.HorizontalAlign = HorizontalAlign.Left
                    If dv.Table.Rows.Count < 1 Then Exit Sub

                    dg.DataSource = dv
                    dg.DataBind()
                    dg.RenderControl(htmlWrite)

                    SessionManager.ExportString = stringWrite.ToString

                    HttpContext.Current.Response.Redirect(HttpContext.Current.Request.ApplicationPath.ToString + "/UI/UserControls/Export.aspx")
                Catch Exc As Exception
                    Throw
                End Try
            End If
        End Sub
        Private Sub _btnFunctionOne_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles _btnFunctionOne.Click
            RaiseEvent FunctionButtonOneClick(sender, e)
        End Sub
        Private Sub _grdInformation_RowCommand(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewCommandEventArgs) Handles _grdInformation.RowCommand
            RaiseEvent onRowCommand(sender, e)
        End Sub
        Private Sub _grdInformation_Sorting(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewSortEventArgs) Handles _grdInformation.Sorting
            If Not ViewState("sortfield") Is Nothing AndAlso ViewState("sortfield").ToString <> e.SortExpression Then
                ViewState("sortdirection") = "DESC"
            ElseIf ViewState("sortfield") Is Nothing OrElse ViewState("sortfield").ToString = "" Then
                ViewState("sortdirection") = "DESC"
            End If

            ViewState.Add("sortfield", e.SortExpression)

            'Sort Toggle
            If ViewState("sortdirection") = "ASC" Then
                ViewState("sortdirection") = "DESC"
            Else
                ViewState("sortdirection") = "ASC"
            End If

            If _SaveSortOrder Then
                Dim objh As Hashtable

                If Not SessionManager.SavedSortOrders Is Nothing Then
                    objh = CType(SessionManager.SavedSortOrders, Hashtable)
                    objh.Remove(SessionManager.CurrentProgramURL)
                Else
                    objh = New Hashtable
                End If

                objh.Add(SessionManager.CurrentProgramURL, e.SortExpression + "~" + ViewState("sortdirection"))
                SessionManager.SavedSortOrders = objh
            End If

            BindDataGrid(False)
        End Sub
        Private Sub _grdInformation_Sorted(sender As Object, e As System.EventArgs) Handles _grdInformation.Sorted
            RaiseEvent Sorted(sender, e)
        End Sub
#End Region

#Region " Custom Methods"
        Public Overrides Sub DataBind()
            If _grdInformation.Columns.Count = 0 Then
                _BindData = True
            Else
                BindDataGrid(False)
            End If
        End Sub
        Public Overloads Sub DataBind(ByVal passForceRefresh As Boolean)
            If _grdInformation.Columns.Count = 0 Then
                _BindData = True
            Else
                BindDataGrid(True)
            End If
        End Sub
        Friend Sub BindDataGrid(ByVal passForceRefresh As Boolean)
            _grdInformation.PageIndex = 0

            Dim strSortField As String = ""
            Dim strSortDirection As String = ""
            Dim cm As New SqlClient.SqlCommand
            Dim dtView As DataView

            Try
                'get the sort information first
                If _SaveSortOrder Then
                    'determine if we have saved sort information
                    If SessionManager.SavedSortOrders IsNot Nothing AndAlso SessionManager.SavedSortOrders.Count > 0 Then
                        Dim objh As Hashtable
                        objh = CType(SessionManager.SavedSortOrders, Hashtable)
                        If objh.ContainsKey(SessionManager.CurrentProgramURL) Then
                            Dim strholder As String() = objh(SessionManager.CurrentProgramURL).ToString.Split("~")
                            strSortField = strholder(0)
                            strSortDirection = strholder(1)
                        Else
                            If ViewState("sortfield") Is Nothing Then
                                ViewState.Add("sortdirection", "ASC")
                            Else
                                strSortField = ViewState("sortfield")
                                strSortDirection = ViewState("sortdirection")
                            End If
                        End If
                    Else
                        If ViewState("sortfield") Is Nothing OrElse ViewState("sortfield").ToString.Trim.Length = 0 Then
                            ViewState.Add("sortfield", _InitialSort)
                            If _InitialSortOrder.Trim.Length = 0 Then
                                _InitialSortOrder = "ASC"
                            End If
                            ViewState.Add("sortdirection", _InitialSortOrder)

                            strSortField = _InitialSort
                            strSortDirection = _InitialSortOrder
                        Else
                            strSortField = ViewState("sortfield")
                            strSortDirection = ViewState("sortdirection")
                        End If
                    End If
                Else
                    If ViewState("sortfield") Is Nothing OrElse ViewState("sortfield").ToString.Trim.Length = 0 Then
                        ViewState.Add("sortfield", _InitialSort)
                        ViewState.Add("sortdirection", _InitialSortOrder)

                        strSortField = _InitialSort
                        strSortDirection = _InitialSortOrder
                    Else
                        strSortField = ViewState("sortfield")
                        strSortDirection = ViewState("sortdirection")
                    End If
                End If

                If Not passForceRefresh AndAlso HttpContext.Current.Session("MasterControlDataTable") IsNot Nothing AndAlso _
                TypeOf HttpContext.Current.Session("MasterControlDataTable") Is DataTable AndAlso DirectCast(HttpContext.Current.Session("MasterControlDataTable"), DataTable).Rows.Count > 0 Then
                    dtView = DirectCast(HttpContext.Current.Session("MasterControlDataTable"), DataTable).DefaultView
                ElseIf _DataSource IsNot Nothing Then
                    dtView = _DataSource
                Else
                    Dim objDT As New DataTable

                    cm.Parameters.Clear()
                    cm.CommandText = _CommandText
                    cm.CommandType = System.Data.CommandType.StoredProcedure
                    If _ConnectionString.Trim.Length > 0 Then
                        cm.Connection = New SqlConnection(_ConnectionString)
                        cm.Connection.Open()
                    Else
                        cm.Connection = New ApplicationConnection().OpenConnection(Nothing)
                    End If

                    Dim param As SqlParameter
                    If _StoredProcedureParams.Count > 0 Then
                        Dim myEnumerator As IDictionaryEnumerator = _StoredProcedureParams.GetEnumerator()
                        While myEnumerator.MoveNext
                            param = New SqlParameter(myEnumerator.Key.ToString, myEnumerator.Value)
                            If Not cm.Parameters.Contains(param) Then
                                cm.Parameters.Add(param)
                            End If
                        End While
                    End If

                    Dim da As New SqlClient.SqlDataAdapter(cm)

                    da.Fill(objDT)
                    dtView = objDT.DefaultView
                End If

                If _DataFilters.Count > 0 Then
                    If _Translate Then
                        _grdInformation.EmptyDataText = GetTranslationString("No records exist for filtered data")
                    Else
                        _grdInformation.EmptyDataText = "No records exist for filtered data"
                    End If

                    Dim strFilter As String = ""

                    Dim myEnumerator As IEnumerator = _DataFilters.GetEnumerator()
                    While myEnumerator.MoveNext
                        If strFilter.Trim.Length > 0 Then
                            strFilter += " AND "
                        End If

                        strFilter += myEnumerator.Current.ToString
                    End While

                    dtView.RowFilter = strFilter
                End If

                If strSortField.Trim.Length > 0 Then
                    If strSortField.IndexOf("|") > -1 Then
                        Dim strFields() As String = strSortField.Split("|")
                        Dim strSortCommand As String = ""
                        For icounter As Integer = 0 To strFields.Length - 1
                            If strSortCommand.Trim.Length > 0 Then
                                strSortCommand += ", "
                            End If
                            strSortCommand += strFields(icounter)
                            If icounter = 0 Then
                                strSortCommand += " " + strSortDirection
                            Else
                                strSortCommand += " ASC"
                            End If
                        Next

                        dtView.Sort = strSortCommand
                    Else
                        dtView.Sort = strSortField + " " + strSortDirection
                    End If
                End If

                If _ShowAdd OrElse _ShowExit OrElse _ShowExport OrElse _ShowFunctionButtonOne Then
                    _pnlButtons.Visible = True
                Else
                    _pnlButtons.Visible = False
                End If

                If _ShowExport Then
                    If dtView.Count > 0 Then
                        _btnExport.Visible = True
                    Else
                        _btnExport.Visible = False
                    End If
                End If

                cm.Parameters.Clear()

                If _AutoGenerateColumns Then
                    _grdInformation.Columns.Clear()

                    Dim dkList As String = ""
                    Dim objField As BoundField

                    For Each objCol As DataColumn In dtView.Table.Columns
                        objField = New BoundField
                        objField.HeaderText = objCol.ColumnName
                        objField.DataField = objCol.ColumnName
                        objField.SortExpression = objCol.ColumnName

                        If dkList.Trim.Length > 0 Then dkList += ","
                        dkList += objField.DataField.ToString

                        _grdInformation.Columns.Add(objField)
                    Next

                    _grdInformation.DataKeyNames = dkList.Split(",")
                End If

                If _MaxRows > 0 Then
                    If dtView.Count > _MaxRows Then
                        Dim dtCol As New DataColumn("FilterRowIndex", Type.GetType("System.Int32"))
                        dtView.Table.Columns.Add(dtCol)

                        Dim iRowCount As Integer = dtView.Count
                        Dim iRowCounter As Integer = 0
                        Do While iRowCounter <= _MaxRows
                            dtView(iRowCounter)("FilterRowIndex") = iRowCounter + 1
                            iRowCounter += 1
                        Loop

                        Dim strFilter As String = "FilterRowIndex < " & (_MaxRows + 1).ToString
                        If dtView.RowFilter.Trim.Length > 0 Then
                            strFilter = dtView.RowFilter & " AND " & strFilter
                        End If

                        dtView.RowFilter = strFilter

                        If _ShowRowCount AndAlso dtView.Count >= 0 Then
                            _lblRows.Text = dtView.Count.ToString + " records returned (filtered of " & iRowCount & ")"
                        End If
                    Else
                        If _ShowRowCount AndAlso dtView.Count >= 0 Then
                            _lblRows.Text = dtView.Count.ToString + " records returned"
                        End If
                    End If
                Else
                    If _ShowRowCount AndAlso dtView.Count >= 0 Then
                        _lblRows.Text = dtView.Count.ToString + " records returned"
                    End If
                End If

                If dtView.Count <= 1 Then
                    UseScrollingColor = False
                End If

                If dtView.Count = 0 AndAlso _HideEmptyGrid Then
                    'don't bind and hide button panel
                    _pnlButtons.Visible = False
                Else
                    _grdInformation.DataSource = dtView
                    _grdInformation.DataBind()
                End If

                HttpContext.Current.Session("MasterControlDataTable") = dtView.Table
            Catch Exc As Exception
                _ErrorControl.DisplayErrors("ApplicationMasterControl" & " - BindDataGrid - " & _CommandText, Exc, SessionManager.UserID, ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            Finally
                If cm.Connection IsNot Nothing Then
                    cm.Connection.Close()
                End If
                cm.Dispose()
            End Try
        End Sub
        Public Sub ControlExit()
            If SessionManager.MasterControlExitProgram <> String.Empty Then
                Dim strExitProgram As String = SessionManager.MasterControlExitProgram
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.MasterControlExitProgram)
                HttpContext.Current.Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strExitProgram))
            End If

            If _ExitURL = "" Then
                HttpContext.Current.Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & (ProgramSecurity.GetProgramURL(SessionManager.CurrentMenuProgram)))
            Else
                HttpContext.Current.Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar + (_ExitURL))
            End If
        End Sub
#End Region

    End Class
#End Region

#Region " MasterControlDesigner Class "
    Public Class MasterControlDesigner
        Inherits ControlDesigner

        Public Overrides Function GetDesignTimeHtml() As String
            'Retrieve the controls so that they are created
            Dim objControl As MasterControl = CType(Component, MasterControl)
            Dim strHolder As String

            If objControl.GridColumns.Count > 0 Then
                Dim objTable As New Table
                Dim objRow As TableRow
                Dim objCell As TableCell

                objTable.Width = New Unit("100%")
                objTable.GridLines = GridLines.None
                objTable.CellSpacing = 1
                objTable.CellPadding = 3
                objTable.BorderColor = Drawing.ColorTranslator.FromHtml("#FFFFFF")
                objTable.BorderWidth = New Unit(2, UnitType.Pixel)
                objTable.BorderStyle = Web.UI.WebControls.BorderStyle.Ridge

                'Header
                objRow = New TableRow
                objRow.VerticalAlign = VerticalAlign.Top
                objRow.HorizontalAlign = HorizontalAlign.Left
                objRow.Font.Size = New FontUnit(11, UnitType.Pixel)
                objRow.Font.Bold = True
                objRow.ForeColor = Drawing.ColorTranslator.FromHtml("#FFFFFF")
                objRow.BackColor = Drawing.ColorTranslator.FromHtml("#41519A")

                For Each bf As MasterControlField In objControl.GridColumns
                    If bf.Visible Then
                        objCell = New TableCell
                        objCell.Text = bf.ToString
                        objRow.Cells.Add(objCell)
                    End If
                Next

                'add edit rows
                If objControl.ShowView Then
                    objCell = New TableCell
                    objRow.Cells.Add(objCell)
                End If
                If objControl.ShowEdit Then
                    objCell = New TableCell
                    objRow.Cells.Add(objCell)
                End If
                If objControl.ShowDelete Then
                    objCell = New TableCell
                    objRow.Cells.Add(objCell)
                End If

                objTable.Rows.Add(objRow)

                'add a blank data row
                objRow = New TableRow
                objRow.VerticalAlign = VerticalAlign.Top
                objRow.HorizontalAlign = HorizontalAlign.Left
                objRow.Font.Size = New FontUnit(11, UnitType.Pixel)
                objRow.ForeColor = Drawing.Color.Black
                objRow.ForeColor = Drawing.ColorTranslator.FromHtml("#000000")
                objRow.BackColor = Drawing.ColorTranslator.FromHtml("#f5f5f5")

                For Each bf As MasterControlField In objControl.GridColumns
                    If bf.Visible Then
                        objCell = New TableCell
                        objCell.Text = "&nbsp;"
                        objRow.Cells.Add(objCell)
                    End If
                Next
                'add edit rows
                If objControl.ShowView Then
                    objCell = New TableCell
                    objCell.Text = objControl.ViewLabel
                    objRow.Cells.Add(objCell)
                End If
                If objControl.ShowEdit Then
                    objCell = New TableCell
                    objCell.Text = objControl.EditLabel
                    objRow.Cells.Add(objCell)
                End If
                If objControl.ShowDelete Then
                    objCell = New TableCell
                    objCell.Text = objControl.DeleteLabel
                    objRow.Cells.Add(objCell)
                End If
                objTable.Rows.Add(objRow)

                Dim writer As New System.IO.StringWriter()
                Dim html As New HtmlTextWriter(writer)

                objTable.RenderControl(html)
                strHolder = writer.ToString
                strHolder += "<br/><br/>"

                If objControl.ShowExit Then
                    strHolder += "<input type=button value=Exit style=""BORDER-RIGHT: darkgray 1px solid;BORDER-TOP: darkgray 1px solid;FONT-SIZE: 8pt;	BORDER-LEFT: darkgray 1px solid;WIDTH: 80px;BORDER-BOTTOM: darkgray 1px solid;FONT-FAMILY: Tahoma, Verdana, 'Times New Roman';	BACKGROUND-COLOR: lightsteelblue;>"">&nbsp;&nbsp;"
                End If
                If objControl.ShowAdd Then
                    strHolder += "<input type=button value=New style=""BORDER-RIGHT: darkgray 1px solid;BORDER-TOP: darkgray 1px solid;FONT-SIZE: 8pt;	BORDER-LEFT: darkgray 1px solid;WIDTH: 80px;BORDER-BOTTOM: darkgray 1px solid;FONT-FAMILY: Tahoma, Verdana, 'Times New Roman';	BACKGROUND-COLOR: lightsteelblue;>"">&nbsp;&nbsp;"
                End If
                If objControl.ShowExport Then
                    strHolder += "<input type=button value=Export style=""BORDER-RIGHT: darkgray 1px solid;BORDER-TOP: darkgray 1px solid;FONT-SIZE: 8pt;	BORDER-LEFT: darkgray 1px solid;WIDTH: 80px;BORDER-BOTTOM: darkgray 1px solid;FONT-FAMILY: Tahoma, Verdana, 'Times New Roman';	BACKGROUND-COLOR: lightsteelblue;>"">"
                End If
                If objControl.ShowFunctionButtonOne Then
                    strHolder += "<input type=button value=""Function One"" style=""BORDER-RIGHT: darkgray 1px solid;BORDER-TOP: darkgray 1px solid;FONT-SIZE: 8pt;	BORDER-LEFT: darkgray 1px solid;WIDTH: 100px;BORDER-BOTTOM: darkgray 1px solid;FONT-FAMILY: Tahoma, Verdana, 'Times New Roman';	BACKGROUND-COLOR: lightsteelblue;>"">"
                End If

                Return strHolder
            Else
                Return "No columns defined."
            End If
        End Function

        Public Overrides Sub Initialize(ByVal component As System.ComponentModel.IComponent)
            If (Not TypeOf component Is Control) And (Not TypeOf component Is INamingContainer) Then
                Throw New ArgumentException("Component must be a container control", "component")
            End If
            MyBase.Initialize(component)
        End Sub
    End Class
#End Region

#Region " MasterControlBuilder Class "
    Public Class MasterControlBuilder : Inherits ControlBuilder
        Public Overrides Function GetChildControlType(ByVal TagName As String, ByVal Attributes As IDictionary) As Type
            If InStr(TagName, "BoundColumn") Then
                Return GetType(System.Web.UI.WebControls.BoundColumn)
            End If

            Return Nothing
        End Function
    End Class
#End Region

End Namespace
