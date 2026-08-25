<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="EntityMaster1.aspx.vb" Inherits="WebApp.APlus.UI.SLICE.EntityMaster1"
    Title="Entity Master" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="asp" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <asp:UpdateProgress ID="UpdateProgress1" runat="server" DisplayAfter="50">
        <ProgressTemplate>
            <div style="position: absolute; z-index: 1;">
                <asp:Image runat="server" ID="imgWait" Height="48" Width="48" ImageUrl="~/images/barcircle.gif" />
                <asp:AlwaysVisibleControlExtender ID="imgWait_AlwaysVisibleControlExtender" runat="server"
                    Enabled="True" TargetControlID="imgWait" VerticalSide="Middle" HorizontalSide="Center">
                </asp:AlwaysVisibleControlExtender>
            </div>
        </ProgressTemplate>
    </asp:UpdateProgress>
    <asp:UpdatePanel ID="UpdatePanel1" runat="server">
        <ContentTemplate>
            <table>
                <tr>
                    <td class="style2">
                        <asp:Label ID="Label3" runat="server">Workcenter:</asp:Label>
                    </td>
                    <td class="style1">
                        <asp:Label ID="Label1" runat="server">Entity:</asp:Label>
                    </td>
                    <td>
                        <asp:Label ID="Label2" runat="server">Location:</asp:Label>
                    </td>
                </tr>
                <tr>
                    <td class="style2">
                        <asp:DropDownList ID="ddlWorkcenter" runat="server" CssClass="DropdownList_Entry"
                            Width="225px">
                        </asp:DropDownList>
                    </td>
                    <td class="style1">
                        <asp:TextBox ID="txtEntity" runat="server" CssClass="Textbox_Entry" MaxLength="25"
                            Width="160px"></asp:TextBox>
                    </td>
                    <td>
                        <asp:TextBox ID="txtLocation" runat="server" CssClass="Textbox_Entry" MaxLength="25"
                            Width="165px"></asp:TextBox>
                    </td>
                </tr>
            </table>
            <table width="100%">
                <tr>
                    <td style="width: 146px">
                        <asp:Button ID="btnApplyFilter" TabIndex="3" Text="Apply Filter" CssClass="Button_Default"
                            runat="server"></asp:Button>
                    </td>
                </tr>
            </table>
            <hr style="width: 99%; color: black; height: 1px">
            <CC1:MasterControl ID="MasterControl1" runat="server" CommandText="spSelEntityMasterFilter"
                FormName="Entity Master" NewLinkCaption="Entity" ProgramMode="EntityMasterMode"
                ProgramName="EntityMaster1" RedirectProgramName="EntityMaster2" ShowExport="False"
                AlternatingRows="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="EntityID" Visible="False" HeaderText="Entity ID" />
                    <CC1:MasterControlField DataField="Workcenter" SortExpression="Workcenter" HeaderText="Workcenter" />
                    <CC1:MasterControlField ShowReturns="False" DataField="SAPEntity" SortExpression="SAPEntity"
                        HeaderText="SAP Entity" />
                    <CC1:MasterControlField ShowReturns="False" DataField="Entity" SortExpression="Entity"
                        HeaderText="Entity" />
                    <CC1:MasterControlField ShowReturns="False" DataField="Location" SortExpression="Location"
                        HeaderText="Location" />
                    <CC1:MasterControlField ShowReturns="False" DataField="WorkcenterID" Visible="False"
                        HeaderText="WorkcenterID" />
                </GridColumns>
            </CC1:MasterControl>
            <asp:Timer ID="Timer1" runat="server" Interval="50">
            </asp:Timer>
        </ContentTemplate>
        <Triggers>
            <asp:AsyncPostBackTrigger ControlID="Timer1" EventName="Tick" />
        </Triggers>
    </asp:UpdatePanel>
</asp:Content>
<asp:Content ID="Content2" runat="server" contentplaceholderid="ContentHeader">
    <style type="text/css">
        .style1
        {
            width: 180px;
        }
        .style2
        {
            width: 250px;
        }
    </style>
</asp:Content>

