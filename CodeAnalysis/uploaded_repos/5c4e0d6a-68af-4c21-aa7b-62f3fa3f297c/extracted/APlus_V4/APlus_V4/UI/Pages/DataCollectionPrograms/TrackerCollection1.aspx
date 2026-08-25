<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TrackerCollection1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TrackerCollection1"
    Title="Savings Types Maintenance" %>

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
                ShowEdit="True" NewLinkCaption="Savings Type" RedirectProgramName="TrackerCollection2"
                FormName="Tracker Maintenance" ProgramName="TrackerCollection1" CommandText="spSelTrackerCollections"
                ProgramMode="TrackerCollectionMode" AlternatingRows="True" Translate="true">
                <GridColumns>
                    <CC1:MasterControlField Visible="False" DataField="TrackerCollectionID" HeaderText="TrackerCollectionID" />
                    <CC1:MasterControlField Visible="False" DataField="TrackerID" HeaderText="TrackerID" />
                    <CC1:MasterControlField Visible="False" DataField="TrackerTypeID" HeaderText="TrackerTypeID" />
                    <CC1:MasterControlField DataField="Team" SortExpression="Team" HeaderText="Team" />
                    <CC1:MasterControlField DataField="Tracker" SortExpression="Tracker" HeaderText="Savings Tracker" />
                    <CC1:MasterControlField DataField="TrackerType" SortExpression="TrackerType" HeaderText="Savings Type" />
                    <CC1:MasterControlField DataField="SavingsType" SortExpression="SavingsType" HeaderText="Savings" />
                    <CC1:MasterControlField DataField="Formula" SortExpression="Formula" HeaderText="Formula" />
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
