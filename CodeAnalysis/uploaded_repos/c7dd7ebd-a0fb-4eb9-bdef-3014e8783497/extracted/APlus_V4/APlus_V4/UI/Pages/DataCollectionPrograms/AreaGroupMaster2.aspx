<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="AreaGroupMaster2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.AreaGroupMaster2"
    Title="Area Group Maintenance" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<%@ Register Namespace="WebApp.APlus.UI.CustomControls" TagPrefix="CC2" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblAreaGroupID" runat="server" Text="Area Group ID:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtAreaGroupID" runat="server" CssClass="Textbox_Display" MaxLength="3"
                    Width="31px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblSite" runat="server" Text="Site:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSite" runat="server" CssClass="Textbox_Display" MaxLength="3"
                    Width="150px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblAreaGroup" runat="server" Text="Area Group:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtAreaGroup" runat="server" CssClass="Textbox_Entry" MaxLength="30"
                    Width="259px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqAreaGroup" runat="server" ErrorMessage="Enter Area Group"
                    ControlToValidate="txtAreaGroup" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblAreaGroupAbbrev" runat="server" Text="Area Group Abbrev:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtAreaGroupAbbrev" runat="server" CssClass="Textbox_Entry" MaxLength="5"
                    Width="50px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqAreaGroupAbbrev" runat="server" ErrorMessage="Enter Area Group Abbrev"
                    ControlToValidate="txtAreaGroupAbbrev" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblActive0" runat="server" Text="Sequence:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSequence" runat="server" CssClass="Textbox_Entry" MaxLength="3"
                    Width="50px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqSequence" runat="server" ErrorMessage="Enter Sequence"
                    ControlToValidate="txtSequence" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblActive1" runat="server" Text="Default Area:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlArea" runat="server" CssClass="DropdownList_Entry" Width="194px">
                </asp:DropDownList>
                <asp:TextBox ID="txtArea" runat="server" CssClass="Textbox_Display" ReadOnly="True"
                    Width="184px" Visible="False"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblActive" runat="server" Text="Active:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckActive" runat="server" />
            </td>
        </tr>
    </table>
    <asp:Panel runat="server" ID="pnlGrids">
        <table width="100%">
            <tr>
                <td>
                    <br />
                    <asp:Label ID="lblAreas" runat="server" Width="150px" Text="Areas:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
            </tr>
            <tr>
                <td align="left">
                    <CC2:MasterControl ID="mcAreas" runat="server" AlternatingRows="True" CommandText="spSelAreaGroupAreaMaster"
                        DeleteLabel="" EditLabel="" PrimaryControl="False" ProgramName="AreaGroupMaster2"
                        RedirectProgramName="AreaGroupMaster2" ShowAdd="False" ShowDelete="False" ShowEdit="False"
                        ShowExit="False" ShowExport="False" ShowView="False" Translate="true" Width="100%">
                        <GridColumns>
                            <CC2:MasterControlField DataField="Area" HeaderText="Area">
                            </CC2:MasterControlField>
                            <CC2:MasterControlField DataField="AreaAbbrev" HeaderText="Abbreviation">
                            </CC2:MasterControlField>
                            <CC2:MasterControlField DataField="Active" HeaderText="Active">
                            </CC2:MasterControlField>
                        </GridColumns>
                    </CC2:MasterControl>
                </td>
            </tr>
            <tr>
                <td>
                    <br />
                    <asp:Label ID="lblUsers" runat="server" Width="150px" Text="Users:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
            </tr>
            <tr>
                <td align="left">
                    <CC2:MasterControl ID="mcUsers" runat="server" AlternatingRows="True" CommandText="spSelAreaGroupUserMasterByAreaGroup"
                        DeleteLabel="" EditLabel="" PrimaryControl="False" ProgramName="AreaGroupMaster2"
                        RedirectProgramName="AreaGroupMaster2" ShowAdd="False" ShowDelete="False" ShowEdit="False"
                        ShowExit="False" ShowExport="False" ShowView="False" Translate="true" Width="100%">
                        <GridColumns>
                            <CC2:MasterControlField DataField="UserName" HeaderText="User" />
                        </GridColumns>
                    </CC2:MasterControl>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK" EnableViewState="False">
                    </asp:Button>
                </td>
                <td align="left" class="style1">
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                        CausesValidation="False"></asp:Button>
                </td>
                <td align="left" class="style1">
                    <asp:Button ID="btnAreas" runat="server" CausesValidation="False" CssClass="Button_Default"
                        Text="Areas" />
                </td>
                <td align="left">
                    <asp:Button ID="btnUsers" runat="server" CausesValidation="False" CssClass="Button_Default"
                        Text="Users" />
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlExit" runat="server" Visible="False">
        <table id="Table3" class="Table_Default">
            <tr>
                <td class="style1">
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                    </asp:Button>
                </td>
                <td class="style1">
                    <asp:Button ID="btnAreas1" runat="server" CausesValidation="False" CssClass="Button_Default"
                        Text="Areas" />
                </td>
                <td>
                    <asp:Button ID="btnUsers1" runat="server" CausesValidation="False" CssClass="Button_Default"
                        Text="Users" />
                </td>
            </tr>
        </table>
    </asp:Panel>
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
<asp:Content ID="Content2" runat="server" ContentPlaceHolderID="ContentHeader">
    <style type="text/css">
        .style1
        {
            width: 175px;
        }
    </style>
</asp:Content>
