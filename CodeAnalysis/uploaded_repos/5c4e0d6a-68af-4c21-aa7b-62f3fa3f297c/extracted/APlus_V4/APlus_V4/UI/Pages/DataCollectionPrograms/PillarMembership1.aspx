<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="PillarMembership1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.PillarMembership1"
    Title="Pillar Membership Maintenance" %>

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
            <CC1:MasterControl ID="MasterControl1" runat="server" ShowAdd="True" ShowDelete="True"
                ShowEdit="True" ShowView="True" NewLinkCaption="Pillar Membership" RedirectProgramName="PillarMembershipMasterMaintenance2"
                FormName="Pillar Membership Maintenance" ProgramName="PillarMembership1" CommandText="spSelPillarMemberShip"
                ProgramMode="PillarMembershipMode" ShowExport="True" AlternatingRows="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="Site" SortExpression="Site" HeaderText="Site" />
                    <CC1:MasterControlField DataField="PillarListing" SortExpression="PillarListing"
                        HeaderText="Pillar" />
                    <CC1:MasterControlField DataField="LastName" SortExpression="LastName" HeaderText="Last Name" />
                    <CC1:MasterControlField DataField="FirstName" SortExpression="FirstName" HeaderText="First Name" />
                    <CC1:MasterControlField DataField="UserID" SortExpression="UserID" HeaderText="UserID" />
                    <CC1:MasterControlField DataField="Role" SortExpression="Role" HeaderText="Role" />
                    <CC1:MasterControlField DataField="DateJoined" HeaderText="Date Joined" HtmlEncode="false" />
                    <CC1:MasterControlField DataField="Active" SortExpression="Active" HeaderText="Active" />
                    <CC1:MasterControlField Visible="False" DataField="PillarAbbrev" HeaderText="Pillar" />
                    <CC1:MasterControlField Visible="False" DataField="SiteID" HeaderText="SiteID" />
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
