<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="AnomalyMaster1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.AnomalyMaster1"
    Title="My Anomalies" %>

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
            <table>
                <tr>
                    <td class="style1">
                        <asp:Label ID="lblAnomalyType" runat="server">Anomaly Type:</asp:Label>
                    </td>
                    <td class="style4">
                        <asp:DropDownList ID="ddlAnomalyType" runat="server" CssClass="DropdownList_Entry"
                            Width="190px">
                        </asp:DropDownList>
                    </td>
                    <td>
                        <asp:Label ID="lblAnomalyStatus" runat="server">Anomaly Status:</asp:Label>
                    </td>
                    <td class="style4">
                        <asp:DropDownList ID="ddlAnomalyStatus" runat="server" CssClass="DropdownList_Entry"
                            Width="190px">
                            <asp:ListItem Value=""></asp:ListItem>
                            <asp:ListItem Value="1">Pending Analysis</asp:ListItem>
                            <asp:ListItem Value="2">Open</asp:ListItem>
                            <asp:ListItem Value="3">Pending Evaluation</asp:ListItem>
                            <asp:ListItem Value="4">Processed</asp:ListItem>
                        </asp:DropDownList>
                    </td>
                    <td class="style3">
                        <asp:Label ID="lblAnomalyID" runat="server">Anomaly ID:</asp:Label>
                    </td>
                    <td>
                        <asp:TextBox ID="txtAnomalyID" runat="server" CssClass="Textbox_Entry" MaxLength="5"
                            Width="50px"></asp:TextBox>
                    </td>
                </tr>
                <tr>
                    <td class="style1">
                        <asp:Label ID="lblArea" runat="server">Area:</asp:Label>
                    </td>
                    <td class="style4">
                        <asp:DropDownList ID="ddlArea" runat="server" CssClass="DropdownList_Entry" Width="190px">
                        </asp:DropDownList>
                    </td>
                    <td>
                        &nbsp;
                    </td>
                    <td class="style4">
                        <asp:CheckBox ID="ckAllAreas" runat="server" Text="Show Supporting Areas" />
                    </td>
                    <td class="style3">
                        <asp:Label ID="lblDescription" runat="server">Description:</asp:Label>
                    </td>
                    <td>
                        <asp:TextBox ID="txtDescription" runat="server" CssClass="Textbox_Entry" MaxLength="30"
                            Width="200px"></asp:TextBox>
                    </td>
                </tr>
                <tr>
                    <td class="style1">
                        <asp:Label ID="lblResponsibleUser" runat="server">Responsible User:</asp:Label>
                    </td>
                    <td class="style4">
                        <asp:DropDownList ID="ddlResponsibleUser" runat="server" CssClass="DropdownList_Entry"
                            Width="190px">
                        </asp:DropDownList>
                    </td>
                    <td>
                        &nbsp;
                    </td>
                    <td class="style4">
                        <asp:CheckBox ID="ckSGI" runat="server" Text="Show Only SGI Anomalies" />
                    </td>
                    <td class="style3">
                        &nbsp;
                    </td>
                    <td>
                        &nbsp;
                    </td>
                </tr>
                <div runat="server" id="pnlOrigin">
                    <tr>
                        <td class="style1">
                            <asp:Label ID="lblOrigin" runat="server">Origin:</asp:Label>
                        </td>
                        <td class="style4">
                            <asp:DropDownList ID="ddlOrigin1" runat="server" CssClass="DropdownList_Entry" Width="190px">
                            </asp:DropDownList>
                        </td>
                        <td>
                            &nbsp;
                        </td>
                        <td class="style4">
                            <asp:DropDownList ID="ddlOrigin2" runat="server" CssClass="DropdownList_Entry" Width="190px">
                            </asp:DropDownList>
                        </td>
                        <td class="style3">
                            &nbsp;
                        </td>
                        <td>
                            <asp:DropDownList ID="ddlOrigin3" runat="server" CssClass="DropdownList_Entry" Width="190px">
                            </asp:DropDownList>
                        </td>
                    </tr>
                </div>
                <tr>
                    <td class="style1">
                        &nbsp;
                    </td>
                    <td class="style4">
                        &nbsp;
                    </td>
                    <td>
                        &nbsp;
                    </td>
                    <td class="style4">
                        &nbsp;
                    </td>
                    <td class="style3">
                        &nbsp;
                    </td>
                    <td>
                        &nbsp;
                    </td>
                </tr>
            </table>
            <table>
                <tr>
                    <td style="width: 146px">
                        <asp:Button ID="btnApplyFilter" TabIndex="3" Text="Apply Filter" CssClass="Button_Default"
                            runat="server"></asp:Button>
                    </td>
                    <td>
                        <asp:Button ID="btnClearFilter" TabIndex="3" Text="Clear Filter" CssClass="Button_Default"
                            runat="server"></asp:Button>
                    </td>
                </tr>
            </table>
            <hr style="width: 99%; color: black; height: 1px">
            <CC1:MasterControl ID="MasterControl1" runat="server" ShowAdd="True" ShowDelete="True"
                ShowEdit="True" NewLinkCaption="Anomaly" RedirectProgramName="AnomalyMaster2"
                FormName="Anomaly Maintenance" ProgramName="AnomalyMaster1" CommandText="spSelAnomalyMaster"
                ProgramMode="AnomalyMode" AlternatingRows="True" Translate="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="AnomalyID" HeaderText="ID" />
                    <CC1:MasterControlField Visible="False" DataField="Site" SortExpression="Site" HeaderText="Site" />
                    <CC1:MasterControlField DataField="AreaAbbrev" SortExpression="AreaAbbrev" HeaderText="Area" />
                    <CC1:MasterControlField DataField="AnomalyType" SortExpression="AnomalyType" HeaderText="Type" />
                    <CC1:MasterControlField DataField="Anomaly" SortExpression="Anomaly" HeaderText="Anomaly" />
                    <CC1:MasterControlField DataField="Subject" SortExpression="Subject" HeaderText="Description" />
                    <CC1:MasterControlField DataField="OpenActions" SortExpression="OpenActions" HeaderText="Open Actions" />
                    <CC1:MasterControlField DataField="ClosedActions" SortExpression="ClosedActions"
                        HeaderText="Closed Actions" />
                    <CC1:MasterControlField DataField="ResponsibleUser" SortExpression="ResponsibleUser"
                        HeaderText="Responsible User" />
                    <CC1:MasterControlField DataField="CreatedDateTime" SortExpression="CreatedDateTime"
                        HeaderText="Created" />
                    <CC1:MasterControlField DataField="Observations" SortExpression="Observations" HeaderText="Observations"
                        ShowReturns="true" />
                    <CC1:MasterControlField DataField="ClosedDateTime" SortExpression="ClosedDateTime"
                        HeaderText="Closed" />
                    <CC1:MasterControlField DataField="EvaluatedDateTime" SortExpression="EvaluatedDateTime"
                        HeaderText="Evaluated" />
                    <CC1:MasterControlField DataField="AnomalyOrigins" HeaderText="Origins" ShowReturns="true" />
                    <CC1:MasterControlField DataField="SGI" HeaderText="SGI" ShowReturns="true" SortExpression="SGI" />
                    <CC1:MasterControlField DataField="Attachments" HeaderText="" />
                    <CC1:MasterControlField Visible="False" DataField="EditAnomaly" HeaderText="EditAnomaly" />
                    <CC1:MasterControlField Visible="False" DataField="EditActions" HeaderText="EditActions" />
                    <CC1:MasterControlField Visible="False" DataField="AutoGenerated" HeaderText="AutoGenerated" />
                    <CC1:MasterControlField Visible="False" DataField="OpenTargetDate" HeaderText="OpenTargetDate" />
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
<asp:Content ID="Content2" runat="server" ContentPlaceHolderID="ContentHeader">
    <style type="text/css">
        .style1
        {
            width: 100px;
        }
        .style2
        {
            width: 215px;
        }
        .style3
        {
            width: 75px;
        }
        .style4
        {
            width: 200px;
        }
    </style>
</asp:Content>
