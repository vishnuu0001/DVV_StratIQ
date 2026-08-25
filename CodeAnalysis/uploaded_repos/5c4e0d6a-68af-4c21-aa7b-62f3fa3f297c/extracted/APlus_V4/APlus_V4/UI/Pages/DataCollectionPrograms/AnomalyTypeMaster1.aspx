<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="AnomalyTypeMaster1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.AnomalyTypeMaster1"
    Title="Anomaly Type Maintenance" %>

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
                Translate="true" ShowEdit="True" NewLinkCaption="Anomaly Type" RedirectProgramName="AnomalyTypeMaster2"
                FormName="Anomaly Type Maintenance" ProgramName="AnomalyTypeMaster1" CommandText="spSelAnomalyTypeMaster"
                ProgramMode="Mode" AlternatingRows="True">
                <GridColumns>
                    <CC1:MasterControlField Visible="False" DataField="AnomalyTypeID" HeaderText="AnomalyTypeID" />
                    <CC1:MasterControlField DataField="AnomalyType" SortExpression="AnomalyType" HeaderText="Anomaly Type" />
                    <CC1:MasterControlField DataField="CauseRequired" SortExpression="CauseRequired"
                        HeaderText="Cause Required" />
                    <CC1:MasterControlField DataField="KPIRequired" SortExpression="KPIRequired" HeaderText="KPI Required" />
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
