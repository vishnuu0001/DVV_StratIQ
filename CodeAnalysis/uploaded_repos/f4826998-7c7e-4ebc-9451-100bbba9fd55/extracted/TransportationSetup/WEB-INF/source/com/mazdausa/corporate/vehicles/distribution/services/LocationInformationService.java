package com.mazdausa.corporate.vehicles.distribution.services;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

import org.apache.log4j.Logger;

import com.mazdausa.common.dao.DTOCreatorHandler;
import com.mazdausa.common.dao.GenericDAO;
import com.mazdausa.common.dao.GenericDAOHelper;
import com.mazdausa.common.exceptions.DAOException;
import com.mazdausa.common.log.EMDCSLogger;
import com.mazdausa.common.util.ApplicationUtil;
import com.mazdausa.corporate.vehicles.distribution.application.constants.AppConstant;
import com.mazdausa.corporate.vehicles.distribution.application.util.CommonUtility;
import com.mazdausa.corporate.vehicles.distribution.persistence.dto.LocationIndexDTO;

public class LocationInformationService {
	
	private static final Logger LOG = EMDCSLogger.getLogger(LocationInformationService.class);
	private static final String SETERROR_RESPONSE = "Error in db. Please contact DB administrator."; 
	private String locationName;
	private String locationCode;
	private String inputCountry;
	private String inputRegion;
	private String inputState;
	private String locationZipcode;
	private String inputCity;
	private String inputStatuscode;
	private String inputType;
	private List<LocationIndexDTO> searchList=null;
	private Map<String,LocationIndexDTO> searchMapList=null;
	private List<LocationIndexDTO>updateList=null;
	private List<LocationIndexDTO> searchCountryList;
	private static final String CONTEXT = "context";
public LocationIndexDTO getSearchDetails(String locationname,String locationcode,String inputcountry,String inputregion,String inputstate,String locationzipcode,String inputcity,String inputstatuscode,String inputtype,String username) throws DAOException {
		
		LOG.debug("Inside getSearchDetails method");
		LocationIndexDTO dto = new LocationIndexDTO();		
		GenericDAO<LocationIndexDTO> dao = null;
		
		this.locationName = locationname!=null ? locationname : "";
		this.locationCode = locationcode!=null ? locationcode : "";
		this.inputCountry = inputcountry!=null ? inputcountry : "";
		this.inputRegion = inputregion!=null ? inputregion : "";
		this.inputState = inputstate!=null ? inputstate : "";
		this.locationZipcode = locationzipcode!=null ? locationzipcode : "";
		this.inputCity = inputcity!=null ? inputcity : "";
		this.inputStatuscode = inputstatuscode!=null ? inputstatuscode : "";
		this.inputType = inputtype!=null ? inputtype : "";
		
		try {
			String procedureName = ApplicationUtil.getSystemProperty(AppConstant.TransportationSetup, AppConstant.SP_LOCATIONDETAILS);
			dao = GenericDAOHelper.<LocationIndexDTO> getDAO();
			dto = (LocationIndexDTO) dao.findDTO(procedureName, new DTOCreatorHandler<LocationIndexDTO>() {
				public LocationIndexDTO createDTO(ResultSet result, Object[] outputValues) throws DAOException{
					LocationIndexDTO dto = new LocationIndexDTO();
					LocationIndexDTO dtoaddresType = new LocationIndexDTO();
					LocationIndexDTO dto1 = new LocationIndexDTO();
					searchList=new ArrayList<LocationIndexDTO>();
					searchMapList=new TreeMap<String, LocationIndexDTO>();
					 Map<String,String> typeMapList=new LinkedHashMap<String, String>();
					 Map<String,LocationIndexDTO> typeMapCdList=new LinkedHashMap<String, LocationIndexDTO>();
					 Map<String,String> typeMapValueCdList=new LinkedHashMap<String, String>();
					int count=0;
						if (result != null) {
							try {
								while (result.next()) {

								dto = new LocationIndexDTO();
//								if(count>100){
//								break;
//								}
//								count++;
								
								String transactionId =  result.getString(AppConstant.DB_LOCTN_CD);	
								
									if( searchMapList.containsKey(transactionId) ) {
										dto = (LocationIndexDTO)searchMapList.get(transactionId);
										
										String addresstypenm = CommonUtility.checkResultValue(result.getString(AppConstant.DB_ADDR_TYPE_NM));
										dto.setAddressTypeNm(addresstypenm.trim());
										
									
										String shippingstreetaddress1 = CommonUtility.checkResultValue(result.getString(AppConstant.DB_STR1_AD).trim());
										dto.setShippingstreetaddress1(shippingstreetaddress1.trim()); 
										
										
										String shippingstreetaddress2 =CommonUtility.checkResultValue( result.getString(AppConstant.DB_STR2_AD).trim());
										dto.setShippingstreetaddress2(shippingstreetaddress2.trim()); 
										
										
										String shippingstreetaddress3 = CommonUtility.checkResultValue(result.getString(AppConstant.DB_STR3_AD).trim());
										dto.setShippingstreetaddress3(shippingstreetaddress3.trim()); 
										
									
										String shippingcityname = CommonUtility.checkResultValue(result.getString(AppConstant.DB_CITY_NM));
										dto.setShippingcityname(shippingcityname.trim()); 
										
									
										String shippingstatecode = CommonUtility.checkResultValue(result.getString(AppConstant.DB_ST_CD));
										dto.setShippingstatecode(shippingstatecode.trim()); 
										
										
										
										String shippingzipcode = CommonUtility.checkResultValue(result.getString(AppConstant.DB_ZIP_CD));
										dto.setShippingzipcode(shippingzipcode.trim()); 
										
										
										String shippingcountrycode = CommonUtility.checkResultValue(result.getString(AppConstant.DB_CNTRY_CD));
										dto.setShippingcountrycode(shippingcountrycode.trim()); 
										
									
										String shippingcountrynm = CommonUtility.checkResultValue(result.getString(AppConstant.DB_CNTRY_NM));
										dto.setShippingcountrynm(shippingcountrynm.trim()); 
										
										if( typeMapCdList.containsKey(transactionId) ) {										
											dtoaddresType=typeMapCdList.get(transactionId);
											String cdtvaluetx = CommonUtility.checkResultValue(result.getString(AppConstant.DB_CDT_VALUE_TX).trim());
											String cdtvaluecd = CommonUtility.checkResultValue(result.getString(AppConstant.DB_CDT_VALUE_CD).trim());
											dtoaddresType.setCdtvalueCd(dtoaddresType.getCdtvalueCd()+","+cdtvaluecd);
											dtoaddresType.setCdtvalueTx(dtoaddresType.getCdtvalueTx()+","+cdtvaluetx);
											typeMapList=new LinkedHashMap<String, String>();
											String[] arr = dtoaddresType.getCdtvalueTx().split(",");
											for(int i=0;i<arr.length;i++){
											typeMapList.put(arr[i].trim(), arr[i].trim());
											}
											dtoaddresType.setCdtvalueTx(typeMapList.values().toString().replace("[","").replace("]",""));
											typeMapList=new LinkedHashMap<String, String>();
												arr = dtoaddresType.getCdtvalueCd().split(",");
											for(int i=0;i<arr.length;i++){
												typeMapList.put(arr[i].trim(), arr[i].trim());
											}
											dtoaddresType.setCdtvalueCd(typeMapList.values().toString().replace("[","").replace("]",""));
											
											dto.setCdtvalueCd(dtoaddresType.getCdtvalueCd());
											dto.setCdtvalueTx(dtoaddresType.getCdtvalueTx());
											typeMapCdList.put(transactionId, dtoaddresType);
										}else{
											String cdtvaluetx = CommonUtility.checkResultValue(result.getString(AppConstant.DB_CDT_VALUE_TX).trim());
											String cdtvaluecd = CommonUtility.checkResultValue(result.getString(AppConstant.DB_CDT_VALUE_CD).trim());
											dtoaddresType=new LocationIndexDTO();
											dtoaddresType.setCdtvalueCd(cdtvaluecd);
											dtoaddresType.setCdtvalueTx(cdtvaluetx);
											dto.setCdtvalueCd(dtoaddresType.getCdtvalueCd());
											dto.setCdtvalueTx(dtoaddresType.getCdtvalueTx());
											typeMapCdList.put(transactionId, dtoaddresType);
										}
										searchMapList.put(result.getString(AppConstant.DB_LOCTN_CD), dto);
										Collection<LocationIndexDTO> valuesList = searchMapList.values();
										searchList=new ArrayList<LocationIndexDTO>(valuesList);
										}else{
										String currlocationcode = CommonUtility.checkResultValue(result.getString(AppConstant.DB_LOCTN_CD));
										dto.setCurrentLocationCode(currlocationcode.trim()); 	
										
										
										String locationname = CommonUtility.checkResultValue(result.getString(AppConstant.DB_LOCTN_NM));
										dto.setLocationName(locationname.trim()); 
										
									
										String streetaddress1 = CommonUtility.checkResultValue(result.getString(AppConstant.DB_STR1_AD).trim());
										dto.setStreetAddress1(streetaddress1.trim()); 
										
										
										String streetaddress2 =CommonUtility.checkResultValue( result.getString(AppConstant.DB_STR2_AD).trim());
										dto.setStreetAddress2(streetaddress2.trim()); 
										
										
										String streetaddress3 = CommonUtility.checkResultValue(result.getString(AppConstant.DB_STR3_AD).trim());
										dto.setStreetAddress3(streetaddress3.trim()); 
										
									
										String cityname = CommonUtility.checkResultValue(result.getString(AppConstant.DB_CITY_NM));
										dto.setCityName(cityname.trim()); 
										
									
										String statecode = CommonUtility.checkResultValue(result.getString(AppConstant.DB_ST_CD));
										dto.setStateCode(statecode.trim()); 
										
										
										
										String zipcode = CommonUtility.checkResultValue(result.getString(AppConstant.DB_ZIP_CD));
										dto.setZipCode(zipcode.trim()); 
										
										
										String countrycode = CommonUtility.checkResultValue(result.getString(AppConstant.DB_CNTRY_CD));
										dto.setCountryCd(countrycode.trim()); 
										
									
										String countrynm = CommonUtility.checkResultValue(result.getString(AppConstant.DB_CNTRY_NM));
										dto.setCountryNm(countrynm.trim()); 
										
									
										String phnacno = CommonUtility.checkResultValue(result.getString(AppConstant.DB_PHNAC_NO));
										dto.setPhoneAcNo(phnacno.trim()); 
										
									
										String phnexcno = CommonUtility.checkResultValue(result.getString(AppConstant.DB_PHNEXC_NO));
										dto.setPhoneExcNo(phnexcno.trim());
										
									
										String phoneno = CommonUtility.checkResultValue(result.getString(AppConstant.DB_PHONE_NO));
										dto.setPhoneNo(phoneno.trim());
										
										
										String phoneExtnsnNo = CommonUtility.checkResultValue(result.getString(AppConstant.DB_EXTNSN_NO));
										dto.setPhoneExtnsnNo(phoneExtnsnNo.trim());
										
										
										String faxAcno = CommonUtility.checkResultValue(result.getString(AppConstant.DB_FAXAC_NO));
										dto.setFaxAcNo(faxAcno.trim()); 
										
									
										String faxexcno = CommonUtility.checkResultValue(result.getString(AppConstant.DB_FAXEXC_NO));
										dto.setFaxExcNo(faxexcno.trim());
										
									
										String faxno = CommonUtility.checkResultValue(result.getString(AppConstant.DB_FAXPHN_NO));
										dto.setFaxNo(faxno.trim());
										
										String addresstypenm = CommonUtility.checkResultValue(result.getString(AppConstant.DB_ADDR_TYPE_NM));
										dto.setAddressTypeNm(addresstypenm.trim());
										
										
										String statusdesc = CommonUtility.checkResultValue(result.getString(AppConstant.DB_STATUS_DESC));
										dto.setStatusDesc(statusdesc.trim());
										
										
										String statuscd = CommonUtility.checkResultValue(result.getString(AppConstant.DB_STATUS_CD));
										dto.setStatusCdSearch(statuscd.trim());
										
										
									
										/*String cdtvaluecd = CommonUtility.checkResultValue(result.getString(AppConstant.DB_CDT_VALUE_CD));
										dto.setCdtvalueCd(cdtvaluecd.trim());
										
										
										
										String cdtvaluetx = CommonUtility.checkResultValue(result.getString(AppConstant.DB_CDT_VALUE_TX));
										dto.setCdtvalueTx(cdtvaluetx.trim());*/
										
										
										String regioncd = CommonUtility.checkResultValue(result.getString(AppConstant.DB_RGN_CD));
										dto.setRegionCd(regioncd.trim());
										
									
										String lastupdatetime = CommonUtility.checkResultValue(result.getString(AppConstant.DB_LAST_UPDT_TM));
										dto.setLastUpdateTime(lastupdatetime.trim());
										
									
										String lastuseridcd = CommonUtility.checkResultValue(result.getString(AppConstant.DB_LAST_USERID_CD) );
										dto.setLastUserIdCd(lastuseridcd.trim());
										
										
										String statusdate = CommonUtility.checkResultValue(result.getString(AppConstant.DB_STATUS_DT));
										dto.setStatusDate(statusdate.trim());
										
										String firstName = CommonUtility.checkResultValue(result.getString(AppConstant.DB_CONTC_FRST_NM));
										dto.setFirstName(firstName.trim());
										
										String lastName = CommonUtility.checkResultValue(result.getString(AppConstant.DB_CONTC_LAST_NM));
										dto.setLastName(lastName.trim());
										
										String contactTitle = CommonUtility.checkResultValue(result.getString(AppConstant.DB_CONTC_TITLE_TX));
										dto.setContactTitle(contactTitle.trim());
										
										String districtCode = CommonUtility.checkResultValue(result.getString(AppConstant.DB_DSTRCT_CD)!=null ? (result.getString(AppConstant.DB_DSTRCT_CD)):"");
										dto.setDistrictCode(districtCode.trim());
										
										String cdtvaluetx = CommonUtility.checkResultValue(result.getString(AppConstant.DB_CDT_VALUE_TX).trim());
										String cdtvaluecd = CommonUtility.checkResultValue(result.getString(AppConstant.DB_CDT_VALUE_CD).trim());
										dtoaddresType=new LocationIndexDTO();
										dtoaddresType.setCdtvalueCd(cdtvaluecd);
										dtoaddresType.setCdtvalueTx(cdtvaluetx);
										typeMapCdList.put(transactionId, dtoaddresType);
										dto.setCdtvalueCd(dtoaddresType.getCdtvalueCd());
										dto.setCdtvalueTx(dtoaddresType.getCdtvalueTx());
										searchMapList.put(result.getString(AppConstant.DB_LOCTN_CD), dto);
										}
								}
								
								Collection<LocationIndexDTO> valuesList = searchMapList.values();
								searchList=new ArrayList<LocationIndexDTO>(valuesList);
								
								
								
							} catch (SQLException e) {
							
								LOG.info(CONTEXT, e);
					            LOG.error("ERROR in getSearchDetails() : "+e.getMessage());

							}
							dto1.setSearchList((ArrayList<LocationIndexDTO>) searchList);
							}
						return dto1;
						
					
				}

				
			},AppConstant.SP_ACTIONCODE_SEARCH,AppConstant.BLANK,this.locationName,this.locationCode,this.inputCountry,this.inputRegion,this.inputState,this.locationZipcode,this.inputCity,this.inputStatuscode,this.inputType, username,AppConstant.BLANK);
			
			if(dto == null){
				throw new DAOException(SETERROR_RESPONSE);
			}
		} catch (DAOException e) {
			LOG.info(CONTEXT, e);
            LOG.error("ERROR in getSearchDetails() : "+e.getMessage());

			throw new DAOException(e.getMessage());
		} catch (SQLException e) {
			LOG.info(CONTEXT, e);
            LOG.error("ERROR in getSearchDetails() : "+e.getMessage());

			throw new DAOException(e.getMessage());
		} catch (Exception e) {
			LOG.info(CONTEXT, e);
            LOG.error("ERROR in getSearchDetails() : "+e.getMessage());

			throw new DAOException(e.getMessage());
		}
		return dto;
		
	}

	

public LocationIndexDTO getCountrySearchDetails(String country,String username) throws DAOException {
		LOG.debug("getCountrySearchDetails");
		LocationIndexDTO dto = new LocationIndexDTO();		
		GenericDAO<LocationIndexDTO> dao = null;
		
		try {
			String procedureName = ApplicationUtil.getSystemProperty(AppConstant.TransportationSetup, AppConstant.SP_LOCATIONDETAILS);
			dao = GenericDAOHelper.<LocationIndexDTO> getDAO();
			dto = (LocationIndexDTO) dao.findDTO(procedureName, new DTOCreatorHandler<LocationIndexDTO>() {
				public LocationIndexDTO createDTO(ResultSet result, Object[] outputValues)throws DAOException {
					LocationIndexDTO dto = new LocationIndexDTO();
					LocationIndexDTO dto1 = new LocationIndexDTO();
					searchCountryList=new ArrayList<LocationIndexDTO>();
					
					try{
						
						if (result != null) {
							while (result.next()) {
				
							
							
							String regioncd = CommonUtility.checkResultValue(result.getString(AppConstant.DB_RGN_CD));
							dto.setRegionCd(regioncd.trim());
							
							
							String statecode = CommonUtility.checkResultValue(result.getString(AppConstant.DB_ST_CD));
							dto.setStateCode(statecode.trim()); 
							
							searchCountryList.add(dto);
							}
							dto1.setCountrySearchList((ArrayList<LocationIndexDTO>) searchCountryList);
							}
						return dto1;
						
					}catch (Exception e) {
						LOG.info(CONTEXT, e);
			            LOG.error("ERROR in getCountrySearchDetails() : "+e.getMessage());

						throw new DAOException(e.getMessage());
					}
				}

				
			},AppConstant.SP_ACTIONCODE_SEARCH,
			AppConstant.BLANK,
			AppConstant.BLANK,
			AppConstant.BLANK,
			country,
			AppConstant.BLANK,
			AppConstant.BLANK,
			AppConstant.BLANK,
			AppConstant.BLANK,
			AppConstant.BLANK,
			AppConstant.BLANK,
			username,
			AppConstant.BLANK);
			
			if(dto == null){
				throw new  DAOException(SETERROR_RESPONSE);
			}
		} catch (DAOException e) {
			LOG.info(CONTEXT, e);
            LOG.error("ERROR in getCountrySearchDetails() : "+e.getMessage());

			throw new DAOException(e.getMessage());
		} catch (SQLException e) {
			LOG.info(CONTEXT, e);
            LOG.error("ERROR in getCountrySearchDetails() : "+e.getMessage());

			throw new DAOException(e.getMessage());
		} catch (Exception e) {
			LOG.info(CONTEXT, e);
            LOG.error("ERROR in getCountrySearchDetails() : "+e.getMessage());

			throw new DAOException(e.getMessage());
		}
		return dto;
		
	}

public LocationIndexDTO updatelocationDetails(StringBuilder inputParam, String userName) throws DAOException {
	
	LOG.debug("Inside updatelocationDetails");
	
	LocationIndexDTO dto = new LocationIndexDTO();		
	GenericDAO<LocationIndexDTO> dao = null;
	
	try {
		String procedureName = ApplicationUtil.getSystemProperty(AppConstant.TransportationSetup, AppConstant.SP_LOCATIONDETAILS);
		dao = GenericDAOHelper.<LocationIndexDTO> getDAO();
		dto = (LocationIndexDTO) dao.findDTO(procedureName, new DTOCreatorHandler<LocationIndexDTO>() {
			public LocationIndexDTO createDTO(ResultSet result, Object[] outputValues)throws DAOException {
				LocationIndexDTO dto = new LocationIndexDTO();
				updateList=new ArrayList<LocationIndexDTO>();
				
				try{
					
					
					String[] responseData =  ((String)outputValues[1]).split(";");
					
					String respMsg = responseData[3];
					
					dto.setResponseCode(responseData[0]);
					dto.setResponse(respMsg);
					dto.setResponseSeqNumber(responseData[4]);
					if(responseData[0].startsWith("E")){
						dto.setResponseCode(AppConstant.ERRORCODE_E100);
						dto.setResponse(respMsg.trim());
					}

					return dto;
				}catch (Exception e) {
					LOG.info(CONTEXT, e);
					throw new DAOException(e.getMessage());
				}
			}

			
		},AppConstant.SP_ACTIONCODE_UPDATE,AppConstant.BLANK,AppConstant.BLANK,AppConstant.BLANK,AppConstant.BLANK,AppConstant.BLANK,AppConstant.BLANK,AppConstant.BLANK,AppConstant.BLANK,AppConstant.BLANK,AppConstant.BLANK,userName,inputParam.toString());
		
		if(dto == null){
            

			throw new DAOException(SETERROR_RESPONSE);
		}
	} catch (DAOException e) {
		LOG.info(CONTEXT, e);
        LOG.error("ERROR in updatelocationDetails() : "+e.getMessage());

		throw new DAOException(e.getMessage());
	} catch (SQLException e) {
		LOG.info(CONTEXT, e);
        LOG.error("ERROR in updatelocationDetails() : "+e.getMessage());

		throw new DAOException(e.getMessage());
	} catch (Exception e) {
		LOG.info(CONTEXT, e);
        LOG.error("ERROR in updatelocationDetails() : "+e.getMessage());

		throw new DAOException(e.getMessage());
	}
	return dto;
	
}


public LocationIndexDTO deletelocationDetails(String locationCode, String userName) throws DAOException {
	LOG.debug("deletelocationDetails");
	LocationIndexDTO dto = new LocationIndexDTO();		
	GenericDAO<LocationIndexDTO> dao = null;
	
	try {
		String procedureName = ApplicationUtil.getSystemProperty(AppConstant.TransportationSetup, AppConstant.SP_LOCATIONDETAILS);
		dao = GenericDAOHelper.<LocationIndexDTO> getDAO();
		dto = (LocationIndexDTO) dao.findDTO(procedureName, new DTOCreatorHandler<LocationIndexDTO>() {
			public LocationIndexDTO createDTO(ResultSet result, Object[] outputValues) throws DAOException{
				LocationIndexDTO dto = new LocationIndexDTO();
				
				try{
					
					String[] responseData =  ((String)outputValues[1]).split(";");
					String respMsg = responseData[3];
					
					dto.setResponseCode(responseData[0]);
					dto.setResponse(respMsg);
					if(responseData[0].startsWith("E")){
						dto.setResponseCode(AppConstant.ERRORCODE_E100);
						dto.setResponse(respMsg.trim());
					}
					
					return dto;
				}catch (Exception e) {
					LOG.info(CONTEXT, e);
		            LOG.error("ERROR in deletelocationDetails() : "+e.getMessage());

					throw new DAOException(e.getMessage());
				}
			}

			
		},AppConstant.SP_ACTIONCODE_DELETE,
		AppConstant.BLANK,
		AppConstant.BLANK,
		locationCode,
		AppConstant.BLANK,
		AppConstant.BLANK,
		AppConstant.BLANK,
		AppConstant.BLANK,
		AppConstant.BLANK,
		AppConstant.BLANK,
		AppConstant.BLANK,
		userName,
		AppConstant.BLANK);
		
		if(dto == null){
			throw new DAOException(SETERROR_RESPONSE);
		}
	} catch (DAOException e) {
		LOG.info(CONTEXT, e);
        LOG.error("ERROR in deletelocationDetails() : "+e.getMessage());

		throw new DAOException(e.getMessage());
	} catch (SQLException e) {
		LOG.info(CONTEXT, e);
        LOG.error("ERROR in deletelocationDetails() : "+e.getMessage());

		throw new DAOException(e.getMessage());
	} catch (Exception e) {
		LOG.info(CONTEXT, e);
        LOG.error("ERROR in deletelocationDetails() : "+e.getMessage());

		throw new DAOException(e.getMessage());
	}
	return dto;
	
}

public LocationIndexDTO savelocationDetails(StringBuilder inputParam, String userName) throws DAOException {
	LOG.debug("savelocationDetails");
	
	LocationIndexDTO dto = new LocationIndexDTO();		
	GenericDAO<LocationIndexDTO> dao = null;
	
	try {
		String procedureName = ApplicationUtil.getSystemProperty(AppConstant.TransportationSetup, AppConstant.SP_LOCATIONDETAILS);
		dao = GenericDAOHelper.<LocationIndexDTO> getDAO();
		dto = (LocationIndexDTO) dao.findDTO(procedureName, new DTOCreatorHandler<LocationIndexDTO>() {
			public LocationIndexDTO createDTO(ResultSet result, Object[] outputValues) throws DAOException{
				LocationIndexDTO dto = new LocationIndexDTO();
				
				try{
					String[] responseData =  ((String)outputValues[1]).split(";");
					String respMsg = responseData[3];
					dto.setResponseCode(responseData[0]);
					dto.setResponse(respMsg);
					dto.setResponseSeqNumber(responseData[4]);
					if(responseData[0].startsWith("E")){
						dto.setResponseCode(AppConstant.ERRORCODE_E100);
						dto.setResponse(respMsg.trim());
					
					}
					
					return dto;
				}catch (Exception e) {
					LOG.info(CONTEXT, e);
		            LOG.error("ERROR in savelocationDetails() : "+e.getMessage());

					throw new DAOException(e.getMessage());
				}
			}

			
		},AppConstant.SP_ACTIONCODE_ADD,AppConstant.BLANK,AppConstant.BLANK,AppConstant.BLANK,AppConstant.BLANK,AppConstant.BLANK,AppConstant.BLANK,AppConstant.BLANK,AppConstant.BLANK,AppConstant.BLANK,AppConstant.BLANK,userName,inputParam.toString());
		
		if(dto == null){
			throw new DAOException(SETERROR_RESPONSE);
		}
	} catch (DAOException e) {
		LOG.info(CONTEXT, e);
        LOG.error("ERROR in savelocationDetails() : "+e.getMessage());

		throw new DAOException(e.getMessage());
	} catch (SQLException e) {
		LOG.info(CONTEXT, e);
        LOG.error("ERROR in savelocationDetails() : "+e.getMessage());

		throw new DAOException(e.getMessage());
	} catch (Exception e) {
		LOG.info(CONTEXT, e);
        LOG.error("ERROR in savelocationDetails() : "+e.getMessage());

		throw new DAOException(e.getMessage());
	}
	return dto;
	
}
	
}