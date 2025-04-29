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

  updateRoomAvailability(roomId: number, available: boolean): Observable<any> {
    return this.http.patch<any>(`/api/room/${roomId}`, { available });
  }

  getUserConversations(userId: number): Observable<any[]> {
    return this.http.get<any[]>(`/api/conversations/user/${userId}`);
  }
}
