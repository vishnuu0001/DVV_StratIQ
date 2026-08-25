<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="InterfaceDataElementsMaster1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.InterfaceDataElementsMaster1"
    Title="Interface Data Elements Maintenance" %>

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
                ShowView="True" ShowEdit="True" NewLinkCaption="Data Element" RedirectProgramName="InterfaceDataElementsMaster2"
                FormName="Interface Data Elements Maintenance" ProgramName="InterfaceDataElementsMaster1"
                CommandText="spSelInterfaceDataElementsMaster" ProgramMode="DataElementMode" AlternatingRows="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="Site" SortExpression="Site" HeaderText="Site" />
                    <CC1:MasterControlField DataField="Source" SortExpression="Source" HeaderText="Source" />
                    <CC1:MasterControlField DataField="DataElement" SortExpression="DataElement" HeaderText="Data Element" />
                    <CC1:MasterControlField DataField="UOM" SortExpression="UOM" HeaderText="UOM" />
                    <CC1:MasterControlField DataField="KPIDailyValue" SortExpression="KPIDailyValue"
                        HeaderText="Daily" />
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
