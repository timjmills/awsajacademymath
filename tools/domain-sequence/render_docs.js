const {chromium}=require('/opt/node-tools/node_modules/playwright');const fs=require('fs');const path=require('path');
const dir=process.argv[2],out=process.argv[3];const F=JSON.parse(fs.readFileSync(path.join(dir,'files.json')));
(async()=>{const b=await chromium.launch({args:['--no-sandbox']});const pg=await b.newPage();
for(const[g,f]of Object.entries(F)){for(const[k,land]of[['pg',true],['hb',false]]){
 await pg.goto('file://'+path.resolve(dir,f[k]+'.html'));await pg.waitForTimeout(150);
 const foot=`<div style="font:7px Liberation Sans,sans-serif;color:#8A8077;width:100%;padding:0 ${land?'9':'14'}mm;display:flex;justify-content:space-between"><span>${f[k+'foot']}</span><span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>`;
 await pg.pdf({path:path.join(out,f[k]+'.pdf'),format:'A4',landscape:land,printBackground:true,displayHeaderFooter:true,headerTemplate:'<div></div>',footerTemplate:foot,margin:land?{top:'9mm',bottom:'11mm',left:'9mm',right:'9mm'}:{top:'14mm',bottom:'16mm',left:'14mm',right:'14mm'}});
 console.log(g,k);}}await b.close();})();
