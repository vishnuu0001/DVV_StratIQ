/**
 * This is the VDSActionAbstract.java
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

/**
 * @author TechM
 *
 */
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

import org.apache.log4j.Logger;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;

import com.mazdausa.common.application.actions.EmazdaActionAbstract;
import com.mazdausa.common.application.actions.UserContext;
import com.mazdausa.common.application.actions.helpers.DealerCollectionViewHelper;
import com.mazdausa.common.log.EMDCSLogger;
import com.mazdausa.corporate.vehicles.distribution.application.util.CommonUtility;
import com.mazdausa.corporate.vehicles.distribution.persistence.dataObject.SessionUser;
import com.mazdausa.vds.security.ApplicationMenuRegistry;
import com.mazdausa.vds.security.SecurityUtility;
import com.mazdausa.vds.security.VDSMenuGroupList;

public abstract class VDSActionAbstract extends EmazdaActionAbstract {
	private static Logger log = EMDCSLogger.getLogger(VDSActionAbstract.class);
	
	@Override
	public ActionForward execute(ActionMapping mapping, ActionForm form,
			HttpServletRequest request, HttpServletResponse response) throws Exception {
		ActionForward forward = null;
		long startTime1=System.currentTimeMillis();
		log.debug("VDS Action abstract starts -PRVEhicles....."+startTime1);
		
		log.info("APPLICATION MODE:"+CommonUtility.isDebug());
		String uri = request.getRequestURI();
		if(!CommonUtility.isDebug()) {
			UserContext userContext = this.getUserContext(request);
			initializeViewHelper(userContext, request);
			initializeUserContext(userContext, request);
		}
		
		
		SessionUser userDetails = CommonUtility.getUserDetails(request);
//		
		//CODE FOR IMPLEMENTING VDS SECURITY
		//String[] userGroups = {"corp_vds_distribution","corp_vds_distribution_mgmt","corp_vds_allocation","corp_vds_finance","corp_vds_mexico_distribution","corp_vds_fleet"};
		String[] userGroups = SecurityUtility.getUserWslGroups(request);
		log.info("WSL GROUP:"+userGroups.length);
		ApplicationMenuRegistry objApplicationMenuRegistry=ApplicationMenuRegistry.getInstance();
		VDSMenuGroupList objVDSMenuGroupList = objApplicationMenuRegistry.getMenuList(userGroups) ;
		log.info("NUMBER OF APPLICATION:"+objVDSMenuGroupList.getGroupList().size());
		
//	    if(!SecurityUtility.hasPermission(request, objVDSMenuGroupList)){
//	    	log.info("SORRY YOU DO NOT HAVE PERMISSION TO THIS PAGE");
//	    	log.info("REDIRECTING TO HOME PAGE");
//			return mapping.findForward("global-welcome");
//		}else{
//			log.info("YOU HAVE PERMISSION TO THIS PAGE");
//		}
	    //END-CODE FOR IMPLEMENTING VDS SECURITY
		
		
		try{
			forward = executeAction(mapping, form, request, response);
			
			if(forward!=null && uri.indexOf("FetchModel.do") == -1){
				// CODE FOR MODEL YEAR LIST
				
		       
				//CODE FOR GETTING DEFAULT SESSION VALUES
		        String sUserCountryCode = CommonUtility.getUserCountryCode(request);
				
				
				
				
				
				
				
				StringBuffer objScriptBuffer = new StringBuffer("\n");
				objScriptBuffer.append("<script type=\"text/javascript\">");
				objScriptBuffer.append("\n");
				objScriptBuffer.append("var oDefaultCarlineList =new Array(");
				objScriptBuffer.append(");\n");
				objScriptBuffer.append("\n");
				objScriptBuffer.append("</script>");
				//END- CODE FOR GETTING DEFAULT SESSION VALUES
				request.setAttribute("defaultScriptValues", objScriptBuffer.toString());
				request.setAttribute("APP_MENU_GROUP_LIST",objVDSMenuGroupList);
			}
			
						
		} catch(Exception e) {
			log.error("An exception was caught while executing action", e);
			throw e;
		}
		
		if(userDetails.getRole().equalsIgnoreCase("region"))
			request.setAttribute("bRegionUser", true);
		else
			request.setAttribute("bRegionUser", false);
		log.debug("VDS Action abstract-PRVehicles ends....."+System.currentTimeMillis());
		log.debug("VDS Action abstract-PRVehicles completes in ....."+String.valueOf(System.currentTimeMillis()-startTime1)+" ms");
		log.info("VDS Action abstract-PRVehicles completes in ....."+String.valueOf(System.currentTimeMillis()-startTime1)+" ms");
		return forward;
	}
	
	public void initializeViewHelper(UserContext userContext, HttpServletRequest req){
	    DealerCollectionViewHelper helper = (DealerCollectionViewHelper)req.getSession().getAttribute("UserInfoBean");
	    if (helper == null){
	        helper = new DealerCollectionViewHelper(userContext);
	        req.getSession().setAttribute("UserInfoBean", helper);
	    }
	}
	
	public void initializeUserContext(UserContext ctx, HttpServletRequest req) {
		req.setAttribute("userContext", ctx);
	}
	
}

