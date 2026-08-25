/**
 * This is the CarrierSetupAction.java
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
package com.mazdausa.corporate.vehicles.distribution.application.action;

import java.io.PrintWriter;
import java.util.ArrayList;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

import org.apache.log4j.Logger;
import org.apache.poi.hssf.usermodel.HSSFWorkbook;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;

import com.google.gson.Gson;
import com.mazdausa.common.application.actions.UserContext;
import com.mazdausa.common.application.actions.UserContextException;
import com.mazdausa.common.log.EMDCSLogger;
import com.mazdausa.common.user.model.User;
import com.mazdausa.corporate.vehicles.distribution.application.constants.AppConstant;
import com.mazdausa.corporate.vehicles.distribution.application.form.CarrierSetupForm;
import com.mazdausa.corporate.vehicles.distribution.application.util.CommonUtility;
import com.mazdausa.corporate.vehicles.distribution.application.util.LocationExcelUtil;
import com.mazdausa.corporate.vehicles.distribution.persistence.dto.CarrierSetupDTO;
import com.mazdausa.corporate.vehicles.distribution.persistence.dto.LocationIndexDTO;
import com.mazdausa.corporate.vehicles.distribution.services.CarrierSetupService;
import com.mazdausa.corporate.vehicles.distribution.services.LocationIndexService;

/**
 * @author TechM
 * 
 */
public class CarrierSetupAction extends VDSActionAbstract {

	private static Logger log = EMDCSLogger.getLogger(CarrierSetupAction.class);

	@Override
	protected ActionForward executeAction(ActionMapping mapping,
			ActionForm form, HttpServletRequest req, HttpServletResponse response)
			throws Exception {
		log.debug("CarrierSetupAction-executeAction starts here");
		CarrierSetupService carrierSetupService=null;
		CarrierSetupDTO carrierSetupDTO=null;
		LocationIndexService service = new LocationIndexService();
		LocationIndexDTO dto = null;
		try {
			carrierSetupService=new CarrierSetupService();
			carrierSetupDTO=carrierSetupService.getDropdownValues();
			CarrierSetupForm  carrierSetupForm=(CarrierSetupForm)form;
			carrierSetupForm=this.setValuesFromRequest(carrierSetupForm,req);
			
			
			CommonUtility common=new CommonUtility();
			common.restrictAccess(req);
			HttpSession httpSession = req.getSession();
			
			
			if(null ==carrierSetupForm.getAction() || null!=carrierSetupForm.getAction() && AppConstant.ACTION_CD_D.equalsIgnoreCase(carrierSetupForm.getAction() )){
				carrierSetupDTO=carrierSetupService.getDropdownValues();
				carrierSetupForm.setStatusList(carrierSetupDTO.getStatusList());
				carrierSetupForm.setTypeList(carrierSetupDTO.getTypeList());
				carrierSetupForm.setCurrencyList(carrierSetupDTO.getCurrencyList());
				carrierSetupForm.setDetailedTypeList(carrierSetupDTO.getDetailedCarrierTypeList());
				carrierSetupForm.setDetailedCurrencyList(carrierSetupDTO.getDetailedCurrencyList());
				
				dto=service.getLocationDetails(" ");
				carrierSetupForm.setCountryList(dto.getCountryCodeList());
				carrierSetupForm.setStateList(dto.getStateNameList());
				
			}else if(null!=carrierSetupForm.getAction() && AppConstant.ACTION_CD_C.equalsIgnoreCase(carrierSetupForm.getAction())){
				if(req.getParameter("countryCd")!=null && !req.getParameter("countryCd").equals(""))  { 
					dto=service.getCountrySearchDetails(req.getParameter("countryCd"),carrierSetupForm.getUserId());
				}else{
					dto=service.getLocationDetails(" ");
					
				}
				
				if(!(null==(dto))){
					   
					   carrierSetupForm.setStateList((ArrayList) dto.getStateNameList());
					}
				   

				   Gson gson = new Gson();
					String json = gson.toJson(carrierSetupForm);
					response.setContentType("json/text;charset=utf-8");
					response.setHeader("cache-control", "no-cache");
					PrintWriter out = response.getWriter();
					out.println(json);
					out.flush();
				   return null;


			}else if(null!=carrierSetupForm.getAction() && AppConstant.ACTION_CD_E.equalsIgnoreCase(carrierSetupForm.getAction())){	
				carrierSetupForm.setAction("S");
				carrierSetupForm.setCarrierName(req.getParameter("searchCarrierName")!=null ? req.getParameter("searchCarrierName"):"");
				carrierSetupForm.setCarrierCd(req.getParameter("searchCarrierCode") !=null ? req.getParameter("searchCarrierCode"):"");
				carrierSetupForm.setStatus(req.getParameter("searchStatusCd")!=null ? req.getParameter("searchStatusCd"):"" );
				carrierSetupForm.setCarrierType(req.getParameter("searchTypeCd") !=null ? req.getParameter("searchTypeCd"):"");
				carrierSetupForm.setCurrencyCd(req.getParameter("searchCurrencyCd") !=null ? req.getParameter("searchCurrencyCd"):"");
				
				 
				 
				 
				carrierSetupDTO=carrierSetupService.searchCarrierList(carrierSetupForm);
				HSSFWorkbook workbook=LocationExcelUtil.carrierDetailsToExcel(carrierSetupDTO.getSearchList());
				 if (workbook != null) {
					 	response.setContentType("text/xls");
						response.setHeader(AppConstant.CONTENT_DISPOSITION, AppConstant.ATTACHMENT+AppConstant.SEMI_COLON+AppConstant.FILENAME+AppConstant.EQUAL+ AppConstant.CARRIER_EXCEL+AppConstant.EXCEL_FILEFORMAT);
						workbook.write(response.getOutputStream());  
						
						workbook.close();
		            }
				 return null;
			}else {
				
				carrierSetupDTO=carrierSetupService.searchCarrierList(carrierSetupForm);
				Gson gson = new Gson();
				String json = gson.toJson(carrierSetupDTO);
				response.setContentType("json/text;charset=utf-8");
				response.setHeader("cache-control", "no-cache");
				PrintWriter out = response.getWriter();
				out.println(json);
				out.flush();
				return null;
				
				
			}	
			
			
			log.debug("CarrierSetupAction-executeAction ends here");
			return mapping.findForward(AppConstant.SUCCESS);
		} catch (Exception e) {
			log.error("CarrierSetupAction-executeAction error" + e);
			return mapping.findForward(AppConstant.ERROR);
		}
	}
	
	private CarrierSetupForm setValuesFromRequest(CarrierSetupForm carrierSetupForm,HttpServletRequest req) throws UserContextException{
		
		carrierSetupForm.setAction(req.getParameter("action"));
		carrierSetupForm.setCarrierName(req.getParameter("carrierName"));
		carrierSetupForm.setCarrierCd(req.getParameter("carrierCd"));
		carrierSetupForm.setCarrierType(req.getParameter("carrierType"));
		carrierSetupForm.setCurrencyCd(req.getParameter("currencyCd"));
		carrierSetupForm.setStatus(req.getParameter("status"));
		carrierSetupForm.setStatusDt(req.getParameter("statusDate"));
		
		
		carrierSetupForm.setReturnErrorDataYes(req.getParameter("receivingErrorData"));
		carrierSetupForm.setDeliveryDataYes(req.getParameter("receivingDeliveryDate"));
		carrierSetupForm.setContractFirstName(req.getParameter("firstName"));
		carrierSetupForm.setContractLastName(req.getParameter("lastName"));
		carrierSetupForm.setContactEmail(req.getParameter("email"));
		carrierSetupForm.setContractTitleTx(req.getParameter("titleName"));
		
		carrierSetupForm.setPhoneAcNo(req.getParameter("phoneAcNo"));
		carrierSetupForm.setPhoneExcNo(req.getParameter("phoneExcNo"));
		carrierSetupForm.setPhoneNo(req.getParameter("phoneNo"));
		carrierSetupForm.setExtnsnNo(req.getParameter("phoneExtensnNo"));
		carrierSetupForm.setFaxAcNo(req.getParameter("faxAcNo"));
		carrierSetupForm.setFaxExcNo(req.getParameter("faxExcNo"));
		carrierSetupForm.setFaxphnNo(req.getParameter("faxNo"));
		carrierSetupForm.setClPhoneAcNo(req.getParameter("cellAcNo"));
		carrierSetupForm.setClPhoneExcNo(req.getParameter("cellExcNo"));
		carrierSetupForm.setClPhoneNo(req.getParameter("cellNo"));
		
		
		carrierSetupForm.setMailingStreet1Address(req.getParameter("mailingAddr1"));
		carrierSetupForm.setMailingStreet2Address(req.getParameter("mailingAddr2"));
		carrierSetupForm.setMailingStreet3Address(req.getParameter("mailingAddr3"));
		carrierSetupForm.setMailingCityName(req.getParameter("mailingCity"));
		carrierSetupForm.setMailingStateCd(req.getParameter("mailingStateCd"));
		carrierSetupForm.setMailingZipCd(req.getParameter("mailingZipCd"));
		carrierSetupForm.setMailingCountryCd(req.getParameter("mailingCountryCd"));
		carrierSetupForm.setShippingCountryCd(req.getParameter("shippingCountryCd"));
		
		carrierSetupForm.setShippingZipCd(req.getParameter("shippingZipCd"));
		carrierSetupForm.setShippingStateCd(req.getParameter("shippingStateCd"));
		carrierSetupForm.setShippingCityName(req.getParameter("shippingCity"));
		carrierSetupForm.setShippingStreet3Address(req.getParameter("shippingAddr3"));
		carrierSetupForm.setShippingStreet1Address(req.getParameter("shippingAddr1"));
		carrierSetupForm.setShippingStreet2Address(req.getParameter("shippingAddr2"));
		carrierSetupForm.setShippingStateCd(req.getParameter("shippingStateCd"));
		String userName = CommonUtility.getUser(req);
		carrierSetupForm.setUserId(userName);
		
//		User user =null;
//		UserContext userContext = null;
//			userContext = this.getUserContext(req);
//			user = userContext.getUser();	
//		carrierSetupForm.setUserId(user.getUserid());
		
		carrierSetupForm.setAction(req.getParameter("action"));
		return carrierSetupForm;
	}

}
