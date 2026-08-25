<%@ taglib uri="/WEB-INF/struts-html.tld" prefix="html" %> 
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c"%>

		<!--LEFT PANEL START -->
			<div id="leftSecContainer">
		    	<div class="leftmenu">
			        	
			        	<div class="menuTitle submenuheader" sub-menu-id="Country" id="country_menu">Country</div>
		           		<div class="submenu" id="Country">
		           			<c:forEach var="country" items="${systemCountryLst}">
		           				<a class="menuitem-country" href="counrty.do?countryCd=${country.code}&returnUrl=" title="Country" country-code="${country.code}">${country.name}</a>
		           			</c:forEach>
		           			
				         	
		           		</div>
		           		
		           		<c:forEach var="MenuGroup" items="${APP_MENU_GROUP_LIST.groupList}">
							<div class="menuTitle" sub-menu-id="${MenuGroup.attribute}">${MenuGroup.header}</div>
							<div class="submenu" id="${MenuGroup.attribute}">
								<c:forEach var="AppMenu" items="${MenuGroup.menuList}">
								
									<c:choose>
										<c:when test="${AppMenu.visible==false}">
											<a class="menuitem" href="/${AppMenu.context}/${AppMenu.homeUrl}" sub-menu-id="${MenuGroup.attribute}" style="display:none;">${AppMenu.title}</a>
										</c:when>
										<c:when test="${AppMenu.popup ==false}">
											<a class="menuitem" href="/${AppMenu.context}/${AppMenu.homeUrl}" sub-menu-id="${MenuGroup.attribute}">${AppMenu.title}</a>
										</c:when>
										<c:otherwise>
											<a class="menuitem" href="/${AppMenu.context}/${AppMenu.homeUrl}" sub-menu-id="${MenuGroup.attribute}" target="_blank">${AppMenu.title}</a>
										</c:otherwise>
									</c:choose>
								
								
								</c:forEach>
							</div>
					  </c:forEach>
		         	
		            	
						
		             <div class="menuTitle-others" style="cursor: point;" onclick='javascript:window.open("${APP_MENU_GROUP_LIST.helpPage}","","resizable=yes,top=100,left=100,height=500,width=800,scrollbars=1");'>Help</div>
		            <div class="menuTitle-others" style="cursor: point;" onclick="return printData();">Print</div>
		            <div class="menuTitle-others" style="cursor: point;" onclick="return doExportEcel();">Export</div>
		            <div class="menuTitle-others" style="cursor: point;" onclick="return eraseCookie();">Log Out</div>
				</div>
				
		    </div>
		    <!--LEFT PANEL END -->