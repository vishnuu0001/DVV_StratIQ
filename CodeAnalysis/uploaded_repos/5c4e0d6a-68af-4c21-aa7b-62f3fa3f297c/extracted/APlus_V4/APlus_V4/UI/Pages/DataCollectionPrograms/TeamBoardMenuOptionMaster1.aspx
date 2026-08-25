<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TeamBoardMenuOptionMaster1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamBoardMenuOptionMaster1"
    Title="Team Board Menu Option Master" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
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
                ShowEdit="True" ShowView="True" NewLinkCaption="Team Board Menu Option" RedirectProgramName="TeamBoardMenuOptionMaster2"
                FormName="Team Board Menu Option Master Maintenance" ProgramName="TeamBoardMenuOptionMaster1"
                CommandText="spSelTeamBoardMenuOptionMasterByTeam" ProgramMode="TeamBoardMenuOptionMasterMode"
                AlternatingRows="True" Translate="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="MenuOptionID" HeaderText="MenuOptionID" Visible="false" />
                    <CC1:MasterControlField DataField="Team" HeaderText="Team" />
                    <CC1:MasterControlField DataField="BoardColumn" SortExpression="BoardColumn|BoardRow"
                        HeaderText="Column" />
                    <CC1:MasterControlField DataField="BoardRow" SortExpression="BoardRow|BoardColumn"
                        HeaderText="Row" />
                    <CC1:MasterControlField DataField="RCSequence" HeaderText="Seq" />
                    <CC1:MasterControlField DataField="LinkType" HeaderText="Link Type" />
                    <CC1:MasterControlField DataField="BoardDescription" HeaderText="Description" />
                </GridColumns>
            </CC1:MasterControl>
            <asp:Timer ID="Timer1" runat="server" Interval="50">
            </asp:Timer>
        </ContentTemplate>
        <Triggers>
            <asp:AsyncPostBackTrigger ControlID="Timer1" EventName="Tick" />
        </Triggers>
    </asp:UpdatePanel>
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False"
        Translate="true" />
</asp:Content>
