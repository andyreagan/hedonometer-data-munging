private String depunctuateStringEnglish(String in)
     {
//         working spec.:
//         continue to split on white space (as we discussed), but remove basic punctuation when leading or trailing, e.g. this list from Peter:
//         . (period)
//         , (apostrophe)  TODO: "," or "'" ?
//         ; (semicolon)
//         [!+] (exclamation mark, possibly repeated)
//        [?+] (question mark, possibly repeated)
//         [!?+] (mixed exclamation and question marks, possibly repeated).
//         dashes between words (em dash, en dash)
//         " (double quotes)
//         ' (single quotes; trickier---leave inside words definitely; may want to just leave them and see what kind of junk we get).
 
           //items from spec.
           //TODO: should we do all of these only when leading/trailing, or anywhere?
           in = in.replaceAll("\\.\\.\\."," ");  //ellipsis
           in = in.replaceAll("\\.( )"," ");           //period (properly punctuated)
           in = in.replaceAll("[\\;,]"," ");           // semi, comma
           in = in.replaceAll("\\-\\-\\-"," "); //em dash ; TODO: need to do unicode em
           in = in.replaceAll("\\-\\-"," ");           //en dash ; TODO: need to do unicode en
                                                                 //NB: single dash left in
           in = in.replaceAll("\""," ");               //"
           in = in.replaceAll("!+"," ");               //!+ 
           in = in.replaceAll("\\?+"," ");       //?+  (these two passively fix !?+ and ?!+)
          
           //items in spirit of spec.
           in = in.replaceAll("[\\(\\)\\?]"," ");           //()"?
           in = in.replaceAll(":( )", " ");                 //": "    (properly punctuated colon; leaves http://* alone)
           in = in.replaceAll("^\\.|\\.$"," ");             //period at beginning or end of line (no following space but proper)
           in = in.replaceAll("''","");                     //strike ''  (doubled single quotes used as " quote
           in = in.replaceAll("[^\\x00-\\x7F]", "");   //strike all non-ascii (trader parser overhead for counting overhead later)
                     
           return in.trim();
     }
