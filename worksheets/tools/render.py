# usage: python3 render.py <saved download json path> <file id>  -> renders pages to SCRATCH/ws/img/<id>_pN.png
import sys,json,base64,pymupdf,os
src,fid=sys.argv[1],sys.argv[2]
out=sys.argv[3] if len(sys.argv)>3 else os.path.join(os.path.dirname(os.path.abspath(__file__)),'img')
os.makedirs(out,exist_ok=True)
d=json.load(open(src)); b=base64.b64decode(d['content'])
doc=pymupdf.open(stream=b,filetype='pdf')
n=min(doc.page_count,3)
for i in range(n):
    p=os.path.join(out,f'{fid}_p{i+1}.png'); doc[i].get_pixmap(dpi=60).save(p); print(p)
print('pages_total',doc.page_count)
