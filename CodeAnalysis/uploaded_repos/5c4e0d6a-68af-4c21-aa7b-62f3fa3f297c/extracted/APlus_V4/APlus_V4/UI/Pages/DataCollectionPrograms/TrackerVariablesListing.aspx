<%@ Page Language="VB" AutoEventWireup="false" CodeFile="TrackerVariablesListing.aspx.vb"
    Inherits="WebApp.APlus.UI.Pages.TrackerVariablesListing" %>

<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="asp" %>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head runat="server">
    <title>Data Elements</title>
    <script type="text/javascript" language="JavaScript" src="../../../Scripts/CommonFunctions.js"></script>
    <link href="../../../Styles/ApplicationMasterStyles.css" type="text/css" rel="stylesheet" />
</head>
<body onkeydown="javascript:DisableFunctionKeys(window.event);">
    <form id="Form1" method="post" autocomplete="on" runat="server">
    <asp:ScriptManager ID="ScriptManager1" runat="server" EnablePartialRendering="True"
        EnableScriptGlobalization="True">
    </asp:ScriptManager>
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
                ShowView="false" ShowEdit="false" NewLinkCaption="" RedirectProgramName="TrackerVariablesListing"
                FormName="Interface Data Elements Maintenance" ProgramName="TrackerVariablesListing"
                CommandText="spSelTrackerVariablesListing" ProgramMode="Mode" ShowExit="false"
                AlternatingRows="True" ShowExport="False">
                <GridColumns>
                    <CC1:MasterControlField DataField="Site" HeaderText="Site" />
                    <CC1:MasterControlField DataField="TrackerVariable" HeaderText="Variable" />
                    <CC1:MasterControlField DataField="VariableValue" HeaderText="Value" />
                </GridColumns>
            </CC1:MasterControl>
            <asp:Timer ID="Timer1" runat="server" Interval="50">
            </asp:Timer>
        </ContentTemplate>
        <Triggers>
            <asp:AsyncPostBackTrigger ControlID="Timer1" EventName="Tick" />
        </Triggers>
    </asp:UpdatePanel>
    </form>
</body>
</html>
