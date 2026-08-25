 
package com.mazdausa.corporate.vehicles.distribution.persistence.dto;

import java.util.ArrayList;
import java.util.List;

public class LocationIndexDTO {
	
	
	private List countryCodeList;
	private List regionCodeList;
	private List stateNameList;
	private List stateCodeList;
	private List statusCodeList;
	private List typeNameList;
	private String responseCode;
	private String response;
	private String responseSeqNumber;

	
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
	private String phoneExtnsnNo;
	
	private String faxAcNo;
	private String faxExcNo;
	private String faxNo;
	
	private String emailId;
	private String cellNo1;
	private String cellNo2;
	private String cellNo3;
	
	private String addressTypeNm;
	private String statusDesc;
	private String statusCdSearch;
	private String cdtvalueCd;
	private String cdtvalueTx;
	
	private String cdtvalueCd2;
	private String cdtvalueTx2;
	private String cdtvalueCd3;
	private String cdtvalueTx3;
	
	private String regionCd;
	private String lastUpdateTime;
	private String lastUserIdCd;
	private String statusDate;
	private String firstName;
	private String lastName;
	private String contactTitle;
	
	private String shippingstreetaddress1;
	private String shippingstreetaddress2;
	private String shippingstreetaddress3;
	private String shippingcityname;
	private String shippingstatecode;
	private String shippingzipcode;
	private String shippingcountrycode;
	private String shippingcountrynm;

	private List<LocationIndexDTO> searchList;
	private List<LocationIndexDTO> updateList;
	private List<LocationIndexDTO> deleteList;
	private List<LocationIndexDTO> saveList;
	private List<LocationIndexDTO> saveCheckList;
	private List<LocationIndexDTO> countrySearchList;
	private String districtCode;
	private String  addressFormatting;
	private String  locationTypeFormatting;

	
	public String getResponseSeqNumber() {
		return responseSeqNumber;
	}
	public void setResponseSeqNumber(String responseSeqNumber) {
		this.responseSeqNumber = responseSeqNumber;
	}
	public List getStateCodeList() {
		return stateCodeList;
	}
	public void setStateCodeList(List stateCodeList) {
		this.stateCodeList = stateCodeList;
	}
	public List getStatusCodeList() {
		return statusCodeList;
	}
	public void setStatusCodeList(List statusCodeList) {
		this.statusCodeList = statusCodeList;
	}
	public List getTypeNameList() {
		return typeNameList;
	}
	public void setTypeNameList(List typeNameList) {
		this.typeNameList = typeNameList;
	}
	public List<LocationIndexDTO> getCountrySearchList() {
		return countrySearchList;
	}
	public void setCountrySearchList(List<LocationIndexDTO> countrySearchList) {
		this.countrySearchList = countrySearchList;
	}
	public List<LocationIndexDTO> getSaveCheckList() {
		return saveCheckList;
	}
	public void setSaveCheckList(List<LocationIndexDTO> saveCheckList) {
		this.saveCheckList = saveCheckList;
	}
	public List<LocationIndexDTO> getUpdateList() {
		return updateList;
	}
	public void setUpdateList(List<LocationIndexDTO> updateList) {
		this.updateList = updateList;
	}
	public List<LocationIndexDTO> getDeleteList() {
		return deleteList;
	}
	public void setDeleteList(List<LocationIndexDTO> deleteList) {
		this.deleteList = deleteList;
	}
	public List<LocationIndexDTO> getSaveList() {
		return saveList;
	}
	public void setSaveList(List<LocationIndexDTO> saveList) {
		this.saveList = saveList;
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
	
	
	public List getCountryCodeList() {
		return countryCodeList;
	}
	public void setCountryCodeList(List countryCode) {
		this.countryCodeList = countryCode;
	}
	public List getRegionCodeList() {
		return regionCodeList;
	}
	public void setRegionCodeList(List regionCode) {
		this.regionCodeList = regionCode;
	}
	public List getStateNameList() {
		return stateNameList;
	}
	public void setStateNameList(List stateName) {
		this.stateNameList = stateName;
	}
	public List getStatusCode() {
		return statusCodeList;
	}
	public void setStatusCode(List statusCode) {
		this.statusCodeList = statusCode;
	}
	public List getTypeName() {
		return typeNameList;
	}
	public void setTypeName(List typeName) {
		this.typeNameList = typeName;
	}
	public String getCurrentLocationCode() {
		return currentLocationCode;
	}
	public void setCurrentLocationCode(String currentLocationCode) {
		this.currentLocationCode = currentLocationCode;
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
	
	public String getResponseCode() {
		return responseCode;
	}
	public void setResponseCode(String responseCode) {
		this.responseCode = responseCode;
	}
	public String getResponse() {
		return response;
	}
	public void setResponse(String response) {
		this.response = response;
	}
	public List<LocationIndexDTO> getSearchList() {
		return searchList;
	}
	public void setSearchList(List<LocationIndexDTO> searchList) {
		this.searchList = searchList;
	}
	public String getLastUpdateTime() {
		return lastUpdateTime;
	}
	public void setLastUpdateTime(String lastUpdateTime) {
		this.lastUpdateTime = lastUpdateTime;
	}
	public String getLastUserIdCd() {
		return lastUserIdCd;
	}
	public void setLastUserIdCd(String lastUserIdCd) {
		this.lastUserIdCd = lastUserIdCd;
	}
	public String getStatusDate() {
		return statusDate;
	}
	public void setStatusDate(String statusDate) {
		this.statusDate = statusDate;
	}

	public String getCdtvalueCd() {
		return cdtvalueCd;
	}
	public void setCdtvalueCd(String cdtvalueCd) {
		this.cdtvalueCd = cdtvalueCd;
	}
	public String getStatusCdSearch() {
		return statusCdSearch;
	}
	public void setStatusCdSearch(String statusCdSearch) {
		this.statusCdSearch = statusCdSearch;
	}
	public String getFirstName() {
		return firstName;
	}
	public void setFirstName(String firstName) {
		this.firstName = firstName;
	}
	public String getLastName() {
		return lastName;
	}
	public void setLastName(String lastName) {
		this.lastName = lastName;
	}
	public String getContactTitle() {
		return contactTitle;
	}
	public void setContactTitle(String contactTitle) {
		this.contactTitle = contactTitle;
	}
	public String getShippingstreetaddress1() {
		return shippingstreetaddress1;
	}
	public void setShippingstreetaddress1(String shippingstreetaddress1) {
		this.shippingstreetaddress1 = shippingstreetaddress1;
	}
	public String getShippingstreetaddress2() {
		return shippingstreetaddress2;
	}
	public void setShippingstreetaddress2(String shippingstreetaddress2) {
		this.shippingstreetaddress2 = shippingstreetaddress2;
	}
	public String getShippingstreetaddress3() {
		return shippingstreetaddress3;
	}
	public void setShippingstreetaddress3(String shippingstreetaddress3) {
		this.shippingstreetaddress3 = shippingstreetaddress3;
	}
	public String getShippingcityname() {
		return shippingcityname;
	}
	public void setShippingcityname(String shippingcityname) {
		this.shippingcityname = shippingcityname;
	}
	public String getShippingstatecode() {
		return shippingstatecode;
	}
	public void setShippingstatecode(String shippingstatecode) {
		this.shippingstatecode = shippingstatecode;
	}
	public String getShippingzipcode() {
		return shippingzipcode;
	}
	public void setShippingzipcode(String shippingzipcode) {
		this.shippingzipcode = shippingzipcode;
	}
	public String getShippingcountrycode() {
		return shippingcountrycode;
	}
	public void setShippingcountrycode(String shippingcountrycode) {
		this.shippingcountrycode = shippingcountrycode;
	}
	public String getShippingcountrynm() {
		return shippingcountrynm;
	}
	public void setShippingcountrynm(String shippingcountrynm) {
		this.shippingcountrynm = shippingcountrynm;
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
	public String getFaxNo() {
		return faxNo;
	}
	public void setFaxNo(String faxNo) {
		this.faxNo = faxNo;
	}
	public String getDistrictCode() {
		return districtCode;
	}
	public void setDistrictCode(String districtCode) {
		this.districtCode = districtCode;
	}
	public String getAddressFormatting() {
		return addressFormatting;
	}
	public void setAddressFormatting(String addressFormatting) {
		this.addressFormatting = addressFormatting;
	}
	public String getPhoneExtnsnNo() {
		return phoneExtnsnNo;
	}
	public void setPhoneExtnsnNo(String phoneExtnsnNo) {
		this.phoneExtnsnNo = phoneExtnsnNo;
	}
	public String getEmailId() {
		return emailId;
	}
	public void setEmailId(String emailId) {
		this.emailId = emailId;
	}
	public String getCellNo1() {
		return cellNo1;
	}
	public void setCellNo1(String cellNo1) {
		this.cellNo1 = cellNo1;
	}
	public String getCellNo2() {
		return cellNo2;
	}
	public void setCellNo2(String cellNo2) {
		this.cellNo2 = cellNo2;
	}
	public String getCellNo3() {
		return cellNo3;
	}
	public void setCellNo3(String cellNo3) {
		this.cellNo3 = cellNo3;
	}
	public String getCdtvalueCd2() {
		return cdtvalueCd2;
	}
	public void setCdtvalueCd2(String cdtvalueCd2) {
		this.cdtvalueCd2 = cdtvalueCd2;
	}
	public String getCdtvalueTx2() {
		return cdtvalueTx2;
	}
	public void setCdtvalueTx2(String cdtvalueTx2) {
		this.cdtvalueTx2 = cdtvalueTx2;
	}
	public String getCdtvalueCd3() {
		return cdtvalueCd3;
	}
	public void setCdtvalueCd3(String cdtvalueCd3) {
		this.cdtvalueCd3 = cdtvalueCd3;
	}
	public String getCdtvalueTx3() {
		return cdtvalueTx3;
	}
	public void setCdtvalueTx3(String cdtvalueTx3) {
		this.cdtvalueTx3 = cdtvalueTx3;
	}
	public String getLocationTypeFormatting() {
		return locationTypeFormatting;
	}
	public void setLocationTypeFormatting(String locationTypeFormatting) {
		this.locationTypeFormatting = locationTypeFormatting;
	}
		
}
