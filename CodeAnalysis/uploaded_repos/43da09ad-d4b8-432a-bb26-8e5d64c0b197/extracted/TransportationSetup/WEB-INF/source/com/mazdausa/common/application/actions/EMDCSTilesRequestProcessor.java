
package com.mazdausa.common.application.actions;

import java.io.IOException;
import java.util.Locale;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.log4j.Logger;
import org.apache.struts.Globals;
import org.apache.struts.action.Action;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;
import org.apache.struts.config.ModuleConfig;
import org.apache.struts.tiles.TilesRequestProcessor;
import org.apache.struts.util.RequestUtils;

import com.mazdausa.common.constants.CommonConstants;
import com.mazdausa.common.log.EMDCSLogger;

public class EMDCSTilesRequestProcessor extends TilesRequestProcessor {

	private static Logger log = EMDCSLogger.getLogger(EMDCSTilesRequestProcessor.class);
	
	private static final String STACK_TRACE = "Stacktrace is"; 
	private static final String CONTENT_TYPE = "text/html"; 
	private static final String ERROR_INFO = "Error Information:";
	private static final String INCONVINIENCE = "inconvenience and will work to correct the problem.";
	
	
	protected void processLocale(HttpServletRequest req, HttpServletResponse resp) {
		Locale currentLocale = (Locale) req.getSession().getAttribute(Globals.LOCALE_KEY);

		Locale newLocale = EmazdaLocaleProcessor.processLocale(req, currentLocale);

		if (newLocale != null) {
			req.getSession().setAttribute(Globals.LOCALE_KEY, newLocale);
		}
	}

	protected boolean queueAction(HttpServletRequest req, HttpServletResponse resp) throws IOException,
			ServletException {
		RequestContext requestContext = ContextFactory.getInstance().createRequestContext(req);

		String path = processPath(req, resp);
		if (path == null) {
			log.info("queueAction:action path to be queued is null");
			return false;
		}
		log.info("queueAction:Retrieve the action mapping for path:" + path);
		ActionMapping mapping = processMapping(req, resp, path);
		if (mapping == null) {
			log.info("queueAction:actionMapping retrieve from path " + path + " is null");
			return true;
		}

		log.info("queueAction:action to be queued:" + mapping.toString());
		log.info("queueAction:create the EMDCSActionInfo object for the path " + path + " and prefix"
				+ mapping.getPrefix());
		EMDCSActionInfo actionInfo = new EMDCSActionInfo(mapping.getPath()!=null?mapping.getPath():"", mapping.getPrefix());
		log.info("queueAction:push action into queue");
		requestContext.pushAction(actionInfo);

		return true;
	}

	
	protected ActionForward localLogin(HttpServletRequest req, HttpServletResponse resp) throws IOException,
			ServletException {
		
		ActionForward forward = getForward(req, "", CommonConstants.ACTION_MAPPING_LOCAL_LOGIN,
				CommonConstants.ACTION_MAPPING_LOCAL_LOGIN_FORWARD);
		return forward;

	}

	
	protected ActionForward getForward(HttpServletRequest req, String modPrefix, String actionMappingPath,
			String forwardName) {
		RequestUtils.selectModule(modPrefix, req, getServletContext());
		ModuleConfig moduleConfig = RequestUtils.getModuleConfig(req, getServletContext());
		ActionMapping loginMapping = (ActionMapping) moduleConfig.findActionConfig(actionMappingPath);
		ActionForward forward = loginMapping.findForward(forwardName);
		return forward;
	}

	
	protected ActionForward getGlobalForward(HttpServletRequest req, String modPrefix, String forwardName) {
		RequestUtils.selectModule(modPrefix, req, getServletContext());
		ModuleConfig moduleConfig = RequestUtils.getModuleConfig(req, getServletContext());
		ActionForward forward = (ActionForward) moduleConfig.findForwardConfig(forwardName);
		return forward;
	}

	
	protected ActionForward wslLogin(HttpServletRequest req, HttpServletResponse resp) throws IOException,
			ServletException {
		ActionForward forward = getForward(req, "", "/wslloginaction",
				CommonConstants.ACTION_MAPPING_DEFAULT_GLOBAL_FORWARD);
		return forward;
	}

	protected ActionForward processQueuedAction(HttpServletRequest req, HttpServletResponse resp) throws IOException,
			ServletException {
		ActionForward forward=null;
		log.info("Inside processQueuedAction");
		log.info("Retrieve the Request Context");
		RequestContext requestContext = ContextFactory.getInstance().createRequestContext(req);
		log.info("pop the Action from Q");
		EMDCSActionInfo actionInfo = requestContext.popAction();
		if (actionInfo == null){
			log.info("The queued action is null");
		}
		log.info("Select the module");
// to fix the sonar issue added condition by TechM
		if(actionInfo!=null){
			RequestUtils.selectModule(actionInfo.getMappingModulePrefix()!=null?actionInfo.getMappingModulePrefix():"", req, getServletContext());
			log.info("Compute the forward from the action mapping");
			forward= getForward(req, actionInfo.getMappingModulePrefix()!=null?actionInfo.getMappingModulePrefix():"", actionInfo.getActionPath(),
					CommonConstants.ACTION_MAPPING_DEFAULT_FORWARD);
			log.info("Return the forward:" + forward);
		}
		return forward;
	}

	protected ActionForward processActionPerform(HttpServletRequest req, HttpServletResponse resp, Action action,
			ActionForm form, ActionMapping actionMapping) throws IOException, ServletException {
		ActionForward forward = new ActionForward();
		try {

			if (actionMapping instanceof EMDCSLocalLoginActionMapping) {
			
				log.info("Process local login action");
				forward = super.processActionPerform(req, resp, action, form, actionMapping);
				if (((EMDCSLocalLoginActionMapping) actionMapping).getProcessingState() == ICommonApplicationConstants.LOCAL_LOGIN_STATE_PROCESS_COMPLETE) {
					log.info("After Processing local login action, check the user context for login status");
					UserContext userContext = ContextFactory.getInstance().createUserContext(req);
					if (userContext.isLoggedOn()) {
						log.info("User is logged on. Proceed to target action (queued)");
						forward = processTargetAction(req, resp);
					} else {
						log.info("forward to local login");
						forward = getLoginForward(req, resp);
					}
				}

				if (forward == null) {
					log.info("No forward specified, proceed to not found action");
					return getGlobalForward(req, "", ICommonApplicationConstants.GLOBAL_FORWARD_NOT_FOUND);
				} else {
					log.info("Return the forward: " + forward);
					return forward;
				}
			} else {
				log.info("Retrieve the user context");
				UserContext userContext = ContextFactory.getInstance().createUserContext(req);
				if (!userContext.isLoggedOn()) {
					log.info("Queued the intended action");
					queueAction(req, resp);
					log.info("Return the local login action forward");
					return getLoginForward(req, resp);
				} else {
					log.info("Delegate to the super class for action processing");
					try {

						log.info("Delegate to super.processActionPerform");
						forward = super.processActionPerform(req, resp, action, form, actionMapping);
					} catch (ServletException exp) {
						exp.printStackTrace();
						log.error("Exception encountered when invoking the application action: "
								+ actionMapping.toString());
						log.error(STACK_TRACE, exp);
						resp.setContentType(CONTENT_TYPE);
						java.io.PrintWriter out = resp.getWriter();
						out.println("<html><head><title>Application Error</title></head><body><h2>Sorry</h2><p>An error occurred while processing this page.</p><table ");
						out.println("order=1><tr><td><b>"+ERROR_INFO+"</b> " + exp.toString()
								+ "</td></tr><tr><td><b>Root Cause: </b>" + exp.getRootCause()
								+ "</td></tr></table><p> We apologize for the ");
						out.println(INCONVINIENCE+"</p></body></html>");
						forward = null;
					}

					if (actionMapping instanceof EmazdaNoCacheActionMapping
							&& ((EmazdaNoCacheActionMapping) actionMapping).isNocacheEnabled()) {
						log.info("processMappingNocache: setup no cache header");
						processMappingNocache(req, resp);
					}
					return forward;
				}
			}

		} catch (UserContextException exp) {
			log.info("UserContextException " + this.getClass().getName() + ". Method:processActionPerform. Msg. "
					+ exp.toString());
			log.info(STACK_TRACE, exp);
			resp.setContentType(CONTENT_TYPE);
			java.io.PrintWriter out = resp.getWriter();
			out.println("<html><head><title>Application Error</title></head><body><h2>Sorry</h2><p>An error occurred while processing this page.</p><table ");
			out.println("order=1><tr><td><b>"+ERROR_INFO+"</b>" + exp.toString()
					+ "</td></tr><tr><td><b>Cause: </b>" + exp.getCause()
					+ "</td></tr></table><p> We apologize for the ");
			out.println(INCONVINIENCE+"</p></body></html>");
			forward = null;
		} catch (Exception exp) {
			log.error("Exception " + this.getClass().getName() + ". Method:processActionPerform. Msg. " + exp.toString());
			log.error(STACK_TRACE, exp);
			resp.setContentType(CONTENT_TYPE);
			java.io.PrintWriter out = resp.getWriter();
			out.println("<html><head><title>Application Error</title></head><body><h2>Sorry</h2><p>An error occurred while processing this page.</p><table ");
			out.println("order=1><tr><td><b>"+ERROR_INFO+"</b> " + exp.toString()
					+ "</td></tr><tr><td><b>Cause: </b>" + exp.getCause()
					+ "</td></tr></table><p> We apologize for the ");
			out.println(INCONVINIENCE+"</p></body></html>");
			forward = null;
		}
		return forward;
	}

	protected void processMappingNocache(HttpServletRequest req, HttpServletResponse resp) throws IOException,
			ServletException {
		resp.setHeader("Pragma", "No-cache");
		resp.setHeader("Cache-Control", "no-cache");
		resp.setDateHeader("Expires", 1);
	}

	
	protected ActionForward processTargetAction(HttpServletRequest req, HttpServletResponse resp) throws IOException,
			ServletException {
		log.info("Retrieve the user context from inside processTargetAction method ");
		RequestContext requestContext = ContextFactory.getInstance().createRequestContext(req);
		// Process the queued action
		if (requestContext.hasQueuedAction()) {
			log.info("There is an action in the queue, process it");
			return processQueuedAction(req, resp);
		} else {
			log.info("There are no action in the queue");
			return null;
		}
	}

	protected ActionForward getLoginForward(HttpServletRequest req, HttpServletResponse resp) throws IOException,
			ServletException {
		if (ApplicationContext.getInstance().isDevelopmentMode()) {
			return localLogin(req, resp);
		} else {
			return wslLogin(req, resp);
		}
	}

	
	protected ActionForward processException(HttpServletRequest req, HttpServletResponse resp, Exception exception,
			ActionForm form, ActionMapping mapping) throws IOException, ServletException {
		log.info("Exception generated from the Struts framework: " + exception + ". form:" + form + "  .Mapping:"
				+ mapping);

		return super.processException(req, resp, exception, form, mapping);
	}
}
