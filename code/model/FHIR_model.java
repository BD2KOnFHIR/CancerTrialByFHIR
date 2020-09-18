package ijmi.fhirModel;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.Reader;
import java.math.BigInteger;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Random;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;
import org.hl7.fhir.r4.model.Bundle;
import org.hl7.fhir.r4.model.CodeableConcept;
import org.hl7.fhir.r4.model.Coding;
import org.hl7.fhir.r4.model.Condition;
import org.hl7.fhir.r4.model.Extension;
import org.hl7.fhir.r4.model.FamilyMemberHistory;
import org.hl7.fhir.r4.model.Medication;
import org.hl7.fhir.r4.model.Observation;
import org.hl7.fhir.r4.model.Patient;
import org.hl7.fhir.r4.model.Procedure;
import org.hl7.fhir.r4.model.Ratio;
import org.hl7.fhir.r4.model.StringType;

import ca.uhn.fhir.context.FhirContext;
import ca.uhn.fhir.parser.IParser;


public class FHIR_model {
	
	public static void main(String[] args) throws Exception{
		HashMap<String,FHIRConcept_Bean> concept_observation=getConceptMapping("Observation");
		HashMap<String,FHIRConcept_Bean> concept_medication=getConceptMapping("Medication");
		HashMap<String,FHIRConcept_Bean> concept_patient=getConceptMapping("Patient");
		HashMap<String,FHIRConcept_Bean> concept_procedure=getConceptMapping("Procedure");
//		List<Map.Entry<String,String>> input_data=read_exampleData("./src/ijmi/fhirModel/sample_data.csv");
		ArrayList<ArrayList<Map.Entry<String,String>>> input_datas=read_Data
				("./src/ijmi/fhirModel/revision_task_CRF.tsv") ; 
		File dir=new File("./src/ijmi/fhirModel/fhir_json");
		dir.mkdirs();
		for(ArrayList<Map.Entry<String,String>> input_data:input_datas){
			String id="1024";
			for (int i = 0; i < input_data.size(); i++) {
				Map.Entry<String,String> entry=input_data.get(i);
				if(entry.getKey().equals("id")){
					id=entry.getValue();
				}
			}
			writeFHIR_all( concept_observation,
					concept_medication,
					concept_patient,
					concept_procedure,
					input_data, Integer.valueOf(id), "./src/ijmi/fhirModel/fhir_json");
		}
		
		
	}
	
	
	public static List<Map.Entry<String,String>> read_exampleData(String file) throws IOException{
		List<Map.Entry<String,String>> data=new ArrayList<Map.Entry<String,String>>();
		Reader reader = Files.newBufferedReader(Paths.get(file));
		CSVParser csvParser = new CSVParser(reader, CSVFormat.EXCEL);  
		List<CSVRecord> csvRecords=csvParser.getRecords();
		HashMap<String,Integer> idx=new HashMap<>();
		for (CSVRecord csvRecord : csvRecords){ 
			String id=csvRecord.get(0).toLowerCase();	
			String value=csvRecord.get(1).toLowerCase();	
			Map<String,String> map=new HashMap<>();
			map.put(id, value);
			for(Entry<String,String> entry:map.entrySet()){
				data.add(entry);
			}
		}
		return data;
	}
	
	public static ArrayList<ArrayList<Map.Entry<String,String>>> read_Data(String file) throws IOException{
		ArrayList<ArrayList<Map.Entry<String,String>>> all_data=new ArrayList<ArrayList<Map.Entry<String,String>>>();
		
		
		Reader reader = Files.newBufferedReader(Paths.get(file));
		CSVParser csvParser = new CSVParser(reader, CSVFormat.EXCEL.withDelimiter('\t'));  
		List<CSVRecord> csvRecords=csvParser.getRecords();
		int i=0;
		HashMap<Integer,String> idx=new HashMap<>();
		for (CSVRecord csvRecord : csvRecords){ 
			i++;
			if(i==1){
				idx.put(0, "id");
				for (int j = 1; j < csvRecord.size(); j++) {
					idx.put(j, csvRecord.get(j).toLowerCase());
				}
				
			}else{
				ArrayList<Map.Entry<String,String>> data=new ArrayList<Map.Entry<String,String>>();
				for (int j = 0; j < csvRecord.size(); j++) {
					HashMap<String,String> local=new HashMap<>();
					String id=idx.get(j).toLowerCase();	
					String value=csvRecord.get(j).toLowerCase();	
					Map<String,String> map=new HashMap<>();
					map.put(id, value);
					for(Entry<String,String> entry:map.entrySet()){
						data.add(entry);
					}
				}
				all_data.add(data);
			}
			
		}
		return all_data;
	}
	
	public static HashMap<String,FHIRConcept_Bean> getConceptMapping(String filter) throws IOException{
		String input="./src/ijmi/fhirModel/DataMpdel_mapping.csv";
		HashSet<String> ids=new HashSet<>();
		Reader reader = Files.newBufferedReader(Paths.get(input));
		CSVParser csvParser = new CSVParser(reader, CSVFormat.EXCEL);  
		List<CSVRecord> csvRecords=csvParser.getRecords();
		HashMap<String,Integer> idx=new HashMap<>();
		HashMap<String,FHIRConcept_Bean> map=new HashMap<>();
		for (CSVRecord csvRecord : csvRecords){ 
			
			String key=csvRecord.get(0).toLowerCase();
			String value_tmp=csvRecord.get(1);
			value_tmp=value_tmp.replace("new "+filter+".value (code =", "").toString();
			System.out.println(value_tmp);
			String code=value_tmp.substring(0,value_tmp.indexOf("(")).trim();
			String value=value_tmp.substring(value_tmp.indexOf("(")+1,value_tmp.lastIndexOf(")")).trim();
			FHIRConcept_Bean bean =new FHIRConcept_Bean();
			bean.setId(code);
			bean.setText(value);
			map.put(key, bean);
			
		}
		return map;
	}
	
	public static void writeFHIR_all(HashMap<String,FHIRConcept_Bean> concept_observation,
			HashMap<String,FHIRConcept_Bean> concept_medication,
			HashMap<String,FHIRConcept_Bean> concept_patient,
			HashMap<String,FHIRConcept_Bean> concept_procedure,
			List<Map.Entry<String,String>> input_data,
			int id, String outdir) throws Exception {
		
		
		Bundle bundle = new Bundle();
		bundle.setType(Bundle.BundleType.COLLECTION);
		
		for (int i = 0; i < input_data.size(); i++) {
			
			Entry<String,String> entry=input_data.get(i);
				
			
			
			String key=entry.getKey();
			String value=entry.getValue();
			
			if(key.startsWith("colorectal.subject.vitalstatus")){
				Patient patient	=new Patient();
				Extension e= new Extension();
				e.setId("vital status");
				e.setValue(new StringType(value));
				bundle.addEntry()
				   .setResource(patient);
				patient.addExtension(e);
				patient.setId(String.valueOf(id));
			}
			if(key.startsWith("colorectal.macro")||
				key.startsWith("colorectal.micro")||
				key.startsWith("colorectal.preanalytic")||
				key.startsWith("colorectal.synthesisoverview")){
				if(!concept_observation.containsKey(key)){
					continue;
				}
				FHIRConcept_Bean bean=concept_observation.get(key);
				String code=bean.getId();
				String text=bean.getText();
				
				Observation observation=new Observation();
				bundle.addEntry().setResource(observation);
				observation.setValue(new StringType(value));
				CodeableConcept concept=new CodeableConcept();
				concept.setText(text);
				Coding coding=new Coding();
				String system="";
				if(code.contains("http:")){
					system="http://cap.org/protocols";
					code=code.substring(code.indexOf("#")+1,code.length()).trim();
				}
				if(code.contains("LOINC")){
					system="https://fhir.loinc.org/CodeSystem/?url=http://loinc.org";
					code=code.substring(code.indexOf("#")+1,code.length()).trim();
				}
				if(code.contains("SNOMED")){
					system="http://snomed.info/sct";
					code=code.substring(code.indexOf("#")+1,code.length()).trim();
				}
				coding.setSystem(system);
				coding.setCode(code);
				concept.addCoding(coding);
				observation.setCode(concept);
			}
			
			if(key.startsWith("colorectal.laboratorytest")){
				if(!concept_observation.containsKey(key)){
					continue;
				}
				FHIRConcept_Bean bean=concept_observation.get(key);
				String code=bean.getId();
				String text=bean.getText();
				String key_real=key.substring(0,key.lastIndexOf("."));
				String type=key.substring(key.lastIndexOf(".")+1,key.length());
			}
			
			if(key.startsWith("colorectal.medication.treatment.unit")){
				continue;
			}
			if(key.startsWith("colorectal.medication.treatment.value")){
				continue;
			}
			if(key.startsWith("colorectal.medication.treatment.code")){
				
				String system="http://www.nlm.nih.gov/research/umls/rxnorm";
				String code="";
				String text=value;
				if(value.toLowerCase().equals("leucovorin")){
					code="6313";
				}
				if(value.toLowerCase().equals("fluorouracil")){
					code="4492";
				}
				if(value.toLowerCase().equals("oxaliplatin")){
					code="32592";
				}
				if(value.toLowerCase().equals("cetuximab")){
					code="318341";
				}
				
				Medication medication=new Medication();
				bundle.addEntry().setResource(medication);
				CodeableConcept concept=new CodeableConcept();
				concept.setText(text);
				Coding coding=new Coding();
				
				if(code.contains("http:")){
					system="http://cap.org/protocols";
					code=code.substring(code.indexOf("#")+1,code.length()).trim();
				}
				if(code.contains("LOINC")){
					system="https://fhir.loinc.org/CodeSystem/?url=http://loinc.org";
					code=code.substring(code.indexOf("#")+1,code.length()).trim();
				}
				if(code.contains("SNOMED")){
					system="http://snomed.info/sct";
					code=code.substring(code.indexOf("#")+1,code.length()).trim();
				}
				coding.setSystem(system);
				coding.setCode(code);
				concept.addCoding(coding);
				medication.setCode(concept);
				
				for (int j = 0; j < input_data.size(); j++) {
					Entry<String,String> entry_1=input_data.get(j);
					
					if(entry_1.getKey().startsWith("colorectal.medication.treatment.unit")){
						
						Extension extension_1=new Extension();
						extension_1.setValue(new StringType(entry_1.getValue()));
						extension_1.setId("unit");
						medication.addExtension(extension_1);
					}
					if(entry_1.getKey().startsWith("colorectal.medication.treatment.unit")){
						Extension extension_1=new Extension();
						extension_1.setValue(new StringType(entry_1.getValue()));
						extension_1.setId("unit");
						medication.addExtension(extension_1);
					}
				}
				
			}
			
			if(key.startsWith("colorectal.surgery.date")){
				continue;
			}
			if(key.startsWith("colorectal.surgery.resectionextent")){
				continue;
			}
			if(key.startsWith("colorectal.surgery.type")){
				
				Procedure procedure=new Procedure();
				bundle.addEntry().setResource(procedure);
				
				CodeableConcept concept=new CodeableConcept();
				concept.setText(value);
				String system="";
				String code= "";
				Coding coding=new Coding();
				if(value.toLowerCase().equals("laparoscopy")){
					 system="https://fhir.loinc.org/CodeSystem/?url=http://loinc.org";
					 code= "LA15411-4";
				}
				
				coding.setSystem(system);
				coding.setCode(code);
				concept.addCoding(coding);
				procedure.setCode(concept);
				
				
				for (int j = 0; j < input_data.size(); j++) {
					Entry<String,String> entry_1=input_data.get(j);
					
					if(entry_1.getKey().startsWith("colorectal.surgery.date")){
						procedure.setPerformed(new StringType(entry_1.getValue()));
					}
					if(entry_1.getKey().startsWith("colorectal.surgery.resectionextent")){
						Extension e =new Extension();
						e.setId("resection extent");
						e.setValue(new StringType(entry_1.getValue()));
						procedure.addExtension(e);
					}
				}
				
			}
		}
		
				
			FhirContext ctx = FhirContext.forR4();
			IParser parser = ctx.newJsonParser();
			// Indent the output
			parser.setPrettyPrint(true);
			// Serialize it
			
			String serialized = parser.encodeResourceToString(bundle);
//			System.out.println(serialized);
			FileWriter fw=new FileWriter(new File(outdir+"/"+id+".json"));
			fw.write(serialized);
			fw.flush();
			fw.close();
		}
		
	

}
