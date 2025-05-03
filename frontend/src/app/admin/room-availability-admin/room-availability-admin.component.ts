import { Component, OnInit } from '@angular/core';
import { AdminDataService } from '../admin-data.service';

@Component({
  selector: 'app-room-availability-admin',
  templateUrl: './room-availability-admin.component.html',
  styleUrls: ['./room-availability-admin.component.css']
})
export class RoomAvailabilityAdminComponent implements OnInit {
  rooms: any[] = [];
  updatingRoomIds = new Set<number>(); // Track which rooms are updating

  constructor(private adminDataService: AdminDataService) {}

  ngOnInit(): void {
    this.loadRooms();
  }

  loadRooms(): void {
    this.adminDataService.getAllRooms().subscribe((data) => {
      this.rooms = data;
    });
  }

  toggleAvailability(room: any): void {
    this.updatingRoomIds.add(room.id);

    this.adminDataService.toggleRoomAvailability(room.id).subscribe({
      next: (res) => {
        console.log('Backend response:', res);
        room.available = res.is_available; // update only when backend responds
        this.updatingRoomIds.delete(room.id);
      },
      error: () => {
        this.updatingRoomIds.delete(room.id);
        alert('Failed to update availability');
      }
    });
  }

  isUpdating(room: any): boolean {
    return this.updatingRoomIds.has(room.id);
  }
}
