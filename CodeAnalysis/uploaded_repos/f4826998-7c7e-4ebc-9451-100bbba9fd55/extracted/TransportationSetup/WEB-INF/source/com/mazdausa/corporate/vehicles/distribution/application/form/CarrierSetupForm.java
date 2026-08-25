/**
 * This is the CarrierSetupForm.java
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
package com.mazdausa.corporate.vehicles.distribution.application.form;

import java.util.List;

import org.apache.struts.action.ActionForm;
import org.apache.struts.util.LabelValueBean;

import com.mazdausa.corporate.vehicles.distribution.persistence.dto.CarrierSetupDTO;

/**
 * @author TechM
 *
 */
public class CarrierSetupForm extends ActionForm {

	private String action;
	private String carrierName;
	private String carrierCd;
	private String carrierAddress;
	private String carrierType;
	private String paymentType;
	private String status;
	private String mailingStreet1Address;
	private String mailingStreet2Address;
	private String mailingStreet3Address;
	private String mailingCityName;
	private String mailingStateCd;
	private String mailingZipCd;
	private String carrierTypeDesc;
	private String paymentTypeDesc;
	private String statusDesc;
	private String statusDt;
	private String currencyCd;
	private List<LabelValueBean> statusList;
	private List<LabelValueBean> typeList;
	private List<LabelValueBean> currencyList;
	
	private List<LabelValueBean> detailedTypeList;
	private List<LabelValueBean> detailedCurrencyList;
	
	private List<CarrierSetupDTO> searchList;
	private String contract1No;
	private String contract1Tx;
	private String contract2No;
	private String contract2Tx;
	private String contract3No;
	private String contract3Tx;
	private String contract4No;
	private String contract5Tx;
	private String contract6No;
	private String contract6Tx;
	private String contract4Tx;
	private String contract5No;
	private String mailingStateName;
	private String mailingCountryCd;
	private String mailingCountryName;
	private String contractFirstName;
	private String contractLastName;
	private String contractTitleTx;
	private String phoneAcNo;
	private String phoneExcNo;
	private String phoneNo;
	private String extnsnNo;
	private String faxAcNo;
	private String faxExcNo;
	private String faxphnNo;
	private String shippingStreet1Address;
	private String shippingStreet2Address;
	private String shippingStreet3Address;
	private String shippingStateCd;
	private String shippingStateName;
	private String shippingCountryCd;
	private String shippingCountryName;
	private String shippingZipCd;
	private String shippingCityName;
	private String clPhoneAcNo;
	private String clPhoneExcNo;
	private String clPhoneNo;
	private String clExtnsnNo;
	private String clFaxAcNo;
	private String clFaxExcNo;
	private String clFaxphnNo;
	private List<LabelValueBean> countryList;
	private List<LabelValueBean> stateList;
	private String contactEmail;
	private String userId;
	private String lastUpdateBy;
	private String concatedUserDetails;
	private String lastUpdateFirtName;
	private String lastUpdatedLastName;
	private String maxLastUpdateTimeStamp;
	private String lastUpdateTimeStamp;
	private String mailingLastUpdateTimeStamp;
	private String contactLastUpdateTimeStamp;
	private String currency;
	private String shippingLastUpdateTimeStamp;
	private String deliveryDataYes;
	private String returnErrorDataYes;
	private String statusDate;
	private String statusDate1;
	
	
	public String getContactEmail() {
		return contactEmail;
	}
	public void setContactEmail(String contactEmail) {
		this.contactEmail = contactEmail;
	}
	public String getUserId() {
		return userId;
	}
	public void setUserId(String userId) {
		this.userId = userId;
	}
	public String getLastUpdateBy() {
		return lastUpdateBy;
	}
	public void setLastUpdateBy(String lastUpdateBy) {
		this.lastUpdateBy = lastUpdateBy;
	}
	public String getConcatedUserDetails() {
		return concatedUserDetails;
	}
	public void setConcatedUserDetails(String concatedUserDetails) {
		this.concatedUserDetails = concatedUserDetails;
	}
	public String getLastUpdateFirtName() {
		return lastUpdateFirtName;
	}
	public void setLastUpdateFirtName(String lastUpdateFirtName) {
		this.lastUpdateFirtName = lastUpdateFirtName;
	}
	public String getLastUpdatedLastName() {
		return lastUpdatedLastName;
	}
	public void setLastUpdatedLastName(String lastUpdatedLastName) {
		this.lastUpdatedLastName = lastUpdatedLastName;
	}
	public String getMaxLastUpdateTimeStamp() {
		return maxLastUpdateTimeStamp;
	}
	public void setMaxLastUpdateTimeStamp(String maxLastUpdateTimeStamp) {
		this.maxLastUpdateTimeStamp = maxLastUpdateTimeStamp;
	}
	public String getLastUpdateTimeStamp() {
		return lastUpdateTimeStamp;
	}
	public void setLastUpdateTimeStamp(String lastUpdateTimeStamp) {
		this.lastUpdateTimeStamp = lastUpdateTimeStamp;
	}
	public String getMailingLastUpdateTimeStamp() {
		return mailingLastUpdateTimeStamp;
	}
	public void setMailingLastUpdateTimeStamp(String mailingLastUpdateTimeStamp) {
		this.mailingLastUpdateTimeStamp = mailingLastUpdateTimeStamp;
	}
	public String getContactLastUpdateTimeStamp() {
		return contactLastUpdateTimeStamp;
	}
	public void setContactLastUpdateTimeStamp(String contactLastUpdateTimeStamp) {
		this.contactLastUpdateTimeStamp = contactLastUpdateTimeStamp;
	}
	public String getCurrency() {
		return currency;
	}
	public void setCurrency(String currency) {
		this.currency = currency;
	}
	public String getShippingLastUpdateTimeStamp() {
		return shippingLastUpdateTimeStamp;
	}
	public void setShippingLastUpdateTimeStamp(String shippingLastUpdateTimeStamp) {
		this.shippingLastUpdateTimeStamp = shippingLastUpdateTimeStamp;
	}
	public String getDeliveryDataYes() {
		return deliveryDataYes;
	}
	public void setDeliveryDataYes(String deliveryDataYes) {
		this.deliveryDataYes = deliveryDataYes;
	}
	public String getReturnErrorDataYes() {
		return returnErrorDataYes;
	}
	public void setReturnErrorDataYes(String returnErrorDataYes) {
		this.returnErrorDataYes = returnErrorDataYes;
	}
	public String getAction() {
		return action;
	}
	public void setAction(String action) {
		this.action = action;
	}
	public String getCarrierName() {
		return carrierName;
	}
	public void setCarrierName(String carrierName) {
		this.carrierName = carrierName;
	}
	public String getCarrierCd() {
		return carrierCd;
	}
	public void setCarrierCd(String carrierCd) {
		this.carrierCd = carrierCd;
	}
	public String getCarrierAddress() {
		return carrierAddress;
	}
	public void setCarrierAddress(String carrierAddress) {
		this.carrierAddress = carrierAddress;
	}
	public String getCarrierType() {
		return carrierType;
	}
	public void setCarrierType(String carrierType) {
		this.carrierType = carrierType;
	}
	public String getPaymentType() {
		return paymentType;
	}
	public void setPaymentType(String paymentType) {
		this.paymentType = paymentType;
	}
	public String getStatus() {
		return status;
	}
	public void setStatus(String status) {
		this.status = status;
	}
	public String getMailingStreet1Address() {
		return mailingStreet1Address;
	}
	public void setMailingStreet1Address(String mailingStreet1Address) {
		this.mailingStreet1Address = mailingStreet1Address;
	}
	public String getMailingStreet2Address() {
		return mailingStreet2Address;
	}
	public void setMailingStreet2Address(String mailingStreet2Address) {
		this.mailingStreet2Address = mailingStreet2Address;
	}
	public String getMailingStreet3Address() {
		return mailingStreet3Address;
	}
	public void setMailingStreet3Address(String mailingStreet3Address) {
		this.mailingStreet3Address = mailingStreet3Address;
	}
	public String getMailingCityName() {
		return mailingCityName;
	}
	public void setMailingCityName(String mailingCityName) {
		this.mailingCityName = mailingCityName;
	}
	public String getMailingStateCd() {
		return mailingStateCd;
	}
	public void setMailingStateCd(String mailingStateCd) {
		this.mailingStateCd = mailingStateCd;
	}
	public String getMailingZipCd() {
		return mailingZipCd;
	}
	public void setMailingZipCd(String mailingZipCd) {
		this.mailingZipCd = mailingZipCd;
	}
	public String getCarrierTypeDesc() {
		return carrierTypeDesc;
	}
	public void setCarrierTypeDesc(String carrierTypeDesc) {
		this.carrierTypeDesc = carrierTypeDesc;
	}
	public String getPaymentTypeDesc() {
		return paymentTypeDesc;
	}
	public void setPaymentTypeDesc(String paymentTypeDesc) {
		this.paymentTypeDesc = paymentTypeDesc;
	}
	public String getStatusDesc() {
		return statusDesc;
	}
	public void setStatusDesc(String statusDesc) {
		this.statusDesc = statusDesc;
	}
	public String getStatusDt() {
		return statusDt;
	}
	public void setStatusDt(String statusDt) {
		this.statusDt = statusDt;
	}
	public String getCurrencyCd() {
		return currencyCd;
	}
	public void setCurrencyCd(String currencyCd) {
		this.currencyCd = currencyCd;
	}
	public List<LabelValueBean> getStatusList() {
		return statusList;
	}
	public void setStatusList(List<LabelValueBean> statusList) {
		this.statusList = statusList;
	}
	public List<LabelValueBean> getTypeList() {
		return typeList;
	}
	public void setTypeList(List<LabelValueBean> typeList) {
		this.typeList = typeList;
	}
	public List<LabelValueBean> getCurrencyList() {
		return currencyList;
	}
	public void setCurrencyList(List<LabelValueBean> currencyList) {
		this.currencyList = currencyList;
	}
	public List<CarrierSetupDTO> getSearchList() {
		return searchList;
	}
	public void setSearchList(List<CarrierSetupDTO> searchList) {
		this.searchList = searchList;
	}
	public String getContract1No() {
		return contract1No;
	}
	public void setContract1No(String contract1No) {
		this.contract1No = contract1No;
	}
	public String getContract1Tx() {
		return contract1Tx;
	}
	public void setContract1Tx(String contract1Tx) {
		this.contract1Tx = contract1Tx;
	}
	public String getContract2No() {
		return contract2No;
	}
	public void setContract2No(String contract2No) {
		this.contract2No = contract2No;
	}
	public String getContract2Tx() {
		return contract2Tx;
	}
	public void setContract2Tx(String contract2Tx) {
		this.contract2Tx = contract2Tx;
	}
	public String getContract3No() {
		return contract3No;
	}
	public void setContract3No(String contract3No) {
		this.contract3No = contract3No;
	}
	public String getContract3Tx() {
		return contract3Tx;
	}
	public void setContract3Tx(String contract3Tx) {
		this.contract3Tx = contract3Tx;
	}
	public String getContract4No() {
		return contract4No;
	}
	public void setContract4No(String contract4No) {
		this.contract4No = contract4No;
	}
	public String getContract5Tx() {
		return contract5Tx;
	}
	public void setContract5Tx(String contract5Tx) {
		this.contract5Tx = contract5Tx;
	}
	public String getContract6No() {
		return contract6No;
	}
	public void setContract6No(String contract6No) {
		this.contract6No = contract6No;
	}
	public String getContract6Tx() {
		return contract6Tx;
	}
	public void setContract6Tx(String contract6Tx) {
		this.contract6Tx = contract6Tx;
	}
	public String getContract4Tx() {
		return contract4Tx;
	}
	public void setContract4Tx(String contract4Tx) {
		this.contract4Tx = contract4Tx;
	}
	public String getContract5No() {
		return contract5No;
	}
	public void setContract5No(String contract5No) {
		this.contract5No = contract5No;
	}
	public String getMailingStateName() {
		return mailingStateName;
	}
	public void setMailingStateName(String mailingStateName) {
		this.mailingStateName = mailingStateName;
	}
	public String getMailingCountryCd() {
		return mailingCountryCd;
	}
	public void setMailingCountryCd(String mailingCountryCd) {
		this.mailingCountryCd = mailingCountryCd;
	}
	public String getMailingCountryName() {
		return mailingCountryName;
	}
	public void setMailingCountryName(String mailingCountryName) {
		this.mailingCountryName = mailingCountryName;
	}
	public String getContractFirstName() {
		return contractFirstName;
	}
	public void setContractFirstName(String contractFirstName) {
		this.contractFirstName = contractFirstName;
	}
	public String getContractLastName() {
		return contractLastName;
	}
	public void setContractLastName(String contractLastName) {
		this.contractLastName = contractLastName;
	}
	public String getContractTitleTx() {
		return contractTitleTx;
	}
	public void setContractTitleTx(String contractTitleTx) {
		this.contractTitleTx = contractTitleTx;
	}
	public String getPhoneAcNo() {
		return phoneAcNo;
	}
	public void setPhoneAcNo(String phoneAcNo) {
		this.phoneAcNo = phoneAcNo;
	}
	public String getPhoneExcNo() {
		return phoneExcNo;
	}
	public void setPhoneExcNo(String phoneExcNo) {
		this.phoneExcNo = phoneExcNo;
	}
	public String getPhoneNo() {
		return phoneNo;
	}
	public void setPhoneNo(String phoneNo) {
		this.phoneNo = phoneNo;
	}
	public String getExtnsnNo() {
		return extnsnNo;
	}
	public void setExtnsnNo(String extnsnNo) {
		this.extnsnNo = extnsnNo;
	}
	public String getFaxAcNo() {
		return faxAcNo;
	}
	public void setFaxAcNo(String faxAcNo) {
		this.faxAcNo = faxAcNo;
	}
	public String getFaxExcNo() {
		return faxExcNo;
	}
	public void setFaxExcNo(String faxExcNo) {
		this.faxExcNo = faxExcNo;
	}
	public String getFaxphnNo() {
		return faxphnNo;
	}
	public void setFaxphnNo(String faxphnNo) {
		this.faxphnNo = faxphnNo;
	}
	public String getShippingStreet1Address() {
		return shippingStreet1Address;
	}
	public void setShippingStreet1Address(String shippingStreet1Address) {
		this.shippingStreet1Address = shippingStreet1Address;
	}
	public String getShippingStreet2Address() {
		return shippingStreet2Address;
	}
	public void setShippingStreet2Address(String shippingStreet2Address) {
		this.shippingStreet2Address = shippingStreet2Address;
	}
	public String getShippingStreet3Address() {
		return shippingStreet3Address;
	}
	public void setShippingStreet3Address(String shippingStreet3Address) {
		this.shippingStreet3Address = shippingStreet3Address;
	}
	public String getShippingStateCd() {
		return shippingStateCd;
	}
	public void setShippingStateCd(String shippingStateCd) {
		this.shippingStateCd = shippingStateCd;
	}
	public String getShippingStateName() {
		return shippingStateName;
	}
	public void setShippingStateName(String shippingStateName) {
		this.shippingStateName = shippingStateName;
	}
	public String getShippingCountryCd() {
		return shippingCountryCd;
	}
	public void setShippingCountryCd(String shippingCountryCd) {
		this.shippingCountryCd = shippingCountryCd;
	}
	public String getShippingCountryName() {
		return shippingCountryName;
	}
	public void setShippingCountryName(String shippingCountryName) {
		this.shippingCountryName = shippingCountryName;
	}
	public String getShippingZipCd() {
		return shippingZipCd;
	}
	public void setShippingZipCd(String shippingZipCd) {
		this.shippingZipCd = shippingZipCd;
	}
	public String getShippingCityName() {
		return shippingCityName;
	}
	public void setShippingCityName(String shippingCityName) {
		this.shippingCityName = shippingCityName;
	}
	public String getClPhoneAcNo() {
		return clPhoneAcNo;
	}
	public void setClPhoneAcNo(String clPhoneAcNo) {
		this.clPhoneAcNo = clPhoneAcNo;
	}
	public String getClPhoneExcNo() {
		return clPhoneExcNo;
	}
	public void setClPhoneExcNo(String clPhoneExcNo) {
		this.clPhoneExcNo = clPhoneExcNo;
	}
	public String getClPhoneNo() {
		return clPhoneNo;
	}
	public void setClPhoneNo(String clPhoneNo) {
		this.clPhoneNo = clPhoneNo;
	}
	public String getClExtnsnNo() {
		return clExtnsnNo;
	}
	public void setClExtnsnNo(String clExtnsnNo) {
		this.clExtnsnNo = clExtnsnNo;
	}
	public String getClFaxAcNo() {
		return clFaxAcNo;
	}
	public void setClFaxAcNo(String clFaxAcNo) {
		this.clFaxAcNo = clFaxAcNo;
	}
	public String getClFaxExcNo() {
		return clFaxExcNo;
	}
	public void setClFaxExcNo(String clFaxExcNo) {
		this.clFaxExcNo = clFaxExcNo;
	}
	public String getClFaxphnNo() {
		return clFaxphnNo;
	}
	public void setClFaxphnNo(String clFaxphnNo) {
		this.clFaxphnNo = clFaxphnNo;
	}
	public List<LabelValueBean> getCountryList() {
		return countryList;
	}
	public void setCountryList(List<LabelValueBean> countryList) {
		this.countryList = countryList;
	}
	public List<LabelValueBean> getStateList() {
		return stateList;
	}
	public void setStateList(List<LabelValueBean> stateList) {
		this.stateList = stateList;
	}
	public List<LabelValueBean> getDetailedTypeList() {
		return detailedTypeList;
	}
	public void setDetailedTypeList(List<LabelValueBean> detailedTypeList) {
		this.detailedTypeList = detailedTypeList;
	}
	public List<LabelValueBean> getDetailedCurrencyList() {
		return detailedCurrencyList;
	}
	public void setDetailedCurrencyList(List<LabelValueBean> detailedCurrencyList) {
		this.detailedCurrencyList = detailedCurrencyList;
	}
	public String getStatusDate() {
		return statusDate;
	}
	public void setStatusDate(String statusDate) {
		this.statusDate = statusDate;
	}
	public String getStatusDate1() {
		return statusDate1;
	}
	public void setStatusDate1(String statusDate1) {
		this.statusDate1 = statusDate1;
	}
	
	
}	
