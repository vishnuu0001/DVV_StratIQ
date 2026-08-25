/**
 * 
 * This is a constant class used to store constant Strings
 * 
 * Jul 15, 2006, 3:49:45 PM
 * <p>
 * Patterns Used: List of patterns used if applicable
 * <p>
 * Copyright 2002 by Mazda North America Operations, Inc., <br>
 * 7755 Irvine Center Drive <br>
 * Irvine, CA 92623, U.S.A. <br>
 * All rights reserved.
 * <p>
 * This software is the confidential and proprietary information of Mazda North
 * America Operations Inc. ("Confidential Information"). You shall not disclose
 * such Confidential Information and shall use it only is accordance with the
 * terms of the license agreement you entered into with Mazda North American
 * Operations.
 * 
 * @author Satyam
 * @version 1.0
 */


package com.mazdausa.corporate.vehicles.distribution.application.util;

import com.mazdausa.common.configuration.EmdcsRuntimeEnvironment;
import com.mazdausa.common.util.ApplicationUtil;

 

 
 
public class LocationConstants {
	

	public static final String LTSLOCATION_INDEX_DATASOURCE="locationIndex";
	public static final String LTS_LOCATIONINDEX_DSN="locationIndex";
	public static final String LTS_LOCATIONSETUP_DSN="locationSetup";
	public static final String LTS_CARRIERSETUP_DSN="carrierSetup";
	
	public static final String LTS_STRING_BLANK = "";
	public static final String LTS_EMPTY_STRING = " ";
	
	public static final String CONFIG_PROPERTY_FILE = "com.mazdausa.corporate.transportation.logistics.properties.dbservices";
	public static final String DB_SCHEMA_NAME="DB_SCHEMA";
	/*** LOCATION FILTER*/
	public static  final String REGION="REGION";
	public static  final String STATE="STATE";
	public static  final String RESET="RESET";
	public static  final String COUNTRY_FUNCTION_NUMBER="001";
	public static  final String REGION_FUNCTION_NUMBER="002ALL";
	public static  final String STATE_FUNCTION_NUMBER="003ALL";
	public static  final String STATE_FUNCTION_NUMBER1="003ALLALL";
	public static  final String US_STATE_FUNCTION_NUMBER="003US ";
	public static  final String TYPE_FUNCTION_NUMBER="004";
	public static  final String STATUS_ACTIVE_CODE="A";
	public static  final String STATUS_ACTIVE_NAME="ACTIVE";
	public static  final String STATUS_ALL_CODE="L";
	public static  final String STATUS_ALL_NAME="ALL";
	public static  final String STATUS_BLOCK_CODE="B";
	public static  final String STATUS_BLOCK_NAME="BLOCK";
	public static  final String STATUS_DELETE_CODE="D";
	public static  final String STATUS_DELETE_NAME="DELETE";
	public static  final String STATUS_INACTIVE_CODE="I";
	public static  final String STATUS_INACTIVE_NAME="INACTIVE";
	public static  final String STATUS_PENDING_CODE="P";
	public static  final String STATUS_PENDING_NAME="PENDING";
	public static  final String STATUS_REPORT_CODE="R";
	public static  final String STATUS_REPORT_NAME="TERMINATED (REPORT)";
	public static  final String STATUS_COMPLETE_CODE="T";
	public static  final String STATUS_COMPLETE_NAME="TERMINATED (COMPLETE)";

	/**LOCATION SEARCH**/
	public static final String LTS_LOCATIONSEARCH_DSN="locationSearch";
	public static final String LOCATIONSEARCH_DETAILS_STORE_PROC="SV40001(?)";
	public static final String LOCATION_SEARCH_STORE_PROC="SV40002(?)";
	public static final String LTS_ROW_BACKGROUND_COLOR_ODD="listingRowBackgroundOdd";
	public static final String LTS_ROW_BACKGROUND_COLOR_EVEN="listingRowBackground";
	
	/***LOCATION SETUP PROCEDURE**********/
	public static final String LOCATION_SETUP_STORE_PROC="SV40003(?,?,?,?)";
	/*******CARRIER SETUP PROCEDURE***************/
	public static final String CARRIER_SETUP_STORE_PROC="SV40005(?,?,?,?)";
	
	
	
	/** LOCATION SAVE,UPDATE AND DELTE**/
	public static final String NEW="NEW";
	public static final String SAVE="SAVE";
	public static final String UPDATE="UPDATE";
	public static final String DELETE="DELETE";
	public static final String RETRIVE="RETRIVE";
	public static final String REGIONSTATECHANGE="REGIONSTATECHANGE";
	public static final String ADDOPTION="ADD";
	
	
	/** CARRIER TIMES ****/
	/*public static final String CARRIER_FUNCTION_NUMBER="005";
	public static final String CARRIER_ORIGIN_CODE_NUMBER="004";
	public static final String CARRIER_DEST_STATE_CODE_NUMBER="004";
	public static final String CARRIER_ORIGIN_TYPE_CODE_NUMBER="004";
	public static final String EFFECTIVE_DATE_CURRENT_CODE="C";
	public static final String EFFECTIVE_DATE_CURRENT_NAME="Current";*/
	
	/** CARRIER INDEX **/
	public static final String CARRIERINDEX_DETAILS_STORE_PROC="SV40001(?)";
	public static final String LTS_CARRIERINDEX_DSN="carrierIndex";
	public static  final String CARRIERCODE_FUNCTION_NUMBER="005";
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
	
	
	public static final String LTS_CARRIERSEARCH_DSN="carrierSearch";
	/*******Location variable*************/
	public static final String DEFAULT_SELECTION="Y";
	public static final String STATUS_VALUE="A";
	public static final String PAYMENT_STATUS="S";
	
	
	
	 /**LOCATION SEARCH PERAMETER **************/
	public static final int	LOCATION_SEARCH_LOCTN_NAME=30;
	public static final int LOCATION_SEARCH_LOCATION_CODE=5;
	public static final int LOCATION_SEARCH_COUNTRY_CODE=3;
	public static final int LOCATION_SEARCH_REGION_CODE=3;
	public static final int LOCATION_SEARCH_STATE_CODE=3;
	public static final int LOCATION_SEARCH_ZIP_CODE=9;
	public static final int LOCATION_SEARCH_CITY_NAME=25;
	public static final int LOCATION_SEARCH_STATUS_CODE=3;
	public static final int LOCATION_SEARCH_LOCATION_TYPE_CODE=3;//Total Length 84

	
	
	/********LOCATION UPDATE AND SAVE FIELD*************/
	public static final int	LOCATION_ACTION_CODE=1; 
	public static final int	LOCATION_USER_ID=8;
	public static final int LOCATION_LOCATION_CODE=5;
	public static final int	LOCATION_LOCATION_NAME=30;
	public static final int	LOCATION_REGION_CODE=2;
	public static final int	LOCATION_LOCATION_TYPE1_CODE=2;
	public static final int	LOCATION_LOCATION_TYPE2_CODE=2;
	public static final int	LOCATION_LOCATION_TYPE3_CODE=2;
	public static final int	LOCATION_STATUS_CODE=1; 
	public static final int	LOCATION_STATUS_DATE=10; 
	
	public static final int	LOCATION_CONTACT_FIRST_NAME=15;
	public static final int	LOCATION_CONTACT_LAST_NAME=20;
	public static final int	LOCATION_CONTACT_TITLE=20;
	public static final int	LOCATION_AREA_CODE=3;
	public static final int	LOCATION_EXCHANGE=3;
	public static final int	LOCATION_PHONE_NUMBER=4;
	public static final int	LOCATION_EXTENSION_NO=5;
	public static final int	LOCATION_FAX_AREA_CODE=3;
	public static final int	LOCATION_FAX_EXCHANGE=3;
	public static final int	LOCATION_FAX_NUMBER=4;
	
	
	public static final int	LOCATION_MAILING_STREET1=30;
	public static final int	LOCATION_MAILING_STREET2=30;
	public static final int	LOCATION_MAILING_STREET3=30;
	public static final int	LOCATION_MAILING_CITY_NAME=25;
	public static final int	LOCATION_MAILING_STATE_CODE=3;
	public static final int	LOCATION_MAILING_ZIP_CODE=9;
	public static final int	LOCATION_MAILING_COUNTRY_CODE=2;
	public static final int	LOCATION_SHIPPING_STREET1=30;
	public static final int	LOCATION_SHIPPING_STREET2=30;
	public static final int	LOCATION_SHIPPING_STREET3=30;
	

	public static final int	LOCATION_SHIPPING_CITY_NAME=25;
	public static final int	LOCATION_SHIPPING_STATE_CODE=3;
	public static final int	LOCATION_SHIPPING_ZIP_CODE=9;
	public static final int	LOCATION_SHIPPING_COUNTRY_CODE=2;
	public static final int	LOCATION_EMAIL_ADDRESS=30;
	public static final int	LOCATION_CELL_AREA_CODE=3;
	public static final int	LOCATION_CELL_EXCHANGE=3;
	public static final int	LOCATION_CELL_NUMBER=4;
	
	public static final int LOCATION_LAST_UPDATED_TIME_STAMP=26;
	public static final int LOCATION_MAILING_LAST_UPDATED_TIME_STAMP=26; 
	public static final int LOCATION_SHIPPING_LAST_UPDATED_TIME_STAMP=26;
	public static final int LOCATION_CONTACT_LAST_UPDATED_TIME_STAMP=26;
	
	
	/** CARRIER SEARCH **/
	public static final String CARRIERSEARCH_DETAILS_STORE_PROC="SV40004(?)";
	
	
	
	/** ERROR SP **/
	public static final String ERRORMESSAGE_STORE_PROC="SM34170(?,?)";
	
	
	 /**CARRIER SEARCH PERAMETER **************/
	public static final int	CARRIER_SEARCH_CARRIER_NAME=40;
	public static final int CARRIER_SEARCH_CARRIER_CODE=5;
	public static final int CARRIER_SEARCH_STATUS_CODE=3;
	public static final int CARRIER_SEARCH_CARRIER_TYPE_CODE=3;
	public static final int CARRIER_SEARCH_CARRIER_CURRENCY=1;
	
	/********** Carrier Save,Update and Delete input peramenters1***************/
	//1-10
	public static final int CARRIER_ACTION_CODE=1;
	public static final int CARRIER_USERID_CODE=8;
	public static final int CARRIER_CARRIER_CODE=5;
	public static final int CARRIER_CARRIER_NAME=30;
	public static final int CARRIER_TYPE_DESC=10;
	public static final int CARRIER_STATUS_CODE1=3;
	public static final int CARRIER_STATUS_CODE=1;
	
	public static final int CARRIER_STATUS_DATE=10;
	public static final int CARRIER_PYMT_TYPE_CODE=1;
	public static final int CARRIER_RECIEVE_DELIVERY_DATA=1;
	public static final int CARRIER_RETURN_ERROR_DATA=1;
	
	//10-20
	public static final int CARRIER_CONTACT_NO1=15;
	public static final int CARRIER_CONTACT_DESC1=30;
	public static final int CARRIER_CONTACT_NO2=15;
	public static final int CARRIER_CONTACT_DESC2=30;
	public static final int CARRIER_CONTACT_NO3=15;
	public static final int CARRIER_CONTACT_DESC3=30;
	public static final int CARRIER_CONTACT_NO4=15;
	public static final int CARRIER_CONTACT_DESC4=30;
	public static final int CARRIER_CONTACT_NO5=15;
	public static final int CARRIER_CONTACT_DESC5=30;
	
	//20-30
	public static final int CARRIER_CONTACT_NO6=15;
	public static final int CARRIER_CONTACT_DESC6=30;
	public static final int CARRIER_MAILING_ST1=30;
	public static final int CARRIER_MAILING_ST2=30;
	public static final int CARRIER_MAILING_ST3=30;
	public static final int CARRIER_MAILING_CITY=25;
	public static final int CARRIER_MAILING_STATE_CODE=3;
	public static final int CARRIER_MAILING_STATE=20;
	public static final int CARRIER_MAILING_ZIP_CODE=9;
	public static final int CARRIER_MAILING_COUNTRY_CODE=2;
	
	//30-40
	public static final int CARRIER_MAILING_COUNTRY_NAME=30;
	public static final int CARRIER_CONTACT_FIRST_NAME =15;
	public static final int CARRIER_CONTACT_LAST_NAME=20;
	public static final int CARRIER_CONTACT_TITLE=20;
	public static final int CARRIER_BUS_AREA_CODE=3;
	public static final int CARRIER_BUS_EXCHANGE=3;
	public static final int CARRIER_BUS_PHONE=4;
	public static final int CARRIER_BUS_EXTN=5;
	public static final int CARRIER_FAX_AREA_CODE=3;
	public static final int CARRIER_FAX_EXCHANGE=3;
	
	//40-50
	public static final int CARRIER_FAX_PHONE=4;
	public static final int CARRIER_EMAIL_ID=30;
	public static final int CARRIER_CELL_AREA_CODE=3;
	public static final int CARRIER_CELL_EXCHANGE=3;
	public static final int CARRIER_CELL_PHONE=4;
	public static final int CARRIER_SHIPPING_ST1=30;
	public static final int CARRIER_SHIPPING_ST2=30;
	public static final int CARRIER_SHIPPING_ST3=30;
	public static final int CARRIER_SHIPPING_CITY=25;
	public static final int CARRIER_SHIPPING_STATE_CODE=3;
	public static final int CARRIER_SHIPPING_STATE=20;
	
	//50-53
	public static final int CARRIER_SHIPPING_ZIP_CODE=9;
	public static final int CARRIER_SHIPPING_COUNTRY_CODE=2;
	public static final int CARRIER_SHIPPING_COUNTRY=30;
	
	public static final int CARRIER_MAX_LAST_UPDATES_TIME_STAMP=26;
	public static final int CARRIER_LAST_UPDATES_TIME_STAMP=26;
	public static final int CARRIER_MAILING_LAST_UPDATES_TIME_STAMP=26;
	public static final int CARRIER_CONTACT_LAST_UPDATES_TIME_STAMP=26;
	public static final int CARRIER_SHIPPING_LAST_UPDATES_TIME_STAMP=26;
	
	/********Error Query ****************/
	public static final String LTS_ADMIN="\"ltsadmin\"";
	public static final String LTS_INQUIRY="\"ltsinquiry\""; 	
	public static final String LTS_NONFINANCE="\"ltsnofinanceinquiry\"";
	public static final String GENERATE_EXCEL_REPORT_CMDID="GENERATEEXCEL";
	public static final String GENERATE_EXCEL_REPORT="generateExcel";
	public static final String GENERATE_LOCATION_EXCEL_REPORT="locationExcelReport";
	public static final String APPLICATION_VNDMS_EXCEL="application/vnd.ms-excel; charset=UTF-8";
	public static final String CONTENT_DISPOSITION="content-disposition";
	public static final String ATTACHMENT_FILENAME="attachment; filename=";
	/****Carrier Constant**************/
	public static final String LTS_USER_PRIVILEGE="UserPrivilege";
	public static final String CARRIER_INDEX_SUCCESS_PAGE="success";
	public static final String CARRIER_INDEX_FAILURE_PAGE="failure";
	public static final String CARRIER_INDEX_PROPERTIES_KEY="name";
	public static final String CARRIER_INDEX_PROPERTIES_VALUE="carrier.index";
	public static final String CARRIER_RESET="RESET";
	public static final String CARRIER_COUNTRY_CHANGE="COUNTRYCHANGE";
	public static final String CARRIER_SEARCH_MSG="Search exceeds more than 1000 records. Please narrow down the search criteria";
	public static final String CARRIER_SAVE_ACTION_CODE="S";
	public static final String CARRIER_SAVE_ACTION_CONFIRM_CODE="A";
	public static final String CARRIER_SAVE_ACTION_CHANGE_CODE="C";
	public static final String CARRIER_MAILING_COUNTRY="MAILINGCOUNTRY";
	public static final String CARRIER_SHIPPING_COUNTRY_CHANGE="SHIPPINGCOUNTRY";
	public static final String CARRIER_COUNTRY_ALL=" ALL";
	public static final String CARRIER_LANGUAGE_CODE="EN";
	public static final String CARRIER_CONFIRMMSG="CONFIRMMSG";
	public static final String CARRIER_ERRORMSG="ERRORMSG";
	public static final String CARRIER_SUCCESSMSG="SUCCESSMSG";
	public static final String CARRIER_FUNCTION_N0_00="0";
	public static final String CARRIER_FUNCTION_NO_01="1";
	public static final String CARRIER_FUNCTION_NO_02="2";
	public static final String CARRIER_FUNCTION_NO_03="3";
	public static final String CARRIER_FUNCTION_NO_04="4";
	public static final String CARRIER_FUNCTION_NO_05="5";
	public static final String CARRIER_SEARCH_STATUS_MSG="No records found for search criteria.";
	public static final String CARRIER_SEARCH_SUCCESS_PAGE="success";
	public static final String CARRIER_SEARCH_FAILURE_PAGE="failure";
	public static final String CARRIER_EXCEL_FILE_NAME="carrierExcelReport.xls";
	public static final String LOCATION_EXCEL_FILE_NAME="locationExcelReport.xls";
	public static final String CARRIER_BUTTON_STATUS="True";
	public static final String CARRIER_SETUP_NEWENTRY_PAGE="carrierNewEntry";
	public static final String CARRIER_SETUP_UPDATE_ENTRY_PAGE="carrierUpdateEntry";
	public static final String CARRIER_BUTTON_STATUS_FALSE="False";
	public static final String CARRIER_SARCH_PAGE="searchPage";
	public static final String CARRIER_SETUP_RETURNCODE="RETURNCODE";
	public static final String CARRIER_SETUP_SAVEMSG="SAVEMSG";
	public static final String CARRIER_COUNTRY_LIST="COUNTRYLIST";
	public static final String CARRIER_STATELIST_LIST="STATELIST";
	public static final String CARRIER_SETUP_ERROR_PAGE="setupError";
	public static final String CARRIER_STATE_NO="003";
	public static final String CARRIER_SELECT="Select";
	/***********Location Constant**************/
	public static final String LOCATION_INDEX_SPAGE="locationindx";
	public static final String LOCATION_COUNTRYLIST="COUNTRYLIST";
	public static final String LOCATION_LOCATIONTYPELIST="LOCATIONTYPELIST";
	public static final String LOCATION_REGIONLIST="REGIONLIST";
	public static final String LOCATION_STATELIST="STATELIST";
	public static final String LOCATION_USREGION="USREGION";
	public static final String LOCATION_USSTATELIST="USSTATELIST";
	public static final String LOCATION_INDEX_FUNCTION_NO_001="001";
	public static final String LOCATION_SEARCH_SUCCESS="success";
	public static final String LOCATION_SEARCH_FAILURE="failure";
	public static final String LOCATION_RESET="RESET";
	public static final String LOCATION_FILTER_SUCCESS="filterSuccess";
	public static final String LOCATION_FILTER_FAILURE="filterError";
	public static final String LOCATION_FILTER_EMPTY="empty";
	public static final String LOCATION_FILTER_FUNCTION_NO_002="002";
	public static final String LOCATION_FILTER_FUNCTION_NO_003="003";
	public static final String LOCATION_SEARCH_MSG="Search exceeds more than 1000 records. Please narrow down the search criteria";
	public static final String LOCATION_BUTTON_STATUS="True";
	public static final String LOCATION_SETUP_NEW_ENTRY_PAGE="setupNewEntry";
	public static final String LOCATION_SETUP_UPDATE_ENTRY_PAGE="setupUpdate";
	public static final String LOCATION_ACTION_CODE_A="A";
	public static final String LOCATION_ACTION_CODE_S="S";
	public static final String LOCATION_ACTION_CODE_C="C";
	public static final String LOCATION_ACTION_TYPE_SAVE="SAVE";
	public static final String LOCATION_OPERATION_TYPE_UPDATE="UPDATE";
	public static final String LOCATION_OPERATION_TYPE_SAVE="SAVE";
	public static final String LOCATION_MESSAGE_CONFIRMMSG="CONFIRMMSG";
	public static final String LOCATION_MESSAGE_ERRORMSG="ERRORMSG";
	public static final String LOCATION_MESSAGE_SUCCESSMSG="SUCCESSMSG";
	public static final String LOCATION_BUTTON_STATUS_FALSE="False";
	public static final String LOCATION_STATE="STATE";
	public static final String LOCATION_SHIPPINGCOUNTRY ="SHIPPINGCOUNTRY";
	public static final String LOCATION_REGION="REGION";
	public static final String LOCATION_RETURN_CODE="RETURNCODE";
	public static final String LOCATION_SAVEMSG="SAVEMSG";
	public static final String LOCATION_SETUP_UPDATE_ERROR_PAGE="updateError";
	public static final String LOCATION_SETUP_NEW_ERROR_PAGE="newError";
	public static final String LOCATION_SELECT="Select";
	public static final String LOCATION_ALL=" ALL";
	public static final String LOCATION_INDEX_MSG="Selected country does not have region! Select other country";
	public static final String LOCATION_STATE_MSG="Selected region does not have state! Select other region";
	
		
	/*** ERROR CONSTANT *******/
	
	public static final int ERRORMESSAGE_SIZE=5;
	
	
	
	/***********Times ********************/
	
	 
	public static final int USER_ID=8;
	public static final int CARRIER_CODE=5;
	//changes made for LTS enhancemets 7-27-09 Arthy
	public static final int SELECT_FLAG=1;
	//end
	
	public static final int TIMES_CARRIER_STATUS_CODE=3;
	public static final int CARRIER_TYPE_CODE=10;
	public static final int ORIGIN_CODE=5;
	public static final int ORIGIN_STATUS_CODE=3;
	public static final int ORIGIN_TYPE_CODE=3;
	public static final int DESTINATION_CODE=5;
	public static final int DESTINATION_STATUS_CODE=3;
	public static final int DESTINATION_STATE_CODE=3;
	public static final int EFFECTIVE_DATE_DESC=10;
	public static final int PRIOR_ORIGIN_CODE=5;
	public static final int NEXT_DESTINATION_CODE=5;
	public static final int START_DATE=10;
	public static final int END_DATE=10;
	public static final int CARRIER_PRIORITY_CODE=1;
	public static final int TRANSIT_HOURS=5;
	public static final int FLAT_RATE_AMOUNT=8;
	public static final int PER_MILE_RATE=6;
	public static final int BI_LEVEL_RATE=5;
	public static final int TRI_LEVEL_RATE=5;
  //Changes done for LTS Enhancement on 07/23/09
	public static final int AUTOMAX_RATE=5;
	public static final int ARTICULATE_RATE=5;
	public static final int VIN_BI_RATE=5;
	public static final int VIN_TRI_RATE=5;
 // Changes Ends
	public static final int LAST_UPDATED_TIME=26;
	public static final String OPEN_DATE="10"; 
	public static final String OPEN="OPEN";
	public static final String SAVE_ACTION_CODE="S";
	public static final String DELETE_ACTION_CODE="D";
	//LTS enhancement 7-29-09
	public static final String MASS_DELETE_ACTION_CODE="X";
	//end
	public static final String MASSUPDATE_ACTION_CODE="M";
	
	public static final int RATE_EXPIRY=4;
	public static final int PRIORITY_FLAG=1;
	public static final int PAGE_NUM=3;
	public static final int REC_CNT=3;
	public static final int SORT_COLUMN=50;
	public static final int SORT_TYPE=1;
	
	public static final String REC_CNT_PER_PAGE="10";
	
	/** TRANSIT TIMES UPDATE **/
	public static final String TRANSITTIMESUPDATE_DETAILS_STORE_PROC="SV40007(?,?,?,?)";
	public static final String LTS_TRANSITTIMESUPDATE_DSN="transitTimesUpdate";
	public static final String TRANSITTIMESUPDATE_SAVE="S";
	public static final String TRANSITTIMESUPDATE_CONFIRMADD="A";
	public static final String TRANSITTIMESUPDATE_CONFIRMCHANGE="C";
	public static final String TRANSITTIMESUPDATE_DELETE="D";
	public static final String NEWTRANSITTIMESSEARCH="newTransitTimeSearch";
	public static final String TIMES_UPDATE_ERROR_KEY="times.update";
	public static final String TIMES_UPDATE_EXCEPTION_MESSAGE="Problem occurred while performing the operation! Please contact Admin";

	/** CARRIER TRANSIT TIMES FILTER  ****/
	public static final String LTS_CARRIER_TIMES_DSN="carrierTimes";
	 
	public static final String CARRIER_FUNCTION_NUMBER="005";
	public static final String CARRIER_ORIGIN_CODE_NUMBER="006         ALLALL";
	public static final String CARRIER_DESTINATION_CODE_NUMBER="007      ALL   ALL";
	public static final String CARRIER_DEST_STATE_CODE_NUMBER="003";
	public static final String CARRIER_ORIGIN_TYPE_CODE_NUMBER="004";
	public static final String EFFECTIVE_DATE_PAST_CODE="PAST      ";
	public static final String EFFECTIVE_DATE_PAST_NAME="PAST";
	public static final String EFFECTIVE_DATE_CURRENT_CODE="CURRENT   ";
	public static final String EFFECTIVE_DATE_CURRENT_NAME="CURRENT";
	public static final String EFFECTIVE_DATE_FUTURE_CODE="FUTURE    ";
	public static final String EFFECTIVE_DATE_FUTURE_NAME="FUTURE";
	public static  final String TIMESFILTERSUCCESS="timesFilterSuccess";
	public static  final String TIMESFILTERFAILURE="timesFilterFailure";
	public static  final String TIMESEXCELFILENAME="transitTimesExcelReport.xls";
	public static  final String NORECORDSRETURNED="No records found;Please change the search criteria and search again";
	public static final String TIMES_SEARCH_FILTER_ERRORKEY="times.searchfilter";
	public static final String TIMES_SEARCH_FILTER_EXCEPTION_MESSAGE="Problem occurred while performing the operation in carrier transit times search! Please contact Admin";

	/** TRANSIT TIMES SEARCH UPDATE **/
	public static final String LTS_TRANSIT_TIMES_SEARCH_UPDATE_STORE_PROC="SV40010(?,?,?,?,?)";
	public static final String LTS_TRANSIT_TIMES_SEARCH_UPDATE_DSN="transitTimesSearchUpdate";
	public static final String TIMES_SEARCH_UPDATE_ERRORKEY="times.searchupdate";
	public static final String TIMES_SEARCH_UPDATE_EXCEPTION_MESSAGE="Problem occurred while performing the operation! Please contact Admin";
	public static final String UPDATE_SUCCESS="Y";
	public static final String UPDATE_FAILURE="N";
	
	/** CARRIER TRANSIT TIMES SEARCH **/
	public static final String CARRIERTRANSITTIMESSEARCH_DETAILS_STORE_PROC="SV40006(?)";
	public static final String LTS_CARRIERTRANSITTIMESSEARCH_DSN="carrierTransitTimesSearch";
	public static final String TIMES_SEARCH_ERRORKEY="times.search";
	public static final String TIMES_SEARCH_EXCEPTION_MESSAGE="Problem occurred while performing the operation in transit times search! Please contact Admin";
	
	 	
	/** TRANSIT TIMES SAVE,UPDATE AND DELTE**/
	 
	public static final String ERROR="ERROR";
	public static final String SUCCESS="SUCCESS";
	public static final String SEARCH="SEARCH";
	public static final String NOSEARCH="NOSEARCH";

	/*** USER CONSTANTS ****/
	public static final String USER_GROUP_CONST="\"epcfrontcontroller\",\"it-java\",\"partsinquiry\",\"ptsaccprinq\",\"salesinquiry\",\"serviceinquiry\",\"svcwrntyrecallinq\",\"vehreqinq0\",\"timecardagency\",\"timecardadmin\",\"timecardproject\",\"timecardresource\",\"ltsinquiry\",\"ltsadmin\"," +																							"\"ltsnofinanceinquiry\"";
	public static final String USERPRIVILEGE="UserPrivilege";

	
	
 	public static final String FORWARDSUCCESS="success";
	public static final String FORWARDFAILURE="failure";
	public static final String ERRORNAME="name";
	public static final String FALSE="false";
	public static final String TRUE="true";
	public static final String NARROWDOWNSEARCH="Please narrow down your selection, as the default search returned more data";
	public static final String ZERO="0";
	public static final String ENGLISH="EN";
	public static final String BLANK="";
	public static final int CHANGE=3;
	public static final int SOFTERROR=1;
	public static final int HARDERROR=2;
	public static final int ADD=4;
	public static final int CODEADD=5;
	public static final int COMPLETED=0;
	
	public static  final String TIMES_TYPE_ALL_CODE="ALL";
	public static  final String TIMES_TYPE_ALL_NAME="ALL";
//	public static  final String TIMES_TYPE_TRUCK_CODE="TRUCK     ";
	public static  final String TIMES_TYPE_TRUCK_CODE="T         ";
	public static  final String TIMES_TYPE_TRUCK_NAME="TRUCK";
//	public static  final String TIMES_TYPE_RAIL_CODE="RAIL      ";
	public static  final String TIMES_TYPE_RAIL_CODE="R         ";
	public static  final String TIMES_TYPE_RAIL_NAME="RAIL";
//	public static  final String TIMES_TYPE_AIR_CODE="AIR       ";
	public static  final String TIMES_TYPE_AIR_CODE="A         ";
	public static  final String TIMES_TYPE_AIR_NAME="AIR";
//	public static  final String TIMES_TYPE_SEA_CODE="SEA       ";
	public static  final String TIMES_TYPE_SEA_CODE="S         ";
	public static  final String TIMES_TYPE_SEA_NAME="SEA";
	public static  final String TIMES_TYPE_SHIP_CODE="S         ";
	public static  final String TIMES_TYPE_SHIP_NAME="SEA";
	
	 
	 	
	/******** Transit Rates Constant ****************/
	
	/** TRANSIT RATES **/
	public static final String LTS_TRANSIT_RATES_DSN="transitRates";
	public static final String TRANSIT_RATES_FUNCTION_NUMBER="010";
	public static final String TRANSIT_RATES_Y="Y";
	public static final String TRANSIT_RATES_N="N";
	public static final String TRANSIT_RATES_RAIL="RAIL";
	public static final String TRANSIT_RATES_TRUCK="TRUCK";
	public static final String TRANSIT_RATES_SHIP="SHIP";
	public static final String TRANSIT_RATES_TRUCK_OR_RAIL_MAP = "transitRatesTruckRailMap";
	public static final String TRANSIT_RATES_TRUCK_OR_RAIL_LIST = "transitRatesTruckRailList";
	public static final String CURRENCY_LIST = "currencyList";
	/** TRANSIT RATES SEARCH **/
	public static final String LTS_TRANSIT_RATES_SEARCH_STORE_PROC="SV40008(?)";
	public static final String LTS_TRANSIT_RATES_SEARCH_ADD_STORE_PROC="SV40018(?,?,?)";
	public static final String LTS_TRANSIT_RATES_SEARCH_DSN="transitRatesSearch";
	public static final String LTS_TRANSIT_RATES_SEARCH_TWO_STORE_PROC="SV40001(?)";
	
	/** TRANSIT RATES UPDATE **/
	public static final String TRANSITRATESUPDATE_SAVE="S";
	public static final String TRANSITRATESUPDATE_CONFIRMADD="A";
	public static final String TRANSITRATESUPDATE_CONFIRMCHANGE="C";
	public static final String TRANSITRATESUPDATE_DELETE="D";
	public static final String LTS_TRANSIT_RATES_UPDATE_STORE_PROC="SV40009(?,?,?,?)";
	public static final String LTS_TRANSIT_RATES_UPDATE_DSN="transitRatesUpdate";
	public static final String LTS_TRANSIT_UPDATE_STORE_PROC="SV40023(?,?,?,?)";
	/** TRANSIT RATES SEARCH UPDATE **/
	public static final String LTS_TRANSIT_RATES_SEARCH_UPDATE_STORE_PROC="SV40011(?,?,?,?,?)";
	public static final String LTS_TRANSIT_RATES_SEARCH_UPDATE_DSN="transitRatesSearchUpdate";
	
    /**** Transit Rates $ constant********/
	public static final String FUNCTION_CODE_008="008";
	public static final String DOLLAR_SYMBOL="$";
	 
	
	/***** Transit Rates Constants**********/
	
	
	public static final String DESTINATIONCODELIST="DESTINATIONCODELIST";
	public static final String CARRIERCODELIST="CARRIERCODELIST";
	public static final String CARRIERNAMES="CARRIERNAMES";
	public static final String ORIGINCODELIST="ORIGINCODELIST";
	public static final String ORIGINNAMES="ORIGINNAMES";
	public static final String DESTINATIONNAMES="DESTINATIONNAMES";
	
	
	public static final String RATES_SUCCESS="SUCCESS";
	public static final String RATES_SEARCH="SEARCH";
	
	public static final String RATES_SEARCH_MSG="No records found for search criteria.";
	
	public static final String RATES_NOSEARCH="NOSEARCH";
	
	public static final String RATES_ACTIONCODE_M="M";
	
	public static final String RATES_FALSE="false";
	
	public static final String RATES_SAVEBUTTON_TRUE="true";
	
	public static final String RATES_SAVEBUTTON_FALSE="false";
	
	public static final String RATES_SEARCH_UPDATE_MSG="No records found for search criteria.";
	
	//public static final String RATES_SEARCH_MESSAGE="Please narrow down your selection, as the default search returned more data's";
	public static final String RATES_SEARCH_MESSAGE="Search exceeds more than 250 records. Please narrow down the search criteria.";
	
	public static final String RATES_ERROR="ERROR";
	
	public static final String RATES_CRPP188="CRPP188";
	
	public static final String RATESEXCELFILENAME="transitRatesExcelReport.xls";
	
	
	public static final String RATES_ACTION_SUCCESS_PAGE="success";
	
	public static final String RATES_ACTION_FAILURE_PAGE="failure";
	 
	public static final String RATES_SEARCH_PAGE="newTransitRatesSearch";
	
	public static final String RATES_TRANSIT_SEARCH_PAGE="transitRatesSearch";
	
	//Route Segment Sp
	
	public static final String ROUTESEGMENT_STORE_PROC="SV40017(?,?,?,?)";
	
 
	public static final String RAMP_CODE_FUNCTION_NUMBER="006         RH ALL";
	
	
	/*********** Route Segment SV40017 Constants ********************/
	 
public static final int RS_ACTION_CD=1;
public static final int RS_USER_ID=8;
public static final int RS_ORIG_CD=5;
public static final int RS_RAMP_CD=5;
public static final int RS_DEST_CD=5;
public static final int RS_BEG_EFF_DT=10;
public static final int RS_END_EFF_DT=10;

public static final int RS_TT_ORIG_CD=5;
public static final int RS_TT_DEST_CD=5;
public static final int RS_TT_CARR_CD=5;
public static final int RS_TT_BEG_EFF_DT=10;
public static final int RS_TT_END_EFF_DT=10;
public static final int RS_TT_TRANSIT_HRS=5;
public static final int RS_TT_MILE_AMT=5;
public static final int RS_TT_LAST_UPDT_TM=26;
public static final int RS_TT_TOT_TRANSIT_HRS=5;

public static final int RS_TR_ORIG_CD=5;
public static final int RS_TR_DEST_CD=5;
public static final int RS_TR_CARR_CD=5;
public static final int RS_TR_BEG_EFF_DT=10;
public static final int RS_TR_END_EFF_DT=10;
public static final int RS_TR_FULL_BI_AM=5;
public static final int RS_TR_FULL_TRI_AM=5;
public static final int RS_TR_FLAT_AM=8; //size changed
public static final int RS_TR_PER_MILE_AM=5; //size changed
public static final int RS_TR_LAST_UPDT_TM=26;
public static final int RS_TR_TOT_BI_AM=5;
public static final int RS_TR_TOT_TRI_AM=5;
public static final int RS_TR_TOT_TRK_AM=8; //size changed


/*************** ROUTE SEGMENT***************/
public static final String ROUTESEGMENTEXCELFILENAME="routeSegmentExcelReport.xls";
public static final String ROUTE_SEGMENT_INDEX_DSN="routeSegment";
public static final String ROUTESEGMENT_SEARCH_STORE_PROC="SV40016(?)";
public static final String ROUTESEGMENT_SEARCH_NEW_PROC="SV40020(?,?,?)";

public static final int ORIGIN_SEGMENT_CODE=5;	
public static final int ORIGIN_SEGMENT_STATUS_CODE=3;
public static final int RAMP_SEGMENT_CODE=5;
public static final int RAMP_SEGMENT_STATUS_CODE=3;
public static final int EFFECTIVE_DATES=10;
public static final int FINAL_DESTINATION=5;
public static final int SEGMNET_STARTDATE=10;
public static final int SEGMENT_START_TIME=8;
public static final String ROUTE_SEGMENT_SEARCH_EXCEPTION_MESSAGE="Problem occurred while performing the operation in route segment search! Please contact Admin";

public static final String ROUTE_SEGMENTBLANK=" ";
public static final String START_TIME="23.00.00";
public static final String EN="N";
public static final String Y="Y";
public static final String ROUTESEARCH_DRAFT_STORE_PROC="SV40013(?,?,?)";
public static final int RAMP_CODE=5;

public static final String ADDTIMES="ADDTIMES";
public static final String ADDRATES="ADDRATES";
public static final String ADD_MULTI_ROWS="ADD_MULTI_ROWS";
public static final String ROUTE_SEGMENT_EFFDATE="effDate";
public static final String ROUTE_SEGMENT_ORIGINCODE="originCode";
public static final String ROUTE_SEGMENT_RAMPCODE="rampCode";
public static final String ROUTE_SEGMENT_TRUE="True";
public static final String ROUTE_SEGMENT_ONE="1";
public static final String ROUTE_SEGMENT_NEWENTRY="routeSegmentNewEntry";
public static final String ROUTE_SEGMENT_USER="USEr";
public static final String ROUTE_SEGMENT_CONFIRMMSG="CONFIRMMSG";
public static final String ROUTE_SEGMENT_SAVEMSG="SAVEMSG";
public static final String ROUTE_SEGMENT_ERRORMSG="ERRORMSG";
public static final String ROUTE_SEGMENT_UPDATE_CONFIRMADD="A";
public static final String ROUTE_SEGMENT_SUCCESSMSG="SUCCESSMSG";
public static final String ROUTE_SEGMENT_RETURNCODE="RETURNCODE";
public static final String ROUTE_SEGMENT_ZERO="0";
public static final String ROUTE_SEGMENT_UPDATE="UPDATE";
public static final String ROUTE_SEGMENT_THREE="3";
public static final String ROUTE_SEGMENT_UPDATEPAGE="routeSegmentUpdate";
public static final String ROUTE_SEGMENT_A="A";
public static final String ROUTE_SEGMENT_C="C";
public static final String ROUTE_SEGMENT_DA="DA";
public static final String ROUTE_SEGMENT_SEARCHPAGE="searchPage";
public static final String ROUTE_SEGMENT_FALSE="False";
public static final String ROUTE_SEGMENT_SETUP="routeSegmentSetup";
public static final String ROUTE_SEGMENT_OPEN="OPEN";

public static final String ROUTE_SEGMENT_ORIGIN_CODE_NUMBER="006         RH ALL"; //Added here to fix issue#138
 
public static final String ROUTE_SEGMENT_Y="Y";
public static final String ROUTE_SEGMENT_R="R";
public static final String ROUTE_SEGMENT_T="T";


//Max Rows Count in route segment search
public static final int ROUTE_SEGMENT_MAX_ROW_COUNT=1000;
public static final String ROUTE_SEGMENT_DEFAULT_SEARCH_MESSAGE="Search exceeds more than " + ROUTE_SEGMENT_MAX_ROW_COUNT + " records. Please narrow down the search criteria.";
 
/*** ROUTE INDEX ***/
public static final String LOCATION_DETAILS_FUNCTION_NUMBER="004";
//public static final String RAMP_CODE_FUNCTION_NUMBER="006         RH ALL";
public static final String ROUTE_INDEX_DSN="routeIndex";
public static final String PRIORITY_ONE="1";
public static final String PRIORITY_TWO="2";
public static final String PRIORITY_THREE="3";
public static final String PRIORITY_FOUR="4";
public static final String PRIORITY_FIVE="5";
public static final String PRIORITY_SIX="6";
public static final String PRIORITY_SEVEN="7";
public static final String PRIORITY_EIGHT="8";
public static final String PRIORITY_NINE="9";
public static final String ROUTE_INDEX_ERROR_KEY="route.index";
public static final String ROUTE_INDEX_EXCEPTION_MESSAGE="Problem occurred while performing the operation in route search! Please contact Admin";

public static final String ROUTE_DEFAULT_SEARCH_MESSAGE="Search exceeds more than 250 records. Please narrow down the search criteria.";
public static final String ROUTE__ORIGIN_CODE_NUMBER="006         RH ALL"; //Added here to fix issue#138


//public static final String ROUTE_SEGMENT_ORIGINCODE="ORIGINCODE";
public static final String ROUTE_SEGMENT_ORIGINNAMES="ORIGINNAMES";
//public static final String ROUTE_SEGMENT_RAMPCODE="RAMPCODE";
public static final String ROUTE_SEGMENT_RAMPNAMES="RAMPNAMES";
public static final String ROUTE_SEGMENT_CARRIERCODE="CARRIERCODE";
public static final String ROUTE_SEGMENT_CARRIERNAMES="CARRIERNAMES";
public static final String ROUTE_SEGMENT_DESTINATIONCODE="DESTINATIONCODE";
public static final String ROUTE_SEGMENT_DESTNAMES="DESTNAMES";
public static final String ROUTE_SEGMENT_CARRTYPE="CARRTYPE";


/*** ROUTE SEARCH ***/
public static final String ROUTEEXCELFILENAME="routeExcelReport.xls";
public static final String ROUTE_SEARCH_ERRORKEY="route.search";
public static final String ROUTESEARCH_STORE_PROC="SV40012(?)";
public static final String ROUTESEARCH_NEW_STORE_PROC="SV40019(?,?,?)";
//public static final String ROUTESEARCH_DRAFT_STORE_PROC="SV40013(?,?,?)";
public static final String LTS_ROUTESEARCH_DSN="routeSearch";
//public static final int RAMP_CODE=5;
public static final int RAMP_STATUS_CODE=3;
public static final int DESTINATION_TYPE_CODE=3;
//Changes done for LTS Enhancement on 08-12-09
public static final int MILEAGE_CODE=5;
public static final int ROUTESTATUS_CODE=1;
public static final int SUP_DRAFT_DAYS=3;
//changes ends
public static final int ROUTE_STATUS_CODE=3;
public static final int ROUTE_PRIORITY_CODE=3;
public static final int PRIORITY_CODE=1;
public static final String ROUTE_ERRORCODE_CONTINUE="6057";
public static final String ROUTE_EMPTY_DRAFTDAYS="000";
public static final String ROUTE_HOURS="23.00.00";
public static final String ROUTE_Y="Y";
public static final String ROUTE_N="N";
public static final String ROUTE_SEARCH_EXCEPTION_MESSAGE="Problem occurred while performing the operation in route search! Please contact Admin";

/*** ROUTE UPDATE ***/
public static final String NEWROUTE="newRoute";
public static final String ROUTEUPDATE_CONFIRMADD="A";
public static final String ROUTEUPDATE_CONFIRMCHANGE="C";
public static final String ROUTEUPDATE_DELETE="D";
public static final String LTS_ROUTE_UPDATE_STORE_PROC="SV40014(?,?,?,?)";
public static final String LTS_ROUTE_UPDATE_DSN="routeUpdate";
public static final int STATUS_CODE=1;
public static final int TRUCK_MILEAGE=5;
public static final int ROUTEUPDATE_ROUTE_PRIORITY_CODE=1;
public static final int SUPP_DRAFT_DAYS=3;
public static final String ROUTE_UPDATE_EXCEPTION_MESSAGE="Problem occurred while executing transit rates update. Please contact Admin";
/*** ROUTE SEARCH UPDATE ***/
public static final String LTS_ROUTE_SEARCH_UPDATE_STORE_PROC="SV40015(?,?,?,?,?)";
public static final String LTS_ROUTE_SEARCH_UPDATE_DSN="routeSearchUpdate";
public static final String ROUTE_SEARCH_UPDATE_EXCEPTION_MESSAGE="Problem occurred while performing the operation in route search update! Please contact Admin";
public static final String INQUIRY="INQUIRY"; 
public static final String ONE="1";

/*** ERROR MESSAGE CONSTAN********/

public static final int SQLCODE_100=100;
public static final int SQLCODE_911=911;
public static final int SQLCODE_803=803;
public static final int SQLCODE_532=532;
public static final int SQLCODE_530=530;

public static final String ERROR_MSGNO_8050="8050";
public static final String ERROR_MSGNO_2="2";
public static final String ERROR_MSGNO_9="9";
public static final String ERROR_MSGNO_53="53";
public static final String ERROR_MSGNO_1141="1141";


public static final int MAX_RECORD_COUNT=200;
public static final int REC_COUNT_100= 100;
 
public static String MFDB_SCHEMA_NAME ="";


 static {
    try {
        if (EmdcsRuntimeEnvironment.isDevelopment()) {
            MFDB_SCHEMA_NAME = ApplicationUtil.getDB2MainframeSchemaName();
        }
        if (EmdcsRuntimeEnvironment.isTest()) {
            MFDB_SCHEMA_NAME = ApplicationUtil.getDB2MainframeSchemaName();
        } else if (EmdcsRuntimeEnvironment.isQA()) {
            MFDB_SCHEMA_NAME = ApplicationUtil.getDB2MainframeSchemaName();
        } else if (EmdcsRuntimeEnvironment.isProd()) {
            MFDB_SCHEMA_NAME = ApplicationUtil.getDB2MainframeSchemaName();
        }
    } catch (Throwable t) {

    }
}  

public static final String FULL_BI_LEVEL = "FULL BI-LEVEL";
public static final String FBI = "FBI";
public static final String FULL_TRI_LEVEL= "FULL TRI-LEVEL";
public static final String FTRI = "FTRI";
public static final String VIN_BI_LEVEL = "VIN BI-LEVEL";
public static final String VBI = "VBI";
public static final String VIN_TRI_LEVEL= "VIN TRI-LEVEL";
public static final String VTRI = "VTRI";
public static final String FULL_AUTOMAX= "FULL AUTOMAX";
public static final String FAUTO = "FAUTO";
public static final String FULL_ARTICULATED= "FULL ARTICULATED";
public static final String FARTIC = "FARTIC";
public static final String A_FLAG = "A";
public static final String D_FLAG = "D";
public static final String YES = "YES";
public static final String NO = "NO";
public static final String PAGE_COUNT = "PAGE_COUNT";
public static final String PREVIOUS = "PREVIOUS";
public static final String STR_ONE = "1";

public static final String STR_CARRIER =  "Carrier";
public static final String COL_CARR_CD ="CARR_CD";
public static final String STR_ORIGIN ="Origin";
public static final String COL_ORIGIN_CD ="ORIGIN_CD";
public static final String STR_DESTN ="Destn";
public static final String COL_DESTN_CD ="DESTN_CD";
public static final String STR_PRIORITY ="Priority";
public static final String COL_CARR_PRTY_CD ="CARR_PRTY_CD";
public static final String STR_START_DT ="Start Date";
public static final String COL_EFCTV_DT ="EFCTV_DT";
public static final String STR_END_DT ="End Date";
public static final String COL_END_EFCTV_DT ="END_EFCTV_DT";
public static final String STR_TRANSIT_HR ="Transit Hours";
public static final String COL_TRANSIT_HR_AM ="TRANSIT_HR_AM";
public static final String STR_CURRENCY ="Currency";
public static final String COL_CURRENCY_FL ="CURRENCY_FL";
public static final String COL_FLAT_AM ="FLAT_AM"; 
public static final String COL_PER_MILE_AM ="PER_MILE_AM"; 
public static final String COL_MILEAGE_AM ="MILEAGE_AM";
public static final String COL_TOTAL_RATE_AM ="TOTAL_RATE_AM"; 
public static final String COL_CARR_RAIL_TYPE ="CARR_RAIL_TYPE"; 
public static final String COL_CARR_TYPE ="CARR_TYPE";
public static final String COL_PER_VIN_RATE_AM ="PER_VIN_RATE_AM"; 
public static final String COL_LAST_USERID_CD ="LAST_USERID_CD";
public static final String COL_FIXED_RATE_AM ="FIXED_RATE_AM";

public static final String CURRENCY_USD_DESC = "USD";
public static final String CURRENCY_PESO_DESC = "PESO";
//public static final String CURRENCY_USD_CODE = "D";
public static final String CURRENCY_USD_CODE = "U";
public static final String CURRENCY_PESO_CODE = "P";

public static final String CARR_TYPE_TRUCK ="T";
public static final String CARR_TYPE_RAIL ="R";
public static final String CARR_TYPE_SHIP ="S";

public static final String ON ="ON";
public static final String P_FLAG ="P";

/*** ROUTE AND SEGMENT SEARCH START ***/
public static final String ROUTEANDSEGMENT_SEARCH_STORE_PROC="SV40024(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)";
public static  final String PATTERN_START_CODE="S";
public static  final String PATTERN_CONTAINS_CODE="C";

public static  final String PATTERN_START_NAME="START";
public static  final String PATTERN_CONTAINS_NAME="CONTAINS";
public static  final String COL_ORIGIN_CODE="LOCTN_ORIG_CD";
public static  final String COL_DESTN_CODE="LOCTN_DESTN_CD";
public static  final String COL_RAMP_CODE ="RAIL_HEAD_CD";
public static  final String COL_ROUTE_CODE = "ROUTE_CD";
public static  final String COL_MILEAGE="DSTNC_QT";
public static  final String COL_ROUTE_STATUS="RTE_STATUS_FL";
public static  final String COL_ROUTE_PRIORITY="RTE_PRTY_CD";
public static  final String COL_DRAFT_DAYS ="STD_SHP_DAYS_QT";
public static  final String COL_SUP_DRAFT_DAYS="DRAFT_SUP_DAYS_QT";
public static  final String COL_TOTAL_DRAFT_DAYS="CALC_SUP_DAYS_QT";
public static  final String COL_LAST_UPDT_TM = "LAST_UPDT_TM";
public static  final String COL_CARR_NM = "CARR_NM"; 

public static  final String STR_ORIGIN_CODE="Origin";
public static  final String STR_DESTN_CODE="Destn";
public static  final String STR_RAMP_CODE ="Ramp";
public static  final String STR_ROUTE_CODE = "Route";
public static  final String STR_MILEAGE="Mileage";
public static  final String STR_ROUTE_STATUS="Status";
public static  final String STR_ROUTE_PRIORITY="Priority";
public static  final String STR_DRAFT_DAYS ="Draft Days";
public static  final String STR_SUP_DRAFT_DAYS="Supp Draft Days";
public static  final String STR_TOTAL_DRAFT_DAYS="Total Draft Days";
public static  final String ROUTE_AND_SEGMENT_EXCEL_REPORT_CMD_ID="ROUTE_AND_SEGMENT_EXCEL_REPORT";
public static final String ROUTE_NEW_ACTION_CODE="N";
public static final String ROUTE_COPY_ACTION_CODE="C";
public static final String ROUTE_EDIT_ACTION_CODE="E";
public static final String ROUTE_DELETE_ACTION_CODE="D";
public static final String ROUTE_SEGMENT_DETIALS_ACTION_CODE="S";
public static final String ROUTE_CARRIER_TRANSIT_ACTION_CODE="T";
public static final String ROUTE_CARRIER_VALIDATION_ACTION_CODE="V";

public static final String ROUTE_AND_SEGMENT_POPUP_CMD_ID="ROUTE_AND_SEGMENT_POPUP";
public static final String ROUTE_AND_SEGMENT_UPDATE_CMD_ID="ROUTE_AND_SEGMENT_UPDATE";
public static final String FORWARD_NEW_ROUTE_SEGMENT ="newRouteAndSegment";
public static final String FORWARD_POPUP ="popUp";

public static final String INQUIRY_ROUTE_AND_SEGMENT_COMMAND ="INQUIRY_COMMAND";
public static final String NEW_ROUTE_AND_SEGMENT_COMMAND ="NEW_COMMAND";
public static final String UPDATE_ROUTE_AND_SEGMENT_COMMAND ="UPDATE_COMMAND";
public static final String COPY_ROUTE_AND_SEGMENT_COMMAND ="COPY_COMMAND";
public static final String DELETE_ROUTE_AND_SEGMENT_COMMAND ="COPY_COMMAND";

public static final String ACTION_NEW ="NEW";
public static final String ACTION_UPDATE ="UPDATE";
public static final String ACTION_SAVE ="SAVE";
public static final String ACTION_DELETE ="DELETE";
public static final String ACTION_COPY ="COPY";

public static final String ROUTEANDSEGMENT_UPDATE_STORE_PROC="SV40025(?,?,?,?,?,?,?,?,?,?,?,?,?,?)";
public static final int ORIGIN_CODE_LENGTH=5;
public static final int DESTN_CODE_LENGTH=5;
public static final int PRIORITY_CODE_LENGTH=1;
public static final int ROUTE_TYPE_LENGTH=1;
public static final int CARRIER_POS_LENGTH=1;
public static final int START_DATE_LENGTH=10;
public static final int END_DATE_LENGTH=10;
public static final int CARRIER_CODE_LENGTH=5;
public static final int MILEAGE_LENGTH=12;
public static final int TRANSIT_HRS_LENGTH=5;
public static final String ERR_ROUTE_ALREADY_EXISTS = "Route Already Exists";
public static final String ERR_NO_RAIL_HEAD_EXISTS = "No Rail Head exists";
public static final String ERR_REC_EXISTS_WITH_SAME_PRIORITY = "Record already exists with same priority";
public static final String FLAG_Y = "Y";
public static final String FLAG_N = "N";
public static final String FLAG_R = "R";

public static final int LENGTH_100 = 100;
public static final int LENGTH_10 = 10;
public static final String VALID_ROUTE = "VALID ROUTE CODE";
public static final String ROUTE_REMOVED_SUCCESSFULLY = "SUCCESSFULLY REMOVED";
public static final String ROUTE_CREATED_SUCCESSFULLY = "SUCCESSFULLY APPLIED";
public static final String ROUTE_ALREADY_EXIST = "ROUTE ALREADY EXISTS";
public static final String ROUTE_CD_ALREADY_EXIST = "ROUTE CD ALREADY EXISTS";


public static final String ROUTE_AND_UPDATE_EXCEPTION_MESSAGE="Problem occurred while executing route and segment update. Please contact Admin";
public static final String ROUTE_ACTION_FAILURE_PAGE="failure";

public static final String XLSX_FILE_XTN = ".xlsx";
public static final String XLS_FILE_XTN = ".xls";
public static final String CMD_VALIDATE = "validate";
public static final String CMD_INSERT = "insert";
public static final String ROUTE_VALIDATE_STORE_PROC="SV40026(?,?,?,?,?,?,?,?)";
public static final String ROUTE_MASSUPDATE_STORE_PROC="SV40027(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)";


public static  final String ROUTE_AND_SEGMENT_DOWNLOADEXCEL_TEMPLATE_CMD_ID="ROUTE_AND_SEGMENT_DOWNLOADEXCEL_TEMPLATE";

public static  final String ADD_NEW_ROUTE_AND_SEGMENT_CMD_ID="ADD_NEW_ROUTE_AND_SEGMENT";
public static  final String TRANSIT_INQUIRY_CMD_ID="TRANSIT_INQUIRY";
public static  final String TRANSIT_SELECT_CMD_ID="TRANSIT_SELECT";
public static  final String TRANSIT_DELETE_CMD_ID="TRANSIT_DELETE";
public static  final String DELETE_ROUTE_AND_SEGMENT_CMD_ID="DELETE_ROUTE_AND_SEGMENT";
public static  final String CANCEL_ROUTE_AND_SEGMENT_CMD_ID="CANCEL_ROUTE_AND_SEGMENT";
public static  final String CONFIRM_ROUTE_AND_SEGMENT_CMD_ID="CONFIRM_ROUTE_AND_SEGMENT";
public static  final String SAVE_ROUTE_AND_SEGMENT_CMD_ID="SAVE_ROUTE_AND_SEGMENT";
public static  final String COPY_ROUTE_AND_SEGMENT_CMD_ID="COPY_ROUTE_AND_SEGMENT";
public static  final String EDIT_ROUTE_AND_SEGMENT_CMD_ID="EDIT_ROUTE_AND_SEGMENT";
public static  final String DOWNLOAD_DEALER_EXCEL_CMD_ID="DOWNLOAD_DEALER_EXCEL";
public static  final String CREATE_ROUTES_CMD_ID="CREATE_ROUTES";
public static  final String DELETE_ROUTES_CMD_ID="DELETE_ROUTES";
public static  final String FLAG_V = "V";
public static  final String FLAG_A = "A";
public static  final String COL_EXIST_FL = "EXIST_FL";
public static  final String COL_LOCTN_CD = "LOCTN_CD";
public static  final String COL_ACTIVE_FL = "ACTIVE_FL"; 
public static  final String INACTIVE_DEALER = "Inactive Dealer";
public static  final String TRANSIT_NOT_EXISTS = "Transit Does Not Exist";
public static  final String INVALID_CARRIER_CODE = "invalid Carrier code";
public static  final String INVALID_DEALER = "Invalid Dealer";
public static  final String TRANSIT_EXISTS = "Carrier Transit already exists";
public static  final String ERROR_CODE_E1 = "E1";
public static  final String ERROR_CODE_E2 = "E2";
public static  final String ERROR_CODE_E3 = "E3";

public static final String SUCCESSCODE_S02 = "S02";

public static  final String ERROR_CODE_E01 = "E01";
public static  final String ERROR_CODE_E02 = "E02";
public static  final String ERROR_CODE_S01 = "S01";
public static final String SLASH = "/";
public static final String CNST_ZERO = "0";
public static final String HYPEN = "-";
public static final String SHOW_UPLOAD = "SHOW";
public static final String NOT_SHOW_UPLOAD = "NOT_SHOW";
public static final String COUNT = "COUNT";
public static final String MASS_UPDATE = "MASS_UPDATE";
public static final String UPDATE_FLAG = "U";

public static  final String ROUTE_CREATED = "Route(s) Created Successfully";
public static  final String ERR_ROUTE_CREATE = "Error occured while creating Route";
public static  final String ERR_UPLOAD_MSG = "Maximum 100 records can be uploaded";
public static  final String DOWNLOAD_EXCEL_TEMPLATE="downLoadExcelTemplate";

public static  final String DOWNLOAD_DEALER_EXCEL="downLoadDealerExcel";

public static final String ROUTE_AND_SEGMENT_DOWNLOADEXCEL_FILENAME="downLoadExcelTemplate.xls";

public static final String DOWNLOAD_DEALER_EXCEL_FILENAME="downLoadDealerExcel.xls";
/*** ROUTE AND SEGMENT SEARCH END ***/

public static final String HDR_DEALER_CODE = "Dealer Code";
public static final String HDR_CARRIER = "Carrier";
public static final String HDR_PRIORITY = "Priority";
public static final String HDR_START_DATE = "Start Date";
public static final String HDR_END_DATE = "End Date";
public static final String HDR_TRANSIT_HOURS = "Transit Hours";
public static final String HDR_FLAT_RATE = "Flat Rate";
public static final String HDR_PER_MILE_RATE = "Per Mile Rate";
public static final String HDR_MILEAGE = "Mileage";
public static final String HDR_STATUS = "Status";

public static final String STR_NOT_AVAILABLE = "NOT AVAILABLE";
public static final String ERR_ROUTE_EXISTS_MSG = "Routes are already exists for these dealers";
public static final String ROUTE_ALREADY_EXISTS = "Similar Route with same Origin, Destination & Priority exist. Consider a new Priority.";
public static final String ERR_ROUTE_CD_EXISTS = "Similar Route with same Origin, Destination and Segments exists.";
public static final String INVALID_ORIGIN = "Invalid Origin";


public static final String ACTIONCODE_SUBMITJOB = "SUBMIT JOB";
public static final String ACTIONCODE_SEARCH = "SEARCH";
public static final String ACTIONCODE_UPDATE = "UPDATE";
public static final String ACTIONCODE_ADD = "ADD";
public static final String ACTIONCODE_DELETE = "DELETE";
public static final String ACTIONCODE_RESET = "RESET";
public static final String ACTIONCODE_COUNTRYSEARCH = "SELECTCOUNTRY";
public static final String ACTIONCODE_GENERATEEXCEL = "EXCEL_DOWNLOAD";
public static final String ACTIONCODE_MAILING_COUNTRYSEARCH = "SELECTMAILINGCOUNTRY";
public static final String ACTIONCODE_SHIPPING_COUNTRYSEARCH = "SELECTSHIPPINGCOUNTRY";


public static final String TransportationSetup = "TransportationSetup";
public static final String VDS = "VDS";
public static final String SP_PACKINGLIST = "vds.sp.packinglistrequest";
public static final String SP_LOCATIONDETAILS = "vds.sp.locationdetails";
public static final String ERRORCODE_E100 = "E100";
public static final String DB_LOCATION_NAME = "LOCATION_NAME";
public static final String DB_LOCATION_CODE = "LOCATION_CODE";
public static final String DB_COUNTRY_CODE = "COUNTRY_CODE";
public static final String DB_REGION_CODE = "REGION_CODE";
public static final String DB_STATE_NAME = "STATE_NAME";
public static final String DB_ZIP_CODE = "ZIP_CODE";
public static final String DB_CITY_NAME = "CITY_NAME";
public static final String DB_STATUS_CODE = "STATUS_CODE";
public static final String DB_TYPE_NAME = "TYPE_NAME";

//Location Setup VIEW FUNCTIONALITIES

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

// LOCATION SCREEN SEARCH FUNCTIONALITIES

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
public static final String DB_ADDR_TYPE_NM="ADDR_TYPE_NM";
public static final String DB_STATUS_DESC="STATUS_DESC";
public static final String DB_STATUS_CD="STATUS_CD";
public static final String DB_CDT_VALUE_CD="CDT_VALUE_CD";
public static final String DB_CDT_VALUE_TX="CDT_VALUE_TX";
public static final String DB_RGN_CD="RGN_CD";
public static final String DB_LAST_UPDT_TM="LAST_UPDT_TM";  
public static final String DB_LAST_USERID_CD="LAST_USERID_CD";
public static final String DB_STATUS_DT="STATUS_DT";


public static final String SP_ACTIONCODE_VIEW_SEARCH = "I";
public static final String SP_ACTIONCODE_SEARCH = "S";
public static final String SP_ACTIONCODE_ADD = "A";
public static final String SP_ACTIONCODE_DELETE = "R";
public static final String SP_ACTIONCODE_UPDATE = "U";
// Location Search Input Parameter

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

// Adding the Location Details to DB

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
public static final String FORM_ATTRIBUTE_LOCATION_LOCATION_STATUS_DATE="locStatusDate";
public static final String FORM_ATTRIBUTE_LOCATION_LOCATION_CURRENT_DATE="currentDate";
public static final String vds_location_index_view_loading="SV77952"; 


public static final String ATTACHMENT = "attachment";
	public static final String SEMI_COLON = ";";
		public static final String FILENAME = "filename";
			public static final String EQUAL = "=";
				public static final String DOWNLOAD_LOCATION_EXCEL_FILENAME="locationIndexExcel.xls";
					public static final String EXCEL_FILEFORMAT = ".xls";

public static final String LOCATION_PROPERTY_FILE = "com.mazdausa.corporate.vehicles.distribution.persistence.properties.location";
public static final String FILE_LOCATION_PATH = "FILE_LOCATION_PATH";
public static final String LOCATION_INDEX = "LOCATION_INDEX";

public static final String KEY_ENABLED_TYPE1CODE_D80 = "location.d80.enabled.type1codes";
}

