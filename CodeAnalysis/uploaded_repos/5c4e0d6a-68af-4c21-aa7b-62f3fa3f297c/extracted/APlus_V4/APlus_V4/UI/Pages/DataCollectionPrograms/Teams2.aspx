<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="Teams2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.Teams2"
    Title="Teams Maintenance" EnableTheming="true" StylesheetTheme="APlus_Default" %>

<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="cc1" %>
<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<%@ Register TagPrefix="ApplicationControls" TagName="Attachments" Src="../../UserControls/Attachments.ascx" %>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/CalanderStyle.css" rel="stylesheet" />
    <style type="text/css">
        .style1
        {
            width: 145px;
        }
        .style2
        {
            width: 150px;
        }
        .style3
        {
            width: 155px;
        }
    </style>
</asp:Content>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table id="Table1" style="height: 160px" class="Table_Default">
        <tr>
            <td style="width: 105px">
                <asp:Label ID="lblTeamID" runat="server" CssClass="Label_Left_8PT" Text="Team ID:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtTeamID" runat="server" CssClass="Textbox_Display" ReadOnly="True"
                    Width="75px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 105px">
                <asp:Label ID="lblTeam" runat="server" CssClass="Label_Left_8PT" Text="Team:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtTeam" runat="server" CssClass="Textbox_Entry" MaxLength="10"
                    Width="112px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqTeam" runat="server" ControlToValidate="txtTeam"
                    CssClass="Label_Left_8PT" Display="None" ErrorMessage="Enter a Team"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 105px">
                <asp:Label ID="lblTeamName" runat="server" Text="Team Name:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtTeamName" runat="server" Width="520px" MaxLength="100" CssClass="Textbox_Entry"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqTeamName" runat="server" Display="None" ControlToValidate="txtTeamName"
                    ErrorMessage="Enter Team Name" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 105px">
                <asp:Label ID="lblTeamNameOther" runat="server" Text="Team Name (English):" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtTeamNameOther" runat="server" Width="520px" MaxLength="100" CssClass="Textbox_Entry"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqTeamNameOther" runat="server" Display="None" ControlToValidate="txtTeamNameOther"
                    ErrorMessage="Enter Team Name (English)" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 105px">
                <asp:Label ID="lblSite" runat="server" Text="Site:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlSite" runat="server" Width="216px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtSite" runat="server" CssClass="Textbox_Display" ReadOnly="True"
                    Width="216px" Visible="False"></asp:TextBox>
            </td>
            <asp:RequiredFieldValidator ID="reqSite" runat="server" Display="None" ControlToValidate="ddlSite"
                ErrorMessage="Enter a Site" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator></tr>
        <tr>
            <td style="width: 105px">
                <asp:Label ID="lblBusinessArea" runat="server" Text="Business Area:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlBusinessArea" runat="server" CssClass="DropdownList_Entry"
                    Width="272px">
                </asp:DropDownList>
                <asp:TextBox ID="txtBusinessArea" runat="server" CssClass="Textbox_Display" ReadOnly="True"
                    Visible="False" Width="272px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 105px">
                <asp:Label ID="lblBusinessUnit" runat="server" CssClass="Label_Left_8PT" Text="Business Unit:"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlBusinessUnit" runat="server" CssClass="DropdownList_Entry"
                    Width="272px">
                </asp:DropDownList>
                <asp:TextBox ID="txtBusinessUnit" runat="server" CssClass="Textbox_Display" ReadOnly="True"
                    Visible="False" Width="272px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 105px">
                <asp:Label ID="lblPillar" runat="server" CssClass="Label_Left_8PT" Text="Pillar:"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlPillar" runat="server" CssClass="DropdownList_Entry" Width="272px">
                </asp:DropDownList>
                <asp:TextBox ID="txtPillar" runat="server" CssClass="Textbox_Display" ReadOnly="True"
                    Visible="False" Width="272px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 105px">
                <asp:Label ID="lblRoute" runat="server" Text="Route:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlRoute" runat="server" Width="272px" CssClass="DropdownList_Entry"
                    AutoPostBack="True">
                </asp:DropDownList>
                <asp:TextBox ID="txtRoute" runat="server" Width="272px" CssClass="Textbox_Display"
                    ReadOnly="True" Visible="false"></asp:TextBox>
                <asp:Panel runat="server" ID="pnlChange" Visible="false">
                    <table id="tblChange">
                        <tr>
                            <td>
                                <asp:Label ID="lblRouteChange" runat="server" CssClass="Label_Left_8PT" ForeColor="Red"
                                    Text="Changing the Route will rebuild the Team Board. All existing Team Board links will be deleted."
                                    Visible="true" Width="544px"></asp:Label>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <asp:Label ID="lblRouteChange2" runat="server" CssClass="Label_Left_8PT" ForeColor="Red"
                                    Text="Changing the Route will remove existing Planned Dates." Visible="False"
                                    Width="368px"></asp:Label>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <asp:Label ID="lblRouteChangeJob" runat="server" CssClass="Label_Left_8PT" ForeColor="Red"
                                    Text="Changing the Route will create a new Team Training Matrix." Visible="False"
                                    Width="368px"></asp:Label>
                            </td>
                        </tr>
                    </table>
                </asp:Panel>
            </td>
        </tr>
        <tr>
            <td style="width: 105px;">
                <asp:Label ID="lblDeptNumber" runat="server" Text="Department:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtDeptNumber" runat="server" Width="112px" MaxLength="15" CssClass="Textbox_Entry"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 105px">
                <asp:Label ID="lblTeamFolder" runat="server" Text="Team Folder:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtTeamFolder" runat="server" Width="600px" MaxLength="200" CssClass="Textbox_Entry"
                    Height="16px"></asp:TextBox>
                <asp:FileUpload type="file" ID="fiTeamFolder" runat="server" onchange="loaded()"
                    Style="overflow: hidden; width: 83px;" />
                <asp:Label ID="lblTeamFolderMessage" runat="server" Text="Select a file within the Team folder, or type in folder name."
                    Visible="false" Style="color: Red" />
            </td>
        </tr>
    </table>
    <table id="Table3" class="Table_Default">
        <tr>
            <td>
                <asp:Label ID="lblStartDate" runat="server" Text="Start Date:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="width: 200px">
                <asp:TextBox ID="txtStartDate" runat="server" Width="80px" MaxLength="10" CssClass="Textbox_Entry"></asp:TextBox>
                <cc1:CalendarExtender ID="txtStartDate_CalendarExtender" runat="server" PopupButtonID="imgStartDate"
                    TargetControlID="txtStartDate" CssClass="APlus_Calendar">
                </cc1:CalendarExtender>
                <asp:ImageButton ID="imgStartDate" runat="server" ImageUrl="~/Images/date-time_select.gif"
                    ToolTip="Click to Select Date..." CausesValidation="False" />
                <asp:RequiredFieldValidator ID="reqStartDate" runat="server" Display="None" ControlToValidate="txtStartDate"
                    ErrorMessage="Enter a Start Date" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
                <asp:CompareValidator ID="cmpStartDate" runat="server" Display="None" ControlToValidate="txtStartDate"
                    ErrorMessage="Invalid Start Date" Type="Date" Operator="DataTypeCheck" CssClass="Label_Left_8PT"></asp:CompareValidator>
            </td>
            <td style="width: 85px">
                <asp:Label ID="lblFinishDate" runat="server" Text="Finish Date:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtFinishDate" runat="server" Width="80px" MaxLength="10" CssClass="Textbox_Entry"></asp:TextBox>
                <cc1:CalendarExtender ID="txtFinishDate_CalendarExtender" runat="server" PopupButtonID="imgFinishDate"
                    TargetControlID="txtFinishDate" CssClass="APlus_Calendar">
                </cc1:CalendarExtender>
                <asp:ImageButton ID="imgFinishDate" runat="server" ImageUrl="~/Images/date-time_select.gif"
                    ToolTip="Click to Select Date..." CausesValidation="False" />
            </td>
        </tr>
        <tr>
            <td>
                <asp:Label ID="lblTeamBoardType" runat="server" Width="128px" Text="Team Board Type:"
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="width: 200px">
                <asp:DropDownList ID="ddlTeamBoardType" runat="server" Width="65px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtTeamBoardType" runat="server" CssClass="Textbox_Display" ReadOnly="True"
                    Visible="False" Width="65px"></asp:TextBox>
            </td>
            <td style="width: 85px">
                <asp:Label ID="lblMasterPlanType" runat="server" Width="136px" Text="Master Plan Type:"
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlMasterPlanType" runat="server" Width="120px" CssClass="DropdownList_Entry">
                    <asp:ListItem Value="W" Text="Week Number"></asp:ListItem>
                    <asp:ListItem Value="D" Text="Week Ending Date"></asp:ListItem>
                </asp:DropDownList>
                <asp:TextBox ID="txtMasterPlanType" runat="server" Width="95px" CssClass="Textbox_Display"
                    Visible="False" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td>
                &nbsp;
            </td>
            <td style="width: 200px">
                &nbsp;
            </td>
            <td style="width: 85px">
                &nbsp;
            </td>
            <td>
            </td>
        </tr>
        <tr>
            <td style="width: 85px; height: 15px">
                <asp:Label ID="lblStatus" runat="server" Text="Status:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="width: 200px; height: 15px">
                <asp:DropDownList ID="ddlStatus" runat="server" Width="144px" CssClass="DropdownList_Entry">
                    <asp:ListItem></asp:ListItem>
                    <asp:ListItem Value="P" Text="Planned"></asp:ListItem>
                    <asp:ListItem Value="O" Text="Open"></asp:ListItem>
                    <asp:ListItem Value="S" Text="Stopped"></asp:ListItem>
                    <asp:ListItem Value="D" Text="Monitoring"></asp:ListItem>
                    <asp:ListItem Value="C" Text="Closed"></asp:ListItem>
                </asp:DropDownList>
                <asp:TextBox ID="txtTeamStatus" runat="server" Width="140px" CssClass="Textbox_Display"
                    Visible="False" ReadOnly="True"></asp:TextBox>
            </td>
            <td style="width: 85px; height: 15px">
                <asp:Label ID="lblTeamType" runat="server" Text="Team Type:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlTeamType" runat="server" Width="144px" CssClass="DropdownList_Entry">
                    <asp:ListItem></asp:ListItem>
                    <asp:ListItem Value="P" Text="Planned"></asp:ListItem>
                    <asp:ListItem Value="O" Text="Open"></asp:ListItem>
                    <asp:ListItem Value="S" Text="Stopped"></asp:ListItem>
                    <asp:ListItem Value="D" Text="Monitoring"></asp:ListItem>
                    <asp:ListItem Value="C" Text="Closed"></asp:ListItem>
                </asp:DropDownList>
                <asp:RequiredFieldValidator ID="reqTeamType" runat="server" Display="None" ControlToValidate="ddlTeamType"
                    ErrorMessage="Select Team Type" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
                <asp:TextBox ID="txtTeamType" runat="server" Width="140px" CssClass="Textbox_Display"
                    Visible="False" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 85px">
                <asp:Label ID="lblTeamCategory" runat="server" Text="Team Category:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="width: 200px">
                <asp:DropDownList ID="ddlTeamCategory" runat="server" Width="180px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:RequiredFieldValidator ID="reqTeamCategory" runat="server" Display="None" ControlToValidate="ddlTeamCategory"
                    ErrorMessage="Select Team Category" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
                <asp:TextBox ID="txtTeamCategory" runat="server" Width="160px" CssClass="Textbox_Display"
                    Visible="False" ReadOnly="True"></asp:TextBox>
            </td>
            <td style="width: 85px">
                &nbsp;
            </td>
            <td>
                &nbsp;
            </td>
        </tr>
        <tr>
            <td style="width: 85px">
                <asp:Label ID="lblAllUsersView" runat="server" CssClass="Label_Left_8PT" Text="All Users View:"
                    Width="112px"></asp:Label>
            </td>
            <td style="width: 200px">
                <asp:CheckBox ID="ckAllUsersView" runat="server" CssClass="Checkbox_Default" />
            </td>
            <td style="width: 85px">
                <asp:Label ID="lblMembersOnly" runat="server" CssClass="Label_Left_8PT" Text="Members Only:"
                    Width="112px" Visible="False"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckMembersOnly" runat="server" CssClass="Checkbox_Default" Visible="False" />
            </td>
        </tr>
        <tr>
            <td style="width: 85px">
                <asp:Label ID="lblMaintenanceUserID" runat="server" Width="134px" Text="Maintenance UserID:"
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="width: 200px">
                <asp:TextBox ID="txtMaintenanceUserID" runat="server" Width="80px" MaxLength="10"
                    CssClass="Textbox_Display" ReadOnly="True"></asp:TextBox>
            </td>
            <td style="width: 80px">
                <asp:Label ID="lblMaintenanceDate" runat="server" Width="150px" Text="Maintenance Date:"
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtMaintenanceDate" runat="server" Width="150px" MaxLength="10"
                    CssClass="Textbox_Display" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
    </table>
    <table id="Table4" style="width: 761px" cellspacing="0" cellpadding="0">
        <tr>
            <td>
                <br />
                <asp:Label ID="lblTeamActionItems" runat="server" Width="150px" Text="Open Action Items:"
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
        </tr>
        <tr>
            <td style="width: 603px" align="left">
                <asp:GridView ID="gvTeamActionItems" runat="server" AutoGenerateColumns="False" SkinID="GridView"
                    Width="100%" EmptyDataText="No Open Action Items">
                    <Columns>
                        <asp:BoundField DataField="ActionNumber" HeaderText="No.">
                            <ItemStyle />
                        </asp:BoundField>
                        <asp:BoundField DataField="Stepno" HeaderText="Step"></asp:BoundField>
                        <asp:BoundField DataField="UserName" HeaderText="Who">
                            <ItemStyle Wrap="False"></ItemStyle>
                        </asp:BoundField>
                        <asp:BoundField DataField="AssignedToOther" HeaderText="Others"></asp:BoundField>
                        <asp:BoundField DataField="ActionItem" HeaderText="Action Item">
                            <ItemStyle Wrap="False"></ItemStyle>
                        </asp:BoundField>
                        <asp:BoundField DataField="TargetDate" HeaderText="By When" DataFormatString="{0:yyyy/MM/dd}">
                            <ItemStyle Wrap="False"></ItemStyle>
                        </asp:BoundField>
                    </Columns>
                </asp:GridView>
            </td>
        </tr>
        <tr>
            <td>
                <br />
            </td>
        </tr>
        <tr>
            <td>
                <br />
                <asp:Label ID="lblTeamMembership" runat="server" Width="150px" Text="Team Membership:"
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
        </tr>
        <tr>
            <td style="width: 603px" align="left">
                <asp:GridView ID="gvTeamMembership" runat="server" AutoGenerateColumns="False" SkinID="GridView"
                    Width="100%">
                    <Columns>
                        <asp:BoundField DataField="UserName" HeaderText="User Name" ReadOnly="True" />
                        <asp:BoundField DataField="Title" HeaderText="Title" ReadOnly="True" />
                        <asp:BoundField DataField="Role" HeaderText="Role" ReadOnly="True" />
                    </Columns>
                </asp:GridView>
            </td>
        </tr>
        <tr>
            <td>
                <br />
                <asp:Label ID="lblTeamTrackers" runat="server" Width="150px" Text="Team Savings Trackers:"
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
        </tr>
        <tr>
            <td style="width: 603px" align="left">
                <asp:GridView ID="gvTeamTrackers" runat="server" AutoGenerateColumns="False" SkinID="GridView"
                    Width="100%" EmptyDataText="No Team Savings Trackers">
                    <Columns>
                        <asp:BoundField DataField="Tracker" HeaderText="Tracker" ReadOnly="True" />
                        <asp:BoundField DataField="Description" HeaderText="Description" ReadOnly="True" />
                        <asp:BoundField DataField="SavingsCategory" HeaderText="Category" ReadOnly="True" />
                        <asp:BoundField DataField="TrackerValueUOM" HeaderText="UOM" ReadOnly="True" />
                        <asp:BoundField DataField="Interface" HeaderText="Interface" ReadOnly="True" />
                        <asp:BoundField DataField="Active" HeaderText="Active" ReadOnly="True" />
                    </Columns>
                </asp:GridView>
            </td>
        </tr>
        <tr>
            <td>
                <br />
                <asp:Label ID="lblTeamKPI" runat="server" Width="150px" Text="Team KPIs:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
        </tr>
        <tr>
            <td style="width: 603px" align="left">
                <asp:GridView ID="gvTeamKPIs" runat="server" AutoGenerateColumns="False" SkinID="GridView"
                    Width="100%" EmptyDataText="No Team KPIs">
                    <Columns>
                        <asp:BoundField DataField="KPI" HeaderText="KPI" />
                    </Columns>
                </asp:GridView>
            </td>
        </tr>
        <tr>
            <td>
                <br />
            </td>
        </tr>
        <tr>
            <td style="width: 603px" align="left">
                <asp:Label ID="lblTeamPhoto" runat="server" Width="544px" Visible="False" ForeColor="Red"
                    Text="Team Photo file name must contain TeamPhoto example; TeamPhoto.jpg or WL522-0502 TeamPhoto.gif"
                    CssClass="Label_Left_8PT"></asp:Label><ApplicationControls:Attachments ID="ucTeamAttachments"
                        runat="server"></ApplicationControls:Attachments>
            </td>
        </tr>
    </table>
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK"></asp:Button>
                </td>
                <td style="width: 110px">
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                        CausesValidation="False"></asp:Button>
                </td>
                <td style="width: 130px">
                    <asp:Button ID="btnTeamMembership" runat="server" Width="119px" CssClass="Button_Default"
                        Text="Team Membership"></asp:Button>
                </td>
                <td class="style1">
                    <asp:Button ID="btnTeamUsers" runat="server" Width="119px" CssClass="Button_Default"
                        Text="Team Users"></asp:Button>
                </td>
                <td class="style2">
                    <asp:Button ID="btnTeamTrackers" runat="server" CssClass="Button_Default" Text="Savings Trackers"
                        Width="119px" />
                </td>
                <td>
                    <asp:Button ID="btnTeamKPI" runat="server" CssClass="Button_Default" Text="Team KPI"
                        Width="119px" />
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlExit" runat="server" Visible="False">
        <table id="Table5" class="Table_Default">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                    </asp:Button>
                </td>
                <td style="width: 130px">
                    <asp:Button ID="btnTeamMembership2" runat="server" Width="119px" CssClass="Button_Default"
                        Text="Team Membership" CausesValidation="False"></asp:Button>
                </td>
                <td class="style1">
                    <asp:Button ID="btnTeamUsers2" runat="server" Width="119px" CssClass="Button_Default"
                        Text="Team Users" CausesValidation="False"></asp:Button>
                </td>
                <td class="style2">
                    <asp:Button ID="btnTeamTrackers2" runat="server" CssClass="Button_Default" Text="Savings Trackers"
                        Width="119px" />
                </td>
                <td class="style3">
                    <asp:Button ID="btnTeamKPI2" runat="server" CssClass="Button_Default" Text="Team KPI"
                        Width="119px" />
                </td>
                <td>
                    <asp:Button ID="btnEditTeam" runat="server" CssClass="Button_Default" Text="Edit Team"
                        Visible="False" Width="119px" />
                </td>
            </tr>
        </table>
    </asp:Panel>
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False"
        Translate="true" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>

    <script type="text/javascript">
        function loaded() {
            var filePath = document.getElementById('ctl00_ContentPlaceHolder1_fiTeamFolder').value;
            var teamFolder = document.getElementById('ctl00_ContentPlaceHolder1_txtTeamFolder');
            if (teamFolder != null) {
                teamFolder.value = filePath.substr(0, filePath.lastIndexOf("\\"));

                var fil1 = document.getElementById('ctl00_ContentPlaceHolder1_fiTeamFolder');
                var fil2 = fil1.cloneNode(false);
                fil1.parentNode.replaceChild(fil2, fil1);
            }
        }
    </script>

</asp:Content>
