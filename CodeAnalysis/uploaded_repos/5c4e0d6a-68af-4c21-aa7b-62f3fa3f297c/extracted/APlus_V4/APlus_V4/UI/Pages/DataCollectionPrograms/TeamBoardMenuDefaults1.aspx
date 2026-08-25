<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TeamBoardMenuDefaults1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamBoardMenuDefaults1"
    Title="Team Board Menu Defaults" %>

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
            <CC1:MasterControl ID="MasterControl1" runat="server" ProgramMode="TeamBoardMenuDefaultsMode"
                ShowAdd="True" ShowDelete="True" ShowEdit="True" ShowView="True" NewLinkCaption="Team Board Menu Default"
                RedirectProgramName="TeamBoardMenuDefaults2" FormName="Team Board Menu Defaults"
                ProgramName="TeamBoardMenuDefaults1" CommandText="spSelTeamBoardMenuDefaults"
                ShowExport="True" AlternatingRows="True" Translate="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="TeamBoardMenuDefaultsID" SortExpression="TeamBoardMenuDefaultsID"
                        Visible="false" HeaderText="ID" />
                    <CC1:MasterControlField DataField="SiteID" Visible="false" SortExpression="SiteID"
                        HeaderText="SiteID" />
                    <CC1:MasterControlField DataField="Site" HeaderText="Site" />
                    <CC1:MasterControlField DataField="BoardColumn" SortExpression="BoardColumn|BoardRow"
                        HeaderText="Column" />
                    <CC1:MasterControlField DataField="BoardRow" SortExpression="BoardRow|BoardColumn"
                        HeaderText="Row" />
                    <CC1:MasterControlField DataField="RCSequence" SortExpression="RCSequence" HeaderText="Seq" />
                    <CC1:MasterControlField DataField="BoardDescription" SortExpression="BoardDescription"
                        HeaderText="Description" />
                    <CC1:MasterControlField DataField="LinkType" HeaderText="Link Type" Visible="false" />
                    <CC1:MasterControlField DataField="Program" SortExpression="Program" HeaderText="Program" />
                    <CC1:MasterControlField DataField="LinkFileURL" SortExpression="LinkFileURL" HeaderText="Link File URL" />
                    <CC1:MasterControlField DataField="BoardDefault" SortExpression="BoardDefault" HeaderText="Default" />
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
