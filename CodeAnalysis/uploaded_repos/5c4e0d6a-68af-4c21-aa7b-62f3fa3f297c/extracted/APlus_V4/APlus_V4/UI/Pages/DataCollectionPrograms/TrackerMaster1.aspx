<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TrackerMaster1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TrackerMaster1"
    Title="Savings Tracker Maintenance" %>

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
                ShowEdit="True" NewLinkCaption="Savings Tracker" RedirectProgramName="TrackerMaster2"
                FormName="Tracker Maintenance" ProgramName="TrackerMaster1" CommandText="spSelTrackersListing"
                ProgramMode="TrackerMode" AlternatingRows="True" Translate="True">
                <GridColumns>
                    <CC1:MasterControlField Visible="False" DataField="TrackerID" HeaderText="TrackerID" />
                    <CC1:MasterControlField DataField="Team" SortExpression="Team|Tracker" HeaderText="Team" />
                    <CC1:MasterControlField DataField="TeamName" SortExpression="TeamName|Tracker" HeaderText="Team Name" />
                    <CC1:MasterControlField DataField="TeamStatus" SortExpression="TeamStatus|Team" HeaderText="Team Status" />
                    <CC1:MasterControlField DataField="Tracker" SortExpression="Tracker" HeaderText="Savings Tracker" />
                    <CC1:MasterControlField DataField="TrackerTypes" SortExpression="TrackerTypes" HeaderText="Savings Types"
                        ShowReturns="true" />
                    <CC1:MasterControlField DataField="SavingsCategory" SortExpression="SavingsCategory"
                        HeaderText="Category" />
                    <CC1:MasterControlField DataField="TrackerValueUOM" SortExpression="TrackerValueUOM"
                        HeaderText="UOM" />
                    <CC1:MasterControlField DataField="Historic" SortExpression="Historic" HeaderText="Historic"
                        DataFormatString="{0:0.####}" ItemStyle-HorizontalAlign="Right">
                        <ItemStyle HorizontalAlign="Right" />
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="Target" SortExpression="Target" HeaderText="Target"
                        DataFormatString="{0:0.####}" ItemStyle-HorizontalAlign="Right">
                        <ItemStyle HorizontalAlign="Right" />
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="StartPeriod" SortExpression="StartPeriod" HeaderText="Start Period"
                        HtmlEncode="false" DataFormatString="{0:yyyy/MM/dd}" />
                    <CC1:MasterControlField DataField="Description" SortExpression="Description" HeaderText="Description"
                        ShowReturns="true" />
                    <CC1:MasterControlField DataField="Interface" HeaderText="Interface" SortExpression="Interface" />
                    <CC1:MasterControlField DataField="Active" SortExpression="Active" HeaderText="Active" />
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
