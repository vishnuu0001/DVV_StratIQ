<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TeamBoardMenuOptionMaster2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamBoardMenuOptionMaster2"
    Title="Team Board Menu Option Master" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1" cellspacing="2" cellpadding="2" border="0">
        <tr>
            <td style="width: 126px">
                <asp:Label ID="lblTeam" runat="server" Text="Team:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtTeam" runat="server" CssClass="Textbox_Display" MaxLength="10"
                    Width="72px"></asp:TextBox><asp:RequiredFieldValidator ID="reqTeam" runat="server"
                        ErrorMessage="Enter Team" ControlToValidate="txtTeam" Display="None"></asp:RequiredFieldValidator><asp:TextBox
                            ID="txtLinkType" runat="server" CssClass="Textbox_Display" Width="16px" ReadOnly="True"
                            Visible="False"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 126px">
                <asp:Label ID="lblBoardColumn" runat="server" Text="Board Column:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtBoardColumn" runat="server" CssClass="Textbox_Entry" MaxLength="1"
                    Width="16px"></asp:TextBox><asp:RequiredFieldValidator ID="reqBoardColumn" runat="server"
                        ErrorMessage="Enter Board Column" ControlToValidate="txtBoardColumn" CssClass="Label_Left_8PT"
                        Display="None"></asp:RequiredFieldValidator><asp:RangeValidator ID="rngBoardColumn"
                            runat="server" ErrorMessage="Enter 1-9" ControlToValidate="txtBoardColumn" MaximumValue="9"
                            CssClass="Label_Left_8PT" MinimumValue="1" Text="Enter 1-9"></asp:RangeValidator><asp:TextBox
                                ID="txtBoardColumnOld" runat="server" CssClass="Textbox_Display" MaxLength="1"
                                Width="16px" Visible="False"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 126px">
                <asp:Label ID="lblBoardRow" runat="server" Text="Board Row:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtBoardRow" runat="server" CssClass="Textbox_Entry" MaxLength="1"
                    Width="16px"></asp:TextBox><asp:RequiredFieldValidator ID="reqBoardRow" runat="server"
                        ErrorMessage="Enter Board Row" ControlToValidate="txtBoardRow" CssClass="Label_Left_8PT"
                        Display="None"></asp:RequiredFieldValidator><asp:RangeValidator ID="rngBoardRow"
                            runat="server" ErrorMessage="Enter 1-9" ControlToValidate="txtBoardRow" CssClass="Label_Left_8PT"
                            MaximumValue="9" MinimumValue="1" Text="Enter 1-9"></asp:RangeValidator><asp:TextBox
                                ID="txtBoardRowOld" runat="server" CssClass="Textbox_Display" MaxLength="1" Width="16px"
                                Visible="False"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 126px">
                <asp:Label ID="lblRCSequence" runat="server" Text="Sequence:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtRCSequence" runat="server" CssClass="Textbox_Entry" MaxLength="1"
                    Width="16px"></asp:TextBox><asp:RequiredFieldValidator ID="reqRCSequence" runat="server"
                        CssClass="Label_Left_8PT" ErrorMessage="Enter Sequence" ControlToValidate="txtRCSequence"
                        Display="None"></asp:RequiredFieldValidator><asp:RangeValidator ID="rngRCSequence"
                            runat="server" ErrorMessage="Enter 1-9" ControlToValidate="txtRCSequence" MaximumValue="9"
                            MinimumValue="1" Text="Enter 1-9" CssClass="Label_Left_8PT"></asp:RangeValidator><asp:TextBox
                                ID="txtRCSequenceOld" runat="server" CssClass="Textbox_Display" MaxLength="1"
                                Width="16px" Visible="False"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 126px">
                <asp:Label ID="lblBoardDescription" runat="server" CssClass="Label_Left_8PT" Text="Board Description:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtBoardDescription" runat="server" CssClass="Textbox_Entry" MaxLength="55"
                    Width="330px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 126px">
                <br />
            </td>
            <td>
                <br />
                <asp:Label ID="Label3" runat="server" Width="336px" Text="Select no more than one of the following:"
                    CssClass="Label_Left_8PT"></asp:Label><br />
                <br />
            </td>
        </tr>
        <tr>
            <td style="width: 126px; vertical-align: top;">
                <asp:Label ID="lblProgram" runat="server" Text="Program:" CssClass="Label_Left_8PT"></asp:Label><br />
            </td>
            <td>
                <asp:DropDownList ID="ddlProgram" runat="server" Width="335px" CssClass="DropdownList_Entry"
                    AutoPostBack="True">
                </asp:DropDownList>
                <asp:TextBox ID="txtProgram" runat="server" CssClass="Textbox_Display" Width="335px"
                    ReadOnly="True"></asp:TextBox><br />
                <br />
                <span>
                    <asp:Label ID="Label6" runat="server" Text="OR" CssClass="Label_Left_8PT"></asp:Label></span>
            </td>
        </tr>
        <tr>
            <td style="width: 126px; vertical-align: top;">
                <asp:Label ID="lblLinkFileURL" runat="server" Text="Team Document Link:" CssClass="Label_Left_8PT"></asp:Label><br />
            </td>
            <td>
                <asp:TextBox ID="txtLinkFileURL" runat="server" CssClass="Textbox_Entry" MaxLength="150"
                    Width="400px"></asp:TextBox><br />
                <asp:Label ID="Label4" runat="server" Text="(Note: File must exist in the Team Folder)"
                    CssClass="Label_Left_8PT"></asp:Label><br />
                <br />
                <span>
                    <asp:Label ID="Label7" runat="server" Text="OR" CssClass="Label_Left_8PT"></asp:Label></span>
            </td>
            <tr>
                <td style="width: 126px; vertical-align: top;">
                    <asp:Label ID="lblURLLink" runat="server" Text="URL Link:" CssClass="Label_Left_8PT"></asp:Label><br />
                </td>
                <td>
                    <asp:TextBox ID="txtURLLink" runat="server" CssClass="Textbox_Entry" MaxLength="250"
                        Width="500px"></asp:TextBox><br />
                    <br />
                    <span>
                        <asp:Label ID="Label8" runat="server" Text="OR" CssClass="Label_Left_8PT"></asp:Label></span>
                </td>
            </tr>
            <tr>
                <td style="width: 126px; vertical-align: top;">
                    <asp:Label ID="lblTrainingMatrixLink" runat="server" Text="Training Matrix Link:"
                        CssClass="Label_Left_8PT"></asp:Label><br />
                </td>
                <td>
                    <asp:DropDownList ID="ddlJob" runat="server" Width="335px" CssClass="DropdownList_Entry"
                        AutoPostBack="True">
                    </asp:DropDownList>
                    <asp:TextBox ID="txtJob" runat="server" CssClass="Textbox_Display" Width="335px"
                        ReadOnly="True" Visible="False"></asp:TextBox><br />
                    <br />
                    <span>
                        <asp:Label ID="Label9" runat="server" Text="OR" CssClass="Label_Left_8PT"></asp:Label></span>
                </td>
            </tr>
            <tr>
                <td style="width: 126px; vertical-align: top;">
                    <asp:Label ID="lblKPILink" runat="server" Text="KPI Link:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:DropDownList ID="ddlKPI" runat="server" Width="335px" CssClass="DropdownList_Entry"
                        AutoPostBack="True">
                    </asp:DropDownList>
                    <asp:TextBox ID="txtKPI" runat="server" CssClass="Textbox_Display" Width="335px"
                        ReadOnly="True" Visible="False"></asp:TextBox>&nbsp;
                    <asp:DropDownList ID="ddlKPISite" runat="server" CssClass="DropdownList_Entry" Width="194px"
                        AutoPostBack="True">
                    </asp:DropDownList>
                    <br />
                    <br />
                    <span>
                        <asp:Label ID="Label1" runat="server" Text="OR" CssClass="Label_Left_8PT"></asp:Label></span>
                </td>
            </tr>
            <tr>
                <td style="width: 126px; vertical-align: top;">
                    <asp:Label ID="lblSavingsTrackerLink" runat="server" Text="Savings Tracker Link:"
                        CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:DropDownList ID="ddlTracker" runat="server" Width="335px" CssClass="DropdownList_Entry"
                        AutoPostBack="True">
                    </asp:DropDownList>
                    <asp:TextBox ID="txtTracker" runat="server" CssClass="Textbox_Display" Width="335px"
                        ReadOnly="True" Visible="False"></asp:TextBox><br />
                    <br />
                    <span>
                        <asp:Label ID="Label2" runat="server" Text="OR" CssClass="Label_Left_8PT"></asp:Label></span>
                </td>
            </tr>
            <tr>
                <td style="width: 126px; vertical-align: top;">
                    <asp:Label ID="lblTeamLink" runat="server" Text="Team Link:" CssClass="Label_Left_8PT"></asp:Label><br />
                </td>
                <td>
                    <asp:DropDownList ID="ddlLinkTeams" runat="server" Width="335px" CssClass="DropdownList_Entry"
                        AutoPostBack="True">
                    </asp:DropDownList>
                    <asp:CheckBox ID="ckClosedTeams" runat="server" AutoPostBack="True" Text="Include Closed Teams">
                    </asp:CheckBox><asp:TextBox ID="txtLinkTeam" runat="server" CssClass="Textbox_Display"
                        Width="335px" ReadOnly="True"></asp:TextBox>
                </td>
            </tr>
            <tr>
                <td style="width: 126px">
                </td>
                <td>
                    <asp:RadioButtonList ID="rblTeamProgram" runat="server" Width="296px" Height="8px"
                        RepeatDirection="Horizontal">
                        <asp:ListItem Value="TeamBoardMenu" Selected="True" Text="Team Board"></asp:ListItem>
                        <asp:ListItem Value="TeamStatus" Text="Team Status"></asp:ListItem>
                        <asp:ListItem Value="TeamOPIReports2" Text="OPI Reports"></asp:ListItem>
                    </asp:RadioButtonList>
                    <br />
                </td>
            </tr>
        </tr>
    </table>
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK" EnableViewState="False">
                    </asp:Button>
                </td>
                <td>
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                        CausesValidation="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlExit" runat="server" Visible="False">
        <table id="Table3" class="Table_Default">
            <tr>
                <td>
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                    </asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False"
        Translate="true" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
