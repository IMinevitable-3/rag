import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpResponse } from '@angular/common/http';
import { Observable, Subject, map, tap } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class OcrService {
  private apiUrl = 'http://localhost:3000/api';
  private readonly TOKEN_KEY = 'ocr-user-token';
  private historyUpdated$ = new Subject<void>();

  constructor(private http: HttpClient) {}

  private getToken(): string {
    return localStorage.getItem(this.TOKEN_KEY) || '';
  }

  private storeToken(token: string): void {
    if (token) {
      localStorage.setItem(this.TOKEN_KEY, token);
    }
  }

  uploadImageAndExtractText(
    file: File
  ): Observable<{ text: string; structured: any }> {
    const formData = new FormData();
    formData.append('image', file);

    const headers = new HttpHeaders().set('x-user-token', this.getToken());

    return this.http
      .post<{ text: string; structured: any }>(`${this.apiUrl}/ocr`, formData, {
        headers,
        observe: 'response',
      })
      .pipe(
        tap((res) => {
          const newToken = res.headers.get('x-user-token');
          if (newToken) {
            this.storeToken(newToken);
          }
          this.historyUpdated$.next();
        }),
        map((res) => res.body!)
      );
  }

  getHistory(): Observable<{ history: any[] }> {
    const headers = new HttpHeaders().set('x-user-token', this.getToken());
    return this.http.get<{ history: any[] }>(`${this.apiUrl}/history`, {
      headers,
    });
  }

  onHistoryUpdated(): Observable<void> {
    return this.historyUpdated$.asObservable();
  }
}
