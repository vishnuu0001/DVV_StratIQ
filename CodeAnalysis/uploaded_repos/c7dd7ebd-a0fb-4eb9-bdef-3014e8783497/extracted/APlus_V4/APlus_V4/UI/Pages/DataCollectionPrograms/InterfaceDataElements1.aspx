<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="InterfaceDataElements1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.InterfaceDataElements1"
    Title="OptiRep/SAP values w/o Data Elements" %>

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
            <CC1:MasterControl ID="MasterControl1" runat="server" ShowAdd="False" ShowDelete="False"
                ShowView="false" ShowEdit="false" NewLinkCaption="" RedirectProgramName="InterfaceDataElements1"
                FormName="OptiRep/SAP values w/o Data Elements" ProgramName="InterfaceDataElements1" CommandText="spSelInterfaceDataElementsOptiRep"
                ProgramMode="Mode" AlternatingRows="True" ShowRowCount="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="Site" SortExpression="Site" HeaderText="Site" />
                    <CC1:MasterControlField DataField="Source" SortExpression="Source" HeaderText="Source" />
                    <CC1:MasterControlField DataField="DataElement" SortExpression="DataElement" HeaderText="Data Element" />
                    <CC1:MasterControlField DataField="APP_KPIKEY" SortExpression="APP_KPIKEY" HeaderText="KPI Key" />
                    <CC1:MasterControlField DataField="APP_MILL" SortExpression="APP_MILL" HeaderText="App Mill" />
                    <CC1:MasterControlField DataField="APP_IDENTKEY" SortExpression="APP_IDENTKEY" HeaderText="App Ident Key" />
                    <CC1:MasterControlField DataField="APP_IDENT" SortExpression="APP_IDENT" HeaderText="App Ident" />
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
