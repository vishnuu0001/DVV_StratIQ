
package com.mazdausa.corporate.vehicles.distribution.application.form;

import java.util.ArrayList;

import org.apache.struts.action.ActionForm;


import com.mazdausa.corporate.vehicles.distribution.persistence.dto.LocationIndexDTO;

public class LocationIndexForm extends ActionForm {


	private static final long serialVersionUID = 1L;
	private String countryCode;
	private ArrayList countryList;
	private String regionCode;
	private ArrayList regionCodeList;
	private String stateName;
	private ArrayList stateNameList;
	private String statusCode;
	private ArrayList statusCodeList;
	private String typeName;
	private ArrayList typeNameList;
	
	private String locationCode;
	
	
	private LocationIndexDTO countryregionCodeList;
	private LocationIndexDTO countrystateCodeList;
	
	
	private String currentLocationCode;
	private String locationName;
	private String streetAddress1;
	private String streetAddress2;
	private String streetAddress3;
	private String cityName;
	private String stateCode;
	private String zipCode;
	private String countryCd;
	private String countryNm;
	private String phoneAcNo;
	private String phoneExcNo;
	private String phoneNo;
	private String addressTypeNm;
	private String statusDesc;
	private String statusDescCd;
	private String cdtvalueTx;
	private String cdtvalueTxCd;
	private String currentDate;
	private String currentDate1;
	private String regionCd;
	private String responseText;
	private String responseCode;
	private String locationCodeVisible;
	

	private String locstatusCode;
	private String loctypeName;
	private String loctypeName2;
	private String loctypeName3;
	private String locregionCode;
	private String mailstateName;
	private String shipstateName;
	private String mailcountryCode;
	private String shipcountryCode;

	private ArrayList<LocationIndexDTO> searchList;
	private ArrayList<LocationIndexDTO> saveList;
	private ArrayList<LocationIndexDTO> deleteList;
	private ArrayList<LocationIndexDTO> updateList;
	private ArrayList<LocationIndexDTO> saveCheckList;
	private ArrayList<LocationIndexDTO> countrySearchList;
	private String districtCode;
	private String locationLatestCode;
	private String actionCode;
	private String  locDate;
	private String latestUpdatedBy;
	
	public String getLocstatusCode() {
		return locstatusCode;
	}
	public void setLocstatusCode(String locstatusCode) {
		this.locstatusCode = locstatusCode;
	}
	public String getLoctypeName() {
		return loctypeName;
	}
	public void setLoctypeName(String loctypeName) {
		this.loctypeName = loctypeName;
	}
	public String getLoctypeName2() {
		return loctypeName2;
	}
	public void setLoctypeName2(String loctypeName2) {
		this.loctypeName2 = loctypeName2;
	}
	public String getLoctypeName3() {
		return loctypeName3;
	}
	public void setLoctypeName3(String loctypeName3) {
		this.loctypeName3 = loctypeName3;
	}
	public String getLocregionCode() {
		return locregionCode;
	}
	public void setLocregionCode(String locregionCode) {
		this.locregionCode = locregionCode;
	}
	public String getMailstateName() {
		return mailstateName;
	}
	public void setMailstateName(String mailstateName) {
		this.mailstateName = mailstateName;
	}
	public String getShipstateName() {
		return shipstateName;
	}
	public void setShipstateName(String shipstateName) {
		this.shipstateName = shipstateName;
	}
	public String getMailcountryCode() {
		return mailcountryCode;
	}
	public void setMailcountryCode(String mailcountryCode) {
		this.mailcountryCode = mailcountryCode;
	}
	public String getShipcountryCode() {
		return shipcountryCode;
	}
	public void setShipcountryCode(String shipcountryCode) {
		this.shipcountryCode = shipcountryCode;
	}
	
	
	
	public ArrayList<LocationIndexDTO> getCountrySearchList() {
		return countrySearchList;
	}
	public void setCountrySearchList(ArrayList<LocationIndexDTO> countrySearchList) {
		this.countrySearchList = countrySearchList;
	}
	
	public ArrayList<LocationIndexDTO> getSaveCheckList() {
		return saveCheckList;
	}
	public void setSaveCheckList(ArrayList<LocationIndexDTO> saveCheckList) {
		this.saveCheckList = saveCheckList;
	}
	public ArrayList getCountryList() {
		return countryList;
	}
	public void setCountryList(ArrayList countryList) {
		this.countryList = countryList;
	}

	public ArrayList getRegionCodeList() {
		return regionCodeList;
	}
	public void setRegionCodeList(ArrayList regionCodeList) {
		this.regionCodeList = regionCodeList;
	}
	
	
	public ArrayList getStateNameList() {
		return stateNameList;
	}
	public void setStateNameList(ArrayList stateNameList) {
		this.stateNameList = stateNameList;
	}
	
	public ArrayList getStatusCodeList() {
		return statusCodeList;
	}
	public void setStatusCodeList(ArrayList statusCodeList) {
		this.statusCodeList = statusCodeList;
	}
	
	public ArrayList getTypeNameList() {
		return typeNameList;
	}
	public void setTypeNameList(ArrayList typeNameList) {
		this.typeNameList = typeNameList;
	}
	public String getCurrentLocationCode() {
		return currentLocationCode;
	}
	public void setCurrentLocationCode(String currentLocationCode) {
		this.currentLocationCode = currentLocationCode;
	}
	public String getLocationName() {
		return locationName;
	}
	public void setLocationName(String locationName) {
		this.locationName = locationName;
	}
	public String getStreetAddress1() {
		return streetAddress1;
	}
	public void setStreetAddress1(String streetAddress1) {
		this.streetAddress1 = streetAddress1;
	}
	public String getStreetAddress2() {
		return streetAddress2;
	}
	public void setStreetAddress2(String streetAddress2) {
		this.streetAddress2 = streetAddress2;
	}
	public String getStreetAddress3() {
		return streetAddress3;
	}
	public void setStreetAddress3(String streetAddress3) {
		this.streetAddress3 = streetAddress3;
	}
	public String getCityName() {
		return cityName;
	}
	public void setCityName(String cityName) {
		this.cityName = cityName;
	}
	public String getStateCode() {
		return stateCode;
	}
	public void setStateCode(String stateCode) {
		this.stateCode = stateCode;
	}
	public String getZipCode() {
		return zipCode;
	}
	public void setZipCode(String zipCode) {
		this.zipCode = zipCode;
	}
	public String getCountryCd() {
		return countryCd;
	}
	public void setCountryCd(String countryCd) {
		this.countryCd = countryCd;
	}
	public String getCountryNm() {
		return countryNm;
	}
	public void setCountryNm(String countryNm) {
		this.countryNm = countryNm;
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
	public String getAddressTypeNm() {
		return addressTypeNm;
	}
	public void setAddressTypeNm(String addressTypeNm) {
		this.addressTypeNm = addressTypeNm;
	}
	public String getStatusDesc() {
		return statusDesc;
	}
	public void setStatusDesc(String statusDesc) {
		this.statusDesc = statusDesc;
	}
	public String getCdtvalueTx() {
		return cdtvalueTx;
	}
	public void setCdtvalueTx(String cdtvalueTx) {
		this.cdtvalueTx = cdtvalueTx;
	}
	public String getRegionCd() {
		return regionCd;
	}
	public void setRegionCd(String regionCd) {
		this.regionCd = regionCd;
	}
	public String getResponseText() {
		return responseText;
	}
	public void setResponseText(String responseText) {
		this.responseText = responseText;
	}
	public String getResponseCode() {
		return responseCode;
	}
	public void setResponseCode(String responseCode) {
		this.responseCode = responseCode;
	}
	public String getLocationCodeVisible() {
		return locationCodeVisible;
	}
	public void setLocationCodeVisible(String locationCodeVisible) {
		this.locationCodeVisible = locationCodeVisible;
	}
	public ArrayList<LocationIndexDTO> getSearchList() {
		return searchList;
	}
	public void setSearchList(ArrayList<LocationIndexDTO> searchList) {
		this.searchList = searchList;
	}
	public ArrayList<LocationIndexDTO> getSaveList() {
		return saveList;
	}
	public void setSaveList(ArrayList<LocationIndexDTO> saveList) {
		this.saveList = saveList;
	}
	public ArrayList<LocationIndexDTO> getDeleteList() {
		return deleteList;
	}
	public void setDeleteList(ArrayList<LocationIndexDTO> deleteList) {
		this.deleteList = deleteList;
	}
	public ArrayList<LocationIndexDTO> getUpdateList() {
		return updateList;
	}
	public void setUpdateList(ArrayList<LocationIndexDTO> updateList) {
		this.updateList = updateList;
	}
	public String getCountryCode() {
		return countryCode;
	}
	public void setCountryCode(String countryCode) {
		this.countryCode = countryCode;
	}
	public String getRegionCode() {
		return regionCode;
	}
	public void setRegionCode(String regionCode) {
		this.regionCode = regionCode;
	}
	public String getStateName() {
		return stateName;
	}
	public void setStateName(String stateName) {
		this.stateName = stateName;
	}
	public String getStatusCode() {
		return statusCode;
	}
	public void setStatusCode(String statusCode) {
		this.statusCode = statusCode;
	}
	public String getTypeName() {
		return typeName;
	}
	public void setTypeName(String typeName) {
		this.typeName = typeName;
	}
	
	public String getLocationCode() {
		return locationCode;
	}
	public void setLocationCode(String locationCode) {
		this.locationCode = locationCode;
	}
	public LocationIndexDTO getCountryregionCodeList() {
		return countryregionCodeList;
	}
	public void setCountryregionCodeList(LocationIndexDTO countryregionCodeList) {
		this.countryregionCodeList = countryregionCodeList;
	}
	public LocationIndexDTO getCountrystateCodeList() {
		return countrystateCodeList;
	}
	public void setCountrystateCodeList(LocationIndexDTO countrystateCodeList) {
		this.countrystateCodeList = countrystateCodeList;
	}
	public String getStatusDescCd() {
		return statusDescCd;
	}
	public void setStatusDescCd(String statusDescCd) {
		this.statusDescCd = statusDescCd;
	}
	public String getCdtvalueTxCd() {
		return cdtvalueTxCd;
	}
	public void setCdtvalueTxCd(String cdtvalueTxCd) {
		this.cdtvalueTxCd = cdtvalueTxCd;
	}
	public String getCurrentDate() {
		return currentDate;
	}
	public void setCurrentDate(String currentDate) {
		this.currentDate = currentDate;
	}
	public String getDistrictCode() {
		return districtCode;
	}
	public void setDistrictCode(String districtCode) {
		this.districtCode = districtCode;
	}
	public String getCurrentDate1() {
		return currentDate1;
	}
	public void setCurrentDate1(String currentDate1) {
		this.currentDate1 = currentDate1;
	}
	public static long getSerialVersionUID() {
		return serialVersionUID;
	}
	
	public String getActionCode() {
		return actionCode;
	}
	public void setActionCode(String actionCode) {
		this.actionCode = actionCode;
	}
	
	public String getLocDate() {
		return locDate;
	}
	public void setLocDate(String locDate) {
		this.locDate = locDate;
	}
	public String getLatestUpdatedBy() {
		return latestUpdatedBy;
	}
	public void setLatestUpdatedBy(String latestUpdatedBy) {
		this.latestUpdatedBy = latestUpdatedBy;
	}
	public String getLocationLatestCode() {
		return locationLatestCode;
	}
	public void setLocationLatestCode(String locationLatestCode) {
		this.locationLatestCode = locationLatestCode;
	}
	
	
}
