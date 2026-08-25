#Region " Imports"
Imports System.IO
Imports System.Data
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.DataAccess.Custom
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class TeamBoardMenu
        Inherits ApplicationBase

#Region "Public Properties"
        Public ReadOnly Property DragDisabled() As String
            Get
                Dim dd As Boolean = Not UserCanEdit()
                Return dd.ToString().ToLower()
            End Get
        End Property
        Public ReadOnly Property DeleteConfirmString() As String
            Get
                Return GetTranslationString("teamboarddeleteconfirm", "This will delete the selected Team Board Menu Option. Are you sure?")
            End Get
        End Property
        Public ReadOnly Property MoveConfirmString() As String
            Get
                Return GetTranslationString("teamboardmoveconfirm", "This will move the selected Team Board Menu Option. Are you sure?")
            End Get
        End Property
#End Region

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            If IsPostBack Then
                If (actionInfo.Value <> String.Empty) Then
                    Dim args As String() = actionInfo.Value.Split("|")
                    Select Case args(0)
                        Case "DELETE"
                            Dim itemId As String = args(1)
                            If IsNumeric(itemId) Then
                                DeleteTeamBoardMenuOptionMaster(Convert.ToInt32(itemId))
                            End If
                        Case "MOVE"
                            Dim itemId As String = args(1)
                            Dim destinationRow As String = args(2)
                            Dim destinationCol As String = args(3)
                            If IsNumeric(itemId) AndAlso IsNumeric(destinationRow) AndAlso IsNumeric(destinationCol) Then
                                MoveTeamBoardMenuOptionMaster(Convert.ToInt32(itemId), destinationRow, destinationCol)
                            End If
                    End Select
                    actionInfo.Value = String.Empty
                End If
            End If

            Master.IconImage = Request.ApplicationPath + "/images/signpost.gif"
            Master.HeaderMessage = GetTranslationString("teamboard", "Team Board")
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            SessionManager.CurrentMenuProgram = "TeamBoardMenu"
            If SessionManager.SelectedTeamID = 0 Then
                SessionManager.CallingProgram = "TeamBoardMenu"
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamSelection"), False)
            End If
            Try
                Dim ds As DataTable = Teams.SelectTeams(SessionManager.SelectedTeamID)
                If ds.Rows.Count <> 0 Then
                    Dim dr As DataRow = ds.Rows(0)
                    Select Case dr("TeamBoardType").ToString
                        Case "Step"
                            LoadStepTeamBoardMenu(True)
                        Case "Pillar"
                            LoadPillarTeamBoardMenu()
                        Case Else
                            LoadStepTeamBoardMenu(False)
                    End Select
                End If
                trashcan.Visible = UserCanEdit()

            Catch Exc As Exception
                Master.DisplayErrors("TeamBoardMenu - Page_Load ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub LinkButton_Click(ByVal sender As System.Object, ByVal e As WebControls.CommandEventArgs)
            Dim strLink() As String = (CType(sender, LinkButton).CommandArgument).Split("|")
            Dim strProgram As String = ""

            If strLink.Length > 0 Then
                Select Case strLink(0)
                    Case "Team"
                        PushTeamOntoStack(SessionManager.SelectedTeamID, SessionManager.SelectedTeam, SessionManager.SelectedOPI, "TeamBoardMenu", SessionManager.CurrentMenuProgram)
                        Dim objDT As DataTable = Teams.SelectTeams(strLink(1))
                        If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                            Dim dtRow As DataRow = objDT.Rows(0)

                            SessionManager.SelectedTeamID = dtRow("TeamID")
                            SessionManager.SelectedTeam = dtRow("Team").ToString
                            SessionManager.SelectedTeamName = Teams.GetTeamName(SessionManager.SelectedTeamID)
                            SessionManager.SelectedOPI = ""
                            SessionManager.SelectedTeamAllowEdit = UserSiteMaster.SelectTeamAllowEdit(SessionManager.SelectedTeamID, SessionManager.UserID)
                            strProgram = strLink(2)
                        End If
                    Case "KPI"
                        SessionManager.SelectedValueKPIID = strLink(1)
                        SessionManager.CallingProgram = "TeamBoardMenu"
                        strProgram = strLink(2)
                    Case "Tracker"
                        SessionManager.SelectedValueTrackerID = strLink(1)
                        SessionManager.CallingProgram = "TeamBoardMenu"
                        strProgram = strLink(2)
                End Select
            End If

            If strProgram.Trim.Length > 0 Then
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strProgram), False)
            End If
        End Sub
        Private Sub JobLinkButton_Click(ByVal sender As System.Object, ByVal e As WebControls.CommandEventArgs)
            Dim strJob As String = CType(sender, LinkButton).ID
            SessionManager.SelectedValueJob = strJob
            SessionManager.SelectedValueJobName = JobMaster.SelectJobNameFromJobID(strJob)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserSkillRatings1"), False)
        End Sub
        Private Sub actionButton_Click(ByVal sender As Object, ByVal e As System.Web.UI.ImageClickEventArgs)
            Dim strArgs() As String = sender.CommandArgument.ToString.Split("|")
            Dim strProgram As String = strArgs(0)
            Dim rowNum As String = strArgs(1)
            Dim colNum As String = strArgs(2)

            SessionManager.MenuActionCoordinates = String.Format("{0}|{1}", rowNum, colNum)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strProgram), False)
        End Sub
#End Region

#Region "Custom Methods"
        Private Sub LoadPillarTeamBoardMenu()
            Try
                Dim ds As DataTable = TeamBoardMenuOptionMaster.SelectTeamBoardMenuOptionMasterByTeam(SessionManager.SelectedTeamID)
                Dim intMaxRow As Integer
                Dim intMaxColumn As Integer
                Dim iCounter As Integer = 0
                Dim ContainerRow As TableRow
                Dim ContainerCell As TableCell
                Dim HeaderRow As TableRow
                Dim HeaderCell As TableCell = Nothing
                Dim lnkbtn As LinkButton = Nothing
                Dim lnk As HyperLink = Nothing
                Dim lblbtn As Label = Nothing
                Dim strSessionID As String = Session.SessionID.ToString
                strSessionID = "(S(" + strSessionID + "))"

                'get maxrow & maxcolumn
                For iCounter = ds.Rows.Count - 1 To 0 Step -1
                    If ds.Rows(iCounter)("BoardRow") > intMaxRow Then
                        intMaxRow = ds.Rows(iCounter)("BoardRow")
                    End If
                    If ds.Rows(iCounter)("BoardColumn") > intMaxColumn Then
                        intMaxColumn = ds.Rows(iCounter)("BoardColumn")
                        If intMaxColumn < 6 Then
                            intMaxColumn = 6
                        End If
                    End If
                Next

                'Create empty container table rows. We will add data later

                'Set table properties
                TeamBoardTable1.BorderColor = Drawing.Color.Black
                TeamBoardTable1.BorderWidth = New Unit(5)
                TeamBoardTable1.CellSpacing = 8

                'Add header row
                HeaderRow = New TableRow

                'Add header cells to Row
                For col As Integer = 1 To intMaxColumn
                    If col = 1 Then
                        HeaderCell = New TableCell

                        HeaderCell.Height = New Unit(15)
                        HeaderCell.Width = New Unit((100 / intMaxColumn).ToString + "%")
                        HeaderCell.BorderColor = Drawing.Color.Black
                        HeaderCell.BackColor = Drawing.Color.LightCyan
                        HeaderCell.BorderWidth = New Unit(1)
                        HeaderCell.ColumnSpan = 2
                        HeaderCell.HorizontalAlign = HorizontalAlign.Center
                        HeaderCell.Font.Size = New FontUnit(12)
                        HeaderCell.Wrap = False
                        HeaderCell.Text = GetTranslationString("PILLARVISION", "PILLAR VISION")

                    ElseIf col = 3 Then
                        HeaderCell = New TableCell

                        HeaderCell.Height = New Unit(8)
                        HeaderCell.Width = New Unit((100 / intMaxColumn).ToString + "%")
                        HeaderCell.BorderColor = Drawing.Color.Black
                        HeaderCell.BackColor = Drawing.Color.LightCyan
                        HeaderCell.BorderWidth = New Unit(1)
                        HeaderCell.ColumnSpan = 2
                        HeaderCell.HorizontalAlign = HorizontalAlign.Center
                        HeaderCell.Font.Size = New FontUnit(12)
                        HeaderCell.Text = GetTranslationString("DEPLOYMENT", "DEPLOYMENT")
                    ElseIf col = 5 Then
                        HeaderCell = New TableCell

                        HeaderCell.Height = New Unit(8)
                        HeaderCell.Width = New Unit((100 / intMaxColumn).ToString + "%")
                        HeaderCell.BorderColor = Drawing.Color.Black
                        HeaderCell.BackColor = Drawing.Color.LightCyan
                        HeaderCell.BorderWidth = New Unit(1)
                        HeaderCell.ColumnSpan = 2
                        HeaderCell.HorizontalAlign = HorizontalAlign.Center
                        HeaderCell.Font.Size = New FontUnit(12)
                        HeaderCell.Text = GetTranslationString("TEAMACTIVITY", "TEAM ACTIVITY")
                        HeaderCell.Wrap = False
                    End If

                    'Add cell to row
                    If HeaderCell IsNot Nothing Then
                        HeaderRow.Cells.Add(HeaderCell)
                    End If
                Next

                'Add Header row to the table
                TeamBoardTable1.Rows.Add(HeaderRow)

                For row As Integer = 1 To intMaxRow
                    ContainerRow = New TableRow

                    'Add cells to Row
                    For col As Integer = 1 To intMaxColumn
                        ContainerCell = New TableCell

                        ContainerCell.Height = New Unit(92)
                        ContainerCell.Width = New Unit((100 / intMaxColumn).ToString + "%")
                        ContainerCell.BorderColor = Drawing.Color.Black
                        ContainerCell.BackColor = Drawing.Color.LightSteelBlue
                        ContainerCell.BorderWidth = New Unit(1)
                        ContainerCell.HorizontalAlign = HorizontalAlign.Center
                        ContainerCell.CssClass = "Relative"
                        ContainerCell.Attributes.Add("CellPosition", String.Format("{0}|{1}", row, col))
                        'Add cell to row
                        ContainerRow.Cells.Add(ContainerCell)
                    Next

                    'Add row to the table
                    TeamBoardTable1.Rows.Add(ContainerRow)
                Next

                'Load Data from Table
                If ds.Rows.Count = 0 Then
                    lblbtn = New Label
                    lblbtn.Text = "NO PROGRAMS or LINKS HAVE BEEN DEFINED"
                    lblbtn.ForeColor = Drawing.Color.Indigo
                    lblbtn.Font.Size = New FontUnit(16)
                    TeamBoardTable1.Rows(1 - 1).Cells(1 - 1).Controls.Add(lblbtn)
                End If

                Dim strLanguage As String = "en"
                If SessionManager.CulturePref.Trim.Length > 2 Then
                    strLanguage = SessionManager.CulturePref.Substring(0, 2)
                End If

                'Load Data from Table
                For Each dr As DataRow In ds.Rows
                    Dim intBoardRow As String = dr("BoardRow") + 1
                    Dim intBoardColumn As String = dr("BoardColumn")
                    Dim strBoardDescription As String = dr("BoardDescription")
                    Dim strLinkType As String = dr("LinkType")
                    Dim strProgram As String = dr("Program")
                    Dim strLinkFileURL As String = dr("LinkFileURL")

                    Select Case strLinkType
                        Case "P"
                            'Program
                            lnkbtn = New LinkButton
                            lnkbtn.Text = strBoardDescription
                            lnkbtn.ForeColor = Drawing.Color.Black
                            lnkbtn.Attributes.Add("LinkId", BuildLinkId(dr))
                        Case "K"
                            lnkbtn = New LinkButton
                            AddHandler lnkbtn.Command, AddressOf LinkButton_Click
                            lnkbtn.ID = "KPI|" + strLinkFileURL + "|" + strProgram + "|" + strBoardDescription
                            lnkbtn.CommandArgument = "KPI|" + strLinkFileURL + "|" + strProgram + "|" + strBoardDescription
                            lnkbtn.Text = strBoardDescription
                            lnkbtn.ForeColor = Drawing.Color.Red
                            lnkbtn.Attributes.Add("LinkId", BuildLinkId(dr))
                        Case "S"
                            lnkbtn = New LinkButton
                            AddHandler lnkbtn.Command, AddressOf LinkButton_Click
                            lnkbtn.ID = "Tracker|" + strLinkFileURL + "|" + strProgram + "|" + strBoardDescription
                            lnkbtn.CommandArgument = "Tracker|" + strLinkFileURL + "|" + strProgram + "|" + strBoardDescription
                            lnkbtn.Text = strBoardDescription
                            lnkbtn.ForeColor = Drawing.Color.Red
                            lnkbtn.Attributes.Add("LinkId", BuildLinkId(dr))
                        Case "T"
                            lnkbtn = New LinkButton
                            AddHandler lnkbtn.Command, AddressOf LinkButton_Click
                            lnkbtn.ID = "Team|" + strLinkFileURL + "|" + strProgram + "|" + strBoardDescription
                            lnkbtn.CommandArgument = "Team|" + strLinkFileURL + "|" + strProgram + "|" + strBoardDescription
                            lnkbtn.Text = strBoardDescription
                            lnkbtn.ForeColor = Drawing.Color.Blue
                            lnkbtn.Attributes.Add("LinkId", BuildLinkId(dr))
                        Case "L"
                            'LinkFileURL 
                            lnkbtn = New LinkButton
                            lnkbtn.ForeColor = Drawing.Color.Green
                            lnkbtn.Text = strBoardDescription
                            lnkbtn.ToolTip = strLinkFileURL
                            lnkbtn.Attributes.Add("LinkId", BuildLinkId(dr))
                        Case "U"
                            'URL Link
                            lnkbtn = New LinkButton
                            lnkbtn.ForeColor = Drawing.Color.Blue
                            lnkbtn.Text = strBoardDescription
                            lnkbtn.ToolTip = strLinkFileURL
                            lnkbtn.Attributes.Add("LinkId", BuildLinkId(dr))
                        Case "J"
                            lnkbtn = New LinkButton
                            AddHandler lnkbtn.Command, AddressOf JobLinkButton_Click
                            lnkbtn.ID = strLinkFileURL
                            lnkbtn.Text = strBoardDescription
                            lnkbtn.ForeColor = Drawing.Color.Black
                            lnkbtn.Attributes.Add("LinkId", BuildLinkId(dr))
                        Case "D"
                            'Text Label
                            lblbtn = New Label
                            lblbtn.ForeColor = Drawing.Color.Indigo
                            lblbtn.Text = strBoardDescription
                            lblbtn.Attributes.Add("LinkId", BuildLinkId(dr))
                        Case "F"
                            'PrinterFriendly Program
                            lnk = New HyperLink
                            lnk.Target = "_blank "
                            lnk.Text = strBoardDescription
                            lnk.NavigateUrl = Context.Request.ApplicationPath & "/" & strSessionID & "/" & ProgramSecurity.GetProgramURL(strProgram)
                            lnk.ForeColor = Drawing.Color.Blue
                            lnk.Attributes.Add("LinkId", BuildLinkId(dr))
                        Case "Z"
                            'Training Document
                            lnkbtn = New LinkButton
                            lnkbtn.ForeColor = Drawing.Color.Blue
                            lnkbtn.Text = strBoardDescription
                            lnkbtn.ToolTip = strLinkFileURL
                            lnkbtn.Attributes.Add("LinkId", BuildLinkId(dr))
                    End Select

                    Select Case strLinkType
                        Case "L"
                            'Link File URL
                            lnkbtn.Attributes.Add("onclick", "javascript:LaunchExplorer('" & (Teams.GetTeamFolder(SessionManager.SelectedTeamID) & "\" & strLinkFileURL).Replace("\", "\\") & "');")
                        Case "U"
                            'URL Link
                            lnkbtn.Attributes.Add("onclick", "javascript:LaunchExplorer('" & strLinkFileURL.Replace("\", "\\") & "');")
                        Case "P"
                            'Program 
                            lnkbtn.Attributes.Add("onclick", "javascript:window.navigate('" + Context.Request.ApplicationPath & "/" & strSessionID & "/" & ProgramSecurity.GetProgramURL(strProgram) + "');return false;")
                        Case "Z"
                            'Training Document
                            lnkbtn.Attributes.Add("onclick", "javascript:LaunchExplorer('http://" & ConfigurationManager.AppSettings("ApplicationServerDNS").ToString & ConfigurationManager.AppSettings("TrainingAttachmentsVirtualRootDirectory").ToString & strLanguage & "/" & strLinkFileURL & "');")
                    End Select

                    'Add data to appropriate cell
                    Select Case strLinkType
                        Case "D"
                            TeamBoardTable1.Rows(intBoardRow - 1).Cells(intBoardColumn - 1).Controls.Add(lblbtn)
                        Case "F"
                            TeamBoardTable1.Rows(intBoardRow - 1).Cells(intBoardColumn - 1).Controls.Add(lnk)
                        Case "P", "L", "U", "T", "J", "Z", "S", "K"
                            TeamBoardTable1.Rows(intBoardRow - 1).Cells(intBoardColumn - 1).Controls.Add(lnkbtn)
                        Case Else
                    End Select

                    'Add a Break tag
                    TeamBoardTable1.Rows(intBoardRow - 1).Cells(intBoardColumn - 1).Controls.Add(New LiteralControl("<BR><BR>"))
                Next

                ' Add action button to each table cell, regardless of presence of business data in the cell
                LoadEditButtons(intMaxRow, intMaxColumn, False)
            Catch Exc As Exception
                Master.DisplayErrors("TeamBoardMenu - LoadPillarTeamBoardMenu ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub LoadStepTeamBoardMenu(ByVal bStepHeaders As Boolean)
            Try
                Dim ds As DataTable = TeamBoardMenuOptionMaster.SelectTeamBoardMenuOptionMasterByTeam(SessionManager.SelectedTeamID)
                Dim intMaxRow As Integer = 1
                Dim intMaxColumn As Integer = 1
                Dim iCounter As Integer = 0
                Dim ContainerRow As TableRow
                Dim ContainerCell As TableCell
                Dim HeaderRow As TableRow
                Dim HeaderCell As TableCell
                Dim lnkbtn As LinkButton = Nothing
                Dim lnk As HyperLink = Nothing
                Dim lblbtn As Label = Nothing
                Dim strSessionID As String = Session.SessionID.ToString
                strSessionID = "(S(" + strSessionID + "))"

                'get maxrow & maxcolumn
                For iCounter = ds.Rows.Count - 1 To 0 Step -1
                    If ds.Rows(iCounter)("BoardRow") > intMaxRow Then
                        intMaxRow = ds.Rows(iCounter)("BoardRow")
                    End If
                    If ds.Rows(iCounter)("BoardColumn") > intMaxColumn Then
                        intMaxColumn = ds.Rows(iCounter)("BoardColumn")
                    End If
                Next

                'Create empty container table rows. We will add data later

                'Set table properties
                TeamBoardTable1.BorderColor = Drawing.Color.Black
                TeamBoardTable1.BorderWidth = New Unit(5)
                TeamBoardTable1.CellSpacing = 8

                'Add header row
                HeaderRow = New TableRow

                'Fixed columns with no STEP header cell(empty header cell) and no border
                'only if we want to shoe the step header
                If bStepHeaders Then
                    For col As Integer = 1 To 2
                        HeaderCell = New TableCell
                        HeaderCell.Height = New Unit(15)
                        HeaderCell.Width = New Unit((100 / intMaxColumn).ToString & "%")
                        HeaderCell.BorderWidth = New Unit(0)

                        'Add cell to row
                        HeaderRow.Cells.Add(HeaderCell)
                    Next

                    'Add header cells to Row
                    For col As Integer = 3 To intMaxColumn

                        HeaderCell = New TableCell

                        HeaderCell.Height = New Unit(20)
                        HeaderCell.Width = New Unit((100 / intMaxColumn).ToString & "%")
                        HeaderCell.BorderColor = Drawing.Color.Black
                        HeaderCell.BackColor = Drawing.Color.LightCyan
                        HeaderCell.BorderWidth = New Unit(1)
                        HeaderCell.HorizontalAlign = HorizontalAlign.Center

                        HeaderCell.Text = GetTranslationString("STEP", "STEP ") & (col - 2).ToString

                        'Add cell to row
                        HeaderRow.Cells.Add(HeaderCell)
                    Next

                    'Add Header row to the table
                    TeamBoardTable1.Rows.Add(HeaderRow)
                End If

                For row As Integer = 1 To intMaxRow
                    ContainerRow = New TableRow

                    'Add cells to Row
                    For col As Integer = 1 To intMaxColumn
                        ContainerCell = New TableCell

                        If bStepHeaders Then
                            ContainerCell.Height = New Unit(92)
                        End If
                        ContainerCell.Width = New Unit((100 / intMaxColumn).ToString & "%")
                        ContainerCell.BorderColor = Drawing.Color.Black
                        ContainerCell.BackColor = Drawing.Color.LightSteelBlue
                        ContainerCell.BorderWidth = New Unit(1)
                        ContainerCell.HorizontalAlign = HorizontalAlign.Center
                        If bStepHeaders Then
                            ContainerCell.VerticalAlign = VerticalAlign.Middle
                        Else
                            ContainerCell.VerticalAlign = VerticalAlign.Top
                        End If
                        ContainerCell.CssClass = "Relative"
                        ContainerCell.Attributes.Add("CellPosition", String.Format("{0}|{1}", row, col))
                        'Add cell to row
                        ContainerRow.Cells.Add(ContainerCell)
                    Next

                    'Add row to the table
                    TeamBoardTable1.Rows.Add(ContainerRow)
                Next

                'Load Data from Table
                If ds.Rows.Count = 0 Then
                    lblbtn = New Label
                    lblbtn.Text = "NO PROGRAMS or LINKS HAVE BEEN DEFINED"
                    lblbtn.ForeColor = Drawing.Color.Indigo
                    lblbtn.Font.Size = New FontUnit(16)
                    TeamBoardTable1.Rows(1 - 1).Cells(1 - 1).Controls.Add(lblbtn)
                End If

                Dim strLanguage As String = "en"
                If SessionManager.CulturePref.Trim.Length > 2 Then
                    strLanguage = SessionManager.CulturePref.Substring(0, 2)
                End If

                'Load Data from Table
                For Each dr As DataRow In ds.Rows
                    Dim addedActionButton = False
                    Dim intBoardRow As String
                    If bStepHeaders Then
                        intBoardRow = dr("BoardRow") + 1
                    Else
                        intBoardRow = dr("BoardRow")
                    End If
                    Dim intBoardColumn As String = dr("BoardColumn")
                    Dim strBoardDescription As String = dr("BoardDescription")
                    Dim strLinkType As String = dr("LinkType")
                    Dim strProgram As String = dr("Program")
                    Dim strLinkFileURL As String = dr("LinkFileURL")

                    Select Case strLinkType
                        Case "P"
                            'Program
                            lnkbtn = New LinkButton
                            lnkbtn.ForeColor = Drawing.Color.Black
                            lnkbtn.Text = strBoardDescription
                            lnkbtn.Attributes.Add("LinkId", BuildLinkId(dr))
                        Case "K"
                            lnkbtn = New LinkButton
                            AddHandler lnkbtn.Command, AddressOf LinkButton_Click
                            lnkbtn.ID = "KPI|" + strLinkFileURL + "|" + strProgram + "|" + strBoardDescription
                            lnkbtn.CommandArgument = "KPI|" + strLinkFileURL + "|" + strProgram + "|" + strBoardDescription
                            lnkbtn.Text = strBoardDescription
                            lnkbtn.ForeColor = Drawing.Color.Red
                            lnkbtn.Attributes.Add("LinkId", BuildLinkId(dr))
                        Case "S"
                            lnkbtn = New LinkButton
                            AddHandler lnkbtn.Command, AddressOf LinkButton_Click
                            lnkbtn.ID = "Tracker|" + strLinkFileURL + "|" + strProgram + "|" + strBoardDescription
                            lnkbtn.CommandArgument = "Tracker|" + strLinkFileURL + "|" + strProgram + "|" + strBoardDescription
                            lnkbtn.Text = strBoardDescription
                            lnkbtn.ForeColor = Drawing.Color.Red
                            lnkbtn.Attributes.Add("LinkId", BuildLinkId(dr))
                        Case "T"
                            lnkbtn = New LinkButton
                            AddHandler lnkbtn.Command, AddressOf LinkButton_Click
                            lnkbtn.ID = "Team|" + strLinkFileURL + "|" + strProgram + "|" + strBoardDescription
                            lnkbtn.CommandArgument = "Team|" + strLinkFileURL + "|" + strProgram + "|" + strBoardDescription
                            lnkbtn.Text = strBoardDescription
                            lnkbtn.ForeColor = Drawing.Color.Blue
                            lnkbtn.Attributes.Add("LinkId", BuildLinkId(dr))
                        Case "L"
                            'LinkFileURL 
                            lnkbtn = New LinkButton
                            lnkbtn.ForeColor = Drawing.Color.Green
                            lnkbtn.Text = strBoardDescription
                            lnkbtn.ToolTip = strLinkFileURL
                            lnkbtn.Attributes.Add("LinkId", BuildLinkId(dr))
                        Case "U"
                            'Link URL 
                            lnkbtn = New LinkButton
                            lnkbtn.ForeColor = Drawing.Color.Blue
                            lnkbtn.Text = strBoardDescription
                            lnkbtn.ToolTip = strLinkFileURL
                            lnkbtn.Attributes.Add("LinkId", BuildLinkId(dr))
                        Case "J"
                            lnkbtn = New LinkButton
                            AddHandler lnkbtn.Command, AddressOf JobLinkButton_Click
                            lnkbtn.ID = strLinkFileURL
                            lnkbtn.Text = strBoardDescription
                            lnkbtn.ForeColor = Drawing.Color.Black
                            lnkbtn.Attributes.Add("LinkId", BuildLinkId(dr))
                        Case "D"
                            'Text Label
                            lblbtn = New Label
                            lblbtn.ForeColor = Drawing.Color.Indigo
                            lblbtn.Text = strBoardDescription
                            lblbtn.Attributes.Add("LinkId", BuildLinkId(dr))
                        Case "Z"
                            'Training Document
                            lnkbtn = New LinkButton
                            lnkbtn.ForeColor = Drawing.Color.Blue
                            lnkbtn.Text = strBoardDescription
                            lnkbtn.ToolTip = strLinkFileURL
                            lnkbtn.Attributes.Add("LinkId", BuildLinkId(dr))
                        Case Else
                            'PrinterFriendly Program
                            lnk = New HyperLink
                            lnk.Target = "_blank "
                            lnk.Text = strBoardDescription
                            lnk.NavigateUrl = Context.Request.ApplicationPath & "/" & strSessionID & "/" & ProgramSecurity.GetProgramURL(strProgram)
                            lnk.ForeColor = Drawing.Color.Blue
                            lnk.Attributes.Add("LinkId", BuildLinkId(dr))
                    End Select

                    Select Case strLinkType
                        Case "L"
                            'Link File URL
                            lnkbtn.Attributes.Add("onclick", "javascript:LaunchExplorer('" & (Teams.GetTeamFolder(SessionManager.SelectedTeamID) & "\" & strLinkFileURL).Replace("\", "\\") & "');")
                        Case "U"
                            'URL Link
                            lnkbtn.Attributes.Add("onclick", "javascript:LaunchExplorer('" & strLinkFileURL.Replace("\", "\\") & "');")
                        Case "P"
                            'Program 
                            lnkbtn.Attributes.Add("onclick", "javascript:window.navigate('" + Context.Request.ApplicationPath & "/" & strSessionID & "/" & ProgramSecurity.GetProgramURL(strProgram) + "');return false;")
                        Case "Z"
                            'Training Document
                            lnkbtn.Attributes.Add("onclick", "javascript:LaunchExplorer('http://" & ConfigurationManager.AppSettings("ApplicationServerDNS").ToString & ConfigurationManager.AppSettings("TrainingAttachmentsVirtualRootDirectory").ToString & strLanguage & "/" & strLinkFileURL & "');")
                    End Select

                    'Add data to appropriate cell
                    Select Case strLinkType
                        Case "P", "L", "U", "T", "J", "Z", "S", "K"
                            TeamBoardTable1.Rows(intBoardRow - 1).Cells(intBoardColumn - 1).Controls.Add(lnkbtn)
                        Case "D"
                            TeamBoardTable1.Rows(intBoardRow - 1).Cells(intBoardColumn - 1).Controls.Add(lblbtn)
                        Case "F"
                            TeamBoardTable1.Rows(intBoardRow - 1).Cells(intBoardColumn - 1).Controls.Add(lnk)
                        Case Else
                    End Select

                    'Add a Break tag
                    TeamBoardTable1.Rows(intBoardRow - 1).Cells(intBoardColumn - 1).Controls.Add(New LiteralControl("<BR><BR>"))
                Next

                ' Add action button to each table cell, regardless of presence of business data in the cell
                LoadEditButtons(intMaxRow, intMaxColumn, Not bStepHeaders)
            Catch Exc As Exception
                Master.DisplayErrors("TeamBoardMenu - LoadStepTeamBoardMenu ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub LoadEditButtons(ByVal passMaxRow As Integer, ByVal passMaxColumn As Integer, ByVal passStepHeaders As Boolean)
            For intRow As Integer = 1 To passMaxRow
                For intCol = 1 To passMaxColumn
                    Dim objButton As New ImageButton
                    Dim correctedRow As Integer = intRow
                    If passStepHeaders Then
                        correctedRow -= 1
                    End If

                    objButton.Height = 11
                    objButton.Width = 11
                    objButton.ID = String.Format("Action{0}/{1}", correctedRow, intCol)
                    objButton.CssClass = "ActionButton"
                    'TeamBoardCellBlank.gif
                    'plus.gif
                    objButton.ImageUrl = "~/images/TeamBoardCellBlank.gif"
                    objButton.Attributes.Add("onmouseover", "this.src='../../../images/plus.gif'")
                    objButton.Attributes.Add("onmouseout", "this.src='../../../images/TeamBoardCellBlank.gif'")
                    objButton.CommandName = "Program"
                    objButton.BorderStyle = BorderStyle.None

                    objButton.CommandArgument = String.Format("{0}|{1}|{2}", "TeamBoardMenuOptionMaster1", intRow, intCol)
                    TeamBoardTable1.Rows(correctedRow).Cells(intCol - 1).Controls.Add(objButton)
                    AddHandler objButton.Click, AddressOf actionButton_Click
                Next
            Next
        End Sub
        Private Function DeleteTeamBoardMenuOptionMaster(ByVal passItemID As Integer) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim strBoardDescription As String = GetTeamBoardLinkDescription(passItemID)
                TeamBoardMenuOptionMaster.DeleteTeamBoardMenuOptionMaster(passItemID)
                RecordTransactionHistory.InsertRecordTransactionHistory("TeamBoardMenu", passItemID.ToString, "Team Board Menu Option - " & strBoardDescription & " - Deleted", SessionManager.UserID)
                RecordTransactionHistory.InsertRecordTransactionHistory("TeamBoardMenuOptions", SessionManager.SelectedTeamID.ToString, "Team Board Menu Option - " & strBoardDescription & " - Deleted", SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors("TeamBoardMenu" & " - DeleteTeamBoardMenuOptionMaster ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
        End Function
        Private Function MoveTeamBoardMenuOptionMaster(ByVal passItemID As Integer, ByVal destinationRow As String, ByVal destinationCol As String) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                TeamBoardMenuOptionMaster.MoveTeamBoardMenuOptionMaster(passItemID, CInt(destinationRow), CInt(destinationCol))

                RecordTransactionHistory.InsertRecordTransactionHistory("TeamBoardMenu", passItemID.ToString, "Team Board Menu Option Moved", SessionManager.UserID)
                RecordTransactionHistory.InsertRecordTransactionHistory("TeamBoardMenuOptions", SessionManager.SelectedTeamID.ToString, "Team Board Option - " & GetTeamBoardLinkDescription(passItemID) & " - moved to Row, Col: " & destinationRow & ", " & destinationCol, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors("TeamBoardMenu" & " - MoveTeamBoardMenuOptionMaster ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
        End Function
        Private Function BuildLinkId(ByVal dr As DataRow) As String
            Dim retVal As String = String.Format("{0}|{1}|{2}", dr("MenuOptionId").ToString(), dr("BoardRow").ToString(), dr("BoardColumn").ToString())
            Return retVal
        End Function
        Private Function UserCanEdit() As Boolean
            Dim bAccess As Boolean = DataAccess.Tables.UserSiteMaster.SelectTeamAllowEdit(SessionManager.SelectedTeamID, SessionManager.UserID)
            Return bAccess
        End Function
        Private Function GetTeamBoardLinkDescription(ByVal passLinkID As Integer) As String
            Dim strReturn As String = ""

            Try
                Dim objDT As DataTable = TeamBoardMenuOptionMaster.SelectTeamBoardMenuOptionMasterByID(passLinkID)
                If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                    strReturn = objDT.Rows(0)("BoardDescription").ToString.Trim
                End If
            Catch ex As Exception

            End Try

            Return strReturn
        End Function
#End Region

    End Class
End Namespace
