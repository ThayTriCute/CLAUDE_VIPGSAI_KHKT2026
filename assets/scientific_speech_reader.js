/* One speech controller per page. Pure planning functions are also tested in Node. */
(function (root) {
  "use strict";
  const VERSION = "20261102.2";
  const VI_MARKS = /[ăâđêôơưàáảãạằắẳẵặầấẩẫậèéẻẽẹềếểễệìíỉĩịòóỏõọồốổỗộờớởỡợùúủũụừứửữựỳýỷỹỵ]/iu;
  const EN_WORDS = new Set(("a an the this that these those is are was were be been being am it its " +
    "of to and or but for from in on at by with without as if then than because when where which who " +
    "what why how not no yes do does did have has had can could will would shall should may might must " +
    "i you he she we they my your his her our their them us me all some any each every also there here " +
    "answer question choose correct incorrect complete following sentence word words vocabulary grammar " +
    "read write listen speak learn learning school teacher student students science scientific " +
    "photosynthesis mitochondria chromosome chromosomes nucleus nuclear atom atoms molecule molecules " +
    "oxygen hydrogen carbon dioxide acid base reaction energy force velocity acceleration mass electric " +
    "current voltage resistance derivative integral function equation vector probability temperature " +
    "perseverance inspirational distinguished dedication life stories inspiring people world " +
    "hello good morning afternoon english vietnamese native pronunciation warm voice volume pressure " +
    "computer algorithm algorithms data information history geography technology ecosystem biodiversity " +
    "cafe café naive naïve resume résumé").split(/\s+/));
  const LOAN_ACCENTS = new Set(["café", "naïve", "résumé"]);
  const VI_PLAIN = new Set("va la cua trong cho mot hai ba bon nam sau bay tam chin muoi khong co em anh chi hoc sinh thay toan ly hoa van dung sai cau bai phan so cong tru nhan chia".split(" "));
  const SUBJECT_TERMS = {
    "Toán học": {"TXĐ":"tập xác định", "TCĐ":"tiệm cận đứng", "TCN":"tiệm cận ngang", "TCX":"tiệm cận xiên", "BBT":"bảng biến thiên", "Oxyz":"hệ tọa độ ô ích y dét", "Oxy":"hệ tọa độ ô ích y"},
    "Vật lý": {"AC":"dòng điện xoay chiều", "DC":"dòng điện một chiều"},
    "Hóa học": {"pH":"pê hát"},
    "Sinh học": {"ADN":"a đê en", "ARN":"a rờ en", "DNA":"đi en ây", "RNA":"a rờ en ây", "ATP":"a tê pê"},
    "Tin học": {"CPU":"xi pi iu", "RAM":"ram", "HTML":"hát tê em lờ", "SQL":"ét kiu eo"},
    "Địa lý": {"GDP":"gi đi pi", "GIS":"gi ai ét"}
  };
  function subjectName(value) {
    return ({"Toán":"Toán học", "Vật lí":"Vật lý", "Hoá học":"Hóa học", "Địa lí":"Địa lý"})[value] || value;
  }
  function languageOf(text, fallback) {
    const words = String(text).normalize("NFC").toLowerCase().match(/[\p{L}]+/gu) || [];
    if (words.some(w => VI_MARKS.test(w) && !LOAN_ACCENTS.has(w))) return "vi";
    const en = words.filter(w => EN_WORDS.has(w)).length;
    const vi = words.filter(w => VI_PLAIN.has(w)).length;
    if (vi >= 2 && vi > en) return "vi";
    if (en > vi || (en && words.length === 1)) return "en";
    return fallback === "en" ? "en" : "vi";
  }
  function replaceTerms(text, subject) {
    const terms = {...(SUBJECT_TERMS[subjectName(subject)] || {})};
    if (subject === "Khoa học tự nhiên") Object.assign(terms, SUBJECT_TERMS["Vật lý"], SUBJECT_TERMS["Hóa học"], SUBJECT_TERMS["Sinh học"]);
    for (const [term, spoken] of Object.entries(terms)) {
      text = text.replace(new RegExp("(?<![\\p{L}\\p{N}_])" + term + "(?![\\p{L}\\p{N}_])", "gu"), spoken);
    }
    return text;
  }
  function formulaSpeech(source, lang) {
    const en = lang === "en";
    let index = 0, depth = 0;
    const say = (vi, english) => en ? english : vi;
    const commands = {
      alpha:["an pha","alpha"], beta:["bê ta","beta"], gamma:["gam ma","gamma"],
      delta:["đen ta","delta"], Delta:["đen ta","delta"], omega:["ô mê ga","omega"],
      Omega:["ôm","ohm"], pi:["pi","pi"], theta:["thê ta","theta"],
      infty:["vô cực","infinity"], leq:["nhỏ hơn hoặc bằng","less than or equal to"],
      le:["nhỏ hơn hoặc bằng","less than or equal to"], geq:["lớn hơn hoặc bằng","greater than or equal to"],
      ge:["lớn hơn hoặc bằng","greater than or equal to"], neq:["khác","not equal to"],
      notin:["không thuộc","not an element of"], in:["thuộc","an element of"],
      approx:["xấp xỉ","approximately"], times:["nhân","times"], cdot:["nhân","times"],
      pm:["cộng trừ","plus or minus"], to:["tiến tới","approaches"],
      rightarrow:["mũi tên sang phải","right arrow"], Rightarrow:["suy ra","implies"],
      Leftrightarrow:["tương đương","if and only if"], forall:["với mọi","for all"],
      exists:["tồn tại","there exists"], subset:["là tập con của","is a subset of"],
      subseteq:["là tập con hoặc bằng","is a subset of or equal to"],
      sin:["sin","sine"], cos:["cô sin","cosine"], tan:["tang","tangent"],
      cot:["cô tang","cotangent"], ln:["lô ga tự nhiên","natural logarithm"], log:["lô ga","logarithm"],
      int:["tích phân","integral"], sum:["tổng","sum"], lim:["giới hạn","limit"],
      partial:["đạo hàm riêng","partial"], nabla:["na bla","nabla"],
      nearrow:["mũi tên lên phải","upward right arrow"], searrow:["mũi tên xuống phải","downward right arrow"]
    };
    function group() {
      while (/\s/.test(source[index] || "") && index < source.length) index++;
      if (source[index] !== "{") {
        if (index >= source.length) throw Error("Công thức thiếu đối số.");
        return source[index++];
      }
      index++;
      return parse(true);
    }
    function chemicalGroup() {
      while(source[index] === " ") index++;
      if(source[index++] !== "{") throw Error("Công thức hóa học thiếu ngoặc.");
      const start=index;
      let count=1;
      while(index<source.length && count) { const c=source[index++]; if(c==="{") count++; if(c==="}") count--; }
      if(count) throw Error("Công thức hóa học chưa đóng.");
      let value=source.slice(start,index-1);
      if(!/^[A-Za-z0-9\s(){}.+\-=<>^_]+$/.test(value)) throw Error("Ký hiệu hóa học này chưa có cách đọc đã hỗ trợ.");
      const charges=[];
      value=value.replace(/\^\{(\d*[+-])\}/g,"^$1");
      const chargeToken=(base,n,sign)=>{
        charges.push(say(" mang điện tích "," with charge ")+(n?n+" ":"")+
          (sign==="+"?say("dương","positive"):say("âm","negative")));
        return base+" gsaiioncharge"+(charges.length-1)+"end ";
      };
      value=value.replace(/([A-Za-z0-9)])\^(\d*)([+-])(?=\s|$)/g,(_,base,n,sign)=>chargeToken(base,n,sign))
        .replace(/([A-Za-z0-9)])([+-])(?=\s|$)/g,(_,base,sign)=>chargeToken(base,"",sign));
      value=value.replace(/<=>|<->/g,say(" phản ứng thuận nghịch "," reversible reaction ")).replace(/->|=>/g,say(" tạo thành "," yields "));
      value=value.replace(/([A-Z][a-z]?)(\d*)/g,(_,symbol,n)=>say(" ký hiệu "," symbol ")+symbol.split("").join(" ")+(n?say(" chỉ số "," subscript ")+n:"")+" ")
        .replace(/\+/g,say(" cộng "," plus ")).replace(/[{}]/g,"").replace(/\^/g,say(" điện tích "," charge ")).replace(/_/g,say(" chỉ số "," subscript "));
      value=value.replace(/gsaiioncharge(\d+)end/g,(_,i)=>charges[Number(i)]);
      return say(" công thức hóa học: "," chemical notation: ")+value;
    }
    function parse(grouped) {
      if (++depth > 16) throw Error("Công thức quá sâu để đọc an toàn.");
      let out = "";
      while (index < source.length) {
        const c = source[index++];
        if (c === "}") { if (!grouped) throw Error("Công thức thừa dấu ngoặc."); depth--; return out; }
        if (c === "{") { out += " " + parse(true) + " "; continue; }
        if (c === "\\") {
          const match = /^[A-Za-z]+/.exec(source.slice(index));
          if (!match) { index++; out += " "; continue; }
          const cmd = match[0]; index += cmd.length;
          if (["left","right","displaystyle","limits"].includes(cmd)) continue;
          if (cmd === "ce") out += chemicalGroup();
          else if (["frac","dfrac","tfrac"].includes(cmd)) {
            const numerator = group(), denominator = group();
            out += say(" phân số, tử số "," fraction, numerator ") + numerator + say(", mẫu số ",", denominator ") + denominator + say(", hết phân số. ",", end fraction. ");
          } else if (cmd === "sqrt") {
            let order = say("hai","two");
            if (source[index] === "[") { const end = source.indexOf("]",index); if (end < 0) throw Error("Căn thức chưa đóng."); order = source.slice(index+1,end); index = end+1; }
            out += say(" căn bậc "," root of order ") + order + say(" của "," of ") + group() + say(", hết căn. ",", end root. ");
          } else if (["vec","overrightarrow"].includes(cmd)) {
            out += say(" véc tơ "," vector ") + group().replace(/([A-Z])(?=[A-Z])/g,"$1 ") + " ";
          } else if (["int","sum","lim"].includes(cmd)) {
            let lower="", upper="";
            for(let step=0;step<2;step++) {
              while(source[index]===" ")index++;
              if(source[index]==="_"){index++;lower=group();}
              else if(source[index]==="^"){index++;upper=group();}
              else break;
            }
            out += " "+commands[cmd][en?1:0]+" ";
            if(lower)out += (cmd==="lim"?say("khi ","as "):say("từ ","from "))+lower+" ";
            if(upper)out += say("đến ","to ")+upper+" ";
          } else if (["text","mathrm","operatorname","mathbf","mathbb","mathcal"].includes(cmd)) {
            const value = group().trim();
            out += cmd === "mathbb" && value === "R" ? say(" tập số thực "," real numbers ") : " " + value + " ";
          } else if (commands[cmd]) out += " " + commands[cmd][en ? 1 : 0] + " ";
          else throw Error("Chưa có cách đọc công thức cho \\" + cmd + ". Hãy đối chiếu công thức trên màn hình.");
        } else if (c === "^") out += say(" mũ "," to the power ") + group() + " ";
        else if (c === "_") out += say(" chỉ số dưới "," subscript ") + group() + " ";
        else if (c === "=") out += say(" bằng "," equals ");
        else if (c === "+") out += say(" cộng "," plus ");
        else if (c === "-" || c === "−") out += say(" trừ "," minus ");
        else if (c === "<") out += say(" nhỏ hơn "," less than ");
        else if (c === ">") out += say(" lớn hơn "," greater than ");
        else if (c === "/") out += say(" chia cho "," divided by ");
        else if (c === "'") out += say(" phẩy "," prime ");
        else out += c;
      }
      depth--;
      if (grouped) throw Error("Công thức thiếu dấu ngoặc đóng.");
      return out;
    }
    return parse(false).replace(/\s+/g," ").trim();
  }
  function prepareText(text, lang, subject) {
    const formulas = [];
    text = String(text).normalize("NFC").replace(/```[\s\S]*?```/g, lang === "en" ? " Code block; refer to the displayed code. " : " Khối mã; đối chiếu mã trên màn hình. ")
      .replace(/\$\$([\s\S]*?)\$\$|\\\[([\s\S]*?)\\\]|\\\(([^\n]*?)\\\)|\$([^$\n]+)\$/g,
      (_,a,b,c,d) => { formulas.push(formulaSpeech(a || b || c || d || "",lang)); return " GSAISPEECHFORMULA"+(formulas.length-1)+"END "; });
    text = text.replace(/```[\s\S]*?```/g, lang === "en" ? " Code block; refer to the displayed code. " : " Khối mã; đối chiếu mã trên màn hình. ")
      .replace(/!\[([^\]]*)\]\([^)]*\)/g,"$1").replace(/\[([^\]]+)\]\([^)]*\)/g,"$1")
      .replace(/<[^>]*>/g," ").replace(/^\s*#{1,6}\s+/gm,"").replace(/^\s*[-*•]\s+/gm,"");
    if(text.includes("$")) throw Error("Dấu phân cách công thức chưa đầy đủ; hãy chọn trọn công thức.");
    if (/\\[A-Za-z]+/.test(text)) throw Error("Đoạn chọn còn mã công thức chưa hỗ trợ. Hãy chọn trọn công thức hoặc đối chiếu bản hiển thị.");
    text = text.replace(/^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$/gm,"")
      .replace(/\s*\|\s*/g,"; ").replace(/[*`~]/g,"")
      .replace(/\n\s*\n/g,".\n").replace(/([.!?;:])\1+/g,"$1");
    if (lang === "vi") {
      text = replaceTerms(text, subject);
      const units = {"kg":"ki lô gam","cm":"xen ti mét","mm":"mi li mét","km":"ki lô mét","m":"mét","s":"giây","mol":"mol","Hz":"héc","kHz":"ki lô héc","MHz":"mê ga héc","Pa":"pát xcan","kPa":"ki lô pát xcan","J":"jun","W":"oát","V":"vôn","A":"am pe","N":"niu tơn","Ω":"ôm","°C":"độ xê"};
      if (["Toán học","Vật lý","Hóa học","Khoa học tự nhiên","Công nghệ"].includes(subjectName(subject))) {
        text = text.replace(/(\d+(?:[.,]\d+)?)\s*(MHz|kHz|kPa|kg|cm|mm|km|mol|Hz|Pa|°C|Ω|m|s|J|W|V|A|N)(?![\p{L}\p{N}_])/gu, (_,n,u) => n + " " + units[u]);
      }
    }
    // Unit expansion applies to prose, not bare variables inside formulas:
    // y=2m+1 contains parameter m, not a measurement of two metres.
    text = text.replace(/GSAISPEECHFORMULA(\d+)END/g,(_,i)=>formulas[Number(i)]);
    return text.replace(/[ \t]+/g," ").trim();
  }
  function planSpeech(text, subject, forced) {
    if (String(text).length > 120000) throw Error("Nội dung quá dài; hãy chọn từng phần để đọc đầy đủ.");
    const fallback = subjectName(subject) === "Tiếng Anh" ? "en" : "vi";
    const formulas=[];
    const protectedText=String(text).replace(/\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\]|\\\([^\n]*?\\\)|\$[^$\n]+\$/g,
      value=>{formulas.push(value); return "GSAIPROTECTEDMATH"+(formulas.length-1)+"END";});
    const parts = protectedText.split(/(?<=[.!?;])\s+|\n+/u).filter(s=>s.trim());
    const planned = [];
    for (const protectedPart of parts) {
      const part=protectedPart.replace(/GSAIPROTECTEDMATH(\d+)END/g,(_,i)=>formulas[Number(i)]);
      const prose=protectedPart.replace(/GSAIPROTECTEDMATH\d+END/g,"");
      const base = forced === "vi" || forced === "en" ? forced : languageOf(prose,fallback);
      // Keep formulas intact. In bilingual prose split clearly identifiable English runs.
      let runs = [{text:part,lang:base}];
      if (!forced && base === "vi" && !/[$\\]/.test(part)) {
        runs = [];
        for (const token of part.split(/(\s+)/)) {
          if (!token) continue;
          const word = token.toLowerCase().replace(/^[^\p{L}]+|[^\p{L}]+$/gu,"");
          const lang = word.length>1 && EN_WORDS.has(word) && !VI_PLAIN.has(word) && !(VI_MARKS.test(word) && !LOAN_ACCENTS.has(word)) ? "en" :
            /\p{L}/u.test(token) ? "vi" : (runs.at(-1)?.lang || base);
          if (runs.at(-1)?.lang === lang) runs.at(-1).text += token;
          else runs.push({text:token,lang});
        }
      }
      for (const run of runs) {
        const clean = prepareText(run.text,run.lang,subject);
        // Chunk without losing punctuation, decimals, or text at a fixed-length cutoff.
        const words = clean.match(/\S+\s*/g) || [];
        let chunk = "";
        for (const word of words) {
          if (chunk.length + word.length > 240 && chunk) { planned.push({text:chunk.trim(),lang:run.lang}); chunk = ""; }
          chunk += word;
        }
        if (chunk.trim()) planned.push({text:chunk.trim(),lang:run.lang});
      }
    }
    if (planned.length > 1000) throw Error("Nội dung quá dài; hãy đọc từng phần.");
    return planned;
  }
  function chooseVoice(voices, lang, saved) {
    const candidates = voices.filter(v => String(v.lang).toLowerCase().startsWith(lang + "-") || v.lang === lang);
    return candidates.find(v => v.voiceURI === saved) ||
      (lang === "en" ? candidates.find(v=>v.lang.toLowerCase() === "en-us") || candidates.find(v=>v.lang.toLowerCase() === "en-gb") :
        candidates.find(v=>/NamMinh|Nam Minh/i.test(v.name))) || candidates[0] || null;
  }
  const api = {VERSION, languageOf, replaceTerms, formulaSpeech, prepareText, planSpeech, chooseVoice};
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  root.GSAIScienceReader = api;
})(typeof window !== "undefined" ? window : globalThis);
