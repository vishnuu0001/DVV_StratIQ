<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="SLICEActivityMaster2.aspx.vb" Inherits="WebApp.APlus.UI.SLICE.SLICEActivityMaster2"
    Title="SLICE Activity Maintenancentitled Page" EnableTheming="true" StylesheetTheme="APlus_Default" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<%@ Register Src="../../UserControls/WorkcenterSubHeader.ascx" TagName="WorkcenterSubHeader"
    TagPrefix="uc1" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc2" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <script type="text/javascript" language="javascript" src="../../../Scripts/jquery.functions.js"></script>
    <script type="text/javascript" language="javascript">
        $(document).ready(function () {
            $("textarea[name*='txtExpand']").TextAreaExpander();
        });
    </script>
    <uc1:WorkcenterSubHeader ID="WorkcenterSubHeader1" runat="server"></uc1:WorkcenterSubHeader>
    <br />
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 150px">
                <asp:Label ID="lblSLICEActivityID" runat="server" Text="SLICE Activity ID:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSLICEActivityID" runat="server" MaxLength="10" ReadOnly="True"
                    CssClass="Textbox_Display" Width="48px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 150px; height: 2px">
                <asp:Label ID="lblSLICEActivityGroup" runat="server" CssClass="Label_Left_8PT" Text="SLICE Activity Group:"></asp:Label>
            </td>
            <td style="height: 2px">
                <asp:DropDownList ID="ddlSLICEActivityGroup" runat="server" CssClass="DropdownList_Entry"
                    Width="232px">
                </asp:DropDownList>
                <asp:TextBox ID="txtSLICEActivityGroup" runat="server" MaxLength="50" ReadOnly="True"
                    CssClass="Textbox_Display" Width="256px"></asp:TextBox><asp:RequiredFieldValidator
                        ID="reqSliceActivityGroup" runat="server" Display="None" ErrorMessage="Select Slice Activity Group"
                        ControlToValidate="ddlSliceActivityGroup"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 150px; height: 28px">
                <asp:Label ID="lblEntity" runat="server" CssClass="Label_Left_8PT" Text="Entity:">  </asp:Label>
            </td>
            <td style="height: 28px">
                <asp:DropDownList ID="ddlEntity" runat="server" CssClass="DropdownList_Entry" Width="232px">
                </asp:DropDownList>
                <asp:TextBox ID="txtEntity" runat="server" MaxLength="50" ReadOnly="True" CssClass="Textbox_Display"
                    Width="256px"></asp:TextBox><asp:RequiredFieldValidator ID="reqEntity" runat="server"
                        Display="None" ErrorMessage="Select Entity" ControlToValidate="ddlEntity"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 150px; height: 16px">
                <asp:Label ID="lblPosition" runat="server" CssClass="Label_Left_8PT" Text="Position:"></asp:Label>
            </td>
            <td style="height: 16px">
                <asp:DropDownList ID="ddlPosition" runat="server" CssClass="DropdownList_Entry" Width="232px">
                </asp:DropDownList>
                <asp:TextBox ID="txtPosition" runat="server" MaxLength="50" ReadOnly="True" CssClass="Textbox_Display"
                    Width="256px"></asp:TextBox><asp:RequiredFieldValidator ID="reqPosition" runat="server"
                        Display="None" ErrorMessage="Select Position" ControlToValidate="ddlPosition"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 150px">
                <asp:Label ID="lblPresentationSequence" runat="server" CssClass="Label_Left_8PT"
                    Text="Presentation Sequence:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtPresentationSequence" runat="server" MaxLength="4" CssClass="Textbox_Entry"
                    Width="40px"></asp:TextBox><asp:RequiredFieldValidator ID="reqPresentationSequence"
                        runat="server" Display="None" ErrorMessage="Enter Presentation Sequence" ControlToValidate="txtPresentationSequence"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 150px; height: 22px">
                <asp:Label ID="lblSLICEFrequency" runat="server" CssClass="Label_Left_8PT" Text="SLICE Frequency:"></asp:Label>
            </td>
            <td style="height: 22px">
                <asp:DropDownList ID="ddlSLICEFrequency" runat="server" CssClass="DropdownList_Entry"
                    Width="232px">
                </asp:DropDownList>
                <asp:TextBox ID="txtSLICEFrequency" runat="server" MaxLength="50" ReadOnly="True"
                    CssClass="Textbox_Display" Width="232px"></asp:TextBox><asp:RequiredFieldValidator
                        ID="reqSLICEFrequency" runat="server" Display="None" ErrorMessage="Select SLICE Frequency"
                        ControlToValidate="ddlSLICEFrequency"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 150px" valign="top">
                <asp:Label ID="lblMeasurement" runat="server" CssClass="Label_Left_8PT" Text="Measurement:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandMeasurement" runat="server" MaxLength="50" CssClass="Textbox_Entry"
                    Width="408px" TextMode="MultiLine" Height="32px"></asp:TextBox><asp:RequiredFieldValidator
                        ID="reqMeasurement" runat="server" Display="None" ErrorMessage="Enter Measurement"
                        ControlToValidate="txtExpandMeasurement" Enabled="False"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 150px; height: 37px" valign="top">
                <asp:Label ID="lblDesiredCondition" runat="server" CssClass="Label_Left_8PT" Text="Desired Condition:"></asp:Label>
            </td>
            <td style="height: 37px">
                <asp:TextBox ID="txtExpandDesiredCondition" runat="server" MaxLength="50" CssClass="Textbox_Entry"
                    Width="408px" TextMode="MultiLine" Height="32px"></asp:TextBox><asp:RequiredFieldValidator
                        ID="reqDesiredCondition" runat="server" Display="None" ErrorMessage="Enter Desired Condition"
                        ControlToValidate="txtExpandDesiredCondition"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 150px; height: 23px">
                <asp:Label ID="lblTargetTime" runat="server" CssClass="Label_Left_8PT" Text="Target Time:"></asp:Label>
            </td>
            <td style="height: 23px">
                <asp:TextBox ID="txtTargetTime" runat="server" MaxLength="50" CssClass="Textbox_Entry"
                    Width="64px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqTargetTime" runat="server" Display="None" ErrorMessage="Enter Target Time"
                    ControlToValidate="txtTargetTime"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 150px">
                <asp:Label ID="lblLastcompleted" runat="server" CssClass="Label_Left_8PT" Text="Last Completed Date:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtLastCompleted" runat="server" MaxLength="50" ReadOnly="True"
                    CssClass="Textbox_Display" Width="216px"></asp:TextBox>
            </td>
        </tr>
    </table>
    <br />
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" style="width: 488px; height: 26px" cellspacing="2" cellpadding="2"
            width="488" border="0">
            <tr>
                <td style="width: 153px" align="left">
                    <p>
                        <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK" EnableViewState="False">
                        </asp:Button></p>
                </td>
                <td align="left">
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                        CausesValidation="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <br />
    <asp:Panel ID="pnlSliceTypes" runat="server" Visible="True">
        <table id="Table2" style="width: 761px" cellspacing="0" cellpadding="0">
            <tr>
                <td align="left">
                    <CC1:MasterControl ID="mcSliceTypes" runat="server" CommandText="spSelSLICETypeIDSLICEType"
                        PrimaryControl="false" FormName="SLICE Activity Link Maintenance" NewLinkCaption="SLICE Type"
                        RedirectProgramName="SLICEActivityMaster2" ShowExport="False" ShowAdd="False"
                        ShowDelete="False" ShowEdit="False" ShowExit="False" ShowRowCount="False" ShowView="False"
                        UseScrollingColor="false">
                        <GridColumns>
                            <CC1:MasterControlField DataField="SLICEType" HeaderText="SLICE Type" ShowReturns="False" />
                        </GridColumns>
                    </CC1:MasterControl>
                </td>
            </tr>
            <tr>
                <td>
                    <br />
                    <asp:Button ID="btnSliceTypes" runat="server" Visible="False" CssClass="Button_Variable"
                        Text="Edit SLICE Types" CausesValidation="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <br />
    <asp:Panel ID="pnlActivityLinks" runat="server" Visible="True">
        <table id="Table4" style="width: 761px" cellspacing="0" cellpadding="0">
            <tr>
                <td align="left">
                    <CC1:MasterControl ID="mcActivityLinks" runat="server" CommandText="spSelSLICEActivityLinkByLinkID"
                        PrimaryControl="false" FormName="SLICE Activity Link Maintenance" NewLinkCaption="SLICE Activity Link"
                        RedirectProgramName="SLICEActivityLinksMaster2" ShowExport="False" ShowAdd="False"
                        ShowDelete="False" ShowEdit="False" ShowExit="False" ShowRowCount="False" ShowView="False"
                        UseScrollingColor="false">
                        <GridColumns>
                            <CC1:MasterControlField DataField="SLICEActivityLinkType" HeaderText="SLICE Activity Link Type"
                                ShowReturns="False" />
                            <CC1:MasterControlField DataField="LinkDescription" HeaderText="Link Description"
                                ShowReturns="False" />
                            <CC1:MasterControlField DataField="LinkURL" HeaderText="LinkURL" ShowReturns="False" />
                        </GridColumns>
                    </CC1:MasterControl>
                </td>
            </tr>
            <tr>
                <td>
                    <br />
                    <asp:Button ID="btnSLICEActivityLinks" runat="server" Visible="False" CssClass="Button_Variable"
                        Text="Edit SLICE Activity Links" CausesValidation="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <br />
    <br />
    <asp:Panel ID="pnlActivityResults" runat="server" Visible="True">
        <table id="Table5" style="width: 761px" cellspacing="0" cellpadding="0">
            <tr>
                <td align="left">
                    <CC1:MasterControl ID="mcActivityResults" runat="server" PrimaryControl="false" CommandText="spSelSLICEResultsBySLICEActivityID"
                        FormName="SLICE Activity Result Maintenance" NewLinkCaption="SLICE Activity Result"
                        RedirectProgramName="SLICEActivityResults" ShowExport="False" ShowAdd="False"
                        ShowDelete="False" ShowEdit="False" ShowExit="False" ShowView="False" UseScrollingColor="false">
                        <GridColumns>
                            <CC1:MasterControlField DataField="SLICEResultText" HeaderText="SLICE Result Text"
                                ShowReturns="False" />
                            <CC1:MasterControlField DataField="Pass" HeaderText="Pass" ShowReturns="False" />
                        </GridColumns>
                    </CC1:MasterControl>
                </td>
            </tr>
            <tr>
                <td style="height: 31px">
                    <br />
                    <asp:Button ID="btnSLICEActivityResults" runat="server" CssClass="Button_Variable"
                        Visible="False" Text="Edit SLICE Activity Results" CausesValidation="False">
                    </asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <br />
    <br />
    <asp:Panel ID="pnlExit" runat="server" Visible="False">
        <table id="Table3" cellspacing="2" cellpadding="2" width="321" border="0" class="Table_Default">
            <tr>
                <td>
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                    </asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <uc2:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
