/**
 * This is the AppConstant.java
 * <B>Creation Date: </B> Apr 23, 2019<BR>
 * <BR>
 * @author TechM
 * @version 1.0 <BR>
 * <BR>
 * <B>Patterns Used: </B> <BR>
 * <BR>
 * Copyright 2002 by Mazda North America Operations, Inc., 7755 Irvine
 * Center Drive Irvine, CA 92623, U.S.A. All rights reserved. <BR>
 * <BR>
 * This software is the confidential and proprietary information of
 * Mazda North America Operations Inc. ("Confidential Information").
 * You shall not disclose such Confidential Information and shall use
 * it only is accordance with the terms of the license agreement you
 * entered into with Mazda North American Operations.
 **/
package com.mazdausa.corporate.vehicles.distribution.application.constants;


/**
 * @author TechM
 *
 */
public class AppConstant {
	public static final String FLEET_PROPERTY_SCHEMA="VDS_INQUIRY";
	public static final String ACCESSIBLE_SCREEN = "AccessibleScreen";
	public static final String SUCCESS = "success";
	public static final String ERROR = "error";
	public static final String STATUS_TEXT = "carrier.setup.status.text";
	public static final String STATUS_VALUE = "carrier.setup.status.value";
	public static final String TYPE_TEXT = "carrier.setup.type.text";
	public static final String TYPE_VALUE = "carrier.setup.type.value";
	public static final String CURRENCY_TEXT = "carrier.setup.currency.text";
	
	public static final String DETAILED_TYPE_TEXT = "carrier.setup.detailedtype.text";
	public static final String DETAILED_TYPE_VALUE = "carrier.setup.detailedtype.value";
	
	public static final String DETAILED_CURRENCY_TEXT = "carrier.setup.detailedcurrency.text";
	public static final String DETAILED_CURRENCY_VALUE = "carrier.setup.detailedcurrency.value";
	public static final String LTS_USER_PRIVILEGE="UserPrivilege";
	
	public static final String CURRENCY_VALUE = "carrier.setup.currency.value";
	public static final String TRANSPORTATION_SETUP_PROPERTIES = "ICLService";
	public static final String ACTION_CD_D ="D";
	public static final String ACTION_CD_SEARCH ="S";
	public static final String ACTION_CD_I ="I";
	public static final String ACTION_CD_A ="A";
	public static final String CARR_CD="CARR_CD";
	public static final String CARR_NM="CARR_NM";
	public static final String STR1_AD="STR1_AD";
	public static final String STR2_AD="STR2_AD";
	public static final String STR3_AD="STR3_AD";
	public static final String CITY_NM="CITY_NM";
	public static final String ST_CD="ST_CD";
	public static final String ZIP_CD="ZIP_CD";
	public static final String CARR_TYPE_DESC="CARR_TYPE_DESC";
	public static final String PYMT_TYPE_DESC="PYMT_TYPE_DESC";
	public static final String STATUS_DESC="STATUS_DESC";
	public static final String CURRENCY_CD="CURRENCY_CD";
	public static final String _BLANK=" ";
	public static final String EMPTY = "";
	public static final String ACTION_CD_C ="C";
	private AppConstant() {
		super();
	}
	public static final String FORM_districtCode="districtCode";
		
		public static final String ACTIONCODE_SEARCH = "SEARCH";
		public static final String ACTIONCODE_UPDATE = "UPDATE";
		public static final String ACTIONCODE_ADD = "ADD";
		public static final String ACTIONCODE_DELETE = "DELETE";
		public static final String ACTIONCODE_RESET = "RESET";
		public static final String ACTIONCODE_COUNTRYSEARCH = "SELECTCOUNTRY";
		public static final String ACTIONCODE_GENERATEEXCEL = "EXCEL_DOWNLOAD";
		public static final String ACTIONCODE_MAILING_COUNTRYSEARCH = "SELECTMAILINGCOUNTRY";
		public static final String ACTIONCODE_SHIPPING_COUNTRYSEARCH = "SELECTSHIPPINGCOUNTRY";
		
		public static final String SP_ACTIONCODE_VIEW_SEARCH = "I";
		public static final String SP_ACTIONCODE_SEARCH = "S";
		public static final String SP_ACTIONCODE_ADD = "A";
		public static final String SP_ACTIONCODE_DELETE = "R";
		public static final String SP_ACTIONCODE_UPDATE = "U";
		public static final String DB_DSTRCT_CD="DSTRCT_CD";
		
		public static final String DB_EMAIL_ID="EMAIL_ID";
		public static final String DB_CELL_NO1="CELL_NO1";
		public static final String DB_CELL_NO2="CELL_NO2";
		public static final String DB_CELL_NO3="CELL_NO3";
		
		
		public static final String FORM_ATTRIBUTE_LOCATION_NAME="locationName";
		public static final String FORM_ATTRIBUTE_LOCATION_CODE="locationCode";
		public static final String FORM_ATTRIBUTE_LOCATION_COUNTRY="input_country";
		public static final String FORM_ATTRIBUTE_LOCATION_REGION="input_region";
		public static final String FORM_ATTRIBUTE_LOCATION_STATE="input_State";
		public static final String FORM_ATTRIBUTE_LOCATION_ZIPCD="location_zipCode";
		public static final String FORM_ATTRIBUTE_LOCATION_CITY="input_City";
		public static final String FORM_ATTRIBUTE_LOCATION_STATUS="input_statusCode";
		public static final String FORM_ATTRIBUTE_LOCATION_TYPE="input_Type";
		public static final String ACTIONCODE_SAVE = "SAVE";
		public static final String FORM_ATTRIBUTE_LOCATION_MAILING_COUNTRY="mailingCountry1";
		public static final String FORM_ATTRIBUTE_SHIPPING_MAILING_COUNTRY="mailingCountry2";

		public static final String FORM_ATTRIBUTE_LOCATION_SETUP_NAME="locationsetupName";
		public static final String FORM_ATTRIBUTE_LOCATION_SETUP_FIRSTNAME="locationsetupfirstName";
		public static final String FORM_ATTRIBUTE_LOCATION_SETUP_CODE="locationsetupCode";
		public static final String FORM_ATTRIBUTE_LOCATION_SETUP_LASTNAME="locationsetuplastName";
		public static final String FORM_ATTRIBUTE_LOCATION_STATUS_CODE="input_locationsetup_Statuscode";
		public static final String FORM_ATTRIBUTE_LOCATION_SETUP_TITLE="locationsetupTitle";
		public static final String FORM_ATTRIBUTE_LOCATION_SETUP_EMAIL="locationsetupEmail";
		public static final String FORM_ATTRIBUTE_LOCATION_SETUP_PHONE1="locationsetupPhone1";
		public static final String FORM_ATTRIBUTE_LOCATION_SETUP_PHONE2="locationsetupPhone2";
		public static final String FORM_ATTRIBUTE_LOCATION_SETUP_PHONE3="locationsetupPhone3";
		public static final String FORM_ATTRIBUTE_LOCATION_SETUP_PHONE4="locationsetupPhone4";
		public static final String FORM_ATTRIBUTE_LOCATION_SETUP_TYPE1="input_locationsetup_Type1";
		public static final String FORM_ATTRIBUTE_LOCATION_SETUP_FAX1="locationsetupfaxAreaCode1";
		public static final String FORM_ATTRIBUTE_LOCATION_SETUP_FAX2="locationsetupfaxAreaCode2";
		public static final String FORM_ATTRIBUTE_LOCATION_SETUP_FAX3="locationsetupfaxAreaCode3";
		public static final String FORM_ATTRIBUTE_LOCATION_SETUP_TYPE2="input_locationsetup_Type2";
		public static final String FORM_ATTRIBUTE_LOCATION_SETUP_CELL1="locationsetupcellAreaCode1";
		public static final String FORM_ATTRIBUTE_LOCATION_SETUP_CELL2="locationsetupcellAreaCode2";
		public static final String FORM_ATTRIBUTE_LOCATION_SETUP_CELL3="locationsetupcellAreaCode3"; 
		public static final String FORM_ATTRIBUTE_LOCATION_SETUP_TYPE3="input_locationsetup_Type3";
		public static final String FORM_ATTRIBUTE_LOCATION_SETUP_REGION="input_locationsetupRegion";
		public static final String FORM_ATTRIBUTE_LOCATION_SETUP_MAILINGSTREET="mailingStreet";
		public static final String FORM_ATTRIBUTE_LOCATION_SETUP_MAILINGSTREET1="mailingStreet1";
		public static final String FORM_ATTRIBUTE_LOCATION_SETUP_MAILINGSTREET2="mailingStreet2";
		public static final String FORM_ATTRIBUTE_LOCATION_SETUP_MAILINGSTREET3="mailingStreet3";
		public static final String FORM_ATTRIBUTE_LOCATION_SETUP_MAILINGSTREET4="mailingStreet4";
		public static final String FORM_ATTRIBUTE_LOCATION_SETUP_MAILINGSTREET5="mailingStreet5";
		public static final String FORM_ATTRIBUTE_LOCATION_SETUP_MAILING_CITY1="mailingCity1";
		public static final String FORM_ATTRIBUTE_LOCATION_MAILING_CITY2="mailingCity2";
		public static final String FORM_ATTRIBUTE_LOCATION_MAILING_STATE1="mailing_State1";
		public static final String FORM_ATTRIBUTE_LOCATION_MAILING_STATE2="mailing_State2";
		public static final String FORM_ATTRIBUTE_LOCATION_MAILING_ZIPCD1="mailingZipCd1";
		public static final String FORM_ATTRIBUTE_LOCATION_MAILING_ZIPCD2="mailingZipCd2";
		public static final String FORM_ATTRIBUTE_LOCATION_MAILING_COUNTRY1="mailingCountry1";
		public static final String FORM_ATTRIBUTE_LOCATION_MAILING_COUNTRY2="mailingCountry2";
		
		public static final String FORM_ATTRIBUTE_LOCATION_SETUP_MAIL="locationsetupEmail";
		public static final String FORM_ATTRIBUTE_LOCATION_CELL_AREA_CODE1="locationsetupcellAreaCode1";
		public static final String FORM_ATTRIBUTE_LOCATION_CELL_AREA_CODE2="locationsetupcellAreaCode2";
		public static final String FORM_ATTRIBUTE_LOCATION_CELL_AREA_CODE3="locationsetupcellAreaCode3";
		
		public static final String FORM_ATTRIBUTE_LOCATION_LOCATION_STATUS_DATE="locStatusDate";
		public static final String FORM_ATTRIBUTE_LOCATION_LOCATION_CURRENT_DATE="currentDate";
		public static final String vds_location_index_view_loading="SV77952"; 
		public static final String BLANK=" ";
		public static final String LOCATION_INDEX_SPAGE="locationindx";
		public static final String CONTENT_DISPOSITION="content-disposition";
		public static final String ATTACHMENT = "attachment";
			public static final String SEMI_COLON = ";";
				public static final String FILENAME = "filename";
					public static final String EQUAL = "=";
						public static final String DOWNLOAD_LOCATION_EXCEL_FILENAME="locationIndexExcel.xls";
							public static final String EXCEL_FILEFORMAT = ".xls";

		public static final String LOCATION_PROPERTY_FILE = "com.mazdausa.corporate.vehicles.distribution.persistence.properties.location";
		public static final String FILE_LOCATION_PATH = "FILE_LOCATION_PATH";
		public static final String LOCATION_INDEX = "LOCATION_INDEX";
		public static final String DB_VW_CNTRY_NM = "CNTRY_NM";
		public static final String DB_VW_CNTRY_CD = "CNTRY_CD";
		public static final String DB_VW_RGN_NM = "RGN_NM";
		public static final String DB_VW_RGN_CD = "RGN_CD";
		public static final String DB_VW_STATE_NM = "STATE_NM";
		public static final String DB_VW_ST_CD = "ST_CD";
		public static final String DB_VW_CDT_VALUE_TX = "CDT_VALUE_TX";
		public static final String DB_VW_CDT_VALUE_CD = "CDT_VALUE_CD";
		public static final String DB_VW_STATUS_CD = "STATUS_CD";
		public static final String DB_VW_STATUS_TX = "STATUS_TX";
		public static final String TransportationSetup = "ICLService";
		public static final String SP_LOCATIONDETAILS = "vds.sp.locationdetails";
		
		
		public static final String DB_LOCTN_CD = "LOCTN_CD";
		public static final String DB_LOCTN_NM = "LOCTN_NM";
		public static final String DB_STR1_AD = "STR1_AD";
		public static final String DB_STR2_AD = "STR2_AD";
		public static final String DB_STR3_AD = "STR3_AD";
		public static final String DB_CITY_NM = "CITY_NM";
		public static final String DB_ST_CD="ST_CD";
		public static final String DB_ZIP_CD="ZIP_CD";
		public static final String DB_CNTRY_CD="CNTRY_CD";
		public static final String DB_CNTRY_NM="CNTRY_NM";
		public static final String DB_PHNAC_NO="PHNAC_NO";
		public static final String DB_PHNEXC_NO="PHNEXC_NO";
		public static final String DB_PHONE_NO="PHONE_NO";
		public static final String DB_EXTNSN_NO="EXTNSN_NO";
		
		
		public static final String DB_FAXAC_NO="FAXAC_NO";
		public static final String DB_FAXEXC_NO="FAXEXC_NO";
		public static final String DB_FAXPHN_NO="FAXPHN_NO";
		
		public static final String DB_ADDR_TYPE_NM="ADDR_TYPE_NM";
		public static final String DB_STATUS_DESC="STATUS_DESC";
		public static final String DB_STATUS_CD="STATUS_CD";
		public static final String DB_CDT_VALUE_CD="CDT_VALUE_CD";
		public static final String DB_CDT_VALUE_TX="CDT_VALUE_TX";
		
		public static final String DB_CDT_TYPE_2_CD="TYPE_2_CD";
		public static final String DB_CDT_VALUE_TX2="CDT_VALUE_TX2";
		
		public static final String DB_TYPE_3_CD="TYPE_3_CD";
		public static final String DB_CDT_VALUE_TX3="CDT_VALUE_TX3";
		
		
		public static final String DB_RGN_CD="RGN_CD";
		public static final String DB_LAST_UPDT_TM="LAST_UPDT_TM";  
		public static final String DB_LAST_USERID_CD="LAST_USERID_CD";
		public static final String DB_STATUS_DT="STATUS_DT";
		public static final String DB_CONTC_FRST_NM="CONTC_FRST_NM";
		public static final String DB_CONTC_LAST_NM="CONTC_LAST_NM";
		public static final String DB_CONTC_TITLE_TX="CONTC_TITLE_TX";
		
		public static final String ERRORCODE_E100 = "E100";

		public static final String APPLICATION_URLS = "APPLICATION_URLS";
		public static final String APP_DATA_BASE_URL="APP_DATA_BASE_URL";

	
		public static  final String TYPE_ALL_CODE="ALL";
		public static  final String TYPE_ALL_NAME="ALL";
		public static  final String TYPE_TRUCK_CODE="T";
		public static  final String TYPE_TRUCK_NAME="TRUCK";
		public static  final String TYPE_RAIL_CODE="R";
		public static  final String TYPE_RAIL_NAME="RAIL";
		public static  final String TYPE_AIR_CODE="A";
		public static  final String TYPE_AIR_NAME="AIR";
		public static  final String TYPE_SEA_CODE="V";
		public static  final String TYPE_SEA_NAME="SEA";
		public static final String LOC_FILE_NAME_START_WITH = "locationdetails.file.name.start.with";
		public static final String ACTION_CD_E ="E";
		public static final String CARRIER_EXCEL = "CARRIER_DETAILS";
		public static final String HEADER="GESGEIS1.000MMMAZDA CENTRAL  SDICL            ";
		//public static final String FOOTER="GEE000001";
		public static final String FOOTER="GEE000003";
		public static final String SELECTED_COUNTRY="selectedCountry";
		public static final String STATUSA="A";
		public static final String SHIPPING_COUNTRY="shippingCountry";
		public static final String EMPTYCOUNTRY="SELECT";
		public static final String SELECTED_COUNTRY1="mailcountryCode";
		public static final String SHIPPING_COUNTRY1="shipcountryCode";
		public static final String LOCREGIONCODE="locregionCode";
		public static final String LOCTYPENAME="loctypeName";
		public static final String LOCTYPENAME2="loctypeName2";
		public static final String LOCTYPENAME3="loctypeName3";
		public static final String LOCSTATUSCODE="locstatusCode";
		public static final String LOCATIONSETUPTITLE="locationsetupTitle";
		public static final String MAILSTATENAME="mailstateName";
		public static final String SHIPSTATENAME="shipstateName";
		public static final String LATESTLOC_CODE="locationLatestCode";
		public static final String LOC_DATE="locDate";
		public static final String OLD_LOCSETUP_TYPE="old_input_locationsetup_Type1";
		
	
}
