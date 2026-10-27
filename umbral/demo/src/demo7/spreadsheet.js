/* Local OOXML workbook writer: text stays text, numeric cells stay numeric. */
const UmbralSpreadsheet=(()=>{
  const xml=s=>String(s??'').replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/g,'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
  const column=n=>{let s='';for(n++;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
  const enc=new TextEncoder();
  const crcTable=Array.from({length:256},(_,n)=>{for(let i=0;i<8;i++)n=n&1?0xedb88320^(n>>>1):n>>>1;return n>>>0;});
  function crc(bytes){let n=0xffffffff;for(const b of bytes)n=crcTable[(n^b)&255]^(n>>>8);return (n^0xffffffff)>>>0;}
  function zip(files){
    const chunks=[],central=[];let offset=0,size=0;
    for(const [path,text] of Object.entries(files)){
      const name=enc.encode(path),data=enc.encode(text),sum=crc(data);
      const local=new Uint8Array(30+name.length),l=new DataView(local.buffer);
      l.setUint32(0,0x04034b50,true);l.setUint16(4,20,true);l.setUint16(12,33,true);
      l.setUint32(14,sum,true);l.setUint32(18,data.length,true);l.setUint32(22,data.length,true);l.setUint16(26,name.length,true);local.set(name,30);
      const dir=new Uint8Array(46+name.length),d=new DataView(dir.buffer);
      d.setUint32(0,0x02014b50,true);d.setUint16(4,20,true);d.setUint16(6,20,true);d.setUint16(14,33,true);
      d.setUint32(16,sum,true);d.setUint32(20,data.length,true);d.setUint32(24,data.length,true);d.setUint16(28,name.length,true);d.setUint32(42,offset,true);dir.set(name,46);
      chunks.push(local,data);central.push(dir);offset+=local.length+data.length;size+=dir.length;
    }
    const end=new Uint8Array(22),e=new DataView(end.buffer);
    e.setUint32(0,0x06054b50,true);e.setUint16(8,central.length,true);e.setUint16(10,central.length,true);e.setUint32(12,size,true);e.setUint32(16,offset,true);
    return new Blob([...chunks,...central,end],{type:'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'});
  }
  function sheet({title,subtitle,rows,widths=[]}){
    const n=rows[0].length,last=column(n-1),all=[[title,...Array(n-1).fill('')],[subtitle,...Array(n-1).fill('')],[],...rows];
    const height=row=>Math.max(36,...row.map((v,c)=>Math.ceil(String(v??'').length/(widths[c]||22))*16+8));
    const data=all.map((row,r)=>`<row r="${r+1}" ht="${r===0?32:r===1?42:r===3?52:height(row)}" customHeight="1">${row.map((v,c)=>{
      const numeric=typeof v==='number'&&Number.isFinite(v),style=r===0?1:r===1?2:r===3?3:numeric?(r%2?6:7):(r%2?4:5);
      return `<c r="${column(c)}${r+1}" s="${style}"${numeric?'':' t="inlineStr"'}>${numeric?`<v>${v}</v>`:`<is><t xml:space="preserve">${xml(v)}</t></is>`}</c>`;
    }).join('')}</row>`).join('');
    return `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><dimension ref="A1:${last}${all.length}"/><sheetViews><sheetView workbookViewId="0"><pane ySplit="4" topLeftCell="A5" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews><cols>${rows[0].map((_,i)=>`<col min="${i+1}" max="${i+1}" width="${widths[i]||22}" customWidth="1"/>`).join('')}</cols><sheetData>${data}</sheetData><autoFilter ref="A4:${last}${all.length}"/><mergeCells count="2"><mergeCell ref="A1:${last}1"/><mergeCell ref="A2:${last}2"/></mergeCells><pageMargins left="0.3" right="0.3" top="0.5" bottom="0.5" header="0.2" footer="0.2"/><pageSetup orientation="landscape" paperSize="9" fitToWidth="1" fitToHeight="0"/></worksheet>`;
  }
  function workbook(sheets){
    const ns='http://schemas.openxmlformats.org/officeDocument/2006/relationships';
    const xf=(font,fill,border,numFmt=0)=>`<xf numFmtId="${numFmt}" fontId="${font}" fillId="${fill}" borderId="${border}" xfId="0" applyAlignment="1" applyBorder="1" applyFill="1" applyFont="1" applyNumberFormat="1"><alignment vertical="center" wrapText="1"/></xf>`;
    const files={
      '[Content_Types].xml':`<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>${sheets.map((_,i)=>`<Override PartName="/xl/worksheets/sheet${i+1}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>`).join('')}</Types>`,
      '_rels/.rels':`<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="${ns}/officeDocument" Target="xl/workbook.xml"/></Relationships>`,
      'xl/workbook.xml':`<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="${ns}"><sheets>${sheets.map((s,i)=>`<sheet name="${xml(s.name)}" sheetId="${i+1}" r:id="rId${i+1}"/>`).join('')}</sheets></workbook>`,
      'xl/_rels/workbook.xml.rels':`<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">${sheets.map((_,i)=>`<Relationship Id="rId${i+1}" Type="${ns}/worksheet" Target="worksheets/sheet${i+1}.xml"/>`).join('')}<Relationship Id="styles" Type="${ns}/styles" Target="styles.xml"/></Relationships>`,
      'xl/styles.xml':`<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><numFmts count="1"><numFmt numFmtId="164" formatCode="0.######"/></numFmts><fonts count="3"><font><sz val="11"/><name val="Calibri"/><color rgb="FF173F35"/></font><font><b/><sz val="18"/><name val="Calibri"/><color rgb="FFFFFFFF"/></font><font><b/><sz val="11"/><name val="Calibri"/><color rgb="FFFFFFFF"/></font></fonts><fills count="4"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF143F38"/><bgColor indexed="64"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFEDF3EF"/><bgColor indexed="64"/></patternFill></fill></fills><borders count="2"><border><left/><right/><top/><bottom/><diagonal/></border><border>${['left','right','top','bottom'].map(x=>`<${x} style="thin"><color rgb="FFC5D6CC"/></${x}>`).join('')}<diagonal/></border></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="8">${xf(0,0,0)+xf(1,2,0)+xf(0,3,0)+xf(2,2,1)+xf(0,0,1)+xf(0,3,1)+xf(0,0,1,164)+xf(0,3,1,164)}</cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>`
    };
    sheets.forEach((s,i)=>files[`xl/worksheets/sheet${i+1}.xml`]=sheet(s));return zip(files);
  }
  function parseCsv(text){
    const rows=[];let row=[],value='',quoted=false;
    for(let i=0,s=text.replace(/^\uFEFF/,'');i<s.length;i++){
      const c=s[i];
      if(c==='"'){if(quoted&&s[i+1]==='"'){value+='"';i++;}else quoted=!quoted;}
      else if(!quoted&&(c===','||c==='\n'||c==='\r')){row.push(value);value='';if(c!==','){rows.push(row);row=[];if(c==='\r'&&s[i+1]==='\n')i++;}}
      else value+=c;
    }
    if(value||row.length){row.push(value);rows.push(row);}return rows;
  }
  function download(sheets,name){const url=URL.createObjectURL(workbook(sheets)),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),30000);}
  return {workbook,download,parseCsv};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=UmbralSpreadsheet;
