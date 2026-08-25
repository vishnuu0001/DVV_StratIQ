/**
 * This is the HomeAction.java
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

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.log4j.Logger;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;

import com.mazdausa.common.log.EMDCSLogger;
import com.mazdausa.corporate.vehicles.distribution.application.constants.AppConstant;

/**
 * @author TechM
 *
 */
public class HomeAction extends VDSActionAbstract {

	private static Logger log = EMDCSLogger.getLogger(CarrierSetupAction.class);

	@Override
	protected ActionForward executeAction(ActionMapping mapping,
			ActionForm form, HttpServletRequest req, HttpServletResponse response)
			throws Exception {
			log.debug("HomeAction-executeAction starts here");
		try {
			
			
			log.debug("HomeAction-executeAction ends here");
			return mapping.findForward(AppConstant.SUCCESS);
		} catch (Exception e) {
			log.error("HomeAction-executeAction error" + e);
			return mapping.findForward(AppConstant.ERROR);
		}
	}

}
