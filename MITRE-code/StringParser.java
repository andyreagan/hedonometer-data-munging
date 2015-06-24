package org.mitre.hedonometer.parsers;

import java.io.UnsupportedEncodingException;
import java.util.StringTokenizer;

import org.mitre.hedonometer.data.DailyDataMap;
import org.mitre.hedonometer.data.HedoDate;
import org.mitre.hedonometer.data.TweetProcessingMetadata;
import org.mitre.hedonometer.normalizers.HedoStringTokenizer;
import org.mitre.hedonometer.readers.HedoHashMapReader;
import org.mitre.hedonometer.readers.MTReader;

import com.google.gson.JsonElement;

public class StringParser {

	public TweetProcessingMetadata parse(String myTextString, String lang, MTReader myMTMap,
			HedoHashMapReader myFullHourlyMap, DailyDataMap myDailyDataMap, HedoDate myDate) 
	{
		String dpString = new String();
		TweetProcessingMetadata myStringMetadata = new TweetProcessingMetadata();
		
		if (lang.equals("en"))
		{
			dpString = depunctuateStringEnglish(myTextString);
		}
		else if (lang.equals("ar")) {
			dpString = depunctuateStringArabic(myTextString);
		}
		else if (lang.equals("es")) {
			dpString = depunctuateStringEnglish(myTextString);//[sic] or appropriate depunctuation for the language;
		}
		   
		//
		HedoStringTokenizer st = null;
		//TODO: make sure we are not removing stop words like "is" and "this".  They have valence in the dictionary
		if (lang.equals("en"))
		{
			st = new HedoStringTokenizer(dpString);	
			
		}
		else if (lang.equals("ar"))
		{
			st = new HedoStringTokenizer(dpString, "ar");
		}
		//etc. for "es" , "ru" , ...)	
		
		String newString = "";
		String testString = "";
		while (st.hasMoreTokens())
		{
			myStringMetadata.totalWordsParsed+=1; //count tokens (no tokencount method)
			
			String token = st.nextToken().toString();
			//here is where to apply rules
			//token = token.toLowerCase();
			
			newString +="#"+myFullHourlyMap.reverseHashmap.get(token) + token;
			//check that it exists in hedohashmap
			int index;
			if (myFullHourlyMap.reverseHashmap.get(token)!=null)
			{
				//System.out.println("keeping "+token);
				
				index = myFullHourlyMap.reverseHashmap.get(token);
				
				if (myDailyDataMap.hourlyFrequency.get(myDate.hour)==null)
				{
					myDailyDataMap.hourlyFrequency.put(myDate.hour, new Integer[myFullHourlyMap.forwardHashmap.size()]);
				}
				Integer[] myFreqVect = myDailyDataMap.hourlyFrequency.get(myDate.hour);
				//TODO: SERIOUS  index is off by one !?  works in postprocessing code though
				int offsetIndex = --index;
				
				if (myFreqVect[(offsetIndex)]==null) 
				{
					
					myFreqVect[(offsetIndex)]=1;
				}
				else
				{
					
					myFreqVect[(offsetIndex)]++;
				}
				myDailyDataMap.hourlyFrequency.put(myDate.hour, myFreqVect);
				myStringMetadata.totalWordsCounted+=1;
			}
			else
			{
				//System.out.println("discarding "+token);
			}
			//add one to it
		}
		//System.out.println("parsed: "+newString);
		return myStringMetadata;
	}

	private String depunctuateStringEnglish(String in) 
	{
//		working spec.:
//		continue to split on white space (as we discussed), but remove basic punctuation when leading or trailing, e.g. this list from Peter:
//		. (period)
//		, (apostrophe)  TODO: "," or "'" ?
//		; (semicolon)
//		[!+] (exclamation mark, possibly repeated)
//		[?+] (question mark, possibly repeated)
//		[!?+] (mixed exclamation and question marks, possibly repeated).
//		dashes between words (em dash, en dash)
//		" (double quotes)
//		' (single quotes; trickier---leave inside words definitely; may want to just leave them and see what kind of junk we get).

		//items from spec.
		//TODO: should we do all of these only when leading/trailing, or anywhere?
		in = in.replaceAll("\\.\\.\\."," ");  	//ellipsis
		in = in.replaceAll("\\.( )"," ");  		//period (properly punctuated)
		in = in.replaceAll("[\\;,]"," ");  		// semi, comma 
		in = in.replaceAll("\\-\\-\\-"," "); 	//em dash ; TODO: need to do unicode em
		in = in.replaceAll("\\-\\-"," "); 		//en dash ; TODO: need to do unicode en
												//NB: single dash left in
		in = in.replaceAll("\""," "); 			//"
		in = in.replaceAll("!+"," "); 			//!+  
		in = in.replaceAll("\\?+"," "); 		//?+  (these two passively fix !?+ and ?!+)
		
		//items in spirit of spec.
		in = in.replaceAll("[\\(\\)\\?]"," "); 		//()"?
		in = in.replaceAll(":( )", " ");  			//": "    (properly punctuated colon; leaves http://* alone)
		in = in.replaceAll("^\\.|\\.$"," ");   		//period at beginning or end of line (no following space but proper)
		in = in.replaceAll("''","");				//strike ''  (doubled single quotes used as " quote
		in = in.replaceAll("[^\\x00-\\x7F]", "");	//strike all non-ascii (trader parser overhead for counting overhead later)
				
		return in.trim();
	}
	
	private String depunctuateStringArabic(String in) 
	{
//		in = in.replaceAll("\\.\\.\\."," ");  	//ellipsis
//		in = in.replaceAll("\\.( )"," ");  		//period (properly punctuated)
//		in = in.replaceAll("[\\;,]"," ");  		// semi, comma 
//		in = in.replaceAll("\\-\\-\\-"," "); 	//em dash ; TODO: need to do unicode em
//		in = in.replaceAll("\\-\\-"," "); 		//en dash ; TODO: need to do unicode en
//												//NB: single dash left in
//		in = in.replaceAll("\""," "); 			//"
//		in = in.replaceAll("!+"," "); 			//!+  
//		in = in.replaceAll("\\?+"," "); 		//?+  (these two passively fix !?+ and ?!+)
//		
//		//items in spirit of spec.
//		in = in.replaceAll("[\\(\\)\\?]"," "); 		//()"?
//		in = in.replaceAll(":( )", " ");  			//": "    (properly punctuated colon; leaves http://* alone)
//		in = in.replaceAll("^\\.|\\.$"," ");   		//period at beginning or end of line (no following space but proper)
//		in = in.replaceAll("''","");				//strike ''  (doubled single quotes used as " quote
		
		try {
			in = new String (in.getBytes(),"UTF-8");
		} catch (UnsupportedEncodingException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		//TODO: add unicode replacements from http://www.unicode.org/charts/PDF/U0600.pdf
		in = in.replaceAll("[^\\u0600-\\u06ff]", " ");	//strike all non-arabic (trader parser overhead for counting overhead later)
				
		return in.toLowerCase().trim();
	}	

	
	
	

}
