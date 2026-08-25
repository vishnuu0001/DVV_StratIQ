<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="FXRatesYears.aspx.vb" Inherits="WebApp.APlus.UI.Pages.FXRatesYears"
    Title="FX Rates Years" %>

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
            <CC1:MasterControl ID="MasterControl1" runat="server" ShowView="False" ShowAdd="False"
                ShowDelete="False" ShowEdit="False" ShowExport="true" NewLinkCaption="FX Rate Year"
                RedirectProgramName="FXRatesYears" FormName="FX Rates Years" ProgramName="FXRatesYears"
                CommandText="spSelFXRatesYears" ProgramMode="FXRatesYearsMode" AlternatingRows="True">
                <GridColumns>
                    <CC1:MasterControlField Visible="False" DataField="FXRateID" HeaderText="FXRateID" />
                    <CC1:MasterControlField DataField="FXRateElement" SortExpression="FXRateElement"
                        HeaderText="Element" />
                    <CC1:MasterControlField DataField="FXRateYear" SortExpression="FXRateYear" HeaderText="Year" />
                    <CC1:MasterControlField DataField="FXRateFrom" SortExpression="FXRateFrom" HeaderText="From" />
                    <CC1:MasterControlField DataField="FXRateTo" SortExpression="FXRateTo" HeaderText="To" />
                    <CC1:MasterControlField DataField="FXRate" SortExpression="FXRate" HeaderText="Year Rate" />
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
