/**
 * This is the CommonUtility.java
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
package com.mazdausa.corporate.vehicles.distribution.application.util;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.Statement;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.List;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpSession;

import org.apache.log4j.Logger;

import com.mazdausa.common.application.actions.helpers.DealerCollectionViewHelper;
import com.mazdausa.common.log.EMDCSLogger;
import com.mazdausa.common.user.model.User;
import com.mazdausa.common.util.ApplicationUtil;
import com.mazdausa.corporate.vehicles.distribution.application.constants.AppConstant;
import com.mazdausa.corporate.vehicles.distribution.persistence.dataObject.SessionUser;
import com.mazdausa.vds.security.SecurityUtility;
//import com.mazdausa.common.jmsinterface.EmazdaJMSServiceFactory;
//import com.mazdausa.common.jmsinterface.MazdaCommonJMSService;
//import com.mazdausa.corporate.vehicles.distribution.application.constants.AppConstants;
//import com.mazdausa.corporate.vehicles.distribution.persistence.dataObject.CountryDO;
//import com.mazdausa.corporate.vehicles.distribution.persistence.dataObject.SessionDO;
//import com.mazdausa.corporate.vehicles.distribution.services.CommmonService;
/**
 * @author TechM
 *
 */
	public class CommonUtility {
		private static Logger log = EMDCSLogger.getLogger(CommonUtility.class);
		
		public static boolean hasPermission(SessionUser objUser,String uri){
			boolean bPermission=false;
			//if(!objUser.getRole().equalsIgnoreCase("region")){
				/*if(uri.indexOf("VehicleManualAssignment.do") != -1)
					bPermission=false;
				else*/
					bPermission=true;
			//}
			return bPermission;
		}
		
		public static SessionUser getUserDetails(HttpServletRequest request){
			SessionUser objSessionUser=new SessionUser(); 
			String userId = ApplicationUtil.getSystemProperty(AppConstant.FLEET_PROPERTY_SCHEMA, "debug.username");
		      if(!isDebug()) {
		            // get the user from the session
		            DealerCollectionViewHelper helper = (DealerCollectionViewHelper)request.getSession().getAttribute("UserInfoBean");
		            if(helper != null) {
		            	  userId = helper.getUserContext().getUserId();
		                  User user = helper.getUserContext().getUser();
		                  log.info("USER TITLE:"+user.getTitle());
		                  log.info("USER TYPE1:"+user.getType1Cd());
		                  log.info("USER TYPE2:"+user.getType1Cd());
		                  log.info("USER TYPE3:"+user.getType1Cd());
		                  
		                  if(user.isRegionalPerson()){
		                	  objSessionUser.setRegion(user.getRgnCd());
		        	    	  objSessionUser.setRole("region");
		                  }else if(user.isDealerPerson()){
		                	  objSessionUser.setRegion(user.getRgnCd());
		        	    	  objSessionUser.setRole("delear");
		                  }else{
		                	  objSessionUser.setRegion(user.getRgnCd());
		        	    	  objSessionUser.setRole("corporate");
		                  }
		                  
		                  objSessionUser.setUsername(userId);
		                  objSessionUser.setCountryCd(user.getCountryCd());
		                  
		            }
		      }else{
		    	  objSessionUser.setUsername(userId);
//		    	  objSessionUser.setCountryCd(CommonUtility.getCountryCode(request));
		    	  objSessionUser.setRole(ApplicationUtil.getSystemProperty(AppConstant.FLEET_PROPERTY_SCHEMA , "debug.user.role"));
		    	  objSessionUser.setRegion("GU");
		    	  
		      }
		      
		      return objSessionUser;
		}
		
		public static String getUserType(HttpServletRequest request){
			String userType="R"; 
			if(!isDebug()) {
		            // get the user from the session
		            DealerCollectionViewHelper helper = (DealerCollectionViewHelper)request.getSession().getAttribute("UserInfoBean");
		            if(helper != null) {
		            	 User user = helper.getUserContext().getUser();
		                  log.info("USER TITLE:"+user.getTitle());
		                  log.info("USER TYPE1:"+user.getType1Cd());
		                  log.info("USER TYPE2:"+user.getType1Cd());
		                  log.info("USER TYPE3:"+user.getType1Cd());
		                  
		                  if(user.isCorporatePerson()){
		                	  userType="C";
		                  }else if(user.isRegionalPerson()){
		                	  userType="R";
		                  }else if(user.isDealerPerson()){
		                	  userType="D";
		                  }else if(user.isDistrictPerson()){
		                	  userType="DS";
//		                  }else if(user.isPortPerson()){
//		                	  userType="P";
		                  }
		                
		            }
		      }
		      
		      return userType;
		}
		public static String getUserRegion(HttpServletRequest request){
			String userRegion="GU"; 
			if(!isDebug()) {
		            // get the user from the session
		            DealerCollectionViewHelper helper = (DealerCollectionViewHelper)request.getSession().getAttribute("UserInfoBean");
		            if(helper != null) {
		            	 User user = helper.getUserContext().getUser();
		            	 userRegion= user.getRgnCd();
		                
		            }
		      }
		      
		      return userRegion;
		}
		
		public static String getUser(HttpServletRequest request) {
		      String userId = ApplicationUtil.getSystemProperty(AppConstant.FLEET_PROPERTY_SCHEMA , "debug.username");
		      if(!isDebug()) {
		            // get the user from the session
		            DealerCollectionViewHelper helper = (DealerCollectionViewHelper)request.getSession().getAttribute("UserInfoBean");
		            if(helper != null) {
		                  userId = helper.getUserContext().getUserId();
		                 // helper.getUserContext().getUser().
		                  
		            }
		      }
		      return userId;
		}
		
	
		
		public static String getUserCountryCode(HttpServletRequest request){
			String countryCode = ApplicationUtil.getSystemProperty(AppConstant.FLEET_PROPERTY_SCHEMA , "debug.country.code");
			 if(!isDebug()) {
		            // get the user from the session
		            DealerCollectionViewHelper helper = (DealerCollectionViewHelper)request.getSession().getAttribute("UserInfoBean");
		            if(helper != null) {
					countryCode = helper.getUserContext().getUser().getCountryCd();
		                  
		            }
		      }
		      return countryCode;
		}
		public static boolean isDebug() {
		      return Boolean.parseBoolean(ApplicationUtil.getSystemProperty(AppConstant.FLEET_PROPERTY_SCHEMA, "debug.mode"));
		}
		
		
		
		public static boolean hasAccessibleScreens(HttpServletRequest request) {
			List<String> accessibleScreens = (List<String>)request.getSession().getAttribute(AppConstant.ACCESSIBLE_SCREEN);
			
			if(accessibleScreens == null || accessibleScreens.size() == 0) {
				return false;
			}
			
			if(accessibleScreens != null && accessibleScreens.size() == 1 && "HI".equalsIgnoreCase(accessibleScreens.get(0))) {
				return false;
			}
			
			return true;
		}
		
		public static boolean isFinancePerson(HttpServletRequest request) {
			List<String> accessibleScreens = (List<String>)request.getSession().getAttribute(AppConstant.ACCESSIBLE_SCREEN);
			
			if(accessibleScreens == null || accessibleScreens.size() == 0) {
				return false;
			}
			
			if(accessibleScreens != null && (accessibleScreens.contains("HL") || accessibleScreens.contains("Q1") || accessibleScreens.contains("6A"))) {
				return true;
			}
			
			return false;
		}
		
		
		public static String padRight(String str, int size, String padChar)
		{
			  StringBuffer padded = new StringBuffer(str);
			  while (padded.length() < size){
			    padded.append(padChar);
			  }
			  return padded.toString();
		}
		public static String padLeft(String str, int size, String padChar)
		{
			  String padded = str;
			  while (padded.length() < size){
				  padded = padChar+padded;
			  }
			  return padded;
		}

		public void closeConnection3(List<ResultSet> rsList, Statement stmt, Connection conn) throws Exception
        {
			for(ResultSet rs : rsList){
				 if(rs != null)
		            {
		                try
		                {
		                    rs.close();
		                }
		                catch(Exception e)
		                {
		                    log.error("ERROR CLOSING RESULTSET : "+e,e);
		                }
		            }
			}
			
           
            if(stmt != null)
            {
                try
                {
                    stmt.close();
                }
                catch(Exception e)
                {
                    log.error("ERROR CLOSING STATEMENT : "+e,e);
                }
            }
            if(conn != null)
            {
                try
                {
                    conn.close();
                }
                catch(Exception e)
                {
                    log.error("ERROR CLOSING CONNECTION : "+e,e);
                }
            }        
        }
		
		public static String checkResultValue(String str) {
			
			if(str!=null){
				return str;
			}else{
				return str="";
			}
			
			
		}
		public static String formatDatetoString(String fromFromat, String toformat,String  givenDate){
			String strDate ="";
			try{
			
				if(givenDate!=null){
		    Date date1=new SimpleDateFormat(fromFromat).parse(givenDate);  
		    
		    DateFormat dateFormat = new SimpleDateFormat(toformat);  
		     strDate = dateFormat.format(date1);
				}
			}catch(Exception e){
				
			}
			return strDate;
			
		}

		public void restrictAccess(HttpServletRequest request){
			HttpSession httpSession = request.getSession();
			 httpSession = request.getSession();
			 String[] userGroups = SecurityUtility.getUserWslGroups(request);
			 //String[] userGroups = {"corp_vds_distribution","corp_vds_distribution_mgmt","ltsadmin","corp_vds_allocation","corp_vds_finance","corp_vds_mexico_distribution","corp_vds_fleet"};
				//String[] userGroups = {"corp_vds_distribution","corp_vds_distribution_mgmt","ltsinquiry","corp_vds_allocation","corp_vds_finance","corp_vds_mexico_distribution","corp_vds_fleet"};

			 List<String> userGroupsList=new ArrayList<String>(Arrays.asList(userGroups));
			 if(userGroupsList.contains("ltsadmin")){
				 httpSession.setAttribute(AppConstant.LTS_USER_PRIVILEGE, "ltsadmin");
			 }else  if(userGroupsList.contains("ltsinquiry")){
				 httpSession.setAttribute(AppConstant.LTS_USER_PRIVILEGE, "ltsinquiry");
			 }else {
				 httpSession.setAttribute(AppConstant.LTS_USER_PRIVILEGE, "no");
			 }
//	         String userStatus = (String) httpSession
//	                 .getAttribute(AppConstant.LTS_USER_PRIVILEGE);
//	         if (userStatus != null) {
//	             objLocationIndexForm.setUserPrivilege(userStatus);
//	         }
	         
			
		}
	
}
