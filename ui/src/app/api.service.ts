import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ApiResponse } from './types';
@Injectable({ providedIn: 'root' })
export class ApiService {
  constructor(private http: HttpClient) {}
  run(query: string, opts?: any): Observable<ApiResponse> {
    return this.http.post<ApiResponse>('/api/run', { query, opts: opts || {} });
  }
}
