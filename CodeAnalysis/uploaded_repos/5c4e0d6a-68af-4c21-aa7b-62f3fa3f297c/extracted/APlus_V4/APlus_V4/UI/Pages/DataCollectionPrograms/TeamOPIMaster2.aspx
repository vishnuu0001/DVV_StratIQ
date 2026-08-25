<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TeamOPIMaster2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamOPIMaster2"
    Title="Team OPI Master" %>

<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="cc1" %>
<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/CalanderStyle.css" rel="stylesheet" />
</asp:Content>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <script type="text/javascript" language="javascript" src="../../../Scripts/jquery.functions.js"></script>
    <script type="text/javascript" language="javascript">
        $(document).ready(function () {
            $("textarea[name*='txtExpand']").TextAreaExpander();
        });
    </script>
    <asp:Panel ID="pnlOPIInformation" runat="server">
        <table id="Table2" class="Table_Default">
            <tr>
                <td style="width: 125px">
                    <asp:Label ID="lblRouteAbbrev" runat="server" CssClass="Label_Left_8PT" Text="Team:"></asp:Label>
                </td>
                <td>
                    <asp:DropDownList ID="ddlTeam" runat="server" CssClass="DropdownList_Entry" Width="358px">
                    </asp:DropDownList>
                    <asp:TextBox ID="txtTeam" runat="server" CssClass="Textbox_Display" MaxLength="15"
                        Visible="False" Width="350px" ReadOnly="True"></asp:TextBox>
                    <asp:RequiredFieldValidator ID="reqTeam" runat="server" ControlToValidate="ddlTeam"
                        CssClass="Label_Left_8PT" Display="None" ErrorMessage="Enter Team"></asp:RequiredFieldValidator>
                </td>
            </tr>
            <tr>
                <td style="width: 125px">
                    <asp:Label ID="Label1" runat="server" CssClass="Label_Left_8PT" Text="OPI:"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtOPI" runat="server" CssClass="Textbox_Entry" MaxLength="30" Width="325px"></asp:TextBox>
                    <asp:RequiredFieldValidator ID="reqOPI" runat="server" ControlToValidate="txtOPICategoryMaster"
                        CssClass="Label_Left_8PT" Display="None" ErrorMessage="Enter OPI"></asp:RequiredFieldValidator>
                </td>
            </tr>
            <tr>
                <td style="width: 125px">
                    <asp:Label ID="Label2" runat="server" Text="OPI Presentation Name:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtOPIShortName" CssClass="Textbox_Entry" Width="325px" MaxLength="50"
                        runat="server"></asp:TextBox><asp:RequiredFieldValidator ID="reqOPIShortName" runat="server"
                            ErrorMessage="Enter OPI Presentation Name" ControlToValidate="txtOPIShortName"
                            Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
                </td>
            </tr>
            <tr>
                <td style="width: 125px">
                    <asp:Label ID="Label3" runat="server" Text="OPI Description:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtExpandOPIDescription" runat="server" CssClass="Textbox_Entry"
                        Width="325px" MaxLength="250" TextMode="MultiLine" Rows="1" Height="28px"></asp:TextBox><asp:RequiredFieldValidator
                            ID="reqOPIDescription" runat="server" ErrorMessage="Enter OPI Description" ControlToValidate="txtExpandOPIDescription"
                            Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
                </td>
            </tr>
            <tr>
                <td style="width: 125px">
                    <asp:Label ID="Label4" runat="server" Text="Category:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:DropDownList ID="ddlOPICategoryMaster" runat="server" Width="300px" CssClass="DropdownList_Entry">
                    </asp:DropDownList>
                    <asp:TextBox ID="txtOPICategoryMaster" CssClass="Textbox_Display" Width="300px" MaxLength="15"
                        runat="server" Visible="False" ReadOnly="True"></asp:TextBox>
                    <asp:RequiredFieldValidator ID="reqOPICategory" runat="server" ErrorMessage="Enter OPI Category"
                        ControlToValidate="ddlOPICategoryMaster" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
                </td>
            </tr>
            <tr>
                <td style="width: 125px">
                    <asp:Label ID="Label13" runat="server" Text="UOM:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:DropDownList ID="ddlOPIUOMMaster" runat="server" Width="300px" CssClass="DropdownList_Entry">
                    </asp:DropDownList>
                    <asp:TextBox ID="txtOPIUOMMaster" CssClass="Textbox_Display" Width="300px" MaxLength="15"
                        runat="server" Visible="False" ReadOnly="True"></asp:TextBox><asp:RequiredFieldValidator
                            ID="reqOPIUOM" runat="server" ErrorMessage="Enter OPI UOM" ControlToValidate="ddlOPIUOMMaster"
                            Display="None"></asp:RequiredFieldValidator>
                </td>
            </tr>
            <tr>
                <td style="width: 125px">
                    <asp:Label ID="Label5" runat="server" Text="Time Entry Required:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:CheckBox ID="cbTimeEntryRequired" runat="server" CssClass="Checkbox_Default">
                    </asp:CheckBox>
                </td>
            </tr>
            <tr>
                <td style="width: 125px">
                    <asp:Label ID="Label6" runat="server" Text="OPI Value is Calculated:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:CheckBox ID="cbCalculateValue" runat="server" CssClass="Checkbox_Default"></asp:CheckBox>
                </td>
            </tr>
            <tr>
                <td style="width: 125px">
                    <asp:Label ID="Label7" runat="server" Text="OPI Value Formula:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtExpandOPIFormula" runat="server" CssClass="Textbox_Entry" Width="400px"
                        MaxLength="250" TextMode="MultiLine" Rows="1" Height="28px"></asp:TextBox>
                </td>
            </tr>
            <tr>
                <td style="width: 125px">
                    <asp:Label ID="Label8" runat="server" Text="Benefit Formula:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtExpandBenefitFormula" runat="server" CssClass="Textbox_Entry"
                        Width="400px" MaxLength="250" TextMode="MultiLine" Rows="1" Height="28px"></asp:TextBox>
                </td>
            </tr>
            <tr>
                <td style="width: 125px">
                    <asp:Label ID="Label9" runat="server" Text="Entry Type / Size:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:DropDownList ID="ddlEntryType" runat="server" Width="72px" CssClass="DropdownList_Entry">
                        <asp:ListItem Value="D">Decimal</asp:ListItem>
                        <asp:ListItem Value="N">Integer</asp:ListItem>
                    </asp:DropDownList>
                    <asp:TextBox ID="txtOPIEntryType" CssClass="Textbox_Display" Width="48px" MaxLength="1"
                        runat="server" Visible="False" ReadOnly="True"></asp:TextBox>&nbsp;
                    <asp:TextBox ID="txtOPISize" CssClass="Textbox_Entry" Width="25px" MaxLength="1"
                        runat="server" ToolTip="For integer types the size is the number is significant digits.  For decimal types the size is the number of digits after the decimal place."></asp:TextBox>
                    <asp:RequiredFieldValidator ID="reqOPISize" runat="server" ErrorMessage="Enter OPI Size"
                        ControlToValidate="txtOPISize" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator><asp:CheckBox
                            ID="cbNegativeEntryAllowed" runat="server" Text="Negative Entry Allowed" CssClass="Checkbox_Default">
                        </asp:CheckBox>
                </td>
            </tr>
            <tr>
                <td style="width: 125px">
                    <asp:Label ID="Label10" runat="server" Text="Summary Type:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtSummaryType" CssClass="Textbox_Entry_UpperCase" Width="25px"
                        MaxLength="1" runat="server"></asp:TextBox>
                    <asp:RequiredFieldValidator ID="reqSummaryType" runat="server" ErrorMessage="Enter Summary Type"
                        ControlToValidate="txtSummaryType" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator><asp:RegularExpressionValidator
                            ID="reqValidSummaryType" runat="server" ErrorMessage="Invalid Summary Type - Must equal A (Average), S (Sum) or L (Last)"
                            ControlToValidate="txtSummaryType" Display="None" ValidationExpression="[aAsSlL]"
                            CssClass="Label_Left_8PT"></asp:RegularExpressionValidator>
                </td>
            </tr>
            <tr>
                <td style="width: 125px">
                    <asp:Label ID="Label11" runat="server" Text="Collection Event:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtExpandCollectionEvent" CssClass="Textbox_Entry" Width="325px"
                        MaxLength="100" runat="server" TextMode="MultiLine" Rows="1" Height="28px"></asp:TextBox><asp:RequiredFieldValidator
                            ID="reqCollectionEvent" runat="server" ErrorMessage="Enter Collection Event"
                            ControlToValidate="txtExpandCollectionEvent" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
                </td>
            </tr>
            <tr>
                <td style="width: 125px">
                    <asp:Label ID="Label12" runat="server" Text="Collection Interval:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:DropDownList ID="ddlCollectionInterval" runat="server" Width="258px" CssClass="DropdownList_Entry">
                    </asp:DropDownList>
                    <asp:TextBox ID="txtCollectionInterval" CssClass="Textbox_Display" Width="258px"
                        MaxLength="15" runat="server" Visible="False" ReadOnly="True"></asp:TextBox><asp:RequiredFieldValidator
                            ID="reqCollectionInterval" runat="server" ErrorMessage="Enter Collection Interval"
                            ControlToValidate="ddlCollectionInterval" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
                </td>
            </tr>
        </table>
        <br />
        <asp:Panel ID="pnlAttributes" runat="server">
            <table id="AttributesHeader" class="Table_Default">
                <tr>
                    <td style="width: 184px;" align="left">
                        <asp:Label ID="Label14" runat="server" Text="Attribute Name" CssClass="Label_Left_8PT"></asp:Label>
                    </td>
                    <td style="width: 110px;" align="left">
                        <asp:Label ID="Label15" runat="server" Text="Entry Type" CssClass="Label_Left_8PT"></asp:Label>
                    </td>
                    <td style="width: 32px;" align="left">
                        <asp:Label ID="Label16" runat="server" Text="Size" CssClass="Label_Left_8PT"></asp:Label>
                    </td>
                    <td align="left">
                        <asp:Label ID="Label17" runat="server" Text="Default Last Entered Value" CssClass="Label_Left_8PT"></asp:Label>
                    </td>
                </tr>
            </table>
            <asp:Panel ID="pnlAttribute1" runat="server">
                <table id="Attribute1" class="Table_Default">
                    <tr>
                        <td style="width: 182px">
                            <asp:TextBox ID="txtAttribute1" runat="server" CssClass="Textbox_Entry" Width="176px"></asp:TextBox>
                        </td>
                        <td style="width: 110px">
                            <asp:DropDownList ID="ddlAttribute1EntryType" runat="server" CssClass="DropdownList_Entry"
                                Width="104px">
                                <asp:ListItem></asp:ListItem>
                                <asp:ListItem Value="D">Decimal</asp:ListItem>
                                <asp:ListItem Value="N">Integer</asp:ListItem>
                                <asp:ListItem Value="R">Required Text</asp:ListItem>
                                <asp:ListItem Value="C">Text</asp:ListItem>
                            </asp:DropDownList>
                            <asp:TextBox ID="txtAttribute1EntryType" runat="server" Width="96px" CssClass="Textbox_Display"
                                Visible="False" ReadOnly="True"></asp:TextBox>
                        </td>
                        <td style="width: 32px">
                            <asp:TextBox ID="txtAttribute1Size" runat="server" MaxLength="3" CssClass="Textbox_Entry"
                                Width="26px" ToolTip="For integer types the size is the number is significant digits. For decimal types the size is the number of digits after the decimal place. For Text the size is the number of optional characters. For Required Text the size is the number of Required characters."></asp:TextBox>
                        </td>
                        <td>
                            <asp:CheckBox ID="ckAttribute1Default" runat="server" />
                        </td>
                    </tr>
                </table>
            </asp:Panel>
            <asp:Panel ID="pnlAttribute2" runat="server">
                <table id="Attribute2" class="Table_Default">
                    <tr>
                        <td style="width: 182px">
                            <asp:TextBox ID="txtAttribute2" runat="server" CssClass="Textbox_Entry" Width="176px"></asp:TextBox>
                        </td>
                        <td style="width: 110px">
                            <asp:DropDownList ID="ddlAttribute2EntryType" runat="server" CssClass="DropdownList_Entry"
                                Width="104px">
                                <asp:ListItem></asp:ListItem>
                                <asp:ListItem Value="D">Decimal</asp:ListItem>
                                <asp:ListItem Value="N">Integer</asp:ListItem>
                                <asp:ListItem Value="R">Required Text</asp:ListItem>
                                <asp:ListItem Value="C">Text</asp:ListItem>
                            </asp:DropDownList>
                            <asp:TextBox ID="txtAttribute2EntryType" runat="server" Width="96px" CssClass="Textbox_Display"
                                Visible="False" ReadOnly="True"></asp:TextBox>
                        </td>
                        <td style="width: 32px">
                            <asp:TextBox ID="txtAttribute2Size" runat="server" MaxLength="3" CssClass="Textbox_Entry"
                                Width="26px" ToolTip="For integer types the size is the number is significant digits.  For decimal types the size is the number of digits after the decimal place. For Text the size is the number of optional characters.  For Required Text the size is the number of Required characters."></asp:TextBox>
                        </td>
                        <td>
                            <asp:CheckBox ID="ckAttribute2Default" runat="server" CssClass="Checkbox_Default" />
                        </td>
                    </tr>
                </table>
            </asp:Panel>
            <asp:Panel ID="pnlAttribute3" runat="server">
                <table id="Attribute3" class="Table_Default">
                    <tr>
                        <td style="width: 182px">
                            <asp:TextBox ID="txtAttribute3" runat="server" CssClass="Textbox_Entry" Width="176px"></asp:TextBox>
                        </td>
                        <td style="width: 110px">
                            <asp:DropDownList ID="ddlAttribute3EntryType" runat="server" CssClass="DropdownList_Entry"
                                Width="104px">
                                <asp:ListItem></asp:ListItem>
                                <asp:ListItem Value="D">Decimal</asp:ListItem>
                                <asp:ListItem Value="N">Integer</asp:ListItem>
                                <asp:ListItem Value="R">Required Text</asp:ListItem>
                                <asp:ListItem Value="C">Text</asp:ListItem>
                            </asp:DropDownList>
                            <asp:TextBox ID="txtAttribute3EntryType" runat="server" Width="96px" CssClass="Textbox_Display"
                                Visible="False" ReadOnly="True"></asp:TextBox>
                        </td>
                        <td style="width: 32px">
                            <asp:TextBox ID="txtAttribute3Size" runat="server" MaxLength="3" CssClass="Textbox_Entry"
                                Width="26px" ToolTip="For integer types the size is the number is significant digits. For decimal types the size is the number of digits after the decimal place. For Text the size is the number of optional characters. For Required Text the size is the number of Required characters."></asp:TextBox>
                        </td>
                        <td>
                            <asp:CheckBox ID="ckAttribute3Default" runat="server" CssClass="Checkbox_Default" />
                        </td>
                    </tr>
                </table>
            </asp:Panel>
            <asp:Panel ID="pnlAttribute4" runat="server">
                <table id="Attribute4" class="Table_Default">
                    <tr>
                        <td style="width: 182px">
                            <asp:TextBox ID="txtAttribute4" runat="server" CssClass="Textbox_Entry" Width="176px"></asp:TextBox>
                        </td>
                        <td style="width: 110px">
                            <asp:DropDownList ID="ddlAttribute4EntryType" runat="server" CssClass="DropdownList_Entry"
                                Width="104px">
                                <asp:ListItem></asp:ListItem>
                                <asp:ListItem Value="D">Decimal</asp:ListItem>
                                <asp:ListItem Value="N">Integer</asp:ListItem>
                                <asp:ListItem Value="R">Required Text</asp:ListItem>
                                <asp:ListItem Value="C">Text</asp:ListItem>
                            </asp:DropDownList>
                            <asp:TextBox ID="txtAttribute4EntryType" runat="server" Width="96px" CssClass="Textbox_Display"
                                Visible="False" ReadOnly="True"></asp:TextBox>
                        </td>
                        <td style="width: 32px">
                            <asp:TextBox ID="txtAttribute4Size" runat="server" MaxLength="3" CssClass="Textbox_Entry"
                                Width="26px" ToolTip="For integer types the size is the number is significant digits. For decimal types the size is the number of digits after the decimal place. For Text the size is the number of optional characters. For Required Text the size is the number of Required characters."></asp:TextBox>
                        </td>
                        <td>
                            <asp:CheckBox ID="ckAttribute4Default" runat="server" CssClass="Checkbox_Default" />
                        </td>
                    </tr>
                </table>
            </asp:Panel>
            <asp:Panel ID="pnlAttribute5" runat="server">
                <table id="Attribute5" class="Table_Default">
                    <tr>
                        <td style="width: 182px">
                            <asp:TextBox ID="txtAttribute5" runat="server" CssClass="Textbox_Entry" Width="176px"></asp:TextBox>
                        </td>
                        <td style="width: 110px">
                            <asp:DropDownList ID="ddlAttribute5EntryType" runat="server" CssClass="DropdownList_Entry"
                                Width="104px">
                                <asp:ListItem></asp:ListItem>
                                <asp:ListItem Value="D">Decimal</asp:ListItem>
                                <asp:ListItem Value="N">Integer</asp:ListItem>
                                <asp:ListItem Value="R">Required Text</asp:ListItem>
                                <asp:ListItem Value="C">Text</asp:ListItem>
                            </asp:DropDownList>
                            <asp:TextBox ID="txtAttribute5EntryType" runat="server" Width="96px" CssClass="Textbox_Display"
                                Visible="False" ReadOnly="True"></asp:TextBox>
                        </td>
                        <td style="width: 32px">
                            <asp:TextBox ID="txtAttribute5Size" runat="server" MaxLength="3" CssClass="Textbox_Entry"
                                Width="26px" ToolTip="For integer types the size is the number is significant digits. For decimal types the size is the number of digits after the decimal place. For Text the size is the number of optional characters. For Required Text the size is the number of Required characters."></asp:TextBox>
                        </td>
                        <td>
                            <asp:CheckBox ID="ckAttribute5Default" runat="server" CssClass="Checkbox_Default" />
                        </td>
                    </tr>
                </table>
            </asp:Panel>
            <asp:Panel ID="pnlAttribute6" runat="server">
                <table id="Attribute6" class="Table_Default">
                    <tr>
                        <td style="width: 182px">
                            <asp:TextBox ID="txtAttribute6" runat="server" CssClass="Textbox_Entry" Width="176px"></asp:TextBox>
                        </td>
                        <td style="width: 110px">
                            <asp:DropDownList ID="ddlAttribute6EntryType" runat="server" CssClass="DropdownList_Entry"
                                Width="104px">
                                <asp:ListItem></asp:ListItem>
                                <asp:ListItem Value="D">Decimal</asp:ListItem>
                                <asp:ListItem Value="N">Integer</asp:ListItem>
                                <asp:ListItem Value="R">Required Text</asp:ListItem>
                                <asp:ListItem Value="C">Text</asp:ListItem>
                            </asp:DropDownList>
                            <asp:TextBox ID="txtAttribute6EntryType" runat="server" Width="96px" CssClass="Textbox_Display"
                                Visible="False" ReadOnly="True"></asp:TextBox>
                        </td>
                        <td style="width: 32px">
                            <asp:TextBox ID="txtAttribute6Size" runat="server" MaxLength="3" CssClass="Textbox_Entry"
                                Width="26px" ToolTip="For integer types the size is the number is significant digits. For decimal types the size is the number of digits after the decimal place. For Text the size is the number of optional characters. For Required Text the size is the number of Required characters."></asp:TextBox>
                        </td>
                        <td>
                            <asp:CheckBox ID="ckAttribute6Default" runat="server" CssClass="Checkbox_Default" />
                        </td>
                    </tr>
                </table>
            </asp:Panel>
        </asp:Panel>
    </asp:Panel>
    <table id="Table5" class="Table_Default">
        <tr>
            <td style="width: 175px">
                <asp:Label ID="lblRouteDefinition" runat="server" Text="Primary OPI:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="cbPrimaryOPI" runat="server"></asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td style="width: 175px">
                <asp:Label ID="lblDataCollectionOnline" runat="server" Text="Data Collection Online:"
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="cbDataCollectionOnline" runat="server"></asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td style="width: 175px">
                <asp:Label ID="lblResponsiblePerson" runat="server" Text="Responsible Person" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlResponsiblePerson" runat="server" Width="258px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtResponsiblePerson" runat="server" Width="258px" MaxLength="15"
                    CssClass="Textbox_Display" Visible="False" ReadOnly="True"></asp:TextBox>
                &nbsp;<asp:DropDownList ID="ddlSite" runat="server" CssClass="DropdownList_Entry"
                    Width="194px" AutoPostBack="True">
                </asp:DropDownList>
            </td>
        </tr>
        <tr>
            <td style="width: 175px">
                <asp:Label ID="lblHistoricValue" runat="server" Text="Historic Value:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtHistoric" runat="server" Width="97" MaxLength="15" CssClass="Textbox_Entry"></asp:TextBox><asp:RequiredFieldValidator
                    ID="reqHistoric" runat="server" Display="None" ControlToValidate="txtHistoric"
                    ErrorMessage="Enter Historic"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 175px">
                <asp:Label ID="lblTargetValue" runat="server" Text="Target Value:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtTarget" runat="server" Width="97px" MaxLength="15" CssClass="Textbox_Entry"></asp:TextBox><asp:RequiredFieldValidator
                    ID="reqTarget" runat="server" Display="None" ControlToValidate="txtTarget" ErrorMessage="Enter Target"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 175px;">
                <asp:Label ID="lblHistoricStartDate" runat="server" Text="Historic Start Date:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtStartDate" runat="server" Width="81" CssClass="Textbox_Entry"></asp:TextBox>
                <cc1:CalendarExtender ID="txtStartDate_CalendarExtender" runat="server" PopupButtonID="imgStartDate"
                    TargetControlID="txtStartDate" CssClass="APlus_Calendar">
                </cc1:CalendarExtender>
                <asp:ImageButton ID="imgStartDate" runat="server" ImageUrl="~/Images/date-time_select.gif"
                    ToolTip="Click to Select Date..." CausesValidation="False" />
                <asp:RequiredFieldValidator ID="reqStartDate" runat="server" Display="None" ControlToValidate="txtStartDate"
                    ErrorMessage="Enter Start Date"></asp:RequiredFieldValidator><asp:CompareValidator
                        ID="cmpStartDate" runat="server" Display="None" ControlToValidate="txtStartDate"
                        ErrorMessage="Invalid Start Date" Type="Date" Operator="DataTypeCheck"></asp:CompareValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 175px;">
                <asp:Label ID="lblHistoricEndDate" runat="server" Text="Historic End Date:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtEndDate" runat="server" Width="81" CssClass="Textbox_Entry"></asp:TextBox>
                <cc1:CalendarExtender ID="txtEndDate_CalendarExtender" runat="server" PopupButtonID="imgEndDate"
                    TargetControlID="txtEndDate" CssClass="APlus_Calendar">
                </cc1:CalendarExtender>
                <asp:ImageButton ID="imgEndDate" runat="server" ImageUrl="~/Images/date-time_select.gif"
                    ToolTip="Click to Select Date..." CausesValidation="False" />
                <asp:RequiredFieldValidator ID="reqEndDate" runat="server" Display="None" ControlToValidate="txtEndDate"
                    ErrorMessage="Enter End Date"></asp:RequiredFieldValidator><asp:CompareValidator
                        ID="cmpEndDate" runat="server" Display="None" ControlToValidate="txtEndDate"
                        ErrorMessage="Invalid End Date" Type="Date" Operator="DataTypeCheck"></asp:CompareValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 175px;">
                <asp:Label ID="lblProjectedBenefit" runat="server" Text="Projected Benefit:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtProjectedBenefit" runat="server" Width="80px" CssClass="Textbox_Entry"
                    MaxLength="15"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 175px">
                <asp:Label ID="lblExpectedBenefit" runat="server" Text="Expected Benefit (Per OPI UOM):"
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpectedBenefit" runat="server" Width="80px" MaxLength="10" CssClass="Textbox_Entry"></asp:TextBox><asp:RequiredFieldValidator
                    ID="reqExpectedBenefit" runat="server" Display="None" ControlToValidate="txtExpectedBenefit"
                    ErrorMessage="Enter Extected Benefit"></asp:RequiredFieldValidator>&nbsp;
            </td>
        </tr>
        <tr>
            <td style="width: 175px">
                <asp:Label ID="lblExpectedBenefitUOM" runat="server" Text="Expected Benefit UOM:"
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtUOM" runat="server" Width="100px" CssClass="Textbox_Entry" MaxLength="15"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqUOM" runat="server" ErrorMessage="Enter Expected Benefit UOM"
                    ControlToValidate="txtUOM" Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
    </table>
    <table id="Table4" class="Table_Default">
        <tr>
            <td style="width: 175px">
                <asp:Label ID="lblStartingPeriod" runat="server" Text="Starting Period:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="width: 146px">
                <asp:TextBox ID="txtReportStart" runat="server" CssClass="Textbox_Entry" Width="81px"></asp:TextBox>
                <cc1:CalendarExtender ID="txtReportStart_CalendarExtender" runat="server" PopupButtonID="imgReportStart"
                    TargetControlID="txtReportStart" CssClass="APlus_Calendar">
                </cc1:CalendarExtender>
                <asp:ImageButton ID="imgReportStart" runat="server" ImageUrl="~/Images/date-time_select.gif"
                    ToolTip="Click to Select Date..." CausesValidation="False" />
                <asp:CompareValidator ID="compReportStartDate" runat="server" ErrorMessage="Invalid Report Start Date"
                    ControlToValidate="txtReportStart" Display="None" Operator="DataTypeCheck" Type="Date"></asp:CompareValidator>
                <asp:CompareValidator ID="ValidReportStartDate" runat="server" ErrorMessage="Report Start Period cannot be greater than the Report Ending Period"
                    ControlToValidate="txtReportStart" Display="None" Operator="LessThanEqual" Type="Date"
                    ControlToCompare="txtReportEnd"></asp:CompareValidator>
            </td>
            <td valign="middle" align="center" style="width: 46px">
                <asp:Label ID="lblOR" runat="server" Text="OR" CssClass="Label_Left_8PT"></asp:Label><br />
            </td>
            <td align="left" style="width: 95px">
                <asp:Label ID="lblReportingPeriods" runat="server" Text="Reporting Periods:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtReportingPeriods" runat="server" Width="50px" CssClass="Textbox_Entry"
                    MaxLength="2"></asp:TextBox><asp:RangeValidator ID="validReportingPeriods" runat="server"
                        Display="None" ControlToValidate="txtReportingPeriods" ErrorMessage="Invalid Reporting Period - Must be between 1 and 100"
                        Type="Integer" MinimumValue="1" MaximumValue="99"></asp:RangeValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 175px">
                <asp:Label ID="lblEndingPeriod" runat="server" Text="Ending Period:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="width: 146px">
                <asp:TextBox ID="txtReportEnd" runat="server" Width="81px" CssClass="Textbox_Entry"></asp:TextBox>
                <cc1:CalendarExtender ID="txtReportEnd_CalendarExtender" runat="server" PopupButtonID="imgReportEnd"
                    TargetControlID="txtReportEnd" CssClass="APlus_Calendar">
                </cc1:CalendarExtender>
                <asp:ImageButton ID="imgReportEnd" runat="server" ImageUrl="~/Images/date-time_select.gif"
                    ToolTip="Click to Select Date..." CausesValidation="False" />
                <asp:CompareValidator ID="compReportEndDate" runat="server" Display="None" ControlToValidate="txtReportEnd"
                    ErrorMessage="Invalid Reprot End Date" Type="Date" Operator="DataTypeCheck"></asp:CompareValidator>
            </td>
            <td style="width: 46px">
            </td>
            <td align="left" style="width: 95px">
            </td>
            <td>
            </td>
        </tr>
        <tr>
            <td style="width: 175px">
                <asp:Label ID="lblReportingInterval" runat="server" Text="Reporting Interval:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td colspan="4">
                <asp:DropDownList ID="ddlReportingInterval" runat="server" CssClass="DropdownList_Entry"
                    Width="136px">
                </asp:DropDownList>
                <asp:TextBox ID="txtReportingInterval" runat="server" Width="136px" Visible="False"
                    CssClass="Textbox_Display" MaxLength="15" ReadOnly="True"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqReportingInterval" runat="server" ErrorMessage="Enter Reporting Interval"
                    ControlToValidate="ddlReportingInterval" Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 175px">
            </td>
            <td colspan="4">
            </td>
        </tr>
        <tr>
            <td style="width: 175px">
            </td>
            <td colspan="4">
                <asp:CheckBox ID="chkCustomYValues" runat="server" Text="Use Custom Chart Y Axis Values">
                </asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td style="width: 175px">
                <asp:Label ID="lblChartYMin" runat="server" Text="Chart Y Min:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td colspan="4">
                <asp:TextBox ID="txtChartYMin" runat="server" Width="100px" CssClass="Textbox_Entry"
                    MaxLength="10"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 175px">
                <asp:Label ID="lblChartYMax" runat="server" Text="Chart Y Max:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td colspan="4">
                <asp:TextBox ID="txtChartYMax" runat="server" Width="100px" CssClass="Textbox_Entry"
                    MaxLength="10"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 175px">
                <asp:Label ID="lblChartYLines" runat="server" Text="Chart Y Lines:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td colspan="4">
                <asp:TextBox ID="txtChartYLines" runat="server" Width="100px" CssClass="Textbox_Entry"
                    MaxLength="2"></asp:TextBox>
                <asp:RangeValidator ID="Rangevalidator1" runat="server" ErrorMessage="Invalid Number of Chart Y Lines (1-10)"
                    ControlToValidate="txtChartYLines" Display="None" Type="Integer" MaximumValue="10"
                    MinimumValue="1"></asp:RangeValidator>
            </td>
        </tr>
    </table>
    <asp:Panel ID="pnlOKCancel" runat="server">
        <br />
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK" EnableViewState="False">
                    </asp:Button>
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
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False"
        Translate="true" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
