#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports System.Web
Imports System.Web.UI
Imports System.Web.UI.WebControls
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.DataAccess.Custom
#End Region

Namespace WebApp.APlus.UI.UserControls
    Public Class MenuControl
        Inherits System.Web.UI.UserControl

#Region " Members / Properties"
        Private currentContainerCell As TableCell
        Private currentTable As Table
        Public FormName As String
        Public ProgramName As String = ""
        Public MenuTitle As String
        Public AllowUserSpecifiedColumns As Boolean
        Public MenuType As String
        Public SpacerWidth As Integer
        Public ShowProgramShortcuts As Boolean
        Public AllowProgramShortcuts As Boolean
        Public HideOptionNumbers As Boolean
#End Region

#Region " Javascript Methods"
        Public Sub LoadOKButtonJavaScript(ByRef Page As System.Web.UI.Page, ByRef objTextControl As TextBox, ByRef objOKButton As Button)
            objTextControl.Attributes.Add("onkeydown", "fnTrapKD(document.all." & objOKButton.ClientID & ",window.event)")
        End Sub
#End Region

#Region " Event Handlers"
        'This call is required by the Web Form Designer.
        <System.Diagnostics.DebuggerStepThrough()> Private Sub InitializeComponent()
        End Sub
        Private Sub Page_Init(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Init
            InitializeComponent()
            LoadOKButtonJavaScript(Page, txtOption, btnOK)

            BindTheData()
        End Sub
        Public Sub New()
            SpacerWidth = 20
        End Sub
        Protected Sub Page_PreRender(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.PreRender
            Dim objLink As New HtmlLink()
            objLink.ID = "MasterControlCSS"
            objLink.Attributes.Add("type", "text/css")
            objLink.Attributes.Add("rel", "stylesheet")
            objLink.Attributes.Add("href", "~/Styles/MenuControlStyle.css")
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
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            If Not Page.IsPostBack Then
                LoadCultureTranslations()
            End If
        End Sub
        Private Sub menuButton_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Dim strProgram As String = String.Empty
            Dim strProgramURL As String = String.Empty

            Select Case sender.CommandName.ToString
                Case "Program", "Menu"
                    'verify that the user has access to this program
                    Dim strArgs() As String = sender.CommandArgument.ToString.Split("|")
                    strProgram = strArgs(0)
                    strProgramURL = strArgs(1)

                    If ProgramSecurity.CanUserAccessProgram(SessionManager.UserID, strProgram) Then
                        If sender.CommandName.ToString = "Menu" Then
                            SessionManager.CurrentMenuProgram = strProgram
                        End If
                        If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.Menu) Then
                            EventTracker.AddNoEmail("menuButton_Click", SessionManager.CurrentMenuProgram & ":" & vbCrLf & sender.CommandName.ToString & " - " & strProgram, SessionManager.UserID)
                        End If
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & strProgramURL)
                    Else
                        txtOption.Text = String.Empty
                        tblContainer.Rows.Clear()
                        BindTheData()
                        Exit Sub
                    End If
                Case "Link"
                    strProgramURL = sender.CommandArgument
                    Dim strScript As String

                    strScript = "<script language='javascript'>LaunchExplorer('" + strProgramURL + "')" & "</script>"
                    Page.ClientScript.RegisterStartupScript(Me.GetType, "MenuLink", strScript)
                Case Else
                    If txtOption.Text.Trim.Length = 0 Then
                        txtOption.Text = String.Empty
                        txtOption.Focus()
                        Exit Sub
                    End If

                    'if the option text is numeric then try to get the program from the option
                    If IsNumeric(txtOption.Text) Then
                        ProgramSecurity.GetProgram(SessionManager.UserID.ToString, CBool(SessionManager.IsAdministrator), ProgramName, CInt(txtOption.Text), strProgram, strProgramURL)
                        If strProgram.Trim.Length = 0 Then
                            'ErrorControl.DisplayError("Invalid Option")
                            txtOption.Text = String.Empty
                            txtOption.Focus()
                            Exit Sub
                        End If
                    Else
                        'If program shortcuts aren't allowed, just return with error
                        If AllowProgramShortcuts = False Then
                            'ErrorControl.DisplayError("Program shortcuts are disabled for this menu")
                            txtOption.Text = String.Empty
                            txtOption.Focus()
                            Exit Sub
                        End If

                        'try to get the program from the shortcut
                        ProgramSecurity.GetProgramFromShortcut(SessionManager.UserID, SessionManager.IsAdministrator, txtOption.Text, strProgram, strProgramURL)
                        If strProgram.Trim.Length = 0 Then
                            'Me.Page.Master.DisplayError("Invalid Shortcut")
                            txtOption.Text = String.Empty
                            txtOption.Focus()
                            Exit Sub
                        End If
                    End If

                    If strProgramURL.Trim.Length = 0 Then
                        txtOption.Text = String.Empty
                        txtOption.Focus()
                    Else
                        Dim blnIsMenu As Boolean = False
                        If ProgramMaster.ProgramIsMenu(strProgram) Then
                            SessionManager.CurrentMenuProgram = strProgram
                            blnIsMenu = True
                        End If
                        If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.Menu) Then
                            EventTracker.AddNoEmail("menuButton_Click", SessionManager.CurrentMenuProgram & ":" & vbCrLf & sender.CommandName.ToString & " - " & strProgram, SessionManager.UserID)
                        End If
                        Response.Redirect(Request.ApplicationPath & "/" & strProgramURL)
                    End If
            End Select
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadCultureTranslations()
            btnOK.Text = GetTranslationString("ok", "OK")
            lblOption.Text = GetTranslationString("option", "Option:")
        End Sub
        Private Sub BindTheData()
            Dim iAdmin As Integer

            'Menu Settings 
            Dim Menu As String
            Dim ShowProgramGroups As Boolean
            Dim MaxColumns As Int16

            If SessionManager.CurrentMenuProgram <> "" Then
                ProgramName = SessionManager.CurrentMenuProgram.ToString
            End If

            If ProgramName.Trim.Length = 0 Then
                Return
            End If

            Try
                If SessionManager.IsAdministrator Then
                    iAdmin = 1
                Else
                    iAdmin = 0
                End If

                Dim dtMenuSettings As New DataTable
                Dim drMenuSettings As DataRow

                'First get the menu settings from MenuMaster
                dtMenuSettings = MenuMaster.SelectMenuMasterByKey(ProgramName) '.Tables(0)

                If dtMenuSettings.Rows.Count > 0 Then
                    drMenuSettings = dtMenuSettings.Rows(0)

                    Menu = drMenuSettings("Menu").ToString
                    MenuTitle = GetTranslationString(drMenuSettings("MenuText").ToString, drMenuSettings("MenuText").ToString) ' drMenuSettings("MenuText").ToString
                    ShowProgramGroups = CBool(drMenuSettings("ShowProgramGroups").ToString)
                    MenuType = drMenuSettings("MenuType").ToString
                    AllowProgramShortcuts = CBool(drMenuSettings("AllowProgramShortCuts"))
                    ShowProgramShortcuts = CBool(drMenuSettings("ShowProgramShortcuts"))
                    MaxColumns = CShort(drMenuSettings("MaxColumns"))
                    AllowUserSpecifiedColumns = CBool(drMenuSettings("AllowUserSpecifiedColumns"))
                    HideOptionNumbers = CBool(drMenuSettings("HideOptionNumbers"))

                    'verify menu options agains user preferences
                    If HideOptionNumbers = False Then
                        If Not SessionManager.ShowMenuOptionNumbers Then
                            HideOptionNumbers = True
                        Else
                            HideOptionNumbers = False
                        End If
                    End If
                End If

                If InStr(MenuType.ToUpper, "CENTER") > 0 Then
                    tblContainer.HorizontalAlign = HorizontalAlign.Center
                    tblOption.HorizontalAlign = HorizontalAlign.Center
                End If

                'Get the menuoptions
                Dim ds As New DataSet

                ds = MenuOptionMaster.GetMenuOptions(SessionManager.UserID.ToString, iAdmin, ProgramName, ShowProgramGroups, AllowUserSpecifiedColumns, SessionManager.ShowAllMenuOptions)

                Dim strCurrentProgram As String = String.Empty
                Dim strCurrentProgramURL As String = String.Empty
                Dim bCurrentProgramMenuYN As Boolean = False
                Dim iCurrentProgramOptionValue As Integer = 0
                Dim strCurrentProgramOptionDescription As String = String.Empty
                Dim strCurrentProgramShortcut As String = String.Empty

                If AllowUserSpecifiedColumns Then
                    'User specifies columns
                    Dim currentMenuColumn As Integer = 0
                    Dim currentProgramGroup As String = "empty"
                    Dim rowindex As Integer = 0

                    AddContainerRow()

                    'Menu items with Program Group
                    For Each drMenuData As DataRow In ds.Tables(0).Rows
                        'Menu column changed
                        'Add a new column
                        If CInt(drMenuData("MenuColumn")) <> currentMenuColumn Then
                            AddContainerCellAndTable()

                            'Set the current Menu Column
                            currentMenuColumn = CInt(drMenuData("MenuColumn"))
                        End If

                        'if program group changed then
                        'add a new Program Group row
                        'to current table in current cell
                        If drMenuData("ProgramGroup").ToString <> currentProgramGroup Then
                            AddProgramGroupRow(drMenuData("ProgramGroup").ToString)
                            'Set the new Program Group
                            currentProgramGroup = drMenuData("ProgramGroup").ToString
                        End If

                        'Add Menu Data
                        strCurrentProgram = drMenuData("Program").ToString.Trim
                        strCurrentProgramURL = drMenuData("ProgramURL").ToString.Trim
                        If Not drMenuData("MenuYN") Is DBNull.Value Then
                            bCurrentProgramMenuYN = CBool(drMenuData("MenuYN"))
                        End If
                        If Not drMenuData("OptionValue") Is DBNull.Value Then
                            iCurrentProgramOptionValue = Convert.ToInt16(drMenuData("OptionValue"))
                        End If
                        strCurrentProgramOptionDescription = drMenuData("OptionDescription").ToString.Trim
                        strCurrentProgramShortcut = drMenuData("ProgramShortcut").ToString.Trim

                        AddMenuDataRow(strCurrentProgram, strCurrentProgramURL, bCurrentProgramMenuYN, iCurrentProgramOptionValue, strCurrentProgramOptionDescription, strCurrentProgramShortcut)
                    Next

                    'Menu items without a program Group go here
                    'you dump them in a last existing column

                    'Add Blank program Group
                    If ds.Tables(1).Rows.Count > 0 Then
                        AddContainerCellAndTable()

                        AddProgramGroupRow("&nbsp;")

                        For Each drMenuDataNoProgramGroup As DataRow In ds.Tables(1).Rows
                            'Add Menu Data
                            strCurrentProgram = drMenuDataNoProgramGroup("Program").ToString.Trim
                            strCurrentProgramURL = drMenuDataNoProgramGroup("ProgramURL").ToString.Trim
                            If Not drMenuDataNoProgramGroup("MenuYN") Is DBNull.Value Then
                                bCurrentProgramMenuYN = drMenuDataNoProgramGroup("MenuYN")
                            End If
                            If Not drMenuDataNoProgramGroup("OptionValue") Is DBNull.Value Then
                                iCurrentProgramOptionValue = Convert.ToInt16(drMenuDataNoProgramGroup("OptionValue"))
                            End If
                            strCurrentProgramOptionDescription = drMenuDataNoProgramGroup("OptionDescription").ToString.Trim
                            strCurrentProgramShortcut = drMenuDataNoProgramGroup("ProgramShortcut").ToString.Trim

                            AddMenuDataRow(strCurrentProgram, strCurrentProgramURL, bCurrentProgramMenuYN, iCurrentProgramOptionValue, strCurrentProgramOptionDescription, strCurrentProgramShortcut)
                        Next
                    End If
                Else
                    'System generates the menus automatically
                    'Get Total Rows = Number of Menu Options + Number of Program Groups
                    Dim TotalRows As Integer
                    If ShowProgramGroups Then
                        TotalRows = ds.Tables(1).Rows(0).Item("TotalRows")
                    Else
                        TotalRows = ds.Tables(0).Rows.Count
                    End If

                    'Initially Remaining Programs that should be assigned is TotalRows
                    Dim RemainingProgs As Integer = TotalRows

                    'Remaining columns is number of columns that have to be assigned with menus
                    'Initially it will be equal to MaxColumns
                    Dim RemainingColumns As Integer = MaxColumns

                    'Variable to store number of Programs in Column
                    Dim ProgsInColumn As Integer

                    'Gets the current row index
                    Dim rowindex As Integer = 0
                    Dim currentProgramGroup As String = "empty"
                    Dim drMenuData As DataRow

                    'Add the first row and column
                    AddContainerRow()
                    AddContainerCellAndTable()

                    'Loop until we have assigned all Programs  to their respective columns
                    Do Until RemainingProgs = 0
                        If RemainingProgs Mod RemainingColumns > 0 Then
                            'Divides two numbers and returns an integer result by dropping the remainder
                            'Eg: 3\2 = 1
                            ProgsInColumn = (RemainingProgs \ RemainingColumns) + 1
                        Else
                            ProgsInColumn = (RemainingProgs / RemainingColumns) + 1
                        End If

                        'Row counter to get data
                        'Get the data for that column
                        Dim LastRow As Integer = ProgsInColumn - 1

                        For i As Integer = 0 To ProgsInColumn - 1
                            'Get the current Menu Data
                            If rowindex = ds.Tables(0).Rows.Count Then
                                Exit Do
                            End If

                            drMenuData = ds.Tables(0).Rows(rowindex)

                            'Has Program Group Changed?
                            'If so, output Program Group
                            If drMenuData("ProgramGroup") <> currentProgramGroup Then
                                'This makes sure if Program Group comes in last row
                                'it gets shifted to next column
                                'When we reach last row, we create a new container cell and a table within it
                                If i = LastRow Then
                                    AddContainerCellAndTable()

                                    'Reset ProgsInColumn 
                                    'Subtract 1 from it as we are not assigning this to
                                    'column as it is a ProgramGroup
                                    ProgsInColumn = ProgsInColumn - 1
                                    Exit For
                                End If

                                'Note we are not incrementing the rowindex because
                                'Program Group is in same row as data
                                'we have to come back to same row to add Menu Data
                                'Add Program Group Row
                                AddProgramGroupRow(drMenuData("ProgramGroup"))
                                'Set the new Program Group
                                currentProgramGroup = drMenuData("ProgramGroup")
                            Else
                                'Add Menu Data
                                strCurrentProgram = drMenuData("Program").ToString.Trim
                                strCurrentProgramURL = drMenuData("ProgramURL").ToString.Trim
                                If Not drMenuData("MenuYN") Is DBNull.Value Then
                                    bCurrentProgramMenuYN = drMenuData("MenuYN")
                                End If
                                If Not drMenuData("OptionValue") Is DBNull.Value Then
                                    iCurrentProgramOptionValue = Convert.ToInt16(drMenuData("OptionValue"))
                                End If
                                strCurrentProgramOptionDescription = drMenuData("OptionDescription").ToString.Trim
                                strCurrentProgramShortcut = drMenuData("ProgramShortcut").ToString.Trim

                                AddMenuDataRow(strCurrentProgram, strCurrentProgramURL, bCurrentProgramMenuYN, iCurrentProgramOptionValue, strCurrentProgramOptionDescription, strCurrentProgramShortcut)

                                'If we are in Lastrow for this column,
                                'we add a new column and table
                                If i = LastRow Then
                                    AddContainerCellAndTable()
                                End If

                                'Increment row index
                                rowindex = rowindex + 1
                            End If
                        Next

                        'Calculate the remaining progs that are unassigned
                        RemainingProgs = RemainingProgs - ProgsInColumn
                        'Reduce the number of columns
                        RemainingColumns = RemainingColumns - 1
                    Loop
                End If

                If AllowProgramShortcuts = False AndAlso HideOptionNumbers = True Then
                    tblOption.Visible = False
                End If
            Catch Sxc As SqlException
                EventTracker.AddNoEmail(ProgramName, Sxc.ToString, SessionManager.UserID.ToString)
            Catch Exc As Exception
                EventTracker.AddNoEmail(ProgramName, Exc.ToString, SessionManager.UserID.ToString)
            Finally
                If txtOption.Visible = True Then
                    Dim sScript As New System.Text.StringBuilder

                    sScript.Append("<SCRIPT language='javascript'>")
                    sScript.Append("NextField(document.getElementById('" + txtOption.ClientID + "'))")
                    sScript.Append("</SCRIPT>" & vbCrLf)

                    Page.ClientScript.RegisterStartupScript(Me.GetType, "InputFocus", sScript.ToString)
                End If
            End Try
        End Sub
        Private Sub AddProgramGroupRow(ByVal ProgramGroup As String)
            Dim row As New TableRow
            row.CssClass = ("MenuProgramGroup" & MenuType).ToUpper

            Dim cell As New TableCell
            cell.ColumnSpan = 3

            If ProgramGroup.Trim = String.Empty Then
                cell.Text = "&nbsp;"
            Else
                cell.Text = GetTranslationString(ProgramGroup, ProgramGroup)
            End If

            row.Cells.Add(cell)
            currentTable.Rows.Add(row)
        End Sub
        Private Sub AddMenuDataRow(ByVal passProgram As String, ByVal passProgramURL As String, ByVal bIsMenu As Boolean, ByVal OptionValue As String, ByVal OptionDescription As String, ByVal ProgramShortcut As String)
            Dim row As New TableRow
            Dim lnk As LinkButton
            Dim btn As Button

            If HideOptionNumbers = False Then
                Dim OptionValuecell As New TableCell
                OptionValuecell.Text = OptionValue
                row.Cells.Add(OptionValuecell)
            End If

            Dim ProgramCell As New TableCell
            If InStr(MenuType.ToUpper, "LINKBUTTON") > 0 Then
                lnk = New LinkButton
                If bIsMenu Then
                    lnk.CommandName = "Menu"
                Else
                    If passProgram.Trim.Length > 0 Then
                        lnk.CommandName = "Program"
                    Else
                        lnk.CommandName = "Link"
                    End If
                End If
                lnk.CommandArgument = passProgram & "|" & passProgramURL

                lnk.Text = GetTranslationString(OptionDescription, OptionDescription)

                'Associate button with event handler
                AddHandler lnk.Click, AddressOf menuButton_Click
                ProgramCell.Controls.Add(lnk)

                row.CssClass = ("MenuData" & MenuType).ToUpper
            ElseIf InStr(MenuType.ToUpper, "PUSHBUTTON") > 0 Then
                btn = New Button

                If passProgram.Trim.Length > 0 Then
                    If bIsMenu Then
                        btn.CommandName = "Menu"
                    Else
                        btn.CommandName = "Program"
                    End If
                    btn.CommandArgument = passProgram & "|" & passProgramURL

                    btn.Text = GetTranslationString(OptionDescription, OptionDescription)
                    btn.CssClass = ("MenuData" & MenuType).ToUpper

                    'Associate button with event handler
                    AddHandler btn.Click, AddressOf menuButton_Click
                    ProgramCell.Controls.Add(btn)
                Else
                    btn.CommandName = "Link"
                    btn.CommandArgument = passProgramURL

                    btn.Text = GetTranslationString(OptionDescription, OptionDescription)
                    btn.CssClass = ("MenuData" & MenuType).ToUpper

                    'Associate button with event handler
                    AddHandler btn.Click, AddressOf menuButton_Click
                    ProgramCell.Controls.Add(btn)
                End If
            End If

            row.Cells.Add(ProgramCell)

            If ShowProgramShortcuts Then
                Dim ProgramShortcutCell As New TableCell

                If ProgramShortcut.Trim = String.Empty Then
                    ProgramShortcutCell.Text = "&nbsp;"
                Else
                    ProgramShortcutCell.Text = ProgramShortcut
                End If

                row.Cells.Add(ProgramShortcutCell)
            End If

            currentTable.Rows.Add(row)
        End Sub
        Private Sub AddContainerCellAndTable()
            currentContainerCell = New TableCell
            currentContainerCell.VerticalAlign = VerticalAlign.Top

            tblContainer.Rows(0).Cells.Add(currentContainerCell)

            'Add a table to this cell
            currentTable = New Table
            If InStr(MenuType.ToUpper, "LINKBUTTON") > 0 Then
                currentTable.CellPadding = 3
            ElseIf InStr(MenuType.ToUpper, "PUSHBUTTON") > 0 Then
                currentTable.CellPadding = 2
            End If
            currentTable.CellSpacing = 1
            currentTable.CssClass = ("MenuColumnsTable" & MenuType).ToUpper
            currentContainerCell.Controls.Add(currentTable)

            'Add spacer cell
            Dim spacercell As New TableCell
            spacercell.Width = New Unit(SpacerWidth)
            spacercell.Text = "&nbsp;"

            tblContainer.Rows(0).Cells.Add(spacercell)
        End Sub
        Private Sub AddContainerRow()
            Dim row As New TableRow

            tblContainer.Rows.Add(row)
        End Sub
#End Region

    End Class
End Namespace
