<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TeamUsers1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamUsers1"
    Title="Team Users" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="asp" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <asp:UpdateProgress ID="UpdateProgress1" runat="server" DisplayAfter="50" AssociatedUpdatePanelID="UpdatePanel1">
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
            <CC1:MasterControl ID="MasterControl1" runat="server" ProgramMode="TeamUsersMode"
                ShowAdd="True" ShowDelete="True" ShowEdit="False" ShowView="True" NewLinkCaption="Team User"
                RedirectProgramName="TeamUsers2" FormName="Team Users" ProgramName="TeamUsers1"
                CommandText="[spSelTeamUsers]" ShowExport="True" AlternatingRows="True" Translate="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="TeamID" HeaderText="TeamID" Visible="false" />
                    <CC1:MasterControlField DataField="Team" SortExpression="Team" HeaderText="Team" />
                    <CC1:MasterControlField DataField="TeamName" SortExpression="TeamName" HeaderText="Team Name" />
                    <CC1:MasterControlField DataField="LastName" SortExpression="LastName" HeaderText="Last Name" />
                    <CC1:MasterControlField DataField="FirstName" SortExpression="FirstName" HeaderText="First Name" />
                    <CC1:MasterControlField DataField="UserID" SortExpression="U.UserID" HeaderText="User ID" />
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
