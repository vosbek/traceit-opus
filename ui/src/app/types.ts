export interface Citation { type: 'code' | 'sql' | 'idl' | 'doc'; path: string; lines?: [number,number]; repo?: string; sha?: string; source_env?: string; }
export interface ApiResponse { thread_id: string; final_answer: string; citations: Citation[]; steps: any[]; graph?: {nodes:any[]; edges:any[]}; raw_state?: any; }
