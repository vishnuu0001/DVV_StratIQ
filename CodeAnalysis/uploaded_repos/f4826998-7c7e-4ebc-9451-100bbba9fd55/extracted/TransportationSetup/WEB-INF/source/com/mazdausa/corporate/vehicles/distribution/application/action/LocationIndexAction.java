/**
 * This Action class would retrieve the Location Index page which is called for
 * the first time. This class would also be used to navigate filter class
 * for searching carrier details
 * 
 * 
 * Aug 12, 2006, 3:49:45 PM
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
package com.mazdausa.corporate.vehicles.distribution.application.action;

import java.io.PrintWriter;
import java.sql.SQLException;

import java.util.ArrayList;
import java.util.List;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

import org.apache.log4j.Logger;
import org.apache.poi.hssf.usermodel.HSSFWorkbook;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;

import com.google.gson.Gson;
import com.mazdausa.common.log.EMDCSLogger;
import com.mazdausa.common.util.ApplicationUtil;
import com.mazdausa.corporate.vehicles.distribution.application.constants.AppConstant;
import com.mazdausa.corporate.vehicles.distribution.application.form.LocationIndexForm;
import com.mazdausa.corporate.vehicles.distribution.application.util.CommonUtility;
import com.mazdausa.corporate.vehicles.distribution.application.util.LocationConstants;
import com.mazdausa.corporate.vehicles.distribution.application.util.LocationExcelUtil;
import com.mazdausa.corporate.vehicles.distribution.persistence.dto.LocationIndexDTO;
import com.mazdausa.corporate.vehicles.distribution.services.LocationIndexService;
import com.mazdausa.corporate.vehicles.distribution.services.LocationInformationService;

public class LocationIndexAction extends VDSActionAbstract {

	private static Logger log = EMDCSLogger.getLogger(LocationIndexAction.class);

	private static final String ERROR = "error";
	private static final String CONTENT_TYPE = "json/text;charset=utf-8";
	private static final String CACHE_CONTROL = "cache-control";
	private static final String NO_CACHE = "no-cache";

	public ActionForward executeAction(ActionMapping mapping, ActionForm form, HttpServletRequest request,
			HttpServletResponse response) throws SQLException {

		try {

			String userName = CommonUtility.getUser(request);
			LocationIndexForm objLocationIndexForm = (LocationIndexForm) form;
			LocationIndexService service = new LocationIndexService();
			LocationInformationService infoService = null;
			LocationIndexDTO dto = null;
			String enabledType1codeForD80 = null;
			String type1code = null;
			log.debug("Inside LocationIndexAction");

			CommonUtility common = new CommonUtility();
			common.restrictAccess(request);
			HttpSession httpSession = request.getSession();

			String actionCode = "";
			String streetAddress;
			String streetAddress1;
			String shipCity;
			String shipCountry;
			String shipZip;
			streetAddress = request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_MAILINGSTREET1);
			streetAddress1 = request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_MAILINGSTREET3);
			shipCity = request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_MAILING_CITY2);
			shipCountry = request.getParameter(AppConstant.SHIPPING_COUNTRY);
			String statusCode = request.getParameter(AppConstant.LOCSTATUSCODE);
			shipZip = request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_MAILING_ZIPCD2);
			enabledType1codeForD80 = ApplicationUtil.getSystemProperty(AppConstant.TransportationSetup,
					LocationConstants.KEY_ENABLED_TYPE1CODE_D80);
			// enabledType1codeForD80 = "DL,F0,MC,MH,OT,PC,RG,TC,DD,FC,VS";

			type1code = request.getParameter(AppConstant.OLD_LOCSETUP_TYPE);

			if (!(null == request.getParameter("ACTION"))) {
				actionCode = request.getParameter("ACTION");

			}

			if ((AppConstant.ACTIONCODE_COUNTRYSEARCH).equals(actionCode)) {

				LocationIndexDTO searchCountryDTO = service.getCountrySearchDetails(
						request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_COUNTRY), userName);

				if (!(null == (searchCountryDTO))) {

					objLocationIndexForm.setRegionCodeList((ArrayList) searchCountryDTO.getRegionCodeList());
					objLocationIndexForm.setStateNameList((ArrayList) searchCountryDTO.getStateNameList());
				}

				Gson gson = new Gson();
				String json = gson.toJson(objLocationIndexForm);
				response.setContentType(CONTENT_TYPE);
				response.setHeader(CACHE_CONTROL, NO_CACHE);
				PrintWriter out = response.getWriter();
				out.println(json);
				out.flush();
				return null;
			} else if ((AppConstant.ACTIONCODE_MAILING_COUNTRYSEARCH).equals(actionCode)) {

				if (request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_MAILING_COUNTRY) != null
						&& request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_MAILING_COUNTRY).length() > 0) {

					LocationIndexDTO searchStateDTO = service.getCountrySearchDetails(
							request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_MAILING_COUNTRY), userName);

					if (!(null == (searchStateDTO))) {

						objLocationIndexForm.setStateNameList((ArrayList) searchStateDTO.getStateNameList());
					}
				} else {
					objLocationIndexForm.setStateNameList(new ArrayList<LocationIndexDTO>());
				}

				Gson gson = new Gson();
				String json = gson.toJson(objLocationIndexForm);
				response.setContentType(CONTENT_TYPE);
				response.setHeader(CACHE_CONTROL, NO_CACHE);
				PrintWriter out = response.getWriter();
				out.println(json);
				out.flush();
				return null;
			} else if ((AppConstant.ACTIONCODE_SHIPPING_COUNTRYSEARCH).equals(actionCode)) {

				if (request.getParameter(AppConstant.FORM_ATTRIBUTE_SHIPPING_MAILING_COUNTRY) != null
						&& request.getParameter(AppConstant.FORM_ATTRIBUTE_SHIPPING_MAILING_COUNTRY).length() > 0) {

					LocationIndexDTO searchMailingStateDTO = service.getCountrySearchDetails(
							request.getParameter(AppConstant.FORM_ATTRIBUTE_SHIPPING_MAILING_COUNTRY), userName);

					if (!(null == (searchMailingStateDTO))) {

						objLocationIndexForm.setStateNameList((ArrayList) searchMailingStateDTO.getStateNameList());
					}
				} else {
					objLocationIndexForm.setStateNameList(new ArrayList<LocationIndexDTO>());
				}

				Gson gson = new Gson();
				String json = gson.toJson(objLocationIndexForm);
				response.setContentType(CONTENT_TYPE);
				response.setHeader(CACHE_CONTROL, NO_CACHE);
				PrintWriter out = response.getWriter();
				out.println(json);
				out.flush();
				return null;
			} else if ((AppConstant.ACTIONCODE_GENERATEEXCEL).equals(actionCode)) {

				infoService = new LocationInformationService();

				// LocationIndexDTO
				// generateExcelDTO=infoService.getSearchDetails(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_NAME),request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_CODE).toUpperCase(),request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_COUNTRY),request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_REGION),request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_STATE),request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_ZIPCD),request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_CITY),request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_STATUS),request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_TYPE),userName);
				LocationIndexDTO generateExcelDTO = service.getLocationSearchDetails(
						request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_NAME),
						request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_CODE).toUpperCase(),
						request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_COUNTRY),
						request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_REGION),
						request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_STATE),
						request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_ZIPCD),
						request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_CITY),
						request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_STATUS),
						request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_TYPE), userName);

				if (!(null == (generateExcelDTO.getSearchList()))) {

					HSSFWorkbook workbook = LocationExcelUtil.writeDataToExcel(generateExcelDTO.getSearchList());
					if (workbook != null) {
						response.setContentType("text/xls");
						response.setHeader(AppConstant.CONTENT_DISPOSITION,
								AppConstant.ATTACHMENT + AppConstant.SEMI_COLON + AppConstant.FILENAME
										+ AppConstant.EQUAL + AppConstant.LOCATION_INDEX
										+ AppConstant.EXCEL_FILEFORMAT);
						workbook.write(response.getOutputStream());
						workbook.close();
					}
				}
				return null;
			} else if ((AppConstant.ACTIONCODE_SEARCH).equals(actionCode)) {

				// infoService=new LocationInformationService();

				// LocationIndexDTO
				// searchDTO=infoService.getSearchDetails(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_NAME),request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_CODE).toUpperCase(),request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_COUNTRY),request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_REGION),request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_STATE),request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_ZIPCD),request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_CITY),request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_STATUS),request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_TYPE),userName);

				LocationIndexDTO searchDTO = service.getLocationSearchDetails(
						request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_NAME),
						request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_CODE).toUpperCase(),
						request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_COUNTRY),
						request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_REGION),
						request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_STATE),
						request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_ZIPCD),
						request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_CITY),
						request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_STATUS),
						request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_TYPE), userName);

				if (!(null == (searchDTO.getSearchList()))) {
					objLocationIndexForm.setSearchList((ArrayList<LocationIndexDTO>) searchDTO.getSearchList());
					objLocationIndexForm.setResponseCode("S01");
					objLocationIndexForm.setResponseText("SUCCESSFUL".toLowerCase());
				}

				Gson gson = new Gson();
				String json = gson.toJson(objLocationIndexForm);
				response.setContentType(CONTENT_TYPE);
				response.setHeader(CACHE_CONTROL, NO_CACHE);
				PrintWriter out = response.getWriter();
				out.println(json);
				out.flush();
				return null;
			} else if ((AppConstant.ACTIONCODE_SAVE).equals(objLocationIndexForm.getActionCode())) {

				infoService = new LocationInformationService();

				StringBuilder generatedInputString1 = new StringBuilder();
				StringBuilder generatedInputString2 = new StringBuilder();

				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_CODE), 5)
								.toUpperCase());
				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_NAME), 30));
				generatedInputString1.append(addSpace(request.getParameter(AppConstant.LOCREGIONCODE), 2));
				generatedInputString1.append(addSpace(request.getParameter(AppConstant.LOCTYPENAME), 2));
				generatedInputString1.append(addSpace(request.getParameter(AppConstant.LOCTYPENAME2), 2));
				generatedInputString1.append(addSpace(request.getParameter(AppConstant.LOCTYPENAME3), 2));
				generatedInputString1.append(addSpace(request.getParameter(AppConstant.LOCSTATUSCODE), 1));
				generatedInputString1.append(
						addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_LOCATION_CURRENT_DATE), 10));

				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_NAME), 15));
				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_LASTNAME), 20));
				generatedInputString1.append(addSpace(request.getParameter(AppConstant.LOCATIONSETUPTITLE), 20));
				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_PHONE1), 3));
				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_PHONE2), 3));
				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_PHONE3), 4));
				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_PHONE4), 5));
				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_FAX1), 3));
				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_FAX2), 3));

				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_FAX3), 4));
				generatedInputString1.append(
						addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_MAILINGSTREET), 30));
				generatedInputString1.append(
						addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_MAILINGSTREET2), 30));
				generatedInputString1.append(
						addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_MAILINGSTREET4), 30));
				generatedInputString1.append(
						addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_MAILING_CITY1), 25));
				generatedInputString1.append(addSpace(request.getParameter(AppConstant.MAILSTATENAME), 3));
				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_MAILING_ZIPCD1), 9));
				generatedInputString1.append(addSpace(request.getParameter(AppConstant.SELECTED_COUNTRY1), 2));

				generatedInputString1.append(
						addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_MAILINGSTREET1), 30));
				generatedInputString1.append(
						addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_MAILINGSTREET3), 30));
				generatedInputString1.append(
						addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_MAILINGSTREET5), 30));
				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_MAILING_CITY2), 25));
				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_MAILING_STATE2), 3));
				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_MAILING_ZIPCD2), 9));
				generatedInputString1.append(
						addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_MAILING_COUNTRY2), 2));
				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_MAIL), 30));

				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_CELL1), 3));
				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_CELL2), 3));
				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_CELL3), 4));

				LocationIndexDTO saveCheckDTO = infoService.savelocationDetails(generatedInputString1, userName);

				// ePort Support 2nd Half 2023 - D80 file creation - including only matching
				// type1 codes - update starts here
				/*
				 * NOTE: IF THERE IS ANY ADD/RESTRICT THE TYPE CODES FOR THE D80 FILE TO ICL,
				 * PLEASE REFER AND UPDATE THE PROPERTY FILE IN JAVA FOR THE VDS SCREEN. IT WILL
				 * BE APPLICABLE FOR BOTH ADD AND UPDATES. BELOW TYPE CODES1 ARE ADDED IN THE
				 * JAVA PROPERTY FILE. 'DL','F0','MC','MH','OT','PC','RG','TC','DD','FC','VS'
				 */
				if (!(null == (saveCheckDTO)) && saveCheckDTO.getResponseCode() != null) {
					objLocationIndexForm.setResponseText(saveCheckDTO.getResponse().toLowerCase());
					objLocationIndexForm.setResponseCode(saveCheckDTO.getResponseCode());
					if (saveCheckDTO.getResponse().trim().contains("SUCCESSFULLY ADDED")) {
						if (enabledType1codeForD80 != null && !enabledType1codeForD80.isEmpty() && type1code != null
								&& enabledType1codeForD80.contains(type1code.trim())) {
							if (statusCode.equalsIgnoreCase(AppConstant.STATUSA)) {
								log.info("Creating D80 file starts");

								generatedInputString2.append(
										addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_CODE),
												5).toUpperCase());

								generatedInputString2.append(
										addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_NAME),
												30).toUpperCase());

								generatedInputString2
										.append(addSpace(request.getParameter(AppConstant.LOCTYPENAME), 2));

								generatedInputString2
										.append(addSpace(request.getParameter(AppConstant.LOCREGIONCODE), 2)
												.replace("GU", "SO"));

								generatedInputString2
										.append(addSpace(request.getParameter(AppConstant.FORM_districtCode), 2));

								if (streetAddress.isEmpty() && streetAddress1.isEmpty() && shipCity.isEmpty()
										&& shipCountry.equals(AppConstant.EMPTYCOUNTRY) && shipZip.isEmpty()) {
									generatedInputString2
											.append(addSpace(
													request.getParameter(
															AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_MAILINGSTREET),
													30).toUpperCase());

									generatedInputString2
											.append(addSpace(
													request.getParameter(
															AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_MAILING_CITY1),
													25).toUpperCase());

									generatedInputString2
											.append(addSpace(request.getParameter(AppConstant.MAILSTATENAME), 2));

									generatedInputString2.append(addSpaceAfter(
											request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_MAILING_ZIPCD1),
											9));

									generatedInputString2.append(rightAddSpaces(
											getSplitCountryName(request.getParameter(AppConstant.SELECTED_COUNTRY)),
											25));

								} else {
									generatedInputString2
											.append(addSpace(
													request.getParameter(
															AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_MAILINGSTREET1),
													30).toUpperCase());
									generatedInputString2.append(addSpace(
											request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_MAILING_CITY2), 25)
													.toUpperCase());
									generatedInputString2.append(addSpace(
											request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_MAILING_STATE2),
											2));

									generatedInputString2.append(addSpaceAfter(
											request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_MAILING_ZIPCD2),
											9));
									if (AppConstant.EMPTYCOUNTRY.equals(shipCountry)) {
										generatedInputString2
												.append(rightAddSpaces(request.getParameter(AppConstant.BLANK), 25));
									} else {
										generatedInputString2.append(addSpace(
												getSplitCountryName(request.getParameter(AppConstant.SHIPPING_COUNTRY)),
												25));
									}
								}

								generatedInputString2.append(addSpace(
										request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_PHONE1), 3));

								generatedInputString2.append(addSpace(
										request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_PHONE2), 3));

								generatedInputString2.append(addSpace(
										request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_PHONE3), 4));

								if (streetAddress.isEmpty() && streetAddress1.isEmpty() && shipCity.isEmpty()
										&& shipCountry.equals(AppConstant.EMPTYCOUNTRY) && shipZip.isEmpty()) {
									generatedInputString2
											.append(addSpace(
													request.getParameter(
															AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_MAILINGSTREET2),
													30).toUpperCase());

								} else {
									generatedInputString2
											.append(addSpace(
													request.getParameter(
															AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_MAILINGSTREET3),
													30).toUpperCase());

								}
								generatedInputString2.append(addSpace(AppConstant.BLANK, 28));
								LocationExcelUtil.writedataCSV(generatedInputString2,
										saveCheckDTO.getResponseSeqNumber());

								log.info("D80 file created successfully");

							}
						} else {
							log.info("Location Update -> No need to create D80 file for this Location type code "
									+ type1code);
						}

					} else {
						log.info("Location Creation Failed ");
					}
				}
				// ePort Support 2nd Half 2023 - D80 file creation - including only matching
				// type1 codes - update ends here

				Gson gson = new Gson();
				String json = gson.toJson(objLocationIndexForm);
				response.setContentType(CONTENT_TYPE);
				response.setHeader(CACHE_CONTROL, NO_CACHE);
				PrintWriter out = response.getWriter();
				out.println(json);
				out.flush();
				return null;
			} else if ((AppConstant.ACTIONCODE_UPDATE).equals(objLocationIndexForm.getActionCode())) {

				infoService = new LocationInformationService();
				StringBuilder generatedInputString1 = new StringBuilder();
				StringBuilder generatedInputString2 = new StringBuilder();

				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.LATESTLOC_CODE), 5).toUpperCase());
				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_NAME), 30));
				generatedInputString1.append(addSpace(request.getParameter(AppConstant.LOCREGIONCODE), 2));
				generatedInputString1.append(addSpace(request.getParameter(AppConstant.LOCTYPENAME), 2));
				generatedInputString1.append(addSpace(request.getParameter(AppConstant.LOCTYPENAME2), 2));
				generatedInputString1.append(addSpace(request.getParameter(AppConstant.LOCTYPENAME3), 2));
				generatedInputString1.append(addSpace(request.getParameter(AppConstant.LOCSTATUSCODE), 1));
				generatedInputString1.append(addSpace(request.getParameter(AppConstant.LOC_DATE), 10));

				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_NAME), 15));
				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_LASTNAME), 20));
				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_TITLE), 20));
				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_PHONE1), 3));
				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_PHONE2), 3));
				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_PHONE3), 4));
				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_PHONE4), 5));
				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_FAX1), 3));
				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_FAX2), 3));

				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_FAX3), 4));
				generatedInputString1.append(
						addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_MAILINGSTREET), 30));
				generatedInputString1.append(
						addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_MAILINGSTREET2), 30));
				generatedInputString1.append(
						addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_MAILINGSTREET4), 30));
				generatedInputString1.append(
						addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_MAILING_CITY1), 25));
				generatedInputString1.append(addSpace(request.getParameter(AppConstant.MAILSTATENAME), 3));
				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_MAILING_ZIPCD1), 9));
				generatedInputString1.append(addSpace(request.getParameter(AppConstant.SELECTED_COUNTRY1), 2));

				generatedInputString1.append(
						addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_MAILINGSTREET1), 30));
				generatedInputString1.append(
						addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_MAILINGSTREET3), 30));
				generatedInputString1.append(
						addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_MAILINGSTREET5), 30));
				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_MAILING_CITY2), 25));
				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_MAILING_STATE2), 3));
				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_MAILING_ZIPCD2), 9));
				generatedInputString1.append(
						addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_MAILING_COUNTRY2), 2));

				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_EMAIL), 30));

				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_CELL1), 3));
				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_CELL2), 3));
				generatedInputString1
						.append(addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_CELL3), 4));

				LocationIndexDTO updateDTO = infoService.updatelocationDetails(generatedInputString1, userName);

				// ePort Support 2nd Half 2023 - D80 file creation - including only matching
				// type1 codes - update starts here
				if (!(null == (updateDTO)) && updateDTO.getResponseCode() != null) {
					objLocationIndexForm.setResponseText(updateDTO.getResponse().toLowerCase());
					objLocationIndexForm.setResponseCode(updateDTO.getResponseCode());
					if (updateDTO.getResponse().trim().contains("SUCCESSFULLY UPDATED")) {

						if (enabledType1codeForD80 != null && !enabledType1codeForD80.isEmpty() && type1code != null
								&& enabledType1codeForD80.contains(type1code.trim())) {
							if (AppConstant.STATUSA.equalsIgnoreCase(statusCode)) {
								log.info("Creating D80 file starts");
								generatedInputString2.append(
										addSpace(request.getParameter(AppConstant.LATESTLOC_CODE), 5).toUpperCase());

								generatedInputString2.append(
										addSpace(request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_NAME),
												30).toUpperCase());

								generatedInputString2
										.append(addSpace(request.getParameter(AppConstant.LOCTYPENAME), 2));

								generatedInputString2
										.append(addSpace(request.getParameter(AppConstant.LOCREGIONCODE), 2)
												.replace("GU", "SO"));

								generatedInputString2
										.append(addSpace(request.getParameter(AppConstant.FORM_districtCode), 2));

								if (streetAddress.isEmpty() && streetAddress1.isEmpty() && shipCity.isEmpty()
										&& shipCountry.equals(AppConstant.EMPTYCOUNTRY) && shipZip.isEmpty()) {
									generatedInputString2
											.append(addSpace(
													request.getParameter(
															AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_MAILINGSTREET),
													30).toUpperCase());

									generatedInputString2
											.append(addSpace(
													request.getParameter(
															AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_MAILING_CITY1),
													25).toUpperCase());

									generatedInputString2
											.append(addSpace(request.getParameter(AppConstant.MAILSTATENAME), 2));

									generatedInputString2.append(addSpaceAfter(
											request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_MAILING_ZIPCD1),
											9));

									generatedInputString2.append(rightAddSpaces(
											getSplitCountryName(request.getParameter(AppConstant.SELECTED_COUNTRY)),
											25));

								} else {
									generatedInputString2
											.append(addSpace(
													request.getParameter(
															AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_MAILINGSTREET1),
													30).toUpperCase());
									generatedInputString2.append(addSpace(
											request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_MAILING_CITY2), 25)
													.toUpperCase());
									generatedInputString2.append(addSpace(
											request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_MAILING_STATE2),
											2));
									generatedInputString2.append(addSpaceAfter(
											request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_MAILING_ZIPCD2),
											9));
									if (AppConstant.EMPTYCOUNTRY.equals(shipCountry)) {
										generatedInputString2
												.append(rightAddSpaces(request.getParameter(AppConstant.BLANK), 25));
									} else {
										generatedInputString2.append(addSpace(
												getSplitCountryName(request.getParameter(AppConstant.SHIPPING_COUNTRY)),
												25));
									}

								}

								generatedInputString2.append(addSpace(
										request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_PHONE1), 3));

								generatedInputString2.append(addSpace(
										request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_PHONE2), 3));

								generatedInputString2.append(addSpace(
										request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_PHONE3), 4));

								if (streetAddress.isEmpty() && streetAddress1.isEmpty() && shipCity.isEmpty()
										&& shipCountry.equals(AppConstant.EMPTYCOUNTRY) && shipZip.isEmpty()) {
									generatedInputString2
											.append(addSpace(
													request.getParameter(
															AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_MAILINGSTREET2),
													30).toUpperCase());

								} else {
									generatedInputString2
											.append(addSpace(
													request.getParameter(
															AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_MAILINGSTREET3),
													30).toUpperCase());

								}
								generatedInputString2.append(addSpace(AppConstant.BLANK, 28));

								LocationExcelUtil.writedataCSV(generatedInputString2, updateDTO.getResponseSeqNumber());
								log.info("D80 file created successfully");

							}
						} else {
							log.info("Location Update -> No need to create D80 file for this Location type code "
									+ type1code);
						}

					} else {
						log.info("Location Update Failed");
					}
				}
				// ePort Support 2nd Half 2023 - D80 file creation - including only matching
				// type1 codes - update ends here

				Gson gson = new Gson();
				String json = gson.toJson(objLocationIndexForm);
				response.setContentType(CONTENT_TYPE);
				response.setHeader(CACHE_CONTROL, NO_CACHE);
				PrintWriter out = response.getWriter();
				out.println(json);
				out.flush();
				return null;
			} else if (actionCode.equals(AppConstant.ACTIONCODE_DELETE)) {

				infoService = new LocationInformationService();

				LocationIndexDTO deleteDTO = infoService.deletelocationDetails(
						request.getParameter(AppConstant.FORM_ATTRIBUTE_LOCATION_SETUP_CODE).toUpperCase(), userName);

				if (!(null == (deleteDTO))) {

					objLocationIndexForm.setResponseText(deleteDTO.getResponse().toLowerCase());
					objLocationIndexForm.setResponseCode(deleteDTO.getResponseCode());
				}

				Gson gson = new Gson();
				String json = gson.toJson(objLocationIndexForm);
				response.setContentType(CONTENT_TYPE);
				response.setHeader(CACHE_CONTROL, NO_CACHE);
				PrintWriter out = response.getWriter();
				out.println(json);
				out.flush();
				return null;

			} else {

				dto = service.getLocationDetails(userName);

				if (("SUCCESS").equals(dto.getResponseCode())) {
					setResponseData(objLocationIndexForm, dto.getCountryCodeList(), dto.getRegionCodeList(),
							dto.getStateNameList(), dto.getTypeName(), dto.getStatusCode(), dto.getResponseCode(),
							dto.getResponse(), "false");
				} else {

					setResponseData(objLocationIndexForm, dto.getCountryCodeList(), dto.getRegionCodeList(),
							dto.getStateNameList(), dto.getTypeName(), dto.getStatusCode(), dto.getResponseCode(),
							dto.getResponse(), "true");
				}
				return mapping.findForward(AppConstant.LOCATION_INDEX_SPAGE);

			}

		} catch (Exception e) {

			log.error("error in LocationIndexAction:: " + e.getMessage());

			return mapping.findForward(ERROR);
		}

	}

	private void setResponseData(LocationIndexForm objLocationIndexForm, List countryCode, List regionCode,
			List stateName, List typeName, List statusCode, String responseCode, String responseText,
			String locationCodeVisible) {

		objLocationIndexForm.setCountryList((ArrayList) countryCode);
		objLocationIndexForm.setRegionCodeList((ArrayList) regionCode);
		objLocationIndexForm.setStateNameList((ArrayList) stateName);
		objLocationIndexForm.setTypeNameList((ArrayList) typeName);
		objLocationIndexForm.setStatusCodeList((ArrayList) statusCode);
		objLocationIndexForm.setResponseCode(responseCode);
		objLocationIndexForm.setResponseText(responseText.toLowerCase());
		objLocationIndexForm.setLocationCodeVisible(locationCodeVisible);

	}

	public static String addSpace(String variable, int maxSize) {
		StringBuilder strBuff = new StringBuilder();
		int len = 0;
		String varTrim = variable.trim();
		if (varTrim != null) {
			len = varTrim.length();
			strBuff.append(varTrim);
		}
		for (int i = len; i < maxSize; i++) {
			strBuff.append(" ");
		}
		return strBuff.toString();
	}

	public static String rightAddSpaces(String variable, int maxSize) {
		StringBuilder strBuff = new StringBuilder();
		int len = 0;
		if (variable != null) {
			len = variable.length();
			if (len > maxSize) {
				strBuff.append(variable.substring(0, maxSize));
			} else {
				strBuff.append(variable);

			}
		}
		String tempStr = "";
		for (int i = len; i < maxSize; i++) {

			tempStr += " ";

		}
		return strBuff.toString() + tempStr;
	}

	public static String addSpaceBefore(String variable, int maxSize) {
		String strBuff = new String();
		int len = 0;
		String varTrim = variable.trim();
		if (varTrim != null) {
			len = varTrim.length();
			strBuff = (varTrim);
		}
		for (int i = len; i < maxSize; i++) {
			strBuff = " " + strBuff;
			;
		}
		return strBuff.toString();
	}

	public static String addSpaceAfter(String variable, int maxSize) {
		String strBuff = new String();
		int len = 0;
		String varTrim = variable.trim();
		if (varTrim != null) {
			len = varTrim.length();
			strBuff = (varTrim);
		}
		for (int i = len; i < maxSize; i++) {
			strBuff = strBuff + " ";
			;
		}
		return strBuff.toString();
	}

	public String getSplitCountryName(String countryCode) {

		if (countryCode != null && countryCode.length() > 0) {
			String[] tokens = countryCode.split("-");
			if (tokens.length > 1) {
				return tokens[1].trim();
			}
		}
		return countryCode;

	}

	public String getSplitCountryCode(String countryCode) {

		if (countryCode != null && countryCode.length() > 0) {
			String[] tokens = countryCode.split("-");
			if (tokens.length > 1) {
				return tokens[0].trim();
			}
		}
		return countryCode;

	}
}
