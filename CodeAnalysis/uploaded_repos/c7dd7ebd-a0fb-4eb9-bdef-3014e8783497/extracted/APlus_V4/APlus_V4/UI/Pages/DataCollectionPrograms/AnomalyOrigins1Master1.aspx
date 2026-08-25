<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="AnomalyOrigins1Master1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.AnomalyOrigins1Master1"
    Title="Anomaly Origins Maintenance" %>

<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="asp" %>
<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
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
    <asp:UpdatePanel ID="UpdatePanel1" runat="server" UpdateMode="Conditional">
        <ContentTemplate>
            <CC1:MasterControl ID="MasterControl1" runat="server" CommandText="spSelAnomalyOrigins1"
                FormName="Anomaly Origins 1 Maintenance" NewLinkCaption="Anomaly Origin 1" ProgramMode="Origin1Mode"
                ProgramName="AnomalyOrigins1Master1" RedirectProgramName="AnomalyOrigins1Master2"
                ShowExport="True" ShowView="True" ViewLabel="Select" RaiseExitEvent="True" AlternatingRows="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="AnomalyOrigin1ID" HeaderText="AnomalyOrigin1ID"
                        Visible="False">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="Site" HeaderText="Site" ShowReturns="False" SortExpression="Site">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="AnomalyOrigin1" SortExpression="AnomalyOrigin1"
                        HeaderText="Anomaly Origin 1">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="AnomalyOrigin2" SortExpression="AnomalyOrigin2"
                        HeaderText="Origin 2 Count">
                    </CC1:MasterControlField>
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
