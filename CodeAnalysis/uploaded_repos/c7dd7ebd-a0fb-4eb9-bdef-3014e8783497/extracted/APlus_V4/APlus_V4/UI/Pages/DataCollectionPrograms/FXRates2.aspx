<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="FXRates2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.FXRates2"
    Title="FX Rates Maintenance" %>

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
            <CC1:MasterControl ID="mcFXRateElement" runat="server" ShowView="False" ShowAdd="False"
                ShowDelete="False" ShowEdit="False" NewLinkCaption="FX Rate" RedirectProgramName="FXRates3"
                FormName="FX Rate Maintenance" ProgramName="FXRates2" PrimaryControl="false"
                CommandText="spSelFXRateElements" ProgramMode="FXRateMode" AlternatingRows="True"
                UseScrollingColor="False">
                <GridColumns>
                    <CC1:MasterControlField Visible="False" DataField="FXRateID" HeaderText="FXRateID" />
                    <CC1:MasterControlField DataField="FXRateElement" HeaderText="Element" />
                    <CC1:MasterControlField DataField="FXRateFrom" HeaderText="From" />
                    <CC1:MasterControlField DataField="FXRateTo" HeaderText="To" />
                    <CC1:MasterControlField DataField="FXRatePeriod" HeaderText="Cur Period" DataFormatString="{0:yyyy/MM/dd}" />
                    <CC1:MasterControlField DataField="FXRate" HeaderText="Cur Rate" />
                </GridColumns>
            </CC1:MasterControl>
            <CC1:MasterControl ID="MasterControl1" runat="server" ShowView="True" ShowAdd="True"
                ShowDelete="True" ShowEdit="True" NewLinkCaption="FX Rate" RedirectProgramName="FXRates3"
                FormName="FX Rate Maintenance" ProgramName="FXRates2" CommandText="spSelFXRates"
                ProgramMode="FXRateMode" AlternatingRows="True" RaiseExitEvent="true">
                <GridColumns>
                    <CC1:MasterControlField Visible="False" DataField="FXRateID" HeaderText="FXRateID" />
                    <CC1:MasterControlField DataField="FXRatePeriod" SortExpression="FXRatePeriod" HeaderText="Period"
                        DataFormatString="{0:yyyy/MM/dd}" />
                    <CC1:MasterControlField DataField="FXRate" SortExpression="FXRate" HeaderText="Rate" />
                    <CC1:MasterControlField DataField="LastUpdated" SortExpression="LastUpdated" HeaderText="Last Updated"
                        DataFormatString="{0:yyyy/MM/dd hh:mm}" />
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
