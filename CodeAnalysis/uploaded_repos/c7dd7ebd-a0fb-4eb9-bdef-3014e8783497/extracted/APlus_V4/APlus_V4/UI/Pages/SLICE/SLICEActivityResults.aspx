<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="SLICEActivityResults.aspx.vb" Inherits="WebApp.APlus.UI.SLICE.SLICEActivityResults"
    Title="SLICE Activity Results" EnableTheming="true" StylesheetTheme="APlus_Default" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<%@ Register Src="../../UserControls/WorkcenterSubHeader.ascx" TagName="WorkcenterSubHeader"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <script type="text/javascript" language="javascript" src="../../../Scripts/jquery.functions.js"></script>
    <script type="text/javascript" language="javascript">
        $(document).ready(function () {
            $("textarea[name*='txtExpand']").TextAreaExpander();
        });
    </script>
    <p>
        <uc1:WorkcenterSubHeader ID="WorkcenterSubHeader1" runat="server"></uc1:WorkcenterSubHeader>
    </p>
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 150px">
                <asp:Label ID="lblSLICEActivityID" runat="server" CssClass="Label_Left_8PT" Text="SLICE Activity ID:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSLICEActivityID" Width="48px" CssClass="Textbox_Display" runat="server"
                    ReadOnly="True" MaxLength="10"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 150px; height: 2px">
                <asp:Label ID="lblSLICEActivityGroup" runat="server" CssClass="Label_Left_8PT" Text="SLICE Activity Group:"></asp:Label>
            </td>
            <td style="height: 2px">
                <asp:DropDownList ID="ddlSLICEActivityGroup" runat="server" Width="232px" CssClass="DropdownList_Entry"
                    Visible="False">
                </asp:DropDownList>
                <asp:TextBox ID="txtSLICEActivityGroup" Width="256px" CssClass="Textbox_Display"
                    runat="server" ReadOnly="True" MaxLength="50"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 150px; height: 28px">
                <asp:Label ID="lblEntity" runat="server" CssClass="Label_Left_8PT" Text="Entity:"> </asp:Label>
            </td>
            <td style="height: 28px">
                <asp:DropDownList ID="ddlEntity" runat="server" Width="232px" CssClass="DropdownList_Entry"
                    Visible="False">
                </asp:DropDownList>
                <asp:TextBox ID="txtEntity" Width="256px" CssClass="Textbox_Display" runat="server"
                    ReadOnly="True" MaxLength="50"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 150px; height: 16px">
                <asp:Label ID="lblPosition" runat="server" CssClass="Label_Left_8PT" Text="Position:"></asp:Label>
            </td>
            <td style="height: 16px">
                <asp:DropDownList ID="ddlPosition" runat="server" Width="232px" CssClass="DropdownList_Entry"
                    Visible="False">
                </asp:DropDownList>
                <asp:TextBox ID="txtPosition" Width="256px" CssClass="Textbox_Display" runat="server"
                    ReadOnly="True" MaxLength="50"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 150px; height: 20px">
                <asp:Label ID="lblSLICEType" runat="server" CssClass="Label_Left_8PT" Text="SLICE Type:"></asp:Label>
            </td>
            <td style="height: 20px">
                <asp:DropDownList ID="ddlSLICEType" runat="server" Width="232px" CssClass="DropdownList_Entry"
                    Visible="False">
                </asp:DropDownList>
                <asp:TextBox ID="txtSLICEType" Width="256px" CssClass="Textbox_Display" runat="server"
                    ReadOnly="True" MaxLength="50"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 150px">
                <asp:Label ID="lblPresentationSequence" runat="server" CssClass="Label_Left_8PT"
                    Text="Presentation Sequence:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtPresentationSequence" runat="server" Width="40px" CssClass="Textbox_Entry"
                    MaxLength="4"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 150px; height: 24px">
                <asp:Label ID="lblSLICEFrequency" runat="server" CssClass="Label_Left_8PT" Text="SLICE Frequency:"></asp:Label>
            </td>
            <td style="height: 24px">
                <asp:DropDownList ID="ddlSLICEFrequency" runat="server" Width="232px" CssClass="DropdownList_Entry"
                    Visible="False">
                </asp:DropDownList>
                <asp:TextBox ID="txtSLICEFrequency" Width="232px" CssClass="Textbox_Display" runat="server"
                    ReadOnly="True" MaxLength="50"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 150px" valign="top">
                <asp:Label ID="lblMeasurement" runat="server" CssClass="Label_Left_8PT" Text="Measurement:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandMeasurement" runat="server" Width="408px" CssClass="Textbox_Entry"
                    Height="32px" MaxLength="50" TextMode="MultiLine"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 150px; height: 37px" valign="top">
                <asp:Label ID="lblDesiredCondition" runat="server" CssClass="Label_Left_8PT" Text="Desired Condition:"></asp:Label>
            </td>
            <td style="height: 37px">
                <asp:TextBox ID="txtExpandDesiredCondition" runat="server" Width="408px" CssClass="Textbox_Entry"
                    Height="32px" MaxLength="50" TextMode="MultiLine"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 150px; height: 23px">
                <asp:Label ID="lblTargetTime" runat="server" CssClass="Label_Left_8PT" Text="Target Time:"></asp:Label>
            </td>
            <td style="height: 23px">
                <asp:TextBox ID="txtTargetTime" Width="64px" CssClass="Textbox_Entry" runat="server"
                    MaxLength="50" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 150px">
                <asp:Label ID="lblLastcompleted" runat="server" CssClass="Label_Left_8PT" Text="Last Completed Date:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtLastCompleted" Width="216px" CssClass="Textbox_Display" runat="server"
                    ReadOnly="True" MaxLength="50"></asp:TextBox>
            </td>
        </tr>
    </table>
    <br />
    <br />
    <table id="TblResultsGrid" style="width: 761px" cellspacing="0" cellpadding="0">
        <tr>
            <td align="left">
                <asp:GridView ID="grdResultsGrid" runat="server" SkinID="GridView" AutoGenerateColumns="False"
                    Width="488px">
                    <Columns>
                        <asp:TemplateField HeaderText="SLICE Result Text">
                            <ItemTemplate>
                                <asp:CheckBox ID="chkSLICEResultText" runat="server" Text='<%# Bind("SLICEResultText") %>' />
                            </ItemTemplate>
                        </asp:TemplateField>
                        <asp:BoundField DataField="Pass" HeaderText="Pass">
                            <HeaderStyle Wrap="False" />
                            <ItemStyle Wrap="False" />
                        </asp:BoundField>
                    </Columns>
                </asp:GridView>
            </td>
        </tr>
    </table>
    <br />
    <br />
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" EnableViewState="False"
                        Text="OK"></asp:Button>
                </td>
                <td>
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                        CausesValidation="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlExit" runat="server" Visible="False">
        <table id="Table3" class="Table_Default">
            <tr>
                <td>
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                    </asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
</asp:Content>
