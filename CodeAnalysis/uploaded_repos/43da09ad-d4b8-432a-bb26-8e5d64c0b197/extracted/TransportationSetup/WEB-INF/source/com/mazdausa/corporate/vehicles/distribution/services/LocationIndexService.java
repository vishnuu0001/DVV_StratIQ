
package com.mazdausa.corporate.vehicles.distribution.services;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;

import org.apache.log4j.Logger;
import org.apache.struts.util.LabelValueBean;
 
import com.mazdausa.common.multipleresutlset.dao.DTOCreatorHandler;
import com.mazdausa.common.multipleresutlset.dao.GenericDAO;
import com.mazdausa.common.multipleresutlset.dao.GenericDAOHelper;

import com.mazdausa.common.exceptions.DAOException;
import com.mazdausa.common.log.EMDCSLogger;
import com.mazdausa.common.util.ApplicationUtil;
import com.mazdausa.corporate.vehicles.distribution.application.util.CommonUtility;
import com.mazdausa.corporate.vehicles.distribution.application.constants.AppConstant;
import com.mazdausa.corporate.vehicles.distribution.persistence.dto.LocationIndexDTO;
import com.mazdausa.parts.common.util.Log;


public class LocationIndexService{
	private static final Logger LOG = EMDCSLogger.getLogger(LocationIndexService.class.getName());
	private static final String SUCCESS = "SUCCESS"; 
	private static final String FAILUARE = "FAILUARE";
	private static final String SETERROR_RESPONSE = "Error in db. Please contact DB administrator."; 
	private static final String INSIDE_CREATE_DTO = "INSIDE CREATE DTO";
	private static final String CONTEXT = "context";
	List statenamelist=null;
	List typenamelist=null;
	List regioncodelist=null;
	List countrycodelist=null;
	List statuscodelist=null;
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
	
	public LocationIndexDTO getLocationDetails(String userName) throws DAOException {
		
			
			LOG.debug("INSIDE LocationIndexService");
			LocationIndexDTO dto = null;
			GenericDAO<LocationIndexDTO> dao = null;
			try {
				dao = GenericDAOHelper.<LocationIndexDTO> getDAO();
				String procedureName = AppConstant.vds_location_index_view_loading.trim();
				String schema = ApplicationUtil.getDB2MainframeSchemaName();
				DTOCreatorHandler<LocationIndexDTO> handler = new DTOCreatorHandler<LocationIndexDTO>() {
					

					public LocationIndexDTO createDTO(Statement statement,Object[] outputValues) throws DAOException {
						LOG.debug(INSIDE_CREATE_DTO);
						
						try {
							LocationIndexDTO dto = new LocationIndexDTO();
							LocationIndexService service = new LocationIndexService();
							service.createDTO(statement, dto);
							if (outputValues[0] != null) {
								
								dto.setResponseCode(SUCCESS);
							} else {
								
								dto.setResponseCode(FAILUARE);
							
							}if (outputValues[1] != null) {
								dto.setResponse(outputValues[1].toString());
							} else {
								dto.setResponse(SETERROR_RESPONSE);
							}
							return dto;
						} catch (Exception e) {
							//LOG.info(CONTEXT, e);
				            LOG.error("ERROR in getLocationDetails() : "+e.getMessage());

							throw new DAOException(e.getMessage());
						}
					
					}

					

				};

				dto = (LocationIndexDTO) dao.findDTO(schema, procedureName,handler, AppConstant.SP_ACTIONCODE_VIEW_SEARCH,AppConstant.BLANK,AppConstant.BLANK,AppConstant.BLANK,AppConstant.BLANK,AppConstant.BLANK,AppConstant.BLANK,AppConstant.BLANK,AppConstant.BLANK,AppConstant.BLANK,AppConstant.BLANK,AppConstant.BLANK,userName);

				return dto;
			} catch (Exception e) {

				LOG.info(CONTEXT, e);
				throw new DAOException(e.getMessage());
			}
			
		}
		
		
		
		
	

	LocationIndexDTO createDTO(Statement statement,LocationIndexDTO dto) throws Exception {
		
		ResultSet result = null;
		ResultSet result1 = null;
		ResultSet result2 = null;
		ResultSet result3 = null;
		ResultSet result4 = null;
		
		statenamelist=new ArrayList();
		typenamelist=new ArrayList();
		regioncodelist=new ArrayList();
		countrycodelist=new ArrayList();
		statuscodelist=new ArrayList();
		TreeMap countryMap=new TreeMap();
		TreeMap regionMap=new TreeMap();
		TreeMap stateMap=new TreeMap();
		TreeMap typeMap=new TreeMap();
		TreeMap statuseMap=new TreeMap();
		
		try {
			result = statement.getResultSet();
			if (result != null) {
				
				while (result.next()) {
					
					String countryCode = CommonUtility.checkResultValue(result.getString(AppConstant.DB_VW_CNTRY_CD));
					String countryName = CommonUtility.checkResultValue(result.getString(AppConstant.DB_VW_CNTRY_NM));
					countryMap.put(countryName.trim(),countryCode.trim());
//					countrycodelist.add(new LabelValueBean( countryName.trim(),countryCode.trim()));
					
					}
				countrycodelist=ltsCodeValueDropdown(countryMap);
				dto.setCountryCodeList((ArrayList) countrycodelist);
				if(statement.getMoreResults()){
					
					result1 = statement.getResultSet();
					while (result1.next()) {
						
						String regionCode = CommonUtility.checkResultValue(result1.getString(AppConstant.DB_VW_RGN_CD));
						String regionName = CommonUtility.checkResultValue(result1.getString(AppConstant.DB_VW_RGN_NM));
//						regioncodelist.add(new LabelValueBean(regionName.trim(), regionCode.trim()));
						regionMap.put(regionName.trim(),regionCode.trim());
					
						}
					}
				regioncodelist=ltsCodeValueDropdown(regionMap);
				dto.setRegionCodeList((ArrayList) regioncodelist);
					
				if(statement.getMoreResults()){
					
					result2 = statement.getResultSet();
					while (result2.next()) {
						
						String stateCode = CommonUtility.checkResultValue(result2.getString(AppConstant.DB_VW_ST_CD)); 
						String stateName = CommonUtility.checkResultValue(result2.getString(AppConstant.DB_VW_STATE_NM)); 
//						statenamelist.add(new LabelValueBean(stateName.trim(), stateCode.trim()));
						stateMap.put(stateName.trim(),stateCode.trim());
					
						
						}
					}
				statenamelist=ltsCodeValueDropdown(stateMap);
				dto.setStateNameList((ArrayList) statenamelist);
				
				
				if(statement.getMoreResults()){
					
					result3 = statement.getResultSet();
					while (result3.next()) {
						
						String typeCode = CommonUtility.checkResultValue(result3.getString(AppConstant.DB_VW_CDT_VALUE_CD)); 
						String typeName = CommonUtility.checkResultValue(result3.getString(AppConstant.DB_VW_CDT_VALUE_TX));
						typeMap.put(typeName.trim(),typeCode.trim());
//						typenamelist.add(new LabelValueBean(typeName.trim(), typeCode.trim()));
						
						}
					}
				typenamelist=ltsCodeValueDropdown(typeMap);
				dto.setTypeName((ArrayList) typenamelist);
				
				if(statement.getMoreResults()){
					result4 = statement.getResultSet();
					while (result4.next()) {
						
						String statusCode = CommonUtility.checkResultValue(result4.getString(AppConstant.DB_VW_STATUS_CD)); 
						String statusName = CommonUtility.checkResultValue(result4.getString(AppConstant.DB_VW_STATUS_TX)); 
//						statuscodelist.add(new LabelValueBean(statusName.trim(), statusCode.trim()));
						statuseMap.put(statusName.trim(),statusCode.trim());
						
						}
					}
				statuscodelist=ltsCodeValueDropdown(statuseMap);
				dto.setStatusCode((ArrayList) statuscodelist);
		}
			return dto;
		} catch (SQLException e) {
			LOG.info(CONTEXT, e);
			throw new DAOException(e.getMessage());
		} catch (Exception e) {
			LOG.info(CONTEXT, e);
			throw new DAOException(e.getMessage());
		}finally{
			
				CommonUtility comm=new CommonUtility();
				
				
				List<ResultSet> listR = new ArrayList<ResultSet>();
				listR.add(result);
				listR.add(result1);
				listR.add(result2);
				listR.add(result3);
				listR.add(result4);

				comm.closeConnection3(listR, statement, null);
			
		}
		
	}

	

	
	
	public LocationIndexDTO getCountrySearchDetails(String countrySearch, String userName) throws DAOException {
		
		
		LOG.debug("INSIDE getCountrySearchDetails");
		LocationIndexDTO dto = null;
		GenericDAO<LocationIndexDTO> dao = null;
		try {
			dao = GenericDAOHelper.<LocationIndexDTO> getDAO();
			String procedureName = AppConstant.vds_location_index_view_loading.trim();
			String schema = ApplicationUtil.getDB2MainframeSchemaName();
			DTOCreatorHandler<LocationIndexDTO> handler = new DTOCreatorHandler<LocationIndexDTO>() {
				

				public LocationIndexDTO createDTO(Statement statement,Object[] outputValues) throws DAOException {
					LOG.debug(INSIDE_CREATE_DTO);
					
					try {
						LocationIndexDTO dto = new LocationIndexDTO();
						LocationIndexService service = new LocationIndexService();
						service.createDTO1(statement, dto);
						
						if (outputValues[0] != null) {
							
							dto.setResponseCode(SUCCESS);
						} else {
						
							dto.setResponseCode(FAILUARE);
						
						}
						if (outputValues[1] != null) {
							dto.setResponse(outputValues[1].toString());
						} else {
							dto.setResponse(SETERROR_RESPONSE);
						}
						return dto;
					} catch (Exception e) {
						LOG.info(CONTEXT, e);
						throw new DAOException(e.getMessage());
					}
				
				}

				

			};

			dto = (LocationIndexDTO) dao.findDTO(schema, procedureName,handler, AppConstant.SP_ACTIONCODE_VIEW_SEARCH,
					AppConstant.BLANK,
					AppConstant.BLANK,
					AppConstant.BLANK,
					countrySearch,
					AppConstant.BLANK,
					AppConstant.BLANK,
					AppConstant.BLANK,
					AppConstant.BLANK,
					AppConstant.BLANK,
					AppConstant.BLANK,
					userName,
					AppConstant.BLANK);

			return dto;
		} catch (Exception e) {
			LOG.info(CONTEXT, e);
			throw new DAOException(e.getMessage());
		}
		
	}
	
	
	
	


LocationIndexDTO createDTO1(Statement statement,LocationIndexDTO dto) throws Exception {

	ResultSet result = null;
	ResultSet result1 = null;
	ResultSet result2 = null;
	ResultSet result3 = null;
	ResultSet result4 = null;
	
	List stateNameList=new ArrayList();
	List typeNameList=new ArrayList();
	List regionCodeList=new ArrayList();
	List countryCodeList=new ArrayList();
	List statusCodeList=new ArrayList();
	
	try {
		result = statement.getResultSet();
		if (result != null) {
			
			while (result.next()) {
				String countryCode = CommonUtility.checkResultValue(result.getString(AppConstant.DB_VW_CNTRY_CD));
				String countryName = CommonUtility.checkResultValue(result.getString(AppConstant.DB_VW_CNTRY_NM) );
				countryCodeList.add(new LabelValueBean( countryName.trim(),countryCode.trim()));
				}
			dto.setCountryCodeList((ArrayList) countryCodeList);
			
			if(statement.getMoreResults()){
				
				result1 = statement.getResultSet();
				while (result1.next()) {
					
					
					String regionCode = CommonUtility.checkResultValue(result1.getString(AppConstant.DB_VW_RGN_CD).trim()); 
					String regionName = CommonUtility.checkResultValue(result1.getString(AppConstant.DB_VW_RGN_NM).trim()); 
					regionCodeList.add(new LabelValueBean(regionName, regionCode));
				
					}
				}
			dto.setRegionCodeList((ArrayList) regionCodeList);
			
			if(statement.getMoreResults()){
				
				result2 = statement.getResultSet();
				while (result2.next()) {
					
					String stateCode = CommonUtility.checkResultValue(result2.getString(AppConstant.DB_VW_ST_CD).trim()); 

					String stateName = CommonUtility.checkResultValue(result2.getString(AppConstant.DB_VW_STATE_NM).trim()); 
					stateNameList.add(new LabelValueBean(stateName, stateCode));
					
					
					}
				}
			dto.setStateNameList((ArrayList) stateNameList);
			
			if(statement.getMoreResults()){
				
				result3 = statement.getResultSet();
				while (result3.next()) {
					
					
					String typeCode = CommonUtility.checkResultValue(result3.getString(AppConstant.DB_VW_CDT_VALUE_CD).trim()); 
					String typeName = CommonUtility.checkResultValue(result3.getString(AppConstant.DB_VW_CDT_VALUE_TX).trim()); 
					
					typeNameList.add(new LabelValueBean(typeName, typeCode));
					
					}
				}
			dto.setTypeName((ArrayList) typeNameList);
			
			if(statement.getMoreResults()){
				result4 = statement.getResultSet();
				while (result4.next()) {
					
					
					String statusCode = CommonUtility.checkResultValue(result4.getString(AppConstant.DB_VW_STATUS_CD).trim()); 
					statusCodeList.add(new LabelValueBean(statusCode, statusCode));
					
					}
				}
			dto.setStatusCode((ArrayList) statusCodeList);
	}
		return dto;
	} catch (SQLException e) {
		LOG.debug(e);
		throw new DAOException(e.getMessage());
	} catch (Exception e) {
		LOG.debug(e);
		throw new DAOException(e.getMessage());
	}finally{
			CommonUtility comm=new CommonUtility();
			
			List<ResultSet> listR = new ArrayList<ResultSet>();
			listR.add(result);
			listR.add(result1);
			listR.add(result2);
			listR.add(result3);
			listR.add(result4);
			
			comm.closeConnection3(listR, statement, null);
		
	}
	
}

	private String checkResultValue(String str) {
		
		if(str!=null){
			return str;
		}else{
			return str="";
		}
		
		
	}
	
	public static ArrayList ltsCodeValueDropdown(TreeMap carrierHashMap){
		ArrayList objFormattedList = null;
		String codeValue = null;
		String nameValue = null;
		objFormattedList = new ArrayList();
		
		Set set=carrierHashMap.keySet();
		Iterator iterator=set.iterator();
		 while(iterator.hasNext()){
		 	nameValue=(String)iterator.next();
		 	codeValue=(String)carrierHashMap.get(nameValue);
			objFormattedList.add(new LabelValueBean(nameValue, codeValue));
		}
	return objFormattedList;
	}


	
	public LocationIndexDTO getLocationSearchDetails(String locationname,String locationcode,String inputcountry,String inputregion,String inputstate,String locationzipcode,String inputcity,String inputstatuscode,String inputtype,String username) throws DAOException {
		
		LOG.debug("INSIDE getLocationSearchDetails");
		
		this.locationName = locationname!=null ? locationname : "";
		this.locationCode = locationcode!=null ? locationcode : "";
		this.inputCountry = inputcountry!=null ? inputcountry : "";
		this.inputRegion = inputregion!=null ? inputregion : "";
		this.inputState = inputstate!=null ? inputstate : "";
		this.locationZipcode = locationzipcode!=null ? locationzipcode : "";
		this.inputCity = inputcity!=null ? inputcity : "";
		this.inputStatuscode = inputstatuscode!=null ? inputstatuscode : "";
		this.inputType = inputtype!=null ? inputtype : "";
		
		LocationIndexDTO dto = null;
		GenericDAO<LocationIndexDTO> dao = null;
		try {
			dao = GenericDAOHelper.<LocationIndexDTO> getDAO();
			String procedureName = AppConstant.vds_location_index_view_loading.trim();
			String schema = ApplicationUtil.getDB2MainframeSchemaName();
			DTOCreatorHandler<LocationIndexDTO> handler = new DTOCreatorHandler<LocationIndexDTO>() {
				

				public LocationIndexDTO createDTO(Statement statement,Object[] outputValues) throws DAOException {
					LOG.debug(INSIDE_CREATE_DTO);
					
					try {
						LocationIndexDTO dto = new LocationIndexDTO();
						LocationIndexService service = new LocationIndexService();
						dto=service.createDTO2(statement, dto);
						if (outputValues[0] != null) {
							
							dto.setResponseCode(SUCCESS);
						} else {
							
							dto.setResponseCode(FAILUARE);
						
						}if (outputValues[1] != null) {
							dto.setResponse(outputValues[1].toString());
						} else {
							dto.setResponse(SETERROR_RESPONSE);
						}
						return dto;
					} catch (Exception e) {
						//LOG.info(CONTEXT, e);
			            LOG.error("ERROR in getLocationDetails() : "+e.getMessage());

						throw new DAOException(e.getMessage());
					}
				
				}

				

			};

			dto = (LocationIndexDTO) dao.findDTO(schema, procedureName,handler, AppConstant.SP_ACTIONCODE_SEARCH,
					AppConstant.BLANK,
					this.locationName,
					this.locationCode,
					this.inputCountry,
					this.inputRegion,
					this.inputState,
					this.locationZipcode,
					this.inputCity,
					this.inputStatuscode,
					this.inputType,
					username,
					AppConstant.BLANK);

			return dto;
		} catch (Exception e) {

			LOG.info(CONTEXT, e);
			throw new DAOException(e.getMessage());
		}
		
	}
	
	
	
	


LocationIndexDTO createDTO2(Statement statement,LocationIndexDTO dto) throws Exception {
	ResultSet result = null;
	ResultSet result1 = null;
	
	LocationIndexDTO dtoaddresType = new LocationIndexDTO();
	LocationIndexDTO dto1 = new LocationIndexDTO();
	searchList=new ArrayList<LocationIndexDTO>();
	searchMapList=new TreeMap<String, LocationIndexDTO>();
	 Map<String,LocationIndexDTO> typeMapCdList=new LinkedHashMap<String, LocationIndexDTO>();
	 LocationIndexDTO dto2=null;
	 int count=0;
	
	try {
		result = statement.getResultSet();
		if (result != null) {
			
			while (result.next()) {
				
				dto2 = new LocationIndexDTO();
				count++;
//				if(count>=80){
//					break;
//				}
				
				String transactionId =  result.getString(AppConstant.DB_LOCTN_CD);	
				
					if( searchMapList.containsKey(transactionId) ) {
						dto2 = (LocationIndexDTO)searchMapList.get(transactionId);
						
						String addresstypenm = CommonUtility.checkResultValue(result.getString(AppConstant.DB_ADDR_TYPE_NM));
						dto2.setAddressTypeNm(addresstypenm.trim());
						
						if(addresstypenm.equals("SHIPPING")){
							
							String shippingstreetaddress1 = CommonUtility.checkResultValue(result.getString(AppConstant.DB_STR1_AD).trim());
							dto2.setShippingstreetaddress1(shippingstreetaddress1.trim()); 
							
							
							String shippingstreetaddress2 =CommonUtility.checkResultValue( result.getString(AppConstant.DB_STR2_AD).trim());
							dto2.setShippingstreetaddress2(shippingstreetaddress2.trim()); 
							
							
							String shippingstreetaddress3 = CommonUtility.checkResultValue(result.getString(AppConstant.DB_STR3_AD).trim());
							dto2.setShippingstreetaddress3(shippingstreetaddress3.trim()); 
							
						
							String shippingcityname = CommonUtility.checkResultValue(result.getString(AppConstant.DB_CITY_NM));
							dto2.setShippingcityname(shippingcityname.trim()); 
							
						
							String shippingstatecode = CommonUtility.checkResultValue(result.getString(AppConstant.DB_ST_CD));
							dto2.setShippingstatecode(shippingstatecode.trim()); 
							
							
							
							String shippingzipcode = CommonUtility.checkResultValue(result.getString(AppConstant.DB_ZIP_CD));
							dto2.setShippingzipcode(shippingzipcode.trim()); 
							
							
							String shippingcountrycode = CommonUtility.checkResultValue(result.getString(AppConstant.DB_CNTRY_CD));
							dto2.setShippingcountrycode(shippingcountrycode.trim()); 
							
						
							String shippingcountrynm = CommonUtility.checkResultValue(result.getString(AppConstant.DB_CNTRY_NM));
							dto2.setShippingcountrynm(shippingcountrynm.trim()); 	
							
						}
						
						searchMapList.put(result.getString(AppConstant.DB_LOCTN_CD), dto2);
						Collection<LocationIndexDTO> valuesList = searchMapList.values();
						searchList=new ArrayList<LocationIndexDTO>(valuesList);
						}else{
							String addresstypenm = CommonUtility.checkResultValue(result.getString(AppConstant.DB_ADDR_TYPE_NM));
							dto2.setAddressTypeNm(addresstypenm.trim());
							if(addresstypenm.equals("SHIPPING")){
								
								String shippingstreetaddress1 = CommonUtility.checkResultValue(result.getString(AppConstant.DB_STR1_AD).trim());
								dto2.setShippingstreetaddress1(shippingstreetaddress1.trim()); 
								
								
								String shippingstreetaddress2 =CommonUtility.checkResultValue( result.getString(AppConstant.DB_STR2_AD).trim());
								dto2.setShippingstreetaddress2(shippingstreetaddress2.trim()); 
								
								
								String shippingstreetaddress3 = CommonUtility.checkResultValue(result.getString(AppConstant.DB_STR3_AD).trim());
								dto2.setShippingstreetaddress3(shippingstreetaddress3.trim()); 
								
							
								String shippingcityname = CommonUtility.checkResultValue(result.getString(AppConstant.DB_CITY_NM));
								dto2.setShippingcityname(shippingcityname.trim()); 
								
							
								String shippingstatecode = CommonUtility.checkResultValue(result.getString(AppConstant.DB_ST_CD));
								dto2.setShippingstatecode(shippingstatecode.trim()); 
								
								
								
								String shippingzipcode = CommonUtility.checkResultValue(result.getString(AppConstant.DB_ZIP_CD));
								dto2.setShippingzipcode(shippingzipcode.trim()); 
								
								
								String shippingcountrycode = CommonUtility.checkResultValue(result.getString(AppConstant.DB_CNTRY_CD));
								dto2.setShippingcountrycode(shippingcountrycode.trim()); 
								
							
								String shippingcountrynm = CommonUtility.checkResultValue(result.getString(AppConstant.DB_CNTRY_NM));
								dto2.setShippingcountrynm(shippingcountrynm.trim()); 	
								
							}
						String currlocationcode = CommonUtility.checkResultValue(result.getString(AppConstant.DB_LOCTN_CD));
						dto2.setCurrentLocationCode(currlocationcode.trim()); 	
						
						
						String locationname = CommonUtility.checkResultValue(result.getString(AppConstant.DB_LOCTN_NM));
						dto2.setLocationName(locationname.trim()); 
						
					
						String streetaddress1 = CommonUtility.checkResultValue(result.getString(AppConstant.DB_STR1_AD).trim());
						dto2.setStreetAddress1(streetaddress1.trim()); 
						
						
						String streetaddress2 =CommonUtility.checkResultValue( result.getString(AppConstant.DB_STR2_AD).trim());
						dto2.setStreetAddress2(streetaddress2.trim()); 
						
						
						String streetaddress3 = CommonUtility.checkResultValue(result.getString(AppConstant.DB_STR3_AD).trim());
						dto2.setStreetAddress3(streetaddress3.trim()); 
						
					
						String cityname = CommonUtility.checkResultValue(result.getString(AppConstant.DB_CITY_NM));
						dto2.setCityName(cityname.trim()); 
						
					
						String statecode = CommonUtility.checkResultValue(result.getString(AppConstant.DB_ST_CD));
						dto2.setStateCode(statecode.trim()); 
						
						
						
						String zipcode = CommonUtility.checkResultValue(result.getString(AppConstant.DB_ZIP_CD));
						dto2.setZipCode(zipcode.trim()); 
						
						
						String countrycode = CommonUtility.checkResultValue(result.getString(AppConstant.DB_CNTRY_CD));
						dto2.setCountryCd(countrycode.trim()); 
						
					
						String countrynm = CommonUtility.checkResultValue(result.getString(AppConstant.DB_CNTRY_NM));
						dto2.setCountryNm(countrynm.trim()); 
						
					
						String phnacno = CommonUtility.checkResultValue(result.getString(AppConstant.DB_PHNAC_NO));
						dto2.setPhoneAcNo(phnacno.trim()); 
						
					
						String phnexcno = CommonUtility.checkResultValue(result.getString(AppConstant.DB_PHNEXC_NO));
						dto2.setPhoneExcNo(phnexcno.trim());
						
					
						String phoneno = CommonUtility.checkResultValue(result.getString(AppConstant.DB_PHONE_NO));
						dto2.setPhoneNo(phoneno.trim());
						
						
						String phoneExtnsnNo = CommonUtility.checkResultValue(result.getString(AppConstant.DB_EXTNSN_NO));
						dto2.setPhoneExtnsnNo(phoneExtnsnNo.trim());
						
						
						String faxAcno = CommonUtility.checkResultValue(result.getString(AppConstant.DB_FAXAC_NO));
						dto2.setFaxAcNo(faxAcno.trim()); 
						
					
						String faxexcno = CommonUtility.checkResultValue(result.getString(AppConstant.DB_FAXEXC_NO));
						dto2.setFaxExcNo(faxexcno.trim());
						
					
						String faxno = CommonUtility.checkResultValue(result.getString(AppConstant.DB_FAXPHN_NO));
						dto2.setFaxNo(faxno.trim());
						
						/*String addresstypenm = CommonUtility.checkResultValue(result.getString(AppConstant.DB_ADDR_TYPE_NM));
						dto2.setAddressTypeNm(addresstypenm.trim());
						*/
						
						String statusdesc = CommonUtility.checkResultValue(result.getString(AppConstant.DB_STATUS_DESC));
						dto2.setStatusDesc(statusdesc.trim());
						
						
						String statuscd = CommonUtility.checkResultValue(result.getString(AppConstant.DB_STATUS_CD));
						dto2.setStatusCdSearch(statuscd.trim());
						
						
						String regioncd = CommonUtility.checkResultValue(result.getString(AppConstant.DB_RGN_CD));
						dto2.setRegionCd(regioncd.trim());
						
					
						String lastupdatetime = CommonUtility.checkResultValue(result.getString(AppConstant.DB_LAST_UPDT_TM));
						dto2.setLastUpdateTime(lastupdatetime.trim());
						
					
						String lastuseridcd = CommonUtility.checkResultValue(result.getString(AppConstant.DB_LAST_USERID_CD) );
						dto2.setLastUserIdCd(lastuseridcd.trim());
						
						
						String statusdate = CommonUtility.checkResultValue(result.getString(AppConstant.DB_STATUS_DT));
						dto2.setStatusDate(statusdate.trim());
						
						String firstName = CommonUtility.checkResultValue(result.getString(AppConstant.DB_CONTC_FRST_NM));
						dto2.setFirstName(firstName.trim());
						
						String lastName = CommonUtility.checkResultValue(result.getString(AppConstant.DB_CONTC_LAST_NM));
						dto2.setLastName(lastName.trim());
						
						String contactTitle = CommonUtility.checkResultValue(result.getString(AppConstant.DB_CONTC_TITLE_TX));
						dto2.setContactTitle(contactTitle.trim());
						
						String districtCode = CommonUtility.checkResultValue(result.getString(AppConstant.DB_DSTRCT_CD)!=null ? (result.getString(AppConstant.DB_DSTRCT_CD)):"");
						dto2.setDistrictCode(districtCode.trim());
						
						String cdtvaluetx = CommonUtility.checkResultValue(result.getString(AppConstant.DB_CDT_VALUE_TX) !=null ? (result.getString(AppConstant.DB_CDT_VALUE_TX)):"".trim());
						String cdtvaluecd = CommonUtility.checkResultValue(result.getString(AppConstant.DB_CDT_VALUE_CD) !=null ? (result.getString(AppConstant.DB_CDT_VALUE_CD)):"".trim() );
						dtoaddresType=new LocationIndexDTO();
						dtoaddresType.setCdtvalueCd(cdtvaluecd);
						dtoaddresType.setCdtvalueTx(cdtvaluetx);
						
						String cdtValueTx2 = CommonUtility.checkResultValue(result.getString(AppConstant.DB_CDT_VALUE_TX2) !=null ? (result.getString(AppConstant.DB_CDT_VALUE_TX2)):"".trim() );
						String cdtValueCd2 = CommonUtility.checkResultValue(result.getString(AppConstant.DB_CDT_TYPE_2_CD) !=null ? (result.getString(AppConstant.DB_CDT_TYPE_2_CD)):"".trim());

						dtoaddresType.setCdtvalueCd2(cdtValueCd2);
						dtoaddresType.setCdtvalueTx2(cdtValueTx2);

						String cdtValueTx3 = CommonUtility.checkResultValue(result.getString(AppConstant.DB_CDT_VALUE_TX3)!=null ? (result.getString(AppConstant.DB_CDT_VALUE_TX3)):"".trim());
						String cdtValueCd3 = CommonUtility.checkResultValue(result.getString(AppConstant.DB_TYPE_3_CD)!=null ? (result.getString(AppConstant.DB_TYPE_3_CD)) :"".trim());

						dtoaddresType.setCdtvalueCd3(cdtValueCd3);
						dtoaddresType.setCdtvalueTx3(cdtValueTx3);

						typeMapCdList.put(transactionId, dtoaddresType);
						dto2.setCdtvalueCd(dtoaddresType.getCdtvalueCd());
						dto2.setCdtvalueTx(dtoaddresType.getCdtvalueTx());
						
						dto2.setCdtvalueCd2(dtoaddresType.getCdtvalueCd2());
						dto2.setCdtvalueTx2(dtoaddresType.getCdtvalueTx2());
						
						dto2.setCdtvalueCd3(dtoaddresType.getCdtvalueCd3());
						dto2.setCdtvalueTx3(dtoaddresType.getCdtvalueTx3());
						
						searchMapList.put(result.getString(AppConstant.DB_LOCTN_CD), dto2);
						}
//					count++;
//					if(count>80){
//						break;
//					}

				
			}
			
			if(statement.getMoreResults()){
				
				result1 = statement.getResultSet();
				while (result1.next()) {
					
					String transactionId =  result1.getString(AppConstant.DB_LOCTN_CD);	
					
					if( searchMapList.containsKey(transactionId) ) {
						
					dto2 = (LocationIndexDTO)searchMapList.get(transactionId);
					
					String EMAIL_ID = CommonUtility.checkResultValue(result1.getString(AppConstant.DB_EMAIL_ID)!=null ? (result1.getString(AppConstant.DB_EMAIL_ID)):"");
					dto2.setEmailId(EMAIL_ID.trim());
					
					String CELL_NO1 = CommonUtility.checkResultValue(result1.getString(AppConstant.DB_CELL_NO1)!=null ? (result1.getString(AppConstant.DB_CELL_NO1)):"");
					dto2.setCellNo1(CELL_NO1.trim());
					
					String CELL_NO2 = CommonUtility.checkResultValue(result1.getString(AppConstant.DB_CELL_NO2)!=null ? (result1.getString(AppConstant.DB_CELL_NO2)):"");
					dto2.setCellNo2(CELL_NO2.trim());
					
					String CELL_NO3 = CommonUtility.checkResultValue(result1.getString(AppConstant.DB_CELL_NO3)!=null ? (result1.getString(AppConstant.DB_CELL_NO3)):"");
					dto2.setCellNo3(CELL_NO3.trim());
					
					searchMapList.put(result1.getString(AppConstant.DB_LOCTN_CD), dto2);
					
					}
					
					
				
					}
				
				}
			
			Collection<LocationIndexDTO> valuesList = searchMapList.values();
			searchList=new ArrayList<LocationIndexDTO>(valuesList);
			dto1.setSearchList((ArrayList<LocationIndexDTO>) searchList);
	}
		return dto1;
	} catch (SQLException e) {
		LOG.info(CONTEXT, e);
		e.printStackTrace();
		throw new DAOException(e.getMessage());
	} catch (Exception e) {
		LOG.info(CONTEXT, e);
		e.printStackTrace();
		throw new DAOException(e.getMessage());
	}finally{
		
			CommonUtility comm=new CommonUtility();
			
			
			List<ResultSet> listR = new ArrayList<ResultSet>();
			listR.add(result);
			listR.add(result1);

			comm.closeConnection3(listR, statement, null);
		
	}
	
}
}
