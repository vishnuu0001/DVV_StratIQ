package com.mazdausa.corporate.vehicles.distribution.application.util;

import java.io.FileInputStream;
import java.io.IOException;
import java.util.Properties;
import java.util.StringTokenizer;

import org.apache.log4j.Logger;

import com.mazdausa.common.constants.CommonConstants;
import com.mazdausa.common.log.EMDCSLogger;
import com.mazdausa.common.util.SchemaRegistryLocator;

public class SchemaRegistryLocatorImpl implements SchemaRegistryLocator {
	private static Logger log = EMDCSLogger.getLogger(SchemaRegistryLocatorImpl.class);
	 private final String VAR_MARKER_START = "${";
    private final String VAR_MARKER_END = "}";
    private final int VAR_MARKER_START_LEN = "${".length();
    private final int VAR_MARKER_END_LEN = "}".length();
	@Override
	public String getLocation() {
		
		
		 StringBuffer buffer=new StringBuffer();
			try {
				String propertiesLocation = System.getProperties().getProperty(CommonConstants.EMDCS_CONFIG_PROP_PATH); 
				Properties prop = new Properties();
			    prop.load(new FileInputStream(propertiesLocation));
			    String url = prop.getProperty("dao.schema.registry.inquiry");
			    
			    String key;
		        log.info("Process the path variable substitution for url " + url);
		        StringTokenizer token = new StringTokenizer(url, "${");
		        key = null;
		        if(token.hasMoreTokens())
		            key = token.nextToken();
		        if(key == null || key.length() == 0)
		            return url;
		        
					
		        token = new StringTokenizer(key, "}");
		        if(token.hasMoreTokens())
		            key = token.nextToken();
		        if(key == null || key.length() == 0)
		            return url;
					
		       
		        buffer = new StringBuffer(url);
		        int pos = buffer.toString().indexOf("${");
		        
		        String value = prop.getProperty(key);
		      
					
		        buffer.replace(pos, VAR_MARKER_START_LEN + key.length() + VAR_MARKER_END_LEN, value);
			}catch (IOException ex) {
                log.error(ex.getMessage());

			}
			
			log.info("Schema:"+buffer.toString());
	        return buffer.toString();
		
		/*String schemaRegistryFile = ApplicationUtil.getSystemProperty(AppConstants.FLEET_PROPERTY_SCHEMA, "dao.schema.registry.file");
		return schemaRegistryFile;*/
	}
	
	
	
}
