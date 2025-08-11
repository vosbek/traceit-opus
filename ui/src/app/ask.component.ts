import { Component, AfterViewInit } from '@angular/core';
import { ApiService } from './api.service';
import { ApiResponse, Citation } from './types';
import cytoscape from 'cytoscape';

@Component({
  selector: 'app-ask',
  templateUrl: './ask.component.html',
  styleUrls: ['./ask.component.css']
})
export class AskComponent implements AfterViewInit {
  query = ''; loading = false; resp: ApiResponse | null = null; error = ''; mode: 'default'|'high_precision'|'deep_search' = 'default';
  constructor(private api: ApiService) {}
  ngAfterViewInit(): void {}
  ask() {
    this.error=''; this.resp=null; const q=(this.query||'').trim(); if(!q){ this.error='Enter a question'; return; }
    this.loading=true;
    this.api.run(q,{mode:this.mode}).subscribe({
      next: (r)=>{ this.resp=r; this.loading=false; setTimeout(()=>this.renderGraph(),0); },
      error: (e)=>{ this.error=e?.message||'Request failed'; this.loading=false; }
    });
  }
  renderGraph(){
    const container=document.getElementById('cy'); if(!container || !this.resp?.graph) return;
    const nodes=(this.resp.graph.nodes||[]).map((n:any)=>({data:{id:n.id,label:n.label||n.id}}));
    const edges=(this.resp.graph.edges||[]).map((e:any)=>({data:{id:`${e.source}->${e.target}`,source:e.source,target:e.target}}));
    cytoscape({ container, elements:{nodes,edges}, style:[
      {selector:'node', style:{'background-color':'#3b82f6','label':'data(label)','color':'#fff','font-size':'10px'}},
      {selector:'edge', style:{'width':2,'line-color':'#94a3b8','target-arrow-color':'#94a3b8','target-arrow-shape':'triangle'}}
    ], layout:{name:'breadthfirst', directed:true, padding:10} });
  }
  downloadJSON(){ if(!this.resp) return; const blob=new Blob([JSON.stringify(this.resp,null,2)],{type:'application/json'});
    const url=URL.createObjectURL(blob); const a=document.createElement('a'); a.href=url; a.download=`traceit-run-${Date.now()}.json`; a.click(); URL.revokeObjectURL(url); }
  citeLabel(c: Citation){ const env=c.source_env?` [${c.source_env}]`:''; const repo=c.repo?`${c.repo}:`:''; return `${c.type.toUpperCase()} — ${repo}${c.path}${env}`; }
}
