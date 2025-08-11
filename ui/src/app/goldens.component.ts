import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ApiService } from './api.service';
import { ApiResponse } from './types';

interface GoldenRule { type?: string; must_include?: string[] }
interface GoldenExpect { answer_contains?: string[]; citations?: GoldenRule[] }
export interface GoldenItem { id: string; query: string; expects?: GoldenExpect }
interface GoldenRun extends GoldenItem { running?: boolean; ms?: number; resp?: ApiResponse | null; exact?: number; grounded?: number; cits_ok?: boolean; pass?: boolean; error?: string }

@Component({
  selector: 'app-goldens',
  templateUrl: './goldens.component.html',
  styleUrls: ['./goldens.component.css']
})
export class GoldensComponent {
  items: GoldenRun[] = []; loading=false; results=false; fileError=''; newId=''; newQuery='';
  constructor(private http: HttpClient, private api: ApiService){ this.loadDefaults(); }
  loadDefaults(){ this.http.get<GoldenItem[]>(`assets/golden.json`).subscribe({ next:(arr)=>{ this.items=(arr||[]).map(x=>({...x, resp:null})); }, error:()=>{ this.items=[]; } }); }
  add(){ const id=(this.newId||'').trim(); const q=(this.newQuery||'').trim(); if(!id||!q) return; this.items.push({id,query:q}); this.newId=''; this.newQuery=''; }
  onFile(evt:any){ this.fileError=''; const f=evt.target.files?.[0]; if(!f) return; const reader=new FileReader(); reader.onload=()=>{
    try{ let text=String(reader.result||''); if(f.name.endsWith('.jsonl')){ const lines=text.split(/\r?\n/).filter(Boolean); this.items=lines.map(l=>JSON.parse(l)).map(x=>({...x,resp:null})); }
      else{ const arr=JSON.parse(text); this.items=(arr||[]).map((x:GoldenItem)=>({...x,resp:null})); } }catch(e:any){ this.fileError=e?.message||'Invalid file'; }
  }; reader.readAsText(f); }
  download(){ const blob=new Blob([JSON.stringify(this.items.map(({running,ms,resp,exact,grounded,cits_ok,pass,error, ...rest})=>rest),null,2)],{type:'application/json'});
    const url=URL.createObjectURL(blob); const a=document.createElement('a'); a.href=url; a.download=`golden-${Date.now()}.json`; a.click(); URL.revokeObjectURL(url); }
  async runAll(){ this.loading=true; this.results=false; for(const it of this.items){ await this.runOne(it); } this.loading=false; this.results=true; }
  runOne(it: GoldenRun): Promise<void>{
    it.running=true; it.error=''; it.resp=null; const t0=performance.now();
    return new Promise((resolve)=>{ this.api.run(it.query).subscribe({ next:(r)=>{ it.ms=Math.round(performance.now()-t0); it.resp=r;
      const [exact, cits_ok, grd]=this.score(r, it.expects); it.exact=exact; it.cits_ok=cits_ok; it.grounded=grd; it.pass=(exact>=0.8)&&cits_ok&&(grd>=0.9); it.running=false; resolve(); },
      error:(e)=>{ it.error=e?.message||'Request failed'; it.running=false; resolve(); } }); });
  }
  private score(resp: ApiResponse, expects?: GoldenExpect): [number, boolean, number]{
    const answer=(resp?.final_answer||'').toLowerCase(); const hits=(resp as any)?.raw_state?.hits||[];
    const pool=[resp?.final_answer||'', ...hits.map((h:any)=>h.text||'')].map(x=>x.toLowerCase());
    const req=expects?.answer_contains||[]; const exact=req.length? req.filter(s=>answer.includes(s.toLowerCase())).length/req.length : 1;
    let cits_ok=true; for(const rule of (expects?.citations||[])){ const want=(rule.type||'code');
      const okType=(resp.citations||[]).some(c=> want==='sql_or_code' ? (c.type==='sql'||c.type==='code') : c.type===want); if(!okType){ cits_ok=false; break; }
      for(const s of (rule.must_include||[])){ const found=pool.some(p=>p.includes(s.toLowerCase())); if(!found){ cits_ok=false; break; } } if(!cits_ok) break; }
    const grounded=(resp.citations||[]).length>=1?1:0; return [exact, cits_ok, grounded];
  }
}
