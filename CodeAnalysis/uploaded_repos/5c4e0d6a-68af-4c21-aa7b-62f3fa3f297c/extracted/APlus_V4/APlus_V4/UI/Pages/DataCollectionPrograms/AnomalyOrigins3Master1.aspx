<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="AnomalyOrigins3Master1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.AnomalyOrigins3Master1"
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
            <CC1:MasterControl ID="MasterControl1" runat="server" CommandText="spSelAnomalyOrigins3"
                FormName="Anomaly Origin 3 Maintenance" NewLinkCaption="Anomaly Origin 3" ProgramMode="Origin3Mode"
                ProgramName="AnomalyOrigins3Master1" RedirectProgramName="AnomalyOrigins3Master2"
                ShowExport="True" ShowView="False" RaiseExitEvent="True" AlternatingRows="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="Site" HeaderText="Site" SortExpression="Site">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="AnomalyOrigin1" HeaderText="Anomaly Origin 1"
                        SortExpression="AnomalyOrigin1">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="AnomalyOrigin2" HeaderText="Anomaly Origin 2"
                        SortExpression="AnomalyOrigin2">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="AnomalyOrigin2ID" HeaderText="AnomalyOrigin2ID"
                        Visible="false">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="AnomalyOrigin3ID" HeaderText="AnomalyOrigin3ID"
                        Visible="false">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="AnomalyOrigin3" HeaderText="Anomaly Origin 3"
                        SortExpression="AnomalyOrigin3">
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
