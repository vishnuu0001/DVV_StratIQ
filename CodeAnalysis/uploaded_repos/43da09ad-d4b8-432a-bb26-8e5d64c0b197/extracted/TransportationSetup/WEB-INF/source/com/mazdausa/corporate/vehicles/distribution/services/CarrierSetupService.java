/**
 * This is the CarrierSetupService.java
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
package com.mazdausa.corporate.vehicles.distribution.services;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.apache.log4j.Logger;
import org.apache.struts.util.LabelValueBean;

import com.mazdausa.common.dao.DTOCreatorHandler;
import com.mazdausa.common.dao.GenericDAO;
import com.mazdausa.common.dao.GenericDAOHelper;
import com.mazdausa.common.exceptions.DAOException;
import com.mazdausa.common.log.EMDCSLogger;
import com.mazdausa.common.util.ApplicationUtil;
import com.mazdausa.corporate.vehicles.distribution.application.constants.AppConstant;
import com.mazdausa.corporate.vehicles.distribution.application.form.CarrierSetupForm;
import com.mazdausa.corporate.vehicles.distribution.application.util.CommonUtility;
import com.mazdausa.corporate.vehicles.distribution.persistence.dto.CarrierSetupDTO;


/**
 * @author TechM
 *
 */
public class CarrierSetupService {
	private static Logger LOG = EMDCSLogger.getLogger(CarrierSetupService.class);
	/***
	 * 
	 * @return
	 */
	
	public CarrierSetupDTO getDropdownValues() {
		CarrierSetupDTO carrierSetupDTO=null;
		List<LabelValueBean> statusList=null;
		List<LabelValueBean> typeList=null;
		List<LabelValueBean> currencyList=null;
		List<LabelValueBean> detailedCarrierList=null;
		List<LabelValueBean> detailedCurrencyList=null;
		
		try{
			carrierSetupDTO=new CarrierSetupDTO();
			statusList=getDropdownValues(AppConstant.STATUS_TEXT,AppConstant.STATUS_VALUE);
			typeList=getDropdownValues(AppConstant.TYPE_TEXT,AppConstant.TYPE_VALUE);
			currencyList=getDropdownValues(AppConstant.CURRENCY_TEXT,AppConstant.CURRENCY_VALUE);
			detailedCarrierList=getDropdownValues(AppConstant.DETAILED_TYPE_TEXT,AppConstant.DETAILED_TYPE_VALUE);
			detailedCurrencyList=getDropdownValues(AppConstant.DETAILED_CURRENCY_TEXT,AppConstant.DETAILED_CURRENCY_VALUE);
			
			carrierSetupDTO.setStatusList(statusList);
			carrierSetupDTO.setTypeList(typeList);
			carrierSetupDTO.setCurrencyList(currencyList);
			carrierSetupDTO.setDetailedCarrierTypeList(detailedCarrierList);
			carrierSetupDTO.setDetailedCurrencyList(detailedCurrencyList);
			
		}catch(Exception e){
			
		}
		return carrierSetupDTO;
	}
	
	

	/***
	 * 
	 * @param textString
	 * @param valueString
	 * @return
	 */
	public List<LabelValueBean> getDropdownValues(String textString, String valueString){
		 Map<String,LabelValueBean> dropdownMap=new HashMap<String, LabelValueBean>();;
		List<LabelValueBean> listValue=new ArrayList<LabelValueBean>();
		String procedureName = ApplicationUtil.getSystemProperty(AppConstant.TransportationSetup, AppConstant.SP_LOCATIONDETAILS);
		String statusText=	ApplicationUtil.getSystemProperty(AppConstant.TRANSPORTATION_SETUP_PROPERTIES,textString);
		String statusValue=	ApplicationUtil.getSystemProperty(AppConstant.TRANSPORTATION_SETUP_PROPERTIES,valueString);
		String statusTextArr[]=statusText.split(",");
		String statusValueArr[]=statusValue.split(",");
		for(int i=0;i<statusTextArr.length;i++){
			listValue.add(new LabelValueBean(statusTextArr[i],statusValueArr[i] ));
//			dropdownMap.put(statusTextArr[i], new LabelValueBean(statusTextArr[i],statusValueArr[i] ));
		}
//		Collection<LabelValueBean> valuesList = dropdownMap.values();
//		listValue=new ArrayList<LabelValueBean>(valuesList);
		return listValue;
	}
	
	
	
	public CarrierSetupDTO searchCarrierList(CarrierSetupForm carrierSetupForm) throws Exception {
		CarrierSetupDTO dto = null;
		GenericDAO<CarrierSetupDTO> dao = null;
		LOG.debug("CarrierSetupService-searchCarrierList starts here ");
		try {
			String procedureName ="SV77954"; //ApplicationUtil.getSystemProperty(AppConstants.FLEET_PROPERTY_SCHEMA, "fleet.sp.fl.PR.VehicleAssignmentBackout.display");
			dao = GenericDAOHelper.<CarrierSetupDTO> getDAO();
			dto = (CarrierSetupDTO) dao.findDTO(procedureName, new DTOCreatorHandler<CarrierSetupDTO>() {
				public CarrierSetupDTO createDTO(ResultSet result, Object[] outputValues) {
					CarrierSetupDTO objDO =null;
					List<CarrierSetupDTO> searchList=null;
					try {
						 searchList=new ArrayList<CarrierSetupDTO>();
						CarrierSetupDTO dto = new CarrierSetupDTO();
						if (outputValues[0] != null && outputValues[0].toString().length() >900){
						LOG.debug("outputValues[1]=>" + outputValues[0]);
						dto=parseCarrierInquiryDetails(outputValues[0].toString());
						}
						LOG.debug("outputValues[1]=>" + outputValues[1]);
						if (outputValues[1] != null){
							String arr[]=outputValues[1].toString().split(";");
							dto.setResponseMessage(arr[2].toString().trim());
							dto.setResponseCd(arr[1].toString().trim());
							
						}
						else{
							dto.setResponseMessage("Error in db. Please contact system administrator.");
							dto.setResponseCd("1");
						}
						if (result != null) {
							while (result.next()) {
								
								
								objDO = new CarrierSetupDTO();
								objDO.setCarrierCd(result.getString(AppConstant.CARR_CD)!=null?result.getString(AppConstant.CARR_CD):AppConstant._BLANK);
								objDO.setCarrierName(result.getString(AppConstant.CARR_NM)!=null?result.getString(AppConstant.CARR_NM):AppConstant._BLANK);
								objDO.setStreet1Address(result.getString(AppConstant.STR1_AD)!=null?result.getString(AppConstant.STR1_AD):AppConstant._BLANK);
								objDO.setStreet2Address(result.getString(AppConstant.STR2_AD)!=null?result.getString(AppConstant.STR2_AD):AppConstant._BLANK);
								objDO.setStreet3Address(result.getString(AppConstant.STR3_AD)!=null?result.getString(AppConstant.STR3_AD):AppConstant._BLANK);
								objDO.setCityName(result.getString(AppConstant.CITY_NM)!=null?result.getString(AppConstant.CITY_NM):AppConstant._BLANK);
								objDO.setStateCd(result.getString(AppConstant.ST_CD)!=null?result.getString(AppConstant.ST_CD):AppConstant._BLANK);
								objDO.setZipCd(result.getString(AppConstant.ZIP_CD)!=null?result.getString(AppConstant.ZIP_CD):AppConstant._BLANK);
								objDO.setCarrierTypeDesc(result.getString(AppConstant.CARR_TYPE_DESC)!=null?result.getString(AppConstant.CARR_TYPE_DESC):AppConstant._BLANK);
								objDO.setPaymentTypeDesc(result.getString(AppConstant.PYMT_TYPE_DESC)!=null?result.getString(AppConstant.PYMT_TYPE_DESC):AppConstant._BLANK);
								objDO.setStatusDesc(result.getString(AppConstant.STATUS_DESC)!=null?result.getString(AppConstant.STATUS_DESC):AppConstant._BLANK);
								objDO.setCurrencyCd(result.getString(AppConstant.CURRENCY_CD)!=null?result.getString(AppConstant.CURRENCY_CD):AppConstant._BLANK);
								objDO.setCarrierTypeDesc(result.getString(AppConstant.CARR_TYPE_DESC)!=null?result.getString(AppConstant.CARR_TYPE_DESC):AppConstant._BLANK);
								
								objDO.setCarrierAddress(getAddressDetails(objDO));
								
								searchList.add(objDO);
							}
						}

						

						dto.setSearchList(searchList);
						return dto;
						
					} catch (Exception e) {
						LOG.error("CarrierSetupService-searchCarrierList error "+e);
						e.printStackTrace();
						return null;
					}

				}

				private String getAddressDetails(CarrierSetupDTO objDO) {
					StringBuffer stringBuffer=new StringBuffer();
					boolean commaNeededStatus=false;
					if(null!=objDO.getCarrierName() && objDO.getCarrierName().trim().length()>0 )
					{
						stringBuffer.append(objDO.getCarrierName().trim());
						commaNeededStatus=true;
					}
					if(null!=objDO.getStreet1Address() && objDO.getStreet1Address().trim().length()>0 )
					{
						if(commaNeededStatus){
							stringBuffer.append(",<br/>");
						}
						stringBuffer.append(objDO.getStreet1Address().trim());
						commaNeededStatus=true;
					}
					
					if(null!=objDO.getStreet2Address() && objDO.getStreet2Address().trim().length()>0 )
					{
						if(commaNeededStatus){
							stringBuffer.append(",<br/>");
						}
						stringBuffer.append(objDO.getStreet2Address().trim());
						commaNeededStatus=true;
					}
					if(null!=objDO.getStreet3Address() && objDO.getStreet3Address().trim().length()>0 )
					{
						if(commaNeededStatus){
							stringBuffer.append(",<br/>");
						}
						stringBuffer.append(objDO.getStreet3Address().trim());
						commaNeededStatus=true;
					}
					
					
					
					
//					objDO.setCarrierAddress(getAddressDetails(objDO)+objDO.getStreet1Address()
//							+",<br/>"+objDO.getStreet2Address()
//							+",<br/>"+objDO.getStreet3Address()
//							+",<br/>"+objDO.getCityName()
//							+",<br/>"+objDO.getZipCd()+"\n");
					return stringBuffer.toString();
				}

			}, generateInputParam(carrierSetupForm), AppConstant._BLANK);
			
			
			
			if (dto == null) {
				throw new Exception("Error in database.");
			}
			LOG.debug("CarrierSetupService-searchCarrierList ends here ");
			return dto;
		} catch (DAOException e) {
			LOG.error("CarrierSetupService-searchCarrierList error "+e);
			e.printStackTrace();
			throw e;
		} catch (SQLException e) {
			LOG.error("CarrierSetupService-searchCarrierList error "+e);
			e.printStackTrace();
			throw new DAOException(e.getMessage());
		} catch (Exception e) {
			LOG.error("CarrierSetupService-searchCarrierList error "+e);
			e.printStackTrace();
			throw new DAOException(e.getMessage());
		}
	}
	public static String getDateForSP(String date) {

		
		String strSPDate = "";
		strSPDate = new String();
		try{
			if(!(date.trim().equals("")) && date.indexOf("-")!=-1){
				String tempYear = date.substring(0, date.indexOf("-"));
				String tempMonth = date.substring(date.indexOf("-") + 1, date.lastIndexOf("-"));
				String tempDay = date.substring(date.lastIndexOf("-") + 1, date.length());
				
				String objStringbuffer = null;
				
				if(tempDay.trim().length() < 2 ){		    
				    tempDay = "0" + tempDay; 		    
				}
				if(tempMonth.trim().length() < 2){
				    tempMonth = "0" + tempMonth;
				}
				strSPDate = tempMonth + "/" + tempDay + "/" + tempYear.substring(0,4);
			}
		}catch(Exception e){
			LOG.error("Error while executing LTSUtil's getDateForSP method "
					+ e.getMessage());
			try {
				throw new Exception(e.getMessage());
			} catch (Exception e1) {
				LOG.error("Error while executing LTSUtil's getDateForSP method exception--"+e1.getMessage());
			}
		}
			return strSPDate;
	}
	
	   public CarrierSetupDTO parseCarrierInquiryDetails(String outPutString) throws Exception{
		   CarrierSetupDTO updatedCarrierDetails=new CarrierSetupDTO();
	    	updatedCarrierDetails.setCarrierCd(outPutString.substring(0,5).trim());
	    	updatedCarrierDetails.setCarrierName(outPutString.substring(5,35).trim());
	    	updatedCarrierDetails.setCarrierTypeDesc(outPutString.substring(35,45).trim());
	    	
	    	if(outPutString.substring(35,45).trim().equalsIgnoreCase(AppConstant.TYPE_TRUCK_NAME)){
	    		updatedCarrierDetails.setCarrierType(AppConstant.TYPE_TRUCK_CODE);
	    	}else if(outPutString.substring(35,45).trim().equalsIgnoreCase(AppConstant.TYPE_AIR_NAME)){
	    		updatedCarrierDetails.setCarrierType(AppConstant.TYPE_AIR_CODE);
	    	}else if(outPutString.substring(35,45).trim().equalsIgnoreCase(AppConstant.TYPE_ALL_NAME)){
	    		updatedCarrierDetails.setCarrierType(AppConstant.TYPE_ALL_CODE);
	    	}else if(outPutString.substring(35,45).trim().equalsIgnoreCase(AppConstant.TYPE_RAIL_NAME)){
	    		updatedCarrierDetails.setCarrierType(AppConstant.TYPE_RAIL_CODE);
	    	}else if(outPutString.substring(35,45).trim().equalsIgnoreCase(AppConstant.TYPE_SEA_NAME)){
	    		updatedCarrierDetails.setCarrierType(AppConstant.TYPE_SEA_CODE);
	    	}
	    	updatedCarrierDetails.setStatus(outPutString.substring(45,46).trim());
	    	
	    	
	    	updatedCarrierDetails.setStatusDt(getDateForSP(outPutString.substring(46,56).trim()));
	    	updatedCarrierDetails.setPaymentType(outPutString.substring(56,57).trim());
	    	updatedCarrierDetails.setDeliveryDataYes(outPutString.substring(57,58).trim());
	    	updatedCarrierDetails.setReturnErrorDataYes(outPutString.substring(58,59).trim());
	    	updatedCarrierDetails.setContract1No(outPutString.substring(59,74).trim());
	    	updatedCarrierDetails.setContract1Tx(outPutString.substring(74,104).trim()); 
	    	updatedCarrierDetails.setContract2No(outPutString.substring(104,119).trim());
	    	updatedCarrierDetails.setContract2Tx(outPutString.substring(119,149).trim());
	    	updatedCarrierDetails.setContract3No(outPutString.substring(149,164).trim());
	    	updatedCarrierDetails.setContract3Tx(outPutString.substring(164,194).trim());
	    	updatedCarrierDetails.setContract4No(outPutString.substring(194,209).trim());
	    	updatedCarrierDetails.setContract4Tx(outPutString.substring(209,239).trim());
	    	updatedCarrierDetails.setContract5No(outPutString.substring(239,254).trim());
	    	updatedCarrierDetails.setContract5Tx(outPutString.substring(254,284).trim());
	    	updatedCarrierDetails.setContract6No(outPutString.substring(284,299).trim());
	    	updatedCarrierDetails.setContract6Tx(outPutString.substring(299,329).trim()); 
	    	updatedCarrierDetails.setMailingStreet1Address(outPutString.substring(329,359).trim());
	    	updatedCarrierDetails.setMailingStreet2Address(outPutString.substring(359,389).trim());
	    	updatedCarrierDetails.setMailingStreet3Address(outPutString.substring(389,419).trim());
	    	updatedCarrierDetails.setMailingCityName(outPutString.substring(419,444).trim());
	    	updatedCarrierDetails.setMailingStateCd(outPutString.substring(444,447).trim());
	    	updatedCarrierDetails.setMailingStateName(outPutString.substring(447,467).trim());
	    	updatedCarrierDetails.setMailingZipCd(outPutString.substring(467,476).trim());
	    	updatedCarrierDetails.setMailingCountryCd(outPutString.substring(476,478).trim());
	    	updatedCarrierDetails.setMailingCountryName(outPutString.substring(478,508).trim());
	    	updatedCarrierDetails.setContractFirstName(outPutString.substring(508,523).trim()); 
	    	updatedCarrierDetails.setContractLastName(outPutString.substring(523,543).trim());
	    	updatedCarrierDetails.setContractTitleTx(outPutString.substring(543,563).trim());
	    	
	    	
	    	
	    	
	    	String busPhAreaCode=outPutString.substring(563,566).trim();
	    	String busPhExchangeCode=outPutString.substring(566,569).trim();
	    	String busPhExtentionCode=outPutString.substring(573,578).trim();
	    	String busPhone=outPutString.substring(569,573).trim();
	    	updatedCarrierDetails.setPhoneAcNo(busPhAreaCode);
	    	updatedCarrierDetails.setPhoneExcNo(busPhExchangeCode);
	    	updatedCarrierDetails.setPhoneNo(busPhone);
	    	updatedCarrierDetails.setExtnsnNo(busPhExtentionCode);
	    	
	    	String faxAreaCode=outPutString.substring(578,581).trim();
	    	String faxExchangeCode=outPutString.substring(581,584).trim();
	    	String faxPhone=outPutString.substring(584,588).trim();
	    	updatedCarrierDetails.setFaxAcNo(faxAreaCode.trim()); 
	    	updatedCarrierDetails.setFaxExcNo(faxExchangeCode.trim()); 
	    	updatedCarrierDetails.setFaxphnNo(faxPhone.trim()); 
	    	
	    	
	    	
	    	
	    	updatedCarrierDetails.setContactEmail(outPutString.substring(588,618).trim()); 
	       	String cellAreaCode=outPutString.substring(618,621).trim();
	    	String cellExchangeCode=outPutString.substring(621,624).trim();
	    	String cellPhone=cellAreaCode+cellExchangeCode+outPutString.substring(624,628).trim();
	    	updatedCarrierDetails.setClPhoneAcNo(cellAreaCode.trim());
	    	updatedCarrierDetails.setClPhoneExcNo(cellExchangeCode.trim());
	    	updatedCarrierDetails.setClPhoneNo(outPutString.substring(624,628).trim());
	    	updatedCarrierDetails.setClExtnsnNo(outPutString.substring(624,628).trim());
	    	
	    	
	    	
	    	updatedCarrierDetails.setShippingStreet1Address(outPutString.substring(628,658).trim());
	    	updatedCarrierDetails.setShippingStreet2Address(outPutString.substring(658,688).trim());
	    	updatedCarrierDetails.setShippingStreet3Address(outPutString.substring(688,718).trim());
	    	updatedCarrierDetails.setShippingCityName(outPutString.substring(718,743).trim());
	    	updatedCarrierDetails.setShippingStateCd(outPutString.substring(743,746).trim());
	    	updatedCarrierDetails.setShippingStateName(outPutString.substring(746,766).trim());
	    	updatedCarrierDetails.setShippingZipCd(outPutString.substring(766,775).trim()); 
	    	updatedCarrierDetails.setShippingCountryCd(outPutString.substring(775,777).trim());
	    	updatedCarrierDetails.setShippingCountryName(outPutString.substring(777,807).trim());
	    	updatedCarrierDetails.setUserId(outPutString.substring(807,815).trim());
	    	updatedCarrierDetails.setLastUpdateFirtName(outPutString.substring(815,830).trim());
	    	updatedCarrierDetails.setLastUpdatedLastName(outPutString.substring(830,850).trim());
	    	
	    	updatedCarrierDetails.setConcatedUserDetails(updatedCarrierDetails.getUserId().trim()+" - "+updatedCarrierDetails.getLastUpdateFirtName().trim()+" "+updatedCarrierDetails.getLastUpdatedLastName().trim());
	    	
	    	
	    	
	    	updatedCarrierDetails.setMaxLastUpdateTimeStamp(outPutString.substring(850,876).trim());
	    	updatedCarrierDetails.setLastUpdateTimeStamp(outPutString.substring(876,902).trim());
	    	updatedCarrierDetails.setMailingLastUpdateTimeStamp(outPutString.substring(902,928).trim());
	    	updatedCarrierDetails.setContactLastUpdateTimeStamp(outPutString.substring(928,954).trim());
	    	updatedCarrierDetails.setCurrency(outPutString.substring(954,955).trim());
	    	updatedCarrierDetails.setShippingLastUpdateTimeStamp(outPutString.substring(955,981).trim());
	    	
	    	return updatedCarrierDetails;
	    }
/****
 * 
 * @param carrierSetupForm
 * @return
 */
private static String  generateInputParam(CarrierSetupForm carrierSetupForm){
	StringBuilder generatedInputString1=new StringBuilder();
	
	generatedInputString1.append(addSpace(carrierSetupForm.getAction(),1));
	generatedInputString1.append(addSpace(carrierSetupForm.getUserId(),8));
	generatedInputString1.append(addSpace(carrierSetupForm.getCarrierCd(),5));
	if(!carrierSetupForm.getAction().equals("R")){
	generatedInputString1.append(addSpace(carrierSetupForm.getCarrierName(),30));
	generatedInputString1.append(addSpace(carrierSetupForm.getCarrierType(),10));
	generatedInputString1.append(addSpace(carrierSetupForm.getStatus(),1));
	//generatedInputString1.append(addSpace(CommonUtility.formatDatetoString("MM/DD/yyyy","yyyy-MM-dd",carrierSetupForm.getStatusDt()),10));
	generatedInputString1.append(addSpace(carrierSetupForm.getStatusDt(),10));
	generatedInputString1.append(addSpace(carrierSetupForm.getPaymentType(),1));
	generatedInputString1.append(addSpace(carrierSetupForm.getDeliveryDataYes(),1)); 
	generatedInputString1.append(addSpace(carrierSetupForm.getReturnErrorDataYes(),1)); 
	generatedInputString1.append(addSpace(carrierSetupForm.getContract1No(),15));
	generatedInputString1.append(addSpace(carrierSetupForm.getContract1Tx(),30));
	generatedInputString1.append(addSpace(carrierSetupForm.getContract2No(),15));
	generatedInputString1.append(addSpace(carrierSetupForm.getContract2Tx(),30));
	generatedInputString1.append(addSpace(carrierSetupForm.getContract3No(),15));
	generatedInputString1.append(addSpace(carrierSetupForm.getContract3Tx(),30));
	generatedInputString1.append(addSpace(carrierSetupForm.getContract4No(),15));
	generatedInputString1.append(addSpace(carrierSetupForm.getContract4Tx(),30));
	generatedInputString1.append(addSpace(carrierSetupForm.getContract5No(),15));
	generatedInputString1.append(addSpace(carrierSetupForm.getContract5Tx(),30));
	generatedInputString1.append(addSpace(carrierSetupForm.getContract6No(),15));
	generatedInputString1.append(addSpace(carrierSetupForm.getContract6Tx(),30));
	

//	
    generatedInputString1.append(addSpace(carrierSetupForm.getCurrencyCd(),1)); 
	generatedInputString1.append(addSpace(carrierSetupForm.getMailingStreet1Address(),30));
	generatedInputString1.append(addSpace(carrierSetupForm.getMailingStreet2Address(),30));
	generatedInputString1.append(addSpace(carrierSetupForm.getMailingStreet3Address(),30));
	generatedInputString1.append(addSpace(carrierSetupForm.getMailingCityName(),25));
	generatedInputString1.append(addSpace(carrierSetupForm.getMailingStateCd(),03));
	generatedInputString1.append(addSpace(carrierSetupForm.getMailingStateName(),20));//need to check
	generatedInputString1.append(addSpace(carrierSetupForm.getMailingZipCd(),9));
	generatedInputString1.append(addSpace(carrierSetupForm.getMailingCountryCd(),02));
	generatedInputString1.append(addSpace(carrierSetupForm.getMailingCountryName(),30));//need to check
	generatedInputString1.append(addSpace(carrierSetupForm.getContractFirstName(),15));
	generatedInputString1.append(addSpace(carrierSetupForm.getContractLastName(),20));
	generatedInputString1.append(addSpace(carrierSetupForm.getContractTitleTx(),20));
	generatedInputString1.append(addSpace(carrierSetupForm.getPhoneAcNo(),3));
	generatedInputString1.append(addSpace(carrierSetupForm.getPhoneExcNo(),3));
	generatedInputString1.append(addSpace(carrierSetupForm.getPhoneNo(),4));
	generatedInputString1.append(addSpace(carrierSetupForm.getExtnsnNo(),5));
	generatedInputString1.append(addSpace(carrierSetupForm.getFaxAcNo(),3));
	generatedInputString1.append(addSpace(carrierSetupForm.getFaxExcNo(),3));
	generatedInputString1.append(addSpace(carrierSetupForm.getFaxphnNo(),04));
	generatedInputString1.append(addSpace(carrierSetupForm.getContactEmail(),30));
	generatedInputString1.append(addSpace(carrierSetupForm.getClPhoneAcNo(),3));
	generatedInputString1.append(addSpace(carrierSetupForm.getClPhoneExcNo(),3));
	generatedInputString1.append(addSpace(carrierSetupForm.getClPhoneNo(),4));
	/*generatedInputString1.append(addSpace(carrierSetupForm.getClExtnsnNo(),5));
	generatedInputString1.append(addSpace(carrierSetupForm.getClFaxAcNo(),3));
	generatedInputString1.append(addSpace(carrierSetupForm.getClFaxExcNo(),3));
	generatedInputString1.append(addSpace(carrierSetupForm.getClFaxphnNo(),04));*/
	generatedInputString1.append(addSpace(carrierSetupForm.getShippingStreet1Address(),30));
	generatedInputString1.append(addSpace(carrierSetupForm.getShippingStreet2Address(),30));
	generatedInputString1.append(addSpace(carrierSetupForm.getShippingStreet3Address(),30));
	generatedInputString1.append(addSpace(carrierSetupForm.getShippingCityName(),25));
	generatedInputString1.append(addSpace(carrierSetupForm.getShippingStateCd(),3));
	generatedInputString1.append(addSpace(carrierSetupForm.getShippingStateName(),20));
	generatedInputString1.append(addSpace(carrierSetupForm.getShippingZipCd(),9));
	generatedInputString1.append(addSpace(carrierSetupForm.getShippingCountryCd(),02));
	generatedInputString1.append(addSpace(carrierSetupForm.getShippingCountryName(),30));
	}
	return generatedInputString1.toString();
	
}

/***
 * Adding space
 * @param variable
 * @param maxSize
 * @return
 */
public static String addSpace(String variable, int maxSize){
	StringBuilder strBuff = new StringBuilder();
    int len = 0;
    if( variable != null ){
        len = variable.length();
        strBuff.append(variable);
    }    
    for (int i = len; i < maxSize; i++){
    
        strBuff.append(AppConstant.BLANK);
    }
    return strBuff.toString();
}
/***
 * appending left space
 * @param variable
 * @param maxSize
 * @return
 */
public static String leftSpace(String variable, int maxSize){
    StringBuilder strBuff = new StringBuilder();
    int len = 0;
    if( variable != null ){
        len = variable.length();
        strBuff.append(variable);
    }    
    String tempStr=AppConstant.EMPTY;
    for (int i = len; i < maxSize; i++){
    
    	tempStr+=AppConstant.BLANK;
    }
    return tempStr+strBuff.toString();
}
/***
 * adding default date
 * @param variable
 * @param format
 * @return
 */
public static String addDefaultDate(String variable,String format){
    if( variable != null ){
       return variable;
    }else{
    	return format;
    	
    }
   
}

}
