import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AdminDataService {
  constructor(private http: HttpClient) {}

  getAllRooms(): Observable<any[]> {
    return this.http.get<any[]>(`/api/room`);
  }

  toggleRoomAvailability(roomId: string): Observable<any> {
    return this.http.patch<any>(`/api/rooms/${roomId}/toggle-availability`, {});
  }

  getUserConversations(userId: number): Observable<any[]> {
    return this.http.get<any[]>(`/api/conversations/user/${userId}`);
  }
}
