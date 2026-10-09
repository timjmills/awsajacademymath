const {chromium}=require('/opt/node-tools/node_modules/playwright');const fs=require('fs');const path=require('path');
const dir=process.argv[2],out=process.argv[3];const F=JSON.parse(fs.readFileSync(path.join(dir,'files.json')));
(async()=>{const b=await chromium.launch({args:['--no-sandbox']});const pg=await b.newPage();
for(const[g,f]of Object.entries(F)){
 // one-page year at a glance: shrink the type until it fits one A4 landscape page
 await pg.setViewportSize({width:Math.round((297-16)/25.4*96),height:Math.round((210-14)/25.4*96)});
 await pg.goto('file://'+path.resolve(dir,f.yg+'.html'));
 const fs_=await pg.evaluate(()=>{const H=window.innerHeight;let s=11;document.documentElement.style.fontSize=s+'px';while(document.body.scrollHeight>H-2&&s>5){s-=0.1;document.documentElement.style.fontSize=s+'px';}return s;});
 await pg.pdf({path:path.join(out,f.yg+'.pdf'),format:'A4',landscape:true,printBackground:true,margin:{top:'7mm',bottom:'7mm',left:'8mm',right:'8mm'}});
 console.log(g,'yg font',fs_.toFixed(1));
 for(const[k,land]of[['pg',true],['hb',false]]){
 await pg.goto('file://'+path.resolve(dir,f[k]+'.html'));await pg.waitForTimeout(150);
 const foot=`<div style="font:7px Liberation Sans,sans-serif;color:#8A8077;width:100%;padding:0 ${land?'9':'14'}mm;display:flex;justify-content:space-between"><span>${f[k+'foot']}</span><span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>`;
 await pg.pdf({path:path.join(out,f[k]+'.pdf'),format:'A4',landscape:land,printBackground:true,displayHeaderFooter:true,headerTemplate:'<div></div>',footerTemplate:foot,margin:land?{top:'9mm',bottom:'11mm',left:'9mm',right:'9mm'}:{top:'14mm',bottom:'16mm',left:'14mm',right:'14mm'}});
 }}await b.close();})();
