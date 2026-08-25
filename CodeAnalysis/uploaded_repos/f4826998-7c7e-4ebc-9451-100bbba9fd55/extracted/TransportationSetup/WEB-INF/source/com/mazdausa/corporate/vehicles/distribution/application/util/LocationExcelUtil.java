package com.mazdausa.corporate.vehicles.distribution.application.util;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

import org.apache.log4j.Logger;
import org.apache.poi.hssf.usermodel.HSSFFont;
import org.apache.poi.hssf.usermodel.HSSFWorkbook;
import org.apache.poi.ss.usermodel.BorderStyle;
import org.apache.poi.ss.usermodel.Cell;
import org.apache.poi.ss.usermodel.CellStyle;
import org.apache.poi.ss.usermodel.DataFormat;
import org.apache.poi.ss.usermodel.FillPatternType;
import org.apache.poi.ss.usermodel.IndexedColors;
import org.apache.poi.ss.usermodel.Row;
import org.apache.poi.ss.usermodel.Sheet;
import org.apache.poi.ss.util.CellRangeAddress;

import com.mazdausa.common.log.EMDCSLogger;
import com.mazdausa.common.util.ApplicationUtil;
import com.mazdausa.corporate.vehicles.distribution.application.constants.AppConstant;
import com.mazdausa.corporate.vehicles.distribution.persistence.dto.CarrierSetupDTO;
import com.mazdausa.corporate.vehicles.distribution.persistence.dto.LocationIndexDTO;

public class LocationExcelUtil {

	private LocationExcelUtil() {
		super();
	}


	private static Logger log = EMDCSLogger.getLogger(LocationExcelUtil.class);

	public static HSSFWorkbook writeDataToExcel(List<LocationIndexDTO> arrayList)
	{
		HSSFWorkbook workbook = null;
		
		try{
			workbook = new HSSFWorkbook();
			Sheet locationExcelReportSheet =null;
			
			locationExcelReportSheet = workbook.createSheet("Location Details");

			locationExcelReportSheet.setZoom(85);
			
			DataFormat format = workbook.createDataFormat();
			
			CellStyle style=workbook.createCellStyle();
			style.setBorderBottom(BorderStyle.THIN);
			style.setBorderTop(BorderStyle.THIN);
			style.setBorderRight(BorderStyle.THIN);
			style.setBorderLeft(BorderStyle.THIN);
			style.setTopBorderColor(IndexedColors.BLACK.getIndex());  
			style.setRightBorderColor(IndexedColors.BLACK.getIndex());  
			style.setLeftBorderColor(IndexedColors.BLACK.getIndex());  
			style.setBottomBorderColor(IndexedColors.BLACK.getIndex());
			
	        
			CellStyle headerStyle=workbook.createCellStyle();
			headerStyle.setFillForegroundColor(IndexedColors.LIGHT_BLUE.getIndex());
			headerStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND);
			headerStyle.setBorderBottom(BorderStyle.THIN);
			headerStyle.setBorderTop(BorderStyle.THIN);
			headerStyle.setBorderRight(BorderStyle.THIN);
			headerStyle.setBorderLeft(BorderStyle.THIN);
			headerStyle.setTopBorderColor(IndexedColors.BLACK.getIndex());  
			headerStyle.setRightBorderColor(IndexedColors.BLACK.getIndex());  
			headerStyle.setLeftBorderColor(IndexedColors.BLACK.getIndex());  
			headerStyle.setBottomBorderColor(IndexedColors.BLACK.getIndex());
			headerStyle.setAlignment(org.apache.poi.ss.usermodel.HorizontalAlignment.CENTER);
			HSSFFont font = workbook.createFont();
	        font.setColor(IndexedColors.WHITE.getIndex());
	        headerStyle.setFont(font);
	        
	        CellStyle columnStyle=workbook.createCellStyle();
	        columnStyle.setFillForegroundColor(IndexedColors.DARK_RED.getIndex());
	        columnStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND);
	        columnStyle.setBorderBottom(BorderStyle.THIN);
	        columnStyle.setBorderTop(BorderStyle.THIN);
	        columnStyle.setBorderRight(BorderStyle.THIN);
	        columnStyle.setBorderLeft(BorderStyle.THIN);
	        columnStyle.setTopBorderColor(IndexedColors.BLACK.getIndex());  
	        columnStyle.setRightBorderColor(IndexedColors.BLACK.getIndex());  
	        columnStyle.setLeftBorderColor(IndexedColors.BLACK.getIndex());  
	        columnStyle.setBottomBorderColor(IndexedColors.BLACK.getIndex());
	        columnStyle.setAlignment(org.apache.poi.ss.usermodel.HorizontalAlignment.LEFT);
	        columnStyle.setFont(font);
	        
	        CellStyle columnStyleRight=workbook.createCellStyle();
	        columnStyleRight.setFillForegroundColor(IndexedColors.DARK_RED.getIndex());
	        columnStyleRight.setFillPattern(FillPatternType.SOLID_FOREGROUND);
	        columnStyleRight.setBorderBottom(BorderStyle.THIN);
	        columnStyleRight.setBorderTop(BorderStyle.THIN);
	        columnStyleRight.setBorderRight(BorderStyle.THIN);
	        columnStyleRight.setBorderLeft(BorderStyle.THIN);
	        columnStyleRight.setTopBorderColor(IndexedColors.BLACK.getIndex());  
	        columnStyleRight.setRightBorderColor(IndexedColors.BLACK.getIndex());  
	        columnStyleRight.setLeftBorderColor(IndexedColors.BLACK.getIndex());  
	        columnStyleRight.setBottomBorderColor(IndexedColors.BLACK.getIndex());
	        columnStyleRight.setAlignment(org.apache.poi.ss.usermodel.HorizontalAlignment.RIGHT);
	        columnStyleRight.setFont(font);
	        
	        CellStyle cellColorGreen=workbook.createCellStyle();
	        cellColorGreen.setFillForegroundColor(IndexedColors.GREEN.getIndex());
	        cellColorGreen.setFillPattern(FillPatternType.SOLID_FOREGROUND);
	        cellColorGreen.setBorderBottom(BorderStyle.THIN);
	        cellColorGreen.setBorderTop(BorderStyle.THIN);
	        cellColorGreen.setBorderRight(BorderStyle.THIN);
	        cellColorGreen.setBorderLeft(BorderStyle.THIN);
	        cellColorGreen.setTopBorderColor(IndexedColors.BLACK.getIndex());  
	        cellColorGreen.setRightBorderColor(IndexedColors.BLACK.getIndex());  
	        cellColorGreen.setLeftBorderColor(IndexedColors.BLACK.getIndex());  
	        cellColorGreen.setBottomBorderColor(IndexedColors.BLACK.getIndex());
	        cellColorGreen.setAlignment(org.apache.poi.ss.usermodel.HorizontalAlignment.CENTER);
	        cellColorGreen.setFont(font);
	        
	        CellStyle cellColorRed=workbook.createCellStyle();
	        cellColorRed.setFillForegroundColor(IndexedColors.RED.getIndex());
	        cellColorRed.setFillPattern(FillPatternType.SOLID_FOREGROUND);
	        cellColorRed.setBorderBottom(BorderStyle.THIN);
	        cellColorRed.setBorderTop(BorderStyle.THIN);
	        cellColorRed.setBorderRight(BorderStyle.THIN);
	        cellColorRed.setBorderLeft(BorderStyle.THIN);
	        cellColorRed.setTopBorderColor(IndexedColors.BLACK.getIndex());  
	        cellColorRed.setRightBorderColor(IndexedColors.BLACK.getIndex());  
	        cellColorRed.setLeftBorderColor(IndexedColors.BLACK.getIndex());  
	        cellColorRed.setBottomBorderColor(IndexedColors.BLACK.getIndex());
	        cellColorRed.setAlignment(org.apache.poi.ss.usermodel.HorizontalAlignment.CENTER);
	        cellColorRed.setFont(font);
	        
	        HSSFFont headerFont = workbook.createFont();
	        headerFont.setColor(IndexedColors.BLACK.getIndex());
	        headerFont.setBold(true);
	        headerFont.setFontHeightInPoints((short) 12);
	        
	        CellStyle headerStyle1=workbook.createCellStyle();
	        headerStyle1.setAlignment(org.apache.poi.ss.usermodel.HorizontalAlignment.CENTER);
	        headerStyle1.setVerticalAlignment(org.apache.poi.ss.usermodel.VerticalAlignment.CENTER);
	        headerStyle1.setFont(headerFont);
	        
	        CellStyle wrapStyle = workbook.createCellStyle();
	        wrapStyle.setWrapText(true);
	        
	       
	       
	        int incidentsRowNum = 0;
	        int incidentsColNum = 0;
	        int width1 = 30*256;
	        int width3 = 60*256;
	        
			Row incidentsRow = locationExcelReportSheet.createRow(incidentsRowNum);
			Cell cell1 = incidentsRow.createCell(incidentsColNum);
			
			 CellStyle backgroundStyleOdd = workbook.createCellStyle();
			 backgroundStyleOdd.setBorderBottom(BorderStyle.THIN);
			 backgroundStyleOdd.setBorderTop(BorderStyle.THIN);
			 backgroundStyleOdd.setBorderRight(BorderStyle.THIN);
			 backgroundStyleOdd.setBorderLeft(BorderStyle.THIN);
			 backgroundStyleOdd.setTopBorderColor(IndexedColors.BLACK.getIndex());  
			 backgroundStyleOdd.setRightBorderColor(IndexedColors.BLACK.getIndex());  
			 backgroundStyleOdd.setLeftBorderColor(IndexedColors.BLACK.getIndex());  
			 backgroundStyleOdd.setBottomBorderColor(IndexedColors.BLACK.getIndex());
			 backgroundStyleOdd.setFillForegroundColor(IndexedColors.GREY_25_PERCENT.getIndex());
			 backgroundStyleOdd.setFillPattern(FillPatternType.SOLID_FOREGROUND);
//			 backgroundStyleOdd.setDataFormat(format.getFormat("m/d/yy h:mm"));
			 backgroundStyleOdd.setWrapText(true);
			
			CellStyle backgroundStyleEven = workbook.createCellStyle();
			backgroundStyleEven.setBorderBottom(BorderStyle.THIN);
			backgroundStyleEven.setBorderTop(BorderStyle.THIN);
			backgroundStyleEven.setBorderRight(BorderStyle.THIN);
			backgroundStyleEven.setBorderLeft(BorderStyle.THIN);
			backgroundStyleEven.setTopBorderColor(IndexedColors.BLACK.getIndex());  
			backgroundStyleEven.setRightBorderColor(IndexedColors.BLACK.getIndex());  
			backgroundStyleEven.setLeftBorderColor(IndexedColors.BLACK.getIndex());  
			backgroundStyleEven.setBottomBorderColor(IndexedColors.BLACK.getIndex());
			backgroundStyleEven.setFillForegroundColor(IndexedColors.LIGHT_TURQUOISE.getIndex());
			backgroundStyleEven.setFillPattern(FillPatternType.SOLID_FOREGROUND);
			backgroundStyleEven.setWrapText(true);
			CellRangeAddress cellRangeAddress = new CellRangeAddress(incidentsRowNum,
					incidentsRowNum, 0, 5);
			locationExcelReportSheet.addMergedRegion(cellRangeAddress);
			cell1.setCellValue("Location Index");
			cell1.setCellStyle(headerStyle1);
			
			incidentsRowNum++;
			
			incidentsRow = locationExcelReportSheet.createRow(incidentsRowNum);
			cell1 = incidentsRow.createCell(incidentsColNum);
			CellRangeAddress cellRangeAddress3 = new CellRangeAddress(incidentsRowNum,
					incidentsRowNum, 0, 5);
			locationExcelReportSheet.addMergedRegion(cellRangeAddress3);
			cell1.setCellValue(" ");
			
			incidentsRowNum++;
			incidentsRow = locationExcelReportSheet.createRow(incidentsRowNum);
			cell1 = incidentsRow.createCell(incidentsColNum);
			cell1.setCellValue("Location Code");
			cell1.setCellStyle(headerStyle);
			locationExcelReportSheet.setColumnWidth(incidentsColNum, width1);
			cell1.setCellStyle(headerStyle);
			
			incidentsColNum++;
			cell1 = incidentsRow.createCell(incidentsColNum);
			cell1.setCellValue("Location Name");
			locationExcelReportSheet.setColumnWidth(incidentsColNum, width1);
			cell1.setCellStyle(headerStyle);
			
			
			incidentsColNum++;
			cell1 = incidentsRow.createCell(incidentsColNum);
			cell1.setCellValue("Street Address1");
			locationExcelReportSheet.setColumnWidth(incidentsColNum, width1);
			cell1.setCellStyle(headerStyle);
			
			
			incidentsColNum++;
			cell1 = incidentsRow.createCell(incidentsColNum);
			cell1.setCellValue("Street Address2");
			locationExcelReportSheet.setColumnWidth(incidentsColNum, width1);
			cell1.setCellStyle(headerStyle);
			
			incidentsColNum++;
			cell1 = incidentsRow.createCell(incidentsColNum);
			cell1.setCellValue("Street Address3");
			locationExcelReportSheet.setColumnWidth(incidentsColNum, width1);
			cell1.setCellStyle(headerStyle);
			
			
			incidentsColNum++;
			cell1 = incidentsRow.createCell(incidentsColNum);
			cell1.setCellValue("City");
			locationExcelReportSheet.setColumnWidth(incidentsColNum, width1);
			cell1.setCellStyle(headerStyle);
			
			incidentsColNum++;
			cell1 = incidentsRow.createCell(incidentsColNum);
			cell1.setCellValue("State Code");
			locationExcelReportSheet.setColumnWidth(incidentsColNum, width1);
			cell1.setCellStyle(headerStyle);
			
			incidentsColNum++;
			cell1 = incidentsRow.createCell(incidentsColNum);
			cell1.setCellValue("Country Name");
			locationExcelReportSheet.setColumnWidth(incidentsColNum, width1);
			cell1.setCellStyle(headerStyle);
			
			incidentsColNum++;
			cell1 = incidentsRow.createCell(incidentsColNum);
			cell1.setCellValue("Country Code");
			locationExcelReportSheet.setColumnWidth(incidentsColNum, width1);
			cell1.setCellStyle(headerStyle);
			
			
			incidentsColNum++;
			cell1 = incidentsRow.createCell(incidentsColNum);
			cell1.setCellValue("Zip Code");
			locationExcelReportSheet.setColumnWidth(incidentsColNum, width1);
			cell1.setCellStyle(headerStyle);
			
			incidentsColNum++;
			cell1 = incidentsRow.createCell(incidentsColNum);
			cell1.setCellValue("Phone");
			locationExcelReportSheet.setColumnWidth(incidentsColNum, width1);
			cell1.setCellStyle(headerStyle);
			
			incidentsColNum++;
			cell1 = incidentsRow.createCell(incidentsColNum);
			cell1.setCellValue("Address Type");
			locationExcelReportSheet.setColumnWidth(incidentsColNum, width1);
			cell1.setCellStyle(headerStyle);
			
			
			incidentsColNum++;
			cell1 = incidentsRow.createCell(incidentsColNum);
			cell1.setCellValue("Status");
			locationExcelReportSheet.setColumnWidth(incidentsColNum, width1);
			cell1.setCellStyle(headerStyle);
			
			incidentsColNum++;
			cell1 = incidentsRow.createCell(incidentsColNum);
			cell1.setCellValue("Type");
			locationExcelReportSheet.setColumnWidth(incidentsColNum, width1);
			cell1.setCellStyle(headerStyle);
			
			incidentsColNum++;
			cell1 = incidentsRow.createCell(incidentsColNum);
			cell1.setCellValue("Region");
			locationExcelReportSheet.setColumnWidth(incidentsColNum, width1);
			cell1.setCellStyle(headerStyle);
			
			int rowColor = 0;
			int count=0;
			
			if(arrayList!= null){
				for(LocationIndexDTO generateExcelDto:arrayList){
					rowColor++;
					count++;
					
					incidentsRowNum++;
					incidentsColNum = 0;
					incidentsRow = locationExcelReportSheet.createRow(incidentsRowNum);
					cell1 = incidentsRow.createCell(incidentsColNum);
					cell1.setCellValue(generateExcelDto.getCurrentLocationCode());
					if(rowColor%2==0){
						cell1.setCellStyle(backgroundStyleEven);
					}else{
						cell1.setCellStyle(backgroundStyleOdd);
					}
					
					incidentsColNum++;
					cell1 = incidentsRow.createCell(incidentsColNum);
					
					cell1.setCellValue(generateExcelDto.getLocationName());
					cell1.setCellStyle(wrapStyle);
					if(rowColor%2==0){
						cell1.setCellStyle(backgroundStyleEven);
					}else{
						cell1.setCellStyle(backgroundStyleOdd);
					}
					
					if("SHIPPING".equals(generateExcelDto.getAddressTypeNm())){
					
						incidentsColNum++;
						cell1 = incidentsRow.createCell(incidentsColNum);
						
						cell1.setCellValue(generateExcelDto.getShippingstreetaddress1());
						if(rowColor%2==0){
							cell1.setCellStyle(backgroundStyleEven);
						}else{
							cell1.setCellStyle(backgroundStyleOdd);
						}
						
						
						incidentsColNum++;
						cell1 = incidentsRow.createCell(incidentsColNum);
						
						cell1.setCellValue(generateExcelDto.getShippingstreetaddress2());
						if(rowColor%2==0){
							cell1.setCellStyle(backgroundStyleEven);
						}else{
							cell1.setCellStyle(backgroundStyleOdd);
						}
						
						
						incidentsColNum++;
						cell1 = incidentsRow.createCell(incidentsColNum);
						
						cell1.setCellValue(generateExcelDto.getShippingstreetaddress3());
						if(rowColor%2==0){
							cell1.setCellStyle(backgroundStyleEven);
						}else{
							cell1.setCellStyle(backgroundStyleOdd);
						}
						
						
						incidentsColNum++;
						cell1 = incidentsRow.createCell(incidentsColNum);
						
						cell1.setCellValue(generateExcelDto.getShippingcityname());
						if(rowColor%2==0){
							cell1.setCellStyle(backgroundStyleEven);
						}else{
							cell1.setCellStyle(backgroundStyleOdd);
						}
						
						incidentsColNum++;
						cell1 = incidentsRow.createCell(incidentsColNum);
						
						cell1.setCellValue(generateExcelDto.getShippingstatecode());
						if(rowColor%2==0){
							cell1.setCellStyle(backgroundStyleEven);
						}else{
							cell1.setCellStyle(backgroundStyleOdd);
						}
						
						incidentsColNum++;
						cell1 = incidentsRow.createCell(incidentsColNum);
						
						cell1.setCellValue(generateExcelDto.getShippingcountrynm());
						if(rowColor%2==0){
							cell1.setCellStyle(backgroundStyleEven);
						}else{
							cell1.setCellStyle(backgroundStyleOdd);
						}
						
						incidentsColNum++;
						cell1 = incidentsRow.createCell(incidentsColNum);
						
						cell1.setCellValue(generateExcelDto.getShippingcountrycode());
						if(rowColor%2==0){
							cell1.setCellStyle(backgroundStyleEven);
						}else{
							cell1.setCellStyle(backgroundStyleOdd);
						}
						
						incidentsColNum++;
						cell1 = incidentsRow.createCell(incidentsColNum);
						
						cell1.setCellValue(generateExcelDto.getShippingzipcode());
						if(rowColor%2==0){
							cell1.setCellStyle(backgroundStyleEven);
						}else{
							cell1.setCellStyle(backgroundStyleOdd);
						}
						
						
					}else{
						
						incidentsColNum++;
						cell1 = incidentsRow.createCell(incidentsColNum);
						
						cell1.setCellValue(generateExcelDto.getStreetAddress1());
						if(rowColor%2==0){
							cell1.setCellStyle(backgroundStyleEven);
						}else{
							cell1.setCellStyle(backgroundStyleOdd);
						}
						
						incidentsColNum++;
						cell1 = incidentsRow.createCell(incidentsColNum);
						
						cell1.setCellValue(generateExcelDto.getStreetAddress2());
						if(rowColor%2==0){
							cell1.setCellStyle(backgroundStyleEven);
						}else{
							cell1.setCellStyle(backgroundStyleOdd);
						}
						
						incidentsColNum++;
						cell1 = incidentsRow.createCell(incidentsColNum);
						
						cell1.setCellValue(generateExcelDto.getStreetAddress3());
						if(rowColor%2==0){
							cell1.setCellStyle(backgroundStyleEven);
						}else{
							cell1.setCellStyle(backgroundStyleOdd);
						}
						
						incidentsColNum++;
						cell1 = incidentsRow.createCell(incidentsColNum);
						
						cell1.setCellValue(generateExcelDto.getCityName());
						if(rowColor%2==0){
							cell1.setCellStyle(backgroundStyleEven);
						}else{
							cell1.setCellStyle(backgroundStyleOdd);
						}
						
						incidentsColNum++;
						cell1 = incidentsRow.createCell(incidentsColNum);
						
						cell1.setCellValue(generateExcelDto.getStateCode());
						if(rowColor%2==0){
							cell1.setCellStyle(backgroundStyleEven);
						}else{
							cell1.setCellStyle(backgroundStyleOdd);
						}
						
						incidentsColNum++;
						cell1 = incidentsRow.createCell(incidentsColNum);
						
						cell1.setCellValue(generateExcelDto.getCountryNm());
						if(rowColor%2==0){
							cell1.setCellStyle(backgroundStyleEven);
						}else{
							cell1.setCellStyle(backgroundStyleOdd);
						}
						
						incidentsColNum++;
						cell1 = incidentsRow.createCell(incidentsColNum);
						
						cell1.setCellValue(generateExcelDto.getCountryCd());
						if(rowColor%2==0){
							cell1.setCellStyle(backgroundStyleEven);
						}else{
							cell1.setCellStyle(backgroundStyleOdd);
						}
						
						incidentsColNum++;
						cell1 = incidentsRow.createCell(incidentsColNum);
						
						cell1.setCellValue(generateExcelDto.getZipCode());
						if(rowColor%2==0){
							cell1.setCellStyle(backgroundStyleEven);
						}else{
							cell1.setCellStyle(backgroundStyleOdd);
						}
					}
					
					incidentsColNum++;
					cell1 = incidentsRow.createCell(incidentsColNum);
					
					LocationIndexDTO formattingExcelFinalDto=formatingPhoneNo(generateExcelDto);
					cell1.setCellValue(formattingExcelFinalDto.getAddressFormatting());
					if(rowColor%2==0){
						cell1.setCellStyle(backgroundStyleEven);
					}else{
						cell1.setCellStyle(backgroundStyleOdd);
					}
					
					incidentsColNum++;
					cell1 = incidentsRow.createCell(incidentsColNum);
					
					cell1.setCellValue(generateExcelDto.getAddressTypeNm());
					if(rowColor%2==0){
						cell1.setCellStyle(backgroundStyleEven);
					}else{
						cell1.setCellStyle(backgroundStyleOdd);
					}
					
					incidentsColNum++;
					cell1 = incidentsRow.createCell(incidentsColNum);
					
					cell1.setCellValue(generateExcelDto.getStatusDesc()); 
					if(rowColor%2==0){
						cell1.setCellStyle(backgroundStyleEven);
					}else{
						cell1.setCellStyle(backgroundStyleOdd);
					}
					
					incidentsColNum++;
					cell1 = incidentsRow.createCell(incidentsColNum);
					LocationIndexDTO formattingLocationTypeExcelFinalDto=formatingLocationType(generateExcelDto);
					cell1.setCellValue(formattingLocationTypeExcelFinalDto.getLocationTypeFormatting()); 
					if(rowColor%2==0){
						cell1.setCellStyle(backgroundStyleEven);
					}else{
						cell1.setCellStyle(backgroundStyleOdd);
					}
					
					incidentsColNum++;
					cell1 = incidentsRow.createCell(incidentsColNum);
					
					cell1.setCellValue(generateExcelDto.getRegionCd()); 
					if(rowColor%2==0){
						cell1.setCellStyle(backgroundStyleEven);
					}else{
						cell1.setCellStyle(backgroundStyleOdd);
					}
					


				}
				incidentsRowNum=incidentsRowNum+3;
				incidentsRow = locationExcelReportSheet.createRow(incidentsRowNum);
				cell1 = incidentsRow.createCell(0);
				cell1.setCellValue("Total Record Count:"+count); 
				
				}
				}catch (Exception e) {
					log.error(e.getMessage());
	}
		return workbook;
}
	
	public static void writedataCSV(StringBuilder generatedInputString1, String responceSeqNum) throws IOException{
		StringBuilder generatedInputString=new StringBuilder();
	    File file=new File(ApplicationUtil.getSystemProperty(AppConstant.APPLICATION_URLS, AppConstant.APP_DATA_BASE_URL)+"/veh/ICL/"+ApplicationUtil.getSystemProperty(AppConstant.TransportationSetup, AppConstant.LOC_FILE_NAME_START_WITH) );
	    FileWriter writer=null;
	    SimpleDateFormat ft = new SimpleDateFormat("yyMMddHHmm");
	    SimpleDateFormat f = new SimpleDateFormat("yyyyMMddHHmmss"); 
	    BufferedWriter buffer=null;
		try {
			writer = new FileWriter(file+f.format(new Date())+"0001"+".D80");
			 buffer = new BufferedWriter(writer);
				buffer.write(AppConstant.HEADER+ft.format(new Date())+responceSeqNum.trim());
				buffer.newLine();
				buffer.write(generatedInputString1.toString());
				buffer.newLine();
				buffer.write(AppConstant.FOOTER+responceSeqNum.trim());
				buffer.newLine();
				
		} catch (IOException e) {
			log.debug(e.getMessage());
		}finally{
// to fix sonar issue modified the code by techm  starts here
			if(buffer!=null){
				buffer.close();  
			}
	//ends here		
			
			if(writer != null)
            {
                try
                {
                	
                	writer.close();
                }
                catch(Exception e)
                {
                    log.error("ERROR CLOSING RESULTSET : "+e,e);
                }
            }
		}

    
	}
	
	
	public static String getlocationpathFromPropFile(String key) {
		String value = null;
		try {
			
			value = ApplicationUtil.getSystemProperty(AppConstant.LOCATION_PROPERTY_FILE, key);
			if (value == null) {
				value = AppConstant.BLANK;
			}
		} catch (Exception e) {
			value = AppConstant.BLANK;
		}
		return value;

	}
	
	public static HSSFWorkbook carrierDetailsToExcel(List<CarrierSetupDTO> arrayList)
	{
		HSSFWorkbook workbook = null;
		
		try{
			workbook = new HSSFWorkbook();
			Sheet locationExcelReportSheet =null;
			
			locationExcelReportSheet = workbook.createSheet("Carrier Details");

			locationExcelReportSheet.setZoom(85);
			
			
			
			CellStyle style=workbook.createCellStyle();
			style.setBorderBottom(BorderStyle.THIN);
			style.setBorderTop(BorderStyle.THIN);
			style.setBorderRight(BorderStyle.THIN);
			style.setBorderLeft(BorderStyle.THIN);
			style.setTopBorderColor(IndexedColors.BLACK.getIndex());  
			style.setRightBorderColor(IndexedColors.BLACK.getIndex());  
			style.setLeftBorderColor(IndexedColors.BLACK.getIndex());  
			style.setBottomBorderColor(IndexedColors.BLACK.getIndex());
			
	        
			CellStyle headerStyle=workbook.createCellStyle();
			headerStyle.setFillForegroundColor(IndexedColors.LIGHT_BLUE.getIndex());
			headerStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND);
			headerStyle.setBorderBottom(BorderStyle.THIN);
			headerStyle.setBorderTop(BorderStyle.THIN);
			headerStyle.setBorderRight(BorderStyle.THIN);
			headerStyle.setBorderLeft(BorderStyle.THIN);
			headerStyle.setTopBorderColor(IndexedColors.BLACK.getIndex());  
			headerStyle.setRightBorderColor(IndexedColors.BLACK.getIndex());  
			headerStyle.setLeftBorderColor(IndexedColors.BLACK.getIndex());  
			headerStyle.setBottomBorderColor(IndexedColors.BLACK.getIndex());
			headerStyle.setAlignment(org.apache.poi.ss.usermodel.HorizontalAlignment.CENTER);
			HSSFFont font = workbook.createFont();
	        font.setColor(IndexedColors.WHITE.getIndex());
	        headerStyle.setFont(font);
	        
	        CellStyle columnStyle=workbook.createCellStyle();
	        columnStyle.setFillForegroundColor(IndexedColors.DARK_RED.getIndex());
	        columnStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND);
	        columnStyle.setBorderBottom(BorderStyle.THIN);
	        columnStyle.setBorderTop(BorderStyle.THIN);
	        columnStyle.setBorderRight(BorderStyle.THIN);
	        columnStyle.setBorderLeft(BorderStyle.THIN);
	        columnStyle.setTopBorderColor(IndexedColors.BLACK.getIndex());  
	        columnStyle.setRightBorderColor(IndexedColors.BLACK.getIndex());  
	        columnStyle.setLeftBorderColor(IndexedColors.BLACK.getIndex());  
	        columnStyle.setBottomBorderColor(IndexedColors.BLACK.getIndex());
	        columnStyle.setAlignment(org.apache.poi.ss.usermodel.HorizontalAlignment.LEFT);
	        columnStyle.setFont(font);
	        
	        CellStyle columnStyleRight=workbook.createCellStyle();
	        columnStyleRight.setFillForegroundColor(IndexedColors.DARK_RED.getIndex());
	        columnStyleRight.setFillPattern(FillPatternType.SOLID_FOREGROUND);
	        columnStyleRight.setBorderBottom(BorderStyle.THIN);
	        columnStyleRight.setBorderTop(BorderStyle.THIN);
	        columnStyleRight.setBorderRight(BorderStyle.THIN);
	        columnStyleRight.setBorderLeft(BorderStyle.THIN);
	        columnStyleRight.setTopBorderColor(IndexedColors.BLACK.getIndex());  
	        columnStyleRight.setRightBorderColor(IndexedColors.BLACK.getIndex());  
	        columnStyleRight.setLeftBorderColor(IndexedColors.BLACK.getIndex());  
	        columnStyleRight.setBottomBorderColor(IndexedColors.BLACK.getIndex());
	        columnStyleRight.setAlignment(org.apache.poi.ss.usermodel.HorizontalAlignment.RIGHT);
	        columnStyleRight.setFont(font);
	        
	        CellStyle cellColorGreen=workbook.createCellStyle();
	        cellColorGreen.setFillForegroundColor(IndexedColors.GREEN.getIndex());
	        cellColorGreen.setFillPattern(FillPatternType.SOLID_FOREGROUND);
	        cellColorGreen.setBorderBottom(BorderStyle.THIN);
	        cellColorGreen.setBorderTop(BorderStyle.THIN);
	        cellColorGreen.setBorderRight(BorderStyle.THIN);
	        cellColorGreen.setBorderLeft(BorderStyle.THIN);
	        cellColorGreen.setTopBorderColor(IndexedColors.BLACK.getIndex());  
	        cellColorGreen.setRightBorderColor(IndexedColors.BLACK.getIndex());  
	        cellColorGreen.setLeftBorderColor(IndexedColors.BLACK.getIndex());  
	        cellColorGreen.setBottomBorderColor(IndexedColors.BLACK.getIndex());
	        cellColorGreen.setAlignment(org.apache.poi.ss.usermodel.HorizontalAlignment.CENTER);
	        cellColorGreen.setFont(font);
	        
	        CellStyle cellColorRed=workbook.createCellStyle();
	        cellColorRed.setFillForegroundColor(IndexedColors.RED.getIndex());
	        cellColorRed.setFillPattern(FillPatternType.SOLID_FOREGROUND);
	        cellColorRed.setBorderBottom(BorderStyle.THIN);
	        cellColorRed.setBorderTop(BorderStyle.THIN);
	        cellColorRed.setBorderRight(BorderStyle.THIN);
	        cellColorRed.setBorderLeft(BorderStyle.THIN);
	        cellColorRed.setTopBorderColor(IndexedColors.BLACK.getIndex());  
	        cellColorRed.setRightBorderColor(IndexedColors.BLACK.getIndex());  
	        cellColorRed.setLeftBorderColor(IndexedColors.BLACK.getIndex());  
	        cellColorRed.setBottomBorderColor(IndexedColors.BLACK.getIndex());
	        cellColorRed.setAlignment(org.apache.poi.ss.usermodel.HorizontalAlignment.CENTER);
	        cellColorRed.setFont(font);
	        
	        HSSFFont headerFont = workbook.createFont();
	        headerFont.setColor(IndexedColors.BLACK.getIndex());
	        headerFont.setBold(true);
	        headerFont.setFontHeightInPoints((short) 12);
	        
	        CellStyle headerStyle1=workbook.createCellStyle();
	        headerStyle1.setAlignment(org.apache.poi.ss.usermodel.HorizontalAlignment.CENTER);
	        headerStyle1.setVerticalAlignment(org.apache.poi.ss.usermodel.VerticalAlignment.CENTER);
	        headerStyle1.setFont(headerFont);
	        
	        CellStyle wrapStyle = workbook.createCellStyle();
	        wrapStyle.setWrapText(true);
	        
	       
	       
	        int incidentsRowNum = 0;
	        int incidentsColNum = 0;
	        int width1 = 18*256;
	        int width2 = 40*256;
	        		int count=0;
	        
			Row incidentsRow = locationExcelReportSheet.createRow(incidentsRowNum);
			Cell cell1 = incidentsRow.createCell(incidentsColNum);
			
			 CellStyle backgroundStyleOdd = workbook.createCellStyle();
			 backgroundStyleOdd.setBorderBottom(BorderStyle.THIN);
			 backgroundStyleOdd.setBorderTop(BorderStyle.THIN);
			 backgroundStyleOdd.setBorderRight(BorderStyle.THIN);
			 backgroundStyleOdd.setBorderLeft(BorderStyle.THIN);
			 backgroundStyleOdd.setTopBorderColor(IndexedColors.BLACK.getIndex());  
			 backgroundStyleOdd.setRightBorderColor(IndexedColors.BLACK.getIndex());  
			 backgroundStyleOdd.setLeftBorderColor(IndexedColors.BLACK.getIndex());  
			 backgroundStyleOdd.setBottomBorderColor(IndexedColors.BLACK.getIndex());
			 backgroundStyleOdd.setFillForegroundColor(IndexedColors.GREY_25_PERCENT.getIndex());
			 backgroundStyleOdd.setFillPattern(FillPatternType.SOLID_FOREGROUND);
//			 backgroundStyleOdd.setDataFormat(format.getFormat("m/d/yy h:mm"));
			 backgroundStyleOdd.setWrapText(true);
			
			CellStyle backgroundStyleEven = workbook.createCellStyle();
			backgroundStyleEven.setBorderBottom(BorderStyle.THIN);
			backgroundStyleEven.setBorderTop(BorderStyle.THIN);
			backgroundStyleEven.setBorderRight(BorderStyle.THIN);
			backgroundStyleEven.setBorderLeft(BorderStyle.THIN);
			backgroundStyleEven.setTopBorderColor(IndexedColors.BLACK.getIndex());  
			backgroundStyleEven.setRightBorderColor(IndexedColors.BLACK.getIndex());  
			backgroundStyleEven.setLeftBorderColor(IndexedColors.BLACK.getIndex());  
			backgroundStyleEven.setBottomBorderColor(IndexedColors.BLACK.getIndex());
			backgroundStyleEven.setFillForegroundColor(IndexedColors.LIGHT_TURQUOISE.getIndex());
			backgroundStyleEven.setFillPattern(FillPatternType.SOLID_FOREGROUND);
			backgroundStyleEven.setWrapText(true);
	        
			CellRangeAddress cellRangeAddress = new CellRangeAddress(incidentsRowNum,
					incidentsRowNum, 0, 5);
			locationExcelReportSheet.addMergedRegion(cellRangeAddress);
			cell1.setCellValue("Carrier Setup Details");
			cell1.setCellStyle(headerStyle1);
			
			incidentsRowNum++;
			
			incidentsRow = locationExcelReportSheet.createRow(incidentsRowNum);
			cell1 = incidentsRow.createCell(incidentsColNum);
			CellRangeAddress cellRangeAddress3 = new CellRangeAddress(incidentsRowNum,
					incidentsRowNum, 0, 5);
			locationExcelReportSheet.addMergedRegion(cellRangeAddress3);
			cell1.setCellValue(" ");
			
			incidentsRowNum++;
			incidentsRow = locationExcelReportSheet.createRow(incidentsRowNum);
			cell1 = incidentsRow.createCell(incidentsColNum);
			cell1.setCellValue("Carrier Code");
			cell1.setCellStyle(headerStyle);
			locationExcelReportSheet.setColumnWidth(incidentsColNum, width1);
			cell1.setCellStyle(headerStyle);
			
			
			incidentsColNum++;
			cell1 = incidentsRow.createCell(incidentsColNum);
			cell1.setCellValue("Carrier Name");
			locationExcelReportSheet.setColumnWidth(incidentsColNum, width2);
			cell1.setCellStyle(headerStyle);
			
			incidentsColNum++;
			cell1 = incidentsRow.createCell(incidentsColNum);
			cell1.setCellValue("Street Address1");
			locationExcelReportSheet.setColumnWidth(incidentsColNum, width2);
			cell1.setCellStyle(headerStyle);
			
			incidentsColNum++;
			cell1 = incidentsRow.createCell(incidentsColNum);
			cell1.setCellValue("Street Address2");
			locationExcelReportSheet.setColumnWidth(incidentsColNum, width2);
			cell1.setCellStyle(headerStyle);
			
			incidentsColNum++;
			cell1 = incidentsRow.createCell(incidentsColNum);
			cell1.setCellValue("Street Address3");
			locationExcelReportSheet.setColumnWidth(incidentsColNum, width2);
			cell1.setCellStyle(headerStyle);
			
			incidentsColNum++;
			cell1 = incidentsRow.createCell(incidentsColNum);
			cell1.setCellValue("City");
			locationExcelReportSheet.setColumnWidth(incidentsColNum, width2);
			cell1.setCellStyle(headerStyle);
			
			incidentsColNum++;
			cell1 = incidentsRow.createCell(incidentsColNum);
			cell1.setCellValue("State Code");
			locationExcelReportSheet.setColumnWidth(incidentsColNum, width2);
			cell1.setCellStyle(headerStyle);
			
			incidentsColNum++;
			cell1 = incidentsRow.createCell(incidentsColNum);
			cell1.setCellValue("Zip Code");
			locationExcelReportSheet.setColumnWidth(incidentsColNum, width2);
			cell1.setCellStyle(headerStyle);
			
			
			incidentsColNum++;
			cell1 = incidentsRow.createCell(incidentsColNum);
			cell1.setCellValue("Carrier Type");
			locationExcelReportSheet.setColumnWidth(incidentsColNum, width1);
			cell1.setCellStyle(headerStyle);
			
			
//			incidentsColNum++;
//			cell1 = incidentsRow.createCell(incidentsColNum);
//			cell1.setCellValue("Payment Method");
//			locationExcelReportSheet.setColumnWidth(incidentsColNum, width1);
//			cell1.setCellStyle(headerStyle);
			
			
			
			incidentsColNum++;
			cell1 = incidentsRow.createCell(incidentsColNum);
			cell1.setCellValue("Status");
			locationExcelReportSheet.setColumnWidth(incidentsColNum, width2);
			cell1.setCellStyle(headerStyle);
			
			incidentsColNum++;
			cell1 = incidentsRow.createCell(incidentsColNum);
			cell1.setCellValue("Currency");
			locationExcelReportSheet.setColumnWidth(incidentsColNum, width1);
			cell1.setCellStyle(headerStyle);
			
			int rowColor = 0;
			
			if(arrayList!= null){
				for(CarrierSetupDTO carrierSetupDTO:arrayList){
					rowColor++;
					count++;
					incidentsRowNum++;
					incidentsColNum = 0;
					incidentsRow = locationExcelReportSheet.createRow(incidentsRowNum);
					cell1 = incidentsRow.createCell(incidentsColNum);
					cell1.setCellValue(carrierSetupDTO.getCarrierCd());
					if(rowColor%2==0){
						cell1.setCellStyle(backgroundStyleEven);
					}else{
						cell1.setCellStyle(backgroundStyleOdd);
					}
					
					incidentsColNum++;
					cell1 = incidentsRow.createCell(incidentsColNum);
					
					cell1.setCellValue(carrierSetupDTO.getCarrierName());
					cell1.setCellStyle(wrapStyle);
					if(rowColor%2==0){
						cell1.setCellStyle(backgroundStyleEven);
					}else{
						cell1.setCellStyle(backgroundStyleOdd);
					}
					
					incidentsColNum++;
					cell1 = incidentsRow.createCell(incidentsColNum);
					
					cell1.setCellValue(carrierSetupDTO.getStreet1Address());
					cell1.setCellStyle(wrapStyle);
					if(rowColor%2==0){
						cell1.setCellStyle(backgroundStyleEven);
					}else{
						cell1.setCellStyle(backgroundStyleOdd);
					}
					
					
					incidentsColNum++;
					cell1 = incidentsRow.createCell(incidentsColNum);
					
					cell1.setCellValue(carrierSetupDTO.getStreet2Address());
					cell1.setCellStyle(wrapStyle);
					if(rowColor%2==0){
						cell1.setCellStyle(backgroundStyleEven);
					}else{
						cell1.setCellStyle(backgroundStyleOdd);
					}
					
					incidentsColNum++;
					cell1 = incidentsRow.createCell(incidentsColNum);
					
					cell1.setCellValue(carrierSetupDTO.getStreet3Address());
					cell1.setCellStyle(wrapStyle);
					if(rowColor%2==0){
						cell1.setCellStyle(backgroundStyleEven);
					}else{
						cell1.setCellStyle(backgroundStyleOdd);
					}
					
					incidentsColNum++;
					cell1 = incidentsRow.createCell(incidentsColNum);
					
					cell1.setCellValue(carrierSetupDTO.getCityName().trim());
					cell1.setCellStyle(wrapStyle);
					if(rowColor%2==0){
						cell1.setCellStyle(backgroundStyleEven);
					}else{
						cell1.setCellStyle(backgroundStyleOdd);
					}
					
					incidentsColNum++;
					cell1 = incidentsRow.createCell(incidentsColNum);
					
					cell1.setCellValue(carrierSetupDTO.getStateCd().trim());
					cell1.setCellStyle(wrapStyle);
					if(rowColor%2==0){
						cell1.setCellStyle(backgroundStyleEven);
					}else{
						cell1.setCellStyle(backgroundStyleOdd);
					}
					
					
					incidentsColNum++;
					cell1 = incidentsRow.createCell(incidentsColNum);
					
					cell1.setCellValue(carrierSetupDTO.getZipCd().trim());
					cell1.setCellStyle(wrapStyle);
					if(rowColor%2==0){
						cell1.setCellStyle(backgroundStyleEven);
					}else{
						cell1.setCellStyle(backgroundStyleOdd);
					}
					
					incidentsColNum++;
					cell1 = incidentsRow.createCell(incidentsColNum);
					
					cell1.setCellValue(carrierSetupDTO.getCarrierTypeDesc());
					if(rowColor%2==0){
						cell1.setCellStyle(backgroundStyleEven);
					}else{
						cell1.setCellStyle(backgroundStyleOdd);
					}
					
					incidentsColNum++;
					cell1 = incidentsRow.createCell(incidentsColNum);
					
					cell1.setCellValue(carrierSetupDTO.getStatusDesc()); 
					if(rowColor%2==0){
						cell1.setCellStyle(backgroundStyleEven);
					}else{
						cell1.setCellStyle(backgroundStyleOdd);
					}
					
					incidentsColNum++;
					cell1 = incidentsRow.createCell(incidentsColNum);
					
					cell1.setCellValue(carrierSetupDTO.getCurrencyCd()); 
					if(rowColor%2==0){
						cell1.setCellStyle(backgroundStyleEven);
					}else{
						cell1.setCellStyle(backgroundStyleOdd);
					}
					
//					incidentsColNum++;
//					cell1 = incidentsRow.createCell(incidentsColNum);
//					
//					cell1.setCellValue(carrierSetupDTO.getRegionCd()); 
//					if(rowColor%2==0){
//						cell1.setCellStyle(backgroundStyleEven);
//					}else{
//						cell1.setCellStyle(backgroundStyleOdd);
//					}

				}
				incidentsRowNum=incidentsRowNum+3;
				incidentsRow = locationExcelReportSheet.createRow(incidentsRowNum);
				cell1 = incidentsRow.createCell(0);
				cell1.setCellValue("Total Record Count:"+count); 
				}
				}catch (Exception e) {
					log.error(e.getMessage());
	}
		return workbook;
}
	
	public static String leftAddZero(String variable, int maxSize){
	    StringBuilder strBuff = new StringBuilder();
	    int len = 0;
	    if( variable != null ){
	        len = variable.length();
	        strBuff.append(variable);
	    }    
	    String tempStr="";
	    for (int i = len; i < maxSize; i++){
	    
	    	tempStr+="0";
	    }
	    return tempStr+strBuff.toString();
	}

	
	public static LocationIndexDTO formatingPhoneNo(LocationIndexDTO generateExcelDto){

		LocationIndexDTO formattingExcelDto=new LocationIndexDTO();;
		StringBuilder formattingAddress=new StringBuilder();
		int count=0;
		
			if(null!=generateExcelDto.getPhoneAcNo() &&  !("".equals(generateExcelDto.getPhoneAcNo().trim())) ){
				formattingAddress.append(generateExcelDto.getPhoneAcNo());	
				count++;
			}
			
			if(null!=generateExcelDto.getPhoneExcNo() &&  !("".equals(generateExcelDto.getPhoneExcNo().trim())) ){
				if(count>0){
					formattingAddress.append("-");	
				}
				count++;
				formattingAddress.append(generateExcelDto.getPhoneExcNo());	
				
			}
			
			if(null!=generateExcelDto.getPhoneNo() &&  !("".equals(generateExcelDto.getPhoneNo().trim())) ){
				if(count>0){
					formattingAddress.append("-");	
				}
				count++;
				formattingAddress.append(generateExcelDto.getPhoneNo());	
				
			}
			
			if(null!=generateExcelDto.getPhoneExtnsnNo() &&  !("".equals(generateExcelDto.getPhoneExtnsnNo().trim())) ){
				if(count>0){
					formattingAddress.append("-");	
				}
				count++;
				formattingAddress.append(generateExcelDto.getPhoneExtnsnNo());	
				
			}
			
		
			formattingExcelDto.setAddressFormatting(formattingAddress.toString());
			return formattingExcelDto;
		
		
	}
	
	public static LocationIndexDTO formatingLocationType(LocationIndexDTO generateExcelDto){

		LocationIndexDTO formattingExcelDto=new LocationIndexDTO();;
		StringBuilder formattingLocationTypeFinal=new StringBuilder();
		int count=0;
	
			if(null!=generateExcelDto.getCdtvalueTx() &&  !("".equals(generateExcelDto.getCdtvalueTx().trim())) ){
				formattingLocationTypeFinal.append(generateExcelDto.getCdtvalueTx().trim());	
				count++;
			}if(null!=generateExcelDto.getCdtvalueTx2() &&  !("".equals(generateExcelDto.getCdtvalueTx2().trim())) ){
				if(count>0){
					formattingLocationTypeFinal.append(",");	
				}
				count++;
				formattingLocationTypeFinal.append(generateExcelDto.getCdtvalueTx2().trim());	
			}if(null!=generateExcelDto.getCdtvalueTx3() &&  !("".equals(generateExcelDto.getCdtvalueTx3().trim())) ){
				if(count>0){
					formattingLocationTypeFinal.append(",");	
				}
				formattingLocationTypeFinal.append(generateExcelDto.getCdtvalueTx3().trim());	
			}
			formattingExcelDto.setLocationTypeFormatting(formattingLocationTypeFinal.toString().trim());
			return formattingExcelDto;
	}
}

