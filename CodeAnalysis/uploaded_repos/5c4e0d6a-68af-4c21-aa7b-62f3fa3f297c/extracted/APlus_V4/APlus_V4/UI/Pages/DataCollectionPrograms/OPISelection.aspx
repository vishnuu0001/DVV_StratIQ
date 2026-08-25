<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="OPISelection.aspx.vb" Inherits="WebApp.APlus.UI.Pages.OPISelection"
    Title="OPI Selection" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">

    <script type="text/javascript" language="javascript">
		function CheckOPI(objControl)
		{
			if(objControl.value=='')
			{
			var msg =	"\n You have selected a blank OPI.  \n" +
						"\n\n" +
						"You will be re-directed to the last Menu.\n" +
						"\n\n";
			return confirm(msg);
			}
		}	
    </script>

    <table id="Table1" cellspacing="2" cellpadding="2" border="0">
        <tr>
            <td style="width: 92px">
                <asp:Label ID="lblOPI" runat="server" Text="OPI:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlOPI" runat="server" Width="582px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
            </td>
        </tr>
    </table>
    <table id="Table2" class="Table_Default">
        <tr>
            <td style="width: 110px">
                <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK" CausesValidation="False">
                </asp:Button>
            </td>
            <td>
                <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel">
                </asp:Button>
            </td>
        </tr>
    </table>
</asp:Content>
